"""
LangGraph + LangChain Agent Example with KeywordsAI Tracing

This example demonstrates how to use LangGraph with LangChain tools and agents,
all traced automatically by KeywordsAI.

Shows:
- LangGraph's agent workflow
- Custom LangChain tools
- Automatic KeywordsAI tracing

Prerequisites:
1. Install dependencies: poetry install
2. Set up environment variables in .env:
   - KEYWORDSAI_API_KEY=your_api_key (required for tracing)
   - OPENAI_API_KEY=your_openai_key (required for LLM calls)
   - KEYWORDSAI_BASE_URL=https://api.keywordsai.co/api (optional)

Run:
    python langchain_agent.py
"""

from dotenv import load_dotenv

load_dotenv(override=True)

import os
from typing import Annotated, TypedDict, Literal
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from keywordsai_tracing import KeywordsAITelemetry, workflow
from keywordsai_tracing.instruments import Instruments


# Initialize KeywordsAI tracing for LangGraph + LangChain
telemetry = KeywordsAITelemetry(
    app_name="langgraph-agent-example",
    api_key=os.getenv("KEYWORDSAI_API_KEY"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    instruments={Instruments.LANGCHAIN, Instruments.OPENAI},
)

print("✓ LangGraph + LangChain Agent tracing enabled via KeywordsAITelemetry\n")


# Define custom tools for the agent
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # In a real app, this would call a weather API
    return f"The weather in {city} is sunny with a temperature of 72°F."


@tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression. Input should be a valid Python expression."""
    try:
        result = eval(expression)
        return f"The result is: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


@tool
def search_wiki(query: str) -> str:
    """Search for information. Use this for general knowledge questions."""
    # In a real app, this would search Wikipedia or another knowledge base
    return f"Here's what I found about '{query}': [Simulated search result - in production, this would return actual data]"


# Create the tools list
tools = [get_weather, calculate, search_wiki]


# Initialize the LLM (using KeywordsAI proxy for tracing)
llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api/chat/completions"),
    default_headers={
        "Authorization": f"Bearer {os.getenv('KEYWORDSAI_API_KEY')}",
    },
    temperature=0,
)

# Bind tools to the LLM
llm_with_tools = llm.bind_tools(tools)


# Define the agent graph using LangGraph
def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
    """Decide whether to continue with tools or end"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If there are tool calls, continue to tools node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    # Otherwise, end
    return "__end__"


def call_model(state: MessagesState):
    """Call the LLM with the current state"""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# Build the agent graph with LangGraph
graph_builder = StateGraph(MessagesState)

# Add nodes
graph_builder.add_node("agent", call_model)
graph_builder.add_node("tools", ToolNode(tools))

# Add edges
graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "__end__": END,
    }
)
graph_builder.add_edge("tools", "agent")

# Compile the graph
agent_graph = graph_builder.compile()


@workflow(name="weather_query")
def weather_query():
    """Simple weather query workflow using LangGraph"""
    print("=== Weather Query Example ===\n")
    result = agent_graph.invoke({
        "messages": [HumanMessage(content="What's the weather like in San Francisco?")]
    })
    final_message = result["messages"][-1]
    print(f"\nFinal Answer: {final_message.content}\n")
    return result


@workflow(name="calculation_query")
def calculation_query():
    """Math calculation workflow using LangGraph"""
    print("=== Calculation Example ===\n")
    result = agent_graph.invoke({
        "messages": [HumanMessage(content="What is 15 multiplied by 23, plus 100?")]
    })
    final_message = result["messages"][-1]
    print(f"\nFinal Answer: {final_message.content}\n")
    return result


@workflow(name="multi_tool_query")
def multi_tool_query():
    """Query that requires multiple tools using LangGraph"""
    print("=== Multi-Tool Example ===\n")
    result = agent_graph.invoke({
        "messages": [HumanMessage(content="What's the weather in Tokyo, and then calculate 25 * 4?")]
    })
    final_message = result["messages"][-1]
    print(f"\nFinal Answer: {final_message.content}\n")
    return result


@workflow(name="interactive_agent")
def interactive_agent():
    """Interactive agent chat using LangGraph"""
    print("=== Interactive Agent (type 'quit' to exit) ===\n")
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            
            # Add user message to history
            conversation_history.append(HumanMessage(content=user_input))
            
            # Invoke the agent graph
            result = agent_graph.invoke({"messages": conversation_history})
            
            # Update conversation history with all messages from the result
            conversation_history = result["messages"]
            
            # Print the final response
            final_message = result["messages"][-1]
            print(f"\nAgent: {final_message.content}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    # Run examples
    print("Running LangGraph + LangChain Agent examples with KeywordsAI tracing...\n")
    print("=" * 60)
    
    # Example 1: Weather query
    weather_query()
    
    print("=" * 60)
    
    # Example 2: Calculation
    calculation_query()
    
    print("=" * 60)
    
    # Example 3: Multi-tool query
    multi_tool_query()
    
    print("=" * 60)
    
    # Example 4: Interactive mode
    interactive_agent()

