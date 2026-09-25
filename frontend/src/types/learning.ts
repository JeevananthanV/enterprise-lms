export type EnrollmentStatus = 'ACTIVE' | 'COMPLETED' | 'CANCELLED' | 'SUSPENDED';
export type QuestionType = 'MULTIPLE_CHOICE' | 'SINGLE_CHOICE' | 'TRUE_FALSE';

export interface EnrolledCourseSummary {
  id: string;
  title: string;
  slug: string;
  short_description?: string;
  category?: string;
  level: string;
  thumbnail_url?: string;
  instructor_name?: string;
  module_count: number;
  lesson_count: number;
  total_duration_minutes: number;
}

export interface EnrollmentItem {
  id: string;
  user_id: number;
  course_id: string;
  status: EnrollmentStatus;
  progress_percentage: number;
  enrolled_at: string;
  completed_at?: string;
  last_accessed_lesson_id?: string;
  completed_lesson_count: number;
  total_lesson_count: number;
  course: EnrolledCourseSummary;
}

export interface LessonProgressResponse {
  id: string;
  user_id: number;
  lesson_id: string;
  is_completed: boolean;
  completed_at?: string;
  last_accessed_at: string;
  course_id?: string;
  course_progress_percentage?: number;
}

export interface PlayerLessonItem {
  id: string;
  module_id: string;
  title: string;
  slug: string;
  content_type: string;
  order_index: number;
  duration_minutes: number;
  is_preview: boolean;
  is_completed: boolean;
  completed_at?: string;
  content?: string;
  quiz_id?: string;
}

export interface PlayerModuleItem {
  id: string;
  title: string;
  slug: string;
  description?: string;
  order_index: number;
  lessons: PlayerLessonItem[];
}

export interface CoursePlayerData {
  course_id: string;
  title: string;
  slug: string;
  description?: string;
  category?: string;
  level: string;
  instructor_name?: string;
  is_enrolled: boolean;
  enrollment_id?: string;
  progress_percentage: number;
  completed_lessons: number;
  total_lessons: number;
  last_accessed_lesson_id?: string;
  modules: PlayerModuleItem[];
}

export interface CourseProgressItem {
  course_id: string;
  course_title: string;
  status: EnrollmentStatus;
  progress_percentage: number;
  completed_lessons: number;
  total_lessons: number;
  enrolled_at: string;
  completed_at?: string;
  last_accessed_at?: string;
}

export interface RecentActivityItem {
  lesson_id: string;
  lesson_title: string;
  is_completed: boolean;
  last_accessed_at: string;
  course_id?: string;
}

export interface StudentOverallProgress {
  total_enrolled_courses: number;
  in_progress_courses: number;
  completed_courses: number;
  overall_completion_percentage: number;
  total_completed_lessons: number;
  total_lessons_available: number;
  courses: CourseProgressItem[];
  recent_activity: RecentActivityItem[];
}

// Quiz Types
export interface QuizAnswerOption {
  id: string;
  answer_text: string;
  order_index: number;
}

export interface QuizQuestion {
  id: string;
  question_text: string;
  question_type: QuestionType;
  points: number;
  order_index: number;
  answers: QuizAnswerOption[];
}

export interface QuizPublicData {
  id: string;
  course_id: string;
  lesson_id?: string;
  title: string;
  description?: string;
  passing_score: number;
  time_limit_minutes?: number;
  max_attempts?: number;
  question_count: number;
  total_points: number;
  questions: QuizQuestion[];
}

export interface QuestionAnswerSubmission {
  question_id: string;
  selected_answer_ids: string[];
}

export interface QuizAttemptResponse {
  id: string;
  quiz_id: string;
  user_id: number;
  score: number;
  passed: boolean;
  passing_score: number;
  total_points: number;
  earned_points: number;
  attempt_number: number;
  started_at: string;
  completed_at?: string;
  lesson_completed: boolean;
}

export interface QuizResultDetail {
  quiz_id: string;
  quiz_title: string;
  passing_score: number;
  attempts: QuizAttemptResponse[];
  highest_score: number;
  has_passed: boolean;
}
