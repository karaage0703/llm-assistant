import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github-dark.css';
import './ChatInterface.css';

// Configure marked for code highlighting
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value;
      } catch (err) {}
    }
    try {
      return hljs.highlightAuto(code).value;
    } catch (err) {
      return code;
    }
  }
});

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [websocket, setWebsocket] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const messagesEndRef = useRef(null);
  const clientId = useRef(Math.random().toString(36).substr(2, 9));

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket(`ws://localhost:8000/ws/${clientId.current}`);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('connected');
        setWebsocket(ws);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'response') {
          const responseData = data.data;
          setMessages(prev => [...prev, {
            id: Date.now(),
            type: 'assistant',
            content: responseData.response,
            timestamp: new Date(),
            success: responseData.success,
            error: responseData.error
          }]);
          setIsLoading(false);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setConnectionStatus('disconnected');
        setWebsocket(null);
        // Attempt to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
      };
    };

    connectWebSocket();

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

  const sendMessage = async (message) => {
    if (!message.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // Send via WebSocket if connected, otherwise use REST API
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify({
        message: message,
        session_id: 'default'
      }));
    } else {
      // Fallback to REST API
      try {
        const response = await axios.post('/api/chat', {
          message: message,
          session_id: 'default'
        });

        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          type: 'assistant',
          content: response.data.response,
          timestamp: new Date(),
          success: response.data.success,
          error: response.data.error
        }]);
      } catch (error) {
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          type: 'assistant',
          content: 'Error: Failed to send message. Please check the connection.',
          timestamp: new Date(),
          success: false,
          error: error.message
        }]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputMessage);
  };

  const renderMessage = (message) => {
    const htmlContent = marked(message.content);
    
    return (
      <div key={message.id} className={`message ${message.type}`}>
        <div className="message-header">
          <span className="message-sender">
            {message.type === 'user' ? 'You' : 'Assistant'}
          </span>
          <span className="message-time">
            {message.timestamp.toLocaleTimeString()}
          </span>
          {message.type === 'assistant' && (
            <span className={`message-status ${message.success ? 'success' : 'error'}`}>
              {message.success ? '✓' : '✗'}
            </span>
          )}
        </div>
        <div 
          className="message-content"
          dangerouslySetInnerHTML={{ __html: htmlContent }}
        />
        {message.error && (
          <div className="message-error">
            Error: {message.error}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="chat-interface">
      <div className="connection-status">
        <span className={`status-indicator ${connectionStatus}`}></span>
        Connection: {connectionStatus}
      </div>
      
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h3>Welcome to LLM Assistant Bot!</h3>
            <p>Start a conversation by typing a message below.</p>
            <p><em>This is currently a basic implementation. Claude Code CLI integration coming soon!</em></p>
          </div>
        )}
        
        {messages.map(renderMessage)}
        
        {isLoading && (
          <div className="message assistant loading">
            <div className="message-header">
              <span className="message-sender">Assistant</span>
              <span className="message-time">thinking...</span>
            </div>
            <div className="message-content">
              <div className="loading-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form className="input-form" onSubmit={handleSubmit}>
        <div className="input-container">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message here..."
            disabled={isLoading}
            className="message-input"
          />
          <button 
            type="submit" 
            disabled={isLoading || !inputMessage.trim()}
            className="send-button"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;