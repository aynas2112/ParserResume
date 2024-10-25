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

def getGeminiRes(input_text, pdf_content, prompt):
    model = genAI.GenerativeModel('gemini-1.5-flash')
    res = model.generate_content([input_text, pdf_content, prompt])
    return res.text

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

inputText = st.text_area("Job Description:", key="input")
uploadedFile = st.file_uploader("Upload PDF", type=["pdf"], key="pdf")

submit1 = st.button("Tell me about resume")
submit2 = st.button("How can I improvise my skills")
submit3 = st.button("What are the keywords missing")
submit4 = st.button("Percentage Match")

inputPrompt1 = """
You are a seasoned HR professional tasked with evaluating a candidate's resume against a specific job description.
Please provide an overview of the resume, highlighting key areas that align with the job's requirements.
Identify the candidate's strengths as well as areas that may need improvement in relation to the job description.
Consider factors such as experience, skills, certifications, and overall suitability for the role.
"""

inputPrompt2 = """
You are an HR and career development expert evaluating this resume in comparison to a job description. 
Identify skills that the candidate may be lacking or could further improve to increase their chances of landing this role.
Provide specific suggestions for how the candidate can acquire or enhance these skills, including recommended courses, certifications, or areas of practical experience.
"""

inputPrompt3 = """
As an ATS (Applicant Tracking System) specialist, evaluate this resume against the job description provided.
List any important keywords or phrases that are missing from the resume, which would help it rank better in ATS filters.
These keywords could include job-specific skills, industry-standard terms, or certifications.
Provide a list of these keywords and phrases, and suggest where in the resume they might best be incorporated.
"""

inputPrompt4 = """
You are a skilled ATS (Applicant Tracking System) and HR evaluator with a focus on data-driven matching.
Calculate the match percentage between this resume and the job description based on skills, experiences, and keywords.
The response should begin with the overall percentage match, followed by a list of missing keywords or phrases.
Lastly, offer final thoughts on whether the resume generally meets, exceeds, or falls short of the job requirements.
"""

# Check for file upload and button submission
if uploadedFile is not None:
    st.write("PDF uploaded successfully")   

    # Updated button prompt assignment
    if submit1:
        pdfContent = inputPdf(uploadedFile)
        res = getGeminiRes(inputText, pdfContent, inputPrompt1)
        st.subheader("The response is:")
        st.write(res)

    elif submit2:
        pdfContent = inputPdf(uploadedFile)
        res = getGeminiRes(inputText, pdfContent, inputPrompt2)
        st.subheader("The response is:")
        st.write(res)

    elif submit3:
        pdfContent = inputPdf(uploadedFile)
        res = getGeminiRes(inputText, pdfContent, inputPrompt3)
        st.subheader("The response is:")
        st.write(res)

    elif submit4:
        pdfContent = inputPdf(uploadedFile)
        res = getGeminiRes(inputText, pdfContent, inputPrompt4)
        st.subheader("The response is:")
        st.write(res)

else:
    st.write("Please upload the PDF file")
