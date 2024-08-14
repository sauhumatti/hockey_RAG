import React, { useState } from 'react';
import QueryInput from './QueryInput';
import axios from 'axios';
import { marked } from 'marked';

// Add this line at the top of your file
const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function ChatContainer() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  const addMessage = (sender, content) => {
    setMessages(prevMessages => [...prevMessages, { sender, content }]);
  };

  const handleQuery = async (query) => {
    addMessage('user', query);
    setIsTyping(true);
    try {
      // Update this line to use the apiUrl
      const response = await axios.post(`${apiUrl}/api/query`, { query });
      setIsTyping(false);
      addMessage('ai', response.data.natural_language_answer);
    } catch (error) {
      setIsTyping(false);
      addMessage('ai', `An error occurred: ${error.message}`);
    }
  };

  return (
    <div className="flex flex-col flex-grow overflow-hidden">
      <div className="flex-grow overflow-y-auto p-4">
        {messages.map((message, index) => (
          <div key={index} className={`mb-4 ${message.sender === 'user' ? 'text-right' : 'text-left'}`}>
            <div
              className={`inline-block p-3 rounded-lg ${
                message.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-white'
              }`}
            >
              {message.sender === 'ai' ? (
                <div dangerouslySetInnerHTML={{ __html: marked(message.content) }} />
              ) : (
                message.content
              )}
            </div>
          </div>
        ))}
      </div>
      {isTyping && (
        <div className="text-sm text-gray-300 mb-2 px-4">Analyzing query...</div>
      )}
      <div className="p-4 bg-gray-800">
        <QueryInput onSubmit={handleQuery} />
      </div>
    </div>
  );
}

export default ChatContainer;