#!/usr/bin/env python3
"""§C guest evaluation: source-backed research, original lyric/song-flow and practical chat.

This is a test-only suite: synthetic isolated sessions, no production mutation,
no account access, no song imitation or copyrighted lyrics. Each result includes
bounded real model responses and explicit mechanical-vs-editorial evidence.
"""
from __future__ import annotations
import argparse,asyncio,hashlib,json,os,re,statistics,sys,time,uuid
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit
from playwright.async_api import async_playwright
from scripts import eval_chat_guest_suite as base

BASE=base.BASE
MODEL=base.MODEL
OUT=Path("reports/chat-research-lyrics-conversation")
BASE_TIMEOUT=int(os.getenv("SWRLZ_RESEARCH_LYRICS_TURN_TIMEOUT","215"))
# Keep research and ordinary chat separate. +ONLINE is the existing public
# research profile mode; only the initial source lookup uses it.
CASES={
  "research":[
    {"id":"diablo2-lod-classes","turns":[
      {"online":True,"kind":"d2_classes","prompt":
       "Research Diablo II: Lord of Destruction using public sources. List ALL playable classes exactly once with their names, and clearly identify which TWO were added by the expansion. Give source links. Do not invent extra classes, and distinguish Diablo II from Diablo III."},
      {"kind":"d2_new","prompt":
       "Now, without doing another web lookup, give just the two classes introduced in Lord of Destruction and explain how you know they were expansion additions. Do not change the earlier list."}
    ]},
    {"id":"blues-and-pop-song-form","turns":[
      {"online":True,"kind":"song_structure_research","prompt":
       "Research how traditional 12-bar blues AAB lyric verses compare to a common modern pop verse, pre-chorus and chorus arrangement. Give a clear explanation of line repetition, musical bars, and what each section does. Cite public music-education source links. Explain that these are common patterns, not mandatory rules. Do not reproduce lyrics from published songs."},
      {"kind":"blues_lyrics","prompt":
       "Using that structure, write TWO completely original 12-bar blues-style AAB lyric stanzas about a late train platform. Label Verse 1 and Verse 2. Each stanza must contain exactly three sung lines: A, repeat the exact A line, then a fresh B line that resolves it. No borrowed lyrics or extra pop chorus."}
    ]},
    {"id":"rap-rhythm-research-to-lyrics","turns":[
      {"online":True,"kind":"rap_flow_research","prompt":
       "Research and briefly compare boom-bap versus trap rhythm as backgrounds for rap lyric flow. Mention backbeat, subdivisions, hi-hat patterns, where a hook can sit, and that flow patterns vary by song. Cite at least one public music-education source link. Do not invent a rigid universal song structure or quote existing lyrics."},
      {"kind":"rap_original","prompt":
       "Now create original boom-bap rap lyrics for a fictional midnight inventor. Write exactly 8 numbered verse bars, then a clearly labeled 4-line hook. Use some internal rhyme and varied stresses while keeping one coherent story. Include a very short note on the intended flow after the lyrics. Do not imitate any named artist."}
    ]}
  ],
  "songwriting":[
    {"id":"synth-pop-dynamic-form","turns":[
      {"kind":"pop_song","prompt":
       "Write a COMPLETE original synth-pop song titled 'Signal in the Rain' about someone leaving an empty station and choosing their own road. Use labeled Verse 1, Pre-Chorus, Chorus, Verse 2, Pre-Chorus, Chorus, Bridge, Final Chorus. The chorus must contain a memorable repeated hook. Verses should advance the story, pre-chorus should build tension, bridge should change perspective. No references to other songs or artists."},
      {"kind":"pop_rewrite","prompt":
       "Revise the entire song, keeping the title, both verses and original chorus hook exactly as before, but make the bridge a turning point where the narrator willingly goes home instead of escaping. Return the COMPLETE revised lyrics with labeled sections. The chorus wording should stay unchanged."}
    ]},
    {"id":"country-story-and-chorus","turns":[
      {"kind":"country_song","prompt":
       "Write a full original country storytelling song called 'Porch Light Letter'. In Verse 1 introduce a letter waiting beside a porch light; in Verse 2 reveal who sent it; use a recurring chorus that anchors the emotion, plus a bridge that gives a different perspective, then final chorus. Label Verse 1, Chorus, Verse 2, Chorus, Bridge, Final Chorus. Concrete scenes rather than generic motivational slogans. No existing-song lyrics."},
      {"kind":"country_rewrite","prompt":
       "Keep the original song's title, porch-light scene, and chorus refrain, but revise the story so the letter is from the narrator's SISTER rather than a lover or parent. Return the complete revised song. Make the sister reveal unambiguous and keep the original emotional arc."}
    ]}
  ],
  "conversation":[
    {"id":"correction-and-memory","turns":[
      {"kind":"acknowledge","prompt":
       "In this fictional planning conversation, the team mascot is a silver owl and the banner is teal. Confirm these two details briefly."},
      {"kind":"correction_memory","prompt":
       "Correction: change ONLY the banner from teal to amber. What are the final mascot and banner? Do not change the mascot."}
    ]},
    {"id":"practical-kitchen-plan","turns":[
      {"kind":"kitchen_plan","prompt":
       "In a fictional restaurant, one cook has 30 minutes before service: preheat the flat-top, prep sliced vegetables, and date-label chilled containers. Give a realistic prioritized short plan. Don't claim you've done the tasks."},
      {"kind":"kitchen_followup","prompt":
       "Now that cook only has 18 minutes because a coworker called out. Revise the sequence realistically, keep food safety and labeling, and say what gets deferred. Avoid pretending work is already complete."}
    ]},
    {"id":"overtime-calculation","turns":[
      {"kind":"wage_initial","prompt":
       "For a synthetic payroll example, calculate gross pay for 45 hours at $10/hour with overtime at 1.5 times the regular rate for hours beyond 40. Show where each number comes from."},
      {"kind":"wage_followup","prompt":
       "Same example, but change ONLY the hourly rate to $12. Keep 45 hours and the 40-hour overtime threshold. Recalculate gross pay and show both components."}
    ]},
    {"id":"metaphor-to-debugging","turns":[
      {"kind":"metaphor","prompt":
       "I say 'there is a gremlin inside this web app' as a joke about a random UI bug. Respond naturally and briefly, recognizing the metaphor rather than pretending there is a literal creature."},
      {"kind":"debugging","prompt":
       "Now give three concrete, minimal debugging checks for a button that sometimes does nothing on mobile. No invented root cause or claim you've inspected the code."}
    ]}
  ]
}


