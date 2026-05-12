from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_llm(question:str, context:str):

    prompt = f"""
You are AI Assistent,
Answer Only from the given Context, if have no answer gives I don't know.

Context:
{context}

Question:
{question}

"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",

        messages=[
            {
                "role" : "user",
                "content" : prompt
            }
        ]
    )
    return response.choices[0].message.content

def ask_stream(question:str, context:str):

    prompt = f"""
You are AI Assistent,
Answer Only from the given Context, if have no answer gives I don't know.

Context:
{context}

Question:
{question}

"""
    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",

        messages=[
            {
                "role" : "user",
                "content" : prompt
            }
        ],
        stream = True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def analyze_resume(context: str):

    prompt = f"""
You are a professional resume analyzer AI assistant.

Return ONLY valid JSON.

FORMAT:

{{
  "skills": [],
  "experience_summary": "",
  "strengths": [],
  "weaknesses": [],
  "missing_skills": [],
  "score": 0
}}

Rules:
- Score must be between 0 to 10
- Be strict and realistic
- Do NOT write anything outside JSON
- No explanation

Resume:
{context}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()