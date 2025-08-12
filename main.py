from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"ok": True, "service": "AIEngineSuite Backend"}

@app.get("/health")
def health():
    return {"status": "ok"}
