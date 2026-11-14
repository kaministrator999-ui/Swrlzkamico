"""Fix project-marked HTML draft display and deterministic finish without faking model stop."""
from __future__ import annotations
import ast

def once(s,old,new,label):
    count=s.count(old)
    if count!=1:raise RuntimeError("SOURCE_ANCHOR_DRIFT:"+label+":"+str(count))
    return s.replace(old,new,1)

HELPER=r'''
# SWRLZ_CLOSE_COMPLETE_HTML_FENCE_V1
def _swrlz_close_complete_html_fence(source):
    """Close only an unambiguously finished *single HTML file* wrapper.

    Keep the opening file=/project= metadata byte-for-byte. A closed-looking
    HTML fragment is never enough: require a parsed single-file project.
    This checks source packaging, never claims browser execution.
    """
    raw=str(source or "")
    fence=chr(96)*3
    header=re.match(r"\A[ \t]*"+re.escape(fence)+
                    r"html(?:[ \t]+[^\r\n]+)?\r?\n",raw,re.I)
    if not header:
        return raw,False
    body=raw[header.end():]
    if not re.search(r"(?is)<html\b",body) or not re.search(r"(?is)<body\b",body):
        return raw,False
    if not re.search(r"(?is)</body>\s*</html>\s*",body):
        return raw,False
    if re.search(r"(?is)<script\b",body) and not re.search(r"(?is)</script>",body):
        return raw,False
    if re.search(r"(?is)<style\b",body) and not re.search(r"(?is)</style>",body):
        return raw,False
    if body.rstrip().endswith(fence):
        inner=body.rstrip()[:-len(fence)].rstrip()
        candidate=raw
        if fence in inner:
            return raw,False
    else:
        inner=body.rstrip()
        if fence in inner:
            return raw,False
        candidate=raw.rstrip()+"\n"+fence+"\n"
    if not re.search(r"(?is)</html>\s*\Z",inner):
        return raw,False
    try:
        from project_archive import parse_project_files
        files=parse_project_files(candidate)
    except Exception:
        return raw,False
    if len(files)!=1:
        return raw,False
    entry=files[0]
    if not str(entry.get("path") or "").lower().endswith((".html",".htm")):
        return raw,False
    if not str(entry.get("content") or "").rstrip().lower().endswith("</html>"):
        return raw,False
    return candidate,True


'''

