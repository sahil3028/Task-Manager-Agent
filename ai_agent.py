from dotenv import load_dotenv
import os

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from  langchain_google_genai import ChatGoogleGenerativeAI
from pydantic_core.core_schema import model_field
from langchain.tools import tool
from langchain.agents import create_openai_tools_agent,AgentExecutor
from todoist_api_python.api import TodoistAPI



load_dotenv()

todo_api=os.getenv("TODOLIST_API_KEY")
gemini_api=os.getenv("GEMINI_API_KEY")

llm= ChatGoogleGenerativeAI(
    model='gemini-2.5-flash',
    google_api_key=gemini_api,
    temperature=0.5
)


todolist=TodoistAPI(todo_api)


@tool
def add_task(task,description=None):
    """add a new task for the user, use this when the user asks to add a task or create a new task"""
    todolist.add_task(content=task,
                      description=description
                      )
@tool
def show_task():
    """show all the task from Todolist, use this when the user wants to see all of his task or user asks a questions about their previous task"""
    results_paginator =todolist.get_tasks()
    tasks=[]
    for task_list in results_paginator:
        for task in task_list:
            print(task)
            tasks.append(task.content)
            print(task.content)
    return tasks
tools=[add_task,show_task]


system_prompt="""youre a helpful assistant. who help people with their task and clear their doubts and help them in whatever they ask
                you also show the user all the tasks if they ask you to show all the tasks , you show them directly in bullet points"""

#prompt has a list of 2 tuples
prompt= ChatPromptTemplate([("system",system_prompt),
                            MessagesPlaceholder("history"),
                            ("user","{input}"),
                            MessagesPlaceholder("agent_scratchpad")
                            ])


#in langchain | doesnt mean "OR" it has special meaning
#chain= prompt | llm | StrOutputParser()

#this was used to take input if using chain
#response= chain.invoke({"input":user_input})

agent= create_openai_tools_agent(llm,tools,prompt)
agent_executor= AgentExecutor(agent=agent,tools=tools,verbose=False)

history=[]
while True:
    user_input = input("me: ")
    response = agent_executor.invoke({"input": user_input,"history":history})
    print(response["output"])
    history.append(HumanMessage(content=user_input))
    history.append(AIMessage(content=response["output"]))