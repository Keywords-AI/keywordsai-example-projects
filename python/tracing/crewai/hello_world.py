"""CrewAI Hello World — Simple agent with Respan tracing via OpenInference."""

from dotenv import load_dotenv

load_dotenv(override=True)

# Initialize Respan FIRST (sets up TracerProvider)
from respan import Respan
from respan_instrumentation_openinference import OpenInferenceInstrumentor
from openinference.instrumentation.crewai import CrewAIInstrumentor

respan = Respan(
    instrumentations=[
        OpenInferenceInstrumentor(
            CrewAIInstrumentor,
            use_event_listener=True,
            create_llm_spans=True,
        ),
    ],
)

# Import CrewAI AFTER Respan init so it uses our TracerProvider
from crewai import Agent, Task, Crew

agent = Agent(
    role="Poet",
    goal="Write a short haiku about recursion in programming",
    backstory="You are a programmer who writes haikus.",
    verbose=False,
)

task = Task(
    description="Write a haiku about recursion in programming.",
    expected_output="A single haiku (3 lines: 5-7-5 syllables).",
    agent=agent,
)

crew = Crew(agents=[agent], tasks=[task], verbose=False)
result = crew.kickoff()
print(result.raw)

respan.flush()
