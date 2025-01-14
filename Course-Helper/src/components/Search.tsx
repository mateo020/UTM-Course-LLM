import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
type Result = {
    course_code: string;
    content: string;
  };
  
// Fetch data from the /search API
const fetchSearch = async (userInput: string) => {
  try {
    const response = await axios.post("http://localhost:8080/search", {
      query: userInput, // Send the user input as "query" in the request body
    });
    return response.data.results || []; // Return results from the API response
  } catch (error) {
    console.error("Error fetching data:", error);
    return [];
  }
};

const SearchBar: React.FC = () => {
  const [query, setQuery] = useState<string>(""); // State to store the search query
  const [results, setResults] = useState<Result[]>(
    JSON.parse(localStorage.getItem("searchResults") || "[]") as Result[] //Retrieve cached result if it exists
  );


  const [loading, setLoading] = useState<boolean>(false); // State to indicate loading
  const navigate = useNavigate(); 
    
  
  const handleSearch = async () => {
    if (!query.trim()) {
      alert("Please enter a search term.");
      return;
    }

    setLoading(true); // Set loading to true while fetching
    try {
      const searchResults = await fetchSearch(query); // Fetch results from the API
      setResults(searchResults); // Update results state with API response
      localStorage.setItem("searchResults", JSON.stringify(searchResults)); //Add the search results to localStorage cache
    } catch (error) {
      console.error("Error performing search:", error);
    } finally {
      setLoading(false); // Set loading to false after fetching
    }
  };

  const handleCardClick = (course: Result) => {
    navigate(`/course/${course.course_code}`, {
    state: course
    }); // Navigate to the course details page with the course code
  };

  return (
    <div style={{ padding: "20px", maxWidth: "800px", margin: "auto" }}>
      <h1 style={{ textAlign: "center", marginBottom: "20px" }}>Course Search</h1>
      <input
        type="text"
        placeholder="Enter your search query..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        style={{
          width: "100%",
          padding: "10px",
          marginBottom: "10px",
          borderRadius: "4px",
          border: "1px solid #ccc",
        }}
      />
      <button
        onClick={handleSearch}
        disabled={loading}
        style={{
          width: "100%",
          padding: "10px",
          backgroundColor: loading ? "#ccc" : "#007BFF",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: loading ? "not-allowed" : "pointer",
        }}
      >
        {loading ? "Searching..." : "Search"}
      </button>
      <div style={{ marginTop: "20px" }}>
        <h2 style={{ marginBottom: "10px" }}>Results:</h2>
        {results.length === 0 ? (
          <p>{loading ? "Loading results..." : "No results found."}</p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {results.map((result, index) => (
              <div
                key={index}
                onClick={() => handleCardClick(result)} // Navigate on click
                style={{
                  padding: "20px",
                  border: "1px solid #ddd",
                  borderRadius: "8px",
                  boxShadow: "0 2px 5px rgba(0, 0, 0, 0.1)",
                  backgroundColor: "white",
                  cursor: "pointer", // Indicate it's clickable
                }}
              >
                <h3 style={{ marginBottom: "10px", color: "#007BFF" }}>
                  {result.course_code}
                </h3>
                <p>{result.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchBar;