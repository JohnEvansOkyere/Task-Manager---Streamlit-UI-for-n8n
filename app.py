"""
Task Manager - Streamlit Frontend
Professional UI connecting to FastAPI backend
"""

import streamlit as st
import requests
from datetime import datetime
import time
from typing import Optional, Dict, List

# Page configuration
st.set_page_config(
    page_title="Task Manager Pro",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .task-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .status-todo {
        background-color: #fff3cd;
        border-left-color: #ffc107;
    }
    .status-inprogress {
        background-color: #cfe2ff;
        border-left-color: #0d6efd;
    }
    .status-done {
        background-color: #d1e7dd;
        border-left-color: #198754;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'api_url' not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'show_create_form' not in st.session_state:
    st.session_state.show_create_form = False
if 'connection_status' not in st.session_state:
    st.session_state.connection_status = None
if 'stats' not in st.session_state:
    st.session_state.stats = None


class APIClient:
    """Client for FastAPI backend"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.timeout = 30
    
    def health_check(self) -> tuple[bool, str]:
        """Check API health"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return True, f"✅ Connected - Status: {data['status']}"
            return False, f"❌ Error: {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"❌ Connection failed: {str(e)}"
    
    def get_tasks(self, status_filter: Optional[str] = None) -> Dict:
        """Get all tasks"""
        try:
            params = {}
            if status_filter:
                params['status_filter'] = status_filter
            
            response = requests.get(
                f"{self.base_url}/api/v1/tasks",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_task(self, task_data: Dict) -> Dict:
        """Create a new task"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/tasks",
                json=task_data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_task(self, task_name: str, update_data: Dict) -> Dict:
        """Update a task"""
        try:
            response = requests.put(
                f"{self.base_url}/api/v1/tasks/{task_name}",
                json=update_data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_task(self, task_name: str) -> Dict:
        """Delete a task"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/v1/tasks/{task_name}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_message(self, message: str, session_id: str = "streamlit") -> Dict:
        """Send natural language message"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/message",
                json={"message": message, "session_id": session_id},
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_stats(self) -> Dict:
        """Get task statistics"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/stats",
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Initialize API client
api_client = APIClient(st.session_state.api_url)

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    
    api_url = st.text_input(
        "FastAPI Backend URL",
        value=st.session_state.api_url,
        placeholder="http://localhost:8000",
        help="Enter your FastAPI backend URL"
    )
    
    if api_url != st.session_state.api_url:
        st.session_state.api_url = api_url
        api_client = APIClient(api_url)
        st.session_state.connection_status = None
        st.rerun()
    
    # Test connection
    if st.button("🔌 Test Connection", use_container_width=True):
        with st.spinner("Testing connection..."):
            success, message = api_client.health_check()
            st.session_state.connection_status = (success, message)
            st.rerun()
    
    if st.session_state.connection_status:
        success, message = st.session_state.connection_status
        if success:
            st.success(message)
        else:
            st.error(message)
    
    st.divider()
    
    # Filters
    st.markdown("### 🔍 Filters")
    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "TODO", "IN PROGRESS", "DONE"],
        index=0
    )
    
    st.divider()
    
    st.markdown("### 📊 Status Guide")
    st.markdown("🟡 **TODO** - Not started")
    st.markdown("🔵 **IN PROGRESS** - Working")
    st.markdown("🟢 **DONE** - Completed")
    
    st.divider()
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    st.divider()
    st.markdown("### 📚 Quick Help")
    st.markdown("""
    - Create tasks with all details
    - Update status quickly
    - Delete completed tasks
    - Use natural language commands
    """)

# Main content
st.title("✅ Task Manager Pro")
st.markdown("*Professional task management with AI-powered backend*")

# Action buttons
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("➕ New Task", use_container_width=True):
        st.session_state.show_create_form = not st.session_state.show_create_form

with col2:
    if st.button("📊 View Stats", use_container_width=True):
        result = api_client.get_stats()
        if result["success"]:
            st.session_state.stats = result["data"]

st.divider()

# Display Stats
if st.session_state.stats:
    st.subheader("📊 Task Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    stats = st.session_state.stats
    
    with col1:
        st.metric("Total Tasks", stats.get("total_tasks", 0))
    
    with col2:
        st.metric("TODO", stats.get("by_status", {}).get("TODO", 0))
    
    with col3:
        st.metric("In Progress", stats.get("by_status", {}).get("IN PROGRESS", 0))
    
    with col4:
        completion = stats.get("completion_rate", 0)
        st.metric("Completion Rate", f"{completion}%")
    
    st.divider()

# Create Task Form
if st.session_state.show_create_form:
    st.subheader("➕ Create New Task")
    
    with st.form("create_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            task_name = st.text_input("Task Name *", placeholder="Enter task name")
            status = st.selectbox("Status", ["TODO", "IN PROGRESS", "DONE"], index=0)
        
        with col2:
            deadline = st.date_input("Deadline (Optional)", value=None)
            description = st.text_area("Description (Optional)", placeholder="Enter description", height=100)
        
        submitted = st.form_submit_button("✅ Create Task", use_container_width=True)
        
        if submitted:
            if not task_name:
                st.error("❌ Task name is required!")
            else:
                with st.spinner("Creating task..."):
                    task_data = {
                        "task_name": task_name,
                        "status": status,
                        "description": description if description else None,
                        "deadline": deadline.strftime("%Y-%m-%d") if deadline else None
                    }
                    
                    result = api_client.create_task(task_data)
                    
                    if result["success"]:
                        st.success(f"✅ Task '{task_name}' created successfully!")
                        time.sleep(1)
                        st.session_state.show_create_form = False
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result['error']}")

# Display Tasks
st.subheader("📋 Your Tasks")

# Fetch tasks
filter_param = None if status_filter == "All" else status_filter

with st.spinner("Loading tasks..."):
    result = api_client.get_tasks(filter_param)

if result["success"]:
    data = result["data"]
    tasks = data.get("tasks", [])
    
    if tasks:
        st.markdown(f"*Showing {len(tasks)} task(s)*")
        
        # Display tasks
        for task in tasks:
            task_name = task.get("task_name", "Unnamed Task")
            task_status = task.get("status", "TODO")
            description = task.get("description", "No description")
            deadline = task.get("deadline", "No deadline")
            
            # Status styling
            status_class = {
                "TODO": "todo",
                "IN PROGRESS": "inprogress",
                "DONE": "done"
            }.get(task_status, "todo")
            
            # Display task card
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="task-card status-{status_class}">
                        <h4>📌 {task_name}</h4>
                        <p><strong>Status:</strong> {task_status}</p>
                        <p><strong>Description:</strong> {description}</p>
                        <p><strong>Deadline:</strong> {deadline}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("**Actions**")
                    
                    new_status = st.selectbox(
                        "Change Status",
                        ["TODO", "IN PROGRESS", "DONE"],
                        key=f"status_{task_name}",
                        label_visibility="collapsed"
                    )
                    
                    if st.button("🔄 Update", key=f"update_{task_name}", use_container_width=True):
                        with st.spinner("Updating..."):
                            result = api_client.update_task(
                                task_name,
                                {"status": new_status}
                            )
                            if result["success"]:
                                st.success("✅ Updated!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(f"❌ {result['error']}")
                    
                    if st.button("🗑️ Delete", key=f"delete_{task_name}", use_container_width=True):
                        with st.spinner("Deleting..."):
                            result = api_client.delete_task(task_name)
                            if result["success"]:
                                st.success("✅ Deleted!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(f"❌ {result['error']}")
    else:
        st.info("📭 No tasks found. Create your first task!")
else:
    st.error(f"❌ Error loading tasks: {result['error']}")

# Natural Language Command Section
with st.expander("💬 Natural Language Commands"):
    st.markdown("Send commands in plain English to your AI agent")
    
    custom_message = st.text_area(
        "Your command",
        placeholder="E.g., 'Show me all tasks due this week' or 'Update task X to in progress'",
        height=100
    )
    
    if st.button("🚀 Send Command", use_container_width=True):
        if custom_message:
            with st.spinner("Processing..."):
                result = api_client.send_message(custom_message)
                if result["success"]:
                    st.success("✅ Command processed!")
                    st.json(result["data"])
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p><strong>Task Manager Pro</strong> | FastAPI Backend + Streamlit Frontend + n8n AI Agent</p>
        <p>Built with ❤️ for ML Engineers</p>
    </div>
    """, unsafe_allow_html=True)