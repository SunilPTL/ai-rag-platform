from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, auth, schemas
from .. auth import get_current_user
import os, shutil
from ..rag import process_pdf

router = APIRouter()

UPLOAD_DIR = "app/uploads"

@router.post("/upload")
def upload_file(file:UploadFile = File(...), db:Session = Depends(get_db), user = Depends(get_current_user)):
    username = user["sub"]

    db_user = db.query(models.User).filter(models.User.username == username).first()

    new_file = models.File(
        filename = file.filename,
        user_id = db_user.id
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    process_pdf(file_path=file_path, user_id=db_user.id, file_id=new_file.id)

    return {"message" : "File Uploaded or Processed"}    
    

