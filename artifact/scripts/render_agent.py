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
    receipts = [json.load(open(p, encoding='utf-8')) for p in paths if os.path.exists(p)]
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
