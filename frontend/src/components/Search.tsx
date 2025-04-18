import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { FaSearch, FaSpinner, FaGraduationCap } from 'react-icons/fa';
import { Link } from 'react-router-dom';

type Result = {
  course_code: string;
  title: string | null;
  content: string;
  credits: string | null;
  prerequisites: string | null;
  score: number;
};

// Fetch data from the /search API
const fetchSearch = async (userInput: string) => {
  try {
    const response = await axios.post("http://localhost:8000/api/v1/search", {
      query: userInput
    });
    return response.data.results || [];
  } catch (error) {
    console.error("Error fetching data:", error);
    return [];
  }
};

const SearchBar: React.FC = () => {
  const [query, setQuery] = useState<string>("");
  const [results, setResults] = useState<Result[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post("http://localhost:8000/api/v1/search/search", {
        query: query.trim()
      });
      setResults(response.data.results || []);
    } catch (error) {
      console.error("Error performing search:", error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleCardClick = (course: Result) => {
    navigate(`/course/${course.course_code}`, { state: course });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-2 mb-8">
          <Link to="/" className="flex items-center gap-2 hover:text-indigo-600 transition-colors duration-200">
            <FaGraduationCap className="text-3xl text-indigo-600" />
            <span className="text-3xl font-bold text-indigo-900">Course Search</span>
          </Link>
        </div>

        <div className="relative mb-8">
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Search by course code, title, or keyword..."
              className="w-full pl-12 pr-4 py-3 rounded-xl border-2 border-indigo-200 
                         focus:ring-2 focus:ring-indigo-500 focus:border-indigo-300 
                         shadow-sm transition-all duration-200
                         placeholder-indigo-400 text-indigo-900 bg-white/80
                         hover:border-indigo-300"
            />
            <FaSearch className="absolute left-4 top-1/2 transform -translate-y-1/2 text-indigo-400" />
          </div>
        </div>

        <button
          onClick={handleSearch}
          disabled={loading}
          className="w-full py-3 px-4 bg-indigo-600 text-white rounded-xl
                     hover:bg-indigo-700 active:scale-95 transition-all duration-200
                     disabled:opacity-50 disabled:cursor-not-allowed
                     flex items-center justify-center gap-2
                     shadow-md hover:shadow-lg"
        >
          {loading ? (
            <>
              <FaSpinner className="animate-spin" />
              <span>Searching...</span>
            </>
          ) : (
            <>
              <FaSearch />
              <span>Search</span>
            </>
          )}
        </button>

        <div className="mt-8 space-y-4">
          {results.length > 0 ? (
            results.map((result, index) => (
              <div
                key={index}
                onClick={() => handleCardClick(result)}
                className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md
                         transition-all duration-200 cursor-pointer
                         border border-indigo-100 hover:border-indigo-200
                         hover:bg-indigo-50/50"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-grow">
                    <h3 className="text-xl font-semibold text-indigo-700">
                      {result.course_code}
                    </h3>
                    {result.title && (
                      <p className="text-indigo-900 font-medium mt-1">{result.title}</p>
                    )}
                    <p className="text-indigo-800 mt-2 line-clamp-2">{result.content}</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {result.credits && (
                        <span className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full text-sm">
                          {result.credits}
                        </span>
                      )}
                      {result.prerequisites && (
                        <span className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full text-sm">
                          Prerequisites: {result.prerequisites}
                        </span>
                      )}
                    </div>
                  </div>
                  <span className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full text-sm ml-4">
                    Score: {result.score.toFixed(2)}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-12 bg-white rounded-xl shadow-sm border border-indigo-100">
              <div className="text-6xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold text-indigo-800 mb-2">
                {loading ? "Searching..." : "No matching courses found"}
              </h3>
              <p className="text-indigo-600">
                Try searching by course code (e.g., CSC108) or keywords
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchBar;