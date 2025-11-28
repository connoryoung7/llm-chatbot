from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_ollama import ChatOllama
from pydantic import BaseModel
import uvicorn

import time

app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOllama(
    model="gemma3:1b",
    temperature=0
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

def stream_answer(message):
    messages = [
        ("human", message)
    ]

    for chunk in llm.stream(messages):
        event_str = "event: stream_event"
        yield f"{event_str}\ndata: {chunk.content}\n\n"
        time.sleep(0.1)

@app.post("/chat")
def generate_chat_response(body: ChatRequest):
    return StreamingResponse(stream_answer(body.message), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
