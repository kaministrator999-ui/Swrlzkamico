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


# Round 3: additional fully synthetic, isolated guest conversations. Each
# scenario tests a different failure mode, not merely a reworded first turn.
CASES["research"].extend([
  {"id":"seasons-source-vs-distance","turns":[
    {"kind":"season_research","online":True,"prompt":"Research using a public science education source why Earth has seasons. Explain axial tilt and sunlight angle, and distinguish this from the incorrect claim that seasons are caused mainly by Earth's distance from the Sun. Include a source URL."},
    {"kind":"season_followup","prompt":"Use only the research above, without a new search: why do the northern and southern hemispheres have opposite seasons? Keep it concise and don't invent a source."}
  ]},
  {"id":"music-theory-analysis-without-recording-lyrics","turns":[
    {"kind":"song_structure_research","online":True,"prompt":"Research twelve-bar blues AAB verse structure and compare it to pop verse, pre-chorus and chorus sections. Explain which phrase repeats in AAB and why musical bars are not the same thing as lyric lines. Cite a public teaching source. Do not look up or quote any published song lyrics."},
    {"kind":"blues_lyrics","prompt":"Using your explanation, compose exactly TWO brand-new fictional AAB blues verses about a railway platform. Label Verse 1 and Verse 2. In each verse sing one A line, repeat it exactly, then sing one different B line. No chorus."}
  ]},
  {"id":"electronic-music-history-context","turns":[
    {"kind":"music_history_research","online":True,"prompt":"Research how synthesizers and sequencers shaped early electronic pop arrangements, citing an accessible public source. Explain the functions without requesting or reproducing lyrics from any recording."},
    {"kind":"music_history_followup","prompt":"Without a new web lookup, explain whether a synth-pop song must always use an electronic drum machine. Answer based on instrument roles, not a made-up universal rule."}
  ]}
])
CASES["songwriting"].extend([
  {"id":"rain-title-not-a-weather-lookup","turns":[
    {"kind":"weather_safe_song","prompt":"Write a complete ORIGINAL song titled 'Rain Glass Lantern' with Verse 1, Chorus, Verse 2, Chorus, Bridge and Final Chorus. In the fictional story a lantern shines through rainy glass. This is creative writing, not a weather question. Make both verses have different events and the bridge a turning point."},
    {"kind":"weather_safe_rewrite","prompt":"Revise that ORIGINAL song's bridge so the protagonist chooses to return home to their family. Keep the title 'Rain Glass Lantern', both verses and the recurring chorus, and return all lyrics with section labels. Do not look up a real recording."}
  ]},
  {"id":"eight-bar-rap-followed-by-editorial-critique","turns":[
    {"kind":"rap_original","prompt":"Write a fresh eight-bar boom-bap rap about a fictional midnight inventor. Number bars 1 through 8, then add a labeled four-line Hook and one sentence about stresses or flow. Show inventive internal rhyme; do not imitate a performer."},
    {"kind":"feedback_only","prompt":"Don't write another rap. Explain where the plot in bars 1-4 moves forward in bars 5-8, and identify anything about actual rhythm or musical flow that you cannot verify from text alone. No web lookup."}
  ]},
  {"id":"folk-song-perspective-change","turns":[
    {"kind":"folk_story","prompt":"Write an original folk ballad titled 'Paper Compass' about a father and daughter using a hand-drawn map. Label Verse 1, Chorus, Verse 2, Chorus, Bridge and Final Chorus. Give the bridge a concrete discovery, not a generic pep talk."},
    {"kind":"folk_rewrite","prompt":"Rewrite the full song with its title, map, chorus and emotional arc preserved, but replace the father with an older BROTHER. Do not refer to a published song or fetch lyrics."}
  ]}
])
CASES["conversation"].extend([
  {"id":"exact-list-revision-and-numbering","turns":[
    {"kind":"list_initial","prompt":"For a fictional inventory, list exactly four paint swatches, numbered 1 to 4: cobalt, maroon, ivory and olive. No additional colors or repeated numbering."},
    {"kind":"list_revision","prompt":"Correction: remove ONLY maroon from that list. Return the remaining three colors numbered 1, 2, 3 with no new colors and don't mention the removed one."}
  ]},
  {"id":"fictional-context-weather-word-ambiguity","turns":[
    {"kind":"fictional_ack","prompt":"For a pretend story, a robin stands in rain holding a small amber sign. This is fiction, not a forecast or a location request. Restate the scene in one sentence."},
    {"kind":"fictional_followup","prompt":"Change the bird to a sparrow but keep the amber sign. Don't check the weather; this is still a fictional scene."}
  ]},
  {"id":"debugger-no-fabricated-inspection","turns":[
    {"kind":"debugging","prompt":"Suggest three concrete things I can inspect when a mobile web button occasionally ignores touch. You have no access to my code. Do not claim you've fixed it or suggest nonexistent DOM APIs."},
    {"kind":"debugging","prompt":"Now the same issue also happens in desktop Chrome. Update the debugging checks to include overlapping elements and pointer events. You still have not inspected any code."}
  ]}
])
CASES["transformations"].extend([
  {"id":"parody-of-user-authored-station-verse","turns":[
    {"kind":"source_ack","prompt":"These two fictional original lines are my own, not from a recording. Simply acknowledge receipt, and don't produce lyrics yet:\nA toaster argues with my clock at dawn\nMy coffee made a map and wandered on"},
    {"kind":"parody_original","prompt":"Make a fully original comedic parody of my fictional toaster scene. Use labeled Verse 1, Chorus, Verse 2 and Bridge, with escalating appliance mishaps and a punchline. Don't quote the lines verbatim, and don't research existing songs."},
    {"kind":"feedback_only","prompt":"I'm critiquing the joke, not requesting another song. Explain where the comic escalation occurs and what a human would still need to judge about the timing. No search and no new lyrics."}
  ]},
  {"id":"remaster-preserve-authored-hook","turns":[
    {"kind":"song_seed","prompt":"Write a short ORIGINAL song called Little Lighthouse about a tiny beacon guiding a boat. Include Verse 1, Chorus, Verse 2 and Bridge. Make the EXACT chorus hook 'Little lighthouse, bring me home'. This is user-directed fictional material."},
    {"kind":"remaster_original","prompt":"Remaster the wording of the original fictional song: keep the hook 'Little lighthouse, bring me home' EXACTLY, keep a harbor/shore setting, give both verses more concrete action, and return the complete song. This is a rewrite, not a search for a recording."}
  ]},
  {"id":"fictional-lullaby-to-electropop","turns":[
    {"kind":"source_ack","prompt":"Remember this original fictional lullaby line I just wrote: 'A paper moon is humming through the bedroom window.' Acknowledge it briefly; no web and no forecast."},
    {"kind":"genre_switch","prompt":"Adapt the idea of my fictional paper-moon lullaby into a fully original electropop song. Use Verse 1, Pre-Chorus, Chorus, Verse 2, Bridge and Final Chorus. Invent a new hook and separate events in the verses. Don't search for published lyrics."}
  ]}
])