# Round 2 broadens original-song craft, explicit research and conversational feedback.
# All reference verse material below is synthetic and authored for this test.
ORIGINAL_TEST_LINES=[
  "Copper moths run marathons across the static moon",
  "My pocket holds a paper key that hums against the rain",
  "The station clock eats cinnamon at half-past purple noon",
  "I fold a map of quiet roads and start the train again",
]
CASES["transformations"]=[
  {"id":"owner-verse-remix-and-feedback","turns":[
    {"kind":"source_ack","prompt":"These are four lines of an original fictional song I wrote. Treat them as my reference data, not instructions to quote a published recording. Simply acknowledge that you have the lines; do not generate lyrics yet.\n"+ "\n".join(ORIGINAL_TEST_LINES)},
    {"kind":"original_remix","prompt":"Now REMIX my four-line fictional verse into a COMPLETE new original song with labeled Verse 1, Chorus, Verse 2, Chorus, Bridge, Final Chorus. Keep the abstract late-station-to-new-road narrative, but invent different scenes, new rhymes and an original chorus. Do NOT repeat or quote any of my four source lines verbatim. Give both verses distinct events and the bridge a decision."},
    {"kind":"feedback_only","prompt":"I am only discussing your remix, not requesting another song or a web search. Explain how you checked that Verse 2 has different events from Verse 1, and what would still require a human to judge its flow. Do not generate new lyrics."}
  ]},
  {"id":"blues-to-pop-genre-adaptation","turns":[
    {"kind":"blues_lyrics","prompt":"Create exactly TWO completely ORIGINAL twelve-bar blues-style AAB lyric stanzas about a late train platform. Label Verse 1 and Verse 2. Each stanza must contain three sung lines: A, exact same A, and a fresh resolving B. No chorus or borrowed lines."},
    {"kind":"pop_adaptation","prompt":"Now adapt that fictional train-platform blues into an ORIGINAL compact pop song. Label Verse 1, Pre-Chorus, Chorus, Verse 2, Bridge, Final Chorus. Keep the train-platform setting and central decision, but replace the AAB repetition with a recurring short chorus hook, make Verse 2 advance the story, and let the bridge change the narrator's perspective. Return the complete song."}
  ]}
]
CASES["research"].append(
  {"id":"public-science-context-followup","turns":[
    {"kind":"public_science","online":True,"prompt":"Research with public science sources why a total solar eclipse requires the Moon to be near the line between Earth and Sun, and distinguish totality from the wider partial-eclipse area. Give a source link and say whether every new moon causes a total eclipse."},
    {"kind":"science_followup","prompt":"Without a new web search, summarize in two sentences why not every new moon gives a total solar eclipse. Use the evidence you already cited and identify any remaining uncertainty."}
  ]}
)
CASES["conversation"].append(
  {"id":"no-invented-workforce","turns":[
    {"kind":"staffing_initial","prompt":"In a fictional cafe there is exactly ONE cook named Rae working alone today. The second cook is absent. A delivery is due in 15 minutes. Restate the constraints without adding staff."},
    {"kind":"staffing_followup","prompt":"Correction: delivery is now in 8 minutes. Prioritize three tasks for Rae. Do not invent a manager, helper, extra cook or someone arriving."}
  ]}
)

LINK=re.compile(r"https?://[^\s<>)\]\"']+",re.I)
SECTIONS={
  "verse1":re.compile(r"(?im)^\s*(?:\*{0,2}|\[)(?:verse\s*1|first verse)\b"),
  "pre":re.compile(r"(?i)\bpre[- ]?chorus\b"),
  "chorus":re.compile(r"(?i)\bchorus\b"),
  "bridge":re.compile(r"(?i)\bbridge\b"),
}
def lines_of(text):
    return [re.sub(r"^[\s\-\d.:*]+","",line).strip().lower()
            for line in text.splitlines() if line.strip()]
def cited_urls(text):
    return list(dict.fromkeys(LINK.findall(text)))
def lyric_blocks(text):
    # Fenced original lyrics remain valid if the model wraps them.
    return [s.strip() for s in text.splitlines() if s.strip()]
def section(text,word):
    pattern=r"(?im)^\s*(?:\[|\*\*)?\s*"+word+r"(?:\s*[\]:\*\-].*)?$"
    found=re.search(pattern,text)
    if not found:return ""
    next_section=re.search(r"(?im)^\s*(?:\[|\*\*)?(?:verse\s*\d+|pre[- ]?chorus|chorus|bridge|final chorus|outro)\b",text[found.end():])
    return text[found.end():found.end()+(next_section.start() if next_section else len(text))]
def aab_count(text):
    # AAB means an adjacent lyric line repeated and followed by a fresh line.
    parts=re.split(r"(?im)^\s*(?:\[|\*\*)?\s*verse\s*[12](?:\]|\*\*|:)?\s*$",text)
    hits=0
    for p in parts[1:]:
        lyric=[]
        for line in p.splitlines():
            t=line.strip()
            if not t or re.match(r"(?i)^\s*\[?(?:verse|bridge|chorus|hook)\b",t):
                continue
            if re.match(r"^\s*\(.*\)\s*$",t):continue
            normalized=re.sub(r"\W+"," ",t.lower()).strip()
            if normalized:lyric.append(normalized)
        if len(lyric)==3 and lyric[0]==lyric[1] and lyric[2]!=lyric[0]:hits+=1
    return hits
