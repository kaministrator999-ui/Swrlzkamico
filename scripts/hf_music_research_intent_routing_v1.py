#!/usr/bin/env python3
"""Fix §C request-operation routing for music research vs lyric text and weather.

Exact Space source, single module, no model weights, no account changes.
Each behavioral gate is tested against the actual deployed classifier AST.
"""
from __future__ import annotations
import ast,hashlib,json,os,re,sys
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
SPACE="kamiloki/Swyrlz";FILE="online_tools.py";ROOT=Path("reports/swrlz-music-router-v1")
MARK="swrlz-research-music-operation-disambiguation-v1"
OLD_INSTALLED_WEB=r'''    # swrlz-research-music-operation-disambiguation-v1: actual research commands
    # initiate a public-source search, but descriptions of past research do not.
    research_command=bool(re.search(
        r"(?i)^\s*(?:(?:please|could you|can you)\s+)?"
        r"(?:research|look into|investigate)\b",text))
    explicit_web = bool(_EXPLICIT_WEB.search(text) or research_command)'''
OLD_INSTALLED_LYRIC=r'''    # Lyric *analysis* and revision of a just-created/user-authored song are
    # not requests to retrieve an external song's published lyric text.
    musical_analysis=bool(re.search(
        r"(?i)\b(?:research|compare|explain|describe|analy[sz]e|understand|"
        r"structure|songwriting|rhythm|rhythmic|flow|meter|rhyme|forms?|"
        r"genres?|patterns?|subdivisions?|bars?)\b",text))
    creative_revision=bool(re.search(
        r"(?i)\b(?:revise|rewrite|remix|adapt|transform|rework|polish|"
        r"edit|change|improve|continue)\b.{0,180}"
        r"\b(?:song|lyrics?|verses?|chorus|bridge|hook|stanza)\b",text))
    # Retrieval requires an explicit request for existing lyric text. A word
    # like 'lyrics' alone is insufficient to activate verification.
    lyric_text_demand=bool(re.search(
        r"(?i)\b(?:give|show|provide|print|quote|reproduce|copy|find|fetch|"
        r"retrieve|transcribe|recite|look\s+up|search\s+for)\b.{0,100}"
        r"\b(?:lyrics?|words\s+to\s+(?:the\s+)?song)\b"
        r"|\b(?:full|complete|all\s+the)\s+(?:song\s+)?lyrics?"
        r"\s+(?:of|to|for)\b"
        r"|\blyrics?\s+(?:of|to|for)\s+(?:the\s+)?(?:song|track)\b",
        text))
    explicit_lookup_verb=bool(re.search(
        r"(?i)\b(?:find|fetch|retrieve|look\s+up|search\s+for|quote|"
        r"transcribe|recite|reproduce|show|give|provide|print)\b"
        r".{0,100}\b(?:lyrics?|words\s+to\s+(?:the\s+)?song)\b",text))
    published_full_lyrics=bool(re.search(
        r"(?i)\b(?:full|complete|all\s+the)\s+(?:song\s+)?lyrics?"
        r"\s+(?:of|to|for)\b",text))
    lyrics_lookup=(bool(_LYRICS_LOOKUP.search(text)) and lyric_text_demand
                   and not (creative_revision and not explicit_lookup_verb)
                   and not (musical_analysis and not
                            (explicit_lookup_verb or published_full_lyrics)))'''
OLD_WEB='''    explicit_web = bool(_EXPLICIT_WEB.search(text))'''
NEW_WEB=r'''    # swrlz-research-music-operation-disambiguation-v1
    # Affirmative research prompts search; words inside negative requests don't.
    research_command=bool(re.search(
        r"(?i)^\s*(?:(?:please|could you|can you)\s+)?"
        r"(?:research|look into|investigate)\b",text))
    no_new_lookup=bool(re.search(
        r"(?i)\b(?:without|don't|do not|never|skip|avoid|no|not)\b"
        r".{0,65}\b(?:web\s+search|online\s+search|search|"
        r"look\s*up|lookup|research|browse)\b",text))
    explicit_web=bool(research_command or
                      (_EXPLICIT_WEB.search(text) and not no_new_lookup))'''
