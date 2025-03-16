import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import re
import os  
from textblob import TextBlob
from translate import Translator
import language_tool_python
import matplotlib.pyplot as plt
import seaborn as sns
import shutil
if os.name == 'posix':  # for Linux environment (Streamlit Cloud)
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
else:  # for Windows environment
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# For local environment (Windows), Poppler path
if os.name == 'nt':  # for Windows environment
    poppler_path = r"C:\Program Files\Poppler\Library\bin"
else:
    poppler_path = None  # Poppler is automatically available in Streamlit Cloud

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file, lang='eng'):
    try:
        pdf_bytes = pdf_file.read()
        images = convert_from_bytes(pdf_bytes, dpi=300, poppler_path=poppler_path)
        text = "\n".join([pytesseract.image_to_string(img, lang=lang, config="--psm 6") for img in images])
        return text.strip() if text.strip() else "⚠️ No text found in this PDF."
    except Exception as e:
        return f"❌ Error reading PDF: {str(e)}"

# Function to extract text from Image
def extract_text_from_image(image_file, lang='eng'):
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image, lang=lang, config="--psm 6")
        return text.strip() if text.strip() else "⚠️ No text found in this image."
    except Exception as e:
        return f"❌ Error reading image: {str(e)}"
# Function to parse resume details
def parse_resume(text):
    name_match = re.search(r"^(\w+\s\w+)", text)
    contact_match = re.findall(r"(?:\+\d{1,2}\s?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    email_match = re.findall(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+", text)
    
    skills_match = re.findall(r"\b(?:Python|Java|C\+\+|Machine Learning|Data Science|SQL|AWS|Django|Cloud Computing)\b", text, re.IGNORECASE)
    experience_match = re.search(r"experience[:\n](.*?)(education|skills|$)", text, re.IGNORECASE | re.DOTALL)
    education_match = re.search(r"education[:\n](.*?)(experience|skills|$)", text, re.IGNORECASE | re.DOTALL)
    
    return {
        "Name": name_match.group(1) if name_match else "N/A",
        "Contact": contact_match[0] if contact_match else "N/A",
        "Email": email_match[0] if email_match else "N/A",
        "Skills": ", ".join(set(skills_match)) if skills_match else "N/A",
        "Experience": experience_match.group(1).strip() if experience_match else "N/A",
        "Education": education_match.group(1).strip() if education_match else "N/A",
    }

# Function to check keyword matching
def check_resume_keywords(resume_text, keywords):
    matched_keywords = [kw for kw in keywords if kw.lower() in resume_text.lower()]
    match_score = len(matched_keywords) / len(keywords) * 100 if keywords else 0
    return matched_keywords, match_score

# Function to determine suitable job role based on skills
def determine_role(skills):
    roles = {
        "Python": "Software Developer, Data Scientist",
        "Java": "Backend Developer, Software Engineer",
        "Machine Learning": "ML Engineer, Data Scientist",
        "Data Science": "Data Scientist, Business Analyst",
        "SQL": "Database Administrator, Data Analyst",
        "AWS": "Cloud Engineer, DevOps Engineer",
        "Django": "Full Stack Developer, Web Developer",
        "Cloud Computing": "Cloud Engineer, Solutions Architect"
    }
    
    matched_roles = set()
    for skill in skills.split(", "):
        if skill in roles:
            matched_roles.update(roles[skill].split(", "))
    
    return ", ".join(matched_roles) if matched_roles else "N/A"

# Function to provide job role-specific feedback
def job_role_feedback(role):
    feedback = {
        "Software Developer": "Consider adding more programming languages and frameworks to showcase versatility.",
        "Data Scientist": "Include more projects or experience related to machine learning and data visualization.",
        "Backend Developer": "Mention API development experience, databases, and server-side optimization.",
        "Cloud Engineer": "Highlight cloud certifications, deployment strategies, and security knowledge.",
        "Full Stack Developer": "Showcase frontend and backend expertise with relevant tech stacks."
    }
    
    return feedback.get(role, "Ensure your resume is well-structured and emphasizes relevant skills.")

# Function to recommend skills based on qualification
def recommend_skills(education):
    recommendations = {
        "Computer Science": ["Python", "Java", "Machine Learning", "Cloud Computing", "Data Structures & Algorithms"],
        "Information Technology": ["Networking", "Cybersecurity", "Cloud Computing", "Web Development"],
        "Business Administration": ["Excel", "Data Analysis", "Marketing Analytics", "Project Management"],
        "Mechanical Engineering": ["AutoCAD", "MATLAB", "SolidWorks", "Manufacturing Processes"]
    }
    
    for key, skills in recommendations.items():
        if key.lower() in education.lower():
            return ", ".join(skills)
    
    return "General Recommendations: Communication Skills, Problem-Solving, Teamwork, Leadership"

# Function to analyze sentiment of experience descriptions
def analyze_sentiment(text):
    experience_match = re.search(r"experience[:\n](.*?)(education|skills|$)", text, re.IGNORECASE | re.DOTALL)
    experience_text = experience_match.group(1).strip() if experience_match else ""
    blob = TextBlob(experience_text)
    sentiment_score = blob.sentiment.polarity
    sentiment = "Positive" if sentiment_score > 0 else "Negative" if sentiment_score < 0 else "Neutral"
    return sentiment, sentiment_score

