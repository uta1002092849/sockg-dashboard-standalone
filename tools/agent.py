from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferWindowMemory

from models.llms import gemini_pro

from tools.fewshot import cypher_qa

tools = [
    Tool.from_function (
        name = "General Chat",
        description = "For general chat that not covered by other tools",
        func = gemini_pro.invoke,
        return_direct = True
    ),
    Tool.from_function (
        name = "Cypher QA",
        description="Provides information about SOCKG database, including Experimental Units, Soil Samples, and more.",
        func = cypher_qa,
    ),
]

memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=5,
    return_messages=True,
)

agent_prompt = PromptTemplate.from_template("""
You are a cypher expert providing information about SOCKG database, which stand for Soil Organic Carbon Knowledge Graph.
The project was created to address the demand for accurate soil carbon data, which ultimately helps increase sustainable farming practices that mitigate greenhouse gas emissions.
The project is a collaboration between the University of Texas at Arlington (UTA) and the USDA Agricultural Research Service (ARS)

As a chat agent, your mission is to providing information about SOCKG, be helpful, and answer questions to the best of your ability.
Do not answer any questions that do not relate SOCKG.

TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
""")

agent = create_react_agent(gemini_pro, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True
    )

def generate_response(prompt):
    try:
        response = agent_executor.invoke({"input": prompt})
    except Exception as e:
        response = {
            'output': f"Sorry, some error occurred and I could not process your request. Please try again later."
        }

    return response['output']