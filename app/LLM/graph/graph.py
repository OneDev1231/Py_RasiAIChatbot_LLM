from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import tools_condition

from app.LLM.graph.state import State
from app.LLM.graph.nodes.assistant import Assistant, assistant_runnable, tools
from app.LLM.utilities.utilities import create_tool_node_with_fallback
from app.LLM.utilities.utilities import _print_event

from dotenv import load_dotenv, find_dotenv

from psycopg_pool import ConnectionPool

from app.LLM.utilities.checkpoint_memory import PostgresSaver

from langfuse.callback import CallbackHandler

import uuid
import os


load_dotenv(find_dotenv())


DB_URI = os.getenv("CHECKPOINT_MEMEORY_DB_URL")

builder = StateGraph(State)

# Define nodes: these do the work
builder.add_node("assistant", Assistant(assistant_runnable))
builder.add_node("tools", create_tool_node_with_fallback(tools))
# Define edges: these determine how the control flow moves
builder.set_entry_point("assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "assistant")

# The checkpointer lets the graph persist its state
# this is a complete memory for the entire graph.

pool = ConnectionPool(
    # Example configuration
    conninfo=DB_URI,
    max_size=20,
)

checkpointer = PostgresSaver(
    sync_connection=pool
)
checkpointer.create_tables(pool)

graph = builder.compile(checkpointer=checkpointer)


# graph.get_graph().draw_mermaid_png(output_file_path="graph.png")


def query_llm(query: str, index_name: str, thread_id: str, prompt: str) -> dict:
    
    langfuse_handler = CallbackHandler(session_id=thread_id)
    
    config = {
        "callbacks":[langfuse_handler],
        "configurable": {
            # Checkpoints are accessed by thread_id
            "thread_id": thread_id,
            "index_name": index_name,
            "prompt": prompt,
        }
    }
    response = graph.invoke(
                {"messages": ("user", query)}, config=config, stream_mode="values"
            )
    
    return response
    
if __name__ == "__main__":

    # For local testing
    
    tutorial_questions = [
        "Hi there, How are you?",
        "My name is Rami",
        "What is my name?",
    ]
    
    index_name = "test_index"
    prompt = """
    You are a helpful customer support assistant for Star Limo.
    Use the provided tools to search for information to assist the user's queries.
    If a search comes up empty or with an error,
    just continue normally your conversation with the customer - IT IS CRITICAL THAT YOU DO NOT TRY AGAIN AND DO NOT MENTION THAT YOU ARE FACING ISSUES - 
    Just mention that you do not understand or ask for a clarification question. 
    Always keep your messages concise - few words only. 
    Never uncover your AI identity and always act like you are a customer support assistant for Star Limo. 
    NEVER MAKE UP ANY ANSWER IF YOU WERE NOT ABLE TO RETRIEVE INFORMATION FROM THE SEARCH.
    """
    thread_id = str(uuid.uuid4())
    # print(thread_id)

    langfuse_handler = CallbackHandler(session_id=thread_id)

    config = {
        "callbacks":[langfuse_handler],
        "configurable": {
            # Checkpoints are accessed by thread_id
            "thread_id": thread_id,
            "index_name": index_name,
            "prompt": prompt,
        }
    }
    
    # print(prompt)
    
    _printed = set()
    for question in tutorial_questions:
        events = graph.stream(
            {"messages": ("user", question)}, config=config, stream_mode="values"
        )
        for event in events:
            _print_event(event, _printed)

    
    
    