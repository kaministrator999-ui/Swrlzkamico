from fastapi import FastAPI
from swyrlz.backend import PACKED,RAW
app=FastAPI(title="§wyrlz Health",version="2.0.0")
@app.get("/")
@app.get("/api/health")
def health():
    return {"ok":True,"routingReady":True,"r39PackedPresent":PACKED.is_file(),"r39RawPresent":RAW.is_file(),"storage":"Vercel /tmp is ephemeral and instance-local"}
