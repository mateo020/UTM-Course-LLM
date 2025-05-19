// components/RecommendedCarousel.tsx
import React, { useEffect, useState } from "react";

interface Recommendation {
  course_id: string;
  similarity: number;
}

interface Props {
  courseId: string;
  apiUrl: string;
}

export const RecommendedCarousel: React.FC<Props> = ({ courseId, apiUrl }) => {
  const [courses, setCourses] = useState<Recommendation[]>([]);

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

  return (
    <div className="mt-10">
      <h3 className="text-xl font-semibold text-indigo-800 mb-4">Recommended Courses</h3>
      <div className="flex overflow-x-auto space-x-4 scrollbar-hide">
        {courses.map((course, index) => (
          <div
            key={index}
            className="min-w-[200px] bg-white shadow rounded-lg p-4 hover:shadow-md transition"
          >
            <h4 className="font-bold text-indigo-700">{course.course_id}</h4>
            <p className="text-sm text-gray-600">Similarity: {course.similarity.toFixed(2)}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