def patch_coder(raw):
    s=raw.decode("utf-8")
    if "SWRLZ_CLOSE_COMPLETE_HTML_FENCE_V1" in s:raise RuntimeError("CODER_PATCH_ALREADY_APPLIED")
    s=once(s,"def _swrlz_trim_code_resume(prior,following):",HELPER+"def _swrlz_trim_code_resume(prior,following):","HTML close helper")
    s=once(s,
'''        observed.append(part_observation)
        if pause_at_budget:break''',
'''        # SWRLZ_CLOSE_COMPLETE_HTML_FENCE_V1: a provider can hit its token
        # ceiling after completing </html> but before closing the Markdown
        # artifact fence. Preserve the real finishReason and validate the
        # completed source package before requesting another 4K-token segment.
        original_candidate="".join(parts)
        final_candidate,source_closed=_swrlz_close_complete_html_fence(original_candidate)
        if source_closed:
            part_observation["sourceCompleteByParser"]=True
            part_observation["sourceClosureKind"]="html-file-envelope"
            if final_candidate!=original_candidate:
                parts=[final_candidate]
                yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":attempt}
                yield {"type":"CANDIDATE_PREVIEW_DELTA","text":final_candidate,"attempt":attempt}
        observed.append(part_observation)
        if source_closed:break
        if pause_at_budget:break''',
"segment close detection")
    s=once(s,
'''            if (timing.get("finishReason")=="length" and auto_resume_existing_source):''',
'''            if (timing.get("finishReason")=="length" and auto_resume_existing_source
                    and not timing.get("sourceCompleteByParser")):''',
"avoid restarting completed HTML on length")
    s=once(s,
'''                if timing.get("finishReason")!="length":
                    for repair_number in range(1,_SWRLZ_PATCH_ATTEMPTS+1):''',
'''                if timing.get("finishReason")!="length" or timing.get("sourceCompleteByParser"):
                    for repair_number in range(1,_SWRLZ_PATCH_ATTEMPTS+1):''',
"repair complete-but-invalid HTML")
    s=once(s,
'''                        repair_needed=(timing.get("finishReason")!="length"),''',
'''                        repair_needed=(timing.get("finishReason")!="length"
                            or bool(timing.get("sourceCompleteByParser"))),''',
"checkpoint repair routing")
    s=once(s,
'''    if isinstance(programming,dict):
        yield {"type":"PROGRAMMING_INTENT","intent":programming}
    model=load()''',
'''    if isinstance(programming,dict):
        yield {"type":"PROGRAMMING_INTENT","intent":programming}
    # An older saved draft may already end at </html> without the fence.
    # Verify it before spending minutes loading and decoding a new segment.
    prior_candidate,prior_closed=_swrlz_close_complete_html_fence(source)
    if prior_closed:
        prior_check=completion_validation(
            _candidate_structure_check(prior_candidate,programming,history),
            {"finishReason":"length","sourceCompleteByParser":True})
        if prior_check.get("status")=="PASS":
            if prior_candidate!=source:
                yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":0}
                yield {"type":"CANDIDATE_PREVIEW_DELTA","attempt":0,"text":prior_candidate}
            yield {"type":"CANDIDATE_VALIDATION","validation":prior_check}
            yield {"type":"CODE_OUTPUT_FINISHED",
                   "sourceSha256":hashlib.sha256(prior_candidate.encode("utf-8")).hexdigest()}
            yield {"type":"DELTA","text":prior_candidate}
            yield {"type":"COMPLETED","phase":"COMPLETE",
                   "resumedSource":True,"completionEvidence":"parsed-html-envelope"}
            return
        source=prior_candidate
        checkpoint=dict(checkpoint)
        checkpoint["repairNeeded"]=True
    model=load()''',
"resume completed saved HTML without new model decode")
    s=once(s,
'''        if timing.get("finishReason")!="length" and completion.get("status")!="PASS":''',
'''        if (timing.get("finishReason")!="length" or timing.get("sourceCompleteByParser")) and completion.get("status")!="PASS":''',
"resume repair routing")
    s=once(s,
'''    if timing.get("finishReason")=="length" or completion.get("status")!="PASS":
        next_checkpoint=_swrlz_checkpoint_record(''',
'''    if completion.get("status")!="PASS":
        next_checkpoint=_swrlz_checkpoint_record(''',
"resume completed source after length")
    s=once(s,
'''             repair_needed=(timing.get("finishReason")!="length"),
             reasons=completion.get("reasons"))''',
'''             repair_needed=(timing.get("finishReason")!="length"
                 or bool(timing.get("sourceCompleteByParser"))),
             reasons=completion.get("reasons"))''',
"resume checkpoint repair flag")
    s=once(s,
'''    yield {"type":"CODE_OUTPUT_FINISHED","sourceSha256":checkpoint["sourceSha256"]}''',
'''    yield {"type":"CODE_OUTPUT_FINISHED",
           "sourceSha256":hashlib.sha256(draft.encode("utf-8")).hexdigest()}''',
"correct accepted source hash")
    ast.parse(s,filename="qwen_coder_engine.py")
    return s.encode("utf-8")

_TELEMETRY_OLD='''    result["generationComplete"]=True if reason=="stop" else False if reason=="length" else None
    if reason=="length":
        result["status"]="REJECT"
        result["reasons"]=list(dict.fromkeys([*(result.get("reasons") or []),"model-output-token-limit"]))
    return result'''
_TELEMETRY_NEW='''    # SWRLZ_CLOSE_COMPLETE_HTML_FENCE_V1: preserve provider finishReason
    # "length" in every receipt. Source acceptance is possible only when
    # the completed file envelope was parsed AND the source gate passed.
    parsed_completion=(observation.get("sourceCompleteByParser") is True
                       and result.get("status")=="PASS")
    result["generationComplete"]=(True if reason=="stop" or (reason=="length" and parsed_completion)
                                  else False if reason=="length" else None)
    if reason=="length" and not parsed_completion:
        result["status"]="REJECT"
        result["reasons"]=list(dict.fromkeys([*(result.get("reasons") or []),"model-output-token-limit"]))
    if parsed_completion:
        result["sourceClosureVerified"]=True
        result["executionVerified"]=False
    return result'''

