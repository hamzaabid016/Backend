import os
import re
from openai import OpenAI

client = OpenAI(
    api_key= os.getenv('OPENAI_API_KEY')
)

def generate(conversation:list,bill: dict): 
    response =  client.chat.completions.create(
                messages=[
                     {
                    "role": "system",
                    "content": f"You are an assistant that helps users interact with bill information.\n\n"
                   f"Bill Name: {bill_info['bill_name']}\n"
                   f"Bill Number: {bill_info['bill_number']}\n"
                   f"Sponsor: {bill_info['sponsor']}\n"
                   f"Summary: {bill_info['summary']}\n"
                   f"Status: {bill_info['status']}\n"
                   f"Introduced Date: {bill_info['introduced_date']}"
                    },
                    {
                        "role": "user",  # User-provided input
                        "content": f"Summarize the following text:\n\n{text}"
                    }
                ],
                model="gpt-3.5-turbo",
            )
    assitant_response = response.choices[0].message.content.strip()

    # Add the assistant's response to the conversation
    conversation.append({
        "role": "assistant", 
        "content": assitant_response
    })
    return conversation
