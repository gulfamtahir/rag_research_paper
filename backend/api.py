from agno.agent import Agent , RunResponse
from agno.knowledge.pdf import PDFKnowledgeBase, PDFImageReader
from agno.models.google import Gemini
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.tools.reasoning import ReasoningTools
from agno.document.chunking.agentic import AgenticChunking
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.storage.sqlite import SqliteStorage
from fastapi import FastAPI , UploadFile , File, Depends, HTTPException
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from agno.embedder.ollama import OllamaEmbedder
from agno.embedder.openai import OpenAIEmbedder
from agno.models.openai import OpenAIChat
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI()

# Define the request body model
class QueryRequest(BaseModel):
    question: str

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only - restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize knowledge_base as None

def get_knowledge_base()-> PDFKnowledgeBase:
    """Initialize the knowledge base for Agentic RAG Agent."""
    # Create a knowledge base from PDF files
    # This will process the PDF files and store embeddings in LanceDB
    # Ensure the path points to the directory containing your PDF files
    if not os.path.exists("temp/pdf_data"):
        raise HTTPException(status_code=404, detail="PDF directory not found. Make a folder named 'pdf_data' in the 'temp' directory and upload your PDF files there.")
    else:
        print("PDF's do exist and is accessible.")
        
        return PDFKnowledgeBase(
        path="temp/pdf_data",  # Replace with actual path to PDF file
        vector_db=LanceDb(
            table_name="research_papers",
            uri="temp/lancedb",
            search_type=SearchType.hybrid,  # Use hybrid search for better results
            embedder=OpenAIEmbedder(),
            
            # reranker=CohereReranker(model="rerank-multilingual-v3.0"),
        ),
        reader=PDFImageReader(),
        num_documents=3,  # Number of documents to process
        chunking_strategy=AgenticChunking(model='gemini-2.0-flash-exp'),  # Use AgenticChunking for better context handling


    )

def check_lancedb_exists():
    """Check if the LanceDB database exists."""
    db_path = "temp/lancedb/research_papers.lance"
    if os.path.exists(db_path):
        print(f"LanceDB database found at {db_path}")
        return True
    else:
        print(f"LanceDB database not found at {db_path}")
        raise HTTPException(status_code=404, detail="LanceDB database not found. Please upload a PDF file to create the database.")

def get_agentic_rag_agent(
    model_id: str = "gemini-2.0-flash-exp",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
    knowledge_base: PDFKnowledgeBase = Depends(get_knowledge_base),
)-> Agent:
    """Get an Agentic RAG Agent with Memory."""

    # create the Agentic RAG Agent
    return Agent(
    name="agentic_rag_agent",
    session_id=session_id,  # Track session ID for persistent conversations
    user_id=user_id,
    model=OpenAIChat(id="gpt-4o",temperature=0.3),  # Use Gemini model for responses
    storage=SqliteStorage(
        table_name="research_paper_sessions",
        db_file="temp/sqlite_storage.db",  # Use a local SQLite database for session storage
    ),  # Persist session data
    knowledge=knowledge_base,  # Add knowledge base
    description="You are a helpful Agent called 'Agentic RAG' and your goal is to assist the user in the best way possible.",
    instructions=[
        "1. Knowledge Base Search:",
        "   - ALWAYS start by searching the knowledge base using search_knowledge_base tool",
        "   - Analyze ALL returned documents thoroughly before responding",
        "   - If multiple documents are returned, synthesize the information coherently",
        "2. External Search:",
        "   - If knowledge base search yields no /irrelevant results, use duckduckgo_search",
        "   - Focus on reputable sources and recent information",
        "   - Cross-reference information from multiple sources when possible",
        "3. Context Management:",
        "   - Use get_chat_history tool to maintain conversation continuity",
        "   - Reference previous interactions when relevant",
        "   - Keep track of user preferences and prior clarifications",
        "4. Response Quality:",
        "   - Provide specific citations and sources for claims",
        "   - Structure responses with clear sections and bullet points when appropriate",
        "   - Include relevant quotes from source materials",
        "   - Avoid hedging phrases like 'based on my knowledge' or 'depending on the information'",
        "5. User Interaction:",
        "   - Ask for clarification if the query is ambiguous",
        "   - Break down complex questions into manageable parts",
        "   - Proactively suggest related topics or follow-up questions",
        "6. Error Handling:",
        "   - If no relevant information is found, clearly state this",
        "   - Suggest alternative approaches or questions",
        "   - Be transparent about limitations in available information",
    ],
    search_knowledge=True,  # This setting gives the model a tool to search the knowledge base for information
    read_chat_history=True,  # This setting gives the model a tool to get chat history
    tools=[DuckDuckGoTools(), ReasoningTools(add_instructions=True)],  # Add reasoning tools and DuckDuckGo search tool
    markdown=True,  # This setting tellss the model to format messages in markdown
    # add_chat_history_to_messages=True,
    show_tool_calls=True,
    add_history_to_messages=True,  # Adds chat history to messages
    add_datetime_to_instructions=True,
    debug_mode=debug_mode,
    read_tool_call_history=True,
    num_history_responses=3,
    enable_agentic_memory=True,
)


@app.get('/')
def read_root():
    return {'message': 'Welcome to the Shopping List App'}



@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...), knowledge_base: PDFKnowledgeBase = Depends(get_knowledge_base)):
    try:
        # Ensure the file is a PDF
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Ensure the 'temp' directory exists
        temp_dir = "temp/pdf_data"  # Directory to store temporary files
        if not os.path.exists(temp_dir):
            print(f"Creating directory: {temp_dir} in {os.getcwd()}")  # Debug log
            os.makedirs(temp_dir, exist_ok=True)  # Ensure no error if directory already exists

        # Save the uploaded file temporarily
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Check if the file was successfully created
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Failed to save the uploaded file")
        
        knowledge_base.load(recreate=False, upsert=True, skip_existing=True)  # Load the knowledge base, recreating it if necessary

         # Load the knowledge base, recreating it if necessary

        # Simulate processing the PDF (e.g., storing embeddings)
        # Add your processing logic here

        return {"message": "PDF processed and embeddings stored"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    # finally:
    #     # Delete the uploaded file
    #     if file_path and os.path.exists(file_path):
    #         print(f"Deleting temporary file: {file_path}")  # Debug log
    #         os.remove(file_path)
    # finally:
    #     # Clean up: Remove the temporary file if it exists
    #     if os.path.exists(file_path):
    #         os.remove(file_path)

@app.post("/query/")
async def query_document(request: QueryRequest,  lancedb_exists: bool = Depends(check_lancedb_exists), agent: Agent = Depends(get_agentic_rag_agent)):
    try:
        query = request.question  # Extract the question from the request body
        print(f"Running query: {query}")
        response: RunResponse = agent.run(query)
        print(f"Query response: {response.content}")

        return {"answer": response.content}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


if __name__ == "__main__":
    #getting the agent
    # agent = get_agentic_rag_agent()
    # agent.print_response('what are the authors name of the Deep learning Certification')

    uvicorn.run(
        app="api:app",  # Specify the FastAPI app instance
        host="0.0.0.0",  # Listen on all interfaces
        port=8000,       # Specify the port
        reload=True      # Enable auto-reloading
    )