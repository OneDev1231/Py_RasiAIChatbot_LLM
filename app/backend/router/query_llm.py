from typing import Annotated
from fastapi import APIRouter, HTTPException, Request, Depends, Form, status
from fastapi.responses import JSONResponse
import requests
import os
from dotenv import load_dotenv, find_dotenv
from supabase import create_client, Client

from pydantic import BaseModel

from langfuse import Langfuse

from app.LLM.graph.graph import query_llm
from app.backend.utilities.utilities import verify_token

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


class PromptItems(BaseModel):
    name: str
    business_name: str
    industry: str
    primary_language: str
    selected_functions: list[str]
    communication_style: str

@router.post("/api/v1/create_chatbot_prompt/")
async def create_chatbot_prompt(
    prompt_items: PromptItems,
    token: str = Depends(get_bearer_token),
):  
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        # Initialize Langfuse client
        langfuse = Langfuse()
        # Get current production version
        langfuse_prompt = langfuse.get_prompt("chatbot_onboarding_prompt")
        
        str_prompt = langfuse_prompt.compile(
                name=prompt_items.name,
                business_name=prompt_items.business_name,
                industry=prompt_items.industry,
                primary_language=prompt_items.primary_language,
                selected_functions=prompt_items.selected_functions,
                communication_style= prompt_items.communication_style
            )
        
        str_content = str_prompt[0]['content']
        final_response = JSONResponse(status_code=200, content=str_content)
        return final_response
    except requests.exceptions.RequestException as err:
        return JSONResponse(status_code=400, content={f"error: Error occurred during creating the prompt creation: {str(err)}"})



@router.post("/api/v1/query_llm/")
async def chat_with_llm(
    query: Annotated[str, Form()],
    prompt: Annotated[str, Form()],
    index_name: Annotated[str, Form()],
    thread_id: Annotated[str, Form()],
    token: str = Depends(get_bearer_token),
):  
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        response = query_llm(query=query, index_name=f"{token}-{index_name}", thread_id=thread_id, prompt=prompt)
        final_response = JSONResponse(status_code=200, content=response['messages'][-1].content)
        return final_response
    except requests.exceptions.RequestException as err:
        return JSONResponse(status_code=400, content={f"error: Error occurred during query: {str(err)}"})
