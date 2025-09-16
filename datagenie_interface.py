#!/usr/bin/env python3
"""
DataGenie Interface - The Ultimate Data Chatbot
Eye-catching interface for instant data Q&A
"""

import streamlit as st
import pandas as pd
import json
from typing import Dict, List, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from datagenie_chatbot import DataGenieChatbot

def render_answer_box(title: str, answer_markdown: str, icon: str = "🧞‍♂️", data_used: dict = None) -> None:
    """Render a structured answer with tabs for Summary/Details/Data used."""
    st.markdown(f"#### {icon} {title}")
    
    # Split answer into summary and details
    lines = answer_markdown.splitlines()
    summary_lines = min(6, len(lines))
    summary = "\n".join(lines[:summary_lines])
    details = "\n".join(lines[summary_lines:]) if len(lines) > summary_lines else ""
    
    # Create tabs for different views
    tab_names = ["📋 Summary"]
    if details:
        tab_names.append("📄 Details")
    if data_used:
        tab_names.append("🔍 Data Used")
    
    tabs = st.tabs(tab_names)
    
    with tabs[0]:  # Summary tab
        st.markdown(summary)
    
    if details and len(tabs) > 1:
        with tabs[1]:  # Details tab
            st.markdown(details)
    
    if data_used and len(tabs) > 2:
        with tabs[2]:  # Data Used tab
            st.json(data_used)

