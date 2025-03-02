# core/chatbot.py
import os, getpass

from typing import Sequence, Literal
from typing_extensions import Annotated, TypedDict

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages.ai import AIMessage
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.managed import IsLastStep, RemainingSteps

# Define our tools
@tool
def get_weather(city: Literal["münchen", "augsburg"]):
    """Use this to get weather information."""
    print("call weather")
    if city == "münchen":
        return "In München fällt schnee"
    elif city == "augsburg":
        return "In Augsburg ists schön"
    else:
        raise AssertionError("Unknown city")

@tool
async def amultiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    print("call multiply")
    return a * b

tools = [get_weather, amultiply]
tool_node = ToolNode(tools)

# Initialize model

model = ChatOpenAI(model="gpt-4-turbo-preview").bind_tools(tools)

# Define our state schema for the workflow
class State(TypedDict):
    messages: Annotated[Sequence[dict], add_messages]  # Expecting list of dicts {"role":..., "content":...}
    language: str
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps

# Create prompt template: include a system prompt and then the conversation messages.
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You talk like a pirate. Answer all questions to the best of your ability in {language}."),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

def create_chatbot_workflow(checkpointer: PostgresSaver):
    """Set up and compile the chatbot workflow using the given checkpointer."""
    def should_continue(state: MessagesState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    def call_model(state: State):
        prompt = prompt_template.invoke(state)
        response = model.invoke(prompt)
        return {"messages": response}

    workflow = StateGraph(state_schema=State)

    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")
    return workflow.compile(checkpointer=checkpointer)
