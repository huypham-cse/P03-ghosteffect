"""GUI history-item digest from pre-tap counts, as draft §5.3.

Exact task fields + verified outgoing/acknowledged rows. Layout/XML hashes are
capture identities, not semantic digests. Concurrent look-alikes remain a
calibration challenge; this reader does not consult backend truth or timestamps
invented from row positions.
"""
from collections import Counter
import hashlib
import json
import unicodedata
import xml.etree.ElementTree as ET

from ui import select, digest


def normalized(text):
    return unicodedata.normalize('NFC',text)  # no deletion of nonce or user content


def history_snapshot(xml,capture,profile,match_fields,bottom_receipt):
    def bot(reason):return dict(verdict='BOT',reason=reason)
    if not profile.get('frozen') or not profile.get('profile_id'):
        return bot('unfrozen_profile')
    if not capture.get('stable_tree') or not capture.get('same_foreground') or digest(xml)!=capture.get('tree_sha256'):
        return bot('invalid_capture')
    component=capture.get('foreground_after','')
    if not component.startswith(profile['package']+'/') or profile.get('activity') and component!=profile['activity']:
        return bot('wrong_foreground')
    if not bottom_receipt or bottom_receipt.get('tree_sha256')!=capture['tree_sha256'] or bottom_receipt.get('direction')!='latest' or bottom_receipt.get('unchanged_swipes',0)<2:
        return bot('history_coverage_not_verified')
    root=ET.fromstring(xml)
    if any(len(select(root,profile.get(name)))!=1 for name in ('account','title','timeline')) or not select(root,profile.get('anchor')):
        return bot('identity_or_anchor_not_verified')
    timeline=select(root,profile['timeline'])[0]
    field_map=profile.get('history_fields',{})
    if not match_fields or not set(match_fields).issubset(field_map):
        return bot('missing_semantic_field_map')
    items=[]
    for row in select(timeline,profile.get('row')):
        if not select(row,profile.get('outgoing')) or not select(row,profile.get('acknowledged')):
            continue
        if any(select(row,x) for x in profile.get('exclude',[])):
            continue
        fields={}
        for name,selector in field_map.items():
            values=select(row,selector)
            if len(values)!=1:
                return bot('ambiguous_or_missing_history_field')
            node=values[0]
            fields[name]=normalized(node.get('text','') or node.get('content-desc',''))
        if all(fields[k]==normalized(v) for k,v in match_fields.items()):
            items.append(json.dumps(fields,sort_keys=True,ensure_ascii=True,separators=(',',':')))
    counts=dict(sorted(Counter(items).items()))
    snapshot=dict(profile_id=profile['profile_id'],match_fields=match_fields,items=counts,
                  matches=sum(counts.values()),capture_sha256=capture['tree_sha256'])
    snapshot['semantic_sha256']=hashlib.sha256(json.dumps(counts,sort_keys=True).encode()).hexdigest()
    return dict(verdict='SNAPSHOT',snapshot=snapshot)


def read_digest(before,after):
    if before.get('verdict')!='SNAPSHOT' or after.get('verdict')!='SNAPSHOT':
        return dict(verdict='BOT',reason='missing_verified_pre_or_post_snapshot')
    old,new=before['snapshot'],after['snapshot']
    if old['profile_id']!=new['profile_id'] or old['match_fields']!=new['match_fields']:
        return dict(verdict='BOT',reason='digest_domain_mismatch')
    # A disappearing old item invalidates the count baseline. A new matching
    # item can be concurrent: calibration must account for that false positive.
    if any(new['items'].get(key,0)<count for key,count in old['items'].items()):
        return dict(verdict='BOT',reason='history_baseline_changed')
    added=new['matches']-old['matches']
    return dict(verdict='com' if added>0 else 'abs',added=added,
                lookalike=old['matches']>0,scope='calibrated GUI family observation, not backend proof')
