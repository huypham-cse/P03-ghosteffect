"""Compile whole-effect calibration into aggregate runtime tables (draft §4–5).

Reuses the numerical artifact; does not generate labels or call a backend/model.
Pilot, holdout and lag quotas are frozen in a spec before collection. Synthetic
fixtures remain labelled and are rejected by the production loader.
"""
import argparse
from bisect import bisect_right
import hashlib
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'artifact' / 'scripts'))
import planner_sim as numeric

SCHEMA = 'ghosteffect-calibration-v1'
ORDER = ('hop1', 'nonce', 'digest', 'vlm')
VIEWS = dict(hop1=2, nonce=2, digest=2, vlm=3)
DOMAIN_KEYS = {'app_package', 'app_version', 'backend_revision', 'reader_revision',
               'verifier_revision', 'locale', 'abi', 'load_profile', 'policy_revision', 'origin_kind'}


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def file_sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def configurations(names):
    # Includes handover (drop hop1), digest look-alike skip, and G2 downgrade.
    return [(tuple(f for f in names if (f != 'hop1' or h) and (f != 'vlm' or v)), hc)
            for h in (True, False) for v in (True, False) for hc in (True, False)]


def class_origin(item, cls):
    return item.get('class_origins', {}).get(cls, item['domain']['origin_kind'])


def bound_count(spec, mode):
    names, cap = list(spec['families']), spec['capabilities']
    waits = 0 if cap.get('local') else (2 if 'hop1' in names and cap.get('hop1_lag_independent') else 1)
    if mode == 'joint':
        return 2 + int('hop1' in names) + waits
    if mode == 'source':
        return (6 if 'hop1' in names else 2) + waits
    total = 0
    for name in names:
        levels = numeric.levels(name)
        total += len(levels['abs'])
        if name != 'nonce' or not cap.get('nonce_analytic_qualified'):
            total += len(levels['com'])
    return total + waits


def validate_spec(spec):
    if spec.get('schema') != SCHEMA or spec.get('mode') not in ('product', 'source', 'joint'):
        raise ValueError('unsupported calibration spec/mode')
    if spec.get('evidence_kind') not in ('synthetic_fixture', 'interrupted_measurement'):
        raise ValueError('explicit evidence kind required')
    if not 0 < spec['alpha'] < 1 or not 0 < spec['beta'] < 1:
        raise ValueError('invalid effect risk budgets')
    if (not spec.get('strata') or any(not isinstance(s['id'],str) or not s['id'] for s in spec['strata'])
            or len({s['id'] for s in spec['strata']}) != len(spec['strata'])):
        raise ValueError('stratum IDs must be nonempty and unique')
    for item in spec['strata']:
        domain = item['domain']
        if set(domain) != DOMAIN_KEYS or any(not isinstance(v, str) or not v for v in domain.values()):
            raise ValueError('complete exact-match domain required')
        names = list(item['families'])
        if names != [x for x in ORDER if x in names] or not names:
            raise ValueError('families must follow hop1/nonce/digest/VLM order')
        for family, views in item['families'].items():
            if len(views) != VIEWS[family] or len(set(views)) != len(views) or not all(isinstance(v,str) and v for v in views):
                raise ValueError('frozen distinct view IDs required')
        if (not item['classes'] or not all(isinstance(c,str) and c for c in item['classes'])
                or len(set(item['classes'])) != len(item['classes'])):
            raise ValueError('distinct observable fault classes required')
        origins = item.get('class_origins')
        if origins is not None:
            if (domain['origin_kind'] != 'per_class' or set(origins) != set(item['classes'])
                    or any(not isinstance(v,str) or not v or v=='per_class' for v in origins.values())):
                raise ValueError('per-class clock laws require an explicit origin for every fault class')
        elif domain['origin_kind']=='per_class':
            raise ValueError('per-class clock laws missing')
        cap = item['capabilities']
        if not all(type(v) is bool for v in cap.values()):
            raise ValueError('capability qualifications must be booleans')
        if 'hop1' in names and not cap.get('hop1_qualified'):
            raise ValueError('rendered timeline status is not automatically hop1')
        if cap.get('nonce_analytic_qualified') and item.get('nonce_contract') != dict(
                symbols=6,alphabet='0123456789ABCDEFGHJKMNPQRSTVWXYZ',edit_distance=1,
                max_visible_tokens=40,no_uncommitted_nonce_visible=True):
            raise ValueError('analytic nonce qualification requires the exact lemma contract')
        if spec['mode'] == 'product' and not cap.get('family_independence_qualified'):
            raise ValueError('product requires A2 across families')
        if spec['mode'] == 'source' and not cap.get('source_independence_qualified'):
            raise ValueError('source mode still requires source independence')
        if set(item['quota']) != {'pilot0','pilot1','calibration0','calibration1','lag1'}:
            raise ValueError('explicit pilot/outcome/lag quotas required')
        if spec['mode'] != 'product' and any(item['quota'][x] < 1 for x in ('pilot0','pilot1')):
            raise ValueError('region score selection needs a disjoint pilot for both outcomes')
        if not all(type(n) is int and n >= 0 for n in item['quota'].values()):
            raise ValueError('fixed nonnegative acquisition quotas required')
        if any(item['quota'][x] < 1 for x in ('calibration0','calibration1')):
            raise ValueError('both outcomes need held-out calibration effects')
        if item.get('lag_splits',['calibration']) not in (['calibration'],['lag'],['calibration','lag']):
            raise ValueError('lag collection may reuse calibration, never score-selection pilot')
        if any(item['domain']==other['domain'] for other in spec['strata'] if other is not item):
            raise ValueError('ambiguous duplicate runtime domains')
    return sum(bound_count(s, spec['mode']) * len(s['classes']) for s in spec['strata'])


