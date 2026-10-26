"""Bounded standalone browser-module resolution checks, never execution proof."""
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import shlex
from urllib.parse import quote, unquote, urljoin, urlparse, urlsplit, urlunsplit

_TOKEN=re.compile(r'\s+|//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`|[A-Za-z_$][\w$]*|.',re.S)


def _tokens(code):
    tokens=[];skip_until=0
    for match in _TOKEN.finditer(code):
        if match.start()<skip_until:continue
        token=match.group()
        if token.isspace() or token.startswith(('//','/*','`')):continue
        if token=='/':
            # Conservatively skip regex-like literals. Ambiguous division is
            # left ungraded rather than treating its text as an import.
            j=match.end();character_class=False
            while j<len(code) and code[j]!='\n':
                if code[j]=='\\':j+=2;continue
                if code[j]=='[':character_class=True
                elif code[j]==']':character_class=False
                elif code[j]=='/' and not character_class:skip_until=j+1;break
                j+=1
            continue
        if token[:1] in ('"',"'"):
            tokens.append(('string',token[1:-1] if '\\' not in token else None))
        else:tokens.append(('token',token))
    return tokens


def _imports(code):
    tokens=_tokens(code)
    result=[]
    for i,(_kind,word) in enumerate(tokens):
        if _kind!='token' or word not in ('import','export') or (i and tokens[i-1][1]=='.'):continue
        tail=tokens[i+1:i+65]
        if not tail:continue
        if tail[0][0]=='string':spec=tail[0][1]
        elif word=='import' and tail[0][1]=='(':
            spec=tail[1][1] if len(tail)>1 and tail[1][0]=='string' else None
        else:
            spec=None
            for j,item in enumerate(tail[:-1]):
                if item[1]==';':break
                if item==('token','from') and tail[j+1][0]=='string':spec=tail[j+1][1];break
        if spec and spec not in result:result.append(spec)
    return result


def _pinned_transform_api_gaps(code, resolve, parent="https://standalone.invalid/"):
    """Recognize one verified missing r160 method on clearly bound instances.

    This deliberately is not a JavaScript type checker or a general method
    whitelist. Unknown constructors, versions, rebinding, shadowing and explicit
    method extensions are left ungraded rather than advertised as runtime proof.
    """
    pinned='https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/TransformControls.js'
    tokens=_tokens(code)
    constructors=set()
    # A binding is trusted only when the actual imported module resolves to the
    # exact version whose public source is recorded in the evidence bundle.
    for index, token in enumerate(tokens):
        if token!=('token','import'):
            continue
        end=next((j for j in range(index+1,len(tokens)) if tokens[j]==('token',';')),len(tokens))
        clause=tokens[index+1:end]
        source=next((clause[j+1][1] for j in range(len(clause)-1)
                     if clause[j]==('token','from') and clause[j+1][0]=='string'),None)
        if not source or resolve(source,parent)!=pinned:
            continue
        if len(clause)>=3 and clause[0]==('token','*') and clause[1]==('token','as'):
            constructors.add((clause[2][1],'.','TransformControls'))
        for j, value in enumerate(clause):
            if value==('token','TransformControls'):
                alias=(clause[j+2][1] if j+2<len(clause) and clause[j+1]==('token','as') else 'TransformControls')
                constructors.add((alias,))
    if not constructors:
        return []
    values=[value if kind=='token' else None for kind,value in tokens]
    instances=set()
    for index in range(len(values)-4):
        if values[index] not in ('const','let','var') or values[index+2:index+4]!=['=','new']:
            continue
        for constructor in constructors:
            start=index+4
            if (start+len(constructor)<len(values) and tuple(values[start:start+len(constructor)])==constructor
                    and values[start+len(constructor)]=='('):
                instances.add(values[index+1])
    gaps=[]
    for name in instances:
        # Do not infer the method type after explicit reassignment or a local
        # shadow with the same spelling. This narrow gate prefers abstention.
        declarations=sum(values[i] in ('const','let','var') and values[i+1]==name for i in range(len(values)-1))
        writes=sum(values[i]==name and values[i+1]=='=' for i in range(len(values)-1))
        parameter=any(values[i:i+3]==[name,'=','>'] for i in range(len(values)-2))
        for i in range(len(values)-1):
            if values[i]!='(':
                continue
            depth=1;end=i+1
            while end<len(values) and depth:
                if values[end]=='(':depth+=1
                elif values[end]==')':depth-=1
                end+=1
            function_args=('function' in values[max(0,i-2):i]
                           or values[end:end+2]==['=','>']
                           or (values[end:end+1]==['{'] and i>0
                               and values[i-1] not in ('if','for','while','switch','catch','with')
                               and (i<2 or values[i-2]!='.')))
            if function_args and name in values[i+1:end-1]:
                parameter=True
        extension=(any(values[i:i+4]==[name,'.','update','='] for i in range(len(values)-3))
                   or any(tokens[i:i+5]==[('token',name),('token','['),('string','update'),('token',']'),('token','=')]
                          for i in range(len(tokens)-4)))
        prototype_extension=any(values[i:i+4]==['prototype','.','update','='] for i in range(len(values)-3))
        assigned_extension=any(values[i] == 'Object' and values[i+1]=='.'
                               and values[i+2] in ('assign','defineProperty','defineProperties')
                               and values[i+3:i+5]==['(',name] for i in range(len(values)-4))
        if declarations!=1 or writes!=1 or parameter or extension or prototype_extension or assigned_extension:
            continue
        called=any(values[i:i+4]==[name,'.','update','('] and (i==0 or values[i-1]!='.')
                   for i in range(len(values)-3))
        if called:
            gaps.append('unsupported-three-r160-api:TransformControls.update() is unavailable; remove that call and retain editor controls; scene/render matrix updates handle the gizmo')
    return list(dict.fromkeys(gaps))


