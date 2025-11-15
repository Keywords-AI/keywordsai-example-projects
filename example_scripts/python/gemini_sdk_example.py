from dotenv import load_dotenv
import os

# Load environment variables from parent directory
load_dotenv(override=True)

from google import genai
from google.genai.types import Tool, GenerateContentConfig, UrlContext
from google.genai import types

API_KEY = os.getenv("KEYWORDSAI_API_KEY")
if not API_KEY:
    raise ValueError("KEYWORDSAI_API_KEY not found in environment variables. Please set it in .env file.")

client = genai.Client(
    api_key=API_KEY,
    http_options={
        "base_url": "https://api.keywordsai.co/api/google/gemini",
    }
)
model_id = "gemini-2.5-flash"

# Example: Configure tools for grounding
grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)

# Example: Comprehensive GenerateContentConfig showcasing various parameters
config = types.GenerateContentConfig(
    # System instruction to guide the model's behavior
    system_instruction="You are a helpful assistant that provides accurate, concise information about sports events.",
    
    # Sampling parameters
    temperature=0.7,  # Controls randomness (0.0-1.0). Lower = more focused, Higher = more creative
    top_p=0.95,  # Nucleus sampling. Tokens with cumulative probability up to this value are considered
    top_k=40,  # Top-k sampling. Considers this many top tokens at each step
    
    # Output controls
    max_output_tokens=1024,  # Maximum number of tokens in the response
    stop_sequences=["\n\n\n"],  # Sequences that will stop generation
    
    # Tools and function calling
    tools=[grounding_tool],  # Enable Google Search grounding
    
    # Thinking configuration (for models that support it)
    thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking mode
    
    # Response format options
    # response_mime_type="application/json",  # Uncomment for JSON output
    # response_schema=types.Schema(  # Uncomment to enforce structured output
    #     type=types.Type.OBJECT,
    #     properties={
    #         "winner": types.Schema(type=types.Type.STRING),
    #         "year": types.Schema(type=types.Type.INTEGER)
    #     }
    # ),
    
    # Safety settings
    safety_settings=[
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        )
    ],
    
    # Diversity controls
    presence_penalty=0.0,  # Penalize tokens based on presence in text (-2.0 to 2.0)
    frequency_penalty=0.0,  # Penalize tokens based on frequency in text (-2.0 to 2.0)
    
    # Reproducibility
    # seed=42,  # Uncomment to make responses more deterministic
    
    # Logprobs (for token analysis)
    # response_logprobs=True,  # Uncomment to get log probabilities
    # logprobs=5,  # Number of top candidate tokens to return logprobs for
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Who won the euro 2024?",
    config=config,
)

print(response.text)
