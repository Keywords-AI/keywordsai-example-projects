from openai import OpenAI
import os
from dotenv import load_dotenv

loaded = load_dotenv(".env", override=True)
# print("Loaded env?", loaded)
from keywordsai_tracing.decorators import workflow, task
from keywordsai_tracing.main import KeywordsAITelemetry
import time
from anthropic import Anthropic

client = OpenAI()
anthropic = Anthropic()

k_tl = KeywordsAITelemetry(
)

@task(name="store_joke")
def store_joke(joke: str):
    """
    Simulate the action of storing a joke in a vector database.
    """
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=joke,
    )

    return embedding.data[0].embedding

@task(name="joke_creation")
def create_joke():
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Tell me a joke about opentelemetry"}],
        temperature=0.5,
        max_tokens=100,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        stop=["\n"],
        logprobs=True,
    )
    joke = completion.choices[0].message.content
    store_joke(joke)

    return joke

@task(name="just_wait")
def just_wait():
    time.sleep(10)

@task(name="signature_generation")
def generate_signature(joke: str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "add a signature to the joke:\n\n" + joke}
        ],
    )

    return completion.choices[0].message.content


@task(name="pirate_joke_translation")
def translate_joke_to_pirate(joke: str):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": "translate the joke to pirate language:\n\n" + joke,
            }
        ],
    )

    return completion.choices[0].message.content


@workflow(name="pirate_joke_generator")
def joke_workflow():
    eng_joke = create_joke()
    pirate_joke = translate_joke_to_pirate(eng_joke)
    signature = generate_signature(pirate_joke)
    return pirate_joke + signature

@task(name="audience_laughs")
def audience_laughs(joke: str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "This joke:\n\n" + joke + " is funny, say hahahahaha",
            }
        ],
        max_tokens=10,
    )

    return completion.choices[0].message.content

@task(name="audience_claps")
def audience_claps():
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "Clap once",
            }
        ],
        max_tokens=5,
    )

    return completion.choices[0].message.content

@task(name="audience_applaud")
def audience_applaud(joke:str):
    clap = audience_claps()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "Applaud to the joke, clap clap! " + clap,
            }
        ],
        max_tokens=10,
    )

    return completion.choices[0].message.content

@workflow(name="audience_reaction")
def audience_reaction(joke: StopIteration):
    laughter = audience_laughs(joke=joke)
    applauds = audience_applaud(joke=joke)

    return laughter + applauds

@task(name="logging_joke")
def logging_joke(joke: str, reactions: str):
    """
    Simulates logging the whole process into a database via logging service.
    """
    print(joke + "\n\n" + reactions)
    time.sleep(1)

@task(name="ask_for_comments")
def ask_for_comments(joke: str):
    completion = anthropic.messages.create(
        model="claude-3-5-sonnet-20240620",
        messages=[{"role": "user", "content": f"What do you think about this joke: {joke}"}],
        max_tokens=100,
    )

    return completion.content[0].text

@task(name="read_joke_comments")
def read_joke_comments(comments: str):
    return f"Here is the comment from the audience: {comments}"

@workflow(name="audience_interaction")
def audience_interaction(joke: str):
    comments = ask_for_comments(joke=joke)
    read_joke_comments(comments=comments)



@workflow(name="pirate_joke_plus_audience_reactions")
def pirate_joke_plus_audience(): 

    joke = joke_workflow() # This show case the basic workflow usage and compatibility with the OpenAI SDK
    reactions = audience_reaction(joke=joke) # This show case the the display of multi-workflow under the same trace
    # audience_interaction(joke=joke) # This show case the compatibility with the anthropic SDK
    logging_joke(joke=joke, reactions=reactions) # THis show case the tracing of a function with arbitrary inputs/outputs
    return "python"

pirate_joke_plus_audience()

