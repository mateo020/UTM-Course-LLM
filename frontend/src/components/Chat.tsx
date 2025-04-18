import {useRef, useEffect, useState } from 'react';
import axios from "axios";
import { FaGraduationCap } from 'react-icons/fa';
import { BsSunFill, BsMoonFill } from 'react-icons/bs';
import { Link } from 'react-router-dom';

type Message = {
  id: string;
  role: string;
  content: string;
};

const typingExamples = [
  "What are the prerequisites for CSC108?",
  "Tell me about the Computer Science program at UTM",
  "What courses do I need for a Mathematics major?",
  "How many credits do I need to graduate?"
];

export function Chat(){
  const [chatMessages, setChatMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [typingText, setTypingText] = useState("");
  const [typingIndex, setTypingIndex] = useState(0);
  const [exampleIndex, setExampleIndex] = useState(0);
  const chatParent = useRef<HTMLUListElement>(null);

  // Typing animation effect
  useEffect(() => {
    if (chatMessages.length > 0) return;

    const currentExample = typingExamples[exampleIndex];
    const interval = setInterval(() => {
      if (typingIndex < currentExample.length) {
        setTypingText(currentExample.substring(0, typingIndex + 1));
        setTypingIndex(prev => prev + 1);
      } else {
        clearInterval(interval);
        setTimeout(() => {
          setTypingText("");
          setTypingIndex(0);
          setExampleIndex((prev) => (prev + 1) % typingExamples.length);
        }, 2000);
      }
    }, 100);

    return () => clearInterval(interval);
  }, [typingIndex, exampleIndex, chatMessages.length]);

  const fetchAPI = async(userInput: string) => {
    try {
      setIsLoading(true);
      const response = await axios.post("http://localhost:8000/api/v1/chat/chat", {
        question: userInput,
        chatHistory: chatMessages.map((msg) => msg.content),
        session_id: sessionId
      });
      
      // Store the session ID if we get one
      if (response.data.session_id) {
        setSessionId(response.data.session_id);
      }
      
      return response.data;
    } catch (error){
      console.error("Error fetching data:", error);
      if (axios.isAxiosError(error)) {
        return { answer: `Error: ${error.response?.data?.detail || error.message}` };
      }
      return { answer: "An unexpected error occurred. Please try again." };
    } finally {
      setIsLoading(false);
    }
  };

  const generateId = () => Math.random().toString(36).substring(2,9);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if(!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content: input
    };

    setChatMessages((prev) => [...prev, userMessage]);
    setInput("");

    const apiResponse = await fetchAPI(input);
    const botMessage: Message = {
      id: generateId(),
      role: "bot",
      content: apiResponse.answer,
    };
    setChatMessages((prev) => [...prev, botMessage]);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  useEffect(() => {
    const domNode = chatParent.current;
    if(domNode){
      domNode.scrollTop = domNode.scrollHeight;
    }
  }, [chatMessages]);

  return (
    <main className={`min-h-screen transition-colors duration-200 ${isDarkMode ? 'bg-gray-900 text-white' : 'bg-gray-100'}`}>
      <header className={`p-4 border-b ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} shadow flex justify-between items-center`}>
        <div className="flex items-center gap-2">
          <FaGraduationCap className="text-2xl text-blue-500" />
          <Link to="/" className="text-2xl font-bold hover:text-blue-500 transition-colors duration-200">
            UTM Course Assistant
          </Link>
        </div>
        <button
          onClick={() => setIsDarkMode(!isDarkMode)}
          className={`p-2 rounded-full ${isDarkMode ? 'bg-gray-700 text-yellow-400' : 'bg-gray-200 text-gray-700'}`}
        >
          {isDarkMode ? <BsSunFill /> : <BsMoonFill />}
        </button>
      </header>
      <section className={`flex-grow overflow-y-auto p-4 ${isDarkMode ? 'bg-gray-900' : 'bg-white'} shadow-inner relative`}>
        {chatMessages.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className={`text-center ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              <div className="flex items-center gap-2 mb-4">
                <FaGraduationCap className="text-4xl text-blue-500" />
                <h2 className="text-2xl font-semibold">UTM Course Assistant</h2>
              </div>
              <div className="text-lg">
                {typingText}
                <span className="animate-pulse">|</span>
              </div>
              <p className="mt-4 text-sm">
                Ask me anything about UTM courses and programs
              </p>
            </div>
          </div>
        )}
        <ul ref={chatParent}>
          {chatMessages.map((m) => (
            <li
              key={m.id}
              className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className={`flex items-start gap-2 max-w-[80%] ${m.role === "user" ? "flex-row-reverse" : ""}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${m.role === "user" ? 'bg-blue-500' : 'bg-gray-500'}`}>
                  {m.role === "user" ? "U" : <FaGraduationCap className="text-white" />}
                </div>
                <div>
                  {m.content}
                </div>
              </div>
            </li>
          ))}
          {isLoading && (
            <li className="flex justify-start">
              <div className="flex items-start gap-2 max-w-[80%]">
                <div className="w-8 h-8 rounded-full bg-gray-500 flex items-center justify-center">
                  <FaGraduationCap className="text-white" />
                </div>
                <div className={`rounded-2xl p-4 shadow-md ${isDarkMode ? 'bg-gray-700 text-white' : 'bg-gray-100 text-gray-800'}`}>
                  Thinking...
                </div>
              </div>
            </li>
          )}
        </ul>
      </section>

      <form
        onSubmit={handleSubmit}
        className={`p-4 ${isDarkMode ? 'bg-gray-800' : 'bg-white'} shadow flex items-center gap-2`}
      >
        <div className="flex-grow relative">
          <textarea
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              // Auto-resize textarea
              e.target.style.height = 'auto';
              e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
            }}
            onKeyDown={handleKeyDown}
            placeholder="Ask about UTM courses..."
            className={`w-full rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all duration-200 resize-none ${
              isDarkMode 
                ? 'bg-gray-700 text-white placeholder-gray-400 border-gray-600' 
                : 'bg-white text-gray-800 border-gray-300'
            } border min-h-[40px] max-h-[200px]`}
            disabled={isLoading}
            rows={1}
          />
        </div>
        <button
          type="submit"
          className={`px-4 py-2 rounded-xl text-sm transition-all duration-200 shadow-md hover:shadow-lg ${
            isDarkMode
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-blue-500 text-white hover:bg-blue-600'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
          disabled={isLoading}
        >
          Send
        </button>
      </form>
    </main>
  );
}