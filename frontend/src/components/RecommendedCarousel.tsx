import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

interface Recommendation {
  course_id: string;
  similarity: number;
}

interface Props {
  courseId: string | undefined;
  courseName: string;
  apiUrl: string;
}

export const RecommendedCarousel: React.FC<Props> = ({ courseId, apiUrl }) => {
  const [courses, setCourses] = useState<Recommendation[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchRecommendations = async () => {
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
      }
    };

    fetchRecommendations();
  }, [courseId, apiUrl]);

  const handleClick = (courseId: string) => {
    navigate(`/course/${courseId}`, { state: courseId });
  };

  return (
    <div className="mt-10">
      <h3 className="text-2xl font-semibold text-indigo-800 mb-4">Recommended Courses</h3>
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
    </div>
  );
};
