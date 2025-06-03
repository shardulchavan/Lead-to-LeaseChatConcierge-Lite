import json
from models import Session
from email_utils import send_email  # ✅ import at top

def handle_message(message: str, session: Session) -> str:
    fields = json.loads(session.fields)

    if session.state == "start":
        session.state = "awaiting_name"
        return """I'm your virtual leasing assistant here to help you find the perfect home.  
        Feel free to ask me about available units, schedule a tour, or anything else you need!"""

    elif session.state == "awaiting_name":
        fields["name"] = message.strip()
        session.state = "awaiting_email"
        session.fields = json.dumps(fields)
        return f"""Thanks {fields["name"]}! What's your email?"""

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

def send_booking_confirmation(fields):
    unit_id = f"APT-{fields.get('beds')}01"
    return (
        f"Hi {fields.get('name')}, your tour is confirmed!\n"
        f"📍 Property: 123 Main Street\n"
        f"🏠 Unit: {unit_id}\n"
        f"📅 Time: Tomorrow at 3 PM"
    )

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

    # ✅ Send email to the user
    send_email(email, "Tour Confirmation – Homewiz", message)

    return (
        f"Hi {name}, your tour is confirmed!\n"
        f"📍 Property: 123 Main Street\n"
        f"🏠 Unit: {unit_id}\n"
        f"📅 Time: Tomorrow at 3 PM\n\n"
        f"An email confirmation has been sent to {email}."
    )
