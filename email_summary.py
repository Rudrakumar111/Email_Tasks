import os
import json
from langchain_community.document_loaders import PyPDFLoader
from langchain_groq.chat_models import ChatGroq
from langchain.prompts import PromptTemplate
import streamlit as st
import re

groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model_name="llama3-8b-8192",  # Best balance for summarization
    groq_api_key=groq_api_key,
    temperature=0.2
)

loader = PyPDFLoader("C:/Users/Admin/Desktop/AI-ML_QB/Email_Tasks/AI_Email_Dataset.pdf")  
pages = loader.load()

prompt = PromptTemplate(
    input_variables=["email_text"],
    template="""
You are an expert at summarizing emails.

Given the full raw email below, extract the following in JSON format:
- "from": sender's email address
- "to": recipient's email address
- "subject_summary": a clean, brief summary of the subject
- "body_summary": a concise summary of the body but give me summary aleast 1/8 part size compare to body.

Email:
{email_text}

Return ONLY valid JSON in this format:
{{
  "from": "...",
  "to": "...",
  "subject_summary": "...",
  "body_summary": "..."
}}
"""
)

st.title("Email Summarizer with Langchain + GROQ")

with st.form("Email_form"):
    from_email = st.text_input("From")
    to_email = st.text_input("To")
    subject = st.text_input("Subject")
    body = st.text_area("Email Body",height=500)

    submitted = st.form_submit_button("Summarize Email")

if submitted:
    email_text = f"Subject: {subject}\nTo: {to_email}\nFrom: {from_email}\n\n{body}"

    with st.spinner("Generating Summary..."):  
        formatted_prompt = prompt.format(email_text=email_text)
        response = llm.invoke(formatted_prompt)
        match = re.search(r'\{.*?\}', response.content,re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                result = json.loads(json_str)

                st.success("Email Summary:")
                st.json(result) 

               
                st.write("**From:**", result["from"])
                st.write("**To:**", result["to"])
                st.write("**Subject Summary:**", result["subject_summary"])
                st.write("**Body Summary:**", result["body_summary"])

            except Exception as e:
                st.error("Failed to parse extracted JSON")
                st.code(json_str)
        else:
            st.error("Not Valid Output Found")
            st.code(response.content)
