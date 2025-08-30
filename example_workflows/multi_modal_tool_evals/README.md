# KeywordsAI Multi-Modal Tool Evaluation Demo

## Demo Use Case: Smart Travel Assistant Agent (5-min demo)

### Agent Overview
An AI travel assistant that helps users plan trips by analyzing images and providing recommendations.

**Agent Tools (3 choices):**
1. **Image Analyzer** - Analyzes travel photos to identify locations, landmarks, activities
2. **Weather Checker** - Gets current/forecast weather for destinations
3. **Hotel Finder** - Searches and recommends hotels based on location and preferences

### Demo Scenario
User uploads a photo of a scenic mountain location and asks:
*"I took this photo during my last trip. I want to visit a similar place next month. Can you help me plan?"*

**Expected Agent Flow:**
1. Use Image Analyzer to identify the location/landscape type
2. Use Weather Checker to get forecast for similar destinations
3. Use Hotel Finder to suggest accommodations
4. Provide concise travel recommendations

### KeywordsAI Workflow

#### Phase 1: Setup & Logging (1 min)
- **Proxy Setup**: Configure agent with prompt management
- **Logging**: Enable custom prompt ID tracking with variables:
  - `{{user_image}}` - uploaded travel photo
  - `{{user_query}}` - travel planning request
  - `{{destination_type}}` - extracted from image analysis

#### Phase 2: Agent Execution & Tracing (2 min)
- **Tracing**: Capture complete agent execution flow
  - Tool selection decisions
  - Multi-modal input processing (image + text)
  - Tool outputs and reasoning
  - Final response generation

#### Phase 3: Evaluation Setup (1.5 min)
- **Dataset Creation**: Import logged agent interactions
- **Evaluator Configuration**: Setup 2 LLM-as-Judge evaluators

**Evaluator 1: Tool Selection Accuracy**
```
Prompt: "Evaluate if the agent selected appropriate tools for the given input.

Input: {{llm_input}}
Agent Response: {{llm_output}}

Criteria:
- Did the agent correctly identify the need for image analysis?
- Were the subsequent tool choices logical and relevant?
- Was the tool sequence efficient?

Score: 1-5 (5 = perfect tool selection)
Reasoning: [Explain your scoring]"
```

**Evaluator 2: Response Conciseness**
```
Prompt: "Evaluate the conciseness and clarity of the agent's response.

Input: {{llm_input}}
Agent Response: {{llm_output}}

Criteria:
- Is the response concise while being informative?
- Does it avoid unnecessary verbosity?
- Are the recommendations clear and actionable?

Score: 1-5 (5 = perfectly concise and clear)
Reasoning: [Explain your scoring]"
```

#### Phase 4: Running Evaluations (0.5 min)
- **Experiment Execution**: Run evaluators on dataset
- **Results Analysis**: View scores and reasoning for each evaluation

### Demo Test Cases (3 scenarios)
1. **Mountain landscape** → Should trigger: Image Analyzer → Weather → Hotels
2. **Beach photo** → Should trigger: Image Analyzer → Weather → Hotels  
3. **City landmark** → Should trigger: Image Analyzer → Hotels (weather less critical)

### Expected Demo Outcomes
- Show how multi-modal inputs are processed and traced
- Demonstrate tool selection evaluation across different scenarios
- Highlight response quality assessment
- Showcase KeywordsAI's ability to evaluate complex agent behaviors

### Key KeywordsAI Features Demonstrated
- Multi-modal input handling in proxy
- Comprehensive tracing of tool-using agents
- Flexible prompt management with variables
- LLM-as-Judge evaluation framework
- Dataset creation from logged interactions
- Experiment-based evaluation workflows

### Demo Script Timeline
- 0:00-1:00 - Setup proxy, show prompt variables
- 1:00-3:00 - Execute agent with 3 different image scenarios
- 3:00-4:00 - Create dataset, configure evaluators
- 4:00-5:00 - Run evaluations, show results and insights

### Success Metrics
- Tool selection accuracy > 4.0/5.0 across test cases
- Response conciseness score > 4.0/5.0
- Complete trace capture for all agent interactions
- Clear evaluation insights for agent improvement