OLD_LYRIC='''    lyrics_lookup=bool(_LYRICS_LOOKUP.search(text)) and not (lyrics_creative and not explicit_web)'''
NEW_LYRIC=r'''    # "Lyrics" as subject matter or user-authored content is not an
    # affirmative request for a published recording's transcript.
    affirmative_lyrics_request=bool(re.search(
        r"(?i)\b(?:find|fetch|look\s+up|search\s+for|give|show|provide|"
        r"quote|transcribe|recite|reproduce|print|copy|retrieve)\b"
        r".{0,85}\b(?:lyrics?|words\s+to\s+(?:the\s+)?song)\b",text))
    published_full_lyrics=bool(re.search(
        r"(?i)\b(?:research|find|provide|show|give|fetch|retrieve)\b"
        r".{0,35}\b(?:full|complete|published|existing)\s+"
        r"(?:song\s+)?lyrics?\b",text))
    quote_song_verse=bool(re.search(
        r"(?i)\b(?:quote|recite|transcribe|reproduce|copy)\b"
        r".{0,60}\b(?:verse|chorus)\b",text))
    negated_lyric_retrieval=bool(re.search(
        r"(?i)\b(?:do\s+not|don't|never|avoid|without|skip|no|not)\b"
        r".{0,65}\b(?:look\s*up|search|find|fetch|retrieve|quote|"
        r"reproduce|provide|show|print|transcribe|copy)\b"
        r".{0,90}\b(?:lyrics?|song|recording|verse|chorus)\b",text))
    creative_revision=bool(re.search(
        r"(?i)\b(?:revise|rewrite|remix|adapt|transform|rework|"
        r"polish|edit|change|improve|continue|remaster)\b"
        r".{0,200}\b(?:song|lyrics?|verses?|chorus|bridge|hook)\b",text))
    analysis_not_lyric_retrieval=bool(re.search(
        r"(?i)\b(?:research|compare|explain|describe|analy[sz]e|understand)\b"
        r".{0,140}\b(?:structure|songwriting|rhythm|flow|meter|rhyme|"
        r"form|genres?|patterns?|subdivisions?|bars?|history|arrangements?)\b",text))
    lyrics_lookup=bool(
        (affirmative_lyrics_request or published_full_lyrics or quote_song_verse)
        and not negated_lyric_retrieval
        and not (creative_revision and not published_full_lyrics)
        and not (analysis_not_lyric_retrieval and not published_full_lyrics))'''
OLD_WEATHER='''    weather_intent=bool(_WEATHER_TERMS.search(text) and not weather_negated)'''
NEW_WEATHER=r'''    # Fictional rain and negated weather are not meteorological queries.
    explicit_weather_data=bool(re.search(
        r"(?i)\b(?:what(?:'s|\s+is)\s+(?:the\s+)?"
        r"(?:weather|forecast|temperature|humidity|wind|precipitation)|"
        r"(?:is|will)\s+it\s+(?:rain|raining|snow|snowing)|"
        r"will\s+it\s+(?:rain|snow)|chance\s+of\s+(?:rain|snow)|"
        r"current\s+(?:weather|temperature|forecast)|"
        r"weather\s+in\s+\S+|forecast\s+(?:in|for|at)\s+\S+)\b",text)
        or re.search(
        r"(?i)\b(?:check|give|show|tell\s+me|look\s+up|using?|use)\b"
        r".{0,65}\b(?:weather|forecast|temperature|"
        r"humidity|chance\s+of\s+(?:rain|snow))\b",text))
    weather_intent=bool(explicit_weather_data and not weather_negated)'''
OLD_WEATHER2='''    if _WEATHER_TERMS.search(text) and not weather_negated and not programming.get("codingTask"):'''
OLD_FRESHNESS='''    freshness = bool(_FRESHNESS.search(text))'''
NEW_FRESHNESS=r'''    # The word 'today' inside creative instructions is not freshness intent.
    creative_narrative=bool(re.search(
        r"(?i)\b(?:write|compose|rewrite|revise|remix|remaster|create|"
        r"fictional|lullaby|story|poem|lyrics?|verses?)\b",text))
    freshness=bool(_FRESHNESS.search(text) and not
                   (creative_narrative and not explicit_web))'''
NEW_WEATHER2='''    if weather_intent and not programming.get("codingTask"):'''
def sha(x):return hashlib.sha256(x).hexdigest()
def one(text,old,new,name):
    if text.count(old)!=1:raise RuntimeError(f"Unexpected live source for {name}: count={text.count(old)}")
    return text.replace(old,new,1)
