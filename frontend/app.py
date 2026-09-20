import os
import requests
import streamlit as st

TASK_URL = os.getenv("TASK_SERVICE_URL", "http://task-service:8000")
STATS_URL = os.getenv("STATS_SERVICE_URL", "http://stats-service:8000")

st.set_page_config(page_title="TaskFlow", page_icon="✅", layout="wide")
st.title("✅ TaskFlow")
st.caption("Simple cloud-native task manager")

create_tab, tasks_tab, stats_tab = st.tabs(["Add Task", "My Tasks", "Statistics"])

with create_tab:
    st.subheader("Add a new task")
    with st.form("create_task"):
        title = st.text_input("Task", placeholder="Finish cloud assignment")
        category = st.selectbox("Category", ["University", "Work", "Personal", "Shopping", "Other"])
        submit = st.form_submit_button("Add Task")
    if submit:
        try:
            response = requests.post(f"{TASK_URL}/tasks", json={"title": title, "category": category}, timeout=5)
            if response.ok:
                task = response.json()
                st.success(f"Task #{task['id']} created successfully.")
            else:
                st.error(response.text)
        except Exception as exc:
            st.error(f"Task service unavailable: {exc}")

with tasks_tab:
    st.subheader("My tasks")
    try:
        response = requests.get(f"{TASK_URL}/tasks", timeout=5)
        response.raise_for_status()
        tasks = response.json()
        if not tasks:
            st.info("No tasks yet. Add your first task.")
        for task in tasks:
            col1, col2, col3, col4 = st.columns([5, 2, 2, 1])
            state = "Completed" if task["completed"] else "Pending"
            col1.write(f"**#{task['id']} — {task['title']}**")
            col2.write(task["category"])
            col3.write(state)
            if not task["completed"]:
                if col4.button("✓", key=f"done-{task['id']}", help="Mark completed"):
                    requests.put(f"{TASK_URL}/tasks/{task['id']}", json={"completed": True}, timeout=5)
                    st.rerun()
            else:
                if col4.button("↩", key=f"undo-{task['id']}", help="Mark pending"):
                    requests.put(f"{TASK_URL}/tasks/{task['id']}", json={"completed": False}, timeout=5)
                    st.rerun()
            st.divider()
    except Exception as exc:
        st.error(f"Unable to load tasks: {exc}")

with stats_tab:
    st.subheader("Task statistics")
    try:
        response = requests.get(f"{STATS_URL}/stats", timeout=5)
        response.raise_for_status()
        stats = response.json()
        c1, c2, c3 = st.columns(3)
        c1.metric("Total", stats["total"])
        c2.metric("Completed", stats["completed"])
        c3.metric("Pending", stats["pending"])
        st.write("### Tasks by category")
        if stats["categories"]:
            st.bar_chart(stats["categories"])
        else:
            st.info("Add tasks to see category statistics.")
    except Exception as exc:
        st.error(f"Statistics service unavailable: {exc}")