def verify_refs(row, base):
    """Check lab source identity, not statistical exchangeability or authenticity."""
    references = row.get('evidence', {})
    if set(references) != {'backend', 'fault', 'probes', 'clock'}:
        raise ValueError('real effects require backend/fault/probes/clock evidence references')
    if base is None:
        raise ValueError('real calibration requires an evidence root')
    base = Path(base).resolve()
    for ref in references.values():
        path = (base / ref['path']).resolve()
        if base not in path.parents or not path.is_file() or file_sha(path) != ref['sha256']:
            raise ValueError('missing, external or modified calibration evidence')


def _bounds(e1, e0, names, delta, analytic):
    q = numeric.marginal_bounds(e1, e0, names, delta)
    if 'nonce' in names and not analytic:
        # The analytic nonce lemma needs verified non-optimistic committed views.
        # Without that qualification use actual X0 false-positive counts instead.
        n = len(e0)
        q['nonce']['com'] = {r: numeric.cpu(q['nonce']['ge0'].get(r,0), n, delta)
                             for r in numeric.levels('nonce')['com']}
    return q


def fit_region(p1, p0, h1, h0, names, cap, delta, mode):
    q = _bounds(p1, p0, names, delta, cap.get('nonce_analytic_qualified',False))
    configs = configurations(names)
    hist = [f for f in names if f != 'hop1']
    qh = numeric.cpu(sum(numeric.verdict_of('hop1', r['hop1'])[0] == 'abs' for r in h1), len(h1), delta) if 'hop1' in names else None
    qhc = numeric.cpu(sum(numeric.verdict_of('hop1', r['hop1'])[0] == 'com' for r in h0), len(h0), delta) if 'hop1' in names else None
    if mode == 'source' and 'hop1' in names:
        q['hop1'] = dict(abs={VIEWS['hop1']: qh}, com={VIEWS['hop1']: qhc})
    # FIXED-SEQUENCE candidates must be selected on the pilot, not the holdout.
    # Held-out hop1 rates are certification bounds, not runtime score factors.
    # Source scores therefore retain the pilot's hop1 factors; the source union
    # bound below accounts for that scaling explicitly.
    pilot_q = _bounds(p1,p0,names,delta,cap.get('nonce_analytic_qualified',False))
    if mode == 'source':
        q = pilot_q

    def table(test, side):
        scores = []
        for record in test:
            verdicts = {f: numeric.verdict_of(f, record[f]) for f in names}
            if mode == 'joint':
                score = min(numeric.stop_product(verdicts, seq, q, side, hc) for seq,hc in configs)
            else:
                score = min(numeric.stop_product(verdicts, seq, q, side, False)
                            for seq in (hist, [f for f in hist if f != 'vlm']))
            scores.append(score)
        scores.sort()
        levels = [q[f][side] for f in (names if mode == 'joint' else hist)]
        candidates = sorted({p for p,_ in numeric.enum_assignments(levels)})
        minimum = candidates[0] if candidates else float('inf')
        factor_bound = qh if side == 'abs' else qhc
        factor_score = next(iter(q['hop1'][side].values())) if 'hop1' in names else None
        if mode == 'source' and factor_score is not None:
            candidates = sorted(set(candidates + [factor_score] + [factor_score*t for t in candidates]))
        result, running = [], 0.0
        for threshold in candidates:
            wrong = bisect_right(scores,threshold)
            bound = numeric.cpu(wrong, len(test), delta)
            if mode == 'source' and threshold < minimum:
                bound = 0.0  # empty history region, not a zero-event sampled region
            if mode == 'source' and factor_score is not None:
                # Compare in score space. Avoid multiply-then-divide tie errors.
                if threshold >= factor_score:
                    bound += factor_bound
                elif threshold >= factor_score*minimum:
                    # Runtime multiplies in this same order. No division moves
                    # a floating-point boundary across a calibrated score tie.
                    scaled = sorted(factor_score*s for s in scores)
                    bound += factor_bound*numeric.cpu(bisect_right(scaled,threshold), len(test), delta)
            running = max(running, bound)  # fixed-sequence stop at first failure
            result.append([running, threshold])
        return result
    return dict(q=q, abs_tab=table(h1, 'abs'), com_tab=table(h0, 'com'), qh=qh)


