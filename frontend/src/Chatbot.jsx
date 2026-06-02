import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import axios from 'axios';

export default function Chatbot({ scanContext }) {
  const [messages, setMessages] = useState([
    { role: 'model', text: 'Hello! I am your Virtual Botanist. How can I help you with your crops today?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/chat', {
        messages: [...messages, userMessage],
        context_disease: scanContext ? scanContext.prediction : null
      });

      if (response.data.error) {
        setMessages(prev => [...prev, { role: 'model', text: `Sorry, an error occurred: ${response.data.error}` }]);
      } else {
        const botMessage = { role: 'model', text: response.data.response || 'I received an empty response.' };
        setMessages(prev => [...prev, botMessage]);
      }
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'model', text: 'Sorry, I am having trouble connecting to the server.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <motion.div 
            key={idx}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`chat-message ${msg.role === 'user' ? 'user-message' : 'bot-message'}`}
          >
            <div className="message-icon">
              {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
            </div>
            <div className="message-text">
              {msg.text}
            </div>
          </motion.div>
        ))}
        {isLoading && (
          <div className="chat-message bot-message">
            <div className="message-icon">
              <Bot size={16} />
            </div>
            <div className="message-text flex items-center gap-2">
              <Loader2 size={16} className="animate-spin" /> Thinking...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask me anything about your crops..."
          className="chat-input"
        />
        <button className="chat-send-btn" onClick={sendMessage} disabled={isLoading || !input.trim()}>
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
