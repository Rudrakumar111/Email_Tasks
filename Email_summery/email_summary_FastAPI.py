import os
import json
import re
import queue
import copy
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize FastAPI app
app = FastAPI(title="Email Summarizer API")

# Input schema
class Email(BaseModel):
    id_: str
    from_: str
    to: List[str]
    cc: List[str] 
    bcc: List[str]
    subject: str
    body: str
    is_parent: bool
    parent_email_id: str 

class EmailThread(BaseModel):
    emails: List[Email]
    thread_id: str
    email_count: int

load_dotenv()

# Set up Google Generative AI client
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

messages = [
    SystemMessage(content="you are intelligent chat bot i need to give summrized subject and body"),
    HumanMessage(content="{}")
]

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system", """Summarize emails in 1-2 lines using the subject and body. Include sender name naturally. Don't use phrases like "This email from" or "This is a summary."
            """
        ),
        (
            "user", """ From : {from}  
                        Subject: {subject}
                        Body :{body} 
                        Read 'From', 'Subject' and 'Body' and give me one meaningful summary."""
        )
    ]
)


chain = prompt | llm | StrOutputParser()
summary_list={}

# Endpoint
@app.post("/email/summarize")
def summarize_email(data:EmailThread):
    print("API called...")
    summary = """"""
    for email in data.emails:
        if email.is_parent:

            if(summary_list.get(data.thread_id) is None):
                summary = chain.invoke(
                    {
                        "from":email.from_,
                        "to":email.to,
                        "subject":email.subject,
                        "body" : email.body,
                    }
                    )

        else:
            prev_summaries=""
            for idx,summary in enumerate(summary_list[data.thread_id]):
                prev_summaries += summary + f"Summary {idx}\n\n"

            print(prev_summaries)

            summary = chain.invoke(
                {
                    "from":email.from_,
                    "to":email.to,
                    "subject":email.subject,
                    "body" : email.body + "\n" + prev_summaries

                }
            )

        try:
            if(len(summary) > 0):
                if(email.is_parent):
                    summary_list[data.thread_id] = [summary]
                else:
                    summary_list[data.thread_id].append(summary)
            else:
                raise HTTPException(status_code=500, detail=f"Server error : {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing JSON: {str(e)}")

    return {"summaries": summary_list}