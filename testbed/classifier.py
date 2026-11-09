"""Conservative GUI commit-point classifier from draft §5.1.

Lexicon is configurable and locale keyed; this is a measurable classifier, not
an assertion that all risky actions are covered. False negatives must remain in
native/unprotected outcomes and in the classifier audit denominator.
"""
import re
import xml.etree.ElementTree as ET

LEXICON={
    'en': ('send','pay','save','post','book','confirm','delete','submit','transfer'),
    'vi': ('gửi','thanh toán','lưu','đăng','đặt','xác nhận','xóa','chuyển tiền'),
}


def classify(action,xml,locale='en',structured_effect=False,lexicon=None):
    if structured_effect:
        return dict(commit_candidate=True,reason='structured_plan_effect',protected=False)
    words=(lexicon or LEXICON).get(locale)
    if words is None:
        return dict(commit_candidate=None,reason='unsupported_locale',protected=False)
    kind=action.get('action_type')
    if kind not in ('tap','click','long_press','keyboard_enter'):
        return dict(commit_candidate=False,reason='not_classified_commit_action',protected=False)
    if kind=='keyboard_enter':
        return dict(commit_candidate=True,reason='conservative_keyboard_commit_candidate',protected=False)
    x,y=action.get('x'),action.get('y')
    if type(x) not in (int,float) or type(y) not in (int,float):
        return dict(commit_candidate=None,reason='missing_pixel_coordinates',protected=False)
    try:
        root=ET.fromstring(xml)
    except ET.ParseError:
        return dict(commit_candidate=None,reason='invalid_accessibility_capture',protected=False)
    targets=[]
    for node in root.iter('node'):
        bounds=re.fullmatch(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',node.get('bounds',''))
        if not bounds:continue
        left,top,right,bottom=map(int,bounds.groups())
        if left<=x<right and top<=y<bottom:
            targets.append(node)
    if not targets:
        return dict(commit_candidate=None,reason='no_verified_target',protected=False)
    # Text/content-desc on child labels and resource IDs on clickable ancestors
    # both count; do not scan unrelated labels outside the action target.
    text=' '.join(n.get(k,'') for n in targets for k in ('text','content-desc','resource-id'))
    text=re.sub(r'([a-z])([A-Z])',r'\1 \2',text).casefold()
    text=re.sub(r'[_/:.\-]+',' ',text)
    found=[word for word in words if re.search(r'(?<!\w)'+re.escape(word.casefold())+r'(?!\w)',text)]
    return dict(commit_candidate=bool(found),reason='locale_lexicon' if found else 'no_lexicon_match',
                matched_terms=found,protected=False)


def commit_slot_id(run_id,task_id,slot):
    """Stable identity supplied by the task/structured action boundary, not text."""
    import hashlib,json
    if not all(isinstance(v,str) and v for v in (run_id,task_id,slot)):
        raise ValueError('run/task/commit-slot identity required')
    return 'effect-'+hashlib.sha256(json.dumps([run_id,task_id,slot]).encode()).hexdigest()[:32]
