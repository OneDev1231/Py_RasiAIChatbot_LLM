from typing import Annotated

from fastapi.security import OAuth2PasswordBearer

from app.backend.utilities.utilities import verify_token
from app.vectors_store.ingestion.ingest_json import ingest_json
from app.vectors_store.ingestion.ingest_csv import ingest_csv
from app.vectors_store.ingestion.ingest_pdf import ingest_pdf
from app.vectors_store.ingestion.ingest_txt import ingest_txt
from app.vectors_store.ingestion.ingest_excel import ingest_excel
from app.vectors_store.ingestion.ingest_ppt import ingest_ppt
from app.vectors_store.ingestion.ingest_doc import ingest_doc
from app.vectors_store.delete_vectors.delete_vectors import delete_all_vectors

import requests


from fastapi import APIRouter, HTTPException, Depends, UploadFile, Request, File, Form, status
from fastapi.responses import JSONResponse

import os

from dotenv import load_dotenv, find_dotenv
from supabase import create_client, Client


load_dotenv(find_dotenv())

SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_ANON_PUBLIC_KEY = os.getenv("SUPABASE_ANON_PUBLIC_KEY")


router = APIRouter()
supabase: Client = create_client(SUPABASE_PROJECT_URL, SUPABASE_ANON_PUBLIC_KEY)

def get_bearer_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid scheme")
            return token
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid authorization header format"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Ingest CSV
@router.post("/api/v1/upsert_csv/")
async def upsert_csv(
    file: Annotated[UploadFile, File()],
    index_name: Annotated[str, Form()],
    token: str = Depends(get_bearer_token),
):
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if file.content_type != "text/csv":
        return JSONResponse(status_code=400, content={"error": "Only CSV file is supported"})
    try:
        contents = await file.read()
        with open(f"{file.filename}","wb") as tmp:
            tmp.write(contents)
    except requests.exceptions.RequestException as err:
        return {"error": f"Error occurred during file upload: {str(err)}"}
    try:
        indexing_stats = ingest_csv(file_path=f"{file.filename}", index_name=f"{token}-{index_name}")
        os.remove(f"{file.filename}")
        final_response = JSONResponse(status_code=200, content=f"file name - {file.filename} uploaded successfully with the following stats: {indexing_stats}")
        return final_response
    except requests.exceptions.RequestException as err:
        return JSONResponse(status_code=400, content={f"error: Error occurred during file upload: {str(err)}"})

# Ingest JSON
@router.post("/api/v1/upsert_json/")
async def upsert_json(
    file: Annotated[UploadFile, File()],
    index_name: Annotated[str, Form()],
    token: str = Depends(get_bearer_token),
):
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if file.content_type != "application/json":
        return JSONResponse(status_code=400, content={"error": "Only JSON file is supported"})
    try:
        contents = await file.read()
        with open(f"{file.filename}","wb") as tmp:
            tmp.write(contents)
    except requests.exceptions.RequestException as err:
        return {"error": f"Error occurred during file upload: {str(err)}"}
    try:
        indexing_stats = ingest_json(file_path=f"{file.filename}", index_name=f"{token}-{index_name}")
        os.remove(f"{file.filename}")
        final_response = JSONResponse(status_code=200, content=f"file name - {file.filename} uploaded successfully with the following stats: {indexing_stats}")
        return final_response
        
    except requests.exceptions.RequestException as err:
        return JSONResponse(status_code=400, content={f"error: Error occurred during file upload: {str(err)}"})

# Ingest PDF
@router.post("/api/v1/upsert_pdf/")
async def upsert_pdf(
    file: Annotated[UploadFile, File()],
    index_name: Annotated[str, Form()],
    token: str = Depends(get_bearer_token),
):
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"error": "Only PDF file is supported"})
    try:
        contents = await file.read()
        with open(f"{file.filename}","wb") as tmp:
            tmp.write(contents)
    except requests.exceptions.RequestException as err:
        return {"error": f"Error occurred during file upload: {str(err)}"}
    try:
        indexing_stats = ingest_pdf(file_path=f"{file.filename}", index_name=f"{token}-{index_name}")
        os.remove(f"{file.filename}")
        final_response = JSONResponse(status_code=200, content=f"file name - {file.filename} uploaded successfully with the following stats: {indexing_stats}")
        return final_response
    except requests.exceptions.RequestException as err:
        return JSONResponse(status_code=400, content={f"error: Error occurred during file upload: {str(err)}"})

