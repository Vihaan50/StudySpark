import streamlit as st
import time
import fitz  # PyMuPDF
from groq import Groq
import re
from datetime import datetime

# -----------------------
# PAGE SETTINGS
# -----------------------
st.set_page_config(
    page_title="StudyBot - AI Study Assistant",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session state for chat
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0
if 'chat_robot_visible' not in st.session_state:
    st.session_state.chat_robot_visible = True

# -----------------------
# CUSTOM CSS (INCLUDING ROBOTS)
# -----------------------
st.markdown("""
    <style>
    /* Main Layout */
    .main {
        padding-top: 2rem;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        padding: 15px;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        background-color: #45a049;
    }
    
    /* Difficulty Level Boxes */
    .difficulty-easy {
        background-color: #90EE90;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        color: #006400;
        font-weight: bold;
    }
    
    .difficulty-medium {
        background-color: #FFD700;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        color: #8B4513;
        font-weight: bold;
    }
    
    .difficulty-hard {
        background-color: #FF6B6B;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        color: #8B0000;
        font-weight: bold;
    }
    
    /* ============================================
       ROBOT 1 - LARGE STUDY BUDDY (SKY BLUE)
       ============================================ */
    
    .robot-container {
        position: fixed;
        right: 30px;
        top: 120px;
        z-index: 1000;
        transition: opacity 0.5s ease, transform 0.5s ease;
    }
    
    .robot-container.hidden {
        opacity: 0;
        transform: translateX(100px);
        pointer-events: none;
    }
    
    .robot-large {
        width: 250px;
        height: 350px;
        position: relative;
    }
    
    /* Head */
    .robot-large .head {
        width: 120px;
        height: 120px;
        background: linear-gradient(135deg, #87CEEB, #4682B4);
        border-radius: 25px;
        position: absolute;
        left: 65px;
        top: 0;
        animation: bob 2s ease-in-out infinite;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Antenna */
    .robot-large .antenna {
        width: 5px;
        height: 35px;
        background: #4682B4;
        position: absolute;
        left: 57.5px;
        top: -35px;
    }
    
    .robot-large .antenna-tip {
        width: 15px;
        height: 15px;
        background: #FFD700;
        border-radius: 50%;
        position: absolute;
        left: -5px;
        top: -7.5px;
        animation: blink 1.5s ease-in-out infinite;
        box-shadow: 0 0 10px #FFD700;
    }
    
    /* Eyes */
    .robot-large .eye {
        width: 25px;
        height: 25px;
        background: white;
        border-radius: 50%;
        position: absolute;
        top: 35px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .robot-large .eye-left { left: 25px; }
    .robot-large .eye-right { right: 25px; }
    
    .robot-large .pupil {
        width: 10px;
        height: 10px;
        background: #333;
        border-radius: 50%;
        position: absolute;
        top: 7.5px;
        left: 7.5px;
        animation: look 3s ease-in-out infinite;
    }
    
    /* Mouth */
    .robot-large .mouth {
        width: 50px;
        height: 25px;
        border: 3px solid white;
        border-top: none;
        border-radius: 0 0 25px 25px;
        position: absolute;
        bottom: 25px;
        left: 35px;
    }
    
    /* Body */
    .robot-large .body {
        width: 145px;
        height: 130px;
        background: linear-gradient(135deg, #87CEEB, #4682B4);
        border-radius: 20px;
        position: absolute;
        left: 52.5px;
        top: 145px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Book */
    .robot-large .book {
        width: 50px;
        height: 37px;
        background: white;
        border: 2.5px solid #4682B4;
        border-radius: 4px;
        position: absolute;
        left: 47.5px;
        top: 45px;
    }
    
    .robot-large .book-line {
        width: 37.5px;
        height: 2.5px;
        background: #4682B4;
        position: absolute;
        left: 6.25px;
    }
    
    .robot-large .book-line:nth-child(1) { top: 10px; }
    .robot-large .book-line:nth-child(2) { top: 17.5px; }
    .robot-large .book-line:nth-child(3) { top: 25px; }
    
    /* Robotic Arms */
    .robot-large .arm {
        width: 18px;
        height: 85px;
        background: linear-gradient(135deg, #87CEEB, #4682B4);
        border-radius: 9px;
        position: absolute;
        top: 165px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.2);
    }
    
    .robot-large .arm-left {
        left: 25px;
        transform-origin: top center;
        animation: wave-once 2.5s ease-in-out 0.5s 1;
    }
    
    .robot-large .arm-right {
        right: 25px;
        transform-origin: top center;
    }
    
    .robot-large .hand {
        width: 22px;
        height: 22px;
        background: #4682B4;
        border-radius: 50%;
        position: absolute;
        bottom: -4px;
        left: -2px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .robot-large .finger {
        width: 5px;
        height: 10px;
        background: #4682B4;
        border-radius: 2.5px;
        position: absolute;
    }
    
    .robot-large .finger1 { left: 2.5px; top: -7px; }
    .robot-large .finger2 { left: 8.5px; top: -8.5px; }
    .robot-large .finger3 { left: 14.5px; top: -7px; }
    
    /* Thinking Animation */
    .robot-large .thought-bubble {
        width: 12px;
        height: 12px;
        background: white;
        border-radius: 50%;
        position: absolute;
        opacity: 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .robot-large.thinking .thought-bubble {
        animation: think 2s ease-in-out infinite;
    }
    
    .robot-large .thought1 {
        left: 130px;
        top: 25px;
        animation-delay: 0s;
    }
    
    .robot-large .thought2 {
        left: 145px;
        top: 12px;
        width: 16px;
        height: 16px;
        animation-delay: 0.3s;
    }
    
    .robot-large .thought3 {
        left: 170px;
        top: 4px;
        width: 40px;
        height: 40px;
        animation-delay: 0.6s;
    }
    
    .robot-large .thought-content {
        position: absolute;
        left: 175px;
        top: 9px;
        font-size: 24px;
        animation: think 2s ease-in-out infinite;
        animation-delay: 0.6s;
        opacity: 0;
    }
    
    /* ============================================
       ROBOT ANIMATIONS
       ============================================ */
    
    @keyframes bob {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-12px); }
    }
    
    @keyframes wave {
        0%, 100% { transform: rotate(0deg); }
        20% { transform: rotate(-30deg); }
        40% { transform: rotate(-10deg); }
        60% { transform: rotate(-25deg); }
        80% { transform: rotate(-5deg); }
    }
    
    @keyframes wave-once {
        0%, 100% { transform: rotate(0deg); }
        20% { transform: rotate(-30deg); }
        40% { transform: rotate(-10deg); }
        60% { transform: rotate(-25deg); }
        80% { transform: rotate(-5deg); }
    }
    
    @keyframes blink {
        0%, 90%, 100% { opacity: 1; }
        95% { opacity: 0.3; }
    }
    
    @keyframes look {
        0%, 100% { transform: translate(0, 0); }
        25% { transform: translate(3px, 0); }
        50% { transform: translate(0, 3px); }
        75% { transform: translate(-3px, 0); }
    }
    
    @keyframes think {
        0%, 100% { opacity: 0; transform: translateY(8px); }
        50% { opacity: 1; transform: translateY(0); }
    }
    
    </style>
""", unsafe_allow_html=True)

# -----------------------
# MAIN ROBOT (appears on page load)
# -----------------------
st.markdown("""
    <div class="robot-container" id="mainRobotContainer">
        <div class="robot-large" id="mainRobot">
            <div class="head">
                <div class="antenna">
                    <div class="antenna-tip"></div>
                </div>
                <div class="eye eye-left">
                    <div class="pupil"></div>
                </div>
                <div class="eye eye-right">
                    <div class="pupil"></div>
                </div>
                <div class="mouth"></div>
            </div>
            <div class="body">
                <div class="book">
                    <div class="book-line"></div>
                    <div class="book-line"></div>
                    <div class="book-line"></div>
                </div>
            </div>
            <div class="arm arm-left">
                <div class="hand">
                    <div class="finger finger1"></div>
                    <div class="finger finger2"></div>
                    <div class="finger finger3"></div>
                </div>
            </div>
            <div class="arm arm-right">
                <div class="hand">
                    <div class="finger finger1"></div>
                    <div class="finger finger2"></div>
                    <div class="finger finger3"></div>
                </div>
            </div>
            <div class="thought-bubble thought1"></div>
            <div class="thought-bubble thought2"></div>
            <div class="thought-bubble thought3"></div>
            <div class="thought-content">💡</div>
        </div>
    </div>
    
    <script>
    // Scroll detection to hide/show robot
    window.addEventListener('scroll', function() {
        const robot = document.getElementById('mainRobotContainer');
        if (robot) {
            if (window.scrollY > 300) {
                robot.classList.add('hidden');
            } else {
                robot.classList.remove('hidden');
            }
        }
    });
    </script>
""", unsafe_allow_html=True)

# -----------------------
# HEADING
# -----------------------
st.markdown(
    "<h1 style='text-align: center;'>Hi, tell me what's on the agenda today?</h1>",
    unsafe_allow_html=True
)
st.write("")

# -----------------------
# SIMULATED FADE-IN
# -----------------------
with st.spinner("Getting things ready..."):
    time.sleep(1)

# -----------------------
# INTRODUCTION
# -----------------------
intro_text = """
Welcome! This app is designed to help you study smarter and faster.
You can upload a PDF from **any subject** — history, civics, geography, economics, or even science — and the app will carefully read the content and generate clear, well-structured questions and answers for you.
Whether you need very short answers, short answers, or detailed long answers, everything is written in full sentences and easy language. The goal is to save your time, reduce stress, and make revision simpler and more effective.
"""
st.markdown(intro_text)
st.write("")
st.write("")

# -----------------------
# UPLOAD INSTRUCTION
# -----------------------
st.markdown("### 📄 Click the button below to upload your PDF file")

# -----------------------
# PDF UPLOAD BUTTON
# -----------------------
uploaded_file = st.file_uploader(
    "Upload ONE PDF file (maximum 50 pages)",
    type=["pdf"],
    accept_multiple_files=False
)
st.write("")

# -----------------------
# HELPER FUNCTIONS
# -----------------------

def sanitize_custom_request(text):
    """Sanitize user input to prevent prompt injection."""
    if not text or not text.strip():
        return ""
    
    suspicious_phrases = [
        "ignore previous", "ignore all", "disregard",
        "forget everything", "new instructions", "system prompt", "you are now"
    ]
    
    text_lower = text.lower()
    for phrase in suspicious_phrases:
        if phrase in text_lower:
            return ""
    
    return text.strip()[:500]


def parse_qa_output(text):
    """Parse AI output into structured Q&A pairs."""
    if not text or not text.strip():
        return []
    
    pages = []
    current_page = None
    current_section = None
    current_question = None
    current_answer = None
    
    lines = text.split('\n')
    
    for line in lines:
        stripped_line = line.strip()
        
        if not stripped_line and not current_question and not current_answer:
            continue
        
        if re.match(r'^PAGE\s*\d+', stripped_line, re.IGNORECASE):
            if current_question and current_answer and current_section:
                current_section['qa_pairs'].append({
                    'question': current_question.strip(),
                    'answer': current_answer.strip()
                })
            if current_section and current_page:
                current_page['sections'].append(current_section)
            if current_page:
                pages.append(current_page)
            
            current_page = {
                'title': stripped_line,
                'sections': []
            }
            current_section = None
            current_question = None
            current_answer = None
        
        elif re.search(r'(VERY\s*SHORT|SHORT|LONG)\s*ANSWER', stripped_line, re.IGNORECASE):
            if current_question and current_answer and current_section:
                current_section['qa_pairs'].append({
                    'question': current_question.strip(),
                    'answer': current_answer.strip()
                })
            if current_section and current_page:
                current_page['sections'].append(current_section)
            
            current_section = {
                'title': stripped_line,
                'qa_pairs': []
            }
            current_question = None
            current_answer = None
        
        elif re.match(r'^Q\s*\d+[\)\.\:]', stripped_line, re.IGNORECASE):
            if current_question and current_answer and current_section:
                current_section['qa_pairs'].append({
                    'question': current_question.strip(),
                    'answer': current_answer.strip()
                })
            
            current_question = stripped_line
            current_answer = None
        
        elif re.match(r'^A\s*\d+[\)\.\:]', stripped_line, re.IGNORECASE):
            current_answer = stripped_line
        
        else:
            if current_answer is not None:
                if stripped_line:
                    current_answer += "\n" + stripped_line
                else:
                    current_answer += "\n"
            elif current_question is not None:
                if stripped_line:
                    current_question += " " + stripped_line
    
    if current_question and current_answer and current_section:
        current_section['qa_pairs'].append({
            'question': current_question.strip(),
            'answer': current_answer.strip()
        })
    
    if current_section and current_page:
        current_page['sections'].append(current_section)
    
    if current_page:
        pages.append(current_page)
    
    return pages


# -----------------------
# CUSTOMIZATION OPTIONS
# -----------------------
if uploaded_file is not None:
    st.markdown("---")
    st.markdown("## 🎯 Customize Your Study Material")
    st.write("")
    
    # A) QUESTION TYPE SELECTOR
    st.markdown("### 1. Choose Question Type")
    question_type = st.selectbox(
        "Select the type of questions you want:",
        ["Open-Ended Questions & Answers", "Multiple Choice Questions (MCQs)", "True or False Questions"],
        key="question_type"
    )
    st.write("")
    st.write("")
    
    # B) DIFFICULTY LEVEL SELECTOR
    st.markdown("### 2. Select Difficulty Level")
    
    difficulty = st.radio(
        "Choose difficulty:",
        ["Easy", "Medium", "Hard"],
        horizontal=True,
        key="difficulty"
    )
    
    if difficulty == "Easy":
        st.markdown('<div class="difficulty-easy">✓ Easy Mode Selected - Simple vocabulary, straightforward questions</div>', unsafe_allow_html=True)
    elif difficulty == "Medium":
        st.markdown('<div class="difficulty-medium">✓ Medium Mode Selected - Standard difficulty for Class 9</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="difficulty-hard">✓ Hard Mode Selected - Analytical questions requiring deeper understanding</div>', unsafe_allow_html=True)
    
    st.write("")
    st.write("")

# C) CUSTOM QUESTION COUNT
    st.markdown("### 3. Custom Question Count")
    
    # Check question type and show appropriate options
    if question_type in ["Multiple Choice Questions (MCQs)", "True or False Questions"]:
        st.write("Set how many questions you want per page:")
        questions_per_page = st.number_input(
            "Questions per page",
            min_value=1,
            max_value=8,
            value=4,
            key="questions_per_page"
        )
        # Set defaults for very_short, short, long (won't be used but needed for code)
        very_short_count = 0
        short_count = 0
        long_count = 0
    else:
        st.write("Set how many questions you want for each type (per page):")
        col1, col2, col3 = st.columns(3)
        with col1:
            very_short_count = st.number_input("Very Short", min_value=1, max_value=3, value=2, key="very_short")
        with col2:
            short_count = st.number_input("Short", min_value=1, max_value=3, value=2, key="short")
        with col3:
            long_count = st.number_input("Long", min_value=1, max_value=3, value=2, key="long")
        # Set default for questions_per_page (won't be used but needed for code)
        questions_per_page = 0
    
    st.write("")
    st.write("")
    
    # D) QUIZ MODE TOGGLE
    st.markdown("### 4. Quiz Mode")
    quiz_mode = st.checkbox("Enable Quiz Mode?", key="quiz_mode")
    
    st.markdown("""
        <p style='font-size: 14px; color: #666; margin-top: 5px; line-height: 1.6;'>
        Quiz Mode is a toggle-able setting that is similar to the normal Question and Answers generation, but with a little change. 
        After each question and answer generated, just below the question, the user will find a small button labelled "Reveal Answer". 
        As the name suggests, this will reveal the answer for the question. This mode lets you quiz yourself: look at the question, 
        try to answer it yourself, then reveal the answer to verify if you were correct or not. When turned on, this setting provides 
        the extra "Reveal Answer" option, and when off, it generates the questions normally so you can revise.
        </p>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    # E) CUSTOM REQUESTS
    st.markdown("### 5. Custom Requests (Optional)")
    custom_request = st.text_area(
        "Any specific requests?",
        placeholder="e.g., 'Focus on dates and events' or 'Include map-related questions' or 'Emphasize important definitions'",
        height=100,
        key="custom_request"
    )
    
    st.write("")
    st.write("")
    st.markdown("---")

# ====================
    # CHUNK 3 - GENERATE BUTTON & PROCESSING
    # ====================
    
    # F) GENERATE BUTTON
    if st.button("🚀 Generate Questions & Answers", key="generate_btn"):
        
        # Validate inputs based on question type
        if question_type in ["Multiple Choice Questions (MCQs)", "True or False Questions"]:
            if questions_per_page == 0:
                st.error("❌ Please select at least one question per page.")
                st.stop()
        else:
            if very_short_count + short_count + long_count == 0:
                st.error("❌ Please select at least one question for any category.")
                st.stop()
        
        # Trigger thinking animation on robot
        st.markdown("""
            <script>
            const robot = document.getElementById('mainRobot');
            if (robot) {
                robot.classList.add('thinking');
            }
            </script>
        """, unsafe_allow_html=True)
        
        with st.spinner("Reading your PDF and preparing answers..."):
            doc = None
            start_time = time.time()
            
            try:
                # Initialize Groq client
                api_key = "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"
                client = Groq(api_key=api_key)
                
                # Read PDF with error handling
                try:
                    pdf_bytes = uploaded_file.read()
                    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                except Exception as pdf_error:
                    st.error(f"❌ Failed to read PDF file: {str(pdf_error)}")
                    st.info("Please ensure the file is a valid PDF and try again.")
                    st.stop()
                
                total_pages = min(doc.page_count, 50)
                
                if total_pages == 0:
                    st.error("❌ The PDF appears to be empty or unreadable.")
                    st.stop()
                
                st.info(f"📚 Total pages to process: {total_pages}")
                
                # Progress indicators
                progress_bar = st.progress(0)
                progress_text = st.empty()
                time_estimate = st.empty()
                
                # Storage for results
                all_parsed_pages = []
                
                # Sanitize custom request
                safe_custom_request = sanitize_custom_request(custom_request)
                if custom_request and not safe_custom_request:
                    st.warning("⚠️ Your custom request contained suspicious content and was ignored for security.")
                
                # Chunking settings
                chunk_size = 3
                total_chunks = (total_pages + chunk_size - 1) // chunk_size
                chunk_times = []
                
                # Process PDF in chunks
                for chunk_idx, chunk_start in enumerate(range(0, total_pages, chunk_size)):
                    chunk_end = min(chunk_start + chunk_size, total_pages)
                    chunk_start_time = time.time()
                    
                    progress_text.text(f"Processing pages {chunk_start + 1} to {chunk_end}...")
                    
                    # Calculate and display estimated time remaining
                    if chunk_idx > 0 and chunk_times:
                        avg_time_per_chunk = sum(chunk_times) / len(chunk_times)
                        chunks_remaining = total_chunks - chunk_idx
                        estimated_seconds = int(avg_time_per_chunk * chunks_remaining)
                        
                        if estimated_seconds > 60:
                            mins = estimated_seconds // 60
                            secs = estimated_seconds % 60
                            time_estimate.info(f"⏱️ Estimated time remaining: ~{mins}m {secs}s")
                        else:
                            time_estimate.info(f"⏱️ Estimated time remaining: ~{estimated_seconds} seconds")
                    
                    # Collect text from pages in this chunk
                    chunk_text = ""
                    page_numbers = []
                    
                    for page_number in range(chunk_start, chunk_end):
                        try:
                            page = doc[page_number]
                            page_text = page.get_text()
                            
                            if not page_text or not page_text.strip():
                                page_text = "[This page appears to be blank or contains only images]"
                            
                            page_numbers.append(page_number + 1)
                            chunk_text += f"\n\n--- PAGE {page_number + 1} ---\n{page_text}"
                        except Exception as page_error:
                            st.warning(f"⚠️ Could not read page {page_number + 1}: {str(page_error)}")
                            continue
                    
                    # Skip if no readable text
                    if not chunk_text.strip() or chunk_text.count("[This page appears to be blank") == len(page_numbers):
                        st.warning(f"⚠️ Pages {page_numbers[0]}-{page_numbers[-1]} contain no readable text. Skipping...")
                        progress_bar.progress(chunk_end / total_pages)
                        continue
                    
                    # Build difficulty instruction
                    if difficulty == "Easy":
                        difficulty_instruction = "Use simple vocabulary suitable for Class 9, straightforward questions that are easy to understand."
                    elif difficulty == "Medium":
                        difficulty_instruction = "Standard difficulty appropriate for Class 9 students."
                    else:
                        difficulty_instruction = "Analytical questions requiring deeper understanding and critical thinking, suitable for advanced Class 9 students."
                    
                    # Build question type instruction
                    if question_type == "Multiple Choice Questions (MCQs)":
                        type_instruction = f"""
Generate {questions_per_page} Multiple Choice Questions (MCQs) with 4 options labeled A), B), C), D).
Format EXACTLY like this:

