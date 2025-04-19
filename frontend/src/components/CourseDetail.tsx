import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Graph } from "./Graph";
import { FaArrowLeft, FaGraduationCap, FaBook, FaClock } from "react-icons/fa";

type Course = {
  course_code: string;
  content: string;
  title?: string;
  prerequisites?: string;
  description?: string;
};

const CourseDetail: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const course: Course = location.state as Course;

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-xl
                     hover:bg-indigo-700 active:scale-95 transition-all duration-200"
          >
            <FaArrowLeft />
            Back to Search
          </button>
          <div className="flex items-center gap-2">
            <FaGraduationCap className="text-3xl text-indigo-600" />
            <h1 className="text-3xl font-bold text-indigo-900">Course Details</h1>
          </div>
        </div>

        {/* Course Information Card */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-3xl font-bold text-indigo-700 mb-2">
                {course.course_code}
              </h2>
              {course.title && (
                <h3 className="text-xl text-indigo-600">{course.title}</h3>
              )}
            </div>
            <div className="flex items-center gap-2 bg-indigo-100 px-4 py-2 rounded-full">
              <FaBook className="text-indigo-600" />
              <span className="text-indigo-700 font-medium">Course Details</span>
            </div>
          </div>

          <div className="space-y-6">
            {/* Description */}
            <div className="bg-indigo-50 rounded-lg p-6">
              <h4 className="text-lg font-semibold text-indigo-900 mb-3">Description</h4>
              <p className="text-indigo-800">{course.description}</p>
            </div>

            {/* Prerequisites */}
            {course.prerequisites && (
              <div className="bg-purple-50 rounded-lg p-6">
                <div className="flex items-center gap-2 mb-3">
                  <FaClock className="text-purple-600" />
                  <h4 className="text-lg font-semibold text-purple-900">Prerequisites</h4>
                </div>
                <p className="text-purple-800">{course.prerequisites}</p>
              </div>
            )}
          </div>
        </div>

        {/* Graph Section */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-indigo-900 mb-6 flex items-center gap-2">
            <FaGraduationCap className="text-indigo-600" />
            Course Prerequisites Map
          </h2>
          <div className="h-[600px] w-full bg-gray-50 rounded-lg overflow-hidden">
            <Graph focusId={course.title} graphUrl="http://localhost:8000/api/v1/prereq-graph" />
          </div>
          <div className="mt-4 text-sm text-gray-600">
            <p>• Blue node: Current course</p>
            <p>• Connected nodes: Related prerequisite courses</p>
            <p>• Arrows indicate prerequisite relationships</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseDetail;
