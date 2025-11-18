"""
LangGraph Example with KeywordsAI Tracing

This example demonstrates LangGraph tracing with KeywordsAI using the
keywordsai_tracing package, which handles all OpenTelemetry setup automatically.

Reference: https://docs.langchain.com/langsmith/trace-with-langgraph

Comparison with LangSmith approach:
┌─────────────────────┬──────────────────────────────┬────────────────────────────────┐
│ Aspect              │ LangSmith (from docs)        │ This Example (KeywordsAI)      │
├─────────────────────┼──────────────────────────────┼────────────────────────────────┤
│ Tracing Setup       │ LANGSMITH_TRACING=true       │ KeywordsAITelemetry()          │
│ API Key             │ LANGSMITH_API_KEY=...        │ KEYWORDSAI_API_KEY=...         │
│ Backend             │ LangSmith                    │ KeywordsAI                     │
│ LLM Usage           │ ChatOpenAI(model="gpt-4o")   │ ChatOpenAI via KeywordsAI      │
│ Instrumentation     │ Automatic                    │ Automatic via Instruments      │
│ Graph Definition    │ StateGraph (same)            │ StateGraph (same)              │
└─────────────────────┴──────────────────────────────┴────────────────────────────────┘

How it works:
- KeywordsAITelemetry automatically sets up OpenTelemetry instrumentation
- Instruments LangChain, OpenAI, and other frameworks automatically
- All LangGraph operations are traced without any decorators
- No custom code needed - just initialize and go!

Prerequisites:
1. Install dependencies: poetry install
2. Set up environment variables in .env:
   - KEYWORDSAI_API_KEY=your_api_key (required for tracing)
   - OPENAI_API_KEY=your_openai_key (required for LLM calls)
   - KEYWORDSAI_BASE_URL=https://api.keywordsai.co/api (optional, defaults to this)

Run:
    python langraph.py
"""

from dotenv import load_dotenv

load_dotenv(override=True)

import os
from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from keywordsai_tracing import KeywordsAITelemetry, workflow
from keywordsai_tracing.instruments import Instruments


# Initialize KeywordsAI tracing - this handles all OpenTelemetry setup
telemetry = KeywordsAITelemetry(
    app_name="langgraph-example",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    instruments={Instruments.LANGCHAIN, Instruments.OPENAI},  # Auto-trace LangChain & OpenAI
)

print("✓ LangGraph tracing enabled via KeywordsAITelemetry")


# Define the state type
class State(TypedDict):
    messages: Annotated[list, add_messages]


# Initialize the LLM - automatically traced by OpenTelemetry instrumentation
# Note: With LangSmith, you'd set LANGSMITH_TRACING=true
# Here OpenTelemetry automatically captures all calls
llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api/chat/completions"),
    default_headers={
        "Authorization": f"Bearer {os.getenv('KEYWORDSAI_API_KEY')}",
    }
)


# Define the chatbot node function
def chatbot_respond(state: State):
    """Node function that processes the message and returns the LLM response"""
    return {"messages": [llm.invoke(state["messages"])]}


# Build the graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot_respond)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    """Stream graph execution updates - automatically traced by OpenTelemetry"""
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


@workflow(name="chatbot_qa")
def chatbot_qa():
    """Main chatbot QA workflow - traced by KeywordsAI"""
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            stream_graph_updates(user_input)
        except:
            # fallback if input() is not available
            user_input = "What do you know about LangGraph?"
            print("User: " + user_input)
            stream_graph_updates(user_input)
            break


@workflow(name="simple_haiku_test")
def simple_haiku_test():
    """Simple test workflow that asks for a haiku - traced by KeywordsAI"""
    # Create a custom LLM for this test
    haiku_llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api/chat/completions"),
        default_headers={
            "Authorization": f"Bearer {os.getenv('KEYWORDSAI_API_KEY')}",
        }
    )
    
    # Define a simple state for this test
    def haiku_node(state: State):
        return {"messages": [haiku_llm.invoke(state["messages"])]}
    
    # Build a simple graph
    test_graph = StateGraph(State)
    test_graph.add_node("haiku", haiku_node)
    test_graph.add_edge(START, "haiku")
    test_graph.add_edge("haiku", END)
    compiled_graph = test_graph.compile()
    
    # Run the graph - OpenTelemetry automatically captures everything
    result = compiled_graph.invoke({
        "messages": [
            {"role": "system", "content": "You only respond in haikus."},
            {"role": "user", "content": "Tell me about recursion in programming."}
        ]
    })
    
    print("Haiku Test Result:")
    print(result["messages"][-1].content)
    return result


if __name__ == "__main__":
    # Run the simple haiku test first
    print("Running haiku test...\n")
    simple_haiku_test()
    
    print("\n" + "="*50 + "\n")
    print("Starting interactive chatbot...\n")
    
    # Then run the interactive chatbot
    chatbot_qa()