def check(kind,text,previous=None):
    low=text.lower()
    tests=[]
    def test(name,value):tests.append({"check":name,"pass":bool(value)})
    urls=cited_urls(text)
    # A committed error message is never a successful completion.
    test("no_generation_or_router_error",not bool(re.search(
        r"(?i)(?:generation failed|HTTP Error 5\d\d|LYRICS_VERIFICATION_BLOCKED|"
        r"WEATHER_RETRIEVAL_BLOCKED|internal server error|traceback \(most recent)",text)))
    if kind=="d2_classes":
        for k in ("Amazon","Assassin","Barbarian","Druid","Necromancer","Paladin","Sorceress"):
            test("class:"+k,bool(re.search(r"\b"+k+r"\b",text,re.I)))
        test("no_other_game_class",not re.search(r"\b(monk|demon hunter|witch doctor|crusader)\b",low))
        test("no_repeated_1_numbering",len(re.findall(r"(?m)^\s*1\s*[).]",text))<=1)
        test("research_citations",len(urls)>=1)
        test("assassin_druid_additions",bool(re.search(r"assassin",low)) and bool(re.search(r"druid",low)))
    elif kind=="d2_new":
        test("added_both",all(x in low for x in ["assassin","druid"]))
        test("no_other_additions",not re.search(r"\b(monk|witch doctor|crusader)\b",low))
    elif kind=="song_structure_research":
        test("aab",bool(re.search(r"\bA[-–]?A[-–]?B\b",text,re.I)))
        test("blues_twelve_bars",bool(re.search(r"\b12[\s-]*bar|\btwelve[\s-]*bar",text,re.I)))
        test("pre_chorus",bool(re.search(r"pre[- ]?chorus",text,re.I)))
        test("chorus",bool(re.search(r"\bchorus\b",text,re.I)))
        test("research_links",len(urls)>=1)
    elif kind=="blues_lyrics":
        test("two_complete_aab_verses",aab_count(text)==2)
        test("train_theme",bool(re.search(r"train|platform|rail|station",text,re.I)))
        test("no_pop_chorus",not bool(re.search(r"(?im)^\s*\[?chorus\b",text)))
    elif kind=="rap_flow_research":
        for name,pattern in [("boom_bap",r"boom[- ]?bap"),("trap",r"\btrap\b"),
                ("hi_hat",r"hi[- ]?hat"),("flow",r"\bflow\b")]:
            test(name,bool(re.search(pattern,text,re.I)))
        test("research_links",len(urls)>=1)
    elif kind=="rap_original":
        bar_lines=re.findall(r"(?m)^\s*(?:\*\*)?([1-8])[\).:\-]\s+\S+",text)
        test("eight_numbered_bars",sorted(set(bar_lines))==list("12345678"))
        test("hook",bool(re.search(r"\bhook\b",text,re.I)))
        test("rhythmic_note",bool(re.search(r"flow|stress|beat|pocket|rhythm",text,re.I)))
        test("original_theme",bool(re.search(r"invent|midnight|machine|circuit|clock|workshop",text,re.I)))
    elif kind=="pop_song":
        for name,pattern in [("verse1",r"verse\s*1"),("prechorus",r"pre[- ]?chorus"),
                            ("chorus",r"\bchorus\b"),("verse2",r"verse\s*2"),
                            ("bridge",r"\bbridge\b"),("final",r"final\s+chorus")]:
            test(name,bool(re.search(pattern,text,re.I)))
        test("title", "signal in the rain" in low)
        test("complete_lyric_length",len(text)>=450)
    elif kind=="pop_rewrite":
        test("full_rewrite",len(text)>=400 and "verse 1" in low and "bridge" in low)
        test("home_turning_point",bool(re.search(r"\bhome\b|return|back to",text,re.I)))
        test("title_kept","signal in the rain" in low)
        if previous:
            orig=section(previous,r"chorus")
            now=section(text,r"chorus")
            test("chorus_unchanged",bool(orig and now and re.sub(r"\s+"," ",orig).strip()==re.sub(r"\s+"," ",now).strip()))
    elif kind=="country_song":
        test("title", "porch light letter" in low)
        for token in ("verse 1","verse 2","chorus","bridge"):
            test("section_"+token,token in low)
        test("scene",bool(re.search(r"letter",low)) and bool(re.search(r"porch",low)))
        test("complete_lyric_length",len(text)>=400)
    elif kind=="country_rewrite":
        test("sister_reveal",bool(re.search(r"\bsister\b",low)))
        test("scene_preserved","porch" in low and "letter" in low)
        test("full_song","verse 1" in low and "bridge" in low and len(text)>=400)
    elif kind=="acknowledge":
        test("owl_teal","owl" in low and "teal" in low)
    elif kind=="correction_memory":
        test("owl_kept","silver owl" in low or ("owl" in low and "silver" in low))
        test("amber_banner","amber" in low)
        test("old_color_not_selected",not bool(re.search(r"banner\s*(?:is|:|=)\s*teal",low)))
    elif kind=="kitchen_plan":
        for word in ("preheat","vegetable","label"):
            test(word,word in low or (word=="vegetable" and "prep" in low))
        test("not_done_claim",not bool(re.search(r"\bi (?:have|just) (?:preheated|finished|labeled)\b",low)))
    elif kind=="kitchen_followup":
        test("updated_timing",bool(re.search(r"\b18\b|eighteen|less time|shorter",low)))
        test("kept_labeling","label" in low)
        test("food_safety",bool(re.search(r"\bcold|chill|food safe|safety|temperature|date",low)))
        test("defer",bool(re.search(r"\bdefer|later|postpone|after service|reduce|prioriti",low)))
        test("no_fabricated_relief_cook",not bool(re.search(r"(?i)relief cook|coworker (?:just )?arrived|extra cook arrived",text)))
    elif kind=="wage_initial":
        test("total_475",bool(re.search(r"\$?\s*475(?:\.00)?\b",text)))
        test("regular_400",bool(re.search(r"\$?\s*400(?:\.00)?\b",text)))
        test("overtime_75",bool(re.search(r"\$?\s*75(?:\.00)?\b",text)))
    elif kind=="wage_followup":
        test("total_570",bool(re.search(r"\$?\s*570(?:\.00)?\b",text)))
        test("regular_480",bool(re.search(r"\$?\s*480(?:\.00)?\b",text)))
        test("overtime_90",bool(re.search(r"\$?\s*90(?:\.00)?\b",text)))
    elif kind=="metaphor":
        test("metaphor_grounded",bool(re.search(r"bug|joke|metaphor|figurative|software|app|UI",text,re.I)))
        test("not_literal",not bool(re.search(r"actual gremlin|real creature|literally a gremlin",text,re.I)))
    elif kind=="source_ack":
        test("acknowledged_source",bool(re.search(r"(?i)receiv|got|provided|original|reference",text)))
        test("no_generated_verse",not bool(re.search(r"(?im)^\s*\[?(?:verse|chorus)\s*\d*\]?\s*:?\s*$",text)))
    elif kind=="original_remix":
        test("verse_1",bool(re.search(r"(?i)verse\s*1",text)))
        test("verse_2",bool(re.search(r"(?i)verse\s*2",text)))
        test("chorus_and_bridge",bool(re.search(r"(?i)\bchorus\b",text) and re.search(r"(?i)\bbridge\b",text)))
        test("substantial_song",len(text)>=360)
        for n,line in enumerate(ORIGINAL_TEST_LINES,1):
            test("no_verbatim_source_line_"+str(n),line.lower() not in low)
        v1=section(text,r"verse\s*1").strip().casefold()
        v2=section(text,r"verse\s*2").strip().casefold()
        test("distinct_verses",bool(v1 and v2 and v1!=v2))
    elif kind=="feedback_only":
        test("explains_revision_reasoning",bool(re.search(r"(?i)verse|story|different|event|flow|judge",text)))
        test("no_new_song",not bool(re.search(r"(?im)^\s*(?:\*{0,2}|\[)verse\s*[12]\b",text)))
        test("not_research_hijacked",not bool(re.search(r"(?i)lyrics.*verif|cannot.*retrieve.*lyrics",text)))
    elif kind=="pop_adaptation":
        for marker in ("verse 1","verse 2","pre-chorus","chorus","bridge","final chorus"):
            test("section_"+marker,marker in low or (marker=="pre-chorus" and "pre chorus" in low))
        test("train_setting",bool(re.search(r"(?i)train|platform|station|rail",text)))
        test("complete_rewrite",len(text)>=350)
        test("aab_not_universal",not bool(re.search(r"(?im)^.*\bAAB\b.*$",text)))
    elif kind=="public_science":
        test("eclipse_alignment",bool(re.search(r"(?i)moon",text) and re.search(r"(?i)sun",text) and re.search(r"(?i)earth",text)))
        test("partial_and_total",bool(re.search(r"(?i)partial",text) and re.search(r"(?i)total",text)))
        test("not_every_new_moon",bool(re.search(r"(?i)not every|not each|doesn.t|does not|tilt|inclination",text)))
        test("cites_source",len(urls)>=1)
    elif kind=="science_followup":
        test("new_moon_and_tilt",bool(re.search(r"(?i)new moon",text) and re.search(r"(?i)tilt|orbit|inclina|align|node",text)))
        test("no_invented_facts",not bool(re.search(r"(?i)every new moon (?:makes|creates|causes)",text)))
    elif kind=="staffing_initial":
        test("only_rae",bool(re.search(r"(?i)\brae\b",text)))
        test("delivery_15",bool(re.search(r"(?i)\b15\b|fifteen",text)))
        test("alone",bool(re.search(r"(?i)alone|one cook|solo|second.*absent",text)))
    elif kind=="staffing_followup":
        test("time_8",bool(re.search(r"(?i)\b8\b|eight",text)))
        test("rae",bool(re.search(r"(?i)\brae\b",text)))
        test("no_invented_helpers",not bool(re.search(r"(?i)(?:new|extra|additional|another|relief)\s+(?:cook|staff|helper|manager)|(?:coworker|helper|manager)\s+(?:arrives?|helps?|steps?\s+in)",text)))
    elif kind=="debugging":
        test("debug_actions",bool(re.search(r"reproduc|inspect|console|log|event|click|listener|overlay",text,re.I)))
        test("mobile_specific",bool(re.search(r"mobile|touch|tap|viewport|pointer",text,re.I)))
        test("no_false_inspection",not bool(re.search(r"\bi (?:checked|inspected|fixed) your\b",low)))
        test("valid_dom_debugging_api",not bool(re.search(r"(?i)\.\s*getEventListeners\s*\(|\.\s*addEventListener\.toString\s*\(",text)))
    else:raise RuntimeError("Unknown grader "+kind)
    passed=sum(x["pass"] for x in tests)
    return {"status":"PASS_EVIDENCE" if passed==len(tests) else "REVIEW",
            "passed":passed,"total":len(tests),"checks":tests,
            "link_count":len(urls),"link_hosts":list(dict.fromkeys(
                urlsplit(url).hostname for url in urls if urlsplit(url).hostname))[:10]}

async def ask(context,thread_id,prompt,online):
    rid="swr-research-eval-"+uuid.uuid4().hex[:16]
    message={"protocolVersion":2,"modelId":MODEL,
             "profileId":"LALM+ONLINE" if online else "LALM",
             "ingress":"SWRLZ_LALM_STATION",
             "threadId":thread_id,"requestId":rid,
             "messageId":"u-"+uuid.uuid4().hex[:16],
             "assistantMessageId":"a-"+uuid.uuid4().hex[:16],
             "prompt":prompt,"profile":"","userProfile":"","timeZone":"UTC"}
    started=time.perf_counter()
    response=await context.request.post(BASE+"/api/lalm_station/send",
            data=json.dumps(message),headers={"Content-Type":"application/json",
                                               "X-SWRLZ-Request-Id":rid},timeout=30000)
    if response.status!=202:
        raise RuntimeError("SEND_HTTP_"+str(response.status)+":"+base.redact(await response.text(),160))
    ack=await response.json()
    if ack.get("accepted") is False or ack.get("requestId")!=rid:
        raise RuntimeError("SEND_ACK_INVALID")
    old_timeout=base.TIMEOUT
    base.TIMEOUT=BASE_TIMEOUT
    try:
        result=await base.receive(context,started,rid=rid,thread_id=thread_id)
    finally:
        base.TIMEOUT=old_timeout
    if result.get("thread_id")!=thread_id:raise RuntimeError("CROSS_THREAD_RESPONSE")
    return result