def patch_telemetry(raw):
    s=raw.decode("utf-8")
    if "SWRLZ_CLOSE_COMPLETE_HTML_FENCE_V1" in s:raise RuntimeError("TELEMETRY_PATCH_ALREADY_APPLIED")
    s=once(s,_TELEMETRY_OLD,_TELEMETRY_NEW,"preserve provider stop truth and parse acceptance")
    ast.parse(s,filename="programming_telemetry.py")
    return s.encode("utf-8")

_UI_PREVIEW_OLD='''        const draftText=(savedDraft||(!g.terminal&&!String(g.text||"").trim()))
          ?String(g.previewText||""):"";
        let draftPanel=node.querySelector(".swrlz-code-draft");'''

_UI_PREVIEW_NEW='''        const draftText=(savedDraft||(!g.terminal&&!String(g.text||"").trim()))
          ?String(g.previewText||""):"";
        // SWRLZ_DRAFT_FILENAME_PREVIEW_V1: file=/project= metadata belongs
        // to the artifact protocol, not inside the user's source editor.
        // Remove only the presentation wrapper; the durable draft is intact.
        const draftFence=String.fromCharCode(96,96,96);
        const draftNewline=draftText.indexOf("\\n");
        const draftHeader=draftNewline>0&&draftText.startsWith(draftFence)
          &&/^(?:html|css|javascript|js|typescript|python)\\b/i.test(
            draftText.slice(draftFence.length,draftNewline));
        const draftInfo=draftHeader?draftText.slice(draftFence.length,draftNewline):"";
        const draftFile=draftInfo.match(/\\bfile=([^\\s]+)/)?.[1]||"";
        const draftBody=draftHeader?draftText.slice(draftNewline+1):draftText;
        const draftDisplayed=draftHeader&&draftBody.trimEnd().endsWith(draftFence)
          ?draftBody.trimEnd().slice(0,-draftFence.length).trimEnd():draftBody;
        let draftPanel=node.querySelector(".swrlz-code-draft");'''

_UI_LABEL_OLD='''          if(draftLabel)draftLabel.textContent=savedDraft
            ?(g.terminal?"Saved unverified code · Continue code to resume":"Saved draft · continuing · not yet verified")
            :"Code draft · generating and validating · not saved";'''

_UI_LABEL_NEW='''          if(draftLabel){
            const message=savedDraft
              ?(g.terminal?"Saved unverified code · Continue code to resume":"Saved draft · continuing · not yet verified")
              :"Code draft · generating and validating · not saved";
            draftLabel.textContent=message+(draftFile?" · "+draftFile:"");
          }'''

# JS source has UTF-8 literal dot, not mojibake; string matching is exact.
def patch_html(raw):
    s=raw.decode("utf-8")
    if "SWRLZ_DRAFT_FILENAME_PREVIEW_V1" in s:raise RuntimeError("DRAFT_DISPLAY_ALREADY_APPLIED")
    s=once(s,_UI_PREVIEW_OLD,_UI_PREVIEW_NEW,"project fence preview display")
    s=once(s,_UI_LABEL_OLD,_UI_LABEL_NEW,"draft header filename label")
    s=once(s,'''            if(shown!==draftText){
              const follow=codeViewNearBottom(code);
              if(shown&&draftText.startsWith(shown)&&code.firstChild?.nodeType===Node.TEXT_NODE)
                code.firstChild.appendData(draftText.slice(shown.length));
              else code.textContent=draftText;
              draftPanel._swrlzShownSource=draftText;''',
'''            if(shown!==draftDisplayed){
              const follow=codeViewNearBottom(code);
              if(shown&&draftDisplayed.startsWith(shown)&&code.firstChild?.nodeType===Node.TEXT_NODE)
                code.firstChild.appendData(draftDisplayed.slice(shown.length));
              else code.textContent=draftDisplayed;
              draftPanel._swrlzShownSource=draftDisplayed;''',
"unwrapped code pane scrolling")
    return s.encode("utf-8")
