from fastapi import FastAPI
app=FastAPI(title="§wyrlz Clean Vercel Server",version="2.0.1")
@app.get("/")
def root():
    return {"ok":True,"service":"§wyrlz Clean Vercel Server","version":"2.0.1","health":"/api/health","admin":"/api/admin","lalm":"/api/lalm"}
