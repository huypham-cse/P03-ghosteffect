"""GUI-only Algorithm 1 runtime. No backend labels, app DB or agent reasoning.

Observer interface: verify_context(), read(family,view), monitor(). Monitor may
return pending/acked/failed/stuck; it is an app-GUI observer, not backend truth.
The controller supplies a durable one-read cache and monotonic clock origin.
"""
import math
import time

from calibration import numeric, DOMAIN_KEYS, class_origin


class Recovery:
    def __init__(self, store, observer, now=time.monotonic, sleep=time.sleep):
        self.store, self.observer, self.now, self.sleep = store, observer, now, sleep
        self.trace = []

    def result(self, action, reason):
        return dict(decision=action, reason=reason, trace=self.trace,
                    certificate_sha256=self.store['content_sha256'])

    def event(self, event, **data):
        self.trace.append(dict(event=event, mono_seconds=self.now(), **data))

    def readout(self, family, views):
        ys = []
        for view in views:
            if not self.observer.verify_context():
                raise RuntimeError('foreground/account/window identity changed')
            raw = self.observer.read(family, view)
            if raw not in (0,1,None) or isinstance(raw,bool):
                raise ValueError('view must return integer 0/1 or BOT None')
            ys.append(raw)
        side, level = numeric.verdict_of(family, ys)
        self.event('READ_FAMILY', family=family, views=list(views), observations=ys, side=side, level=level)
        return side, level

    def resolve(self, domain, context):
        if set(domain) != DOMAIN_KEYS:
            return self.result('ASK', 'incomplete_domain')
        matches = [s for s in self.store['strata'] if s['domain'] == domain]
        if len(matches) != 1:
            return self.result('ASK', 'unsupported_domain')
        item = matches[0]
        cap, families, mode = item['capabilities'], item['families'], self.store['mode']
        cls = context.get('fault_class')
        if cls is not None and cls not in item['classes']:
            return self.result('ASK', 'unsupported_fault_class')
        classes = item['classes'] if cls is None else [cls]
        selected = [item['calibrated'][c] for c in classes]
        origins = []
        for fault_class in classes:
            kind = class_origin(item,fault_class)
            receipt = context.get('origins',{}).get(kind,{}) if item.get('class_origins') else context
            if receipt.get('origin_kind') != kind or receipt.get('origin_verified') is not True:
                return self.result('ASK', 'unknown_or_mismatched_origin')
            origin = receipt.get('origin_mono_seconds')
            if isinstance(origin,bool) or not isinstance(origin,(int,float)) or not math.isfinite(origin) or origin > self.now():
                return self.result('ASK', 'invalid_monotonic_origin')
            origins.append(origin)
        if context.get('new_fault_since_origin') or context.get('idle_domain_changed'):
            return self.result('ASK', 'domain_changed_after_origin')
        if not self.observer.verify_context():
            return self.result('ASK', 'identity_not_verified')
        local = cap.get('local',False)
        if not local and not cap.get('backend_visibility_domain_qualified'):
            return self.result('ASK','backend_visibility_domain_not_qualified')
        use_hop = 'hop1' in families
        # Force-stop cancels scheduled work (theorem H3). Unknown eligibility is
        # never promoted to G2 merely because the app/backend supports dedup.
        g2 = cap.get('G2',False) and context.get('g2_eligible') is True and context.get('force_stopped') is not True
        alpha, beta = self.store['alpha'], self.store['beta']
        a_test, a_lag, b_test = (.9 if local else .5)*alpha, (0 if local else .4)*alpha, .9*beta
        q = [record['q'] for record in selected]
        order = [f for f in families if f != 'hop1' and not (f=='vlm' and context.get('lookalike') is True)]
        taus = []
        for record, bounds in zip(selected,q):
            if mode in ('joint','source'):
                taus.append((numeric.tau_from(record['abs_tab'],a_test), numeric.tau_from(record['com_tab'],b_test)))
            else:
                abs_lv = ([bounds['hop1']['abs']] if use_hop else []) + [bounds[f]['abs'] for f in order]
                com_lv = ([bounds['hop1']['com']] if use_hop and (local or g2) else []) + [bounds[f]['com'] for f in order]
                taus.append((numeric.tau_for(numeric.cert_table(abs_lv),a_test) if abs_lv else 0,
                             numeric.tau_for(numeric.cert_table(com_lv),b_test) if com_lv else 0))
        self.event('BUDGET', alpha_test=a_test, alpha_lag=a_lag, beta_test=b_test,
                   K_total=self.store['K_total'], delta=self.store['delta'], classes=len(selected),
                   g2=g2, thresholds=taus)
        products, direction, path = [1.0]*len(selected), None, 'main'

        def multiply(family, side, level):
            for i,bounds in enumerate(q):
                per = bounds[family][side]
                products[i] *= per.get(str(level),per.get(level,1.0))

        def certified(side):
            index = 0 if side == 'abs' else 1
            return all(threshold[index] > 0 and p <= threshold[index] for p,threshold in zip(products,taus))

        def retry(reason):
            if not self.observer.verify_context():
                return self.result('ASK', 'identity_changed_before_retry')
            return self.result('RETRY', reason)

        if use_hop:
            side, level = self.readout('hop1',families['hop1'])
            if side == 'com' and (local or g2):
                multiply('hop1',side,level)
                direction = 'com'
                if local:
                    if certified('com'):
                        return self.result('COMMITTED','certified_local_hop1')
                else:
                    monitor = self.observer.monitor()
                    if not isinstance(monitor,dict) or monitor.get('state') not in ('pending','acked','failed','stuck'):
                        raise ValueError('invalid qualified Monitor observation')
                    # Dedup/stuck age cannot restart at app relaunch. Require
                    # the original issue clock, separately from the lag origin.
                    issued = context.get('issued_mono_seconds')
                    age = self.now()-issued if (type(issued) in (int,float) and math.isfinite(issued) and issued<=self.now()) else float('inf')
                    # Unknown/near dedup horizon is not permission to wait forever.
                    horizon = context.get('dedup_horizon_seconds')
                    near_horizon = not isinstance(horizon,(int,float)) or not math.isfinite(horizon) or age >= horizon-10
                    self.event('MONITOR', state=monitor['state'], age=age if math.isfinite(age) else None, near_horizon=near_horizon)
                    if monitor['state']=='pending' and age < 120 and not near_horizon:
                        return self.result('PENDING','qualified_durable_outbox_pending')
                    if monitor['state']=='acked':
                        if certified('com'):
                            return self.result('COMMITTED','certified_g2_hop1')
                        if monitor.get('end_to_end_ready') is True:
                            path = 'corroborate'
                        else:
                            # A fallible local ACK is not proof a history/search
                            # view has reached the post-visibility distribution.
                            products, direction, path = [1.0]*len(selected), None, 'handover'
                    else:
                        products, direction, path = [1.0]*len(selected), None, 'handover'
            elif side == 'abs':
                multiply('hop1',side,level)
                direction, path = 'abs','h1abs'
                if certified('abs'):
                    return retry('certified_hop1_absence')
        if not local and order and path != 'corroborate':
            waits = []
            for record in selected:
                share = a_lag
                if use_hop and cap.get('hop1_lag_independent'):
                    share = a_lag/2
                    if path == 'h1abs':
                        qh = record['qh']
                        share = min(1,share/qh) if qh else 1
                lag = sorted(record['lag_seconds'] + [float('inf')]*record['lag_censored'])
                waits.append(numeric.certified_wait(lag,share,self.store['delta']))
            # Different fault classes may have different calibrated origins.
            # Max duration added to one clock is not the maximum deadline.
            deadline = max(t+w for t,w in zip(origins,waits))
            remaining = max(0,deadline-self.now())
            wait = max(waits)
            self.event('CERTIFIED_WAIT', wait=wait if math.isfinite(wait) else None,
                       remaining=remaining if math.isfinite(remaining) else None,
                       origin_kind=domain['origin_kind'], origins=origins,
                       deadline=deadline if math.isfinite(deadline) else None,
                       relaxed=path=='h1abs' and cap.get('hop1_lag_independent',False))
            if remaining > 120:
                return self.result('ASK','no_wait_within_additional_120_seconds')
            # Monotonic origin is the same one used by this stratum's lag law.
            # Sleep can wake early; no end-to-end read is allowed before deadline.
            while self.now() < deadline:
                self.sleep(deadline-self.now())
            if not self.observer.verify_context():
                return self.result('ASK','identity_changed_during_wait')
        for family in order:
            side, level = self.readout(family,families[family])
            if side is None:
                continue
            if direction not in (None,side):
                return self.result('ASK','family_disagreement')
            direction = side
            multiply(family,side,level)
            if certified(side):
                if side == 'abs':
                    return retry('certified_end_to_end_absence')
                return self.result('COMMITTED','certified_end_to_end_presence')
        return self.result('ASK','not_certifiable')
