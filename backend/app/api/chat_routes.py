"""
Chat Routes — Conversational AI Chatbot API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/api/chat", tags=["Chatbot"])

# In-memory chatbot sessions
chatbot_sessions = {}


class ChatMessage(BaseModel):
    message: str = Field(..., description="User message")
    session_id: str = Field(default="default", description="Session identifier")


class ChatReset(BaseModel):
    session_id: str = Field(default="default")


def _get_chatbot(session_id: str):
    """Get or create a chatbot instance for a session."""
    from app.models.chatbot_engine import ChatbotEngine
    from app.config import Config

    if session_id not in chatbot_sessions:
        bot = ChatbotEngine(str(Config.CHAT_INTENTS_JSON))
        # Try to load trained model
        if Config.CHATBOT_MODEL_PATH.exists():
            bot.load_model(str(Config.CHATBOT_MODEL_PATH))
        chatbot_sessions[session_id] = bot

    return chatbot_sessions[session_id]


@router.post("/message")
async def send_message(data: ChatMessage):
    """Send a message to the chatbot and get a response."""
    try:
        bot = _get_chatbot(data.session_id)
        result = bot.process_message(data.message)

        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_chat(data: ChatReset):
    """Reset the chatbot conversation."""
    try:
        if data.session_id in chatbot_sessions:
            chatbot_sessions[data.session_id].reset_conversation()
        return {"status": "success", "message": "Conversation reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_history(session_id: str = "default"):
    """Get conversation history."""
    try:
        bot = _get_chatbot(session_id)
        return {
            "status": "success",
            "data": {
                "history": bot.get_history(),
                "context": bot.context,
                "message_count": len(bot.conversation_history)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
