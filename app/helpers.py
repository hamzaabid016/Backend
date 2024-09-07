
import os
import requests

import re
import pdfplumber
from openai import OpenAI

client = OpenAI(
    api_key= os.getenv('OPENAI_API_KEY')
)

def generate(text:str): 
    response =  client.chat.completions.create(
                messages=[
                    {
                        "role": "system",  # Set the assistant's behavior
                        "content": "You are a summarizing assistant."
                    },
                    {
                        "role": "user",  # User-provided input
                        "content": f"Summarize the following text:\n\n{text}"
                    }
                ],
                model="gpt-3.5-turbo",
            )
    summary = response.choices[0].message.content.strip()
    return summary

def split_text(text: str, max_characters: int) -> list:
    chunks = []
    while len(text) > max_characters:
        split_index = text.rfind(' ', 0, max_characters)
        if split_index == -1:
            split_index = max_characters
        
        chunks.append(text[:split_index].strip())
        text = text[split_index:].strip()
    
    if text:
        chunks.append(text)
    
    return chunks

def generate_summary(text: str) -> str:
    if len(text) > 15000:
        try:
            max_characters = 15000  # Adjust based on testing
        
            chunks = split_text(text, max_characters)
            section_summaries = [generate(chunk) for chunk in chunks]
        
            combined_summary = ' '.join(section_summaries)
            final_summary = generate(combined_summary)
        
            return combined_summary
        except Exception as e:
            return f"Error generating summary {e}"
    else:    
        try:
            response = generate(text)
            return response
        except Exception as e:
            return f"Error generating summary {e}"



def convert_to_pdf_url(general_url):
    parts = general_url.strip('/').split('/')
    
    if len(parts) < 2:
        raise ValueError("Invalid URL format")
    
    session = parts[1]  # '37-1'
    bill_number = parts[2]  # 'C-330'
    # Remove the dash in the session to form '371'
    session_number = session.replace('-', '')
    
    # Assume the bill type is 'Private' (can be adjusted based on your needs)
    bill_type = "Private"
    
    # Construct the PDF URL
    pdf_url = f"https://www.parl.ca/Content/Bills/{session_number}/{bill_type}/{bill_number}/{bill_number.lower()}_1/{bill_number.lower()}_1.pdf"
    
    return pdf_url

def clean_text(text: str) -> str:
    # Remove unwanted characters and excessive whitespace
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces/newlines with a single space
    text = re.sub(r'\(cid:\d+\)', '', text)  # Remove PDF encoding artifacts like (cid:1)
    text = text.strip()
    return text


def fetch_pdf_text(pdf_url: str) -> str:
    response = requests.get(pdf_url)
    if response.status_code != 200:
        pdf_url = pdf_url.replace("/Private/", "/Government/")
        response = requests.get(pdf_url)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="PDF not found")

    with open("temp.pdf", "wb") as f:
        f.write(response.content)

    text = ""
    with pdfplumber.open("temp.pdf") as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    # Remove temp file
    os.remove("temp.pdf")
    return text
