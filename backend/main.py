from fastapi import FastAPI
from langchain_ollama import ChatOllama
from pydantic import BaseModel
import uvicorn

app = FastAPI()

llm = ChatOllama(
    model="gemma3:1b"
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def read_root():
    messages = [
        ("human", "What is the capital of Norway?")
    ]
    response = llm.invoke(messages)
    return {"Hello": response.content}

@app.post("/chat")
async def generate_chat_response(body: ChatRequest):
    return {"message": body.message}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
