import streamlit as st
from typing import List
import time
from datetime import datetime
import asyncio
import os
from dotenv import load_dotenv
from logic.topic_extraction import TopicsExtractor
from logic.pdf_content_loading import extract_pdf_contents

# Page configuration
st.set_page_config(
    page_title="Topic Shift 📚",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for beautiful cards
st.markdown("""
    <style>
    /* Main styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Card styling */
    .topic-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #4CAF50;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .topic-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }
    
    .topic-header {
        display: flex;
        justify-content: space-between;
        align-items: start;
        margin-bottom: 16px;
    }
    
    .topic-title {
        font-size: 1.4em;
        font-weight: 700;
        color: #1a1a1a;
        margin: 0;
        flex: 1;
    }
    
    .importance-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
        white-space: nowrap;
    }
    
    .importance-high {
        background-color: #ffcdd2;
        color: #c62828;
        border: 1px solid #ef5350;
    }
    
    .importance-medium {
        background-color: #ffe0b2;
        color: #e65100;
        border: 1px solid #ffb74d;
    }
    
    .importance-low {
        background-color: #c8e6c9;
        color: #2e7d32;
        border: 1px solid #81c784;
    }
    
    .topic-goal {
        background-color: #f5f5f5;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-size: 0.95em;
        color: #555;
        border-left: 3px solid #2196F3;
    }
    
    .contents-section {
        margin-top: 16px;
    }
    
    .contents-title {
        font-size: 0.9em;
        font-weight: 600;
        color: #333;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .content-item {
        background-color: #fafafa;
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 6px;
        border-left: 3px solid #2196F3;
        font-size: 0.95em;
        color: #444;
    }
    
    .content-item:last-child {
        margin-bottom: 0;
    }
    
    .cards-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
        gap: 24px;
        margin-top: 24px;
    }
    
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #999;
    }
    
    .stats-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("# 📚")
with col2:
    st.title("Topic Shift")
    st.markdown("*Extract topics from your PDF documents with AI*")

st.markdown("---")

# Initialize session state
if "topics" not in st.session_state:
    st.session_state.topics = None
if "processing" not in st.session_state:
    st.session_state.processing = False
if "error" not in st.session_state:
    st.session_state.error = None
if "file_name" not in st.session_state:
    st.session_state.file_name = None
if "extractor" not in st.session_state:
    load_dotenv()
    st.session_state.extractor = TopicsExtractor()

# Main content
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📤 Upload & Configure")

    # Description input
    description = st.text_area(
        "📝 Document Description",
        placeholder="e.g., Machine Learning fundamentals lecture",
        height=100,
        help="Provide context about the PDF to improve topic extraction",
    )

    # File upload
    uploaded_file = st.file_uploader(
        "📎 Choose a PDF file", type=["pdf"], label_visibility="collapsed"
    )

    # Process button
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        process_btn = st.button(
            "🚀 Extract Topics",
            use_container_width=True,
            disabled=uploaded_file is None or not description,
            type="primary",
        )

    with col_btn2:
        if st.session_state.topics:
            clear_btn = st.button("🗑️ Clear", use_container_width=True, key="clear_btn")
            if clear_btn:
                st.session_state.topics = None
                st.session_state.error = None
                st.session_state.file_name = None
                st.rerun()

with col2:
    st.subheader("📋 Results Preview")
    if st.session_state.topics:
        st.markdown(f"✅ **Document:** {st.session_state.file_name}")
        st.markdown(f"📊 **Topics Found:** {len(st.session_state.topics)}")

        # Calculate statistics
        high = sum(1 for t in st.session_state.topics if t.get("importance") == "high")
        medium = sum(
            1 for t in st.session_state.topics if t.get("importance") == "medium"
        )
        low = sum(1 for t in st.session_state.topics if t.get("importance") == "low")

        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("🔴 High", high)
        with col_stat2:
            st.metric("🟡 Medium", medium)
        with col_stat3:
            st.metric("🟢 Low", low)
    else:
        st.markdown(
            '<div class="empty-state">Upload a PDF and click Extract to see results</div>',
            unsafe_allow_html=True,
        )

# Process the file when button is clicked
if process_btn and uploaded_file and description:
    st.session_state.processing = True
    st.session_state.error = None

    # Create progress area
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    file_location = f"temp_{uploaded_file.name}"

    try:
        with progress_placeholder.container():
            progress_bar = st.progress(0)

        with status_placeholder.container():
            st.info("🔄 Loading PDF...")

        # Save uploaded file temporarily
        with open(file_location, "wb") as f:
            f.write(uploaded_file.getbuffer())

        progress_bar.progress(20)

        with status_placeholder.container():
            st.info("� Extracting topics from PDF...")

        # Extract topics directly using the logic
        extractor: TopicsExtractor = st.session_state.extractor
        topics = asyncio.run(extractor.extract_topics(file_location, description=description))

        # Convert topics to dict format for display
        topics_dict = [
            {
                "id": topic.id,
                "title": topic.title,
                "importance": topic.importance,
                "contents": topic.contents,
                "goal": topic.goal,
            }
            for topic in topics
        ]

        progress_bar.progress(100)
        st.session_state.topics = topics_dict
        st.session_state.file_name = uploaded_file.name

        with status_placeholder.container():
            st.success("✅ Topics extracted successfully!")

        time.sleep(1)
        progress_placeholder.empty()
        status_placeholder.empty()

        # Clean up the temporary file
        if os.path.exists(file_location):
            os.remove(file_location)

        st.rerun()

    except Exception as e:
        st.session_state.error = str(e)
        progress_placeholder.empty()
        with status_placeholder.container():
            st.error(f"❌ Error: {str(e)}")

        # Clean up on error
        if os.path.exists(file_location):
            os.remove(file_location)

    finally:
        st.session_state.processing = False

# Display results
if st.session_state.topics:
    st.markdown("---")
    
    # Header with statistics
    col_header1, col_header2 = st.columns([2, 1])
    with col_header1:
        st.subheader("📚 Extracted Topics")
    
    with col_header2:
        # Sorting options
        sort_by = st.selectbox(
            "Sort by:",
            options=["importance", "alphabetical"],
            key="sort_select",
            label_visibility="collapsed"
        )
    
    # Sort topics
    topics_to_display = st.session_state.topics.copy()
    if sort_by == "importance":
        importance_order = {"high": 0, "medium": 1, "low": 2}
        topics_to_display.sort(
            key=lambda x: importance_order.get(x.get("importance", "low"), 3)
        )
    elif sort_by == "alphabetical":
        topics_to_display.sort(key=lambda x: x.get("title", "").lower())
    
    # Display topics as cards in a grid
    cols = st.columns(2)
    for idx, topic in enumerate(topics_to_display):
        with cols[idx % 2]:
            importance = topic.get("importance", "low")
            title = topic.get("title", "Untitled")
            goal = topic.get("goal", "No goal specified")
            contents = topic.get("contents", [])
            
            # Build the card HTML
            card_html = f"""
            <div class="topic-card">
                <div class="topic-header">
                    <div class="topic-title">{title}</div>
                    <span class="importance-badge importance-{importance}">
                        {importance.upper()}
                    </span>
                </div>
                <div class="topic-goal">
                    🎯 {goal}
                </div>
                <div class="contents-section">
                    <div class="contents-title">📝 Key Points</div>
            """
            
            if contents:
                for content in contents:
                    card_html += f'<div class="content-item">• {content}</div>'
            else:
                card_html += '<div class="content-item" style="color: #999;">No contents available</div>'
            
            card_html += """
                </div>
            </div>
            """
            
            st.markdown(card_html, unsafe_allow_html=True)

# Sidebar information
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.markdown(
        """
    **Topic Shift** extracts topics from PDF documents using AI.
    
    **Features:**
    - 📤 Drag & drop PDF upload
    - 🤖 AI-powered topic extraction
    - 📊 Importance ranking
    - 📝 Content summaries
    
    **How to use:**
    1. Describe the document
    2. Upload a PDF file
    3. Click Extract Topics
    4. Review the results
    """
    )

    st.markdown("---")
    st.markdown("### 🔧 Configuration")
    st.markdown("**Mode:** Direct processing (no API server required)")

    st.markdown("---")
    st.markdown("### 📚 Made with Streamlit")
    st.markdown("[View Documentation](https://streamlit.io)")
