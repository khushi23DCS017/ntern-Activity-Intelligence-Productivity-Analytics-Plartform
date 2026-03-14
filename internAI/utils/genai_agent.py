# pyre-ignore-all-errors
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_groq import ChatGroq


from utils.db_config import get_db_uri

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_sql_agent(role: str, username: str, db_uri: str = None):
    """
    Creates a LangChain SQL agent connected to the specified database URI.
    Uses Groq for the LLM. It injects custom system prompts based on the user's role to restrict data access.
    """
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        raise ValueError("Groq API Key is missing. Add GROQ_API_KEY to your .env file (see SETUP.md)")

    if db_uri is None:
        db_uri = get_db_uri()

    # Connect to PostgreSQL
    db = SQLDatabase.from_uri(db_uri)

    # Initialize the LLM (Groq - fast, free tier available)
    llm = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile")

    # Define Role-Based System Prompts for Security and Context
    base_instructions = """
    You are a helpful, professional AI analytics assistant for the 'Intern Analytics Platform'.
    Your job is to answer questions by querying the SQL database. 
    The database tracks intern learning progress, courses, mentors, and daily activities logged in hours.
    Always return your final answer in clean, readable Markdown format. Do NOT expose internal IDs, use the actual names (e.g., intern_name, course_name).
    """

    if role == "manager":
        role_instructions = """
        The current user is a Manager. They have full access to all organization data.
        Feel free to run aggregate queries comparing different interns, mentors, and departments.
        """
    elif role == "employee":
        role_instructions = f"""
        The current user is a Mentor named '{username}'. 
        CRITICAL SECURITY RULE: You MUST ONLY query data for interns where the mentor is '{username}'. 
        If you join the dim_intern or dim_mentor tables, always include `WHERE mentor_name = '{username}'`. 
        If the user asks about an intern assigned to a different mentor, respectfully decline to answer citing privacy constraints.
        """
    elif role == "intern":
        role_instructions = f"""
        The current user is an Intern named '{username}'. 
        CRITICAL SECURITY RULE: You MUST ONLY query data where the intern_name is '{username}'.
        Always append `WHERE intern_name = '{username}'` or equivalent joins to restrict the data.
        Refuse any request to view another intern's data, test scores, or activities. You are their personal study buddy.
        """
    else:
        role_instructions = "You have standard read-only access to the analytics."

    system_message = base_instructions + "\n" + role_instructions

    # Create the Agent using tool-calling (Groq supports Llama tool use)
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="tool-calling",
        verbose=True,
        agent_executor_kwargs={
            "handle_parsing_errors": True,
        }
    )

    # We attach the specialized system prompt dynamically
    def safe_query(question: str):
        full_prompt = f"System Instructions: {system_message}\n\nUser Question: {question}"
        try:
            result = agent_executor.invoke({"input": full_prompt})
            return result["output"]
        except Exception as e:
            return f"⚠️ I encountered an error running that query: {str(e)}"

    return safe_query