def compile_store(spec, rows, evidence_root=None):
    k_total = validate_spec(spec)
    delta = min(spec['alpha'], spec['beta']) / (10*k_total)
    definitions = {s['id']:s for s in spec['strata']}
    seen, groups = set(), {}
    for row in rows:
        sid, cls, outcome, split = row['stratum'], row['fault_class'], row['X_backend'], row['split']
        item = definitions.get(sid)
        if item is None or cls not in item['classes'] or type(outcome) is not int or outcome not in (0,1):
            raise ValueError('unknown stratum/class or unresolved backend truth')
        eid = row['effect_id']
        if not isinstance(eid,str) or not eid or eid in seen:
            raise ValueError('each interrupted effect must appear once, not once per view')
        seen.add(eid)
        if row.get('domain') != item['domain'] or split not in ('pilot','calibration','lag'):
            raise ValueError('domain mismatch or invalid split')
        if row.get('population') != 'interrupted' or row.get('evidence_kind') != spec['evidence_kind']:
            raise ValueError('passive/eval/simulation labels cannot become interrupted calibration')
        if row.get('origin_kind') != class_origin(item,cls) or row.get('origin_verified') is not True:
            raise ValueError('probe/lag clock origin must match the deployment law')
        if spec['evidence_kind'] == 'interrupted_measurement':
            verify_refs(row, evidence_root)
            if row.get('terminal_fate') not in ('committed','terminal_nonapply') or (outcome == 1) != (row['terminal_fate'] == 'committed'):
                raise ValueError('finite-horizon zero or pending is not an X0 label')
        if split != 'lag':
            if row.get('probe_eligibility_verified') is not True or set(row['views']) != set(item['families']):
                raise ValueError('calibration views must be collected in the qualified population')
            for name, values in row['views'].items():
                if len(values) != len(item['families'][name]) or any(v is not None and (type(v) is not int or v not in (0,1)) for v in values):
                    raise ValueError('each frozen view has one binary/BOT observation')
        if outcome == 1:
            lag = row.get('lag_upper_seconds')
            if lag is not None and (isinstance(lag,bool) or not isinstance(lag,(int,float)) or not math.isfinite(lag) or lag < 0):
                raise ValueError('lag must be a nonnegative interval upper end or censored null')
        groups.setdefault((sid,cls),[]).append(row)
    strata = []
    for item in spec['strata']:
        per = {}
        for cls in item['classes']:
            records = groups.get((item['id'],cls),[])
            buckets = {(split,x):[r for r in records if r['split']==split and r['X_backend']==x]
                       for split in ('pilot','calibration','lag') for x in (0,1)}
            quota = item['quota']
            for split in ('pilot','calibration'):
                for x in (0,1):
                    if len(buckets[split,x]) != quota[split+str(x)]:
                        raise ValueError('fixed acquisition quota incomplete/exceeded: '+item['id']+'/'+cls+'/'+split+str(x))
            if len(buckets['lag',1]) != quota.get('lag1',0) or buckets['lag',0]:
                raise ValueError('separate lag quota mismatch')
            take = lambda split,x: [r['views'] for r in buckets[split,x]]
            names, cap = list(item['families']), item['capabilities']
            if spec['mode'] == 'product':
                q = _bounds(take('calibration',1), take('calibration',0), names, delta, cap.get('nonce_analytic_qualified',False))
                fitted = dict(q=q, qh=max(q['hop1']['abs'].values()) if 'hop1' in names else None)
            else:
                fitted = fit_region(take('pilot',1), take('pilot',0), take('calibration',1),
                                    take('calibration',0), names, cap, delta, spec['mode'])
            lag_rows = [r for r in records if r['X_backend']==1 and r['split'] in item.get('lag_splits',['calibration'])]
            fitted['lag_seconds'] = sorted([r['lag_upper_seconds'] for r in lag_rows if r.get('lag_upper_seconds') is not None])
            fitted['lag_censored'] = sum(r.get('lag_upper_seconds') is None for r in lag_rows)
            fitted['counts'] = {split+str(x):len(v) for (split,x),v in buckets.items()}
            per[cls] = fitted
        strata.append(dict(**item, calibrated=per))
    result = dict(schema=SCHEMA, mode=spec['mode'], evidence_kind=spec['evidence_kind'],
                  alpha=spec['alpha'], beta=spec['beta'], K_total=k_total, delta=delta,
                  spec_sha256=canonical_sha(spec), spec=spec, effects=len(rows), strata=strata,
                  qualification_scope='conditional on stated domain/population/independence assumptions; file hashes do not prove them')
    result['content_sha256'] = canonical_sha(result)
    return result


