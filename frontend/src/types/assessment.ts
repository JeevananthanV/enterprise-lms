export interface Assignment {
  id: string;
  course_id: string;
  title: string;
  description?: string;
  instructions?: string;
  max_score: number;
  due_date?: string;
  allowed_file_types?: string[];
  max_file_size_mb: number;
  is_published: boolean;
  order: number;
  created_at: string;
  updated_at: string;
  my_submission?: AssignmentSubmission;
}

export type SubmissionStatus = 'DRAFT' | 'SUBMITTED' | 'GRADED' | 'RETURNED';

export interface AssignmentSubmission {
  id: string;
  assignment_id: string;
  student_id: string;
  status: SubmissionStatus;
  text_content?: string;
  file_url?: string;
  file_name?: string;
  file_size?: number;
  score?: number;
  instructor_feedback?: string;
  submitted_at?: string;
  graded_at?: string;
  graded_by?: string;
  created_at: string;
  updated_at: string;
  student?: {
    id: string;
    email: string;
    full_name: string;
  };
  assignment?: {
    id: string;
    course_id: string;
    title: string;
    max_score: number;
  };
}

export interface QuizAttemptResponse {
  id: string;
  quiz_id: string;
  user_id: string;
  score: number;
  passed: boolean;
  attempt_number: number;
  time_spent_seconds?: number;
  expires_at?: string;
  created_at: string;
  quiz_title?: string;
  passing_score?: number;
  questions?: Array<{
    id: string;
    quiz_id: string;
    question_text: string;
    question_type: string;
    points: number;
    order: number;
    answers: Array<{
      id: string;
      answer_text: string;
      order: number;
    }>;
  }>;
}

export interface CourseCompletionReport {
  course_id: string;
  student_id: string;
  is_completed: boolean;
  overall_progress_percent: number;
  lessons_completed: number;
  total_lessons: number;
  quizzes_passed: number;
  total_quizzes: number;
  assignments_submitted: number;
  total_assignments: number;
  certificate_eligible: boolean;
  certificate?: {
    id: string;
    certificate_number: string;
    issue_date: string;
    verification_url: string;
  };
}
