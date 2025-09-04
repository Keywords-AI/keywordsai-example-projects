from .experiments import create_experiment, run_experiment, run_experiment_evals
import json
import os


def create_travel_agent_experiment():
    """Create an experiment for the travel agent with tool calls"""
    
    # Define the travel agent prompt columns
    columns = [
        {
            "model": "gpt-4o",
            "name": "Travel Agent v1 - Original",
            "temperature": 0.7,
            "max_completion_tokens": 256,
            "top_p": 1,
            "frequency_penalty": 0,
            "reasoning_effort": "low",
            "presence_penalty": 0,
            "prompt_messages": [
                {
                    "role": "system",
                    "content": [
                        {
                            "text": "You are a helpful travel assistant. Use the available tools to help users plan their trips based on their preferences. \nYou should try to automatically call the tools once strictly necessary information is available without having to ask for confirmation.\nFor example, if the user wants to book a hotel, you should just call the tool once location is given",
                            "type": "text"
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "User ({{name}}) chose category {{category}}{% if is_booking_hotel %}, wants to book hotel{% endif %}{% if is_checking_weather %}, wants to check weather{% endif %}{% if has_image %}, and uploaded this image: {{image}}{% endif %}",
                            "type": "text"
                        }
                    ]
                }
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "search_places",
                        "description": "Search for places based on landscape category",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "category": {
                                    "type": "string",
                                    "description": "The landscape category (mountain, lake, beach, forest)"
                                }
                            },
                            "required": ["category"]
                        }
                    }
                },
                {
                    "type": "function", 
                    "function": {
                        "name": "check_weather",
                        "description": "Check weather for specific locations",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The location to check weather for"
                                }
                            },
                            "required": ["location"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "find_hotels",
                        "description": "Find hotels for specific locations",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The location to find hotels in"
                                },
                                "preferences": {
                                    "type": "string",
                                    "description": "Hotel preferences (optional)",
                                    "default": "mid-range"
                                }
                            },
                            "required": ["location"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "recommend_activities", 
                        "description": "Recommend activities for specific locations",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The location to recommend activities for"
                                }
                            },
                            "required": ["location"]
                        }
                    }
                }
            ],
            "tool_choice": "auto",
            "response_format": {"type": "text"}
        },
        {
            "model": "gpt-4o",
            "name": "Travel Agent v2 - More Aggressive",
            "temperature": 0.5,
            "max_completion_tokens": 256,
            "top_p": 1,
            "frequency_penalty": 0,
            "reasoning_effort": "low", 
            "presence_penalty": 0,
            "prompt_messages": [
                {
                    "role": "system",
                    "content": [
                        {
                            "text": "You are an expert travel assistant. IMMEDIATELY call the appropriate tools based on user preferences without asking for confirmation. Be proactive and call multiple tools when relevant to provide comprehensive travel planning.",
                            "type": "text"
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "User ({{name}}) chose category {{category}}{% if is_booking_hotel %}, wants to book hotel{% endif %}{% if is_checking_weather %}, wants to check weather{% endif %}{% if has_image %}, and uploaded this image: {{image}}{% endif %}",
                            "type": "text"
                        }
                    ]
                }
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "search_places",
                        "description": "Search for places based on landscape category",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "category": {
                                    "type": "string",
                                    "description": "The landscape category (mountain, lake, beach, forest)"
                                }
                            },
                            "required": ["category"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "check_weather",
                        "description": "Check weather for specific locations",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The location to check weather for"
                                }
                            },
                            "required": ["location"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "find_hotels",
                        "description": "Find hotels for specific locations",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The location to find hotels in"
                                },
                                "preferences": {
                                    "type": "string",
                                    "description": "Hotel preferences (optional)",
                                    "default": "mid-range"
                                }
                            },
                            "required": ["location"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "recommend_activities",
                        "description": "Recommend activities for specific locations", 
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The location to recommend activities for"
                                }
                            },
                            "required": ["location"]
                        }
                    }
                }
            ],
            "tool_choice": "auto",
            "response_format": {"type": "text"}
        }
    ]
    
    # Define the test rows based on our testset
    rows = [
        {
            "input": {
                "category": "beach",
                "name": "Mike (Beach Lover)",
                "is_booking_hotel": False,
                "is_checking_weather": False,
                "has_image": True
            }
        },
        {
            "input": {
                "category": "mountain",
                "name": "Sarah (Adventure Seeker)",
                "is_booking_hotel": True,
                "is_checking_weather": True,
                "has_image": True
            }
        }
    ]
    
    # Create the experiment
    experiment = create_experiment(
        name="Travel Agent Tool Call Evaluation",
        description="Comparing different travel agent prompt versions for tool call accuracy",
        columns=columns,
        rows=rows
    )
    
    return experiment


if __name__ == "__main__":
    print("Creating travel agent experiment...")
    experiment = create_travel_agent_experiment()
    
    if experiment:
        print(f"✅ Experiment created successfully!")
        print(f"Name: {experiment['name']}")
        print(f"ID: {experiment['id']}")
        print(f"Columns: {experiment['column_count']}")
        print(f"Rows: {experiment['row_count']}")
        
        # Optionally run the experiment
        print(f"\nExperiment is ready to run with ID: {experiment['id']}")
        
    else:
        print("❌ Failed to create experiment")