Q1) [Question text]?
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]

A1) Correct Answer: [Letter] - [Full explanation in sentences]

Continue for Q2), Q3), etc. up to Q{questions_per_page}).
"""
                    elif question_type == "True or False Questions":
                        type_instruction = f"""
Generate {questions_per_page} True or False questions.
Format EXACTLY like this:

Q1) [Statement]. True or False?

A1) [True/False] - [Full explanation why this is the correct answer]

Continue for Q2), Q3), etc. up to Q{questions_per_page}).
"""
                    else:
                        type_instruction = """
Generate open-ended questions that require detailed answers.

VERY SHORT ANSWERS should be 1-2 sentences providing a brief definition or explanation.
Example:
Q) What was the Old Regime in France?
A) The term Old Regime is usually used to describe the society and institutions of France before 1789.

SHORT ANSWERS should be 2-4 sentences explaining a concept with some elaboration.
Example:
Q) What were the natural and inalienable rights?
A) Rights such as the right to life, freedom of speech, freedom of opinion, equality before law, were established as 'natural and inalienable' rights, that is, they belonged to each human being by birth and could not be taken away. It was the duty of the state to protect each citizen's natural rights.

LONG ANSWERS should use numbered points (1, 2, 3, 4, 5...) where each point is a complete sentence or short paragraph. Points should flow logically and build upon each other.
Example:
Q) Describe the subsistence crisis in France.
A) 1. The population of France rose from about 23 million in 1715 to 28 million in 1789. This led to a rapid increase in the demand for foodgrains.
2. Production of grains could not keep pace with the demand. So the price of bread which was the staple diet of the majority rose rapidly.
3. Most workers were employed as labourers in workshops whose owner fixed their wages. But wages did not keep pace with the rise in prices.
4. So the gap between the poor and the rich widened. Things became worse whenever drought or hail reduced the harvest.
5. This led to a subsistence crisis, something that occurred frequently in France during the Old Regime.

