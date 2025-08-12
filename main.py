from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os

from drive_client import get_drive_service, get_or_create_subfolder, upload_text

app = FastAPI()

@app.get("/")
def home():
    return {"ok": True, "service": "AIEngineSuite Backend"}

@app.get("/health")
def health():
    return {"status": "ok"}

class PostRequest(BaseModel):
    business_name: str
    industry: str
    goal: str = "grow followers"

class PostResponse(BaseModel):
    posts: List[str]

@app.post("/generate-posts", response_model=PostResponse)
def generate_posts(req: PostRequest):
    name = req.business_name.strip() or "Your Business"
    industry = req.industry.strip() or "business"
    goal = req.goal.strip() or "grow"
    posts = [
        f"🎯 {name} tip for {industry}: small daily actions beat big once-a-month moves. Ready to {goal}?",
        f"🚀 {name} helps {industry} owners save time. Comment 'PLAN' for our 3-step checklist.",
        f"🤝 Consistency > motivation. What {industry} habit are you doing this week?",
        f"📅 Weekly {industry} cheat sheet: 3 tasks Mon–Fri. Want the PDF? Say 'SHEET'.",
        f"💡 {name}: 'What gets measured gets managed.' Track one metric this week."
    ]
    return {"posts": posts}

class SaveRequest(BaseModel):
    subfolder: str
    filename: str
    content: str

@app.post("/save-to-drive")
def save_to_drive(body: SaveRequest):
    parent = os.environ.get("DRIVE_PARENT_FOLDER_ID")
    if not parent:
        raise HTTPException(status_code=500, detail="Missing DRIVE_PARENT_FOLDER_ID")
    service = get_drive_service()
    sub_id = get_or_create_subfolder(service, parent, body.subfolder)
    link = upload_text(service, sub_id, body.filename, body.content)
    return {"ok": True, "webViewLink": link}
