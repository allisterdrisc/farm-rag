from langchain.tools import tool
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
import os
from openai import OpenAI
from dotenv import load_dotenv
from rag_tools import process_query, get_db_connection

load_dotenv()

API_KEY = os.getenv('OPENAI_API_KEY')
MODEL = 'gpt-4o-mini'

client = OpenAI(api_key=API_KEY)

# tools for the farm agent
@tool
def rag_query_tool(question: str) -> str:
    """LangChain tool wrapping the RAG query process."""
    return process_query(question)

@tool
def most_cost_efficient_crop() -> str:
    """Finds the crop that has the highest profit to seed cost ratio"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT detailed_name, total_profit, total_seed_cost,
                       (total_profit / NULLIF(total_seed_cost, 0)) AS efficiency
                FROM crop_entries
                WHERE total_profit IS NOT NULL AND total_seed_cost IS NOT NULL AND total_seed_cost != 0
                ORDER BY efficiency DESC
                LIMIT 1
            """)
            row = cur.fetchone()
            if row:
                name, profit, seed_cost, efficiency = row
                return f"{name} is the most cost-efficient crop with a profit-to-seed-cost ratio of {efficiency:.2f}."
            else:
                return "No valid crop data found in the database."
    except Exception as e:
        return f"Error during query: {str(e)}"
    finally:
        conn.close()

@tool
def most_profitable_crop() -> str:
    """Finds the crop with the highest total profit."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT detailed_name, total_profit
                FROM crop_entries
                WHERE total_profit IS NOT NULL
                ORDER BY total_profit DESC
                LIMIT 1
            """)
            row = cur.fetchone()
            if row:
                name, profit = row
                return f"{name} had the largest profit: ${profit:.2f}."
            else:
                return "No valid profit data found."
    except Exception as e:
        return f"Error during query: {str(e)}"
    finally:
        conn.close()

@tool
def largest_harvest_crop() -> str:
    """Finds the crop with the largest total harvest in pounds."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT detailed_name, pounds_harvested
                FROM crop_entries
                WHERE pounds_harvested IS NOT NULL
                ORDER BY pounds_harvested DESC
                LIMIT 1
            """)
            row = cur.fetchone()
            if row:
                name, pounds = row
                return f"{name} had the largest harvest with {pounds:.2f} pounds."
            else:
                return "No harvest data found."
    except Exception as e:
        return f"Error during query: {str(e)}"
    finally:
        conn.close()

@tool
def list_all_crops() -> str:
    """Returns a list of all the crops from the provided data."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT name FROM crop_entries")
            rows = cur.fetchall()
            if rows:
              crops = [row[0].strip() for row in rows if row[0]]
              return f"The crops listed in your data are: {', '.join(crops)}."
            else:
              return "No crops were found in your data."
    except Exception as e:
        return f"Error during query: {str(e)}"
    finally:
        conn.close()

tools = [rag_query_tool, most_cost_efficient_crop, most_profitable_crop, largest_harvest_crop, list_all_crops]

# agent setup
llm = ChatOpenAI(model=MODEL, temperature=0, api_key=API_KEY)
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True  # Print output to see the agent process
)

def ask_farm_agent(question: str) -> str:
    """Helper for Gradio to send a question to the agent."""
    try:
        return agent.run(question)
    except Exception as e:
        return f"Error: {str(e)}"
