from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from v1.src.Recommendation.recSys import CourseRecommender

router = APIRouter()

class RecommendationRequest(BaseModel):
    course_id: str
    top_k: int = 9

class CourseRecommendation(BaseModel):
    course_id: str
    similarity: float

@router.post("/recommend", response_model=List[CourseRecommendation])
def get_recommendations(request: RecommendationRequest):
    recommender = CourseRecommender()
    """Get top-k recommended courses for a given course ID."""
    recommendations = recommender.get_similar_courses(
        course_id=request.course_id,
        top_k=request.top_k
    )

    if not recommendations:
        raise HTTPException(status_code=404, detail="Course ID not found or no recommendations available.")

    return [CourseRecommendation(course_id=course, similarity=score) for course, score in recommendations]