def load_store(path, allow_synthetic=False):
    store = json.loads(Path(path).read_text(encoding='utf-8'))
    checksum = store.pop('content_sha256')
    if checksum != canonical_sha(store):
        raise ValueError('modified calibration store')
    store['content_sha256'] = checksum
    k = validate_spec(store)
    if store['K_total'] != k or store['delta'] != min(store['alpha'],store['beta'])/(10*k):
        raise ValueError('calibration multiplicity/budget mismatch')
    spec=store.get('spec')
    if not spec or canonical_sha(spec)!=store['spec_sha256'] or validate_spec(spec)!=k:
        raise ValueError('missing or changed acquisition spec')
    if any(store[key]!=spec[key] for key in ('schema','mode','evidence_kind','alpha','beta')):
        raise ValueError('store/spec metadata mismatch')
    if len(store['strata'])!=len(spec['strata']):raise ValueError('store/spec strata mismatch')
    def number(value,maximum=float('inf')):
        return type(value) in (int,float) and math.isfinite(value) and 0<=value<=maximum
    effect_count=0
    for item,definition in zip(store['strata'],spec['strata']):
        if {key:value for key,value in item.items() if key!='calibrated'}!=definition:
            raise ValueError('store/spec domain mismatch')
        if set(item['calibrated'])!=set(item['classes']):raise ValueError('missing calibrated class')
        for record in item['calibrated'].values():
            expected=dict(definition['quota'],lag0=0)
            if record['counts']!=expected:raise ValueError('acquisition count mismatch')
            effect_count+=sum(expected.values())
            lags=record['lag_seconds'];censored=record['lag_censored']
            nlag=sum(expected[split+'1'] for split in item.get('lag_splits',['calibration']))
            if (not all(number(v) for v in lags) or lags!=sorted(lags)
                    or type(censored) is not int or censored<0 or len(lags)+censored!=nlag):
                raise ValueError('invalid or incomplete lag table')
            if set(record['q'])!=set(item['families']):raise ValueError('missing calibrated family')
            for family in item['families']:
                for side in ('abs','com'):
                    levels=record['q'][family][side]
                    if (set(map(str,levels))!=set(map(str,numeric.levels(family)[side]))
                            or not all(number(v,1) for v in levels.values())):
                        raise ValueError('invalid family bound')
            if 'hop1' in item['families'] and not number(record['qh'],1):raise ValueError('invalid hop1 lag bound')
            if store['mode']!='product':
                for side in ('abs','com'):
                    previous=(-1,-1)
                    for risk,threshold in record[side+'_tab']:
                        if (not number(risk,2) or not number(threshold,1)
                                or risk<previous[0] or threshold<=previous[1]):
                            raise ValueError('invalid fixed-sequence table')
                        previous=(risk,threshold)
    if effect_count!=store['effects']:raise ValueError('effect denominator mismatch')
    if store['evidence_kind'] != 'interrupted_measurement' and not allow_synthetic:
        raise ValueError('synthetic fixtures cannot authorize production recovery')
    return store