def build(raw):
    s=raw.decode("utf-8")
    if MARK in s:
        # Upgrade only our exact previously installed patch. Any other Space
        # revision is rejected instead of overwriting unrelated live changes.
        s=one(s,OLD_INSTALLED_WEB,NEW_WEB,"installed research classification")
        s=one(s,OLD_INSTALLED_LYRIC,NEW_LYRIC,"installed lyrics classification")
        compile(s,FILE,"exec")
        return s.encode("utf-8")
    s=one(s,OLD_WEB,NEW_WEB,"explicit research")
    s=one(s,OLD_LYRIC,NEW_LYRIC,"lyrics intent")
    s=one(s,OLD_WEATHER,NEW_WEATHER,"weather intent")
    s=one(s,OLD_WEATHER2,NEW_WEATHER2,"weather fallback")
    s=one(s,OLD_FRESHNESS,NEW_FRESHNESS,"narrative freshness")
    compile(s,FILE,"exec")
    return s.encode("utf-8")
def test(raw):
    source=raw.decode("utf-8")
    tree=ast.parse(source)
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)
              and n.name=="classify_online_request")
    preamble=ast.parse("from __future__ import annotations").body
    minimal=ast.Module(body=preamble+[node],type_ignores=[])
    ns={
      "re":re,"Any":object,"_clean":lambda s,n=2000:str(s or "")[:n],
      "_EXPLICIT_WEB":re.compile(r"search\s+online|look\s+it\s+up|browse\s+online",re.I),
      "_MODELER_REFERENCE_SEARCH":re.compile(r"^never-matching-$"),
      "_MODELER_REFERENCE_NEGATED":re.compile(r"^never-matching-$"),
      "_LYRICS_LOOKUP":re.compile(r"\blyrics?\b|words\s+to\s+(?:the\s+)?song|quote\s+(?:first\s+)?verse",re.I),
      "_WEATHER_TERMS":re.compile(r"\bweather\b|\bforecast\b|\btemperature\b|\brain\b|\bwind\b|\bhumidity\b",re.I),
      "_TIME_TERMS":re.compile(r"what\s+time\s+is\s+it",re.I),
      "_FRESHNESS":re.compile(r"\btoday\b|\blatest\b",re.I),
      "_LOCATION_REQUIRED":re.compile(r"\b(?:here|near\s+me|my)\b",re.I),
      "_weather_negated":lambda s:False,
      "_weather_location_from_prompt":lambda s:"Topeka, Kansas" if "Topeka" in s else "",
      "_time_location_from_prompt":lambda s:"",
      "_normalize_client_location":lambda s:None,
      "_weather_continuation_request":lambda s:False,
      "_prior_weather_context":lambda s:None,
      "_lyrics_subject":lambda s:"Example Song" if "lyrics" in s else "",
      "_lyrics_search_query":lambda s:"example song lyrics",
      "_lyrics_requested_scope":lambda s:"full-lyrics",
      "song_identity":lambda s:{"title":s},
      "_search_query_from_prompt":lambda s:s[:500],
      "creative_music_transform_request":lambda s:bool(re.search(
          r"\b(?:write|create|compose|generate|rewrite)\b.{0,120}\b(?:original|lyrics?|song|rap|verses?)\b",s,re.I)),
      "music_feedback_followup":lambda p,h=None:False,
      "is_simple_checkin":lambda s:False,
      "ONLINE_CONTRACT":"contract",
    }
    # Exercise the genuine deployed regex definitions, not reduced mocks.
    for key in ("_EXPLICIT_WEB","_LYRICS_LOOKUP","_WEATHER_TERMS",
                "_TIME_TERMS","_FRESHNESS","_LOCATION_REQUIRED"):
        nodes=[a for a in tree.body if isinstance(a,ast.Assign)
               and any(isinstance(t,ast.Name) and t.id==key for t in a.targets)]
        if len(nodes)!=1:raise RuntimeError("Missing live grammar "+key)
        exec(compile(ast.Module(body=nodes,type_ignores=[]),FILE,"exec"),ns)
    exec(compile(minimal,FILE,"exec"),ns)
    fn=ns["classify_online_request"]
    cases=[
      ("Research how traditional 12-bar blues AAB lyric verses compare to a modern pop pre-chorus. Cite sources.",True,"search",None),
      ("Research and briefly compare boom-bap and trap rhythm for rap lyric flow. Cite sources.",True,"search",None),
      ("Write a COMPLETE original synth-pop song titled 'Signal in the Rain' with a bridge.",False,"none",None),
      ("Write an original country song with a letter on the porch.",False,"none",None),
      ("Write an original rap song about midnight circuits.",False,"none",None),
      ("Compose original song lyrics about rain with a chorus.",False,"none",None),
      ("What's the weather in Topeka, Kansas?",True,"weather",None),
      ("Please find full lyrics to the song 'Example Song'.",True,"search","lyrics-verification"),
      ("Research full lyrics of the song 'Example Song'.",True,"search","lyrics-verification"),
      ("Provide the lyrics for Roll Call by Tech N9ne.",True,"search","lyrics-verification"),
      ("Revise the entire song, keeping its chorus and return the COMPLETE revised lyrics.",False,"none",None),
      ("These original fictional verses are mine. A paper key hums against the rain. Just acknowledge them.",False,"none",None),
      ("I wrote a song about rain, here are my lyrics. Don't generate anything yet.",False,"none",None),
      ("Is it raining right now in Topeka, Kansas?",True,"weather",None),
      ("Research public articles about early blues arrangements and provide source links.",True,"search",None),
      ("Explain the lyric structure and flow of 12-bar blues.",False,"none",None),
      ("Write an original song using the weather forecast for Topeka, Kansas.",True,"weather",None),
      ("I did some research on lyrical song form yesterday.",False,"none",None),
      ("Without a new web search, summarize the eclipse evidence you previously cited.",False,"none",None),
      ("Don't do another web lookup; summarize the two expansion classes.",False,"none",None),
      ("Skip searching again and use the previous sources.",False,"none",None),
      ("Research public sources about blues form. Do not fetch any published song lyrics.",True,"search",None),
      ("Don't look up published song lyrics; just explain an AAB verse.",False,"none",None),
      ("Please look it up online: the history of hip-hop genres.",True,"search",None),
      ("These are my original fictional verses. Rain hits the station clock. Just acknowledge them, no new lyrics yet.",False,"none",None),
      ("These lines are mine, not from a recording. Simply acknowledge them; don't produce lyrics yet.",False,"none",None),
      ("Write an ORIGINAL song titled Rain Glass Lantern. This is fiction, not a weather question.",False,"none",None),
      ("Revise the entire song, keep the chorus, return the COMPLETE revised lyrics.",False,"none",None),
      ("Remaster my fictional song and keep the hook, return the complete song.",False,"none",None),
      ("Research twelve-bar blues AAB verse structure and compare it to pop chorus sections. Cite a source; don't quote published lyrics.",True,"search",None),
      ("Research how synthesizers and sequencers shaped early electronic pop, without reproducing lyrics from recordings.",True,"search",None),
      ("In a toy chat project list 3 pending tasks: fix Stop, improve lyric formatting and change logo.",False,"none",None),
      ("I am discussing the remix, not requesting another song or a web search. Explain the verses. No new lyrics.",False,"none",None),
      ("Without a new web search, explain why not every new moon creates an eclipse.",False,"none",None),
      ("No weather lookup: a robin stands in rain holding an amber sign in my fictional story.",False,"none",None),
      ("Is it snowing outside in Topeka, Kansas?",True,"weather",None),
      ("Give the published lyrics to Example Song by Fictional Artist.",True,"search","lyrics-verification"),
      ("What is the current temperature in Topeka, Kansas?",True,"weather",None),
    ]
    for prompt,requested,kind,mode in cases:
        result=fn(prompt,[],{},None)
        if bool(result["requested"])!=requested or result["kind"]!=kind or result.get("contentMode")!=mode:
            print("CLASSIFIER_ROUTING_DIAGNOSTIC", "prompt="+repr(prompt), "result="+repr(result), "source_lines="+repr([line.strip() for line in (ast.get_source_segment(source,node) or "").splitlines() if any(word in line for word in ("explicit_web","lyrics_lookup","weather_intent","research_command"))]),flush=True)
            raise AssertionError("Misroute "+repr(prompt)+" -> "+repr(result))
    # Prove safe two-step upgrade from the currently deployed patch version;
    # the same script must work on an unpatched Space or after its first release.
    fixture=("def _operation_fixture():\n"+OLD_WEB+"\n"+OLD_LYRIC+"\n"
             +OLD_WEATHER+"\n"+OLD_WEATHER2+"\n        pass\n").encode()
    patch_v1=fixture.decode().replace(OLD_WEB,OLD_INSTALLED_WEB,1)\
        .replace(OLD_LYRIC,OLD_INSTALLED_LYRIC,1)\
        .replace(OLD_WEATHER,NEW_WEATHER,1)\
        .replace(OLD_WEATHER2,NEW_WEATHER2,1).encode()
    upgraded=build(patch_v1)
    assert NEW_WEB.encode() in upgraded
    assert NEW_LYRIC.encode() in upgraded
    assert MARK.encode() in upgraded
    assert upgraded!=patch_v1
    print("MUSIC_OPERATION_PATCH_UPGRADE_PASS",flush=True)
    print("MUSIC_OPERATION_ROUTING_REGRESSIONS_PASS",len(cases),flush=True)

