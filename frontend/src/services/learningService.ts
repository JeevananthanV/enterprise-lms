import { apiClient } from './apiClient';
import {
  EnrollmentItem,
  LessonProgressResponse,
  CoursePlayerData,
  StudentOverallProgress,
  QuizPublicData,
  QuizAttemptResponse,
  QuizResultDetail,
  QuestionAnswerSubmission,
} from '../types/learning';

export const learningService = {
  // Enroll in Course
  async enrollCourse(courseId: string): Promise<any> {
    const res = await apiClient.post(`/api/v1/courses/${courseId}/enroll`);
    return res.data;
  },

  // My Enrollments
  async getMyEnrollments(): Promise<EnrollmentItem[]> {
    const res = await apiClient.get<EnrollmentItem[]>('/api/v1/me/enrollments');
    return res.data;
  },

  // Student Progress Analytics
  async getMyProgress(): Promise<StudentOverallProgress> {
    const res = await apiClient.get<StudentOverallProgress>('/api/v1/me/progress');
    return res.data;
  },

  // Course Player Syllabus & Progress
  async getCoursePlayerData(courseId: string): Promise<CoursePlayerData> {
    const res = await apiClient.get<CoursePlayerData>(`/api/v1/courses/${courseId}/player`);
    return res.data;
  },

  // Update Lesson Progress
  async updateLessonProgress(lessonId: string, isCompleted: boolean): Promise<LessonProgressResponse> {
    const res = await apiClient.post<LessonProgressResponse>(`/api/v1/lessons/${lessonId}/progress`, {
      is_completed: isCompleted,
    });
    return res.data;
  },

  // Quiz Endpoints
  async getQuiz(quizId: string): Promise<QuizPublicData> {
    const res = await apiClient.get<QuizPublicData>(`/api/v1/quizzes/${quizId}`);
    return res.data;
  },

  async submitQuizAttempt(
    quizId: string,
    submissions: QuestionAnswerSubmission[]
  ): Promise<QuizAttemptResponse> {
    const res = await apiClient.post<QuizAttemptResponse>(`/api/v1/quizzes/${quizId}/attempts`, {
      submissions,
    });
    return res.data;
  },

  async getQuizResults(quizId: string): Promise<QuizResultDetail> {
    const res = await apiClient.get<QuizResultDetail>(`/api/v1/quizzes/${quizId}/results`);
    return res.data;
  },
};
