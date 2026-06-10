import React, { useState, useRef, useEffect } from 'react';
import { chatAPI } from '../services/api';
import { useVoice } from '../hooks/useVoice';
import PDFExport from './PDFExport';

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Hardcoded session ID for demo
  const sessionId = "session_" + Math.random().toString(36).substring(7);
  
  const { isListening, startListening, speak } = useVoice();

  const handleSend = async (text: string = input) => {
    if (!text.trim()) return;
    
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setInput('');
    setIsLoading(true);
    
    try {
      const response = await chatAPI.sendMessage(text, sessionId);
      setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
      speak(response.response);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, an error occurred.' }]);
    }
    
    setIsLoading(false);
  };

  const handleVoiceInput = async () => {
    const transcript = await startListening('en-IN');
    if (transcript) {
      setInput(transcript);
      handleSend(transcript);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-[calc(100vh-64px)] bg-gray-900">
      <div className="flex justify-between items-center bg-blue-900 p-4 text-white">
        <div>
          <h1 className="text-xl font-bold">Drishti Assistant</h1>
          <p className="text-xs">Kannada + English | Voice Enabled</p>
        </div>
        <PDFExport chatHistory={messages} />
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-2xl p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-100'}`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-700 p-3 rounded-lg">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="p-4 border-t border-gray-700 bg-gray-800">
        <div className="flex space-x-2">
          <button
            onClick={handleVoiceInput}
            className={`px-4 py-2 rounded ${isListening ? 'bg-red-600 animate-pulse' : 'bg-gray-600'} text-white`}
          >
            🎤 {isListening ? 'Listening...' : 'Voice'}
          </button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask in English or Kannada... (ಕನ್ನಡದಲ್ಲಿಯೂ ಕೇಳಿ)"
            className="flex-1 px-4 py-2 bg-gray-700 text-white rounded focus:outline-none focus:ring-2 focus:ring-blue-600"
          />
          <button
            onClick={() => handleSend()}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