def stage(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    before=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=rev,token=api.token)).read_bytes()
    after=build(before);test(after)
    (ROOT/"before").mkdir(parents=True,exist_ok=True)
    (ROOT/"after").mkdir(parents=True,exist_ok=True)
    (ROOT/"before"/FILE).write_bytes(before);(ROOT/"after"/FILE).write_bytes(after)
    (ROOT/"manifest.json").write_text(json.dumps({
        "revision":rev,"file":FILE,"before":sha(before),"after":sha(after)},indent=2)+"\n")
    print("MUSIC_OPERATION_ROUTING_PREFLIGHT",rev,sha(before),sha(after),flush=True)
    return rev,before,after
def publish(api):
    if os.getenv("SWRLZ_MUSIC_ROUTING_APPROVED")!="1":
        raise RuntimeError("Explicit user release approval absent")
    if not api.token:raise RuntimeError("HF_TOKEN not connected")
    rev,before,after=stage(api)
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Concurrent Space update")
    newrev=None
    try:
        commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
           operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(ROOT/"after"/FILE))],
           commit_message="§C distinguish music-structure research and original lyrics from song-text lookup and weather")
        newrev=str(commit.oid)
        verified=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=newrev,token=api.token)).read_bytes()
        if verified!=after:raise RuntimeError("Published source differs")
        manifest=json.loads((ROOT/"manifest.json").read_text())
        manifest["publishedRevision"]=newrev
        (ROOT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
        print("MUSIC_OPERATION_ROUTING_PUBLISHED",rev,newrev,flush=True)
    except Exception:
        if newrev and api.repo_info(SPACE,repo_type="space").sha==newrev:
            back=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=newrev,
              operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(ROOT/"before"/FILE))],
              commit_message="Rollback §C music operation routing to exact previous file")
            print("MUSIC_OPERATION_ROUTING_ROLLED_BACK",str(back.oid),flush=True)
        raise
