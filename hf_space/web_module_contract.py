"""Bounded standalone browser-module resolution checks, never execution proof."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
from urllib.parse import urljoin, urlparse

_TOKEN=re.compile(r'\s+|//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`|[A-Za-z_$][\w$]*|.',re.S)


def _imports(code):
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


class _Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False);self.scripts=[];self.active=None
    def handle_starttag(self,tag,attrs):
        if tag=='script':self.active=[dict(attrs),[]]
    def handle_data(self,data):
        if self.active is not None:self.active[1].append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self.active is not None:self.scripts.append((self.active[0],''.join(self.active[1])));self.active=None


def module_dependency_gaps(source):
    """Check declarations against imports; dependencies may still fail at runtime."""
    if len(source)>65536:return []
    document=_Document();document.feed(source)
    imports={};scopes={};modules=[]
    for attrs,body in document.scripts:
        kind=str(attrs.get('type') or '').lower()
        if kind=='importmap':
            try:
                data=json.loads(body)
                if not isinstance(data,dict) or not isinstance(data.get('imports',{}),dict) or not isinstance(data.get('scopes',{}),dict):raise ValueError()
                imports.update(data.get('imports',{}));scopes.update(data.get('scopes',{}))
            except (ValueError,TypeError):return ['invalid-browser-import-map']
        elif kind=='module':
            modules.extend(_imports(body))
            if attrs.get('src'):modules.append(urljoin('https://standalone.invalid/',attrs['src']))
    base='https://standalone.invalid/'
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
    facts=json.loads((Path(__file__).with_name('programming_references')/'three-0.160.0.json').read_text())
    known={entry['url']:entry.get('bareImports',[]) for entry in facts['sources']}
    gaps=[]
    for spec in modules:
        url=resolve(spec,base)
        if url is None:gaps.append('unresolved-browser-module:'+spec[:100])
        for dependency in known.get(url,[]):
            if resolve(dependency,url) is None:gaps.append('unresolved-browser-module:'+dependency+' (required by '+url.rsplit('/',1)[-1]+')')
    return list(dict.fromkeys(gaps))[:8]
