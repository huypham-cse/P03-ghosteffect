# render_agent.py -- exec'd by render_real.py (B-10, B-11). Writes the \Agent* and \LabelTrial* macros of the
# B contract (team/b-log.md, 12/11, 44 names; 14/11 adds the 3 alias counts) and generated/tab_agent.tex from
# artifact/results/real/agent/ (episodes.csv, label_cost.csv, freeze.json, receipts/). Kind of number: LLM-agent
# experiment. Before the runs every macro is ??. Counts use phase=scheduled rows, one per scheduled_index (its
# last attempt); Dev macros use phase=dev rows. Valid means outcome != INVALID. Rates and medians are over valid
# episodes, rates with Wilson 95% intervals. Alias counts (local_model.py renames "type" to "input_text") are
# over all scheduled episodes, from the receipt counters model_calls and type_alias_calls.

AGENT_TEXT = ('AgentFramework', 'AgentModel', 'AgentServing', 'AgentHost', 'AgentHEvalS', 'AgentMaxSteps')
AGENT_COUNTS = ('AgentScheduledN', 'AgentValidN', 'AgentInvalidN', 'AgentRerunN', 'AgentInvalidNoCommitN',
                'AgentInvalidNoFaultN', 'AgentInvalidMeasureN', 'AgentResentN', 'AgentDupN', 'AgentResentNoDupN',
                'AgentDoneNoResendN', 'AgentAskedN', 'AgentTaskFailN', 'AgentNosentValidN', 'AgentSentValidN',
                'AgentNosentDupN', 'AgentSentDupN', 'AgentDevN', 'AgentDevSuccessN')
AGENT_RATES = ('AgentResentPct', 'AgentResentLo', 'AgentResentHi', 'AgentDupPct', 'AgentDupLo', 'AgentDupHi',
               'AgentAskedPct', 'AgentWallMedS', 'AgentStepsAfterMed')
AGENT_ALIAS = ('AgentModelCallsN', 'AgentAliasCallsN', 'AgentAliasEpisodesN')
LABEL_COMPONENTS = ('reset', 'compose', 'fault', 'relaunch', 'observation', 'grading')
LABEL_MACROS = ('LabelTrialMinS', 'LabelTrialMedS', 'LabelTrialMaxS', 'LabelTrialN') + tuple(
    'LabelTrial%sMedS' % c.capitalize() for c in LABEL_COMPONENTS)
AGENT_MACROS = AGENT_TEXT + AGENT_COUNTS + AGENT_RATES + AGENT_ALIAS + LABEL_MACROS
assert len(AGENT_MACROS) == 47
MEASUREMENT_REASONS = ('measurement_error:', 'grading_failed:', 'harness_timeout')


