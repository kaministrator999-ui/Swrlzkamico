from fastapi import FastAPI
app=FastAPI(title="§wyrlz Clean Vercel Server",version="2.0.0")
@app.get("/")
def root():
    return {"ok":True,"service":"§wyrlz Clean Vercel Server","health":"/api/health","admin":"/api/admin","lalm":"/api/lalm"}
