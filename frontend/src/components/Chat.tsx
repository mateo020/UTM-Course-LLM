import {useRef, useEffect, useState } from 'react';
import axios from "axios";

type Message = {
  id: string;
  role: string;
  content: string;
};

export function Chat(){
  const [chatMessages, setChatMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const chatParent = useRef<HTMLUListElement>(null);

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

  useEffect(() => {
    const domNode = chatParent.current;
    if(domNode){
      domNode.scrollTop = domNode.scrollHeight;
    }
  }, [chatMessages]);

  return (
    <main className="flex flex-col h-screen bg-gray-100">
      <header className="p-4 border-b bg-white shadow">
        <h1 className="text-2xl font-bold text-center">UTM Course Assistant</h1>
      </header>

      <section className="flex-grow overflow-y-auto p-4 bg-white shadow-inner">
        <ul ref={chatParent} className="flex flex-col gap-4">
          {chatMessages.map((m) => (
            <li
              key={m.id}
              className={`flex ${
                m.role === "user" ? "justify-start" : "justify-end"
              }`}
            >
              <div
                className={`rounded-xl p-4 shadow-md max-w-xs text-sm ${
                  m.role === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-300 text-gray-800"
                }`}
              >
                {m.content}
              </div>
            </li>
          ))}
          {isLoading && (
            <li className="flex justify-end">
              <div className="rounded-xl p-4 shadow-md max-w-xs text-sm bg-gray-300 text-gray-800">
                Thinking...
              </div>
            </li>
          )}
        </ul>
      </section>

      <form
        onSubmit={handleSubmit}
        className="p-4 bg-white shadow flex items-center gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about UTM courses..."
          className="flex-grow border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          disabled={isLoading}
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={isLoading}
        >
          Send
        </button>
      </form>
    </main>
  );
}