Format EXACTLY like this:
Q1) [Question text]?

A1) [Answer following the style above based on answer length]
"""
                    
                    # Add custom instruction if provided
                    custom_instruction = ""
                    if safe_custom_request:
                        custom_instruction = f"\n\nAdditional instructions from user: {safe_custom_request}"
                    
                    # Create the full prompt
                    prompt_text = f"""
Generate questions and answers from the following pages of a textbook:

{chunk_text}

Instructions:
"""
                    
                    # Add appropriate instructions based on question type
                    if question_type in ["Multiple Choice Questions (MCQs)", "True or False Questions"]:
                        prompt_text += f"- For EACH page, provide exactly {questions_per_page} question(s) with their answers.\n"
                        prompt_text += "- Label each page clearly with 'PAGE X' at the top.\n"
                    else:
                        prompt_text += f"- For EACH page, provide exactly {very_short_count} very short question(s), {short_count} short question(s), and {long_count} long question(s) with their answers.\n"
                        prompt_text += "- Label each page clearly with 'PAGE X' at the top.\n"
                        prompt_text += """- Organize questions under these EXACT headings:
  
  VERY SHORT ANSWERS
  [Questions and answers for very short type]
  
  SHORT ANSWERS
  [Questions and answers for short type]
  
  LONG ANSWERS
  [Questions and answers for long type]

