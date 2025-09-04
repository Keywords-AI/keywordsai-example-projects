from .experiments import create_experiment, run_experiment, run_experiment_evals
from .prompts import list_prompts, get_prompt
import json
import os


def create_travel_agent_experiment_with_prompts():
    """Create an experiment using actual prompts from the prompts API"""
    
    # First, let's list prompts to find our travel agent prompt
    prompts = list_prompts()
    
    travel_prompt = None
    if prompts and prompts.get('results'):
        for prompt in prompts['results']:
            if 'travel' in prompt['name'].lower() or 'agent' in prompt['name'].lower():
                travel_prompt = prompt
                break
    
    if not travel_prompt:
        print("❌ No travel agent prompt found. Creating a new one...")
        from .prompts import create_prompt, create_prompt_version
        
        # Create a new travel agent prompt
        prompt = create_prompt(
            name="Travel Agent Experiment Prompt",
            description="Travel assistant with multi-modal inputs and tool calls for experiments"
        )
        
        if prompt:
            # Create version 1 - Original
            messages_v1 = [
                {
                    "role": "system",
                    "content": "You are a helpful travel assistant. Use the available tools to help users plan their trips based on their preferences. \nYou should try to automatically call the tools once strictly necessary information is available without having to ask for confirmation.\nFor example, if the user wants to book a hotel, you should just call the tool once location is given"
                },
                {
                    "role": "user",
                    "content": "User ({{name}}) chose category {{category}}{% if is_booking_hotel %}, wants to book hotel{% endif %}{% if is_checking_weather %}, wants to check weather{% endif %}{% if has_image %}, and uploaded this image: {{image}}{% endif %}"
                }
            ]
            
            version1 = create_prompt_version(prompt["prompt_id"], messages_v1)
            
            # Create version 2 - More Aggressive
            messages_v2 = [
                {
                    "role": "system", 
                    "content": "You are an expert travel assistant. IMMEDIATELY call the appropriate tools based on user preferences without asking for confirmation. Be proactive and call multiple tools when relevant to provide comprehensive travel planning."
                },
                {
                    "role": "user",
                    "content": "User ({{name}}) chose category {{category}}{% if is_booking_hotel %}, wants to book hotel{% endif %}{% if is_checking_weather %}, wants to check weather{% endif %}{% if has_image %}, and uploaded this image: {{image}}{% endif %}"
                }
            ]
            
            version2 = create_prompt_version(prompt["prompt_id"], messages_v2)
            
            travel_prompt = prompt
            print(f"✅ Created new travel agent prompt: {prompt['prompt_id']}")
        else:
            print("❌ Failed to create prompt")
            return None
    
    # Get the full prompt details
    prompt_details = get_prompt(travel_prompt['prompt_id'])
    if not prompt_details:
        print("❌ Failed to fetch prompt details")
        return None
    
    print(f"📋 Using prompt: {prompt_details['name']} (ID: {prompt_details['prompt_id']})")
    
    # Create experiment columns using the prompt ID instead of hardcoded messages
    columns = [
        {
            "id": prompt_details['prompt_id'],
            "model": "gpt-4o",
            "name": "Travel Agent v1 - Original", 
            "temperature": 0.7,
            "max_completion_tokens": 256,
            "top_p": 1,
            "frequency_penalty": 0,
            "reasoning_effort": "low",
            "presence_penalty": 0,
            # Use prompt_id instead of prompt_messages
            "prompt_id": prompt_details['prompt_id'],
            "prompt_version": 1,  # Use version 1
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
            "id": prompt_details['prompt_id'],
            "model": "gpt-4o",
            "name": "Travel Agent v2 - More Aggressive",
            "temperature": 0.5,
            "max_completion_tokens": 256,
            "top_p": 1,
            "frequency_penalty": 0,
            "reasoning_effort": "low", 
            "presence_penalty": 0,
            # Use prompt_id instead of prompt_messages
            "prompt_id": prompt_details['prompt_id'],
            "prompt_version": 2,  # Use version 2
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
        name="Travel Agent Tool Call Evaluation (Prompt-based)",
        description="Comparing different travel agent prompt versions using actual prompts from API",
        columns=columns,
        rows=rows
    )
    
    return experiment


if __name__ == "__main__":
    print("Creating travel agent experiment with prompts API...")
    experiment = create_travel_agent_experiment_with_prompts()
    
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
