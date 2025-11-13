from google import genai
from google.genai.types import Tool, GenerateContentConfig, UrlContext

API_KEY = "IqgCLJqD.hsYv5N1n24tb2JpSjZAQZoIqbrRG9A67"


client = genai.Client(
    api_key=API_KEY,
    http_options={
        "base_url": "https://api.keywordsai.co/api/google/gemini",
    }
)
model_id = "gemini-2.5-flash"



response = client.models.generate_content(
    model=model_id,
   contents=[{"role": "user", "parts": [{"text": "What color is the sky?"}]}],

)

for each in response.candidates[0].content.parts:
    print(each.text)

# For verification, you can inspect the metadata to see which URLs the model retrieved
print(response.candidates[0].url_context_metadata)
