"""
LangGraph Example with KeywordsAI Tracing

This example demonstrates how to use LangGraph with KeywordsAI for tracing.

Prerequisites:
1. Install dependencies: poetry install
2. Set up environment variables in .env:
   - KEYWORDSAI_API_KEY=your_api_key
   - OPENAI_API_KEY=your_openai_key
   - KEYWORDSAI_BASE_URL=https://api.keywordsai.co/api (optional)

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


# Initialize KeywordsAI tracing
telemetry = KeywordsAITelemetry(
    app_name="langgraph-example",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    base_url=os.getenv("KEYWORDSAI_OAIA_TRACING_ENDPOINT", "https://api.keywordsai.co/api/openai/v1/traces/ingest"),
    enabled=True,
)


# Define the state type
class State(TypedDict):
    messages: Annotated[list, add_messages]


# Initialize the LLM with KeywordsAI endpoint
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
    """Stream graph execution updates"""
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


@workflow(name="chatbot_qa")
def chatbot_qa():
    """Main chatbot QA workflow with KeywordsAI tracing"""
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
    """Simple test workflow that asks for a haiku"""
    # Create a custom LLM for this test with specific instructions
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
    
    # Run the graph
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