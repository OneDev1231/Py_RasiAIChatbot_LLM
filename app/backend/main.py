from fastapi import Depends, FastAPI, File, Form, HTTPException
from fastapi.responses import RedirectResponse

from fastapi.middleware.cors import CORSMiddleware

from app.backend.router import vectors_store
from app.backend.router import query_llm


from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


app = FastAPI(title="Rasi LLM APIs",
    version="1.0",
    description="APIs server")


allowed_origins = [
    "http://localhost",
    "http://localhost:8100", 
    "https://www.rasi.ai",
    "https://llm.rasi.ai",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vectors_store.router, tags=["vectors_store"])
app.include_router(query_llm.router, tags=["query_llm"])
# app.add_exception_handler(HTTPException, custom_http_exception_handler)

@app.get("/", tags=["root"])
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8100)