"""
                    
                    prompt_text += f"""
{type_instruction}

- Number questions sequentially: Q1), Q2), Q3), etc.
- Number answers to match: A1), A2), A3), etc.
- {difficulty_instruction}
- Use simple, clear language suitable for Class 9 students.
- Do NOT use markdown formatting like ** or bold - just plain text.
- Maintain consistent formatting throughout.
{custom_instruction}
"""
                    
                    # API call with retry logic
                    max_retries = 3
                    retry_count = 0
                    output_text = None
                    
                    while retry_count < max_retries:
                        try:
                            response = client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[{"role": "user", "content": prompt_text}],
                                temperature=0.7,
                                max_tokens=8000
                            )
                            
                            output_text = response.choices[0].message.content
                            break
                            
                        except Exception as api_error:
                            error_str = str(api_error)
                            if "rate_limit" in error_str.lower() or "429" in error_str:
                                retry_count += 1
                                if retry_count < max_retries:
                                    wait_time = 10
                                    
                                    warning_placeholder = st.empty()
                                    for remaining in range(wait_time, 0, -1):
                                        warning_placeholder.warning(f"⏳ Rate limit hit. Retrying in {remaining} seconds... (Attempt {retry_count}/{max_retries})")
                                        time.sleep(1)
                                    warning_placeholder.empty()
                                else:
                                    st.error("❌ Rate limit exceeded after multiple retries.")
                                    st.info("💡 Tip: Try again in a few minutes.")
                                    raise Exception("Rate limit exhausted")
                            elif "API key" in error_str or "authentication" in error_str.lower():
                                st.error("❌ API authentication failed. Please check your API key.")
                                raise Exception("Invalid API key")
                            else:
                                st.error(f"❌ AI service error: {str(api_error)}")
                                raise api_error
                    
                    # Check if we got valid output
                    if not output_text or not output_text.strip():
                        st.warning(f"⚠️ No content generated for pages {page_numbers[0]}-{page_numbers[-1]}. Skipping...")
                        progress_bar.progress(chunk_end / total_pages)
                        continue
                    
                    # Parse the output
                    try:
                        parsed_pages = parse_qa_output(output_text)
                        if parsed_pages:
                            all_parsed_pages.extend(parsed_pages)
                        else:
                            st.warning(f"⚠️ Could not parse output for pages {page_numbers[0]}-{page_numbers[-1]}.")
                    except Exception as parse_error:
                        st.warning(f"⚠️ Error parsing pages {page_numbers[0]}-{page_numbers[-1]}: {str(parse_error)}")
                    
                    # Update progress
                    progress_bar.progress(chunk_end / total_pages)
                    
                    # Track chunk time for estimation
                    chunk_time = time.time() - chunk_start_time
                    chunk_times.append(chunk_time)
                    
                    # Delay between chunks
                    if chunk_end < total_pages:
                        time.sleep(2)
                
                # Clear progress indicators
                progress_bar.empty()
                progress_text.empty()
                time_estimate.empty()
                
                # Stop thinking animation
                st.markdown("""
                    <script>
                    const robot = document.getElementById('mainRobot');
                    if (robot) {
                        robot.classList.remove('thinking');
                    }
                    </script>
                """, unsafe_allow_html=True)
                
                # Check if we have any content
                if not all_parsed_pages:
                    st.error("❌ Failed to generate any content from the PDF.")
                    st.info("💡 This could happen if:")
                    st.info("• The PDF contains only images (scanned documents)")
                    st.info("• The text couldn't be extracted properly")
                    st.info("• The AI service encountered repeated errors")
                    st.info("\nPlease try with a different PDF or check if your PDF has selectable text.")
                else:
                    # Calculate total time and question count
                    total_time = time.time() - start_time
                    total_questions = sum(len(section['qa_pairs']) for page in all_parsed_pages for section in page['sections'])
                    
                    # Display success
                    st.success(f"✅ Successfully processed {total_pages} pages in {int(total_time)} seconds!")
                    st.balloons()
                    
                    st.write("")
                    st.write("")
                    st.markdown("---")
                    
                    # Progress Statistics Box
                    st.markdown(f"""
                        <div class="stats-box">
                            Generated {total_questions} questions from {total_pages} pages
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("## 📖 Your Study Material")
                    st.write("")
                    
                    # ====================
                    # CHUNK 3 ENDS HERE
                    # CHUNK 4 WILL HAVE: Display functions, Download, Chat, Feedback
                    # ====================
            
            except Exception as e:
                error_message = str(e)
                
                # User-friendly error messages
                if "Rate limit" in error_message or "rate_limit" in error_message.lower():
                    st.error("❌ You've hit the API rate limit.")
                    st.info("💡 Please wait a few minutes and try again.")
                elif "API key" in error_message or "authentication" in error_message.lower():
                    st.error("❌ There's an issue with the API authentication.")
                    st.info("💡 Please contact the developer to update the API key.")
                elif "PDF" in error_message or "file" in error_message.lower():
                    st.error("❌ There was a problem reading your PDF file.")
                    st.info("💡 Please ensure your file is a valid PDF and try again.")
                else:
                    st.error(f"❌ An unexpected error occurred: {error_message}")
                    st.info("💡 Please try again. If the problem persists, try with a different PDF or contact support.")
            
            finally:
                # Always close the PDF document to free resources
                if doc is not None:
                    try:
                        doc.close()
                    except:
                        pass  # Ignore errors during cleanup