# Round 4: higher-order reasoning and answer quality. All facts here are
# synthetic, explicit in each isolated guest thread and verifiable without web.
# Graders check supported claims/constraints, not model eloquence.
CASES["reasoning"]=[
  {"id":"client-server-direction","turns":[
    {"kind":"handoff_forward","prompt":"In a toy web app the CLIENT browser sends a JSON request to a SERVER API. State the request direction in one short line; do not invent intermediate components."},
    {"kind":"handoff_reverse","prompt":"Now the server has produced its reply. In the same toy app, what is the direction of the response? Say the direction directly without repeating the request direction as the answer."}
  ]},
  {"id":"conflicting-evidence-retained","turns":[
    {"kind":"conflicting_sources","prompt":"Two synthetic reports refer to DIFFERENT datasets: ALPHA records 120 completed units, BETA records 145 completed units. State both figures and explain why a single consolidated total cannot be determined from this alone. Do not invent a merged figure or cite real sources."},
    {"kind":"corrected_sources","prompt":"Correction: only ALPHA's completed-unit count changes from 120 to 135; BETA remains 145. Give the updated pair and whether a combined unique count is now known. Do not treat the datasets as proven disjoint."}
  ]},
  {"id":"guest-browser-constraints","turns":[
    {"kind":"guest_constraints","prompt":"Plan a hypothetical two-device game lobby: a phone and a VR headset must connect through their browsers; joining is guest-only, with no account requirement and no app download. Give three concrete checks before inviting players. Do not silently change the constraints."},
    {"kind":"guest_constraints_update","prompt":"Change just one constraint: a DESKTOP browser joins as a third device. Keep guest-only access, browser play, and no download. Update the checks without adding login or installations."}
  ]},
  {"id":"tests-are-not-deployments","turns":[
    {"kind":"unverified_tests","prompt":"A synthetic build has exactly two failing tests and one passing test. You have not inspected the code or rerun anything. Report what is known and recommend the next verification action without claiming a fix."},
    {"kind":"tests_vs_deploy","prompt":"Update from the test team: now THREE tests pass, but nobody has deployed the build. Summarize the new test state and the separate deployment state. Do not claim live success."}
  ]},
  {"id":"controlled-benchmark-reasoning","turns":[
    {"kind":"benchmark_confounded","prompt":"A synthetic performance report shows version A at 140 ms and version B at 180 ms, but each was measured on a different host. Can we claim a causal speed improvement? Explain the confound and recommend a controlled comparison."},
    {"kind":"benchmark_controlled","prompt":"A controlled same-host rerun instead measures A at 140 ms and B at 165 ms. Report which one is faster in this test and by how many milliseconds, but don't claim universal performance from a single benchmark."}
  ]},
  {"id":"surgical-task-update","turns":[
    {"kind":"task_list","prompt":"For a hypothetical chat project list exactly these three pending tasks: fix the Stop button, improve lyric formatting, and change the logo. Do not claim any task is completed."},
    {"kind":"task_list_revision","prompt":"Revise ONLY task 3: replace 'change the logo' with 'design a dark-theme icon'. Tasks 1 and 2 must remain pending and unchanged. Give the complete updated list, with no fourth task or claim of code changes."}
  ]}
]

