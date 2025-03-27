"""
Streamlit UI for the Chat Summarization API.
"""
import streamlit as st
import pandas as pd
import requests
import json
import os
import datetime
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any


class ChatSummarizerUI:
    """Streamlit UI for Chat Summarization and Insights API."""
    
    def __init__(self):
        """Initialize the UI."""
        # Set page config
        st.set_page_config(
            page_title="Chat Summarization Dashboard",
            page_icon="💬",
            layout="wide"
        )
        
        # Initialize session state
        if "api_key" not in st.session_state:
            st.session_state.api_key = ""
        if "api_url" not in st.session_state:
            st.session_state.api_url = "http://localhost:8000/api/v1"
        if "selected_conversation" not in st.session_state:
            st.session_state.selected_conversation = None
        if "conversations" not in st.session_state:
            st.session_state.conversations = []
        if "current_page" not in st.session_state:
            st.session_state.current_page = "dashboard"  # dashboard, conversations, upload
    
    def setup_sidebar(self):
        """Create the sidebar with navigation and settings."""
        with st.sidebar:
            st.title("Chat Summarization")
            
            # API Settings
            st.subheader("API Settings")
            st.session_state.api_url = st.text_input("API URL", value=st.session_state.api_url)
            st.session_state.api_key = st.text_input("API Key", value=st.session_state.api_key, type="password")
            
            if st.button("Test Connection"):
                self.test_api_connection()
            
            st.divider()
            
            # Navigation
            st.subheader("Navigation")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Dashboard"):
                    st.session_state.current_page = "dashboard"
                    st.session_state.selected_conversation = None
            
            with col2:
                if st.button("💬 Chats"):
                    st.session_state.current_page = "conversations"
                    self.load_conversations()
            
            with col3:
                if st.button("📤 Upload"):
                    st.session_state.current_page = "upload"
    
    def test_api_connection(self):
        """Test the connection to the API."""
        try:
            response = requests.get(f"{st.session_state.api_url.rstrip('/')}/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    st.sidebar.success("API connection successful!")
                else:
                    st.sidebar.warning(f"API status: {data.get('status')}")
            else:
                st.sidebar.error(f"Failed to connect: {response.status_code}")
        except Exception as e:
            st.sidebar.error(f"Connection error: {str(e)}")
    
    def load_conversations(self):
        """Load conversations from the API."""
        if not st.session_state.api_key:
            st.warning("Please enter an API key in the sidebar first.")
            return
        
        try:
            headers = {"X-API-Key": st.session_state.api_key}
            response = requests.get(
                f"{st.session_state.api_url}/users/me/chats",
                headers=headers,
                params={"page": 1, "limit": 50}
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.conversations = data.get("conversations", [])
            elif response.status_code == 401:
                st.error("Unauthorized. Please check your API key.")
            else:
                st.error(f"Failed to load conversations: {response.status_code}")
        except Exception as e:
            st.error(f"Error loading conversations: {str(e)}")
    
    def display_dashboard(self):
        """Display the main dashboard with analytics."""
        st.title("Chat Summarization Dashboard")
        
        # If no conversations, load them
        if not st.session_state.conversations:
            self.load_conversations()
        
        # If still no conversations, show message
        if not st.session_state.conversations:
            st.info("No conversations found. Upload some chat data to get started.")
            return
        
        # Calculate statistics
        total_conversations = len(st.session_state.conversations)
        total_messages = sum(conv.get("message_count", 0) for conv in st.session_state.conversations)
        avg_messages = total_messages / total_conversations if total_conversations > 0 else 0
        
        # Display KPIs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Conversations", total_conversations)
        
        with col2:
            st.metric("Total Messages", total_messages)
        
        with col3:
            st.metric("Avg. Messages per Conversation", f"{avg_messages:.1f}")
        
        # Create sample charts
        st.subheader("Conversation Statistics")
        
        # Sample data for charts
        cols = st.columns(2)
        
        with cols[0]:
            # Create sample sentiment distribution
            sentiments = ["Positive", "Neutral", "Negative", "Mixed"]
            sentiment_counts = [7, 12, 3, 5]  # Sample data
            
            fig = px.pie(
                names=sentiments,
                values=sentiment_counts,
                title="Sentiment Distribution",
                color=sentiments,
                color_discrete_map={
                    "Positive": "#4CAF50",
                    "Neutral": "#2196F3", 
                    "Negative": "#F44336",
                    "Mixed": "#FF9800"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with cols[1]:
            # Create sample conversation outcome distribution
            outcomes = ["Yes", "No", "Maybe", "Curious"]
            outcome_counts = [15, 5, 5, 2]  # Sample data
            
            fig = px.bar(
                x=outcomes,
                y=outcome_counts,
                title="Conversation Outcomes",
                labels={"x": "Outcome", "y": "Count"},
                color=outcomes,
                color_discrete_map={
                    "Yes": "#4CAF50",
                    "No": "#F44336", 
                    "Maybe": "#FF9800",
                    "Curious": "#2196F3"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent conversations
        st.subheader("Recent Conversations")
        if st.session_state.conversations:
            for i, conv in enumerate(st.session_state.conversations[:5]):
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(f"View", key=f"view_{i}"):
                        st.session_state.selected_conversation = conv.get("conversation_id")
                        st.session_state.current_page = "conversation_detail"
                
                with col2:
                    last_message = conv.get("last_message", {})
                    message_preview = last_message.get("message_content", "")
                    if len(message_preview) > 100:
                        message_preview = message_preview[:100] + "..."
                    
                    st.write(f"**Conversation {conv.get('conversation_id')}**")
                    st.write(f"Messages: {conv.get('message_count', 0)}")
                    st.write(f"Last message: {message_preview}")
                
                st.divider()
    
    def display_conversations_list(self):
        """Display the list of all conversations."""
        st.title("All Conversations")
        
        # Load conversations if needed
        if not st.session_state.conversations:
            self.load_conversations()
        
        # Display conversations
        if not st.session_state.conversations:
            st.info("No conversations found. Upload some chat data to get started.")
            return
        
        # Create a dataframe for better display
        data = []
        for conv in st.session_state.conversations:
            last_message = conv.get("last_message", {})
            
            # Try to format timestamp
            try:
                timestamp = last_message.get("timestamp", "")
                if timestamp:
                    dt = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    timestamp = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass
            
            data.append({
                "ID": conv.get("conversation_id", ""),
                "Messages": conv.get("message_count", 0),
                "Last Update": timestamp,
                "Preview": last_message.get("message_content", "")[:50] + "..."
            })
        
        if data:
            df = pd.DataFrame(data)
            
            # Allow searching and filtering
            search = st.text_input("Search conversations", "")
            
            if search:
                df = df[df["Preview"].str.contains(search, case=False) | 
                         df["ID"].str.contains(search, case=False)]
            
            # Display the table
            st.dataframe(df, use_container_width=True)
            
            # Allow selecting a conversation
            selected_id = st.selectbox("Select a conversation to view", 
                                      [""] + df["ID"].tolist())
            
            if selected_id:
                st.session_state.selected_conversation = selected_id
                st.session_state.current_page = "conversation_detail"
                st.rerun()
        else:
            st.info("No conversations match your search criteria.")
    
    def display_conversation_detail(self):
        """Display details of a selected conversation."""
        if not st.session_state.selected_conversation:
            st.session_state.current_page = "conversations"
            st.rerun()
            return
        
        conv_id = st.session_state.selected_conversation
        st.title(f"Conversation: {conv_id}")
        
        # Button to go back to list
        if st.button("← Back to Conversations"):
            st.session_state.current_page = "conversations"
            st.session_state.selected_conversation = None
            st.rerun()
        
        # Get conversation messages
        try:
            headers = {"X-API-Key": st.session_state.api_key}
            response = requests.get(
                f"{st.session_state.api_url}/chats/{conv_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                messages = response.json()
                
                # Try to get summary
                summary_response = requests.get(
                    f"{st.session_state.api_url}/chats/{conv_id}/summary",
                    headers=headers
                )
                
                summary = None
                if summary_response.status_code == 200:
                    summary = summary_response.json()
                
                # Display in columns
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    self.display_conversation_messages(messages)
                
                with col2:
                    self.display_conversation_summary(conv_id, summary)
                
            elif response.status_code == 404:
                st.error(f"Conversation {conv_id} not found.")
            else:
                st.error(f"Failed to load conversation: {response.status_code}")
        except Exception as e:
            st.error(f"Error loading conversation: {str(e)}")
    
    def display_conversation_messages(self, messages):
        """Display chat messages in a conversation."""
        st.subheader("Messages")
        
        if not messages:
            st.info("No messages found in this conversation.")
            return
        
        for msg in messages:
            # Determine if customer or support agent
            is_customer = msg.get("user_type") == "customer"
            user_label = "Customer" if is_customer else "Support Agent"
            bg_color = "#E0F7FA" if is_customer else "#F5F5F5"
            
            # Format timestamp
            timestamp = msg.get("timestamp", "")
            try:
                if timestamp:
                    dt = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    timestamp = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass
            
            # Create the message box
            st.markdown(
                f"""
                <div style="border-radius: 10px; background-color: {bg_color}; padding: 10px; margin: 5px 0;">
                    <b>{user_label}:</b> {msg.get('message_content')}<br>
                    <small style="color: gray;">{timestamp}</small>
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    def display_conversation_summary(self, conv_id, summary):
        """Display the summary and insights for a conversation."""
        st.subheader("Summary & Insights")
        
        if not summary:
            st.info("No summary available for this conversation.")
            
            if st.button("Generate Summary"):
                self.generate_conversation_summary(conv_id)
            
            return
        
        # Display summary
        st.markdown("### Summary")
        st.write(summary.get("summary", "No summary available."))
        
        # Display sentiment and outcome
        col1, col2 = st.columns(2)
        with col1:
            sentiment = summary.get("sentiment", "").capitalize()
            sentiment_color = {
                "Positive": "#4CAF50",
                "Negative": "#F44336",
                "Neutral": "#2196F3",
                "Mixed": "#FF9800"
            }.get(sentiment, "#2196F3")
            
            st.markdown(
                f"""
                <div style="border-radius: 5px; border: 1px solid {sentiment_color}; padding: 10px; text-align: center;">
                    <h4 style="margin: 0; color: {sentiment_color};">Sentiment</h4>
                    <p style="font-size: 1.2em; margin: 5px 0;">{sentiment}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            outcome = summary.get("outcome", "").capitalize()
            outcome_color = {
                "Yes": "#4CAF50",
                "No": "#F44336",
                "Maybe": "#FF9800",
                "Curious": "#2196F3"
            }.get(outcome, "#2196F3")
            
            st.markdown(
                f"""
                <div style="border-radius: 5px; border: 1px solid {outcome_color}; padding: 10px; text-align: center;">
                    <h4 style="margin: 0; color: {outcome_color};">Outcome</h4>
                    <p style="font-size: 1.2em; margin: 5px 0;">{outcome}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Display action items
        st.markdown("### Action Items")
        action_items = summary.get("action_items", [])
        if action_items:
            for item in action_items:
                st.markdown(f"- {item}")
        else:
            st.write("No action items identified.")
        
        # Display decisions
        st.markdown("### Decisions")
        decisions = summary.get("decisions", [])
        if decisions:
            for decision in decisions:
                st.markdown(f"- {decision}")
        else:
            st.write("No decisions identified.")
        
        # Display questions
        st.markdown("### Questions")
        questions = summary.get("questions", [])
        if questions:
            for question in questions:
                st.markdown(f"- {question}")
        else:
            st.write("No questions identified.")
        
        # Display keywords
        st.markdown("### Keywords")
        keywords = summary.get("keywords", [])
        if keywords:
            st.write(", ".join(keywords))
        else:
            st.write("No keywords identified.")
    
    def generate_conversation_summary(self, conv_id):
        """Generate a summary for a conversation."""
        try:
            with st.spinner("Generating summary..."):
                headers = {"X-API-Key": st.session_state.api_key}
                response = requests.post(
                    f"{st.session_state.api_url}/chats/summarize",
                    json={"conversation_id": conv_id},
                    headers=headers
                )
                
                if response.status_code == 200:
                    st.success("Summary generated successfully!")
                    # Refresh the page to show the summary
                    st.rerun()
                else:
                    st.error(f"Failed to generate summary: {response.status_code}")
        except Exception as e:
            st.error(f"Error generating summary: {str(e)}")
    
    def display_upload_page(self):
        """Display the page for uploading CSV files."""
        st.title("Upload Chat Data")
        
        st.write("""
        Upload a CSV file containing chat data. The file should have the following columns:
        - `conversation_id`: Unique identifier for the conversation
        - `message_id`: Unique identifier for the message
        - `message_content`: The text content of the message
        - `user_id`: Identifier for the user who sent the message
        - `user_type`: Either "customer" or "support_agent"
        - `timestamp`: The time the message was sent (ISO format)
        """)
        
        # File upload
        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
        
        if uploaded_file is not None:
            # Preview the data
            df = pd.read_csv(uploaded_file)
            st.subheader("Data Preview")
            st.dataframe(df.head(5), use_container_width=True)
            
            # Upload button
            if st.button("Import Data"):
                self.import_csv_data(uploaded_file)
        
        st.divider()
        
        # Option to import from file path
        st.subheader("Import from File Path")
        file_path = st.text_input("Path to CSV file on server", "cleaned_data.csv")
        
        if st.button("Import from Path"):
            self.import_csv_from_path(file_path)
    
    def import_csv_data(self, file):
        """Import data from an uploaded CSV file."""
        if not st.session_state.api_key:
            st.error("Please enter an API key in the sidebar first.")
            return
        
        try:
            with st.spinner("Importing data..."):
                headers = {"X-API-Key": st.session_state.api_key}
                
                files = {"file": file}
                response = requests.post(
                    f"{st.session_state.api_url}/import/csv",
                    headers=headers,
                    files=files
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Import completed successfully!")
                    
                    stats = result.get("stats", {})
                    st.write(f"- Processed: {stats.get('processed', 0)} messages")
                    st.write(f"- Successful: {stats.get('successful', 0)} messages")
                    st.write(f"- Failed: {stats.get('failed', 0)} messages")
                    st.write(f"- Conversations: {stats.get('conversation_count', 0)}")
                else:
                    st.error(f"Failed to import data: {response.status_code}")
                    st.write(response.text)
        except Exception as e:
            st.error(f"Error importing data: {str(e)}")
    
    def import_csv_from_path(self, file_path):
        """Import data from a file path on the server."""
        if not st.session_state.api_key:
            st.error("Please enter an API key in the sidebar first.")
            return
        
        try:
            with st.spinner(f"Importing data from {file_path}..."):
                headers = {"X-API-Key": st.session_state.api_key}
                response = requests.post(
                    f"{st.session_state.api_url}/import/csv/file",
                    headers=headers,
                    json={"file_path": file_path}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Import completed successfully!")
                    
                    stats = result.get("stats", {})
                    st.write(f"- Processed: {stats.get('processed', 0)} messages")
                    st.write(f"- Successful: {stats.get('successful', 0)} messages")
                    st.write(f"- Failed: {stats.get('failed', 0)} messages")
                    st.write(f"- Conversations: {stats.get('conversation_count', 0)}")
                else:
                    st.error(f"Failed to import data: {response.status_code}")
                    st.write(response.text)
        except Exception as e:
            st.error(f"Error importing data: {str(e)}")
    
    def run(self):
        """Run the Streamlit application."""
        # Setup the sidebar
        self.setup_sidebar()
        
        # Display the appropriate page based on current_page
        if st.session_state.current_page == "dashboard":
            self.display_dashboard()
        elif st.session_state.current_page == "conversations":
            self.display_conversations_list()
        elif st.session_state.current_page == "conversation_detail":
            self.display_conversation_detail()
        elif st.session_state.current_page == "upload":
            self.display_upload_page()


# Run the app
if __name__ == "__main__":
    app = ChatSummarizerUI()
    app.run() 