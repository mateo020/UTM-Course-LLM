import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Chat } from './components/Chat';
import SearchBar from "./components/search"; 
import CourseDetail from './components/CourseDetail';
import './App.css';


function Home() {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
      <h1 className="text-4xl font-bold mb-4">Welcome to the Chat App</h1>
      <Link to="/chat">
        <button className="px-6 py-3 bg-blue-500 text-white rounded-lg text-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400">
          Go to Chat
        </button>
      </Link>

      <Link to="/SearchBar">
        <button className="px-6 py-3 bg-blue-500 text-white rounded-lg text-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400">
          Go to Course Search
        </button>
      </Link>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/SearchBar" element={<SearchBar/>} />
        <Route path="/course/:courseId" element={<CourseDetail />} />
      </Routes>
    </Router>
  );
}

export default App;