# Chromium verifies real phone-sized DOM interaction, not only API transport:
# two practical context tests plus one full song composition/revision through
# visible guest chat. All other cases use Chromium's isolated request context.
UI_SCENARIOS={"correction-and-memory","fictional-context-weather-word-ambiguity",
              "rain-title-not-a-weather-lookup"}
for _batch in CASES.values():
    for _case in _batch:
        _case["lane"]="ui" if _case["id"] in UI_SCENARIOS else "api"

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
    """Count complete AAB stanzas, including markdown headings and A:/B: labels.

    Explanatory notes are not sung lines. A fourth sung line is not discarded
    just to make the model's output count as a valid three-line stanza.
    """
    heading=re.compile(
        r"(?i)^\s*(?:#{1,6}\s*)?(?:\*{1,2})?\s*\[?verse\s*([12])"
        r"(?:\s*\])?(?:\s*\*{1,2})?\s*:?(?:\s*\*{1,2})?\s*$")
    other=re.compile(
        r"(?i)^\s*(?:#{1,6}\s*)?(?:\*{1,2})?\s*"
        r"\[?(?:chorus|bridge|hook|outro|intro|notes?|a quick note|explanation)\b")
    lyric={1:[],2:[]}
    current=None
    for raw in text.splitlines():
        line=raw.strip()
        if not line or line.startswith((chr(96)*3,"---","***")):
            continue
        header=heading.match(line)
        if header:
            current=int(header.group(1))
            continue
        if other.match(line):
            current=None
            continue
        if current is None:
            continue
        line=re.sub(r"(?i)^\s*\*{0,2}(?:a|b)\s*:\*{0,2}\s*","",line)
        if re.match(r"^\s*\(.*\)\s*$",line):
            continue
        normalized=re.sub(r"\W+"," ",line.casefold()).strip()
        if normalized:
            lyric[current].append(normalized)
    return sum(len(v)==3 and v[0]==v[1] and v[2]!=v[0]
               for v in lyric.values())

