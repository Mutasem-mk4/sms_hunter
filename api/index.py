from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scraper import SMSScraper
import uvicorn

app = FastAPI()
scraper = SMSScraper()

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/numbers")
def get_numbers():
    nums = scraper.get_latest_numbers()
    if not nums:
        raise HTTPException(status_code=500, detail="Failed to fetch numbers")
    return nums

@app.get("/api/messages")
def get_messages(url: str):
    msgs = scraper.get_messages(url)
    return msgs

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
