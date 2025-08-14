from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def health():
    return {"ok": True, "mode": os.getenv("RUN_MODE","paper")}
