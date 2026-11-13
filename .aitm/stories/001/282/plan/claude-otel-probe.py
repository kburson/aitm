from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,threading
from uuid import uuid4
root=Path(__file__).resolve().parent
binary=Path.home()/'.local/share/claude/versions/2.1.318'
with binary.open('rb') as f:
    assert hashlib.file_digest(f,'sha256').hexdigest()=='677a2ea7bf576cedd20e191d973914ed8a41796f53a63b1923381ddc4d5b5e7d'
batches=[]
class Collector(BaseHTTPRequestHandler):
    def do_POST(self):
        assert self.path=='/v1/logs'
        size=int(self.headers['Content-Length'])
        assert 0<size<2_000_000
        batches.append(json.loads(self.rfile.read(size)))
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(b'{}')
    def log_message(self,*args):
        pass
with ThreadingHTTPServer(('127.0.0.1',0),Collector) as receiver:
    thread=threading.Thread(target=receiver.serve_forever,daemon=True)
    thread.start()
    env={k:v for k,v in os.environ.items() if k not in {'CLAUDECODE','CLAUDE_CODE_ENTRYPOINT','BETA_TRACING_ENDPOINT'} and not k.startswith('OTEL_')}
    env.update(CLAUDE_CODE_ENABLE_TELEMETRY='1',OTEL_LOGS_EXPORTER='otlp',
               OTEL_METRICS_EXPORTER='none',OTEL_TRACES_EXPORTER='none',
               OTEL_EXPORTER_OTLP_LOGS_PROTOCOL='http/json',
               OTEL_EXPORTER_OTLP_LOGS_ENDPOINT=f'http://127.0.0.1:{receiver.server_port}/v1/logs',
               OTEL_LOG_USER_PROMPTS='0',OTEL_LOG_ASSISTANT_RESPONSES='0',
               OTEL_LOG_TOOL_CONTENT='0',OTEL_LOG_TOOL_DETAILS='0',OTEL_LOGS_EXPORT_INTERVAL='200')
    sid=str(uuid4())
    checkout=root/'project'
    argv=[str(binary),'-p','--model','claude-sonnet-4-6','--effort','low','--restricted',
     '--strict-mcp-config','--mcp-config',str(root/'mcp.json'),'--settings',str(root/'settings.json'),
     '--session-id',sid,'--agents',(root/'agent.json').read_text(),'--tools','Agent,Read',
     '--allowedTools','Agent(aitm-fold-fixture)',f'Read({checkout}/fold-fixture.txt)','--disable-slash-commands',
     '--input-format','stream-json','--output-format','stream-json','--verbose','--include-partial-messages',
     '--forward-subagent-text','--max-budget-usd','0.6']
    def prompt(text):
        return json.dumps({'type':'user','message':{'role':'user','content':text}})+'\n'
    result=subprocess.run(argv,input=prompt('Reply exactly AITM_SCOPE_WARMUP_1. Use no tools.')+
                          prompt((root/'prompt.txt').read_text().strip()),
                          cwd=checkout,env=env,text=True,capture_output=True,timeout=100)
    receiver.shutdown()
    thread.join(5)
(root/'native.stderr').write_text(result.stderr)
(root/'wire.jsonl').write_text(result.stdout)
(root/'telemetry.json').write_text(json.dumps(batches))
(root/'session-id.txt').write_text(sid+'\n')
assert result.returncode==0, result.returncode
events=[json.loads(x) for x in result.stdout.splitlines()]
assert events[-1]['type']=='result' and events[-1]['subtype']=='success'
assert events[-1]['result'].strip()=='AITM_FOLD_PARENT_OK'
print('Native process exited successfully. Local telemetry batches:',len(batches))
