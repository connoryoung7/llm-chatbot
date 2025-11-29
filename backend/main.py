from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_ollama import ChatOllama
from langchain.tools import tool
from pydantic import BaseModel
import uvicorn
from ddgs import DDGS

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

class ChatRequest(BaseModel):
    message: str

@tool
def search_duckduckgo(query: str) -> str:
    """
    Searches the search engine DuckDuckGo and returns the content from the various web pages
    
    :param query: Description
    :type query: str
    :return: Description
    :rtype: str
    """
    result = DDGS().text(query, max_results=1)
    print(result)
    return "Hey there folks!"

llm = ChatOllama(
    model="gemma3:1b",
    temperature=0
)

llm_with_tools = llm.bind_tools([search_duckduckgo])

@app.get("/")
async def read_root():
    messages = [
        ("system", """You are a personal assistant. You are responsible for attempting to answer any question asked. If you do not have the answer, try searching DuckDuckGo to see if you can find the answer."""),
        ("human", "What is the capital of Norway?")
    ]
    response = llm_with_tools.invoke(messages)
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
