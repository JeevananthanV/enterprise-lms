from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.models.assignment import SubmissionStatus


# ==========================================
# 1. Assignment Schemas
# ==========================================

class AssignmentBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    max_marks: int = Field(default=100, ge=1, le=1000)
    due_date: Optional[datetime] = None
    allowed_file_types: str = Field(default="pdf,zip,docx,txt,png,jpg")
    max_file_size_mb: int = Field(default=10, ge=1, le=100)
    module_id: Optional[str] = None
    lesson_id: Optional[str] = None


class AssignmentCreate(AssignmentBase):
    course_id: str


class AssignmentResponse(AssignmentBase):
    id: str
    course_id: str
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssignmentSubmissionCreate(BaseModel):
    submission_text: Optional[str] = None
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None


class AssignmentSubmissionResponse(BaseModel):
    id: str
    assignment_id: str
    student_id: int
    student_name: Optional[str] = None
    student_email: Optional[str] = None
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    submission_text: Optional[str] = None
    status: SubmissionStatus
    score: Optional[float] = None
    feedback: Optional[str] = None
    graded_by: Optional[int] = None
    graded_at: Optional[datetime] = None
    submitted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubmissionGradeRequest(BaseModel):
    score: float = Field(..., ge=0.0)
    feedback: Optional[str] = Field(default="")


# ==========================================
# 2. Advanced & Timed Quiz Schemas
# ==========================================

class SanitizedAnswerOption(BaseModel):
    id: str
    answer_text: str
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class SanitizedQuestion(BaseModel):
    id: str
    question_text: str
    question_type: str
    points: int
    order_index: int
    answers: List[SanitizedAnswerOption]

    model_config = ConfigDict(from_attributes=True)


class TimedQuizAttemptStartResponse(BaseModel):
    attempt_id: str
    quiz_id: str
    quiz_title: str
    attempt_number: int
    max_attempts: Optional[int] = None
    attempts_remaining: Optional[int] = None
    time_limit_minutes: Optional[int] = None
    time_limit_seconds: Optional[int] = None
    started_at: datetime
    expires_at: Optional[datetime] = None
    passing_score: int
    total_questions: int
    questions: List[SanitizedQuestion]


class QuizAnswerItem(BaseModel):
    question_id: str
    selected_answer_ids: List[str] = []
    text_answer: Optional[str] = None


class TimedQuizSubmitRequest(BaseModel):
    answers: List[QuizAnswerItem]


class TimedQuizAttemptDetailResponse(BaseModel):
    id: str
    quiz_id: str
    attempt_number: int
    score: float
    passed: bool
    passing_score: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    time_spent_seconds: Optional[int] = None
    status: str
    total_questions: int
    correct_questions: int


# ==========================================
# 3. Course Completion & Certification Schemas
# ==========================================

class CourseCompletionReport(BaseModel):
    course_id: str
    course_title: str
    student_id: int
    student_name: str
    completion_percentage: float
    is_completed: bool
    completed_lessons: int
    total_lessons: int
    passed_quizzes: int
    total_quizzes: int
    graded_assignments: int
    total_assignments: int
    eligible_for_certificate: bool
    certificate_id: Optional[str] = None
    certificate_number: Optional[str] = None


class CertificateResponse(BaseModel):
    id: str
    certificate_number: str
    enrollment_id: str
    student_id: int
    student_name: str
    course_id: str
    course_title: str
    instructor_name: str
    issued_at: datetime
    completion_date: datetime
    verification_hash: str
    pdf_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CertificateVerifyResponse(BaseModel):
    is_valid: bool
    certificate_number: str
    student_name: str
    course_title: str
    issued_at: datetime
    completion_date: datetime
    verification_hash: str
    institution: str = "Enterprise LMS Global Academy"
