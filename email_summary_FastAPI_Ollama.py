import os
import json
import re
import queue
import copy
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize FastAPI app
app = FastAPI(title="Email Summarizer API")

# Input schema
class EmailInput(BaseModel):
    email_from_id: str
    email_to_id: str
    email_subject: str
    email_body: str

llm = Ollama(model="gemma3n:e2b")

messages = [
    SystemMessage(content="you are intelligent chat bot i need to give summrized subject and body"),
    HumanMessage(content="{}")
]

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system", """you are intelligent Summarizer. you take from, subject and body and give me one meaningful summary using body and suject. also summary size is 2 line.
                        I need to follow important part.
                        1. not add this sentence 'This email from'
                        2. only use sender name not use recipent names
                        3. not add words like "this is summary" and words like "this email"
                        4. add person name in Conversation.
            """
        ),
        (
            "user", """ From : {from}  
                        Subject: {subject}
                        body :{body} 
                        you take From, subject,body and give me one meaningful summary."""
        )
    ]
)


chain = prompt | llm | StrOutputParser()
summary_list=[]

# Endpoint
@app.post("/email/summarize-email")
def summarize_email(data:EmailInput):
    print("in side api")
    summary = chain.invoke(
        {
            "from":data.email_from_id,
            "to":data.email_to_id,
            "subject":data.email_subject,
            "body" : data.email_body,
            # "summaries": None
        }
        )

    print(summary)

    try:
        if(summary):
            summary_list.append(summary)
            return {
                "Summary" : summary
                }
        else:
             raise HTTPException(status_code=500, detail=f"Server error : {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing JSON: {str(e)}")

@app.post("/email/reply")
def email_reply(data:EmailInput):
    pre_summaries=""
    for summary in summary_list:
        pre_summaries += summary + "\n"

    Reply_summary = chain.invoke(
        {
            "from":data.email_from_id,
            "to":data.email_to_id,
            "subject":data.email_subject,
            "body" : data.email_body+ "\n" + pre_summaries
            # "summaries": pre_summaries
        }
    )

    pre_summaries=""

    try:
        if(Reply_summary):
            summary_list.append(Reply_summary)
            for summary in summary_list:
                print(summary)
            return {
                "Summary" : Reply_summary
                }
        else:
             raise HTTPException(status_code=500, detail=f"Server error : {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing JSON: {str(e)}")