async def scenario(browser,case):
    context=await browser.new_context()
    result={"id":case["id"],"turns":[],"outcome":"UNTESTED"}
    thread_id="swr-music-test-"+uuid.uuid4().hex[:18]
    previous=None
    try:
        await base.ensure_guest(context)
        await base.sync(context)
        for n,turn in enumerate(case["turns"],1):
            response=await ask(context,thread_id,turn["prompt"],turn.get("online",False))
            raw=response.pop("text")
            grade=check(turn["kind"],raw,previous)
            excerpt=base.redact(raw,14000)
            result["turns"].append({
                "turn":n,"research_mode_requested":turn.get("online",False),
                "prompt":turn["prompt"],"kind":turn["kind"],"response":excerpt,
                "response_chars":len(raw),"terminal_state":response.get("state"),
                "candidate_validation_status":response.get("candidate_validation_status"),
                "candidate_validation_reasons":response.get("candidate_validation_reasons"),"response_sha256":hashlib.sha256(raw.encode()).hexdigest(),
                "evaluation":grade,"total_ms":response.get("total_ms"),
                "first_text_ms":response.get("first_text_ms"),
                "phases":response.get("phases",[]),"source_link_count":grade["link_count"],
                "source_hosts":grade["link_hosts"]
            })
            previous=raw
        result["outcome"]="PASS_EVIDENCE" if all(
            t["evaluation"]["status"]=="PASS_EVIDENCE" for t in result["turns"]) else "REVIEW"
    except Exception as error:
        result["outcome"]="BLOCKED"
        result["error"]=type(error).__name__+": "+base.redact(str(error),360)
    finally:
        await context.close()
    return result

