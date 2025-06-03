import { useEffect, useState, useRef } from 'react';

export default function Home() {
  const [userId, setUserId] = useState('');
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const chatBoxRef = useRef(null);

  useEffect(() => {
    let storedId = localStorage.getItem('user_id');
    if (!storedId) {
      storedId = 'user_' + Date.now();
      localStorage.setItem('user_id', storedId);
    }
    setUserId(storedId);
  }, []);

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    const trimmed = message.trim();
    if (!trimmed) return;

    setMessages((prev) => [...prev, { sender: 'user', text: trimmed }]);
    setMessage('');

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, message: trimmed }),
      });

      const data = await res.json();
      setMessages((prev) => [...prev, { sender: 'bot', text: data.reply }]);
    } catch (err) {
      setMessages((prev) => [...prev, { sender: 'bot', text: '⚠️ Could not reach server.' }]);
    }
  };

  const resetChat = () => {
    localStorage.removeItem('user_id');
    setMessages([]);
    location.reload();
  };

  return (
    <div style={styles.page}>
      <div style={styles.wrapper}>
        <div style={styles.chatBox} ref={chatBoxRef}>
          {messages.map((msg, index) => (
            <div
              key={index}
              style={{
                ...styles.message,
                textAlign: msg.sender === 'user' ? 'right' : 'left',
                color: msg.sender === 'user' ? 'blue' : 'green',
              }}
            >
              {msg.text}
            </div>
          ))}
        </div>
        <div style={styles.inputArea}>
          <input
            type="text"
            value={message}
            placeholder="Type your message..."
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            style={styles.input}
          />
          <button onClick={sendMessage} style={styles.button}>Send</button>
          <button onClick={resetChat} style={styles.reset}>🔄</button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    fontFamily: 'Arial, sans-serif',
    backgroundColor: '#f9f9f9',
    height: '100vh',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
  wrapper: {
    width: 400,
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 8,
    boxShadow: '0 0 10px rgba(0,0,0,0.1)',
  },
  chatBox: {
    height: 400,
    overflowY: 'auto',
    border: '1px solid #ccc',
    padding: 10,
    marginBottom: 10,
    borderRadius: 4,
    backgroundColor: '#fcfcfc',
  },
  message: {
    margin: '6px 0',
    fontSize: 14,
  },
  inputArea: {
    display: 'flex',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    padding: 8,
    border: '1px solid #ccc',
    borderRadius: 4,
    marginRight: 6,
    fontSize: 14,
  },
  button: {
    padding: '8px 12px',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    borderRadius: 4,
    cursor: 'pointer',
  },
  reset: {
    padding: '8px 10px',
    backgroundColor: '#ffc107',
    color: '#000',
    border: 'none',
    borderRadius: 4,
    cursor: 'pointer',
    marginLeft: 4,
  },
};
