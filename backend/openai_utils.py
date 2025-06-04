import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv() 


api_key=os.environ.get("OPENAI_API_KEY"),


if api_key is None:
    raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file")
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def chat_with_gpt(user_id: str, history: list, message: str) -> str:
    messages = [{
        "role": "system",
        "content": (
            "Your job is to help users schedule a tour by collecting key information step-by-step.\n\n"

            "Please collect the following 5 details from the user:\n"
            "1. Full name\n"
            "2. Email address (must be valid, e.g., someone@example.com)\n"
            "3. Phone number (must be a valid 10-digit mobile number)\n"
            "4. Move-in date (accept formats like YYYY-MM-DD or 'next month')\n"
            "5. Number of bedrooms needed\n\n"

            "For email, validate it contains '@' and a domain name.\n"
            "For phone number, ensure it's 10 digits and does not contain letters.\n"

            "Once you have **all five pieces of information**, respond:\n"
            "'Thank you! Type BOOK to confirm your tour.'\n"
            "Do not ask more questions after that. Wait for the user to type 'book'."
        )
    }]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": message})
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )

    return response.choices[0].message.content