# Function to provide formatting suggestions
def formatting_suggestions(text):
    suggestions = []
    if len(text.split()) < 200:
        suggestions.append("Consider adding more details to your resume to provide a comprehensive overview.")
    if re.search(r"\b\b\b", text):
        suggestions.append("Ensure consistent use of bullet points for lists.")
    if len(re.findall(r"\.\s", text)) < 5:
        suggestions.append("Consider adding more full sentences to describe your experiences and skills.")
    return suggestions

# Function to translate text
def translate_text(text, target_lang):
    try:
        translator = Translator(to_lang=target_lang)
        translated_text = translator.translate(text)
        return translated_text
    except Exception as e:
        return f"❌ Error translating text: {str(e)}"

# Function to check grammar and style
def check_grammar_style(text):
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    errors = [str(match) for match in matches]
    return errors

# Function to generate cover letter
def generate_cover_letter(parsed_data, job_role):
    cover_letter_template = f"""
    Dear Hiring Manager,

    I am writing to express my interest in the {job_role} position at your company. As a dedicated and detail-oriented professional with a strong background in {parsed_data['Skills']}, I believe I can contribute effectively to your team.

    I hold a degree in {parsed_data['Education']} and have gained significant experience in {parsed_data['Experience']}. My skills in {parsed_data['Skills']} make me a strong candidate for this role, and I am eager to apply my knowledge and expertise to contribute to the success of your organization.

    Please find my resume attached for your review. I look forward to discussing how my skills and experience align with the needs of your team.

    Thank you for considering my application.

    Sincerely,
    {parsed_data['Name']}
    """
    return cover_letter_template.strip()


# Sample data for testing
matched_keywords = ['Python', 'Machine Learning', 'Data Analysis']
sentiment_score = 0.75
match_score = 85
resume  = {}  # Placeholder resume data

# Streamlit UI
st.title("📄 Resume Screener App")
st.write("Upload a resume (PDF or Image) to analyze it against job criteria!")

# Allow user to manually enter details BEFORE uploading a file
st.subheader("🔍 Enter Your Details")
parsed_data = {
    "Name": st.text_input("Name", ""),
    "Skills": st.text_input("Skills", ""),
    "Education": st.text_input("Education", ""),
    "Experience": st.text_area("Experience", "")
}

# Language Selection
language = st.selectbox("Select OCR Language", ["eng", "fra", "spa", "deu", "ita"])

uploaded_file = st.file_uploader("Upload Resume (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.success("✅ Resume uploaded successfully!")
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file, language)
    else:
        resume_text = extract_text_from_image(uploaded_file, language)
    
    st.subheader("📄 Extracted Resume Text")
    st.text_area("Resume Content", resume_text, height=200)
    
    if "❌" in resume_text:
        st.error(resume_text)
    else:
        parsed_data = parse_resume(resume_text)
        
        st.subheader("📌 Extracted Details")
        for key, value in parsed_data.items():
            st.write(f"**{key}:** {value}")
        
        job_keywords = st.text_area("Enter Job Keywords (comma-separated)", "Python, Machine Learning, SQL, AWS")
        job_keywords_list = [kw.strip() for kw in job_keywords.split(",") if kw.strip()]
        
        matched_keywords, match_score = check_resume_keywords(resume_text, job_keywords_list)
        
        st.subheader("🔍 Screening Results")
        st.write(f"✅ Matched Keywords: {matched_keywords}")
        
        st.write(f"📊 Resume Score: **{min(100, match_score):.2f}%**")
        if match_score >= 80:
            st.success("✅ Great Match! Your resume is well-optimized.")
        elif match_score >= 50:
            st.warning("⚠️ Needs Improvement! Consider adding more relevant keywords.")
        else:
            st.error("❌ Weak Match! Your resume lacks important keywords.")
        
        suitable_role = determine_role(parsed_data['Skills'])
        st.subheader("🎯 Suitable Job Role")
        st.write(f"**{suitable_role}**")
        
        role_feedback = job_role_feedback(suitable_role)
        st.subheader("📌 Job Role-Specific Feedback")
        st.write(f"**{role_feedback}**")
        
        recommended_skills = recommend_skills(parsed_data['Education'])
        st.subheader("📌 Recommended Skills to Learn")
        st.write(f"**{recommended_skills}**")
        
        sentiment, sentiment_score = analyze_sentiment(resume_text)
        st.subheader("😊 Sentiment Analysis of Experience")
        st.write(f"**Sentiment:** {sentiment} (**Score:** {sentiment_score:.2f})")
        
        formatting_tips = formatting_suggestions(resume_text)
        st.subheader("📌 Formatting Suggestions")
        for tip in formatting_tips:
            st.write(f"**- {tip}**")
            # Input for desired job role
    if "❌" not in resume_text:
        # Use extracted data if available
        parsed_data["Name"] = parsed_data["Name"] or "Extracted Name"
        parsed_data["Skills"] = parsed_data["Skills"] or "Extracted Skills"
        parsed_data["Education"] = parsed_data["Education"] or "Extracted Education"
        parsed_data["Experience"] = parsed_data["Experience"] or "Extracted Experience"

# Input for desired job role
job_role = st.text_input("Desired Job Role", "Software Developer")

# Cover Letter Generation
if st.button("Generate Cover Letter"):
    if not parsed_data['Name'] or not parsed_data['Skills'] or not parsed_data['Education'] or not parsed_data['Experience']:
        st.error("❌ Please fill in all details or upload a resume!")
    else:
        cover_letter = generate_cover_letter(parsed_data, job_role)
        st.subheader("📄 Generated Cover Letter")
        st.text_area("Cover Letter", cover_letter, height=500)
        st.download_button(label="Download Cover Letter", data=cover_letter, file_name='cover_letter.txt', mime='text/plain')
