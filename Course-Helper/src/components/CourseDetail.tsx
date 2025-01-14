import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

type Course = {
  course_code: string;
  content: string;
};

const CourseDetail: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Retrieve course data from state
  const course: Course = location.state as Course;

  return (
    <div style={{ padding: "20px", maxWidth: "800px", margin: "auto" }}>
      <button
        onClick={() => navigate(-1)} // Navigate back to the search page
        style={{
          marginBottom: "20px",
          padding: "10px",
          backgroundColor: "#007BFF",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        Back to Search
      </button>
      <h1 style={{ textAlign: "center", marginBottom: "20px" }}>
        {course.course_code}
      </h1>
      <p style={{ marginBottom: "20px" }}>{course.content}</p>
      <h2>Suggested Courses</h2>
      <p>No suggested courses available.</p>
    </div>
  );
};

export default CourseDetail;
