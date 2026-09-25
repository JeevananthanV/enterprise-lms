from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.enrollment import EnrollmentStatus
from app.models.quiz import QuestionType


# Enrollment Schemas
class EnrollmentBase(BaseModel):
    course_id: str


class EnrollmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: int
    course_id: str
    status: EnrollmentStatus
    progress_percentage: float
    enrolled_at: datetime
    completed_at: Optional[datetime] = None


class EnrolledCourseSummary(BaseModel):
    id: str
    title: str
    slug: str
    short_description: Optional[str] = None
    category: Optional[str] = None
    level: str
    thumbnail_url: Optional[str] = None
    instructor_name: Optional[str] = None
    module_count: int = 0
    lesson_count: int = 0
    total_duration_minutes: int = 0


class EnrollmentWithCourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: int
    course_id: str
    status: EnrollmentStatus
    progress_percentage: float
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    last_accessed_lesson_id: Optional[str] = None
    completed_lesson_count: int = 0
    total_lesson_count: int = 0
    course: EnrolledCourseSummary


# Lesson Progress Schemas
class LessonProgressUpdateRequest(BaseModel):
    is_completed: bool = True


class LessonProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: int
    lesson_id: str
    is_completed: bool
    completed_at: Optional[datetime] = None
    last_accessed_at: datetime
    course_id: Optional[str] = None
    course_progress_percentage: Optional[float] = None


# Student Learning & Course Player Schemas
class PlayerLessonItem(BaseModel):
    id: str
    module_id: str
    title: str
    slug: str
    content_type: str
    order_index: int = 1
    duration_minutes: int = 0
    is_preview: bool = False
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    content: Optional[str] = None
    quiz_id: Optional[str] = None


class PlayerModuleItem(BaseModel):
    id: str
    title: str
    slug: Optional[str] = None
    description: Optional[str] = None
    order_index: int = 1
    lessons: List[PlayerLessonItem] = []


class CoursePlayerResponse(BaseModel):
    course_id: str
    title: str
    slug: str
    description: Optional[str] = None
    category: Optional[str] = None
    level: str
    instructor_name: Optional[str] = None
    is_enrolled: bool = False
    enrollment_id: Optional[str] = None
    progress_percentage: float = 0.0
    completed_lessons: int = 0
    total_lessons: int = 0
    last_accessed_lesson_id: Optional[str] = None
    modules: List[PlayerModuleItem] = []


# Progress Dashboard Analytics
class CourseProgressItem(BaseModel):
    course_id: str
    course_title: str
    status: EnrollmentStatus
    progress_percentage: float
    completed_lessons: int
    total_lessons: int
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None


class StudentOverallProgressResponse(BaseModel):
    total_enrolled_courses: int
    in_progress_courses: int
    completed_courses: int
    overall_completion_percentage: float
    total_completed_lessons: int
    total_lessons_available: int
    courses: List[CourseProgressItem] = []
    recent_activity: List[Dict[str, Any]] = []


# Quiz Schemas
class QuizPublicAnswerOption(BaseModel):
    id: str
    answer_text: str
    order_index: int


class QuizPublicQuestion(BaseModel):
    id: str
    question_text: str
    question_type: QuestionType
    points: int
    order_index: int
    answers: List[QuizPublicAnswerOption] = []


class QuizPublicResponse(BaseModel):
    id: str
    course_id: str
    lesson_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    passing_score: int
    time_limit_minutes: Optional[int] = None
    max_attempts: Optional[int] = None
    question_count: int
    total_points: int
    questions: List[QuizPublicQuestion] = []


class QuestionAnswerSubmission(BaseModel):
    question_id: str
    selected_answer_ids: List[str]


class QuizAttemptSubmitRequest(BaseModel):
    submissions: List[QuestionAnswerSubmission]


class QuizAttemptResponse(BaseModel):
    id: str
    quiz_id: str
    user_id: int
    score: float
    passed: bool
    passing_score: int
    total_points: int
    earned_points: float
    attempt_number: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    lesson_completed: bool = False


class QuizResultDetailResponse(BaseModel):
    quiz_id: str
    quiz_title: str
    passing_score: int
    attempts: List[QuizAttemptResponse] = []
    highest_score: float = 0.0
    has_passed: bool = False
