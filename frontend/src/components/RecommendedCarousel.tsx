import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
interface Recommendation {
  course_id: string;
  similarity: number;
}

interface Props {
  courseId: string | undefined;
  courseName: string;
  apiUrl: string;
}
type Result = {
  course_code: string;
  title: string | null;
  content: string;
  credits: string | null;
  prerequisites: string | null;
  score: number;
};

export const RecommendedCarousel: React.FC<Props> = ({ courseId, apiUrl }) => {
  const [courses, setCourses] = useState<Recommendation[]>([]);
  const navigate = useNavigate();
  const [loading, setLoading] = useState<boolean>(true);


  useEffect(() => {
    const fetchRecommendations = async () => {
      setLoading(true);
      try {
        const response = await fetch(apiUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ course_id: courseId, top_k: 9 }),
        });

        if (!response.ok) throw new Error("Failed to fetch recommendations");
        const data = await response.json();
        setCourses(data);
      } catch (error) {
        console.error("Recommendation error:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [courseId, apiUrl]);

  const handleClick = async (courseId: string) => {
    const response = await axios.get("http://localhost:8000/api/v1/search", {
        params: {
          query: courseId
        }
      });
      const resultList: Result[] = response.data.results || [];

      if (resultList.length == 1) {
        const course = resultList[0]; // the only result
        navigate(`/course/${course.title}`, { state: course });
      } else {
        console.warn("Expected one result, got:", resultList.length);
        // Optionally: show a toast or redirect to search results
      }
    
    
  };
  return (
    <div className="mt-10">
      <h3 className="text-2xl font-semibold text-indigo-800 mb-4">Recommended Courses</h3>
  
      {loading ? (
        <div className="flex justify-center items-center h-48">
          <div className="w-10 h-10 border-4 border-indigo-300 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <div className="flex overflow-x-auto space-x-6 scrollbar-hide">
          {courses.map((course, index) => (
            <div
              key={index}
              onClick={() => handleClick(course.course_id)}
              className="min-w-[280px] h-[180px] bg-white shadow-lg rounded-2xl p-6 
                         hover:shadow-xl cursor-pointer transition-transform transform hover:scale-105"
            >
              <h4 className="text-xl font-bold text-indigo-700 mb-2">
                {course.course_id}
              </h4>
              <p className="text-gray-600 text-sm">Similarity score</p>
              <p className="text-indigo-500 font-semibold text-lg">
                {course.similarity.toFixed(2)}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
  
};
