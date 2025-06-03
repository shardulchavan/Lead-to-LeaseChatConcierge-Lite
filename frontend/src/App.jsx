import React, { useState, useEffect, useRef } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [collectedData, setCollectedData] = useState({});
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (messageText = inputMessage) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      content: messageText,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageText,
          session_id: sessionId
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const assistantMessage = {
        type: 'assistant',
        content: data.reply,
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, assistantMessage]);
      setSessionId(data.session_id);
      setCollectedData(data.collected_data);

    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        type: 'assistant',
        content: 'Sorry, there was an error. Please try again.',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage();
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <div style={{ backgroundColor: '#f5f5f5', border: '1px solid #ddd', borderRadius: '8px', height: '600px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ backgroundColor: '#007bff', color: 'white', padding: '15px', borderRadius: '8px 8px 0 0' }}>
          <h2 style={{ margin: '0', fontSize: '18px' }}>Apartment Leasing Assistant</h2>
        </div>

        <div style={{ flex: 1, padding: '15px', overflowY: 'auto', backgroundColor: 'white' }}>
          {messages.length === 0 && (
            <div style={{ padding: '10px', backgroundColor: '#e9ecef', borderRadius: '5px', marginBottom: '10px' }}>
              Hi! I'm here to help you find an apartment and schedule a tour. What's your name?
            </div>
          )}

          {messages.map((message, index) => (
            <div key={index} style={{
              marginBottom: '10px',
              display: 'flex',
              justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start'
            }}>
              <div style={{
                maxWidth: '70%',
                padding: '10px',
                borderRadius: '5px',
                backgroundColor: message.type === 'user' ? '#007bff' : '#e9ecef',
                color: message.type === 'user' ? 'white' : 'black'
              }}>
                <div>{message.content}</div>
                <div style={{ fontSize: '12px', opacity: '0.7', marginTop: '5px' }}>
                  {message.timestamp}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div style={{ padding: '10px', backgroundColor: '#e9ecef', borderRadius: '5px', marginBottom: '10px' }}>
              Typing...
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} style={{ padding: '15px', borderTop: '1px solid #ddd' }}>
          <div style={{ display: 'flex', gap: '10px' }}>
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading}
              style={{
                flex: 1,
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px'
              }}
            />
            <button 
              type="submit" 
              disabled={isLoading || !inputMessage.trim()}
              style={{
                padding: '10px 20px',
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: isLoading || !inputMessage.trim() ? 'not-allowed' : 'pointer',
                opacity: isLoading || !inputMessage.trim() ? 0.6 : 1
              }}
            >
              Send
            </button>
          </div>
        </form>
      </div>

      {Object.values(collectedData).some(value => value) && (
        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f8f9fa', border: '1px solid #ddd', borderRadius: '8px' }}>
          <h3 style={{ margin: '0 0 10px 0', fontSize: '16px' }}>Collected Information:</h3>
          {Object.entries(collectedData).map(([key, value]) => (
            value && (
              <div key={key} style={{ marginBottom: '5px', fontSize: '14px' }}>
                <strong>{key.replace('_', ' ').toUpperCase()}:</strong> {value}
              </div>
            )
          ))}
        </div>
      )}
    </div>
  );
}

export default App; 