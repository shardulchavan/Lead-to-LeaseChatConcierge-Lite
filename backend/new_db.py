import sqlite3
from datetime import datetime
from typing import Optional
import json
import random

# Import only what we actually use
from models import UserDetails

def init_database():
    """Initialize SQLite database with user details table"""
    try:
        conn = sqlite3.connect('homewiz.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_details (
                conversation_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                phone TEXT,
                move_in_date TEXT,
                beds_wanted INTEGER,
                unit_id TEXT,
                conversation_history TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise

def save_user_details_to_db(user_details: UserDetails):
    """Save user details to SQLite database"""
    print("Saving user details to database", user_details)
    try:
        conn = sqlite3.connect('homewiz.db')
        cursor = conn.cursor()
        
        # Convert conversation_history to JSON string for storage
        conversation_history_json = json.dumps([
            {"role": msg.role, "content": msg.content} 
            for msg in user_details.conversation_history
        ])
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_details 
            (conversation_id, name, email, phone, move_in_date, beds_wanted, unit_id, conversation_history, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_details.conversation_id,
            user_details.name,
            user_details.email,
            user_details.phone,
            user_details.move_in_date,
            user_details.beds_wanted,
            user_details.unit_id,
            conversation_history_json,
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        print(f"✅ Saved ALL user details for conversation: {user_details.conversation_id}")
        print(f"✅ Including {len(user_details.conversation_history)} conversation messages")
        
    except Exception as e:
        print(f"Database save error: {e}")
        raise

def load_user_details_from_db(conversation_id: str) -> Optional[UserDetails]:
    """Load user details from SQLite database"""
    print("Loading user details from database", conversation_id)
    try:
        conn = sqlite3.connect('homewiz.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT conversation_id, name, email, phone, move_in_date, beds_wanted, unit_id, conversation_history
            FROM user_details WHERE conversation_id = ?
        ''', (conversation_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            conversation_id, name, email, phone, move_in_date, beds_wanted, unit_id, conversation_history_json = result
            
            # Parse conversation history from JSON
            conversation_history = []
            if conversation_history_json:
                try:
                    history_data = json.loads(conversation_history_json)
                    from models import ConversationMessage
                    conversation_history = [
                        ConversationMessage(role=msg["role"], content=msg["content"])
                        for msg in history_data
                    ]
                except Exception as e:
                    print(f"Warning: Could not parse conversation history: {e}")
                    conversation_history = []
            
            loaded_details = UserDetails(
                conversation_id=conversation_id,
                name=name,
                email=email,
                phone=phone,
                move_in_date=move_in_date,
                beds_wanted=beds_wanted,
                unit_id=unit_id,
                conversation_history=conversation_history
            )
            print(f"✅ Found existing user details: {loaded_details.to_dict()}")
            print(f"✅ Loaded {len(conversation_history)} conversation messages")
            return loaded_details
        print(f"No existing user details found for {conversation_id}")
        return None
        
    except Exception as e:
        print(f"Database load error: {e}")
        return None

def load_user_details_by_name(name: str) -> Optional[UserDetails]:
    """Load user details from database by name (person's history)"""
    try:
        print(f"Looking for existing user with name: {name}")
        conn = sqlite3.connect('homewiz.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT conversation_id, name, email, phone, move_in_date, beds_wanted, unit_id, conversation_history
            FROM user_details WHERE LOWER(name) = LOWER(?) ORDER BY updated_at DESC LIMIT 1
        ''', (name.strip(),))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            conv_id, name, email, phone, move_in_date, beds_wanted, unit_id, conversation_history_json = result
            
            # Parse conversation history from JSON
            conversation_history = []
            if conversation_history_json:
                try:
                    history_data = json.loads(conversation_history_json)
                    from models import ConversationMessage
                    conversation_history = [
                        ConversationMessage(role=msg["role"], content=msg["content"])
                        for msg in history_data
                    ]
                except Exception as e:
                    print(f"Warning: Could not parse conversation history: {e}")
                    conversation_history = []
            
            loaded_details = UserDetails(
                conversation_id=conv_id,
                name=name,
                email=email,
                phone=phone,
                move_in_date=move_in_date,
                beds_wanted=beds_wanted,
                unit_id=unit_id,
                conversation_history=conversation_history
            )
            print(f"✅ Found existing person: {loaded_details.to_dict()}")
            print(f"✅ Loaded {len(conversation_history)} conversation messages")
            return loaded_details
    except Exception as e:
        print(f"No existing person found with name: {name}")
        return None

def check_inventory(beds: int) -> str:
    """
    Stub function to check inventory and return available unit ID
    Args:
        beds: Number of bedrooms requested
    Returns:
        Available unit ID
    """
    # Generate a realistic unit ID based on bedrooms
    unit_types = {
        1: ["1A", "1B", "1C"],
        2: ["2A", "2B", "2C", "2D"], 
        3: ["3A", "3B"],
        4: ["4A"],
        5: ["5A"]
    }
    
    floor = random.randint(1, 12)  # Random floor 1-12
    unit_type = random.choice(unit_types.get(beds, ["XA"]))
    unit_number = random.randint(1, 99)
    
    unit_id = f"UNIT-{floor}{unit_type}-{unit_number:02d}"
    
    print(f"🏠 Inventory check: {beds} bedrooms → Available unit: {unit_id}")
    return unit_id

def get_all_user_details() -> list:
    """Get all user details from database for debugging"""
    try:
        conn = sqlite3.connect('homewiz.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT conversation_id, name, email, phone, move_in_date, beds_wanted, unit_id, conversation_history, created_at, updated_at
            FROM user_details ORDER BY updated_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "conversation_id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3],
                "move_in_date": row[4],
                "beds_wanted": row[5],
                "unit_id": row[6],
                "conversation_history": row[7],  # JSON string
                "created_at": row[8],
                "updated_at": row[9]
            }
            for row in results
        ]
                
    except Exception as e:
        print(f"Database query error: {e}")
        return []