from pathlib import Path
import ast, errno, hashlib, itertools, json, operator, subprocess, sys
from datetime import UTC, datetime, timedelta
from _pytest.mark import structures
from _pytest import python
from _pytest.mark.structures import ParameterSet
from _pytest.python import IdMaker

root = Path(sys.argv[1]).resolve()
BASE = '766504a02aaeb9dda339d588172dd7d5bdbd2b3f'
TREE = '6f1ae4a5707f2344bbeb4c15efdb823480866feb'
PYTEST_SOURCES = {
    python: '9553fbb38363c987f59b1de522142a9dc0e9f6191cd1f173a6bee21140d4c887',
    structures: 'e8322e0b57aa8c8bb8150a563a3bc8b85983b3f30645773dcc7488b1db6e9755',
}
assert sys.platform == 'darwin' and sys.version_info[:3] == (3, 13, 9)
for module, digest in PYTEST_SOURCES.items():
    assert hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() == digest


def git(*args):
    return subprocess.check_output(('git','-C',str(root),*args))

assert git('rev-parse',f'{BASE}^{{tree}}').decode().strip()==TREE
def exact_source(path):
    raw=path.read_bytes()
    assert raw==git('show',f'{BASE}:{path.relative_to(root)}')
    return ast.parse(raw)

targets = sorted([*(root/'packages/aitm-usage/tests').glob('test_*.py'), root/'tools/ci/tests/test_cli_evidence.py'])
paths = git('ls-tree','-r','--name-only',BASE,'packages/aitm-usage/tests','tools/ci/tests/test_cli_evidence.py').decode().splitlines()
tracked_test_paths = {name for name in paths if Path(name).name.startswith('test_') and name.endswith('.py')}
assert tracked_test_paths=={str(path.relative_to(root)) for path in targets}
assert not any(Path(path).name=='conftest.py' for path in paths)
trees = {p:exact_source(p) for p in targets}

test_module = {p.stem:p for p in targets}
assignments = {
    p:{t.id: node.value for node in tree.body if isinstance(node, ast.Assign) for t in node.targets if isinstance(t, ast.Name)}
    for p,tree in trees.items()
}
types = exact_source(root/'packages/aitm-usage/src/aitm_usage/types.py')
enums = {
    node.name:{t.id: member.value.value for member in node.body if isinstance(member,ast.Assign) and isinstance(member.value,ast.Constant) for t in member.targets if isinstance(t,ast.Name)}
    for node in types.body if isinstance(node,ast.ClassDef) and any(isinstance(base,ast.Name) and base.id=='StrEnum' for base in node.bases)
}
unsupported_value = object()


def literal(p,node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node,(ast.List,ast.Tuple)):
        return type(() if isinstance(node,ast.Tuple) else [])(literal(p,x) for x in node.elts)
    if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):
        x=literal(p,node.operand)
        if type(x) is int: return -x
    if isinstance(node,ast.BinOp) and type(node.op) in (ast.Mult,ast.Add,ast.Pow):
        left,right=literal(p,node.left),literal(p,node.right)
        if (type(left) in (str,int) and type(right) in (str,int)) or (type(left) is datetime and type(right) is timedelta and isinstance(node.op,ast.Add)):
            return {ast.Mult:operator.mul,ast.Add:operator.add,ast.Pow:operator.pow}[type(node.op)](left,right)
    if isinstance(node,ast.Name):
        if node.id=='UTC' and p.name=='test_scan.py': return UTC
        if node.id in assignments[p]: return literal(p,assignments[p][node.id])
        if p.name=='test_monitor_scope.py' and node.id in {'B','UNKNOWN'}: return unsupported_value
        raise ValueError(f'Unsupported name {p.name}:{node.id}')
    if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name):
        if node.value.id in enums: return enums[node.value.id][node.attr]
        if node.value.id=='errno': return getattr(errno,node.attr)
    if isinstance(node,ast.Call):
        name=ast.unparse(node.func)
        from uuid import UUID
        if name=='UUID':
            [kw]=node.keywords
            assert kw.arg=='int' and isinstance(kw.value,ast.Constant)
            return UUID(int=kw.value.value)
        if name=='str' and len(node.args)==1 and not node.keywords:
            value=literal(p,node.args[0])
            if type(value) in (UUID,str): return str(value)
        if p.name=='test_scan.py' and name in {'datetime','timedelta'}:
            args=[literal(p,x) for x in node.args]
            kwargs={kw.arg:literal(p,kw.value) for kw in node.keywords}
            return {'datetime':datetime,'timedelta':timedelta}[name](*args,**kwargs)
        if p.name=='test_scan.py' and name=='AFTER.isoformat':
            assert not node.args and not node.keywords
            return literal(p,assignments[p]['AFTER']).isoformat()
        if p.name=='test_scan.py' and name in {'_claude_line','_claude_cost'}:
            fields={kw.arg:literal(p,kw.value) for kw in node.keywords}
            if name=='_claude_cost':
                assert not node.args
                helper=next(x for x in trees[p].body if isinstance(x,ast.FunctionDef) and x.name==name)
                model,defaults,_=helper.body
                assert ast.unparse(model.targets[0])=='model_usage'
                assert ast.unparse(defaults.targets[0])=='fields'
                # The helper only emits a JSON line with these defaults and
                # the keyword overrides. Reconstruct its data without importing it.
                model=ast.literal_eval(model.value)
                static={k.value:ast.literal_eval(v) for k,v in zip(defaults.value.keys,defaults.value.values) if k.value!='modelUsage'}
                static={'startTime':static['startTime'],'totalCostUSD':static['totalCostUSD'],
                        'modelUsage':{'claude-opus-5-5':model},'private':static['private']}
                kind='cost-state'
                fields=static|fields
            else:
                [kind]=node.args
                assert isinstance(kind,ast.Constant)
                kind=kind.value
            session=fields.pop('session',literal(p,assignments[p]['SESSION']))
            assert type(session) is UUID
            return json.dumps({'type':kind,'sessionId':str(session),**fields},ensure_ascii=True).encode()+b'\n'
        if name=='TokenCounts':
            return unsupported_value
        raise ValueError(f'Unsupported call {p.name}:{name}')
    if isinstance(node,ast.Dict):
        # Dicts can be reconstructed for the reviewed fixture serialization.
        # They do not contribute an ID by themselves in pytest.
        try:
            return ast.literal_eval(node)
        except ValueError:
            return unsupported_value
    raise ValueError(f'Unsupported AST {p.name}:{ast.unparse(node)}')

