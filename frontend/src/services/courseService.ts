import { apiClient } from './apiClient';
import {
  Course,
  CourseDetail,
  CourseCreateInput,
  CourseUpdateInput,
  CoursePublishChecklist,
  CourseListResponse,
  CourseFilters,
  ModuleSummary,
  ModuleCreateInput,
  ModuleUpdateInput,
  LessonSummary,
  LessonCreateInput,
  LessonUpdateInput,
} from '../types/course';

export const courseService = {
  // ============================================================================
  // Public & Student Course Endpoints
  // ============================================================================

  // List published courses with filters & pagination
  async getPublicCourses(params?: CourseFilters): Promise<CourseListResponse> {
    const res = await apiClient.get<CourseListResponse>('/api/v1/courses', { params });
    const data = res.data as any;
    if (Array.isArray(data)) {
      return {
        items: data,
        total: data.length,
        page: 1,
        page_size: data.length,
        pages: 1,
      };
    }
    return res.data;
  },

  // Get public course details by ID
  async getPublicCourseById(courseId: string): Promise<CourseDetail> {
    const res = await apiClient.get<CourseDetail>(`/api/v1/courses/${courseId}`);
    return res.data;
  },

  // Get published curriculum of a course
  async getCourseCurriculum(courseId: string): Promise<ModuleSummary[]> {
    const res = await apiClient.get<ModuleSummary[]>(`/api/v1/courses/${courseId}/curriculum`);
    return res.data;
  },

  // ============================================================================
  // Instructor Course Management Endpoints
  // ============================================================================

  // List courses authored by the current instructor
  async getInstructorCourses(params?: {
    search?: string;
    status?: string;
    skip?: number;
    limit?: number;
    page_size?: number;
  }): Promise<CourseListResponse> {
    const res = await apiClient.get<any>('/api/v1/instructor/courses', { params });
    const data = res.data;
    if (Array.isArray(data)) {
      let filtered = data;
      if (params?.search) {
        const q = params.search.toLowerCase();
        filtered = filtered.filter(
          (c: Course) =>
            c.title?.toLowerCase().includes(q) ||
            c.short_description?.toLowerCase().includes(q) ||
            c.description?.toLowerCase().includes(q)
        );
      }
      if (params?.status) {
        filtered = filtered.filter((c: Course) => c.status === params.status);
      }
      return {
        items: filtered,
        total: filtered.length,
        page: 1,
        page_size: params?.page_size || filtered.length,
        pages: 1,
      };
    }
    return data;
  },

  // Get instructor course details
  async getInstructorCourse(courseId: string): Promise<CourseDetail> {
    const res = await apiClient.get<CourseDetail>(`/api/v1/instructor/courses/${courseId}`);
    return res.data;
  },

  // Create a new course in DRAFT mode
  async createCourse(input: CourseCreateInput): Promise<Course> {
    const res = await apiClient.post<Course>('/api/v1/instructor/courses', input);
    return res.data;
  },

  // Update course metadata
  async updateCourse(courseId: string, input: CourseUpdateInput): Promise<Course> {
    const res = await apiClient.put<Course>(`/api/v1/instructor/courses/${courseId}`, input);
    return res.data;
  },

  // Delete course
  async deleteCourse(courseId: string): Promise<void> {
    await apiClient.delete(`/api/v1/instructor/courses/${courseId}`);
  },

  // Get publish readiness checklist
  async getPublishChecklist(courseId: string): Promise<CoursePublishChecklist> {
    const res = await apiClient.get<CoursePublishChecklist>(
      `/api/v1/instructor/courses/${courseId}/publish-checklist`
    );
    return res.data;
  },

  // Publish course to catalog
  async publishCourse(courseId: string): Promise<Course> {
    const res = await apiClient.post<Course>(`/api/v1/instructor/courses/${courseId}/publish`);
    return res.data;
  },

  // Unpublish course from catalog
  async unpublishCourse(courseId: string): Promise<Course> {
    const res = await apiClient.post<Course>(`/api/v1/instructor/courses/${courseId}/unpublish`);
    return res.data;
  },

  // Preview course as a student
  async previewCourse(courseId: string): Promise<CourseDetail> {
    const res = await apiClient.get<CourseDetail>(`/api/v1/instructor/courses/${courseId}/preview`);
    return res.data;
  },

  // ============================================================================
  // Module Management Endpoints
  // ============================================================================

  // Create a new module inside a course
  async createModule(courseId: string, input: ModuleCreateInput): Promise<ModuleSummary> {
    const res = await apiClient.post<ModuleSummary>(`/api/v1/instructor/courses/${courseId}/modules`, input);
    return res.data;
  },

  // List all modules in a course
  async listModules(courseId: string): Promise<ModuleSummary[]> {
    const res = await apiClient.get<ModuleSummary[]>(`/api/v1/instructor/courses/${courseId}/modules`);
    return res.data;
  },

  // Update module
  async updateModule(
    moduleId: string,
    input: ModuleUpdateInput | { title: string; description?: string }
  ): Promise<ModuleSummary> {
    const res = await apiClient.patch<ModuleSummary>(`/api/v1/instructor/modules/${moduleId}`, input);
    return res.data;
  },

  // Delete module
  async deleteModule(moduleId: string): Promise<void> {
    await apiClient.delete(`/api/v1/instructor/modules/${moduleId}`);
  },

  // Reorder modules in a course
  async reorderModules(courseId: string, moduleIds: string[]): Promise<ModuleSummary[]> {
    const res = await apiClient.post<ModuleSummary[]>(`/api/v1/instructor/courses/${courseId}/modules/reorder`, {
      module_ids: moduleIds,
    });
    return res.data;
  },

  // ============================================================================
  // Lesson Management Endpoints
  // ============================================================================

  // Create a new lesson inside a module
  async createLesson(moduleId: string, input: LessonCreateInput): Promise<LessonSummary> {
    const res = await apiClient.post<LessonSummary>(`/api/v1/instructor/modules/${moduleId}/lessons`, input);
    return res.data;
  },

  // List all lessons in a module
  async listLessons(moduleId: string): Promise<LessonSummary[]> {
    const res = await apiClient.get<LessonSummary[]>(`/api/v1/instructor/modules/${moduleId}/lessons`);
    return res.data;
  },

  // Get single lesson details
  async getLesson(lessonId: string): Promise<LessonSummary> {
    const res = await apiClient.get<LessonSummary>(`/api/v1/instructor/lessons/${lessonId}`);
    return res.data;
  },

  // Update lesson
  async updateLesson(lessonId: string, input: LessonUpdateInput | any): Promise<LessonSummary> {
    const res = await apiClient.patch<LessonSummary>(`/api/v1/instructor/lessons/${lessonId}`, input);
    return res.data;
  },

  // Delete lesson
  async deleteLesson(lessonId: string): Promise<void> {
    await apiClient.delete(`/api/v1/instructor/lessons/${lessonId}`);
  },

  // Reorder lessons in a module
  async reorderLessons(moduleId: string, lessonIds: string[]): Promise<LessonSummary[]> {
    const res = await apiClient.post<LessonSummary[]>(`/api/v1/instructor/modules/${moduleId}/lessons/reorder`, {
      lesson_ids: lessonIds,
    });
    return res.data;
  },
};