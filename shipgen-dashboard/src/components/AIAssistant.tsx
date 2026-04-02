
import React, { useState, useRef, useEffect } from 'react';
import { GoogleGenAI } from '@google/genai';
import { Send, Bot, User, Loader2, Sparkles, X } from 'lucide-react';

const AIAssistant: React.FC = () => {
  const [messages, setMessages] = useState<{ role: 'user' | 'bot'; text: string }[]>([
    { role: 'bot', text: 'Hello! I am ShipGen AI. Ask me anything about your current logistics data or operational efficiency.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMessage }]);
    setIsLoading(true);

    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: userMessage,
        config: {
          systemInstruction: 'You are an expert logistics and supply chain consultant for ShipGen. You have access to dashboard-style operational context (orders, fleet, warehouse). Be concise, professional, and data-driven.',
        },
      });

      const botText = response.text || "I couldn't process that request right now.";
      setMessages(prev => [...prev, { role: 'bot', text: botText }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'bot', text: "Error connecting to AI. Please check your configuration." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-200px)] bg-white rounded-2xl border border-gray-100 shadow-xl overflow-hidden">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 p-4 flex items-center justify-between text-white">
        <div className="flex items-center space-x-3">
          <div className="bg-white/20 p-2 rounded-lg">
            <Bot size={20} />
          </div>
          <div>
            <h3 className="font-bold">ShipGen AI Optimizer</h3>
            <p className="text-[10px] text-blue-100">Powered by Gemini 3.0</p>
          </div>
        </div>
        <Sparkles size={20} className="text-amber-300 animate-pulse" />
      </div>

      <div ref={scrollRef} className="flex-1 p-6 overflow-y-auto space-y-4 bg-gray-50/50">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] flex items-start space-x-3 ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              <div className={`p-2 rounded-lg shrink-0 ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border border-gray-200 shadow-sm text-gray-700'}`}>
                {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>
              <div className={`p-3 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-tr-none shadow-md' 
                  : 'bg-white text-gray-800 rounded-tl-none border border-gray-100 shadow-sm'
              }`}>
                {msg.text}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-100 p-3 rounded-2xl rounded-tl-none shadow-sm flex items-center space-x-2">
              <Loader2 size={16} className="animate-spin text-blue-600" />
              <span className="text-xs text-gray-500 italic">ShipGen is thinking...</span>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 bg-white border-t border-gray-100">
        <div className="relative">
          <input
            type="text"
            placeholder="Ask about warehouse capacity or route trends..."
            className="w-full pl-4 pr-12 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm bg-gray-50"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <button 
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
          >
            <Send size={16} />
          </button>
        </div>
        <p className="text-[10px] text-gray-400 text-center mt-2">
          ShipGen AI may provide insights based on current dashboard data.
        </p>
      </div>
    </div>
  );
};

export default AIAssistant;