class _Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False);self.scripts=[];self.active=None
    def handle_starttag(self,tag,attrs):
        if tag=='script':self.active=[dict(attrs),[]]
    def handle_data(self,data):
        if self.active is not None:self.active[1].append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self.active is not None:self.scripts.append((self.active[0],''.join(self.active[1])));self.active=None


def _declares_module_build(files, document_path):
    """Recognize source-declared build requirements, never a successful build.

    Use the nearest package owner of this HTML document. A package elsewhere or
    an arbitrary script name cannot hide unresolved standalone browser imports.
    """
    by_path={item['path']:item['content'] for item in files}
    directory=document_path.rsplit('/',1)[0] if '/' in document_path else ''
    package=None
    while True:
        path=(directory+'/' if directory else '')+'package.json'
        if path in by_path:
            try:package=json.loads(by_path[path])
            except (ValueError,TypeError):return False
            break
        if not directory:return False
        directory=directory.rsplit('/',1)[0] if '/' in directory else ''
    if not isinstance(package,dict):return False
    dependencies={}
    for field in ('dependencies','devDependencies'):
        if isinstance(package.get(field),dict):dependencies.update(package[field])
    # These are actual package/CLI identities. Merely naming a framework or
    # emitting .ts/.tsx files supplies no evidence that bare imports are built.
    tools={
        'vite':'vite','webpack':'webpack','parcel':'parcel','next':'next',
        'esbuild':'esbuild','rollup':'rollup','astro':'astro',
        'react-scripts':'react-scripts','@rspack/cli':'rspack','typescript':'tsc',
    }
    declared={binary for package_name,binary in tools.items()
              if isinstance(dependencies.get(package_name),str) and dependencies[package_name].strip()}
    scripts=package.get('scripts')
    if not declared or not isinstance(scripts,dict):return False
    for key in ('build','dev','start'):
        script=scripts.get(key)
        if not isinstance(script,str):continue
        try:
            lexer=shlex.shlex(script,posix=True,punctuation_chars=';&|')
            lexer.whitespace_split=True;segments=[[]]
            for token in lexer:
                if token in (';','&&','||','&','|'):segments.append([])
                else:segments[-1].append(token)
        except ValueError:continue
        for words in segments:
            words=list(words)
            if words[:1]==['env']:words.pop(0)
            while words and re.fullmatch(r'[A-Za-z_][\w]*=.*',words[0]):words.pop(0)
            if words[:1]==['npx']:
                words.pop(0)
                while words and words[0].startswith('-'):words.pop(0)
            elif words[:2] in (['npm','exec'],['pnpm','exec'],['yarn','exec'],['yarn','run']):
                words=words[2:]
            metadata_flags={'--version','-v','--help','-h','--showConfig','--listFilesOnly','--noEmit'}
            if words and words[0] in declared and not metadata_flags.intersection(words[1:]):
                return True
    return False


