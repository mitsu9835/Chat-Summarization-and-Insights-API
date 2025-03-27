"""
Streamlit UI for interacting with the Chat Summarization API.
"""
import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime
import time


class ChatSummarizerUI:
    """Streamlit UI for Chat Summarization and Insights API."""
    
    def __init__(self):
        """Initialize the UI components."""
        self.base_url = "http://localhost:8000/api/v1"
        self.api_key = None
        
        # Set page config
        st.set_page_config(
            page_title="Chat Summarization Dashboard",
            page_icon="💬",
            layout="wide"
        )
        
        # Initialize session state
        if "conversations" not in st.session_state:
            st.session_state.conversations = []
        if "current_conversation" not in st.session_state:
            st.session_state.current_conversation = None
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "summary" not in st.session_state:
            st.session_state.summary = None
    
    def setup_sidebar(self):
        """Setup the sidebar with API connection and navigation."""
        with st.sidebar:
            st.title("Chat Summarization")
            
            # API connection
            st.subheader("API Connection")
            self.api_key = st.text_input("API Key", type="password")
            
            if st.button("Test Connection"):
                self.test_connection()
            
            st.divider()
            
            # Navigation
            st.subheader("Navigation")
            if st.button("View Conversations"):
                self.load_conversations()
            
            st.divider()
            
            # Upload new conversation
            st.subheader("Upload Conversation")
            uploaded_file = st.file_uploader(
                "Upload CSV file", 
                type="csv",
                help="CSV format: timestamp,user_id,user_type,message_content"
            )
            
            if uploaded_file is not None:
                conversation_id = st.text_input("Conversation ID (optional)")
                
                if st.button("Process CSV"):
                    self.process_csv(uploaded_file, conversation_id)
    
    def test_connection(self):
        """Test the API connection."""
        try:
            response = requests.get(f"{self.base_url[:-7]}/health")
            if response.status_code == 200:
                st.sidebar.success("Connected to API successfully!")
            else:
                st.sidebar.error(f"Failed to connect: {response.status_code}")
        except Exception as e:
            st.sidebar.error(f"Connection error: {e}")
    
    def load_conversations(self):
        """Load the user's conversations."""
        st.session_state.current_conversation = None
        st.session_state.messages = []
        st.session_state.summary = None
        
        # TODO: In a real app, we would fetch the actual user ID
        user_id = "demo-user"
        
        try:
            headers = {"X-API-Key": self.api_key}
            response = requests.get(
                f"{self.base_url}/users/{user_id}/chats",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.conversations = data.get("conversations", [])
            else:
                st.error(f"Failed to load conversations: {response.status_code}")
        except Exception as e:
            st.error(f"Error loading conversations: {e}")
    
    def process_csv(self, file, conversation_id=None):
        """Process and upload a CSV file of chat messages."""
        try:
            # Read CSV
            df = pd.read_csv(file)
            
            # Generate conversation ID if not provided
            if not conversation_id:
                conversation_id = f"conv-{int(time.time())}"
            
            # Convert DataFrame to messages
            messages = []
            for _, row in df.iterrows():
                message = {
                    "conversation_id": conversation_id,
                    "message_id": f"msg-{len(messages)+1}",
                    "message_content": row["message_content"],
                    "user_id": row["user_id"],
                    "user_type": row["user_type"],
                    "timestamp": row["timestamp"]
                }
                messages.append(message)
            
            # Upload messages
            headers = {"X-API-Key": self.api_key}
            for message in messages:
                response = requests.post(
                    f"{self.base_url}/chats",
                    json=message,
                    headers=headers
                )
                
                if response.status_code != 201:
                    st.error(f"Failed to upload message: {response.status_code}")
                    return
            
            st.sidebar.success(f"Successfully uploaded {len(messages)} messages!")
            
            # Set as current conversation
            st.session_state.current_conversation = conversation_id
            self.load_conversation_messages(conversation_id)
            
        except Exception as e:
            st.error(f"Error processing CSV: {e}")
    
    def load_conversation_messages(self, conversation_id):
        """Load messages for a specific conversation."""
        try:
            headers = {"X-API-Key": self.api_key}
            response = requests.get(
                f"{self.base_url}/chats/{conversation_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                st.session_state.messages = response.json()
                
                # Try to load summary
                self.load_conversation_summary(conversation_id)
            else:
                st.error(f"Failed to load messages: {response.status_code}")
        except Exception as e:
            st.error(f"Error loading messages: {e}")
    
    def load_conversation_summary(self, conversation_id):
        """Load summary for a specific conversation."""
        try:
            headers = {"X-API-Key": self.api_key}
            response = requests.get(
                f"{self.base_url}/chats/{conversation_id}/summary",
                headers=headers
            )
            
            if response.status_code == 200:
                st.session_state.summary = response.json()
            elif response.status_code == 404:
                st.session_state.summary = None
            else:
                st.error(f"Failed to load summary: {response.status_code}")
        except Exception as e:
            st.error(f"Error loading summary: {e}")
    
    def generate_summary(self, conversation_id):
        """Generate a summary for a conversation."""
        try:
            headers = {"X-API-Key": self.api_key}
            response = requests.post(
                f"{self.base_url}/chats/summarize",
                json={"conversation_id": conversation_id},
                headers=headers
            )
            
            if response.status_code == 200:
                st.session_state.summary = response.json()
                st.success("Summary generated successfully!")
            else:
                st.error(f"Failed to generate summary: {response.status_code}")
        except Exception as e:
            st.error(f"Error generating summary: {e}")
    
    def display_conversation_list(self):
        """Display the list of conversations."""
        st.header("Conversations")
        
        if not st.session_state.conversations:
            st.info("No conversations found. Upload a CSV file to get started.")
            return
        
        # Create a DataFrame for better display
        data = []
        for conv in st.session_state.conversations:
            last_message = conv.get("last_message", {})
            data.append({
                "Conversation ID": conv.get("conversation_id"),
                "Last Message": last_message.get("message_content", "")[:50] + "...",
                "Messages": conv.get("message_count", 0),
                "Last Updated": last_message.get("timestamp", "")
            })
        
        df = pd.DataFrame(data)
        
        # Display as a table with select button
        for i, row in df.iterrows():
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button(f"View", key=f"view_{i}"):
                    st.session_state.current_conversation = row["Conversation ID"]
                    self.load_conversation_messages(row["Conversation ID"])
            with col2:
                st.write(f"**{row['Conversation ID']}** - {row['Last Message']}")
                st.write(f"Messages: {row['Messages']} | Last Updated: {row['Last Updated']}")
            st.divider()
    
    def display_conversation(self):
        """Display the current conversation and summary."""
        if not st.session_state.current_conversation:
            self.display_conversation_list()
            return
        
        st.header(f"Conversation: {st.session_state.current_conversation}")
        
        # Actions
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Back to Conversations"):
                st.session_state.current_conversation = None
                st.session_state.messages = []
                st.session_state.summary = None
                st.rerun()
        
        with col2:
            if st.button("Generate Summary"):
                self.generate_summary(st.session_state.current_conversation)
        
        with col3:
            if st.button("Delete Conversation"):
                self.delete_conversation(st.session_state.current_conversation)
        
        # Display conversation and summary side by side
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("Messages")
            self.display_messages()
        
        with col2:
            st.subheader("Summary & Insights")
            self.display_summary()
    
    def display_messages(self):
        """Display the messages in the current conversation."""
        if not st.session_state.messages:
            st.info("No messages found in this conversation.")
            return
        
        for msg in st.session_state.messages:
            is_customer = msg.get("user_type") == "customer"
            
            # Format timestamp
            timestamp = datetime.fromisoformat(msg.get("timestamp").replace("Z", "+00:00"))
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            # Display message with different styling based on user type
            if is_customer:
                st.markdown(
                    f"""
                    <div style="border-radius: 10px; background-color: #e0f7fa; padding: 10px; margin: 5px 0;">
                        <b>Customer:</b> {msg.get('message_content')}<br>
                        <small>{time_str}</small>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="border-radius: 10px; background-color: #f5f5f5; padding: 10px; margin: 5px 0;">
                        <b>Support Agent:</b> {msg.get('message_content')}<br>
                        <small>{time_str}</small>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
    
    def display_summary(self):
        """Display the summary and insights for the current conversation."""
        if not st.session_state.summary:
            st.info("No summary available. Generate a summary to see insights.")
            return
        
        summary = st.session_state.summary
        
        st.write("**Summary:**")
        st.write(summary.get("summary"))
        
        st.divider()
        
        # Sentiment and Outcome
        cols = st.columns(2)
        with cols[0]:
            sentiment = summary.get("sentiment", "").capitalize()
            st.metric("Sentiment", sentiment)
        
        with cols[1]:
            outcome = summary.get("outcome", "").capitalize()
            st.metric("Outcome", outcome)
        
        st.divider()
        
        # Action Items
        st.write("**Action Items:**")
        action_items = summary.get("action_items", [])
        if action_items:
            for item in action_items:
                st.write(f"- {item}")
        else:
            st.write("No action items identified.")
        
        st.divider()
        
        # Decisions
        st.write("**Decisions:**")
        decisions = summary.get("decisions", [])
        if decisions:
            for decision in decisions:
                st.write(f"- {decision}")
        else:
            st.write("No decisions identified.")
        
        st.divider()
        
        # Questions
        st.write("**Questions:**")
        questions = summary.get("questions", [])
        if questions:
            for question in questions:
                st.write(f"- {question}")
        else:
            st.write("No questions identified.")
        
        st.divider()
        
        # Keywords
        st.write("**Keywords:**")
        keywords = summary.get("keywords", [])
        if keywords:
            st.write(", ".join(keywords))
        else:
            st.write("No keywords identified.")
    
    def delete_conversation(self, conversation_id):
        """Delete a conversation."""
        try:
            headers = {"X-API-Key": self.api_key}
            response = requests.delete(
                f"{self.base_url}/chats/{conversation_id}",
                headers=headers
            )
            
            if response.status_code == 204:
                st.success("Conversation deleted successfully!")
                # Reset current conversation
                st.session_state.current_conversation = None
                st.session_state.messages = []
                st.session_state.summary = None
                # Reload conversation list
                self.load_conversations()
                st.rerun()
            else:
                st.error(f"Failed to delete conversation: {response.status_code}")
        except Exception as e:
            st.error(f"Error deleting conversation: {e}")
    
    def run(self):
        """Run the Streamlit application."""
        # Setup sidebar first
        self.setup_sidebar()
        
        # Main content area
        if st.session_state.current_conversation:
            self.display_conversation()
        else:
            self.display_conversation_list()


if __name__ == "__main__":
    app = ChatSummarizerUI()
    app.run() 