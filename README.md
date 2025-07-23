# 📧 Email Summarizer API

This is a FastAPI-based application that summarizes email threads using Google Gemini (via LangChain). It intelligently processes and condenses multiple emails into concise summaries while preserving key information like sender names, subject, and intent.




---

## Sample Input 1

```json
{
  "thread_id": "thread-123",
  "email_count": 2,
  "emails": [
    {
      "id_": "email-1",
      "from_": "alice@example.com",
      "to": ["bob@example.com"],
      "cc": [],
      "bcc": [],
      "subject": "Project Update",
      "body": "Hey Bob, here’s the latest on the project...",
      "is_parent": true,
      "parent_email_id": ""
    },
    {
      "id_": "email-2",
      "from_": "bob@example.com",
      "to": ["alice@example.com"],
      "cc": [],
      "bcc": [],
      "subject": "Re: Project Update",
      "body": "Thanks Alice. Looks good. I added a few suggestions...",
      "is_parent": false,
      "parent_email_id": "email-1"
    }
  ]
}



---
## Sample Output 1

```json
{
  "summaries": {
    "thread-123": [
      "Alice shared the latest updates on the project.",
      "Bob appreciated the updates and added suggestions."
    ],
  }
}





---

## Sample Input 2

```json
{
  "thread_id": "thread-124",
  "email_count": 2,
  "emails": [
    {
      "id_": "email-1",
      "from_": "alice@example.com",
      "to": ["bob@example.com"],
      "cc": [],
      "bcc": [],
      "subject": "Project Update",
      "body": "Hey Bob, here’s the latest on the project...",
      "is_parent": true,
      "parent_email_id": ""
    },
    {
      "id_": "email-2",
      "from_": "bob@example.com",
      "to": ["alice@example.com"],
      "cc": [],
      "bcc": [],
      "subject": "Re: Project Update",
      "body": "Thanks Alice. Looks good. I added a few suggestions...",
      "is_parent": false,
      "parent_email_id": "email-1"
    }
  ]
}



---
## Sample Output 2

```json
{
  "summaries": {
    "thread-123": [
      "Alice shared the latest updates on the project.",
      "Bob appreciated the updates and added suggestions."
    ],
      "thread-124": [
      "Carol sent the meeting agenda for tomorrow's meeting and asked if Dave wanted to add anything.",
      "Dave thanked Carol for the meeting agenda and suggested adding a discussion about last week's client feedback."
    ]
  }
}



## code Stucture:

email-summarizer-api/
├── app/
│   ├── __init__.py         
│   ├── email_summary_FastAPI.py  # Core logic: prompt setup and Gemini integration
│
├── .env                          # Environment variables (e.g., GOOGLE_API_KEY)
├── requirements.txt              # Python dependencies
├── README.md 




## Model Description
This application uses:

Model: gemini-2.5-flash via LangChain's ChatGoogleGenerativeAI

Purpose: To summarize email bodies and subjects in 1–2 lines.

Behavior:

For the parent email, a direct summary is generated.

For follow-up emails, the model is given previous summaries for context.

The summaries are stored thread-wise using an in-memory dictionary.





## Flow
User sends a POST request to /email/summarize with a list of emails in a thread.

The app processes each email:

If it's a parent email, it generates a summary directly.

If it's a child, it prepends earlier summaries for contextual summarization.

The response contains a list of thread-wise summaries.
Ex : email1 ---> s1
    email2 ----> s1 + email2(body) ---> s2
    email3 ----> s1 + s2 + email3(body) ---> s3




## API Endpoint
POST /email/summarize



Request Body: EmailThread schema
{
  "emails": [Email, Email, ...],
  "thread_id": "string",
  "email_count": int
}

Email Object:
{
  "id_": "string",
  "from_": "string",
  "to": ["string"],
  "cc": ["string"],
  "bcc": ["string"],
  "subject": "string",
  "body": "string",
  "is_parent": true/false,
  "parent_email_id": "string"
}
