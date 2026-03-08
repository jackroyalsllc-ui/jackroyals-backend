from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="JackRoyals Backend",
    description="Backend for JackRoyals casino platform",
    version="1.0.0"
)

class SpinRequest(BaseModel):
    user_id: str
    game_id: str
    bet_amount: float

@app.get("/")
def root():
    return {"status": "online", "message": "JackRoyals backend running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/spin")
def spin(req: SpinRequest):
    if req.bet_amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid bet amount")

    return {
        "user_id": req.user_id,
        "game_id": req.game_id,
        "bet_amount": req.bet_amount,
        "result": "win",
        "win_amount": req.bet_amount * 2
    }

@app.post("/callback/balance")
def callback_balance(data: dict):
    return {"status": "received", "data": data}
