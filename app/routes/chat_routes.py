from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..auth import get_current_user
from ..rag import query_rag, resume_rag
from ..ai import ask_llm, analyze_resume, ask_stream
from ..schemas import QuestionRequest
from fastapi.responses import StreamingResponse
import json

router = APIRouter()

@router.post("/ask")
def ask(req: QuestionRequest, db:Session = Depends(get_db), user= Depends(get_current_user)):

    username = user["sub"]

    db_user = db.query(models.User).filter(models.User.username == username).first()

    context = query_rag(question=req.question, user_id = db_user.id)

    answer = ask_llm(context=context,
                     question=req.question)
    
    return {
        "question": req.question,
        "answer" : answer
    }

@router.post("/ask_stream")
def ask_stream(req: QuestionRequest, db:Session = Depends(get_db), user= Depends(get_current_user)):

    username = user["sub"]

    db_user = db.query(models.User).filter(models.User.username == username).first()

    context = query_rag(question=req.question, user_id = db_user.id)

    # answer = ask_llm(context=context,
    #                  question=req.question)
    
    # return {
    #     "question": req.question,
    #     "answer" : answer
    # }
    def generate():
        for chunk in ask_stream(
            context = context,
            question = req.question
        ):
            yield chunk

        return StreamingResponse(generate(), media_type="text/plain")    


@router.get("/analyze-resume")
def ask(db:Session = Depends(get_db), user= Depends(get_current_user)):

    username = user["sub"]

    db_user = db.query(models.User).filter(models.User.username == username).first()

    context = resume_rag(db_user.id)

    result = analyze_resume(context)
    
    try:
        parsed = json.loads(result)

    except:
        parsed = {"row_output" : result} 

    return parsed
