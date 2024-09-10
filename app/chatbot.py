import os
import re
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)


def generate(conversation: list, bill_info: dict): 
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an assistant that helps users interact with bill information.\n\n"
                    f"Bill Name: {bill_info['bill_name']}\n"
                    f"Bill Number: {bill_info['bill_number']}\n"
                    f"Summary: {bill_info['summary']}\n"
                    f"Status: {bill_info['status']}\n"
                    f"Introduced Date: {bill_info['introduced_date']}\n"
                )
            },
            {
                "role": "assistant",
                "content": f"The bill '{bill_info['bill_name']}' is being discussed. What would you like to know about it?"
            }
        ],
        model="gpt-3.5-turbo",
    )
    assistant_response = response.choices[0].message['content'].strip()

    # Add the assistant's response to the conversation
    conversation.append({
        "role": "assistant",
        "content": assistant_response
    })
    return conversation