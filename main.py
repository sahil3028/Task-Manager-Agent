import file_handling as fh
import streamlit as st
import random

from dotenv import load_dotenv
import os

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from  langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain.agents import create_openai_tools_agent,AgentExecutor


if "user" not in st.session_state:
    st.session_state.user = None

@st.dialog("Login")
def login_dialog():
    username = st.text_input("Enter username")

    if st.button("Continue"):
        if username.strip():
            st.session_state.user = username.strip()
            st.rerun()
        else:
            st.warning("Username cannot be empty")

if st.session_state.user is None:
    login_dialog()
    st.stop()

st.title("TO-DO Agent")
st.subheader("manage your tasks with your Bhondu-Bot")

user=st.session_state.user
if "tasks" not in st.session_state:
    st.session_state.tasks = fh.load_file(user)

if "mode" not in st.session_state:
    st.session_state.mode = False

tasks = st.session_state.tasks

ongoing,completed=st.columns(2)
with ongoing:
    st.subheader("CURRENT 🔥")
    if tasks:
        for index, todo in enumerate(tasks):
            if not todo["status"]:
                checked = st.checkbox(
                    todo["task"],
                    key=f"ongoing_{todo['id']}"
                )

                if checked:
                    st.session_state.tasks[index]["status"] = True
                    fh.save_file(user, st.session_state.tasks)
                    st.rerun()
    else:
        st.write("no tasks ")


with completed:
    if tasks:
        st.subheader("FINISHED ✅")
        for index, todo in enumerate(tasks):
            if todo["status"]:
                check,remove=st.columns([4,1])
                with check:
                    checked= st.checkbox(
                        todo["task"],
                        value=True,
                        key=f"completed_{todo['id']}"
                    )
                    if not checked:
                        st.session_state.tasks[index]["status"] = False
                        fh.save_file(user, st.session_state.tasks)
                        st.rerun()

                with remove:
                    delete = st.button(
                        "🗑️",
                        key=f"delete_{todo['id']}"
                    )
                    if delete:
                        st.session_state.tasks.pop(index)
                        fh.save_file(user, tasks)

def ui_add_task():
    """add a new task for the user, use this when the user asks to add a task or create a new task,or use this when the user wants you to remember something"""
    text=st.session_state.new.strip()
    if text is None:
        if not text:
            return

    if tasks:
        st.session_state.tasks.append({
            "task": text,
            "status": False,
            "id": f"{len(st.session_state.tasks)}{random.randint(1, 10)}"
        })
    else:
        st.session_state.tasks.append({
            "task": text,
            "status": False,
            "id": 0
        })
    fh.save_file(user, st.session_state.tasks)
    st.session_state.new=""


@tool
def add_task(text=None):
    """add a new task for the user, use this when the user asks to add a task or create a new task,or use this when the user wants you to remember something"""
    if text is None:
        return

    if tasks:
        st.session_state.tasks.append({
            "task": text,
            "status": False,
            "id": f"{len(st.session_state.tasks)}{random.randint(1, 10)}"
        })
    else:
        st.session_state.tasks.append({
            "task": text,
            "status": False,
            "id": 0
        })
    fh.save_file(user, st.session_state.tasks)


@tool
def get_tasks_text():
    """inspect all the tasks,use if you need to fetch a task for user, when the user ask to show you any task  or show all the task"""
    if not st.session_state.tasks:
        return "You have no tasks."

    lines = []
    for t in st.session_state.tasks:
        status = "Completed-" if t["status"] else "Not Completed-"
        lines.append(f"{status} {t['task']}")

    return "\n".join(lines)


def init_agent():
    load_dotenv()
    gemini_api = os.getenv("GEMINI_API_KEY")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=gemini_api,
        temperature=0.3   # lower = cheaper + more stable
    )

    # system_prompt = (
    #     "You are Bhondu-Bot, a task assistant.\n"
    #     "You can add tasks, explain tasks, and list tasks when asked.\n"
    #     "If the user asks to see tasks, show them clearly in bullet points.\n"
    #     "you're a helpful assistant. who help people with their task and clear their doubts and help them in whatever they ask you"
    # )
    system_prompt = (
        "You are Bhondu-Bot, a helpful personal task assistant.\n"
        "You can:\n"
        "- add tasks\n"
        "- list tasks\n"
        "- explain tasks\n"
        "- give general, safe, step-by-step advice on how to complete a task\n\n"
        "If the user asks how to do a task, explain it in simple steps.\n"
        "Do not refuse for anything."
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("history"),
        ("user", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])

    tools = [add_task,get_tasks_text]

    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False)


def bhondu_bot():
    if "agent" not in st.session_state:
        st.session_state.agent = init_agent()

    if "history" not in st.session_state:
        st.session_state.history = []

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])


    user_msg = st.chat_input("Ask something...")
    if not user_msg:
        return

    # Inject tasks ONLY if relevant
    # if "task" in user_msg.lower() or "show" in user_msg.lower():
    #     task_context = get_tasks_text()
    #     user_msg = f"{user_msg}\n\nUser tasks:\n{task_context}"

    # Call agent ONLY now
    response = st.session_state.agent.invoke({"input": user_msg,"history":st.session_state.history})


    if user_msg:
        st.session_state.messages.append({
            "role": "user",
            "content": user_msg
        })

        reply = response["output"]

        st.session_state.history.append(HumanMessage(content=user_msg))
        st.session_state.history.append(AIMessage(content=response["output"]))

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply
        })

        st.rerun()

if not st.session_state.mode:
    switch=st.button(label="BhOnDU BoT🤖",key="switch")
    st.text_input(label=" ", placeholder="Enter Your Task",key="new",on_change=ui_add_task)

    if switch:
        st.session_state.mode=True
        st.rerun()
else:
    switch=st.button(label="To-dO📝",key="switch")
    st.subheader("BhOnDU BoT🤖 is here")
    bhondu_bot()

    if switch:
        st.session_state.mode= False
        st.rerun()