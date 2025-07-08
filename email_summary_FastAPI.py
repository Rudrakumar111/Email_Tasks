
import os
import json
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_groq.chat_models import ChatGroq
from langchain.prompts import PromptTemplate

groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize FastAPI app
app = FastAPI(title="Email Summarizer API")

# Input schema
class EmailInput(BaseModel):
    from_email: str
    to_email: str
    subject: str
    body: str

# Output
class EmailSummary(BaseModel):
    from_: str
    to: str
    subject_summary: str
    body_summary: str

# LangChain model
llm = ChatGroq(
    model_name="llama3-8b-8192",
    groq_api_key=groq_api_key,
    temperature=0.2
)

# Prompt Template
prompt = PromptTemplate(
    input_variables=["email_text"],
    template="""
You are an expert at summarizing emails.

Given the full raw email below, extract the following in JSON format:
- "from": sender's email address
- "to": recipient's email address
- "subject_summary": a clean, brief summary of the subject
- "body_summary": a concise summary of the body but give me summary at least 1/8 part size compared to body.

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

# Endpoint
@app.post("/summarize-email", response_model=EmailSummary)
def summarize_email(data: EmailInput):
    email_text = f"Subject: {data.subject}\nTo: {data.to_email}\nFrom: {data.from_email}\n\n{data.body}"
    
    formatted_prompt = prompt.format(email_text=email_text)
    response = llm.invoke(formatted_prompt)

    match = re.search(r'\{.*?\}', response.content, re.DOTALL)
    if not match:
        raise HTTPException(status_code=400, detail="Model response did not contain valid JSON.")

    try:
        parsed = json.loads(match.group(0))
        return {
            "from_": parsed["from"],
            "to": parsed["to"],
            "subject_summary": parsed["subject_summary"],
            "body_summary": parsed["body_summary"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing JSON: {str(e)}")