def render_datagenie_interface():
    """Render the DataGenie chatbot interface"""
    
    # Eye-catching header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0; font-size: 2.5rem;">
            🧞‍♂️ DataGenie Chat
        </h1>
        <p style="color: white; text-align: center; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Ask any additional questions about your data - Your AI Data Oracle!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if data is available
    if 'uploaded_data' not in st.session_state or st.session_state.uploaded_data is None:
        st.warning("🚨 **No data uploaded yet!** Please upload your data first and check the Smart Dashboard for key insights.")
        
        st.info("💡 **Tip:** Upload your data and go to the **📊 Smart Dashboard** tab first to see the most important questions and answers automatically. Then come back here to ask any additional questions!")
        
        return
    
    # Compact guidance and Focus mode toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption("Tip: Review the 📊 Smart Dashboard first, then ask follow-up questions here.")
    with col2:
        focus_mode = st.checkbox("🎯 Focus Mode", help="Hide history and quick questions for cleaner interface")
    
    # Initialize DataGenie
    if 'datagenie' not in st.session_state:
        st.session_state.datagenie = DataGenieChatbot()
    
    datagenie = st.session_state.datagenie
    df = st.session_state.uploaded_data
    
    # Initialize session if not done
    if 'datagenie_initialized' not in st.session_state:
        with st.spinner("🧞‍♂️ DataGenie is analyzing your data..."):
            context = datagenie.initialize_session(df, "general")
            st.session_state.datagenie_initialized = True
            st.success("✅ DataGenie is ready! Ask me any additional questions about your data!")
    
    # Display data summary
    with st.expander("📋 Data Summary", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 Total Records", f"{len(df):,}")
        
        with col2:
            st.metric("📋 Columns", len(df.columns))
        
        with col3:
            st.metric("🧠 AI Ready", "✅")
    
    # Chat interface
    st.markdown("### 💬 Chat with DataGenie")
    
    # Display conversation history (hidden in focus mode)
    if not focus_mode and 'datagenie_history' in st.session_state and st.session_state.datagenie_history:
        st.markdown("#### 📜 Recent Conversation")
        history = st.session_state.datagenie_history
        recent = history[-5:]
        for i, message in enumerate(recent):
            if message['type'] == 'user':
                st.markdown(f"""
                <div style=\"background-color: #e3f2fd; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #2196f3;\">
                    <strong>👤 You:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                render_answer_box("DataGenie Answer", message['content'], icon="🧞‍♂️", data_used=message.get('data_used'))
                if 'confidence' in message:
                    confidence_color = "green" if message['confidence'] > 0.8 else "orange" if message['confidence'] > 0.6 else "red"
                    st.markdown(f"""
                    <div style=\"text-align: right; font-size: 0.8rem; color: {confidence_color};\">
                        Confidence: {message['confidence']:.1%}
                    </div>
                    """, unsafe_allow_html=True)

        if len(history) > len(recent):
            with st.expander("Show full history"):
                for i, message in enumerate(history[:-5]):
                    if message['type'] == 'user':
                        st.markdown(f"""
                        <div style=\"background-color: #e3f2fd; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #2196f3;\">
                            <strong>👤 You:</strong> {message['content']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        render_answer_box("DataGenie Answer", message['content'], icon="🧞‍♂️", data_used=message.get('data_used'))
    
    # Quick question buttons (hidden in focus mode)
    if not focus_mode:
        st.markdown("#### ⚡ Quick Questions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Data Overview", key="quick_overview_datagenie"):
                process_question("Tell me about my data", datagenie, df)
        
        with col2:
            if st.button("📈 Top Items", key="quick_top_datagenie"):
                process_question("What are my top products or items?", datagenie, df)
        
        with col3:
            if st.button("📅 Trends", key="quick_trends_datagenie"):
                process_question("Show me trends over time", datagenie, df)
        
        with col4:
            if st.button("🔍 Quality", key="quick_quality_datagenie"):
                process_question("How is my data quality?", datagenie, df)
    
    # Chat input
    st.markdown("#### 💭 Ask DataGenie Anything")
    
    # Text input for custom questions
    user_question = st.text_input(
        "Type your question here...",
        placeholder="e.g., 'What are my best-selling products?' or 'Show me customer patterns'",
        key="datagenie_input"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("🚀 Ask DataGenie", key="ask_datagenie_chat"):
            if user_question.strip():
                process_question(user_question, datagenie, df)
                st.rerun()
            else:
                st.warning("Please enter a question!")
    
    with col2:
        if st.button("🗑️ Clear Chat", key="clear_chat_datagenie"):
            datagenie.clear_conversation()
            st.rerun()
    
    # Sample questions dropdown
    sample_questions = [
        "What's the total revenue in my data?",
        "Which customers have the highest spending?",
        "Are there any trends in my sales data?",
        "What are the most common values in each column?",
        "How is my data quality?",
        "What patterns do you see in my data?",
        "Can you predict next month's performance?",
        "Compare different categories in my data"
    ]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_question = st.selectbox("💡 Sample Questions", ["Select a question..."] + sample_questions, key="sample_question_select")
    with col2:
        if st.button("🚀 Ask Selected", key="ask_selected_question") and selected_question != "Select a question...":
            process_question(selected_question, datagenie, df)
            st.rerun()
    
    # Data insights panel
    if 'datagenie_context' in st.session_state:
        with st.expander("🧠 DataGenie's Knowledge Base", expanded=False):
            context = st.session_state.datagenie_context
            
            st.markdown("**📊 Data Profile:**")
            st.json({
                "Business Type": context["metadata"]["business_type"],
                "Total Records": context["metadata"]["total_rows"],
                "Columns": context["metadata"]["total_columns"],
                "Quality Score": f"{context['data_quality']['quality_score']}/100"
            })
            
            st.markdown("**🔍 Quick Facts:**")
            for fact in context["quick_facts"][:5]:
                st.markdown(f"• {fact}")
            
            if context["business_insights"]["key_metrics"]:
                st.markdown("**📈 Key Metrics:**")
                for metric, value in context["business_insights"]["key_metrics"].items():
                    st.markdown(f"• {metric}: {value}")

def process_question(question: str, datagenie: DataGenieChatbot, df: pd.DataFrame):
    """Process a question and display the response"""
    
    with st.spinner("🧞‍♂️ DataGenie is thinking..."):
        try:
            response = datagenie.process_question(question, df)
            
            # Display the response in a styled box with data used
            render_answer_box("DataGenie Answer", response["answer"], icon="🧞‍♂️", data_used=response.get("data_used"))
            
            # Show confidence
            confidence_color = "green" if response["confidence"] > 0.8 else "orange" if response["confidence"] > 0.6 else "red"
            st.markdown(f"""
            <div style="text-align: right; font-size: 0.8rem; color: {confidence_color}; margin-top: 1rem;">
                Confidence: {response['confidence']:.1%}
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error processing question: {str(e)}")
            st.info("Please try rephrasing your question or check if your data has the required fields.")

def render_datagenie_sidebar():
    """Render DataGenie sidebar with additional features"""
    
    st.sidebar.markdown("### 🧞‍♂️ DataGenie")
    
    # Data upload reminder
    if 'uploaded_data' not in st.session_state or st.session_state.uploaded_data is None:
        st.sidebar.warning("Upload data to start chatting!")
        return
    
    # Quick stats
    df = st.session_state.uploaded_data
    st.sidebar.markdown("**📊 Your Data**")
    col_a, col_b = st.sidebar.columns(2)
    with col_a:
        st.metric("Records", f"{len(df):,}")
    with col_b:
        st.metric("Columns", len(df.columns))
    
    # DataGenie status
    if 'datagenie_initialized' in st.session_state:
        st.sidebar.success("✅ DataGenie Ready")
    else:
        st.sidebar.info("🔄 Initializing...")
    
    # Conversation stats
    if 'datagenie_history' in st.session_state:
        history = st.session_state.datagenie_history
        user_messages = len([m for m in history if m['type'] == 'user'])
        st.sidebar.metric("Questions Asked", user_messages)
    
    # Tips (collapsed)
    with st.sidebar.expander("💡 Tips"):
        st.markdown("""
        • Be specific in your questions
        • Ask about trends, comparisons, or patterns
        • Try the quick question buttons first
        """)
    
    # Export conversation
    if 'datagenie_history' in st.session_state and st.session_state.datagenie_history:
        if st.sidebar.button("📥 Export Chat", key="export_chat_datagenie"):
            export_conversation()

def export_conversation():
    """Export conversation history"""
    if 'datagenie_history' in st.session_state:
        history = st.session_state.datagenie_history
        
        # Create export data
        export_data = {
            "export_timestamp": pd.Timestamp.now().isoformat(),
            "conversation_history": history,
            "data_summary": {
                "total_records": len(st.session_state.uploaded_data),
                "total_columns": len(st.session_state.uploaded_data.columns),
                "columns": st.session_state.uploaded_data.columns.tolist()
            }
        }
        
        # Convert to JSON
        json_str = json.dumps(export_data, indent=2, default=str)
        
        # Download button
        st.download_button(
            label="📥 Download Chat History",
            data=json_str,
            file_name=f"datagenie_chat_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
