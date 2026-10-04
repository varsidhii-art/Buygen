from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json,re

app=FastAPI(title="BUYGEN AI Commerce Agent")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])

with open("data/products.json","r",encoding="utf-8-sig") as f:
    PRODUCTS=json.load(f)

class Goal(BaseModel):
    goal:str

def extract(text):
    t=text.lower()
    r={"budget":None,"battery_hours":None,"anc":False}
    m=re.search(r"(?:under|below|less than|within)\s*(?:₹|rs\.?|inr\s*)?([\d,]+)",t)
    if m:r["budget"]=int(m.group(1).replace(",",""))
    m=re.search(r"(\d+)\s*(?:\+)?\s*(?:hours?|hrs?)",t)
    if m:r["battery_hours"]=int(m.group(1))
    r["anc"]="anc" in t or "noise cancellation" in t or "noise cancelling" in t
    return r

def analyze(p,r):
    score=0
    reasons=[]
    if r["budget"] is not None:
        ok=p["price"]<=r["budget"]
        score+=30 if ok else 0
        reasons.append("Budget: "+("✓" if ok else "✗"))
    if r["battery_hours"] is not None:
        ok=p.get("battery_hours",0)>=r["battery_hours"]
        score+=25 if ok else 0
        reasons.append("Battery: "+("✓" if ok else "✗"))
    if r["anc"]:
        ok=p.get("anc",False)
        score+=25 if ok else 0
        reasons.append("ANC: "+("✓" if ok else "✗"))
    score+=round(p.get("rating",0)*4)
    return min(score,100),reasons

@app.get("/")
def root():
    return {"system":"BUYGEN","status":"online","mode":"human-controlled autonomy"}

@app.post("/agent/run")
def agent(g:Goal):
    r=extract(g.goal)
    candidates=[]
    for p in PRODUCTS:
        if r["budget"] is not None and p["price"]>r["budget"]: continue
        if r["battery_hours"] is not None and p.get("battery_hours",0)<r["battery_hours"]: continue
        if r["anc"] and not p.get("anc",False): continue
        s,reasons=analyze(p,r)
        candidates.append({**p,"match_percentage":s,"reasons":reasons})
    candidates.sort(key=lambda x:(-x["match_percentage"],x["price"]))
    return {
        "goal":g.goal,
        "requirements":r,
        "recommendation":candidates[0] if candidates else None,
        "candidates":candidates[:6],
        "approval_required":True,
        "message":"BUYGEN completed the analysis. No purchase has been made."
    }
