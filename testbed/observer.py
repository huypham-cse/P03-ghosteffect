"""GUI adapters for Algorithm 1 families, separate from backend grading.

Actual frozen profiles map each family/view to navigation and status selectors.
VLM verifier sees one view and effect description, never agent reasoning or
backend receipts. Runtime persistence/read-once is owned by HostController.
"""
import json
from pathlib import Path
import re
import uuid
import xml.etree.ElementTree as ET

from app_driver import navigate
from ui import select,read_nonce,scroll_latest
from probes import history_snapshot,read_digest,normalized


def bound_rows(root,config,profile,nonce):
    """Bind GUI status to this effect; unrelated global status is not a vote."""
    rows=select(root,config.get('entry_selector'))
    if nonce:
        pattern=re.compile(r'(?<![A-Za-z0-9])'+re.escape(nonce)+r'(?![A-Za-z0-9])')
        return [row for row in rows if pattern.search(' '.join(n.get('text','')+' '+n.get('content-desc','') for n in row.iter('node')))]
    fields=config.get('match_fields',{})
    selectors=profile.get('history_fields',{})
    if not fields or not set(fields).issubset(selectors):return []
    matching=[]
    for row in rows:
        values={name:select(row,selectors[name]) for name in fields}
        if all(len(values[k])==1 and normalized(values[k][0].get('text','') or values[k][0].get('content-desc',''))==normalized(v) for k,v in fields.items()):
            matching.append(row)
    return matching


class GUIObserver:
    def __init__(self,adb,profile,description,nonce,pre_snapshots,output,verifier=None):
        if not profile.get('frozen') or not profile.get('profile_id'):
            raise ValueError('actual frozen per-app profile required')
        self.adb,self.profile,self.description,self.nonce=adb,profile,description,nonce
        self.pre_snapshots,self.output,self.verifier=pre_snapshots,Path(output),verifier
        self.output.mkdir(parents=True,exist_ok=False)

    def verify_context(self):
        component=self.adb.foreground()
        if not component.startswith(self.profile['package']+'/'):
            return False
        if self.profile.get('activity') and component!=self.profile['activity']:
            return False
        root=ET.fromstring(self.adb.tree())
        return all(len(select(root,self.profile.get(name)))==1 for name in ('account','title'))

    def capture_view(self,family,view):
        config=self.profile.get('views',{}).get(family,{}).get(view)
        if not config:return None
        navigate(self.adb,self.profile,config.get('actions',[]),self.nonce or None)
        directory=self.output/('view-'+uuid.uuid4().hex)
        if config.get('verified_bottom'):
            view_profile=dict(self.profile,**config.get('reader_overrides',{}))
            data,meta,bottom=scroll_latest(self.adb,view_profile,directory)
            capture=Path(bottom['capture_path'])
        else:
            meta=self.adb.capture(directory)
            data=(directory/'tree.xml').read_bytes();bottom=None;capture=directory
            view_profile=dict(self.profile,**config.get('reader_overrides',{}))
        return config,data,meta,bottom,capture,view_profile

    def read(self,family,view):
        captured=self.capture_view(family,view)
        if captured is None:return None
        config,xml,meta,bottom,directory,profile=captured
        if not self.verify_context() or not meta['stable_tree'] or not meta['same_foreground']:
            return None
        if family=='nonce':
            result=read_nonce(xml,meta,profile,self.nonce,bottom)
        elif family=='digest':
            after=history_snapshot(xml,meta,profile,config.get('match_fields',{}),bottom)
            result=read_digest(self.pre_snapshots.get(view,{}),after)
        elif family=='hop1':
            if not self.profile.get('hop1_qualified'):
                return None
            if not self.nonce:
                # No invented per-row timestamps: compare verified semantic
                # counts captured before the tap. Reader overrides select the
                # qualified local entry states, not rendered server history.
                after=history_snapshot(xml,meta,profile,config.get('match_fields',{}),bottom)
                result=read_digest(self.pre_snapshots.get('hop1',{}).get(view,{}),after)
                if result.get('added',0)>1:
                    result=dict(verdict='BOT',reason='multiple_new_local_entries',duplicate_candidate=True)
            else:
                root=ET.fromstring(xml)
                matching=bound_rows(root,config,profile,self.nonce)
                if len(matching)>1:return None
                if matching:
                    com=select(matching[0],config.get('com_selector'))
                    result=dict(verdict='com' if com else 'BOT')
                else:
                    # "abs" is only a per-view observation; Readout combines it.
                    valid=len(select(root,config.get('empty_or_complete_selector')))==1
                    result=dict(verdict='abs' if valid else 'BOT')
        elif family=='vlm':
            if self.verifier is None:return None
            prompt=('Read only this app screenshot. Is the following effect shown as completed in the verified account history? '
                    'Draft, failed, pending and merely composed entries do not establish completion. '
                    'Return exactly one JSON object: {"verdict":"com"}, {"verdict":"abs"}, or {"verdict":"BOT"}. '
                    'Use BOT for wrong/unclear screen or insufficient evidence. Effect description:\n'+self.description)
            answer,_,raw=self.verifier.predict_mm(prompt,[(directory/'screen.png').read_bytes()])
            try:
                parsed=json.loads(answer)
                if set(parsed)!={'verdict'} or parsed['verdict'] not in ('com','abs','BOT'):
                    return None
                result=parsed
            except (ValueError,TypeError):return None
        else:raise ValueError('unsupported family')
        if not self.verify_context():return None
        (directory/'probe.json').write_text(json.dumps(dict(family=family,view=view,result=result),indent=2),encoding='utf-8')
        return 1 if result['verdict']=='com' else 0 if result['verdict']=='abs' else None

    def monitor(self):
        if not self.profile.get('hop1_qualified') or not self.profile.get('monitor'):
            return dict(state='stuck',reason='no_qualified_monitor')
        config=self.profile['monitor']
        navigate(self.adb,self.profile,config.get('actions',[]))
        if not self.verify_context():return dict(state='stuck',reason='identity_changed')
        root=ET.fromstring(self.adb.tree())
        matching=bound_rows(root,config,self.profile,self.nonce)
        if len(matching)!=1:
            return dict(state='stuck',reason='no_unique_effect_bound_monitor_entry')
        # With no nonce even a unique old look-alike must not be monitored as
        # this issue. Only zero matching entries before the tap permits binding.
        if not self.nonce:
            before=self.pre_snapshots.get('hop1',{}).get(config.get('baseline_view'),{})
            if (before.get('verdict')!='SNAPSHOT' or before['snapshot']['matches']!=0
                    or before['snapshot']['profile_id']!=self.profile['profile_id']
                    or before['snapshot']['match_fields']!=config.get('match_fields')):
                return dict(state='stuck',reason='monitor_entry_not_newly_bound')
        states=[state for state in ('acked','failed','pending') if select(matching[0],config.get(state+'_selector'))]
        return dict(state=states[0] if len(states)==1 else 'stuck',end_to_end_ready=False,
                    scope='fallible local GUI status, not backend acknowledgement')
