from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain.tools import tool
from pydantic import BaseModel
import uvicorn
from ddgs import DDGS

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

def search_duckduckgo(query: str) -> str:
    """
    Searches the search engine DuckDuckGo and returns the content from the various web pages
    
    :param query: Description
    :type query: str
    :return: Description
    :rtype: str
    """
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=10):
            results.append(f"{r['title']} - {r['body']}")
            
    return "\n".join(results)

@tool
def web_search(query: str) -> str:
    """Searches the web for a `query` and returns the title of each result from it."""
    return search_duckduckgo(query=query)

llm = ChatOllama(model="llama3.2:latest", temperature=0)

agent = create_agent(
    model=llm,
    tools=[web_search]
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

def stream_answer(message: str):
    for chunk in agent.stream(
        {
            "messages": [
                {"role": "system", "content": """You are a helpful assistant. If you cannot find current information, use the tool to search the web for the newest information.""" },
                {"role": "user", "content": message}
            ]
        },
        stream_mode="updates"
    ):
        for step, data in chunk.items():
            print(f"step: {step}")
            print(f"content: {data['messages'][-1].content_blocks}")
            event_str = "event: stream_event"
            content = "stuff"
            yield f"{event_str}\ndata: {content}\n\n"

@app.post("/chat")
def generate_chat_response(body: ChatRequest):
    return StreamingResponse(stream_answer(body.message), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
