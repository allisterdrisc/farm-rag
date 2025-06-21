import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import numpy as np
from pydantic import BaseModel, Field
from typing import List
import instructor
import shutil
import re

load_dotenv()

API_KEY = os.getenv('OPENAI_API_KEY')

client = instructor.from_provider(
    model="openai/gpt-4o",
    mode=instructor.Mode.RESPONSES_TOOLS,
)

# Define the structure crop data should adhere to
class Crop(BaseModel):
    name: str = Field(description="Name of crop, for ex: radish, carrot, corn")
    total_seed_cost: float = Field(description="Total cost of the crop's seeds in dollars")
    pounds_harvested: int = Field(description="Amount harvested in pounds")
    total_revenue: float = Field(description="Total revenue from selling the crop in dollars")
    total_profit: float = Field(description="Total profit made from the crop after subtracting seed cost in dollars")

def get_db_connection():
    return psycopg2.connect(
        dbname="farm_db",
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host="localhost",
        port='5432',
    )

def create_tables(conn):
    """Create crop_entries table if not exists, including vector extension for embeddings."""
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS crop_entries (
                id SERIAL PRIMARY KEY,
                name TEXT,
                total_seed_cost FLOAT,
                pounds_harvested INT,
                total_revenue FLOAT,
                total_profit FLOAT,
                embedding vector(1536)
            );
        """)
    conn.commit()

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from the PDF and return as a single string."""
    texts = []
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text = page.extract_text()
            if text and text.strip():
                texts.append(text.strip())
    return "\n".join(texts)

def parse_crop_data(text: str) -> List[Crop]:
    prompt_messages = [
        {"role": "system", "content": "You are a helpful assistant that extracts structured crop data from text."},
        {"role": "user", "content": f"Extract crop data from the following text and return it as a JSON array matching the Crop schema: {text}"}
    ]
    try:
        response = client.chat.completions.create(
            messages=prompt_messages,
            response_model=List[Crop],  # instructs Instructor to return validated objects
            model="gpt-4o"
        )
        return response  # List[Crop] is returned directly thanks to Instructor
    except Exception as e:
        print(f"Error parsing crop data: {e}")
        return []

def generate_embedding(text: str):
    """Generate an embedding vector for the given text."""
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def normalize_crop_name(name: str) -> str:
    """Simplify crop name variants into the known crop name. Ex: 'Kale Dino - Big Y A' => 'Kale'"""
    name = name.strip().lower()
    
    known_crops = [
      "kale", "lettuce", "squash", "tomato", "radish", "carrot", "beet",
        "onion", "pepper", "potato", "turnip", "eggplant", "arugula",
        "leek", "cabbage", "popcorn", "dry beans", "sweet potato", "arugula"
    ]

    for crop in known_crops:
        if crop in name:
            return crop.title()

    return name.title()

def store_crops(crops: List[Crop], conn):
    """Store crop data and embeddings in the database."""
    with conn.cursor() as cur:
        for crop in crops:
            clean_name = normalize_crop_name(crop.name)
            # Create a text summary for embedding (you can customize this)
            summary_text = (
                f"{crop.name}, seed cost: {crop.total_seed_cost}, "
                f"harvested: {crop.pounds_harvested} lbs, revenue: {crop.total_revenue}, "
                f"profit: {crop.total_profit}"
            )
            embedding = generate_embedding(summary_text)
            if embedding is None:
                print(f"Embedding failure.")
                continue
            
            cur.execute("""
                INSERT INTO crop_entries 
                (name, detailed_name, total_seed_cost, pounds_harvested, total_revenue, total_profit, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                clean_name,
                crop.name,
                crop.total_seed_cost,
                crop.pounds_harvested,
                crop.total_revenue,
                crop.total_profit,
                embedding
            ))
        conn.commit()

def split_pdf(input_path, page_ranges, output_folder):
    """Split input PDF into smaller PDFs based on page ranges."""
    reader = PdfReader(input_path)
    os.makedirs(output_folder, exist_ok=True)
    
    for i, (start, end) in enumerate(page_ranges):
        writer = PdfWriter()
        for page_num in range(start-1, end):  # PyPDF2 uses 0-based indexing
            writer.add_page(reader.pages[page_num])
        output_path = os.path.join(output_folder, f"part_{i+1}.pdf")
        with open(output_path, 'wb') as f_out:
            writer.write(f_out)
    print(f"Split PDF saved in {output_folder}")

def process_and_store_pdfs(pdf_folder: str):
    """Process all PDFs in a folder, parse crops, and store them in database."""
    conn = get_db_connection()
    create_tables(conn)

    for filename in os.listdir(pdf_folder):
        if filename.lower().endswith('.pdf'):
            path = os.path.join(pdf_folder, filename)
            print(f"Processing {filename}...")
            text = extract_text_from_pdf(path)
            crops = parse_crop_data(text)
            if crops:
                print(f"Parsed {len(crops)} crops from {filename}. Storing...")
                store_crops(crops, conn)
            else:
                print(f"No crops found in {filename}.")
    conn.close()

def clear_crop_entries(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM crop_entries;")
    conn.commit()


if __name__ == "__main__":
    input_pdf_path = "../data/full_farm_book.pdf"
    output_folder = "../data/split_pdfs"

    # Clear old split PDFs
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    page_ranges = [
        (121, 124), (125, 128), (129, 133), (146, 150),
        (151, 157), (163, 167), (168, 173), (191, 197),
        (198, 202), (203, 207), (208, 212), (218, 222),
        (223, 226), (227, 231), (238, 242), (269, 274),
        (280, 287), (288, 295)
    ]

    split_pdf(input_pdf_path, page_ranges, output_folder)

    # Clear DB entries
    conn = get_db_connection()
    clear_crop_entries(conn)
    conn.close()

    # Process new PDFs
    process_and_store_pdfs(output_folder)