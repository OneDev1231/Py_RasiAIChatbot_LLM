from langchain_openai import ChatOpenAI
from langchain_core.runnables import ensure_config
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.runnables import Runnable, RunnableConfig

from app.LLM.graph.state import State

from datetime import datetime

from app.LLM.graph.tools.retrieve_tool import lookup_info

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            configuration = config.get("configurable", {})
            index_name = configuration.get("index_name", None)
            prompt = configuration.get("prompt", None)
            
            # print(f"index name: {index_name}")
            
            state = {**state, "index_name": index_name, "prompt" : prompt}
            
            result = self.runnable.invoke(state)
            
            # If the LLM happens to return an empty response, we will re-prompt it for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
            
        return {"messages": result}



llm = ChatOpenAI(model="gpt-4o", temperature=0)

# config = ensure_config()
# configuration = config.get("configurable", {})
# print(configuration)


# prompt = configuration.get("prompt", None)

# print(prompt)

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "{prompt} \nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

tools = [
    lookup_info,
]
assistant_runnable = primary_assistant_prompt | llm.bind_tools(tools)