def module_dependency_gaps(source, project_files=None):
    """Check actual HTML/module graphs from returned source, without fetching IO.

    Each standalone document retains its import map and module-parent URLs.
    Local files reachable from its module graph are interpreted as browser JS.
    Source-declared build projects need separate build verification; unrelated
    server/unused files and supported build graphs are outside this direct check.
    """
    from project_archive import MAX_FILE_BYTES, ProjectArchiveError, validate_project_files
    files=[]
    if project_files:
        try:
            files=validate_project_files(project_files)
        except ProjectArchiveError:
            return ['browser-module-invalid-project-files']
    origin='https://standalone.invalid/'
    def local_url(path):
        return urljoin(origin,quote(path,safe='/'))
    returned={local_url(item['path']):item['content'] for item in files}
    documents=[(local_url(item['path']),item['content']) for item in files
               if item['path'].lower().endswith(('.html','.htm'))
               or item.get('language','').lower() in ('html','html5')]
    if not documents:
        documents=[(origin,source)]
    gaps=[]
    facts=json.loads((Path(__file__).with_name('programming_references')/'three-0.160.0.json').read_text())
    known={entry['url']:entry.get('bareImports',[]) for entry in facts['sources']}
    for base,html in documents:
        if files and _declares_module_build(files,unquote(urlsplit(base).path).lstrip('/')):
            continue  # Build-required source, not directly loadable browser JS.
        # Large artifacts never silently bypass validation; inspect each actual
        # returned document in full, within the same bound as source storage.
        if len(html.encode('utf-8'))>MAX_FILE_BYTES:
            gaps.append('browser-module-source-exceeds-validation-limit');continue
        document=_Document();document.feed(html)
        imports={};scopes={};inline=[];pending=deque()
        for attrs,body in document.scripts:
            kind=str(attrs.get('type') or '').lower()
            if kind=='importmap':
                try:
                    data=json.loads(body)
                    if not isinstance(data,dict) or not isinstance(data.get('imports',{}),dict) or not isinstance(data.get('scopes',{}),dict):raise ValueError()
                    imports.update(data.get('imports',{}));scopes.update(data.get('scopes',{}))
                except (ValueError,TypeError):
                    gaps.append('invalid-browser-import-map')
            elif kind=='module':
                if attrs.get('src'):
                    pending.append(urljoin(base,attrs['src']))
                else:
                    inline.append((base,body))
        def mapped(spec,mapping):
            if spec in mapping:return mapping[spec]
            prefixes=[key for key in mapping if key.endswith('/') and spec.startswith(key)]
            if prefixes:
                key=max(prefixes,key=len);value=mapping[key]
                return value+spec[len(key):] if isinstance(value,str) and value.endswith('/') else None
            return None
        def resolve(spec,parent):
            if urlparse(spec).scheme or spec.startswith(('./','../','/')):return urljoin(parent,spec)
            candidates=sorted((key for key in scopes if parent.startswith(urljoin(base,key))),key=len,reverse=True)
            for key in candidates:
                scope=scopes[key]
                if isinstance(scope,dict):
                    value=mapped(spec,scope)
                    if isinstance(value,str):return urljoin(base,value)
            value=mapped(spec,imports)
            return urljoin(base,value) if isinstance(value,str) else None
        def inspect(parent,body):
            for spec in _imports(body):
                url=resolve(spec,parent)
                if url is None:gaps.append('unresolved-browser-module:'+spec[:100])
                else:pending.append(url)
            gaps.extend(_pinned_transform_api_gaps(body,resolve,parent))
        for parent,body in inline:
            inspect(parent,body)
        visited=set()
        while pending:
            url=pending.popleft()
            if url in visited:continue
            visited.add(url)
            for dependency in known.get(url,[]):
                if resolve(dependency,url) is None:
                    gaps.append('unresolved-browser-module:'+dependency+' (required by '+url.rsplit('/',1)[-1]+')')
            parts=urlsplit(url)
            file_url=urlunsplit((parts.scheme,parts.netloc,quote(unquote(parts.path),safe='/'),'',''))
            if file_url in returned:
                inspect(url,returned[file_url])
            elif files and file_url.startswith(origin):
                gaps.append('missing-project-module:'+parts.path.lstrip('/')[:140])
    return list(dict.fromkeys(gaps))[:8]