def acquisition_plan(spec):
    """Best-case zero-event minima, not a promise of autonomous certification."""
    from sample_size import n_zero
    total=validate_spec(spec)
    delta=min(spec['alpha'],spec['beta'])/(10*total)
    rows=[]
    for item in spec['strata']:
        cap=item['capabilities'];local=cap.get('local',False)
        a_test=(.9 if local else .5)*spec['alpha']
        lag=(.2 if 'hop1' in item['families'] and cap.get('hop1_lag_independent') else .4)*spec['alpha']
        rows.append(dict(stratum=item['id'],classes=item['classes'],fixed_quota=item['quota'],
                         zero_event_joint_retry_minimum=n_zero(a_test,delta),
                         zero_event_joint_declare_minimum=n_zero(.9*spec['beta'],delta),
                         zero_exceedance_unconditional_wait_minimum=None if local else n_zero(lag,delta),
                         note='per outcome/class; product/source utility depends on family/region data; not a sufficient sample-size guarantee'))
    return dict(kind='fixed acquisition sizing reference',mode=spec['mode'],K_total=total,delta=delta,
                strata=rows,evidence_kind=spec['evidence_kind'],
                warning='Do not collect-until-pass or treat B0/eval/bootstrap as fresh calibration')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--effects', type=Path)
    parser.add_argument('--evidence-root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--size-plan',action='store_true',help='write best-case minima from fixed spec; do not compile labels')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('fresh output required')
    spec = json.loads(args.spec.read_text(encoding='utf-8'))
    if args.size_plan:
        result=acquisition_plan(spec)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(json.dumps(result,indent=2));return
    if args.effects is None:parser.error('--effects required to compile a store')
    rows = [json.loads(line) for line in args.effects.read_text(encoding='utf-8').splitlines() if line.strip()]
    store = compile_store(spec, rows, args.evidence_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(store, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps(dict(output=str(args.output), effects=len(rows), K_total=store['K_total'],
                         evidence_kind=store['evidence_kind'])))


if __name__ == '__main__':
    main()
