import json
from models import Session
from email_utils import send_email
from openai_utils import chat_with_gpt

user_histories = {}

def handle_message(message: str, session: Session,db) -> str:
    fields = json.loads(session.fields)

    # ✅ LLM Mode
    if session.state == "llm_mode":
        history = user_histories.get(session.user_id, [])
        history.append({"role": "user", "content": message})
        print(history)
        # 📩 If user says 'book', extract info + send email
        if message.strip().lower() == "book":
            collected = extract_fields_from_history(history)

            # if all values collected, send email
            if all(collected.values()):
                session.fields = json.dumps(collected)  
                session.state = "booked"
                print(session.fields)
                db.commit() 
                name = collected["name"]
                email = collected["email"]
                beds = collected["beds"]
                unit_id = f"APT-{beds}01"

                email_msg = (
                    f"Hi {name},\n\n"
                    f"Thank you for your interest! Here's your tour confirmation:\n\n"
                    f"📍 Property: 123 Main Street\n"
                    f"🏠 Unit ID: {unit_id}\n"
                    f"📅 Suggested tour time: Tomorrow at 3 PM\n\n"
                    f"– The Leasing Team"
                )

                send_email(email, "Tour Confirmation – Homewiz", email_msg)

                return (
                    f"Hi {name}, your tour is confirmed!\n"
                    f"📍 Property: 123 Main Street\n"
                    f"🏠 Unit: {unit_id}\n"
                    f"📅 Time: Tomorrow at 3 PM\n\n"
                    f"An email confirmation has been sent to {email}."
                )
            else:
                return "Sorry, I couldn’t find your name, email, or bedroom preference. Please make sure you’ve provided all details."

        # 🤖 Otherwise, continue chat
        reply = chat_with_gpt(session.user_id, history[:-1], message)
        history.append({"role": "assistant", "content": reply})
        user_histories[session.user_id] = history
        return reply

    # 🧱 Classic flow (fallback)
    if session.state == "start":
        session.state = "awaiting_name"
        return "Hi! What's your name?"

    elif session.state == "awaiting_name":
        fields["name"] = message.strip()
        session.state = "awaiting_email"
        session.fields = json.dumps(fields)
        return "Thanks! What's your email?"

    elif session.state == "awaiting_email":
        fields["email"] = message.strip()
        session.state = "awaiting_phone"
        session.fields = json.dumps(fields)
        return "Got it. What's your phone number?"

    elif session.state == "awaiting_phone":
        fields["phone"] = message.strip()
        session.state = "awaiting_movein"
        session.fields = json.dumps(fields)
        return "When do you plan to move in?"

    elif session.state == "awaiting_movein":
        fields["move_in"] = message.strip()
        session.state = "awaiting_beds"
        session.fields = json.dumps(fields)
        return "How many bedrooms do you need?"

    elif session.state == "awaiting_beds":
        fields["beds"] = message.strip()
        session.state = "ready_to_book"
        session.fields = json.dumps(fields)
        return "Awesome! Type 'book' when you're ready to schedule a tour."

    elif "book" in message.lower():
        return send_booking_confirmation(fields)

    else:
        return "Type 'book' when you're ready to schedule a tour."


def extract_fields_from_history(history):
    name = email = phone = move_in = beds = None

    user_messages = [msg["content"].strip() for msg in history if msg["role"] == "user"]


    for content in user_messages:
        content_lower = content.lower()

        # Name: full name (letters & spaces only), not greeting or command
        if not name and content_lower not in ["hi", "hello", "book"]:
            if all(part.isalpha() for part in content.split()):
                name = content.title()
                continue

        # Email: contains @ and a dot
        if not email and "@" in content and "." in content:
            email = content
            continue

        # Phone: 10+ digit number
        digits = ''.join(filter(str.isdigit, content))
        if not phone and len(digits) >= 10:
            phone = content
            continue

        # Move-in: contains month or year reference
        if not move_in and any(m in content_lower for m in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec", "2025", "2024", "next month"]):
            move_in = content
            continue

        # Beds: message is a single digit (e.g., "2", "3")
        if not beds and content.isdigit():
            beds = content
            continue


    return {
        "name": name,
        "email": email,
        "phone": phone,
        "move_in": move_in,
        "beds": beds,
    }

def send_booking_confirmation(fields):
    name = fields.get("name")
    email = fields.get("email")
    beds = fields.get("beds")
    unit_id = f"APT-{beds}01"

    message = (
        f"Hi {name},\n\n"
        f"Thank you for your interest! Here's your tour confirmation:\n\n"
        f"📍 Property: 123 Main Street\n"
        f"🏠 Unit ID: {unit_id}\n"
        f"📅 Suggested tour time: Tomorrow at 3 PM\n\n"
        f"– The Leasing Team"
    )

    send_email(email, "Tour Confirmation – Homewiz", message)

    return (
        f"Hi {name}, your tour is confirmed!\n"
        f"📍 Property: 123 Main Street\n"
        f"🏠 Unit: {unit_id}\n"
        f"📅 Time: Tomorrow at 3 PM\n\n"
        f"An email confirmation has been sent to {email}."
    )
