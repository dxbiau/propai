"""Property Insights Australia agents package — the full agentic stack.

14 agents forming a self-governing AI ecosystem:

Core pipeline:
  Profiler → Scout → Analyst → LiveComps → Stacker →
  Closer → Concierge → Mentor → QA

Specialist agents:
  DueDiligenceBot — Section 32 / Contract analysis ($99/report)
  NegotiationShadow — Real-time WhatsApp coaching ($500/mo)
  PhotoEnhancementAgent — Property photo AI (5 presets)
  ChatbotAgent — Trending news & conversational intelligence
"""

from nexusprop.agents.scout import ScoutAgent
from nexusprop.agents.analyst import AnalystAgent
from nexusprop.agents.closer import CloserAgent
from nexusprop.agents.concierge import ConciergeAgent
from nexusprop.agents.live_comps import LiveCompsAgent
from nexusprop.agents.profiler import ProfilerAgent
from nexusprop.agents.stacker import StackerAgent
from nexusprop.agents.mentor import MentorAgent
from nexusprop.agents.qa import QAAgent
from nexusprop.agents.due_diligence import DueDiligenceBot
from nexusprop.agents.negotiation_shadow import NegotiationShadow
from nexusprop.agents.photo_enhancer import PhotoEnhancementAgent
from nexusprop.agents.chatbot import ChatbotAgent
from nexusprop.agents.state_market import StateMarketAgent

__all__ = [
    # Core pipeline agents
    "ProfilerAgent",
    "ScoutAgent",
    "AnalystAgent",
    "StackerAgent",
    "CloserAgent",
    "ConciergeAgent",
    "MentorAgent",
    "QAAgent",
    # Specialist agents
    "LiveCompsAgent",
    "DueDiligenceBot",
    "NegotiationShadow",
    "PhotoEnhancementAgent",
    "ChatbotAgent",
    "StateMarketAgent",
]
