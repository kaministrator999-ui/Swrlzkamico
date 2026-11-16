#!/usr/bin/env python3
"""Minimal §C research-vs-lyrics routing A/B: neutral phrasing, guest-only.

Isolates intent classification from long-form output cost by testing
short original compositions without named artists or published lyrics.
"""
from __future__ import annotations
import asyncio,json,re,sys,time,uuid,hashlib
from datetime import datetime,timezone
from pathlib import Path
from playwright.async_api import async_playwright
from scripts import eval_chat_guest_suite as base
from scripts import eval_chat_research_lyrics_conversations as broad
OUT=Path("reports/swrlz-music-intent-probes")
SAMPLES=[
 {"id":"theory-no-lyrics-word","online":True,"prompt":
  "Research traditional twelve-bar blues AAB verse form versus common pop verse/pre-chorus/chorus architecture. Explain what repeats, how form supports storytelling, and why these are conventions rather than strict rules. Cite two public music-education source URLs. Discuss only musical structure, not existing songs.",
  "must":[r"(?i)A[-–]?A[-–]?B",r"(?i)12[- ]?bar|twelve[- ]?bar",r"(?i)pre[- ]?chorus",r"https?://"]},
 {"id":"original-pop-neutral-title","online":False,"prompt":
  "Write an ORIGINAL short synth-pop song titled 'Neon Road'. Label Verse 1, Pre-Chorus, Chorus, Verse 2, Bridge, Final Chorus. Keep each section 2 to 4 sung lines, with a consistent catchy chorus hook, a tension-building pre-chorus, and a bridge where the narrator changes their decision. No other songs or artists.",
  "must":[r"(?i)verse\s*1",r"(?i)pre[- ]?chorus",r"(?i)chorus",r"(?i)verse\s*2",r"(?i)bridge"]},
 {"id":"original-eight-bar-rap","online":False,"prompt":
  "Write ORIGINAL boom-bap rap about an inventor building a machine after midnight. Output a labeled Verse of exactly eight numbered bars (1 through 8) with internal rhymes and a labeled four-line Hook. Keep a coherent story and short phrases that fit the beat. Do not imitate any real artist.",
  "must":[r"(?i)\bverse\b",r"(?i)\bhook\b",r"(?m)^\s*1[.):]\s+",r"(?m)^\s*8[.):]\s+"]}
]
async def main():
    OUT.mkdir(parents=True,exist_ok=True)
    res={"schema":"swrlz-music-neutral-route-probe-v1","utc":datetime.now(timezone.utc).isoformat(),
         "mode":"anonymous_guest","results":[]}
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(headless=True,args=["--disable-dev-shm-usage"])
        try:
            for sample in SAMPLES:
                cx=await browser.new_context()
                record={"id":sample["id"],"online_requested":sample["online"],"status":"UNTESTED"}
                try:
                    await base.ensure_guest(cx)
                    await base.sync(cx)
                    tid="swr-neutral-music-"+uuid.uuid4().hex[:16]
                    reply=await broad.ask(cx,tid,sample["prompt"],sample["online"])
                    text=reply["text"]
                    record.update({
                      "duration_ms":reply.get("total_ms"),
                      "response":base.redact(text,14000),
                      "response_sha256":hashlib.sha256(text.encode()).hexdigest(),
                      "phases":reply.get("phases"),
                      "source_links":broad.cited_urls(text)[:12],
                      "checks":[{"pattern":p,"pass":bool(re.search(p,text))} for p in sample["must"]]})
                    record["status"]="PASS_EVIDENCE" if all(x["pass"] for x in record["checks"]) else "REVIEW"
                except Exception as exc:
                    record.update({"status":"BLOCKED","error":type(exc).__name__+":"+base.redact(exc,300)})
                finally:
                    await cx.close()
                res["results"].append(record)
                print("MUSIC_NEUTRAL_PROBE",json.dumps({"id":record["id"],"status":record["status"],
                      "duration_ms":record.get("duration_ms"),
                      "phases":record.get("phases",[])[-8:] if record.get("phases") else [],
                      "checks":[v["pass"] for v in record.get("checks",[])],
                      "error":record.get("error")}),flush=True)
        finally:
            await browser.close()
    (OUT/"report.json").write_text(json.dumps(res,indent=2,ensure_ascii=False)+"\n")
    print("MUSIC_NEUTRAL_SUMMARY",json.dumps({"passing":sum(x["status"]=="PASS_EVIDENCE" for x in res["results"]),
          "review":sum(x["status"]=="REVIEW" for x in res["results"]),
          "blocked":sum(x["status"]=="BLOCKED" for x in res["results"])}),flush=True)
if __name__=="__main__":sys.exit(asyncio.run(main()))
