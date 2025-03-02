import os
from dotenv import load_dotenv

import getpass
from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages.ai import AIMessage
from typing import Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver
in_memory_store = InMemoryStore()

# INIT Model
load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

model = init_chat_model("gpt-4o-mini", model_provider="openai")

# Define System prompt
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You talk like a pirate. Answer all questions to the best of your ability in {language}.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# Define Persistence
workflow = StateGraph(state_schema=State)

# Define the function that calls the model
def call_model(state: State):
    prompt = prompt_template.invoke(state)
    response = model.invoke(prompt)
    return {"messages": response}

# Define the (single) node in the graph
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory, store=in_memory_store)

# define thread id. individual per conversation
config = {"configurable": {"thread_id": "abc123", "user_id": "1"}}

#output = app.invoke({"messages": [HumanMessage("my nam is kai")], "language": "Deutsch"}, config)
#print("Model:", output["messages"][-1].pretty_print())
#output = app.invoke({"messages": [HumanMessage("what is my name?")]}, config)
#print("Model:", output["messages"][-1].pretty_print())

def invoke(app, message, language):
    print("User: " + message)
    print("AI: ", end="")
    for chunk, metadata in app.stream(
        {"messages": message, "language": language},
        config,
        stream_mode="messages",
    ):
        if isinstance(chunk, AIMessage):  # Filter to just model responses
            print(chunk.content, end="")
    print("")

invoke(app, "my name is kai", "deutsch")
invoke(app, "what is my name?", "deutsch")



# Interactive loop for user input
#while True:
#    user_input = input("\nEnter your message (or type 'exit' to quit): ")
#    if user_input.lower() in ['exit', 'quit']:
#        print("Exiting conversation.")
#        break
#    print("You:", user_input)
#    output = app.invoke({"messages": [HumanMessage(user_input)], "language": "Deutsch"}, config)
#    print("Model:", output["messages"][-1].pretty_print())