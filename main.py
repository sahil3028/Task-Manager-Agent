import file_handling as fh
import streamlit as st

if "user" not in st.session_state:
    st.session_state.user = None

@st.dialog("Login")
def login_dialog():
    username = st.text_input("Enter username")

    if st.button("Continue"):
        if username.strip():
            username=username.strip()
            st.session_state.user = username
            st.rerun()
        else:
            st.warning("Username cannot be empty")

if st.session_state.user is None:
    login_dialog()
else:
    st.success(f"Welcome, {st.session_state.user} 👋")


st.title("TO-DO Agent")
st.subheader("manage your tasks with your ai friend")


print("++++++++++++++++++++++++++++++++++++++++++++++\n\n\n"+st.session_state.user)
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
                    fh.complete_task(user,st.session_state.tasks)
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
                        fh.complete_task(user,st.session_state.tasks)
                        st.rerun()

                with remove:
                    delete = st.button(
                        "🗑️",
                        key=f"delete_{todo['id']}"
                    )
                    if delete:
                        st.session_state.tasks.pop(index)
                        fh.complete_task(user, tasks)

def add_task():
    text = st.session_state.new.strip()
    if not text:
        return
    if tasks:
        st.session_state.tasks.append({
            "task": text,
            "status": False,
            "id": len(st.session_state.tasks)
        })
    else:
        st.session_state.tasks.append({
            "task": text,
            "status": False,
            "id": 0
        })
    fh.complete_task(user,st.session_state.tasks)
    st.session_state.new=""

if not st.session_state.mode:
    switch=st.button(label="BhOnDU BoT🤖",key="switch")
    st.text_input(label=" ", placeholder="Enter Your Task",key="new",on_change=add_task)

    if switch:
        st.session_state.mode=True
        st.rerun()
else:
    switch=st.button(label="To-dO📝",key="switch")
    st.subheader("BhOnDU BoT🤖 is comming soon")

    if switch:
        st.session_state.mode= False
        st.rerun()

print(st.session_state["new"])