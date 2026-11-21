"""COF (b-log 21/11): Element co-failure with every denominator, from data already in artifact/results/real/.

One row per source: trials, trials where both families were read late, both wrong, exactly one wrong (a stale
screen counts here), no-observation, and trials with no family read at all. Campaign 1 is shown twice, as
re-scored (its five "co-failures" are no-observation, c1_rescored_cofailures.csv) and as first scored (five
co-failures), so the reader sees both. Families are not identical across campaigns: campaign 2 and the pilot read
the timeline row and the room-list digest; campaign 1 read the send-state indicator, the history copy count and
the room-list digest, and its pair here is indicator and copy count (the pair its five co-failures were scored on).
Discarded runs whose raw data are not in the artifact (campaign 1's stale accessibility-forwarder runs) are listed
with an unknown count. Writes artifact/results/real/cofailure_full/{cofailure_full.csv,SUMMARY.md}."""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REAL = ROOT / 'artifact/results/real'
OUT = REAL / 'cofailure_full'


def rows(path):
    with open(REAL / path, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def cp_upper_zero(n, conf=0.95):
    """Two-sided Clopper-Pearson upper bound for 0 events in n (the convention of c2_element_cofailure.csv)."""
    return 1 - ((1 - conf) / 2) ** (1 / n) if n else 1.0


def cp_upper(k, n, conf=0.95):
    """Two-sided Clopper-Pearson upper bound by bisection on the binomial CDF (stdlib only)."""
    if k == 0:
        return cp_upper_zero(n, conf)
    if k >= n:
        return 1.0
    from math import comb
    cdf = lambda p: sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))
    lo, hi, tail = k / n, 1.0, (1 - conf) / 2
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if cdf(mid) > tail else (lo, mid)
    return hi


def main():
    out = []
    # Campaign 2, recorded trials: timeline row and room-list digest, late reads.
    c2 = rows('campaign2/c2_element_per_trial_families.csv')
    both = [r for r in c2 if r['b_row_late'] != 'BOT' and r['c_digest_late'] != 'BOT']
    out.append(dict(source='campaign 2, recorded', families='row, digest', trials=len(c2), both_read=len(both),
                    both_wrong=sum(r['b_row_late'] == 'wrong' and r['c_digest_late'] == 'wrong' for r in both),
                    one_wrong=sum((r['b_row_late'] == 'wrong') != (r['c_digest_late'] == 'wrong') for r in both),
                    no_observation=len(c2) - len(both), no_read=0, note='the 101 trials of Table 3'))
    # Campaign 2 attempts that left no row (SUMMARY.md: six failed before the send, two committed, unknown lag).
    out.append(dict(source='campaign 2, attempts with no row', families='none', trials=8, both_read=0, both_wrong=0,
                    one_wrong=0, no_observation=0, no_read=8, note='6 failed before the send, 2 committed; no reads'))
    # Pilot (campaign 2 rig, not in the 101): late row verdict and room-list digest verdict.
    pil = rows('campaign2/pilot_element.csv')
    assert all(r['server_copies'] != '0' for r in pil)     # every pilot message was committed
    wrong = lambda v: v == 'absent'
    out.append(dict(source='pilot (not in the 101)', families='row, digest', trials=len(pil), both_read=len(pil),
                    both_wrong=sum(wrong(r['late_verdict']) and wrong(r['digest_verdict']) for r in pil),
                    one_wrong=sum(wrong(r['late_verdict']) != wrong(r['digest_verdict']) for r in pil),
                    no_observation=0, no_read=0, note='the one-wrong trial is a stale digest on a verified screen'))
    # Campaign 1, Element: indicator and copy count, late reads ('1' wrong, '0' right).
    c1 = [r for r in rows('e5_per_trial_family_errors.csv') if r['app'] == 'element']
    first_cof = [r for r in c1 if r['a_indicator_late'] == '1' and r['b_copycount_late'] == '1']
    resc = rows('campaign2/c1_rescored_cofailures.csv')
    assert len(resc) == len(first_cof) and all(r['rescored_a_b'].startswith('BOT') for r in resc)
    one1 = sum((r['a_indicator_late'] == '1') != (r['b_copycount_late'] == '1') for r in c1)
    out.append(dict(source='campaign 1, as re-scored', families='indicator, copy count', trials=len(c1),
                    both_read=len(c1) - len(first_cof), both_wrong=0, one_wrong=one1,
                    no_observation=len(first_cof), no_read=0, note='five co-failures re-scored as no-observation'))
    out.append(dict(source='campaign 1, as first scored', families='indicator, copy count', trials=len(c1),
                    both_read=len(c1), both_wrong=len(first_cof), one_wrong=one1, no_observation=0, no_read=0,
                    note='screen identity was not logged'))
    out.append(dict(source='campaign 1, stale-forwarder runs', families='', trials='unknown', both_read='',
                    both_wrong='', one_wrong='', no_observation='', no_read='',
                    note='discarded; raw data not in the artifact'))
    for r in out:
        if isinstance(r['both_read'], int) and r['both_read']:
            r['both_wrong_ci95_hi_pct'] = f"{100 * cp_upper(r['both_wrong'], r['both_read']):.2f}"
        else:
            r['both_wrong_ci95_hi_pct'] = ''
    # Pooled views over the sources with reads (campaign 2 recorded, pilot, campaign 1 in each scoring).
    pools = {}
    for tag, c1row in (('pooled, campaign 1 re-scored', out[3]), ('pooled, campaign 1 as first scored', out[4])):
        parts = [out[0], out[2], c1row]
        n, k = sum(p['both_read'] for p in parts), sum(p['both_wrong'] for p in parts)
        pools[tag] = (k, n, cp_upper(k, n))
    OUT.mkdir(parents=True, exist_ok=True)
    cols = ['source', 'families', 'trials', 'both_read', 'both_wrong', 'one_wrong', 'no_observation', 'no_read',
            'both_wrong_ci95_hi_pct', 'note']
    with open(OUT / 'cofailure_full.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator='\n')
        w.writeheader()
        w.writerows(out)
        for tag, (k, n, hi) in pools.items():
            w.writerow(dict(source=tag, families='mixed', both_read=n, both_wrong=k,
                            both_wrong_ci95_hi_pct=f'{100 * hi:.2f}', note='sum of the rows with reads'))
    lines = ['# Element co-failure with every denominator (COF, b-log 21/11)', '',
             'Generated by `testbed/cofailure_full.py` from data already in `artifact/results/real/`. No new runs.', '',
             '| Source | Families | Trials | Both read | Both wrong | One wrong | No-observation | No read | CI95 hi, both wrong (%) |',
             '|---|---|---|---|---|---|---|---|---|']
    for r in out:
        lines.append('| ' + ' | '.join(str(r[c]) for c in cols[:-1]) + ' |')
    lines.append('')
    for tag, (k, n, hi) in pools.items():
        lines.append(f'- {tag}: {k}/{n} both wrong, two-sided 95% Clopper-Pearson upper bound {100 * hi:.2f}%.')
    lines += ['', 'Families differ by campaign (see the script docstring), so the pooled rows are a summary, not one '
              'experiment. A stale screen shows up as one family wrong, not two.']
    (OUT / 'SUMMARY.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))


if __name__ == '__main__':
    sys.exit(main())
