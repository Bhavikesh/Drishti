import React, { useState, useRef, useEffect } from 'react';
import { chatAPI } from '../services/api';
import { useVoice } from '../hooks/useVoice';
import { useNavigate } from 'react-router-dom';
import PDFExport from './PDFExport';

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [language, setLanguage] = useState('en');
  const [lastAgent, setLastAgent] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  
  const [sessionId] = useState(() => "session_" + Math.random().toString(36).substring(7));
  
  const { isListening, isSpeaking, startListening, speak, stopSpeech } = useVoice();

  const handleSend = async (text: string = input) => {
    if (!text.trim()) return;
    
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setInput('');
    setIsLoading(true);
    
    try {
      const response = await chatAPI.sendMessage(text, sessionId, language);
      
      // If LLM failed but we have SQL results, build a fallback markdown response
      let finalContent = response.response;
      if (finalContent.includes("trouble processing") && response.sql_results) {
        finalContent = "⚠️ **AI Generation Rate Limited.**\n\n*However, the database successfully executed the query. Here are the raw results:*\n\n```json\n" + JSON.stringify(response.sql_results, null, 2) + "\n```";
      }

      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: finalContent,
        investigate_query: response.investigate_query
      } as any]);
      setLastAgent(response.agent || '');
      speak(response.response);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, an error occurred. Please try again.' }]);
    }
    
    setIsLoading(false);
  };

  const handleVoiceInput = async () => {
    const langCode = language === 'kn' ? 'kn-IN' : 'en-IN';
    const transcript = await startListening(langCode);
    if (transcript) {
      setInput(transcript);
      handleSend(transcript);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Format AI response with markdown-like rendering
  const formatResponse = (text: string) => {
    // Bold text
    let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Bullet points
    formatted = formatted.replace(/^[•\-]\s/gm, '• ');
    return formatted;
  };

  return (
    <div className="flex flex-col h-[calc(100vh-64px)] bg-gray-900">
      <div className="flex justify-between items-center bg-gradient-to-r from-blue-900 to-indigo-900 p-4 text-white">
        <div>
          <h1 className="text-xl font-bold">🔍 CrimeMind AI Assistant</h1>
          <p className="text-xs text-blue-200">
            Multi-Agent System | {language === 'kn' ? 'ಕನ್ನಡ' : 'English'} | Voice Enabled
            {lastAgent && <span className="ml-2 bg-blue-700 px-2 py-0.5 rounded text-xs">Agent: {lastAgent}</span>}
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setLanguage(language === 'en' ? 'kn' : 'en')}
            className="px-3 py-1 bg-blue-700 rounded text-sm hover:bg-blue-600 transition-colors"
          >
            {language === 'en' ? '🌐 ಕನ್ನಡ' : '🌐 English'}
          </button>
          <PDFExport chatHistory={messages} />
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 space-y-4">
            <div className="text-6xl">🔍</div>
            <h2 className="text-xl font-semibold text-gray-400">CrimeMind AI Investigation Copilot</h2>
            <p className="text-sm text-center max-w-md">
              Ask me about crime patterns, criminal networks, hotspot analysis, or generate investigation reports.
            </p>
            <div className="grid grid-cols-2 gap-2 max-w-lg">
              {[
                "Show burglary hotspots in Mysuru",
                "Who are the top repeat offenders?",
                "Analyze crime trends in Bengaluru",
                "Generate investigation report for theft cases"
              ].map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(suggestion)}
                  className="text-xs text-left p-3 bg-gray-800 rounded-lg hover:bg-gray-700 border border-gray-700 hover:border-blue-500 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-3xl p-4 rounded-lg ${
              msg.role === 'user' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-800 text-gray-100 border border-gray-700'
            }`}>
              {msg.role === 'assistant' ? (
                <div>
                  <div 
                    className="whitespace-pre-wrap leading-relaxed"
                    dangerouslySetInnerHTML={{ __html: formatResponse(msg.content) }}
                  />
                  {(msg as any).investigate_query && (
                    <div className="mt-4 pt-4 border-t border-gray-700 flex justify-end">
                      <button 
                        onClick={() => navigate('/investigate', { state: { query: (msg as any).investigate_query } })}
                        className="flex items-center space-x-2 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 text-white px-4 py-2 rounded-lg text-sm font-bold shadow-lg shadow-red-900/50 transition-all"
                      >
                        <span>🕵️‍♂️ View Investigation Board</span>
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                msg.content
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
                <span className="text-sm text-gray-400">CrimeMind AI is analyzing...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="p-4 border-t border-gray-700 bg-gray-800">
        <div className="flex space-x-2">
          {isSpeaking && (
            <button
              onClick={stopSpeech}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center space-x-1"
            >
              <span>⏹️</span>
              <span className="hidden sm:inline">Stop Speech</span>
            </button>
          )}
          <button
            onClick={handleVoiceInput}
            className={`px-4 py-2 rounded-lg transition-all ${isListening ? 'bg-red-600 animate-pulse shadow-lg shadow-red-500/30' : 'bg-gray-600 hover:bg-gray-500'} text-white`}
          >
            🎤 {isListening ? 'Listening...' : 'Voice'}
          </button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={language === 'kn' ? 'ಕನ್ನಡದಲ್ಲಿ ಅಥವಾ ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ಕೇಳಿ...' : 'Ask about crimes, networks, hotspots, or generate reports...'}
            className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
          />
          <button
            onClick={() => handleSend()}
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
