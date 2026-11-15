#!/usr/bin/env python3
"""Inspect current Hugging Face §C coder prose finalization paths without mutation."""
import ast,json,re
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download
space='kamiloki/Swyrlz'
api=HfApi()
rev=api.repo_info(space,repo_type='space').sha
p=Path(hf_hub_download(space,'qwen_coder_engine.py',repo_type='space',revision=rev))
s=p.read_text().splitlines()
print('QWEN_PROSE_REV',rev,'LINES',len(s),flush=True)
patterns=[
    r'candidate_text\s*=',r'guarded_turn',r'code_delivery',r'PROSE-ONLY',r'RESPONSE MODE',
    r'yield.*DELTA',r'yield.*COMPLETED',r'_candidate_structure_check',r'generate_events\(',
    r'if not guarded_turn',r'if guarded_turn',r'programming_intent\(',r'temperature\s*=',
    r'create_chat_completion',r'plain.*response',r'candidate_preview',r'for chunk in']
hits=[]
for i,line in enumerate(s):
    if any(re.search(p,line,re.I) for p in patterns): hits.append(i)
selected=[]
for i in hits:
    if i<1080:continue
    if i>min(2100,len(s)):continue
    lo=max(0,i-4);hi=min(len(s),i+9)
    if selected and lo<=selected[-1][1]+2:
        selected[-1]=(selected[-1][0],max(selected[-1][1],hi))
    else:selected.append((lo,hi))
for lo,hi in selected[:48]:
    print('QWEN_PROSE_RANGE',json.dumps({'start':lo+1,'end':hi,
        'text':'\n'.join(str(i+1)+': '+s[i] for i in range(lo,hi))},ensure_ascii=False),flush=True)
