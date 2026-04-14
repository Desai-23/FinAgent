import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import TypedDict
from langgraph.graph import StateGraph, END
from agent.agents import research_agent, sentiment_agent, report_agent


class AnalysisState(TypedDict):
    ticker: str
    research: dict
    sentiment: dict
    final_report: str
    current_step: str
    error: str


def run_research(state: AnalysisState) -> AnalysisState:
    try:
        result = research_agent(state["ticker"])
        return {**state, "research": result, "current_step": "sentiment"}
    except Exception as e:
        return {**state, "error": f"Research agent failed: {str(e)}", "current_step": "error"}


def run_sentiment(state: AnalysisState) -> AnalysisState:
    try:
        result = sentiment_agent(state["ticker"])
        return {**state, "sentiment": result, "current_step": "report"}
    except Exception as e:
        return {**state, "error": f"Sentiment agent failed: {str(e)}", "current_step": "error"}


def run_report(state: AnalysisState) -> AnalysisState:
    try:
        result = report_agent(state["ticker"], state["research"], state["sentiment"])
        return {**state, "final_report": result, "current_step": "done"}
    except Exception as e:
        return {**state, "error": f"Report agent failed: {str(e)}", "current_step": "error"}


def route_after_research(state: AnalysisState) -> str:
    return "error" if state.get("error") else "sentiment"


def route_after_sentiment(state: AnalysisState) -> str:
    return "error" if state.get("error") else "report"


def build_analysis_graph():
    graph = StateGraph(AnalysisState)
    graph.add_node("research", run_research)
    graph.add_node("sentiment", run_sentiment)
    graph.add_node("report", run_report)
    graph.set_entry_point("research")
    graph.add_conditional_edges("research", route_after_research,
        {"sentiment": "sentiment", "error": END})
    graph.add_conditional_edges("sentiment", route_after_sentiment,
        {"report": "report", "error": END})
    graph.add_edge("report", END)
    return graph.compile()


analysis_graph = build_analysis_graph()


def run_analysis(ticker: str) -> dict:
    """Run the full multi-agent LangGraph pipeline."""
    initial_state: AnalysisState = {
        "ticker": ticker.upper().strip(),
        "research": {},
        "sentiment": {},
        "final_report": "",
        "current_step": "research",
        "error": "",
    }
    return analysis_graph.invoke(initial_state)