def check(kind,text,previous=None,phases=None,allow_search=False):
    low=text.lower()
    tests=[]
    def test(name,value):tests.append({"check":name,"pass":bool(value)})
    urls=cited_urls(text)
    # A committed error message is never a successful completion.
    test("no_generation_or_router_error",not bool(re.search(
        r"(?i)(?:generation failed|HTTP Error 5\d\d|LYRICS_VERIFICATION_BLOCKED|"
        r"WEATHER_RETRIEVAL_BLOCKED|internal server error|traceback \(most recent)",text)))
    # None of these scenarios asks for an executable program. A failed code
    # draft is a routing error, not a response to a lyric or explanation task.
    code_phases={"CODE_DRAFT_STREAMING","CODE_REPAIRING","RESUMING_CODE",
                 "CODE_DRAFT_SAVED","CANDIDATE_INCOMPLETE"}
    test("no_code_generator_hijack",not bool(
        re.search(r"(?i)source has been generated but did not pass code validation|"
                  r"send\s+\*{0,2}continue code|unverified draft is marked",text)
        or (phases is not None and any(p in code_phases for p in phases))))
    # Every scenario in this suite asks for ORIGINAL lyrics or public research
    # about a subject, never external copyrighted lyric reproduction.
    test("no_lyrics_lookup_hijack",not bool(re.search(
        r"(?i)I found search results for the lyrics|couldn.t verify the requested lyric text|LYRICS_VERIFICATION_BLOCKED",text)))
    test("no_weather_lookup_hijack",not bool(re.search(
        r"(?i)I need a city/region|location before I can check live weather|WEATHER_RETRIEVAL_BLOCKED",text)))
    test("no_local_inference_failure",not bool(re.search(
        r"(?i)Local Qwen inference failed|please try again|upstream inference error|model overloaded",text)))
    if phases is not None and not allow_search:
        network_phases={"SEARCH_STARTED","SEARCH_PROVIDER_VISIT","WEATHER_FETCH_COMPLETE",
                        "LYRICS_VERIFICATION_BLOCKED","WEATHER_RETRIEVAL_BLOCKED"}
        test("no_unrequested_web_tool",not any(p in network_phases for p in phases))
    if kind=="handoff_forward":
        test("request_client_to_server",bool(re.search(r"(?i)client\s*(?:→|->|[- ]to[- ]|toward(?:s)?|sends?\s+(?:a\s+)?(?:json\s+)?request\s+to)\s*server",text)))
        test("no_false_reverse",not bool(re.search(r"(?i)^(?:server\s*(?:→|->|to)\s*client)\s*$",text.strip())))
    elif kind=="handoff_reverse":
        test("reply_server_to_client",bool(re.search(r"(?i)server\s*(?:→|->|[- ]to[- ]|toward(?:s)?|sends?\s+(?:the\s+)?(?:reply|response)\s+to)\s*client",text)))
    elif kind=="conflicting_sources":
        test("alpha_120",bool(re.search(r"(?is)\balpha\b.{0,55}\b120\b",text)))
        test("beta_145",bool(re.search(r"(?is)\bbeta\b.{0,55}\b145\b",text)))
        test("uncertain_combined",bool(re.search(r"(?i)cannot|can't|not (?:possible|known|enough)|unknown|different datasets|overlap|disjoint|cannot determine",text)))
        test("not_fabricated_sum",not bool(re.search(r"(?i)(?:total|combined|merged)\s*(?:is|:|=)\s*265\b",text)))
    elif kind=="corrected_sources":
        test("alpha_135",bool(re.search(r"(?is)\balpha\b.{0,55}\b135\b",text)))
        test("beta_145",bool(re.search(r"(?is)\bbeta\b.{0,55}\b145\b",text)))
        test("no_old_alpha",not bool(re.search(r"(?is)\balpha\b.{0,20}(?:is|:|=)\s*120\b",text)))
        test("no_invented_union",bool(re.search(r"(?i)unknown|cannot|can't|overlap|not (?:known|enough|determined)|disjoint",text)))
    elif kind=="guest_constraints":
        test("phone_and_vr",bool(re.search(r"(?i)phone|mobile",text) and re.search(r"(?i)\bvr\b|headset",text)))
        test("browser",bool(re.search(r"(?i)browser|web",text)))
        test("guest",bool(re.search(r"(?i)guest|without (?:an? )?account|no login|no sign",text)))
        test("no_forced_install",not bool(re.search(r"(?i)(?:must|need|require|only after you)\s+(?:to\s+)?(?:install|download|sign in|log in|register)",text)))
    elif kind=="guest_constraints_update":
        test("third_desktop",bool(re.search(r"(?i)desktop",text)))
        test("guest_kept",bool(re.search(r"(?i)guest|no (?:account|login)|without.*(?:account|login)",text)))
        test("browsers_kept",bool(re.search(r"(?i)browser|web",text)))
        test("no_forced_install",not bool(re.search(r"(?i)(?:must|need|require|only after you)\s+(?:to\s+)?(?:install|download|sign in|log in|register)",text)))
    elif kind=="unverified_tests":
        test("two_fail",bool(re.search(r"(?i)(?:\b2\b|two).{0,25}fail|fail.{0,25}(?:\b2\b|two)",text)))
        test("one_pass",bool(re.search(r"(?i)(?:\b1\b|one).{0,25}pass|pass.{0,25}(?:\b1\b|one)",text)))
        test("no_fake_fix",not bool(re.search(r"(?i)\bi (?:fixed|patched|reran|verified|deployed)\b",text)))
        test("next_check",bool(re.search(r"(?i)inspect|reproduc|rerun|investigat|check|test|trace|logs?",text)))
    elif kind=="tests_vs_deploy":
        test("three_pass",bool(re.search(r"(?i)(?:\b3\b|three).{0,30}pass|pass.{0,30}(?:\b3\b|three)",text)))
        test("not_deployed",bool(re.search(r"(?i)not deployed|not yet deployed|haven't deployed|hasn't been deployed|no deployment|not live|deployment.*pending",text)))
        test("no_live_claim",not bool(re.search(r"(?i)\b(?:now|already) live\b|successfully deployed|deployed to production",text)))
    elif kind=="benchmark_confounded":
        test("both_measurements",bool(re.search(r"\b140\b",text) and re.search(r"\b180\b",text)))
        test("confounding",bool(re.search(r"(?i)host|environment|hardware|machine|controlled|confound",text)))
        test("not_causal_claim",bool(re.search(r"(?i)cannot|can't|not (?:necessarily|reliably|enough)|uncertain|confound|doesn't prove",text)))
    elif kind=="benchmark_controlled":
        test("both_measurements",bool(re.search(r"\b140\b",text) and re.search(r"\b165\b",text)))
        test("difference_25ms",bool(re.search(r"(?i)\b25\s*(?:ms|milliseconds)\b",text)))
        test("a_faster",bool(re.search(r"(?i)\bA\b.{0,30}(?:fast|quick|low)|(?:fast|quick|low).{0,30}\bA\b",text)))
        test("scope_calibrated",bool(re.search(r"(?i)test|single|measurement|run|not necessarily|other (?:hosts|workloads)",text)))
    elif kind=="task_list":
        for n,p in (("stop",r"\bstop\b"),("lyrics",r"lyric"),("logo",r"logo")):
            test("task_"+n,bool(re.search(p,text,re.I)))
        test("not_completed_claim",not bool(re.search(r"(?i)\bi (?:fixed|completed|changed|deployed)\b",text)))
    elif kind=="task_list_revision":
        test("stop_kept",bool(re.search(r"(?i)\bstop\b",text)))
        test("lyrics_kept",bool(re.search(r"(?i)lyric",text)))
        test("new_icon_task",bool(re.search(r"(?i)dark[- ]theme",text) and re.search(r"(?i)icon",text)))
        test("no_logo_task",not bool(re.search(r"(?im)^\s*(?:[-*]|\d+[.):])?\s*(?:change|update|redesign)\s+(?:the\s+)?logo",text)))
        test("no_fourth_task",len(re.findall(r"(?m)^\s*(?:\d+[.)]|[-*])\s+\S+",text))<=3)
        test("not_claimed_done",not bool(re.search(r"(?i)\bi (?:fixed|completed|changed|deployed)\b",text)))
    elif kind=="d2_classes":
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
        test("train_theme",bool(re.search(r"train|platform|rail|station|ticket|tracks?|steam|engine",text,re.I)))
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
        test("metaphor_grounded",bool(re.search(r"bug|joke|metaphor|figurative|software|app|UI|glitch|easter egg|layout",text,re.I)))
        test("not_literal",not bool(re.search(r"actual gremlin|real creature|literally a gremlin",text,re.I)))
    elif kind=="source_ack":
        test("acknowledged_source",bool(re.search(r"(?i)receiv|got|provided|original|reference|acknowledg|noted|understood|have (?:those|your|the) lines|ready",text)))
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
        source_bigrams=set()
        for line in ORIGINAL_TEST_LINES:
            words=re.findall(r"[a-z]+",line.casefold())
            source_bigrams.update(" ".join(words[i:i+2]) for i in range(len(words)-1))
        output_words=re.findall(r"[a-z]+",text.casefold())
        output_bigrams=set(" ".join(output_words[i:i+2]) for i in range(len(output_words)-1))
        # Two incidental shared word pairs are tolerable; recycling several
        # distinctive scene fragments is not a fresh interpretation.
        reused=[b for b in source_bigrams & output_bigrams if
                not b.startswith(("the ","and ","a ","my ","of ","to ","in ","at "))]
        test("limited_recycled_source_imagery",len(reused)<3)
    elif kind=="feedback_only":
        test("explains_revision_reasoning",bool(re.search(r"(?i)verse|story|different|event|flow|judge",text)))
        test("no_new_song",not bool(re.search(r"(?im)^\s*(?:\*{0,2}|\[)verse\s*[12]\b",text)))
        test("not_research_hijacked",not bool(re.search(r"(?i)lyrics.*verif|cannot.*retrieve.*lyrics",text)))
    elif kind=="weather_safe_song":
        for token in ("verse 1","chorus","verse 2","bridge"):
            test("section_"+token,token in low)
        test("requested_title","rain glass lantern" in low)
        test("substantial_original_song",len(text)>=240)
    elif kind=="weather_safe_rewrite":
        test("title_kept","rain glass lantern" in low)
        test("bridge_changed",bool(re.search(r"(?i)bridge",text) and re.search(r"(?i)home|return|family",text)))
        test("complete_song",len(text)>=240 and "verse 1" in low and "verse 2" in low)
    elif kind=="folk_story":
        test("requested_title","paper compass" in low)
        for token in ("verse 1","verse 2","chorus","bridge"):
            test("section_"+token,token in low)
        test("story",bool(re.search(r"(?i)compass|map",text) and re.search(r"(?i)father|daughter",text)))
    elif kind=="folk_rewrite":
        test("new_relation",bool(re.search(r"(?i)brother",text)))
        test("kept_theme",bool(re.search(r"(?i)compass|map",text)))
        test("full_rewrite",len(text)>=280 and "bridge" in low and "chorus" in low)
    elif kind=="list_initial":
        for color in ("cobalt","maroon","ivory","olive"):
            test("listed_"+color,color in low)
        test("no_scarlet","scarlet" not in low)
    elif kind=="list_revision":
        for color in ("cobalt","ivory","olive"):
            test("retained_"+color,color in low)
        test("maroon_removed","maroon" not in low)
        test("only_three",len(re.findall(r"(?m)^\s*(?:[-*]|\d+[.)])\s+",text))<=3)
    elif kind=="fictional_ack":
        test("fictional_robin","robin" in low)
        test("fictional_rain","rain" in low)
    elif kind=="fictional_followup":
        test("amber_kept","amber" in low)
        test("updated_bird","sparrow" in low)
        test("no_real_weather_data",not bool(re.search(r"(?i)forecast|temperature|weather station|humidity",text)))
    elif kind=="parody_original":
        for token in ("verse 1","chorus","verse 2"):
            test("section_"+token,token in low)
        test("comic_turn",bool(re.search(r"(?i)robot|toaster|spoon|receipt|kitchen|appliance",text)))
        test("complete",len(text)>=200)
        test("no_verbatim_owner_line",not any(line.lower() in low for line in ("a toaster argues with my clock at dawn","my coffee made a map and wandered on")))
    elif kind=="song_seed":
        test("chorus",bool(re.search(r"(?i)chorus",text)))
        test("user_hook","little lighthouse" in low)
        test("verse",bool(re.search(r"(?i)verse",text)))
    elif kind=="remaster_original":
        test("same_hook","little lighthouse, bring me home" in low)
        test("complete_rewrite",len(text)>=200 and "verse" in low and "chorus" in low)
        test("different_scene",bool(re.search(r"(?i)harbor|pier|boat|shore",text)))
    elif kind=="genre_switch":
        for token in ("verse 1","verse 2","pre-chorus","chorus","bridge"):
            test("section_"+token,token in low or (token=="pre-chorus" and "pre chorus" in low))
        test("lullaby_reference",bool(re.search(r"(?i)moon|bedtime|sleep|lantern",text)))
        test("complete",len(text)>=240)
        test("not_a_verbatim_lullaby", "a paper moon is humming through the bedroom window" not in low)
    elif kind=="season_research":
        test("tilt",bool(re.search(r"(?i)tilt|axial inclination",text)))
        test("sunlight",bool(re.search(r"(?i)sunlight|solar|sun|daylight",text)))
        test("cites_source",len(urls)>=1)
        test("not_distance_cause",bool(re.search(r"(?i)not.*distanc|tilt.*(?:instead|rather)",text)))
    elif kind=="season_followup":
        test("tilt_kept",bool(re.search(r"(?i)tilt|axial",text)))
        test("north_south_opposite",bool(re.search(r"(?i)opposite|northern|southern|hemispher",text)))
    elif kind=="music_history_research":
        test("synth",bool(re.search(r"(?i)synthesiz|synth",text)))
        test("sequencer",bool(re.search(r"(?i)sequenc|oscillator|analog|electronic",text)))
        test("citation",len(urls)>=1)
    elif kind=="music_history_followup":
        test("electronic_context",bool(re.search(r"(?i)synth|sequenc|oscillator|electronic",text)))
        test("acknowledge_limits",bool(re.search(r"(?i)context|depends|vary|not always|not every|instrument",text)))
    elif kind=="pop_adaptation":
        for marker in ("verse 1","verse 2","pre-chorus","chorus","bridge","final chorus"):
            test("section_"+marker,marker in low or (marker=="pre-chorus" and "pre chorus" in low))
        test("train_setting",bool(re.search(r"(?i)train|platform|station|rail",text)))
        test("complete_rewrite",len(text)>=350)
        test("aab_not_universal",not bool(re.search(r"(?im)^.*\bAAB\b.*$",text)))
        def repeated_verse_lines(body):
            normalized=[re.sub(r"^(?:[AB]:\s*)","",re.sub(r"\W+"," ",line.casefold()).strip())
                        for line in body.splitlines() if line.strip()]
            return any(len(a)>10 and a==b for a,b in zip(normalized,normalized[1:]))
        test("no_blues_aab_copied_into_pop_verses",
             not any(repeated_verse_lines(section(text,r"verse\s*"+str(n)))
                     for n in (1,2)))
    elif kind=="public_science":
        test("eclipse_alignment",bool(re.search(r"(?i)moon",text) and re.search(r"(?i)sun",text) and re.search(r"(?i)earth",text)))
        test("partial_and_total",bool(re.search(r"(?i)partial",text) and re.search(r"(?i)total",text)))
        test("not_every_new_moon",bool(re.search(r"(?i)not every|not each|doesn.t|does not|tilt|inclination",text)))
        test("cites_source",len(urls)>=1)
    elif kind=="science_followup":
        test("new_moon_and_tilt",bool(re.search(r"(?i)new moon",text) and re.search(r"(?i)tilt|orbit|inclina|align|node",text)))
        test("no_invented_facts",not bool(re.search(r"(?i)(?<!not )\bevery new moon (?:makes|creates|causes)",text)))
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

