"""SYNTHETIC stand-in for the vLLM endpoint: rehearse agent_episode.py --framework m3a without a GPU.

Answers the three calls the harness makes (/version, /v1/models, /v1/chat/completions) and replies to
native M3A prompts with a fixed rule: open compose, fill recipient, subject and text from the goal,
send (and "Send and Delete" on the no-Sent dialog), then report done. A fresh agent after the relaunch
does the same again, so a rehearsal of the fault case should end RESENT_DUPLICATE.
Its SERVING.json carries synthetic=true; agent_episode.py then writes study_data=false. Never study data.
"""
import argparse
import ast
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import time

from serve_model import QWEN_IMAGE_POLICY
from setup_models import LOCK, ROOT

ELEMENT = re.compile(r'^UI element (\d+): (\{.*\})\s*$', re.M)


def elements(prompt):
    found = []
    for match in ELEMENT.finditer(prompt):
        try:
            found.append(ast.literal_eval(match.group(2)))
        except (ValueError, SyntaxError):
            pass
    return found


def label(element):
    return ' '.join(str(element.get(k) or '') for k in ('text', 'content_description', 'hint_text')).strip().lower()


def decide(prompt):
    """(marker, action) for one M3A action prompt."""
    goal = re.search(r'The current user goal/request is: (.*)', prompt).group(1)
    recipient = re.search(r'[\w.+-]+@[\w.-]+\.\w+', goal).group(0)
    subject = re.search(r'subject "([^"]*)"', goal).group(1)
    text = re.search(r'text "([^"]*)"', goal).group(1)
    done = set(re.findall(r'fake:(\w+) done', prompt))
    els = elements(prompt)
    by_label = lambda *names: next((e['index'] for e in els if any(
        str(e.get(k) or '').strip().lower() in names for k in ('text', 'content_description'))), None)
    dialog = by_label('send and delete')
    if dialog is not None:
        return 'dialog', dict(action_type='click', index=dialog)
    send = by_label('send')
    editable = [e for e in els if e.get('is_editable')]
    if send is not None and editable:
        subject_field = next((e for e in editable if 'subject' in label(e)), None)
        body_field = next((e for e in editable if 'message' in label(e) or 'compose email' in label(e)), None)
        to_field = next((e for e in editable if e is not subject_field and e is not body_field), None)
        for name, field, value in (('to', to_field, recipient), ('subject', subject_field, subject),
                                   ('body', body_field, text)):
            if name not in done and field is not None:
                return name, dict(action_type='input_text', text=value, index=field['index'])
        return 'send', dict(action_type='click', index=send)
    if done & {'send', 'dialog'}:
        return 'complete', dict(action_type='status', goal_status='complete')
    compose = by_label('compose')
    if compose is not None:
        return 'compose', dict(action_type='click', index=compose)
    return 'wait', dict(action_type='wait')


def reply(prompt):
    if prompt.rstrip().endswith('Summary of this step:'):
        marker = re.search(r'Based on the reason: fake:(\w+)', prompt)
        return 'fake:%s done' % (marker.group(1) if marker else 'unknown')
    marker, action = decide(prompt)
    return 'Reason: fake:%s\nAction: %s' % (marker, json.dumps(action))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8101)
    parser.add_argument('--delay', type=float, default=0, help='seconds per completion, to mimic GPU latency')
    parser.add_argument('--receipt', type=Path, required=True, help='SERVING.json to write for --serving-receipt')
    args = parser.parse_args()
    model = json.loads(LOCK.read_text())['models']['qwen']
    snapshot = str(ROOT / 'runtime' / 'models' / 'qwen' / model['revision'])
    endpoint = 'http://127.0.0.1:%d/v1' % args.port
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(dict(
        status='MODEL_SERVING_READY', synthetic=True, kind='SYNTHETIC fake_model.py rehearsal; not study data',
        repo_id=model['repo_id'], revision=model['revision'], snapshot=snapshot, endpoint=endpoint,
        dtype='bfloat16', max_model_len=32768, engine_version='0.11.0', checkpoint_files_verified=True,
        models_loaded=True, image_policy=QWEN_IMAGE_POLICY, history_policy='upstream_recipe'), indent=2))

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def send(self, body):
            data = json.dumps(body).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == '/version':
                return self.send(dict(version='0.11.0'))
            if self.path == '/v1/models':
                return self.send(dict(data=[dict(id=model['repo_id'], root=snapshot, max_model_len=32768)]))
            self.send_error(404)

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            prompt = next(c['text'] for c in body['messages'][0]['content'] if c['type'] == 'text')
            text = reply(prompt)
            time.sleep(args.delay)
            print(text.splitlines()[0], flush=True)
            self.send(dict(model=model['repo_id'], choices=[dict(message=dict(role='assistant', content=text),
                                                               finish_reason='stop')],
                           usage=dict(prompt_tokens=len(prompt) // 4, completion_tokens=len(text) // 4)))

    print('SYNTHETIC fake model on %s, receipt %s' % (endpoint, args.receipt), flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()


if __name__ == '__main__':
    main()
