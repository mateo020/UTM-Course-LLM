import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Chat } from './components/Chat';
import SearchBar from "./components/Search"; 
import CourseDetail from './components/CourseDetail';
import './App.css';


function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 relative overflow-hidden">
      {/* Background shapes */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-0 w-96 h-96 bg-blue-100 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-96 h-96 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative min-h-screen flex flex-col items-center justify-center px-4">
        {/* Speech bubble */}
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-lg relative mb-8 max-w-md w-full">
          {/* <div className="absolute bottom-0 right-0 w-8 h-8 bg-white/80 backdrop-blur-sm transform rotate-45 -translate-x-4 translate-y-4"></div> */}
          <h1 className="text-4xl font-bold text-center">
            UTM<br />
            <span className="text-blue-600">Chat App</span>
          </h1>
        </div>

        {/* Buttons */}
        <div className="flex gap-4">
          <Link to="/chat">
            <button className="px-8 py-3 bg-blue-500 text-white rounded-xl text-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all duration-200 shadow-md hover:shadow-lg">
              Go to Chat
            </button>
          </Link>

          <Link to="/SearchBar">
            <button className="px-8 py-3 bg-blue-500 text-white rounded-xl text-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all duration-200 shadow-md hover:shadow-lg">
              Go to Course Search
            </button>
          </Link>
        </div>
      </div>
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
