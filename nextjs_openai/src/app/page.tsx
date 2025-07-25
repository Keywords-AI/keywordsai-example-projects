'use client';

import { useState, useRef } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  metadata?: {
    model?: string;
    id?: string;
  };
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamingEnabled, setStreamingEnabled] = useState(true);
  const streamingMessageIndexRef = useRef<number | null>(null);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = { role: 'user', content: inputMessage };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputMessage('');
    setIsLoading(true);

    try {
      if (streamingEnabled) {
        // Handle streaming response
        const assistantMessage: Message = {
          role: 'assistant',
          content: '',
        };
        const messagesWithAssistant = [...newMessages, assistantMessage];
        setMessages(messagesWithAssistant);
        streamingMessageIndexRef.current = messagesWithAssistant.length - 1;

        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            messages: newMessages,
            stream: true,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (reader) {
          try {
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;

              const chunk = decoder.decode(value);
              const lines = chunk.split('\n');

              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  try {
                    const data = JSON.parse(line.slice(6));
                    
                    if (data.type === 'content') {
                      const streamingIndex = streamingMessageIndexRef.current;
                      if (streamingIndex !== null) {
                        setMessages(prevMessages => {
                          const updated = [...prevMessages];
                          updated[streamingIndex] = {
                            ...updated[streamingIndex],
                            content: data.fullContent,
                          };
                          return updated;
                        });
                      }
                    } else if (data.type === 'done') {
                      // Finalize the message with metadata
                      console.log('Streaming completed. Final content:', data.fullContent);
                      const streamingIndex = streamingMessageIndexRef.current;
                      if (streamingIndex !== null) {
                        setMessages(prevMessages => {
                          const updated = [...prevMessages];
                          updated[streamingIndex] = {
                            ...updated[streamingIndex],
                            content: data.fullContent,
                            metadata: {
                              model: data.model,
                              id: data.id,
                            },
                          };
                          return updated;
                        });
                      }
                      streamingMessageIndexRef.current = null;
                    } else if (data.type === 'error') {
                      console.error('Streaming error:', data.error);
                      alert('Streaming error: ' + data.error);
                    }
                  } catch (parseError) {
                    console.error('Error parsing streaming data:', parseError);
                  }
                }
              }
            }
          } finally {
            reader.releaseLock();
          }
        }
      } else {
        // Handle regular response
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            messages: newMessages,
            stream: false,
          }),
        });

        const data = await response.json();

        if (response.ok) {
          const assistantMessage: Message = {
            role: 'assistant',
            content: data.message,
            metadata: {
              model: data.model,
              id: data.id,
            },
          };
          setMessages([...newMessages, assistantMessage]);
        } else {
          console.error('Error:', data.error);
          alert('Error: ' + data.error);
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Error sending message');
      // Clean up streaming state on error  
      streamingMessageIndexRef.current = null;
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
      
      {/* Streaming toggle */}
      <div style={{ marginBottom: '10px' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <input
            type="checkbox"
            checked={streamingEnabled}
            onChange={(e) => setStreamingEnabled(e.target.checked)}
            disabled={isLoading}
          />
          <span>Enable Streaming (Test KeywordsAI workflow streaming)</span>
        </label>
      </div>
      
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
            {message.metadata && (
              <span style={{ fontSize: '12px', color: '#666', marginLeft: '10px' }}>
                ({message.metadata.model} - {message.metadata.id})
              </span>
            )}
            <div style={{ 
              marginLeft: '10px', 
              whiteSpace: 'pre-wrap',
              position: 'relative'
            }}>
              {message.content}
              {streamingMessageIndexRef.current === index && (
                <span style={{ 
                  animation: 'blink 1s infinite',
                  fontSize: '18px',
                  marginLeft: '2px'
                }}>▊</span>
              )}
            </div>
          </div>
        ))}
        {isLoading && streamingMessageIndexRef.current === null && <div>AI is typing...</div>}
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
        <br />
        {streamingEnabled ? 'Streaming enabled - messages will appear in real-time' : 'Streaming disabled - messages will appear all at once'}
      </p>

      <style jsx>{`
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }
      `}</style>
    </div>
  );
}
