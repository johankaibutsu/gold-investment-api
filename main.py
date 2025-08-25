import os
import google.generativeai as genai
from openai import OpenAI
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import List, Optional

# Database stuff

from sqlalchemy.orm import Session
import database
from database import SessionLocal, engine

database.create_db_and_tables()

load_dotenv()

app = FastAPI(
    title="Financial Assistant API",
    description="An API that answers financial questions and conditionally nudges users to invest in digital gold, using LLMs.",
    version="0.1.0"
)

# Load Google API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")
genai.configure(api_key=api_key)

# Load OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

class ChatQuery(BaseModel):
    user_id: str = Field(..., example="user123", description="A unique identifier for the user.")
    question: str = Field(..., example="What are the benefits of investing in gold?", description="The user's question.")

class ChatResponse(BaseModel):
    llm_answer: str
    action_to_perform: Optional[str] = Field(None, example="call_investment_options", description="A command for the client app.")

class InvestmentOption(BaseModel):
    plan_name: str
    duration_months: int
    min_investment: float
    description: str

class InvestmentSteps(BaseModel):
    options: List[InvestmentOption]
    purchase_steps: List[str]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- THE SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are "FinBot", a helpful financial assistant. Your expertise is strictly limited to finance, investing, economics, and market analysis.

Follow these rules strictly:
1.  **Analyze the user's query:** First, determine if the question is related to your area of expertise (finance, investing, etc.).
2.  **Handle Off-Topic Queries:** If the question is NOT related to finance (e.g., asking about cooking, sports, history), you MUST respond with the exact phrase: "I can't help you with this" and nothing more.
3.  **Handle On-Topic Queries:** If the question IS finance-related, provide a clear and accurate answer.
4.  **Conditional Nudge:** After answering a finance-related question, check if the user's original query contained the words "gold" or "investment".
    -   If it did, and ONLY if it did, you MUST add a persuasive nudge for the user to consider digital gold. End this nudge with the question: "Would you like to see some digital gold investment options?"
    -   If it did not mention "gold" or "investment", simply answer the question and do not add any nudge.
"""

# --- Initialize the Gemini Model with the System Prompt ---
# gemini_model = genai.GenerativeModel(
#     model_name='gemini-1.5-pro-latest',
#     system_instruction=SYSTEM_PROMPT
# )


# --- API Endpoints ---

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "Financial Assistant API is running!"}

@app.post("/chat", response_model=ChatResponse, tags=["Finance Chat"])
def handle_chat_query(query: ChatQuery, db: Session = Depends(get_db)):
    nudge_trigger_phrase = "Would you like to see some digital gold investment options?"
    affirmative_responses = ["yes", "sure", "ok", "yep", "yes please", "yes sure", "go ahead"]

    last_log = db.query(database.ConversationLog).filter(database.ConversationLog.user_id == query.user_id).order_by(database.ConversationLog.id.desc()).first()

    if last_log and last_log.bot_response and last_log.bot_response.strip().endswith(nudge_trigger_phrase):
        if query.question.lower().strip() in affirmative_responses:
            bot_reply = "Great! Here are the investment options available for you."
            db_log = database.ConversationLog(user_id=query.user_id, user_prompt=query.question, bot_response=bot_reply)
            db.add(db_log)
            db.commit()

            return ChatResponse(
                llm_answer=bot_reply,
                action_to_perform="call_investment_options"
            )
    db_log = database.ConversationLog(user_id=query.user_id, user_prompt=query.question)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    try:
        # response = gemini_model.generate_content(query.question)
        # llm_response_text = response.text
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query.question}
            ]
        )
        llm_response_text = completion.choices[0].message.content
        db_log.bot_response = llm_response_text
        db.commit()
        return ChatResponse(llm_answer=llm_response_text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred with the LLM API: {str(e)}")


@app.get("/invest/options", response_model=InvestmentSteps, tags=["Investment"])
def get_investment_options():
    # This endpoint remains the same. It's the destination.
    mock_options = [
        InvestmentOption(plan_name="Gold Starter Pack", duration_months=6, min_investment=500.00, description="A perfect plan for beginners."),
        InvestmentOption(plan_name="Steady Saver", duration_months=12, min_investment=1000.00, description="Systematically invest every month for a year."),
        InvestmentOption(plan_name="Wealth Builder", duration_months=24, min_investment=2500.00, description="A long-term plan for serious investors.")
    ]
    mock_steps = ["1. Select a plan.", "2. Complete KYC.", "3. Make payment.", "4. Gold is credited!"]
    return InvestmentSteps(options=mock_options, purchase_steps=mock_steps)
