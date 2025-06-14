import os
import psycopg2
from dotenv import load_dotenv
from openai import OpenAI

MODEL = 'gpt-4o-mini'

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_db_connection():
    return psycopg2.connect(
        dbname="farm_db",
        user=os.getenv('POSTGRES_USER'), 
        password=os.getenv('POSTGRES_PASSWORD'),
        host="localhost",
        port='5432',
    )

def generate_embedding(text):
    """Generate embedding vector for the input text using OpenAI."""
    if not text:
        print("Warning: empty text for embedding.")
        return None
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",  # or your preferred model
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding error: {str(e)}")
        return None

def search_similar_crops(query, limit=5):
    """Search PostgreSQL for entries similar to the query based on embeddings."""
    query_embedding = generate_embedding(query)
    if query_embedding is None:
        return []

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT name, 
                       CONCAT('Seed cost: $', total_seed_cost, ', Harvested: ', pounds_harvested, ' lbs, Revenue: $', total_revenue, ', Profit: $', total_profit) as description,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM crop_entries
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (query_embedding, query_embedding, limit))

            results = cur.fetchall()
            formatted = [{
                'crop_name': row[0],
                'description': row[1],
                'similarity': row[2]
            } for row in results]
            return formatted
    finally:
        conn.close()

def format_rag_prompt(relevant_crops):
    """Format the RAG prompt with context and question."""
    prompt = (
        "You are an expert farm management assistant helping a farmer analyze and optimize crop decisions. "
        "Use the crop data provided to answer the user's questions clearly and specifically. "
        "Base all answers strictly on the information provided below. "
        "If the data is insufficient, say so instead of guessing. Keep answers practical and focused on numbers, comparisons, and insights.\n\n"
        "Relevant crop data:\n"
    )
    for crop in relevant_crops:
        prompt += f"Crop: {crop['crop_name']}\nDescription: {crop['description']}\n\n"
    return prompt

def get_llm_response(prompt, question):
    """Get response from OpenAI's API."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question}
        ],
    )
    return response.choices[0].message.content

def process_query(question):
    """Process a query and return the response with sources."""
    if not question.strip():
        return "Please enter a question about your farm data."

    relevant_crops = search_similar_crops(question, limit=3)
    if not relevant_crops:
        return "No relevant crop data found."

    prompt = format_rag_prompt(relevant_crops)
    response = get_llm_response(prompt, question)

    # Add similarity-based sources
    sources = "\n\nSources:\n" + "\n".join([
        f"- {entry['crop_name']} (Similarity: {entry['similarity']:.2f})"
        for entry in relevant_crops
    ])

    return response + sources