import { apiClient } from './apiClient';
import {
  LessonContent,
  LessonContentCreateInput,
  LessonContentUpdateInput,
} from '../types/content';

export const contentService = {
  async getLessonContent(lessonId: string): Promise<LessonContent> {
    const response = await apiClient.get<LessonContent>(`/api/v1/lessons/${lessonId}/content`);
    return response.data;
  },

  async createLessonContent(
    lessonId: string,
    data: LessonContentCreateInput
  ): Promise<LessonContent> {
    const response = await apiClient.post<LessonContent>(
      `/api/v1/lessons/${lessonId}/content`,
      data
    );
    return response.data;
  },

  async updateLessonContent(
    lessonId: string,
    data: LessonContentUpdateInput
  ): Promise<LessonContent> {
    const response = await apiClient.put<LessonContent>(
      `/api/v1/lessons/${lessonId}/content`,
      data
    );
    return response.data;
  },

  async publishLessonContent(lessonId: string): Promise<LessonContent> {
    const response = await apiClient.post<LessonContent>(
      `/api/v1/lessons/${lessonId}/content/publish`
    );
    return response.data;
  },

  async unpublishLessonContent(lessonId: string): Promise<LessonContent> {
    const response = await apiClient.post<LessonContent>(
      `/api/v1/lessons/${lessonId}/content/unpublish`
    );
    return response.data;
  },
};

export default contentService;
