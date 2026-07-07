"""Basic CrewAI run with Respan tracing and gateway routing."""

from respan import workflow

from _shared import build_llm, create_respan, print_result, result_text, run_with_attributes

WORKFLOW_NAME = "crewai_01_basic_crew"


@workflow(name=WORKFLOW_NAME)
def run_basic_crew(context) -> str:
    from crewai import Agent, Crew, Process, Task

    llm = build_llm(context.settings)
    researcher = Agent(
        role="AI Researcher",
        goal="Explain CrewAI and Respan in one practical paragraph",
        backstory="You write concise technical explanations for Python developers.",
        llm=llm,
        verbose=False,
    )
    task = Task(
        description="Explain how CrewAI and Respan work together for tracing.",
        expected_output="One concise paragraph for Python developers.",
        agent=researcher,
    )
    crew = Crew(
        agents=[researcher],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
    )
    return result_text(crew.kickoff())


def main() -> None:
    context = create_respan(
        app_name="crewai-01-basic-crew",
        example_name="01_basic_crew",
        workflow_name=WORKFLOW_NAME,
    )
    output = run_with_attributes(context, lambda: run_basic_crew(context))
    print_result("Crew output", output)
    print_result("Workflow name", WORKFLOW_NAME)
    print_result("Example run id", context.run_id)
    context.respan.flush()


if __name__ == "__main__":
    main()
