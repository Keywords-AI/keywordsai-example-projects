```System
You are a helpful travel assistant. Use the available tools to help users plan their trips based on their preferences. 
You should try to automatically call the tools once strictly necessary information is available without having to ask for confirmation.
For example, if the user wants to book a hotel, you should just call the tool once location is given.

YOU SHOULD BE CALLING ALL TOOLS ONCE LOCATION IS PROVIDED
```

```User
User ({{name}}) chose category {{category}}{% if is_booking_hotel %}, wants to book hotel{% endif %}{% if is_checking_weather %}, wants to check weather{% endif %}{% if has_image %}, and uploaded this image: {{image}}{% endif %}
```

tools:

```
{
  "name": "search_places",
  "parameters": {
    "type": "object",
    "required": [
      "category"
    ],
    "properties": {
      "category": {
        "type": "string",
        "enum": [
          "mountain",
          "lake",
          "beach",
          "forest"
        ],
        "description": "Landscape category to search for"
      }
    }
  },
  "description": "Search for travel destinations based on landscape category"
}
```

```
{
  "name": "check_weather",
  "parameters": {
    "type": "object",
    "required": [
      "location"
    ],
    "properties": {
      "location": {
        "type": "string",
        "description": "Specific location name (e.g., 'Lake Tahoe', 'Santorini')"
      }
    }
  },
  "description": "Get weather information for specific travel destinations"
}
```

```
{
  "name": "find_hotels",
  "description": "Find hotels for specific locations",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "description": "The location where you want to find hotels (e.g., 'Lake Tahoe', 'Banff', 'Santorini')",
        "type": "string"
      },
      "preferences": {
        "description": "Hotel preferences or price range",
        "type": "string"
      }
    },
    "required": [
      "location"
    ],
    "additionalProperties": false
  }
}
```

```
{
  "name": "recommend_activities",
  "parameters": {
    "type": "object",
    "required": [
      "location"
    ],
    "properties": {
      "location": {
        "type": "string",
        "description": "Specific location name (e.g., 'Lake Tahoe', 'Santorini')"
      }
    }
  },
  "description": "Recommend activities for specific locations"
}
```