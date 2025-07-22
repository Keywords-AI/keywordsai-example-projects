'use client';

import { useState } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = { role: 'user', content: inputMessage };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: newMessages,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.message,
        };
        setMessages([...newMessages, assistantMessage]);
      } else {
        console.error('Error:', data.error);
        alert('Error: ' + data.error);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Error sending message');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Chat with OpenAI</h1>
      
      <div
        style={{
          border: '1px solid #ccc',
          height: '400px',
          overflowY: 'auto',
          padding: '10px',
          marginBottom: '10px',
          backgroundColor: '#f9f9f9',
        }}
      >
        {messages.map((message, index) => (
          <div key={index} style={{ marginBottom: '10px' }}>
            <strong>{message.role === 'user' ? 'You' : 'AI'}:</strong>
            <div style={{ marginLeft: '10px', whiteSpace: 'pre-wrap' }}>
              {message.content}
            </div>
          </div>
        ))}
        {isLoading && <div>AI is typing...</div>}
      </div>

      <div style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          style={{
            flex: 1,
            padding: '10px',
            border: '1px solid #ccc',
            fontSize: '16px',
          }}
          disabled={isLoading}
        />
        <button
          onClick={sendMessage}
          disabled={isLoading || !inputMessage.trim()}
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            cursor: 'pointer',
            fontSize: '16px',
          }}
        >
          Send
        </button>
      </div>

      <p style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>
        Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  );
}