def render_agent():
    import json
    import statistics
    folder = os.path.join(REAL, 'agent')
    if not os.path.exists(os.path.join(folder, 'episodes.csv')):
        for name in AGENT_MACROS:
            M(name, '??')
        W('tab_agent.tex', '% no agent episodes yet (artifact/results/real/agent/episodes.csv)\n')
        return
    with open(os.path.join(folder, 'episodes.csv'), encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    with open(os.path.join(folder, 'label_cost.csv'), encoding='utf-8', newline='') as f:
        cost = {r['component']: r for r in csv.DictReader(f)}
    with open(os.path.join(folder, 'freeze.json'), encoding='utf-8') as f:
        freeze = json.load(f)
    scheduled = [r for r in rows if r['phase'] == 'scheduled']
    last = {}
    for r in sorted(scheduled, key=lambda r: int(r['attempt'])):
        last[r['scheduled_index']] = r
    final = list(last.values())
    valid = [r for r in final if r['outcome'] != 'INVALID']
    n = len(valid)
    count = lambda rs, *outcomes: sum(r['outcome'] in outcomes for r in rs)

    def pct(k):
        return 'N/A' if n == 0 else f'{100 * k / n:.1f}'

    def wilson(k, z=1.959964):
        if n == 0:
            return 'N/A', 'N/A'
        p, d = k / n, 1 + z * z / n
        c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return f'{100 * max(0.0, c - h):.1f}', f'{100 * min(1.0, c + h):.1f}'

    def median(values, digits):
        values = [float(v) for v in values if v != '']
        if not values:
            return 'N/A'
        m = statistics.median(values)
        return str(int(round(m))) if digits == 0 else f'{m:.{digits}f}'

    M('AgentFramework', freeze['agent']['framework'].upper())
    M('AgentModel', freeze['model']['repo_id'].split('/')[-1])
    M('AgentServing', freeze['model']['engine'] + ', BF16')
    M('AgentHost', freeze['host'])
    M('AgentHEvalS', int(freeze['fault']['h_eval_s']))
    M('AgentMaxSteps', freeze['agent']['max_steps'])
    reasons = [r['invalid_reason'] for r in final if r['outcome'] == 'INVALID']
    resent = count(valid, 'RESENT_DUPLICATE', 'RESENT_BUT_NO_DUP')
    dup = count(valid, 'RESENT_DUPLICATE')
    asked = count(valid, 'ASKED_OR_STOPPED')
    by_config = lambda config: [r for r in valid if r['config'] == config]
    dev = [r for r in rows if r['phase'] == 'dev']
    for name, value in (
            ('AgentScheduledN', len(final)), ('AgentValidN', n), ('AgentInvalidN', len(final) - n),
            ('AgentRerunN', sum(r['attempt'] == '2' for r in scheduled)),
            ('AgentInvalidNoCommitN', reasons.count('original_not_committed')),
            ('AgentInvalidNoFaultN', reasons.count('no_fault_receipt')),
            ('AgentInvalidMeasureN', sum(x.startswith(MEASUREMENT_REASONS) for x in reasons)),
            ('AgentResentN', resent), ('AgentDupN', dup), ('AgentResentNoDupN', count(valid, 'RESENT_BUT_NO_DUP')),
            ('AgentDoneNoResendN', count(valid, 'DECLARED_DONE_NO_RESEND')), ('AgentAskedN', asked),
            ('AgentTaskFailN', count(valid, 'TASK_FAILURE')),
            ('AgentNosentValidN', len(by_config('nosent'))), ('AgentSentValidN', len(by_config('sent'))),
            ('AgentNosentDupN', count(by_config('nosent'), 'RESENT_DUPLICATE')),
            ('AgentSentDupN', count(by_config('sent'), 'RESENT_DUPLICATE')),
            ('AgentDevN', len(dev)),
            ('AgentDevSuccessN', sum(r['backend_copies_at_horizon'] == '1' and r['distinct_message_ids'] == '1'
                                     and r['agent_final_status'] == 'done' for r in dev))):
        M(name, value)
    M('AgentResentPct', pct(resent))
    M('AgentResentLo', wilson(resent)[0])
    M('AgentResentHi', wilson(resent)[1])
    M('AgentDupPct', pct(dup))
    M('AgentDupLo', wilson(dup)[0])
    M('AgentDupHi', wilson(dup)[1])
    M('AgentAskedPct', pct(asked))
    M('AgentWallMedS', median([r['wall_clock_s'] for r in valid], 0))
    M('AgentStepsAfterMed', median([r['steps_after_restart'] for r in valid], 1))
    paths = [os.path.join(folder, 'receipts', r['episode_id'] + '.json') for r in final]
    receipts = []
    for p in paths:
        if os.path.exists(p):
            with open(p, encoding='utf-8') as f:
                receipts.append(json.load(f))
    if len(receipts) == len(final) and all('model_calls' in r for r in receipts):
        M('AgentModelCallsN', sum(r['model_calls'] for r in receipts))
        M('AgentAliasCallsN', sum(r['type_alias_calls'] for r in receipts))
        M('AgentAliasEpisodesN', sum(r['type_alias_calls'] > 0 for r in receipts))
    else:
        for name in AGENT_ALIAS:
            M(name, 'N/A')
    total = cost['total']
    if int(total['n']):
        M('LabelTrialMinS', str(int(round(float(total['min_s'])))))
        M('LabelTrialMedS', str(int(round(float(total['median_s'])))))
        M('LabelTrialMaxS', str(int(round(float(total['max_s'])))))
    else:
        for name in ('LabelTrialMinS', 'LabelTrialMedS', 'LabelTrialMaxS'):
            M(name, 'N/A')
    M('LabelTrialN', total['n'])
    for c in LABEL_COMPONENTS:
        row = cost[c]
        M('LabelTrial%sMedS' % c.capitalize(), f"{float(row['median_s']):.1f}" if int(row['n']) else 'N/A')

    def cells(*outcomes):
        return ' & '.join(str(count(rs, *outcomes)) for rs in (by_config('nosent'), by_config('sent'), valid))
    W('tab_agent.tex', r'''\begin{table}[t]
\caption{M3A on Qwen2.5-VL-7B after a lost SMTP reply and a K-9 force-stop: outcome of each valid scheduled
episode, from the backend at relaunch $+\,H_{\mathrm{eval}}$ (LLM-agent experiment).}
\label{tab:agent}
\centering
\footnotesize
\begin{tabular}{@{}lccc@{}}
\toprule
Outcome & no Sent & Sent & all \\
\midrule
Resent, duplicate at the backend & ''' + cells('RESENT_DUPLICATE') + r''' \\
Resent, no duplicate & ''' + cells('RESENT_BUT_NO_DUP') + r''' \\
Declared done, no resend & ''' + cells('DECLARED_DONE_NO_RESEND') + r''' \\
Asked or stopped & ''' + cells('ASKED_OR_STOPPED') + r''' \\
Task failure & ''' + cells('TASK_FAILURE') + r''' \\
\midrule
Valid episodes & ''' + ' & '.join(str(len(rs)) for rs in (by_config('nosent'), by_config('sent'), valid)) + r''' \\
\bottomrule
\end{tabular}
\end{table}
''')
    guarded = render_guarded(final, valid, json)
    render_rules(guarded, json)
    render_arm('agent_t3a', 'AgentText', valid, json)
    render_arm('agent_killagent', 'AgentKill', valid, json)


def fisher_two_sided(a, b, c, d):
    """Exact two-sided p for the 2x2 table [[a, b], [c, d]] (sum of tables no more likely than the observed)."""
    from math import comb
    r1, c1, n = a + b, a + c, a + b + c + d
    p = lambda x: comb(c1, x) * comb(n - c1, r1 - x) / comb(n, r1)
    observed = p(a)
    return min(1.0, sum(p(x) for x in range(max(0, r1 + c1 - n), min(r1, c1) + 1) if p(x) <= observed * (1 + 1e-9)))


def render_guarded(base_final, base_valid, json):
    """Guarded arm (GhostEffect at the M3A boundary, agent_study_guarded.freeze.json), written only once its
    data exist: the AgentGuard macros. Primary: RESENT_DUPLICATE over valid scheduled episodes, Wilson 95%, and the
    exact two-sided Fisher p against the baseline arm. Secondary: asks, classifier misses, simulated-user errors."""
    folder = os.path.join(REAL, 'agent_guarded')
    if not os.path.exists(os.path.join(folder, 'episodes.csv')):
        return []
    with open(os.path.join(folder, 'episodes.csv'), encoding='utf-8', newline='') as f:
        rows = [r for r in csv.DictReader(f) if r['phase'] == 'scheduled']
    last = {}
    for r in sorted(rows, key=lambda r: int(r['attempt'])):
        last[r['scheduled_index']] = r
    final = list(last.values())
    valid = [r for r in final if r['outcome'] != 'INVALID']
    receipts = {}
    for r in final:
        with open(os.path.join(folder, 'receipts', r['episode_id'] + '.json'), encoding='utf-8') as f:
            receipts[r['episode_id']] = json.load(f).get('guard') or {}
    restart = lambda r: receipts[r['episode_id']].get('restart') or {}
    n, dup = len(valid), sum(r['outcome'] == 'RESENT_DUPLICATE' for r in valid)
    base_dup = sum(r['outcome'] == 'RESENT_DUPLICATE' for r in base_valid)
    z = 1.959964
    if n:
        p, d = dup / n, 1 + z * z / n
        c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        lo, hi, pct = f'{100 * max(0.0, c - h):.1f}', f'{100 * min(1.0, c + h):.1f}', f'{100 * dup / n:.1f}'
    else:
        lo = hi = pct = 'N/A'
    fisher = fisher_two_sided(dup, n - dup, base_dup, len(base_valid) - base_dup)
    for name, value in (
            ('AgentGuardScheduledN', len(final)), ('AgentGuardValidN', n), ('AgentGuardInvalidN', len(final) - n),
            ('AgentGuardDupN', dup), ('AgentGuardDupPct', pct), ('AgentGuardDupLo', lo), ('AgentGuardDupHi', hi),
            ('AgentGuardAskN', sum(restart(r).get('decision') == 'ASK' for r in valid)),
            ('AgentGuardNoCandN', sum(restart(r).get('decision') == 'NO_CANDIDATE' for r in valid)),
            ('AgentGuardUserErrN', sum(receipts[r['episode_id']].get('user_error') == 1 and restart(r).get('decision') == 'ASK'
                                  for r in valid)),
            ('AgentGuardFisherP', f'{fisher:.3f}' if fisher >= 1e-3 else '$<$0.001')):
        M(name, value)
    return valid


def arm_rows(folder, json):
    with open(os.path.join(folder, 'episodes.csv'), encoding='utf-8', newline='') as f:
        rows = [r for r in csv.DictReader(f) if r['phase'] == 'scheduled']
    last = {}
    for r in sorted(rows, key=lambda r: int(r['attempt'])):
        last[r['scheduled_index']] = r
    final = list(last.values())
    receipts = {}
    for r in final:
        with open(os.path.join(folder, 'receipts', r['episode_id'] + '.json'), encoding='utf-8') as f:
            receipts[r['episode_id']] = json.load(f).get('guard') or {}
    return final, [r for r in final if r['outcome'] != 'INVALID'], receipts


def render_rules(guarded_valid, json):
    """Same-evidence rules arm (agent_study_rules.freeze.json, Sent configuration only), written once its data exist:
    the AgentRules macros. Primary: RESENT_DUPLICATE over valid episodes, Wilson 95%, and the exact two-sided Fisher
    p against the guarded arm's Sent-configuration episodes (AgentGuardSent macros). Secondary: retries, asks."""
    folder = os.path.join(REAL, 'agent_rules')
    if not os.path.exists(os.path.join(folder, 'episodes.csv')):
        return
    final, valid, receipts = arm_rows(folder, json)
    restart = lambda r: receipts[r['episode_id']].get('restart') or {}
    n, dup = len(valid), sum(r['outcome'] == 'RESENT_DUPLICATE' for r in valid)
    sent = [r for r in guarded_valid if r['config'] == 'sent']
    sent_dup = sum(r['outcome'] == 'RESENT_DUPLICATE' for r in sent)
    z = 1.959964
    if n:
        p, d = dup / n, 1 + z * z / n
        c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        lo, hi, pct = f'{100 * max(0.0, c - h):.1f}', f'{100 * min(1.0, c + h):.1f}', f'{100 * dup / n:.1f}'
    else:
        lo = hi = pct = 'N/A'
    fisher = fisher_two_sided(dup, n - dup, sent_dup, len(sent) - sent_dup)
    for name, value in (
            ('AgentRulesScheduledN', len(final)), ('AgentRulesValidN', n), ('AgentRulesInvalidN', len(final) - n),
            ('AgentRulesDupN', dup), ('AgentRulesDupPct', pct), ('AgentRulesDupLo', lo), ('AgentRulesDupHi', hi),
            ('AgentRulesRetryN', sum(restart(r).get('decision') == 'RETRY' for r in valid)),
            ('AgentRulesAskN', sum(restart(r).get('decision') == 'ASK' for r in valid)),
            ('AgentRulesNoCandN', sum(restart(r).get('decision') == 'NO_CANDIDATE' for r in valid)),
            ('AgentGuardSentValidN', len(sent)), ('AgentGuardSentDupN', sent_dup),
            ('AgentRulesFisherP', f'{fisher:.3f}' if fisher >= 1e-3 else '$<$0.001')):
        M(name, value)


def render_arm(name, prefix, base_valid, json):
    """Unguarded arm with another agent (agent_t3a: T3A, AgentText macros) or another fault (agent_killagent: agent killed,
    K-9 kept running, AgentKill macros), written once its data exist. Primary: RESENT_DUPLICATE over valid scheduled
    episodes with Wilson 95%. Secondary: the exact two-sided Fisher p against the M3A force-stop baseline, the other
    outcome classes, and the alias counters of the receipts."""
    folder = os.path.join(REAL, name)
    if not os.path.exists(os.path.join(folder, 'episodes.csv')):
        return
    final, valid, _ = arm_rows(folder, json)
    calls = alias = 0
    for r in final:
        with open(os.path.join(folder, 'receipts', r['episode_id'] + '.json'), encoding='utf-8') as f:
            receipt = json.load(f)
        calls += receipt.get('model_calls', 0)
        alias += receipt.get('type_alias_calls', 0)
    n = len(valid)
    count = lambda *outcomes: sum(r['outcome'] in outcomes for r in valid)
    dup, base_dup = count('RESENT_DUPLICATE'), sum(r['outcome'] == 'RESENT_DUPLICATE' for r in base_valid)
    z = 1.959964
    if n:
        p, d = dup / n, 1 + z * z / n
        c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        lo, hi, pct = f'{100 * max(0.0, c - h):.1f}', f'{100 * min(1.0, c + h):.1f}', f'{100 * dup / n:.1f}'
    else:
        lo = hi = pct = 'N/A'
    fisher = fisher_two_sided(dup, n - dup, base_dup, len(base_valid) - base_dup)
    for key, value in (
            ('ScheduledN', len(final)), ('ValidN', n), ('InvalidN', len(final) - n), ('DupN', dup), ('DupPct', pct),
            ('DupLo', lo), ('DupHi', hi), ('DoneNoResendN', count('DECLARED_DONE_NO_RESEND')),
            ('AskedN', count('ASKED_OR_STOPPED')), ('TaskFailN', count('TASK_FAILURE')),
            ('ModelCallsN', calls), ('AliasCallsN', alias),
            ('FisherP', f'{fisher:.3f}' if fisher >= 1e-3 else '$<$0.001')):
        M(prefix + key, value)
