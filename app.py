import streamlit as st
import google.generativeai as genai
import requests
from PyPDF2 import PdfReader
import docx
import faiss
import numpy as np

genai.configure(api_key="AIzaSyAk3XEySAOwd0eHZ-_zm3whmb3YMtlupks")
model = genai.GenerativeModel('gemini-2.0-flash')

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

def get_job_postings(skill):
    try:
        url = "https://jsearch.p.rapidapi.com/search"
        headers = {
            "X-RapidAPI-Key": "b4b611e0bbmshce92db716b7cf79p198a78jsn478ddbc4b850",
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        params = {
            "query": skill,
            "page": 1,
            "num_pages": 1
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()["data"]
    except:
        return []

def extract_skills_from_resume(uploaded_file):
    skills = []
    try:
        if uploaded_file.type == "application/pdf":
            pdf = PdfReader(uploaded_file)
            text = "\n".join([page.extract_text() for page in pdf.pages])
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])
        skills = [line.strip() for line in text.split("\n") if "skill" in line.lower()]
    except:
        skills = ["Error extracting skills from resume"]
    return skills

def get_salary_data(job_title):
    try:
        url = "https://api.adzuna.com/v1/api/jobs/gb/histogram"
        params = {
            "app_id": "a43cf7c1",
            "app_key": "384d6b73284bf185e7d87614a4d522f2",
            "what": job_title
        }
        response = requests.get(url, params=params)
        return response.json()["median_salary"]
    except:
        return "N/A"

def get_free_courses(skill):
    try:
        url = "https://udemy-paid-courses-for-free-api.p.rapidapi.com/rapidapi/courses/search"
        headers = {
            "X-RapidAPI-Key": "b4b611e0bbmshce92db716b7cf79p198a78jsn478ddbc4b850",  
            "X-RapidAPI-Host": "udemy-paid-courses-for-free-api.p.rapidapi.com"
        }
        params = {
            "query": skill,
            "language": "en",
            "page": 1,
            "page_size": 10
        }
        response = requests.get(url, headers=headers, params=params)
        courses = response.json().get("courses", [])
        return courses[:3] if courses else []
    except:
        return []

dimension = 128
index = faiss.IndexFlatL2(dimension)

def store_user_vector(user_skills):
    try:
        vector = np.random.rand(1, dimension).astype('float32')
        index.add(vector)
        return "Vector stored successfully"
    except:
        return "Error storing vector"

st.title("Career Path Oracle 🧙")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Upload Your Resume")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
    if uploaded_file is not None:
        with st.spinner("Analyzing resume..."):
            resume_skills = extract_skills_from_resume(uploaded_file)
            st.success(f"Resume uploaded: {uploaded_file.name}")
            st.write("### Skills Found:")
            st.write(", ".join(resume_skills))
            store_user_vector(resume_skills) 

user_input = st.chat_input("Ask me anything or upload your resume!")

if user_input or uploaded_file:
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
    
    analysis = analyze_skills(user_input if user_input else " ".join(resume_skills))
    skill = user_input if user_input else "Python Developer"
    jobs = get_job_postings(skill)
    salary = get_salary_data(skill)
    courses = get_free_courses(skill)
    
    try:
        job_list = "\n".join([f"- {job.get('job_title', 'N/A')} at {job.get('employer_name', 'N/A')}" for job in jobs[:3]]) if jobs else "No jobs found"
        course_list = "\n".join([f"- [{course.get('title', 'N/A')}]({course.get('url', '#')})" for course in courses[:3]]) if courses else "No courses found"

        response = f"""
        ### Analysis Results:
        {analysis}

        ### Related Job Postings:
        {job_list}

        ### Salary Insights:
        Median Salary: {salary}

        ### Free Courses to Learn:
        {course_list}
        """
    except Exception as e:
        response = f"Error formatting response: {str(e)}. Please try again."

    st.session_state.messages.append({"role": "assistant", "content": response})
    
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            if message["role"] == "assistant":
                feedback = st.radio(
                    "Was this helpful?",
                    ["👍 Yes", "👎 No"],
                    key=f"feedback_{idx}"
                )
                if feedback == "👍 Yes":
                    st.write("Thank you! Refining recommendations...")
                elif feedback == "👎 No":
                    st.write("Got it. Let's try something else!")