async def main(batch):
    started=time.perf_counter()
    OUT.mkdir(parents=True,exist_ok=True)
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(headless=True,args=["--disable-dev-shm-usage"])
        try:
            results=[]
            for case in CASES[batch]:
                result=await scenario(browser,case)
                results.append(result)
                print("SWRLZ_BROAD_CASE",json.dumps({
                    "id":result["id"],"outcome":result["outcome"],"turns":len(result["turns"]),
                    "checks":[[t["evaluation"]["passed"],t["evaluation"]["total"]] for t in result["turns"]],
                    "duration_ms":[t["total_ms"] for t in result["turns"]],
                    "research_source_links":[t["source_link_count"] for t in result["turns"]],
                    "failed_checks":[[x["check"] for x in t["evaluation"]["checks"] if not x["pass"]] for t in result["turns"]],
                    "error":result.get("error")
                }),flush=True)
        finally:await browser.close()
    total=[t for r in results for t in r["turns"]]
    data={"schema":"swrlz-broad-guest-qa-v1","batch":batch,
          "utc":datetime.now(timezone.utc).isoformat(),
          "requested_api_model":MODEL,"guest_only":True,
          "results":results,
          "summary":{"scenarios":len(results),
                     "passing_scenarios":sum(x["outcome"]=="PASS_EVIDENCE" for x in results),
                     "review_scenarios":sum(x["outcome"]=="REVIEW" for x in results),
                     "blocked_scenarios":sum(x["outcome"]=="BLOCKED" for x in results),
                     "completed_turns":len(total),
                     "median_turn_ms":round(statistics.median(t["total_ms"] for t in total)) if total else None,
                     "runtime_ms":round((time.perf_counter()-started)*1000)}}
    (OUT/"report.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    lines=["# §C Research / Lyrics / General Conversations — "+batch,"",
           "Test-only, guest-only; no changes to deployed source.","",
           "Actual model transcripts are in report.json. Keyword/structure checks are limited evidence, not a human songwriting-quality score.","",
           "| Scenario | Result | Completed turns |","|---|---|---:|"]
    for r in results:lines.append(f"| {r['id']} | {r['outcome']} | {len(r['turns'])} |")
    lines.extend(["","Median latency of completed turns: "+str(data["summary"]["median_turn_ms"])+" ms",
      "Public research source URLs are recorded but are not automatically verified for authenticity.",
      "Original lyrics are synthetic test outputs; no published song lyrics were requested."])
    (OUT/"summary.md").write_text("\n".join(lines)+"\n")
    print("SWRLZ_BROAD_SUMMARY",json.dumps(data["summary"]),flush=True)
    # REVIEW and BLOCKED are evidence to investigate; preserve all batches
    # while allowing the next category to run. The workflow summary exposes
    # acceptance status, but the workflow itself is diagnostic, not a release.
    return 0
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--batch",choices=sorted(CASES),required=True)
    args=parser.parse_args()
    sys.exit(asyncio.run(main(args.batch)))
