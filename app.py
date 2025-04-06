import streamlit as st
import google.generativeai as genai
import requests
from PyPDF2 import PdfReader
import docx
import faiss
import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize session state for page control
if 'intro_shown' not in st.session_state:
    st.session_state.intro_shown = False

def show_intro():
    # Introduction page code (unchanged)
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        .intro-container { padding: 1rem; }
        .feature-icon { font-size: 2rem; }
        .intro-title { font-size: 2rem; }
        .intro-subtitle { font-size: 1.25rem; }
        .team-member { margin-bottom: 1rem; }
    }
    .intro-container {
        padding: 2rem;
        background-color: #f0f2f6;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    .feature-icon:hover {
        transform: scale(1.1);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="intro-container">
        <div style="text-align: center;">
            <img src="https://cdn-icons-png.flaticon.com/512/10349/10349936.png" 
                 style="max-width: 150px; height: auto; margin: 0 auto;"/>
        </div>
        <h1 style="color: #4A90E2; font-size: 2.5rem;">Career Path Oracle 🧙‍♂️</h1>
        <h3 style="color: #333; margin-top: 0.5rem;">Your AI-Powered Career Companion</h3>
        <p style="text-align: center; color: #555;">
            Get personalized career guidance, skill analysis, and job market insights
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")

    # Features row
    st.subheader("What I Can Do For You")
    feature_cols = st.columns(3)
    features = [
        ("📝", "Resume Analysis", "Extract skills and get tailored career suggestions"),
        ("🕵️", "Job Market Insights", "Discover relevant job postings and salary data"),
        ("📚", "Learning Resources", "Get free course recommendations to upskill")
    ]
    
    for idx, (icon, title, desc) in enumerate(features):
        with feature_cols[idx]:
            st.markdown(f"""
            <div style="text-align: center; margin: 1.5rem 0;">
                <span class="feature-icon">{icon}</span>
                <h4>{title}</h4>
                <p style="color: #666; font-size: 0.9rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.write("---")
    
    # Team row
    st.subheader("Our Team")
    team_cols = st.columns(3)
    team = [
        ("Pavan", "12305446", "ML Engineer"),
        ("Sakshi", "12306499", "Data Scientist"),
        ("Kausar", "12316343", "Full-Stack Developer")
    ]
    
    for idx, (name, id, role) in enumerate(team):
        with team_cols[idx]:
            st.markdown(f"""
            <div style="text-align: center; margin: 1rem 0;">
                <h4>{name}</h4>
                <p style="color: #666; font-size: 0.85rem;">
                    {role}<br>
                    <code style="background: #f0f2f6;">ID: {id}</code>
                </p>
            </div>
            """, unsafe_allow_html=True)

    st.write("---")
    
    # How it works
    st.subheader("How It Works")
    steps = ["1. Upload/Describe Skills", "2. Get Career Suggestions", 
             "3. Explore Opportunities", "4. Refine Search"]
    step_cols = st.columns(4)
    for idx, step in enumerate(steps):
        with step_cols[idx]:
            st.markdown(f"""
            <div style="text-align: center;">
                <h2 style="color: #4A90E2;">{idx+1}</h2>
                <p>{step}</p>
            </div>
            """, unsafe_allow_html=True)

    if st.button("Let's Get Started ➡️", use_container_width=True):
        st.session_state.intro_shown = True
        st.rerun()

# Main app functionality
def main_app():
    # Get API keys from environment variables
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
    JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY", "your-jsearch-api-key")
    ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "your-adzuna-app-id")
    ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "your-adzuna-app-key")
    UDEMY_API_KEY = os.getenv("UDEMY_API_KEY", "your-udemy-api-key")
    
    # Configure Gemini API
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Initialize bot persona information
    bot_persona = {
        "name": "Career Path Oracle",
        "personality": "helpful, friendly, and knowledgeable about careers",
        "origin": "Created by a team of students (Pavan, Sakshi, and Kausar) as a project to help people find their ideal career paths",
        "mission": "To help users explore career opportunities, analyze their skills, and find resources to enhance their professional growth",
        "likes": "Helping people discover their passions and potential career paths",
        "location": "Cloud-based and accessible from anywhere",
        "hobbies": "Analyzing job markets, matching skills to careers, and finding learning resources"
    }
    
    def respond_to_casual_chat(user_input):
        """Generate responses for casual chat questions about the bot"""
        prompt = f"""
        You are the Career Path Oracle, an AI assistant specialized in career guidance.
        
        About you:
        - Name: {bot_persona['name']}
        - Personality: {bot_persona['personality']}
        - Origin: {bot_persona['origin']}
        - Mission: {bot_persona['mission']}
        - Likes: {bot_persona['likes']}
        - Location: {bot_persona['location']}
        - Hobbies: {bot_persona['hobbies']}
        
        The user asks: "{user_input}"
        
        Respond in a friendly, conversational way as the Career Path Oracle. Keep your response focused and under 100 words.
        After answering their casual question, gently steer the conversation back to career guidance by adding a question
        about their career interests or skills at the end.
        """
        
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"I'm the Career Path Oracle, here to help with your career questions! I encountered a small issue ({str(e)}), but I'm still here to assist you. What career path are you interested in exploring today?"

    def analyze_skills(user_input):
        try:
            prompt = f"""
            Analyze the user's input: "{user_input}"
            Identify their top 3 skills and suggest 3 career paths.
            Format the response as a bulleted list.
            """
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error analyzing skills: {str(e)}"

    def detect_message_type(user_input):
        """
        Detect if the user is having a casual chat or seeking career information
        Returns: 
        - "chat" for casual conversation about the bot
        - "career" for career-related questions
        - "greeting" for simple greetings
        """
        prompt = f"""
        Analyze this message: "{user_input}"
        
        Categorize it as ONE of the following:
        1. "greeting" - if it's just a simple hello or introduction
        2. "chat" - if the user is asking personal questions about the bot itself (like "who are you", "where are you from", "what's your name", etc.)
        3. "career" - if the user is asking about careers, jobs, skills, resume advice, or other professional topics
        
        Respond with ONLY "greeting", "chat", or "career".
        """
        
        try:
            response = model.generate_content(prompt)
            result = response.text.strip().lower()
            if result in ["greeting", "chat", "career"]:
                return result
            else:
                # Default to career if classification fails
                return "career"
        except Exception as e:
            # Default to career if there's an error
            return "career"

    def get_job_postings(skill):
        try:
            url = "https://jsearch.p.rapidapi.com/search"
            headers = {
                "X-RapidAPI-Key": JSEARCH_API_KEY,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }
            params = {
                "query": skill,
                "page": 1,
                "num_pages": 1
            }
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json().get("data", [])
            return []
        except Exception as e:
            st.error(f"Error fetching job postings: {str(e)}")
            return []

    def extract_skills_from_resume(uploaded_file):
        skills = []
        try:
            if uploaded_file.type == "application/pdf":
                pdf = PdfReader(uploaded_file)
                text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = docx.Document(uploaded_file)
                text = "\n".join([para.text for para in doc.paragraphs])
            else:
                return ["Unsupported file format. Please upload a PDF or DOCX file."]
            
            # Check if document contains the word "resume" (case-insensitive)
            if "resume" not in text.lower() and "cv" not in text.lower():
                return ["Not a valid resume - document does not contain valid resume content"]
            
            # Use Gemini to extract skills
            prompt = f"""
            Extract technical and professional skills from this resume text. 
            Format as a comma-separated list.
            
            Resume text:
            {text[:2000]}  # Limit text length to avoid exceeding token limits
            """
            
            response = model.generate_content(prompt)
            skills_text = response.text.strip()
            skills = [skill.strip() for skill in skills_text.split(',')]
            
            if not skills:
                # Fallback method if AI extraction fails
                skills = [line.strip() for line in text.split("\n") if "skill" in line.lower()]
                
            return skills if skills else ["No skills found in resume"]
                
        except Exception as e:
            return [f"Error processing file: {str(e)}"]

    def get_salary_data(job_title):
        try:
            url = "https://api.adzuna.com/v1/api/jobs/gb/histogram"
            params = {
                "app_id": ADZUNA_APP_ID,
                "app_key": ADZUNA_APP_KEY,
                "what": job_title
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json().get("median_salary", "N/A")
            return "N/A"
        except Exception as e:
            st.error(f"Error fetching salary data: {str(e)}")
            return "N/A"

    def get_free_courses(skill):
        try:
            url = "https://udemy-paid-courses-for-free-api.p.rapidapi.com/rapidapi/courses/search"
            headers = {
                "X-RapidAPI-Key": UDEMY_API_KEY,
                "X-RapidAPI-Host": "udemy-paid-courses-for-free-api.p.rapidapi.com"
            }
            params = {
                "query": skill,
                "language": "en",
                "page": 1,
                "page_size": 10
            }
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                courses = response.json().get("courses", [])
                return courses[:3] if courses else []
            return []
        except Exception as e:
            st.error(f"Error fetching courses: {str(e)}")
            return []

    # Vector database initialization
    dimension = 128
    index = faiss.IndexFlatL2(dimension)

    def store_user_vector(user_skills):
        try:
            # Generate a simple vector representation of skills
            # In a real application, you would use embeddings from an NLP model
            vector = np.random.rand(1, dimension).astype('float32')
            index.add(vector)
            return True
        except Exception as e:
            st.error(f"Error storing vector: {str(e)}")
            return False

    st.title("Career Path Oracle 🧙")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "valid_resume" not in st.session_state:
        st.session_state.valid_resume = False
    if "resume_skills" not in st.session_state:
        st.session_state.resume_skills = []
    if "chat_count" not in st.session_state:
        st.session_state.chat_count = 0

    with st.sidebar:
        st.header("Upload Your Resume")
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
        if uploaded_file is not None:
            with st.spinner("Analyzing resume..."):
                resume_skills = extract_skills_from_resume(uploaded_file)
                
                if "Not a valid resume" in resume_skills[0] or "Error" in resume_skills[0]:
                    st.error(resume_skills[0])
                    st.session_state.valid_resume = False
                else:
                    st.success(f"Resume uploaded: {uploaded_file.name}")
                    st.write("### Skills Found:")
                    st.write(", ".join(resume_skills))
                    if store_user_vector(resume_skills):
                        st.session_state.resume_skills = resume_skills
                        st.session_state.valid_resume = True
        else:
            st.session_state.valid_resume = False

        st.write("---")
        st.subheader("About Me")
        st.write("I'm your Career Path Oracle! You can ask me:")
        st.write("- About myself and how I can help you")
        st.write("- For career path suggestions")
        st.write("- About job market insights")
        st.write("- For learning resources")
        
        st.write("---")
        st.subheader("Example Questions")
        st.write("Try asking:")
        st.write("- What skills do I need for data science?")
        st.write("- What are the best career paths for Python developers?")
        st.write("- How can I transition to AI engineering?")
        st.write("- What are you? Who created you?")
        
        st.write("---")
        st.subheader("Team Members")
        st.write("Pavan - 12305446")
        st.write("Sakshi - 12306499")
        st.write("Kausar - 12316343")

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input box for user queries
    user_input = st.chat_input("Ask me anything about careers or chat with me!")

    # Process user input or resume upload
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Detect message type - whether casual chat or career question
                message_type = detect_message_type(user_input)
                
                # Handle based on message type
                if message_type == "greeting":
                    # It's a simple greeting
                    greeting_prompt = f"""
                    The user says: "{user_input}"
                    
                    Respond with a warm, friendly greeting as the Career Path Oracle. 
                    Include a brief introduction about what you can help with (career guidance, skill analysis, etc.).
                    Keep it under 3 sentences.
                    """
                    greeting_response = model.generate_content(greeting_prompt)
                    response = greeting_response.text
                    
                elif message_type == "chat":
                    # It's a casual chat about the bot itself
                    st.session_state.chat_count += 1
                    response = respond_to_casual_chat(user_input)
                    
                else:
                    # It's a career-related question
                    # Reset chat counter when user asks career questions
                    st.session_state.chat_count = 0
                    
                    # Proceed with skill analysis
                    analysis = analyze_skills(user_input)
                    
                    # Extract a key skill to search for jobs and courses
                    skill_prompt = f"Extract a single professional skill or job title from this text: '{user_input}'. Give only the skill or job title, nothing else."
                    skill_response = model.generate_content(skill_prompt)
                    skill = skill_response.text.strip()
                    
                    # Get supporting data
                    jobs = get_job_postings(skill)
                    salary = get_salary_data(skill)
                    courses = get_free_courses(skill)
                    
                    # Format response
                    try:
                        job_list = "\n".join([f"- {job.get('job_title', 'N/A')} at {job.get('employer_name', 'N/A')}" for job in jobs[:3]]) if jobs else "No related job postings found. Try a different query."
                        
                        course_list = "\n".join([f"- [{course.get('title', 'N/A')}]({course.get('url', '#')})" for course in courses[:3]]) if courses else "No courses found. Try searching for more specific skills."
                        
                        response = f"""
                        ### Analysis Results:
                        {analysis}

                        ### Related Job Postings:
                        {job_list}

                        ### Salary Insights:
                        Median Salary: {salary if salary != "N/A" else "Data not available"}

                        ### Free Courses to Learn:
                        {course_list}
                        
                        Would you like more specific information about any of these career paths or skills?
                        """
                    except Exception as e:
                        response = f"I encountered an issue while analyzing your request: {str(e)}. Could you please rephrase or provide more details about what you're looking for?"
                
                # Gently redirect if too much casual chat
                if st.session_state.chat_count > 3:
                    career_prompt = "\n\nI'm happy to chat, but I'm specialized in career guidance. Is there anything about your career path or skills I can help you with today?"
                    response += career_prompt
                
                st.markdown(response)
                
                # Add feedback options
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👍 Helpful", key="helpful"):
                        st.success("Thank you! I'll keep improving my recommendations.")
                with col2:
                    if st.button("👎 Not Helpful", key="not_helpful"):
                        st.info("I appreciate your feedback. Let me know how I can do better!")
        
        # Add assistant message to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Handle resume upload feedback
    elif st.session_state.valid_resume and len(st.session_state.messages) == 0:
        # Only process if we have a valid resume but haven't responded yet
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your resume..."):
                all_skills = ", ".join(st.session_state.resume_skills)
                analysis = analyze_skills(all_skills)
                
                # Extract a primary skill/job title from the resume
                skill_prompt = f"Based on these skills: {all_skills}, what would be the most relevant job title to search for? Give only the job title, nothing else."
                skill_response = model.generate_content(skill_prompt)
                skill = skill_response.text.strip()
                
                # Get supporting data
                jobs = get_job_postings(skill)
                salary = get_salary_data(skill)
                courses = get_free_courses(skill)
                
                # Format response
                try:
                    job_list = "\n".join([f"- {job.get('job_title', 'N/A')} at {job.get('employer_name', 'N/A')}" for job in jobs[:3]]) if jobs else "No related job postings found."
                    
                    course_list = "\n".join([f"- [{course.get('title', 'N/A')}]({course.get('url', '#')})" for course in courses[:3]]) if courses else "No relevant courses found."
                    
                    response = f"""
                    ### Resume Analysis Results:
                    Based on your resume, here's my assessment:
                    
                    {analysis}

                    ### Recommended Job Postings:
                    {job_list}

                    ### Salary Insights for {skill}:
                    Median Salary: {salary if salary != "N/A" else "Data not available"}

                    ### Recommended Learning Resources:
                    {course_list}
                    
                    Is there a specific career path you're most interested in exploring further?
                    """
                except Exception as e:
                    response = f"I encountered an issue while analyzing your resume: {str(e)}. Could you please try uploading it again or describe your skills directly?"
                
                st.markdown(response)
                
                # Add feedback options
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👍 Helpful", key="resume_helpful"):
                        st.success("Thank you! I'll keep improving my recommendations.")
                with col2:
                    if st.button("👎 Not Helpful", key="resume_not_helpful"):
                        st.info("I appreciate your feedback. Let me know how I can do better!")
            
            # Add assistant message to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

# Main app entry point
if not st.session_state.intro_shown:
    show_intro()
else:
    main_app()