# ====================
                    # CHUNK 4 - FINAL SECTION
                    # Display Q&A, Download, Chat, Feedback
                    # ====================
                    
                    # Display Q&A based on quiz mode
                    if quiz_mode:
                        # QUIZ MODE DISPLAY
                        for page in all_parsed_pages:
                            st.markdown(f"### {page['title']}")
                            st.write("")
                            
                            if not page['sections']:
                                st.info("No questions generated for this page.")
                                continue
                            
                            for section in page['sections']:
                                st.markdown(f"**{section['title']}**")
                                st.write("")
                                
                                if not section['qa_pairs']:
                                    st.info("No questions in this section.")
                                    continue
                                
                                for qa in section['qa_pairs']:
                                    st.markdown(f"**{qa['question']}**")
                                    with st.expander("🔍 Reveal Answer", expanded=False):
                                        st.markdown(qa['answer'])
                                    st.write("")
                                    st.write("")
                            
                            st.markdown("---")
                    else:
                        # NORMAL MODE DISPLAY
                        for page in all_parsed_pages:
                            st.markdown(f"### {page['title']}")
                            st.write("")
                            
                            if not page['sections']:
                                st.info("No questions generated for this page.")
                                continue
                            
                            for section in page['sections']:
                                st.markdown(f"**{section['title']}**")
                                st.write("")
                                
                                if not section['qa_pairs']:
                                    st.info("No questions in this section.")
                                    continue
                                
                                for qa in section['qa_pairs']:
                                    st.markdown(f"**{qa['question']}**")
                                    st.write("")
                                    st.markdown(qa['answer'])
                                    st.write("")
                                    st.write("")
                            
                            st.markdown("---")
                    
                    # FEEDBACK SECTION
                    st.write("")
                    st.write("")
                    st.markdown("---")
                    st.markdown("### 💬 We'd love to hear from you!")
                    st.write("")
                    
                    feedback_rating = st.slider(
                        "On a scale of 1 to 10, how much did you like this app and would you use it again?",
                        min_value=1,
                        max_value=10,
                        value=5,
                        key="feedback"
                    )
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        if st.button("Submit Feedback", key="feedback_btn"):
                            st.success("🎉 Thank you for your feedback! Your input helps us improve StudyBot.")
                            st.balloons()
                            time.sleep(0.5)
                    
                    # ====================
                    # END OF CHUNK 4 - PROGRAM COMPLETE!
                    # ====================
