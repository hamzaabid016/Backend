import os
import re
from openai import OpenAI,OpenAIError
from fastapi import HTTPException

# Initialize the OpenAI client
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)


def generate(conversation: list, bill_info: dict): 
    try:
        # Create a response from the OpenAI API
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that provides information about bills. Respond concisely and helpfully. "
                        "Here are the details of the bill:\n"
                        f"Bill Name: {bill_info['bill_name']}\n"
                        f"Bill Number: {bill_info['bill_number']}\n"
                        f"Summary: {bill_info['summary']}\n"
                        f"Status: {bill_info['status']}\n"
                        f"Introduced Date: {bill_info['introduced_date']}\n"
                        "Please ensure your responses are relevant, detailed, and free from unnecessary repetition."
                    )
                },
                # Add the previous conversation history
                *conversation
            ],
            model="gpt-3.5-turbo",
        )
        
        # Extract the assistant's response
        assistant_response = response.choices[0].message.content.strip()
        
        # Add the assistant's response to the conversation
        conversation.append({
            "role": "assistant",
            "content": assistant_response
        })
        
        return conversation
    
    except OpenAIError as openai_err:
        # Handle OpenAI specific exceptions
        raise HTTPException(status_code=500, detail=f"OpenAI API error occurred: {openai_err}")
    
    except Exception as ex:
        # Handle other exceptions
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {ex}")