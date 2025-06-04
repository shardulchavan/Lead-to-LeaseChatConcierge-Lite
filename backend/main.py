from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession
from backend.database import SessionLocal, engine

from backend.models import Base, Session
from backend.logic import handle_message
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, limit this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables
Base.metadata.create_all(bind=engine)

class ChatMessage(BaseModel):
    user_id: str
    message: str
@app.get("/")
def root():
    return {"message": "Lead-to-Lease Chat Concierge is live! 🚀"}


@app.post("/chat")
def chat(chat: ChatMessage):
    db: DBSession = SessionLocal()
    session = db.query(Session).filter_by(user_id=chat.user_id).first()

    if not session:
        session = Session(user_id=chat.user_id, state="llm_mode", fields=json.dumps({}))
        db.add(session)
        db.commit()
        db.refresh(session)

    reply = handle_message(chat.message, session,db)
    db.commit()
    return {"reply": reply}
