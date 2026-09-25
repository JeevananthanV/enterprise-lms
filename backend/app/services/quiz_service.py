import json
import random
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.quiz import Quiz, Question, Answer, QuizAttempt, QuestionType
from app.models.enrollment import EnrollmentStatus
from app.repositories.quiz_repository import quiz_repository
from app.repositories.course_repository import course_repository
from app.repositories.enrollment_repository import enrollment_repository
from app.repositories.progress_repository import progress_repository
from app.schemas.learning import (
    QuizPublicResponse,
    QuizPublicQuestion,
    QuizPublicAnswerOption,
    QuizAttemptResponse,
    QuizResultDetailResponse,
    QuestionAnswerSubmission,
)
from app.schemas.assessment import (
    TimedQuizAttemptStartResponse,
    TimedQuizSubmitRequest,
    TimedQuizAttemptDetailResponse,
    SanitizedQuestion,
    SanitizedAnswerOption,
)


class QuizService:
    async def get_sanitized_quiz_for_student(
        self, db: AsyncSession, user: User, quiz_id: str
    ) -> QuizPublicResponse:
        """Fetch quiz structure with question options sanitized (no answer leakage)."""
        quiz = await quiz_repository.get_with_questions_and_answers(db, quiz_id)
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found.",
            )

        # Verify student enrollment in the course
        is_admin = user.role == UserRole.PLATFORM_ADMIN
        enrollment = await enrollment_repository.get_by_user_and_course(
            db, user_id=user.id, course_id=quiz.course_id
        )

        if not is_admin and not enrollment:
            # Check if linked lesson is preview
            is_preview = quiz.lesson and quiz.lesson.is_free_preview
            if not is_preview:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You must be enrolled in this course to view this quiz.",
                )

        # Sanitize questions: strip is_correct flag
        public_questions: List[QuizPublicQuestion] = []
        total_points = 0

        for q in quiz.questions:
            total_points += q.points
            public_answers = [
                QuizPublicAnswerOption(
                    id=a.id,
                    answer_text=a.answer_text,
                    order_index=a.order_index,
                )
                for a in q.answers
            ]
            public_questions.append(
                QuizPublicQuestion(
                    id=q.id,
                    question_text=q.question_text,
                    question_type=q.question_type,
                    points=q.points,
                    order_index=q.order_index,
                    answers=public_answers,
                )
            )

        return QuizPublicResponse(
            id=quiz.id,
            course_id=quiz.course_id,
            lesson_id=quiz.lesson_id,
            title=quiz.title,
            description=quiz.description,
            passing_score=quiz.passing_score,
            time_limit_minutes=quiz.time_limit_minutes,
            max_attempts=quiz.max_attempts,
            question_count=len(public_questions),
            total_points=total_points,
            questions=public_questions,
        )

    # --- Timed & Randomized Quiz Attempts ---

    async def start_timed_attempt(
        self, db: AsyncSession, user: User, quiz_id: str
    ) -> TimedQuizAttemptStartResponse:
        """Starts a timed quiz attempt with locked question order/randomization."""
        quiz = await quiz_repository.get_with_questions_and_answers(db, quiz_id)
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found.",
            )

        # Verify enrollment
        is_admin = user.role == UserRole.PLATFORM_ADMIN
        enrollment = await enrollment_repository.get_by_user_and_course(
            db, user_id=user.id, course_id=quiz.course_id
        )
        if not is_admin and not enrollment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be enrolled in this course to take this quiz.",
            )

        # Check attempt limits
        past_attempts = await quiz_repository.list_attempts_for_user(db, user.id, quiz.id)
        attempt_count = len(past_attempts)
        if quiz.max_attempts and attempt_count >= quiz.max_attempts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You have reached the maximum allowed attempts ({quiz.max_attempts}) for this quiz.",
            )

        # Handle question order (Randomize if enabled)
        questions_pool = list(quiz.questions)
        if getattr(quiz, "randomize_questions", False):
            random.shuffle(questions_pool)

        selected_ids = [q.id for q in questions_pool]
        now = datetime.now(timezone.utc)
        expires_at = None
        time_limit_seconds = None

        if quiz.time_limit_minutes and quiz.time_limit_minutes > 0:
            time_limit_seconds = quiz.time_limit_minutes * 60
            expires_at = now + timedelta(seconds=time_limit_seconds)

        attempt = QuizAttempt(
            user_id=user.id,
            quiz_id=quiz.id,
            score=0.0,
            passed=False,
            attempt_number=attempt_count + 1,
            started_at=now,
            expires_at=expires_at,
            completed_at=None,
            selected_question_ids=json.dumps(selected_ids),
        )
        attempt = await quiz_repository.create_attempt(db, attempt)

        # Build sanitized questions payload in the selected order
        sanitized_questions: List[SanitizedQuestion] = []
        for q in questions_pool:
            sanitized_answers = [
                SanitizedAnswerOption(
                    id=a.id,
                    answer_text=a.answer_text,
                    order_index=a.order_index,
                )
                for a in q.answers
            ]
            sanitized_questions.append(
                SanitizedQuestion(
                    id=q.id,
                    question_text=q.question_text,
                    question_type=q.question_type,
                    points=q.points,
                    order_index=q.order_index,
                    answers=sanitized_answers,
                )
            )

        attempts_remaining = (
            (quiz.max_attempts - attempt.attempt_number)
            if quiz.max_attempts
            else None
        )

        return TimedQuizAttemptStartResponse(
            attempt_id=attempt.id,
            quiz_id=quiz.id,
            quiz_title=quiz.title,
            attempt_number=attempt.attempt_number,
            max_attempts=quiz.max_attempts,
            attempts_remaining=attempts_remaining,
            time_limit_minutes=quiz.time_limit_minutes,
            time_limit_seconds=time_limit_seconds,
            started_at=attempt.started_at,
            expires_at=attempt.expires_at,
            passing_score=quiz.passing_score,
            total_questions=len(sanitized_questions),
            questions=sanitized_questions,
        )

    async def get_attempt_detail(
        self, db: AsyncSession, user: User, attempt_id: str
    ) -> TimedQuizAttemptStartResponse:
        """Fetch active attempt with its deterministic question sequence."""
        attempt = await quiz_repository.get_attempt_by_id(db, attempt_id)
        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz attempt not found.",
            )

        if attempt.user_id != user.id and user.role != UserRole.PLATFORM_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. This attempt does not belong to you.",
            )

        quiz = await quiz_repository.get_with_questions_and_answers(db, attempt.quiz_id)
        selected_ids = []
        if attempt.selected_question_ids:
            try:
                selected_ids = json.loads(attempt.selected_question_ids)
            except Exception:
                selected_ids = [q.id for q in quiz.questions]
        else:
            selected_ids = [q.id for q in quiz.questions]

        # Order questions matching selected_ids
        q_map = {q.id: q for q in quiz.questions}
        ordered_questions = [q_map[qid] for qid in selected_ids if qid in q_map]

        sanitized_questions: List[SanitizedQuestion] = []
        for q in ordered_questions:
            sanitized_answers = [
                SanitizedAnswerOption(
                    id=a.id,
                    answer_text=a.answer_text,
                    order_index=a.order_index,
                )
                for a in q.answers
            ]
            sanitized_questions.append(
                SanitizedQuestion(
                    id=q.id,
                    question_text=q.question_text,
                    question_type=q.question_type,
                    points=q.points,
                    order_index=q.order_index,
                    answers=sanitized_answers,
                )
            )

        time_limit_seconds = (
            quiz.time_limit_minutes * 60 if quiz.time_limit_minutes else None
        )
        attempts_remaining = (
            (quiz.max_attempts - attempt.attempt_number)
            if quiz.max_attempts
            else None
        )

        return TimedQuizAttemptStartResponse(
            attempt_id=attempt.id,
            quiz_id=quiz.id,
            quiz_title=quiz.title,
            attempt_number=attempt.attempt_number,
            max_attempts=quiz.max_attempts,
            attempts_remaining=attempts_remaining,
            time_limit_minutes=quiz.time_limit_minutes,
            time_limit_seconds=time_limit_seconds,
            started_at=attempt.started_at,
            expires_at=attempt.expires_at,
            passing_score=quiz.passing_score,
            total_questions=len(sanitized_questions),
            questions=sanitized_questions,
        )

    async def submit_timed_attempt(
        self,
        db: AsyncSession,
        user: User,
        quiz_id: str,
        attempt_id: str,
        data: TimedQuizSubmitRequest,
    ) -> TimedQuizAttemptDetailResponse:
        """Submits answers for a timed attempt with authoritative server-side scoring & timing."""
        attempt = await quiz_repository.get_attempt_by_id(db, attempt_id)
        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz attempt not found.",
            )

        if attempt.user_id != user.id and user.role != UserRole.PLATFORM_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied.",
            )

        if attempt.completed_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This attempt has already been submitted and finalized.",
            )

        quiz = await quiz_repository.get_with_questions_and_answers(db, quiz_id)
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found.",
            )

        now = datetime.now(timezone.utc)

        # Server-authoritative timer enforcement
        status_label = "SUBMITTED"
        if attempt.expires_at:
            exp_utc = (
                attempt.expires_at
                if attempt.expires_at.tzinfo
                else attempt.expires_at.replace(tzinfo=timezone.utc)
            )
            if now > (exp_utc + timedelta(seconds=15)):
                status_label = "EXPIRED"

        # Calculate score server-side
        total_possible_points = sum(q.points for q in quiz.questions)
        earned_points = 0.0
        correct_questions_count = 0

        submission_map = {item.question_id: set(item.selected_answer_ids) for item in data.answers}

        for question in quiz.questions:
            correct_answer_ids = {a.id for a in question.answers if a.is_correct}
            user_selected_ids = submission_map.get(question.id, set())

            if user_selected_ids == correct_answer_ids and len(correct_answer_ids) > 0:
                earned_points += question.points
                correct_questions_count += 1

        score_percentage = (
            round((earned_points / total_possible_points) * 100.0, 1)
            if total_possible_points > 0
            else 100.0
        )
        passed = score_percentage >= quiz.passing_score

        # Calculate time spent
        started_utc = (
            attempt.started_at
            if attempt.started_at.tzinfo
            else attempt.started_at.replace(tzinfo=timezone.utc)
        )
        time_spent_seconds = int((now - started_utc).total_seconds())

        attempt.score = score_percentage
        attempt.passed = passed
        attempt.completed_at = now
        attempt.time_spent_seconds = max(0, time_spent_seconds)

        attempt = await quiz_repository.update_attempt(db, attempt)

        # If passed, auto-complete linked lesson
        if passed and quiz.lesson_id:
            await progress_repository.upsert_lesson_progress(
                db,
                user_id=user.id,
                lesson_id=quiz.lesson_id,
                is_completed=True,
            )

        return TimedQuizAttemptDetailResponse(
            id=attempt.id,
            quiz_id=quiz.id,
            attempt_number=attempt.attempt_number,
            score=score_percentage,
            passed=passed,
            passing_score=quiz.passing_score,
            started_at=attempt.started_at,
            completed_at=attempt.completed_at,
            time_spent_seconds=attempt.time_spent_seconds,
            status=status_label,
            total_questions=len(quiz.questions),
            correct_questions=correct_questions_count,
        )

    # --- Phase 5 Legacy Single-Step Submission Compatibility ---

    async def submit_quiz_attempt(
        self,
        db: AsyncSession,
        user: User,
        quiz_id: str,
        submissions: List[QuestionAnswerSubmission],
    ) -> QuizAttemptResponse:
        """Legacy single-turn submit compatibility."""
        quiz = await quiz_repository.get_with_questions_and_answers(db, quiz_id)
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found.",
            )

        past_attempts_count = await quiz_repository.get_attempt_count(db, user.id, quiz.id)
        if quiz.max_attempts and past_attempts_count >= quiz.max_attempts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You have reached the maximum allowed attempts ({quiz.max_attempts}) for this quiz.",
            )

        total_possible_points = sum(q.points for q in quiz.questions)
        earned_points = 0.0
        submission_map = {s.question_id: set(s.selected_answer_ids) for s in submissions}

        for question in quiz.questions:
            correct_answer_ids = {a.id for a in question.answers if a.is_correct}
            user_selected_ids = submission_map.get(question.id, set())
            if user_selected_ids == correct_answer_ids and len(correct_answer_ids) > 0:
                earned_points += question.points

        score_percentage = (
            round((earned_points / total_possible_points) * 100.0, 1)
            if total_possible_points > 0
            else 100.0
        )
        passed = score_percentage >= quiz.passing_score
        now = datetime.now(timezone.utc)

        attempt = QuizAttempt(
            user_id=user.id,
            quiz_id=quiz.id,
            score=score_percentage,
            passed=passed,
            attempt_number=past_attempts_count + 1,
            started_at=now,
            completed_at=now,
            time_spent_seconds=0,
        )
        attempt = await quiz_repository.create_attempt(db, attempt)

        lesson_completed = False
        if passed and quiz.lesson_id:
            await progress_repository.upsert_lesson_progress(
                db,
                user_id=user.id,
                lesson_id=quiz.lesson_id,
                is_completed=True,
            )
            lesson_completed = True

        return QuizAttemptResponse(
            id=attempt.id,
            quiz_id=quiz.id,
            user_id=user.id,
            score=score_percentage,
            passed=passed,
            passing_score=quiz.passing_score,
            total_points=total_possible_points,
            earned_points=earned_points,
            attempt_number=attempt.attempt_number,
            started_at=attempt.started_at,
            completed_at=attempt.completed_at,
            lesson_completed=lesson_completed,
        )

    async def get_student_quiz_results(
        self, db: AsyncSession, user: User, quiz_id: str
    ) -> QuizResultDetailResponse:
        """Fetch past attempts and result status for a quiz."""
        quiz = await quiz_repository.get(db, quiz_id)
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found.",
            )

        attempts = await quiz_repository.list_attempts_for_user(db, user.id, quiz.id)
        total_possible_points = sum(q.points for q in quiz.questions) if quiz.questions else 0

        attempt_responses = [
            QuizAttemptResponse(
                id=a.id,
                quiz_id=a.quiz_id,
                user_id=a.user_id,
                score=a.score,
                passed=a.passed,
                passing_score=quiz.passing_score,
                total_points=total_possible_points,
                earned_points=round((a.score / 100.0) * total_possible_points, 1),
                attempt_number=a.attempt_number,
                started_at=a.started_at,
                completed_at=a.completed_at,
                lesson_completed=a.passed and quiz.lesson_id is not None,
            )
            for a in attempts
        ]

        highest_score = max([a.score for a in attempts], default=0.0)
        has_passed = any(a.passed for a in attempts)

        return QuizResultDetailResponse(
            quiz_id=quiz.id,
            quiz_title=quiz.title,
            passing_score=quiz.passing_score,
            attempts=attempt_responses,
            highest_score=highest_score,
            has_passed=has_passed,
        )


quiz_service = QuizService()