# Ingest TXT
@router.post("/api/v1/upsert_txt/")
async def upsert_txt(
    file: Annotated[UploadFile, File()],
    index_name: Annotated[str, Form()],
    token: str = Depends(get_bearer_token),
):
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if file.content_type != "text/plain":
        return JSONResponse(status_code=400, content={"error": "Only TXT file is supported"})
    try:
        contents = await file.read()
        with open(f"{file.filename}","wb") as tmp:
            tmp.write(contents)
    except requests.exceptions.RequestException as err:
        return {"error": f"Error occurred during file upload: {str(err)}"}
    try:
        indexing_stats = ingest_txt(file_path=f"{file.filename}", index_name=f"{token}-{index_name}")
        os.remove(f"{file.filename}")
        final_response = JSONResponse(status_code=200, content=f"file name - {file.filename} uploaded successfully with the following stats: {indexing_stats}")
        return final_response
    except requests.exceptions.RequestException as err:
        return JSONResponse(status_code=400, content={f"error: Error occurred during file upload: {str(err)}"})



# Ingest EXCEL
@router.post("/api/v1/upsert_excel/")
async def upsert_excel(
    file: Annotated[UploadFile, File()],
    index_name: Annotated[str, Form()],
    token: str = Depends(get_bearer_token),
):
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) 
    if file.content_type not in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
        return JSONResponse(status_code=400, content={"error": "Only xls or xlsx files are supported"})
    try:
        contents = await file.read()
        with open(f"{file.filename}","wb") as tmp:
            tmp.write(contents)
    except requests.exceptions.RequestException as err:
        return {"error": f"Error occurred during file upload: {str(err)}"}
    try:
        indexing_stats = ingest_excel(file_path=f"{file.filename}", index_name=f"{token}-{index_name}")
        os.remove(f"{file.filename}") 
        final_response = JSONResponse(status_code=200, content=f"file name - {file.filename} uploaded successfully with the following stats: {indexing_stats}")
        return final_response
    except requests.exceptions.RequestException as err:
        return JSONResponse(status_code=400, content={f"error: Error occurred during file upload: {str(err)}"})


# Ingest PPT
@router.post("/api/v1/upsert_ppt/")
async def upsert_ppt(
    file: Annotated[UploadFile, File()],
    index_name: Annotated[str, Form()],
    token: str = Depends(get_bearer_token),
):
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if file.content_type != "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        return JSONResponse(status_code=400, content={"error": "Only PPTX file is supported"})
    try:
        contents = await file.read()
        with open(f"{file.filename}","wb") as tmp:
            tmp.write(contents)
    except requests.exceptions.RequestException as err:
        return {"error": f"Error occurred during file upload: {str(err)}"}
    try:
        indexing_stats = ingest_ppt(file_path=f"{file.filename}", index_name=f"{token}-{index_name}")
        os.remove(f"{file.filename}")
        final_response = JSONResponse(status_code=200, content=f"file name - {file.filename} uploaded successfully with the following stats: {indexing_stats}")
        return final_response
    except requests.exceptions.RequestException as err:
        return JSONResponse(status_code=400, content={f"error: Error occurred during file upload: {str(err)}"})


# Ingest DOC
@router.post("/api/v1/upsert_doc/")
async def upsert_doc(
    file: Annotated[UploadFile, File()],
    index_name: Annotated[str, Form()],
    token: str = Depends(get_bearer_token),
):
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if file.content_type != "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return JSONResponse(status_code=400, content={"error": "Only DOCX file is supported"})
    try:
        contents = await file.read()
        with open(f"{file.filename}","wb") as tmp:
            tmp.write(contents)
    except requests.exceptions.RequestException as err:
        return {"error": f"Error occurred during file upload: {str(err)}"}
    try:
        indexing_stats = ingest_doc(file_path=f"{file.filename}", index_name=f"{token}-{index_name}")
        os.remove(f"{file.filename}")
        final_response = JSONResponse(status_code=200, content=f"file name - {file.filename} uploaded successfully with the following stats: {indexing_stats}")
        return final_response
        
    except requests.exceptions.RequestException as err:
        return JSONResponse(status_code=400, content={f"error: Error occurred during file upload: {str(err)}"})
    

@router.delete("/api/v1/delete_all_vectors/{index_name}")
async def delete_vectors(
    index_name: str,
    token: str = Depends(get_bearer_token),
):
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        indexing_stats = delete_all_vectors(index_name=f"{token}-{index_name}")
        final_response = JSONResponse(status_code=200, content=f"All vectors for {index_name} deleted successfully with the following stats: {str(indexing_stats)}")
        return final_response
    except requests.exceptions.RequestException as err:
        return JSONResponse(status_code=400, content={f"error: Error occurred during vectors deletion: {str(err)}"})