def parameters(p,tree,node):
    if isinstance(node,ast.Name):
        imports = {a.asname or a.name:(test_module[x.module],a.name) for x in tree.body if isinstance(x,ast.ImportFrom) and x.module in test_module for a in x.names}
        p,name = imports.get(node.id,(p,node.id))
        node=assignments[p][name]
    if not isinstance(node,ast.List): raise ValueError('parameter list changed')
    return p,node.elts

def params(p,tree,decorator,base):
    argnames=literal(p,decorator.args[0])
    if isinstance(argnames,str): argnames=[s.strip() for s in argnames.split(',') if s.strip()]
    p,values=parameters(p,tree,decorator.args[1])
    ids=None
    for keyword in decorator.keywords:
        assert keyword.arg=='ids'
        ids=literal(p,keyword.value)
    sets=[]
    for value in values:
        pid=None
        if isinstance(value,ast.Call) and ast.unparse(value.func)=='pytest.param':
            [kw]=value.keywords
            assert kw.arg=='id'
            pid=literal(p,kw.value)
            items=value.args
        elif len(argnames)==1:
            items=[value]
        else:
            assert isinstance(value,(ast.List,ast.Tuple))
            items=value.elts
        # Explicit IDs bind the exact suffix independently of actual row values.
        vals=tuple(unsupported_value for _ in items) if pid is not None or ids is not None else tuple(literal(p,x) for x in items)
        sets.append(ParameterSet(vals,[],pid))
    return IdMaker(argnames,sets,None,ids,None,base).make_unique_parameterset_ids()

out=[]
for p,tree in trees.items():
    for test in tree.body:
        if not isinstance(test,ast.FunctionDef) or not test.name.startswith('test_'):
            continue
        base=f'{p.relative_to(root)}::{test.name}'
        dimensions=[]
        for d in reversed(test.decorator_list):
            if isinstance(d,ast.Call) and ast.unparse(d.func)=='pytest.mark.parametrize':
                dimensions.append(params(p,tree,d,base))
            elif not(isinstance(d,ast.Call) and ast.unparse(d.func)=='pytest.mark.skipif'):
                raise ValueError(f'unsupported test decorator {p.name}:{ast.unparse(d)}')
        out.extend([base+'['+'-'.join(ids)+']' for ids in itertools.product(*dimensions)] if dimensions else [base])
out=sorted(out)
digest=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()).hexdigest()
ref=json.loads((root/'.github/spikes/146/reference.json').read_text())['ids']
print('independently assembled',len(out),'unique',len(set(out)),'sha256',digest)
for node in set(out)-set(ref): print('source-only',node)
for node in set(ref)-set(out): print('reference-only',node)
assert set(out)==set(ref) and len(out)==len(set(out))==len(ref)
Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n')
