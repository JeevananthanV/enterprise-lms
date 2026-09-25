import { apiClient } from './apiClient';
import {
  Assignment,
  AssignmentSubmission,
  CourseCompletionReport,
} from '../types/assessment';

export const assessmentService = {
  // --- Student Assignment APIs ---
  async getCourseAssignments(courseId: string): Promise<Assignment[]> {
    const response = await apiClient.get<Assignment[]>(`/api/v1/courses/${courseId}/assignments`);
    return response.data;
  },

  async getAssignmentDetails(assignmentId: string): Promise<Assignment> {
    const response = await apiClient.get<Assignment>(`/api/v1/assignments/${assignmentId}`);
    return response.data;
  },

  async submitAssignment(
    assignmentId: string,
    data: { text_content?: string; file?: File }
  ): Promise<AssignmentSubmission> {
    if (data.file) {
      const formData = new FormData();
      if (data.text_content) {
        formData.append('submission_text', data.text_content);
      }
      formData.append('file', data.file);
      const response = await apiClient.post<AssignmentSubmission>(
        `/api/v1/assignments/${assignmentId}/submissions`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } else {
      const response = await apiClient.post<AssignmentSubmission>(
        `/api/v1/assignments/${assignmentId}/submissions`,
        {
          submission_text: data.text_content,
        }
      );
      return response.data;
    }
  },

  async getMySubmission(assignmentId: string): Promise<AssignmentSubmission> {
    const response = await apiClient.get<AssignmentSubmission>(
      `/api/v1/assignments/${assignmentId}/my-submission`
    );
    return response.data;
  },

  // --- Student Timed Quizzes ---
  async startQuizAttempt(quizId: string): Promise<any> {
    const response = await apiClient.post<any>(`/api/v1/quizzes/${quizId}/attempts/start`);
    return response.data;
  },

  async submitQuizAttempt(
    quizId: string,
    attemptId: string,
    answers: Array<{ question_id: string; selected_answer_id?: string }>
  ): Promise<any> {
    const answersPayload = answers.map((a) => ({
      question_id: a.question_id,
      selected_answer_ids: a.selected_answer_id ? [a.selected_answer_id] : [],
    }));
    const response = await apiClient.post<any>(
      `/api/v1/quizzes/${quizId}/attempts/${attemptId}/submit`,
      { answers: answersPayload }
    );
    return response.data;
  },

  // --- Course Completion & Progress ---
  async getCourseCompletion(courseId: string): Promise<CourseCompletionReport> {
    const response = await apiClient.get<CourseCompletionReport>(
      `/api/v1/courses/${courseId}/completion`
    );
    return response.data;
  },

  // --- Instructor Assignment Management ---
  async createAssignment(
    courseId: string,
    payload: {
      title: string;
      description?: string;
      instructions?: string;
      max_score: number;
      due_date?: string;
      allowed_file_types?: string[];
      max_file_size_mb?: number;
      is_published?: boolean;
    }
  ): Promise<Assignment> {
    const response = await apiClient.post<Assignment>(
      `/api/v1/instructor/courses/${courseId}/assignments`,
      {
        course_id: courseId,
        title: payload.title,
        description: payload.description,
        instructions: payload.instructions,
        max_marks: payload.max_score,
        due_date: payload.due_date,
        allowed_file_types: payload.allowed_file_types ? payload.allowed_file_types.join(',') : undefined,
        max_file_size_mb: payload.max_file_size_mb,
      }
    );
    return response.data;
  },

  async getInstructorCourseAssignments(courseId: string): Promise<Assignment[]> {
    const response = await apiClient.get<Assignment[]>(
      `/api/v1/instructor/courses/${courseId}/assignments`
    );
    return response.data;
  },

  async getAssignmentSubmissions(
    assignmentId: string
  ): Promise<AssignmentSubmission[]> {
    const response = await apiClient.get<AssignmentSubmission[]>(
      `/api/v1/instructor/assignments/${assignmentId}/submissions`
    );
    return response.data;
  },

  async getSubmissionDetails(
    submissionId: string
  ): Promise<AssignmentSubmission> {
    const response = await apiClient.get<AssignmentSubmission>(
      `/api/v1/instructor/submissions/${submissionId}`
    );
    return response.data;
  },

  async gradeSubmission(
    submissionId: string,
    payload: { score: number; instructor_feedback?: string }
  ): Promise<AssignmentSubmission> {
    const response = await apiClient.post<AssignmentSubmission>(
      `/api/v1/instructor/submissions/${submissionId}/grade`,
      {
        score: payload.score,
        feedback: payload.instructor_feedback,
      }
    );
    return response.data;
  },
};
