"""
Chatbot API routes — trending news & conversational intelligence.

Endpoints:
  POST /api/v1/chat          — Send a chat message, get AI response + trending news
  GET  /api/v1/chat/trending  — Get trending property news articles
  GET  /api/v1/chat/summary   — Get AI-generated market intelligence brief
  DELETE /api/v1/chat/{session_id} — Clear a conversation session
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from nexusprop.agents.chatbot import ChatbotAgent

router = APIRouter()

# Singleton chatbot agent (shares news cache across requests)
_chatbot = ChatbotAgent()


# ── Request / Response Models ────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User's chat message")
    session_id: str = Field(default="default", max_length=100, description="Conversation session ID")
    include_news: bool = Field(default=True, description="Whether to include trending news in context")


class ChatResponse(BaseModel):
    response: str
    trending_news: list[dict] = Field(default_factory=list)
    session_id: str
    conversation_length: int = 0
    tokens_used: int = 0


class NewsArticleResponse(BaseModel):
    title: str
    link: str
    source: str
    published: Optional[str] = None
    summary: str = ""
    category: str = "market"
    au_relevance: float = 0.0


class NewsSummaryResponse(BaseModel):
    summary: str
    articles: list[dict] = Field(default_factory=list)
    sentiment: str = "neutral"
    tokens_used: int = 0


# ── Endpoints ────────────────────────────────────────────────────────────

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the Australian Property Associates chatbot.

    The chatbot combines trending real estate news with Australian
    market intelligence to provide contextual, data-driven responses.

    Supports conversation history — use the same `session_id` for
    multi-turn conversations.
    """
    result = await _chatbot.safe_execute(
        user_message=request.message,
        session_id=request.session_id,
        include_news=request.include_news,
    )

    if not result.success:
        return ChatResponse(
            response="I'm having a bit of trouble right now. Try again in a moment, or use the Scout button to search property markets directly!",
            session_id=request.session_id,
            tokens_used=0,
        )

    data = result.data or {}
    return ChatResponse(
        response=data.get("response", ""),
        trending_news=data.get("trending_news", []),
        session_id=data.get("session_id", request.session_id),
        conversation_length=data.get("conversation_length", 0),
        tokens_used=result.tokens_used,
    )


@router.get("/trending", response_model=list[NewsArticleResponse])
async def get_trending_news(
    limit: int = Query(default=10, ge=1, le=50, description="Number of articles to return")
):
    """
    Get trending Australian property news articles, ranked by relevance.

    Articles are scraped from: Domain, realestate.com.au, CoreLogic, AFR, SQM Research.
    Cached and refreshed every 30 minutes.
    """
    articles = await _chatbot.get_trending_news(limit=limit)
    return articles


@router.get("/summary", response_model=NewsSummaryResponse)
async def get_news_summary():
    """
    Get an AI-generated Australian market intelligence briefing based on current trending news.

    Summarises headlines and explains implications for Australian property investors.
    """
    result = await _chatbot.get_news_summary()
    data = result.data or {}
    return NewsSummaryResponse(
        summary=data.get("summary", "Summary unavailable."),
        articles=data.get("articles", []),
        sentiment=data.get("sentiment", "neutral"),
        tokens_used=result.tokens_used,
    )


@router.delete("/{session_id}")
async def clear_session(session_id: str):
    """Clear conversation history for a specific session."""
    _chatbot.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}
