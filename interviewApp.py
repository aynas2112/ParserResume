from dotenv import load_dotenv
import os
import io
import base64
import streamlit as st
from PIL import Image
import pdf2image
import google.generativeai as genAI

# Load environment variables
load_dotenv()
genAI.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to process the PDF and convert it to an image
def inputPdf(upload_file):
    if upload_file is not None:
        images = pdf2image.convert_from_bytes(upload_file.read())
        first_page = images[0]
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Return just the image data
        return {
            "mime_type": "image/jpeg",
            "data": base64.b64encode(img_byte_arr).decode()
        }
    else:
        raise FileNotFoundError("File not found")

# Streamlit app configuration
st.set_page_config(page_title="ATS Tracking", page_icon=":robot:")
st.header("ATS Calculator")

# Initialize session state for questions and answers if not already done
if 'questions' not in st.session_state:
    st.session_state['questions'] = []
if 'answers' not in st.session_state:
    st.session_state['answers'] = []

inputText = st.text_area("Job Description:", key="input")
uploadedFile = st.file_uploader("Upload PDF", type=["pdf"], key="pdf")

# Prompts
inputPromptInterview = """
You are a technical interviewer specializing in [candidate's job role]. Based on the resume and job description provided, generate a list of specific, technical questions
relevant to the candidate's field of expertise. Avoid general HR questions; focus solely on technical skills, problem-solving capabilities, and relevant tools or technologies.
"""

inputPromptScoring = """
You are an experienced technical interviewer. For each technical question answered, please evaluate the candidate’s response and assign a score between 0 and 10, based on the following scale:
- 10: Demonstrates deep understanding, provides relevant examples, and showcases strong technical skills.
- 7-9: Good understanding, but may lack in-depth knowledge or specific examples.
- 4-6: Basic understanding, but needs further development.
- 1-3: Limited knowledge, needs significant improvement.
- 0: No understanding or irrelevant response.

For each answer, provide detailed, constructive feedback focusing on:
1. Specific areas for improvement with concrete examples.
2. Constructive criticism to help the candidate identify gaps in skills or knowledge.
3. Specific resources, tools, or techniques the candidate can use to improve.

Use this format:
- Question: [Question Text]
- Score: [Score]
- Feedback: [Detailed feedback based on criteria above]

Generate feedback for each response as if you are speaking directly to the candidate.
"""

# Helper function to call the generative model API
def getGeminiRes(input_text, pdf_content, prompt):
    model = genAI.GenerativeModel('gemini-1.5-flash')
    res = model.generate_content([input_text, pdf_content, prompt])
    return res.text

# Function to generate technical interview questions
def generate_interview_questions(input_text, pdf_content):
    questions_res = getGeminiRes(input_text, pdf_content, inputPromptInterview)
    questions = [q for q in questions_res.strip().split("\n") if q.strip() and "?" in q][:5]
    return questions

# Technical Interview Section
st.subheader("Technical Interview Section")

if st.button("Generate Technical Questions"):
    if uploadedFile is not None:
        pdfContent = inputPdf(uploadedFile)
        questions = generate_interview_questions(inputText, pdfContent)
        
        if questions:
            # Save questions and reset answers in session state only when questions are generated
            st.session_state['questions'] = questions
            st.session_state['answers'] = [""] * len(questions)  # Reset answers
            st.write("### Technical Questions:")

            # Use st.form to collect answers without rerunning
            with st.form("answer_form"):
                for i, question in enumerate(st.session_state['questions'], 1):
                    st.write(f"**Question {i}:** {question}")
                    # Using form's text_area to prevent reruns
                    st.session_state['answers'][i-1] = st.text_area(
                        f"Your Answer {i}", 
                        value=st.session_state['answers'][i-1],
                        key=f"answer_{i}"
                    )
                submit_answers = st.form_submit_button("Submit Answers")

            if submit_answers:
                st.write("Answers submitted successfully. You can now score them.")
        else:
            st.write("No valid technical questions generated. Please ensure the resume and job description are relevant.")

# Scoring and Feedback Section
if st.button("Score Answers"):
    if st.session_state['answers'] and st.session_state['questions']:
        # Prepare the answers for scoring
        answers_text = "\n".join([f"Question {i+1}: {q}\nAnswer {i+1}: {a}" 
                                  for i, (q, a) in enumerate(zip(st.session_state['questions'], st.session_state['answers']))])

        # Get the scoring and feedback response
        score_res = getGeminiRes(inputText, answers_text, inputPromptScoring)
        st.subheader("Interview Score and Feedback:")
        st.write(score_res)
    else:
        st.write("Please generate questions and answer them before scoring.")