def rollback(api):
    if os.getenv("SWRLZ_MUSIC_ROUTING_APPROVED")!="1":raise RuntimeError("Rollback approval absent")
    manifest=json.loads((ROOT/"manifest.json").read_text())
    published=manifest.get("publishedRevision")
    if not published or api.repo_info(SPACE,repo_type="space").sha!=published:
        raise RuntimeError("Refusing rollback after newer HF source changes")
    old=(ROOT/"before"/FILE).read_bytes()
    if sha(old)!=manifest["before"]:raise RuntimeError("Original source checksum differs")
    commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=published,
      operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(ROOT/"before"/FILE))],
      commit_message="Rollback §C music route after failed postrelease acceptance")
    verify=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=str(commit.oid),token=api.token)).read_bytes()
    if verify!=old:raise RuntimeError("Rollback source mismatch")
    print("MUSIC_OPERATION_ROUTING_ACCEPTANCE_ROLLBACK",published,str(commit.oid),flush=True)
if __name__=="__main__":
    cmd=sys.argv[1:] or ["preflight"]
    if cmd not in (["preflight"],["publish"],["rollback"]):raise SystemExit("preflight|publish|rollback")
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    if cmd==["preflight"]:stage(api)
    elif cmd==["publish"]:publish(api)
    else:rollback(api)
