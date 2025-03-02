import os
from dotenv import load_dotenv

import getpass
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages.ai import AIMessage
from typing import Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
from typing import Literal

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.managed import IsLastStep, RemainingSteps


# INIT weather tool
@tool
def get_weather(city: Literal["nyc", "sf"]):
    """Use this to get weather information."""
    if city == "münchen":
        return "In München fällt schnee"
    elif city == "augsburg":
        return "In Augsburg ists schön"
    else:
        raise AssertionError("Unknown city")


tools = [get_weather]

# INIT Model
load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

model = init_chat_model("gpt-4o-mini", model_provider="openai")

# Define System prompt
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You talk like a pirate. Answer all questions to the best of your ability in {language}.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# INIT sync connection
DB_URI = "postgresql://postgres:TuIPlLMBguEndWsUdrAdbAKOftjfYpwD@maglev.proxy.rlwy.net:59801/railway"
connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

from psycopg_pool import ConnectionPool
with ConnectionPool(
    # Example configuration
    conninfo=DB_URI,
    max_size=20,
    kwargs=connection_kwargs,
) as pool:
    checkpointer = PostgresSaver(pool)

    # NOTE: you need to call .setup() the first time you're using your checkpointer
    checkpointer.setup()

    graph = create_react_agent(model, tools=tools, checkpointer=checkpointer, state_schema=State)

    # Define the function that calls the model
    def call_model(state: State):
        print ("call model")
        prompt = prompt_template.invoke(state)
        response = model.invoke(prompt)
        return {"messages": response}
    
    graph.add_edge(START, "model")
    graph.add_node("model", call_model)

    # define thread id. individual per conversation
    config = {"configurable": {"thread_id": "abc123", "user_id": "1"}}

    def invoke(graph, message, language):
        print("User: " + message)
        print("AI: ", end="")
        for chunk, metadata in graph.stream(
            {"messages": message, "language": language},
            config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage):  # Filter to just model responses
                print(chunk.content, end="")
        print("")

    invoke(graph, "my name is kai", "japanisch")
    invoke(graph, "what is my name?", "japanisch")



# Interactive loop for user input
#while True:
#    user_input = input("\nEnter your message (or type 'exit' to quit): ")
#    if user_input.lower() in ['exit', 'quit']:
#        print("Exiting conversation.")
#        break
#    print("You:", user_input)
#    output = app.invoke({"messages": [HumanMessage(user_input)], "language": "Deutsch"}, config)
#    print("Model:", output["messages"][-1].pretty_print())