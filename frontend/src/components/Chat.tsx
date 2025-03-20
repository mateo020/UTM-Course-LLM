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
  const chatParent = useRef<HTMLUListElement>(null);

  const fetchAPI = async(userInput: string) => {
    try {
      const response = await axios.post("http://localhost:8000/api/v1/chat", {
        question: userInput,
        chatHistory: chatMessages.map((msg) => msg.content),
      });
      return response.data;
    } catch (error){
      console.error("Error fetching data:", error);
      return { answer: "Error fetching response from API."};

    }
  };
  //id gerneation for message -> message hisotry 
  const generateId = () => Math.random().toString(36).substring(2,9);

  //event listener FormEvent 
  const handleSubmit = async (e: React.FormEvent) => {
    // if event does not get handled its default action should not be taken
    e.preventDefault();

    if(!input.trim()) return;


    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content: input

    };
    // sets a new array: ...prev copies all elmnts form existing array prev to new array, ChatMessages stsate variable
    setChatMessages((prev) => [...prev, userMessage]);

    //clear input
    setInput("");

    //API response 
    const apiResponse = await fetchAPI(input);
    const botMessage: Message = {
      id: generateId(),
      role: "bot",
      content: apiResponse.answer,
    };
    setChatMessages((prev) => [...prev, botMessage]);

    


  };
  //scroll to new message
  useEffect(() => {
    const domNode = chatParent.current;
    if(domNode){
      domNode.scrollTop = domNode.scrollHeight;
    }

  }, [chatMessages])

  return (
    <main className="flex flex-col h-screen bg-gray-100">
      <header className="p-4 border-b bg-white shadow">
        <h1 className="text-2xl font-bold text-center">LangChain Chat</h1>
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
          placeholder="Type your message..."
          className="flex-grow border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          Send
        </button>
      </form>
    </main>
  );

}