def failure_types(result):
    """Observable failure families, not inferred model-internal causes."""
    labels=set()
    if result.get("outcome")=="BLOCKED":
        msg=result.get("error") or ""
        labels.add("TURN_TIMEOUT" if "TimeoutError" in msg else "TRANSPORT_OR_UI_BLOCKER")
    checks_to_type={
        "no_weather_lookup_hijack":"WEATHER_ROUTE",
        "no_lyrics_lookup_hijack":"PUBLISHED_LYRICS_ROUTE",
        "no_code_generator_hijack":"CODE_ROUTE",
        "no_unrequested_web_tool":"UNREQUESTED_RESEARCH",
        "no_local_inference_failure":"INFERENCE_FAILURE",
        "no_generation_or_router_error":"GENERATION_OR_ROUTER_ERROR",
    }
    for turn in result.get("turns",[]):
        bad=[c["check"] for c in turn["evaluation"]["checks"] if not c["pass"]]
        known=set(bad)&set(checks_to_type)
        labels.update(checks_to_type[k] for k in known)
        if set(bad)-set(checks_to_type):
            labels.add("CONTENT_OR_FORMAT_REVIEW")
    return sorted(labels)

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
    lane=case.get("lane","api")
    context=await browser.new_context(**({"viewport":{"width":390,"height":844},
              "is_mobile":True,"has_touch":True} if lane=="ui" else {}))
    result={"id":case["id"],"lane":lane,"turns":[],"outcome":"UNTESTED"}
    thread_id="swr-music-test-"+uuid.uuid4().hex[:18] if lane=="api" else None
    previous=None
    page=None
    try:
        await base.ensure_guest(context)
        await base.sync(context)
        if lane=="ui":
            page=await context.new_page()
            page_response=await page.goto(BASE+"/",wait_until="domcontentloaded",timeout=30000)
            if not page_response or page_response.status!=200:
                raise RuntimeError("GUEST_UI_PAGE_HTTP_ERROR")
            await page.locator("#prompt").wait_for(state="visible",timeout=25000)
            await base.dismiss_update_overlay(page)
        for n,turn in enumerate(case["turns"],1):
            if page is not None:
                if turn.get("online"):
                    raise RuntimeError("UI_LANE_DOES_NOT_OVERRIDE_RESEARCH_PROFILE")
                previous_timeout=base.TIMEOUT
                base.TIMEOUT=BASE_TIMEOUT
                try:
                    response=await base.ui_turn(context,page,turn["prompt"],thread_id,n)
                finally:
                    base.TIMEOUT=previous_timeout
                if thread_id is not None and response["thread_id"]!=thread_id:
                    raise RuntimeError("GUEST_UI_THREAD_CHANGED")
                thread_id=response["thread_id"]
            else:
                response=await ask(context,thread_id,turn["prompt"],turn.get("online",False))
            raw=response.pop("text")
            grade=check(turn["kind"],raw,previous,
                        phases=response.get("phases",[]),allow_search=turn.get("online",False))
            excerpt=base.redact(raw,14000)
            result["turns"].append({
                "turn":n,"lane":lane,"ui_response_visible":response.get("ui_response_visible"),
                "ui_rendered_chars":response.get("ui_rendered_chars"),
                "research_mode_requested":turn.get("online",False),
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
    result["failure_types"]=failure_types(result)
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
                    "error":result.get("error"),"failure_types":result.get("failure_types",[])
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
                     "failure_type_counts":{kind:sum(kind in r.get("failure_types",[]) for r in results)
                         for kind in sorted({key for r in results for key in r.get("failure_types",[])})},
                     "median_turn_ms":round(statistics.median(t["total_ms"] for t in total)) if total else None,
                     "runtime_ms":round((time.perf_counter()-started)*1000)}}
    (OUT/"report.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    lines=["# §C Research / Lyrics / General Conversations — "+batch,"",
           "Test-only, guest-only; 3 mobile Chromium UI scenarios and the remainder through isolated Chromium request contexts. No changes to deployed source.","",
           "Actual model transcripts are in report.json. Keyword/structure checks are limited evidence, not a human songwriting-quality score.","",
           "| Scenario | Result | Completed turns |","|---|---|---:|"]
    for r in results:lines.append(f"| {r['id']} | {r['outcome']} | {len(r['turns'])} |")
    lines.extend(["","Observed failure families: "+str(data["summary"]["failure_type_counts"]),
                  "Failure families are telemetry/check evidence, not a definitive root-cause diagnosis.",""])
    lines.extend(["","Median latency of completed turns: "+str(data["summary"]["median_turn_ms"])+" ms",
      "Public research source URLs are recorded but are not automatically verified for authenticity.",
      "Original lyrics are synthetic test outputs; no published song lyrics were requested."])
    (OUT/"summary.md").write_text("\n".join(lines)+"\n")
    print("SWRLZ_BROAD_SUMMARY",json.dumps(data["summary"]),flush=True)
    # REVIEW and BLOCKED are evidence to investigate; preserve all batches
    # while allowing the next category to run. The workflow summary exposes
    # acceptance status, but the workflow itself is diagnostic, not a release.
    # Keep the default diagnostic mode for exploratory history. Strict mode
    # makes new CI an actual acceptance gate: a green workflow can no longer
    # be misread as all model replies passing.
    if os.getenv("SWRLZ_BROAD_STRICT")=="1" and (
        data["summary"]["review_scenarios"] or data["summary"]["blocked_scenarios"]):
        print("SWRLZ_BROAD_ACCEPTANCE_FAILURE",json.dumps(data["summary"]),flush=True)
        return 1
    return 0
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--batch",choices=sorted(CASES),required=True)
    args=parser.parse_args()
    sys.exit(asyncio.run(main(args.batch)))
