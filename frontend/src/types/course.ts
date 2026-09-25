export type CourseStatus = 'DRAFT' | 'PUBLISHED' | 'ARCHIVED' | 'UNPUBLISHED';
export type CourseLevel = 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'ALL_LEVELS';
export type LessonContentType = 'VIDEO' | 'TEXT' | 'DOCUMENT' | 'QUIZ' | 'IFRAME';

export interface InstructorPublicInfo {
  id: number;
  full_name: string;
  email: string;
}

export interface LessonSummary {
  id: string;
  module_id: string;
  title: string;
  slug: string;
  content_type: LessonContentType;
  order_index: number;
  duration_minutes: number;
  is_preview: boolean;
  is_published: boolean;
  created_at: string;
  updated_at?: string;
}

export interface LessonCreateInput {
  title: string;
  content_type?: LessonContentType;
  content_text?: string;
  content_url?: string;
  duration_minutes?: number;
  is_preview?: boolean;
  is_published?: boolean;
  order_index?: number;
}

export interface LessonUpdateInput {
  title?: string;
  content_type?: LessonContentType;
  content_text?: string;
  content_url?: string;
  duration_minutes?: number;
  is_preview?: boolean;
  is_published?: boolean;
}

export interface ModuleSummary {
  id: string;
  course_id: string;
  title: string;
  slug: string;
  description?: string;
  order_index: number;
  is_published: boolean;
  created_at: string;
  updated_at?: string;
  lessons: LessonSummary[];
}

export interface ModuleCreateInput {
  title: string;
  description?: string;
  order_index?: number;
  is_published?: boolean;
}

export interface ModuleUpdateInput {
  title?: string;
  description?: string;
  is_published?: boolean;
}

export interface Course {
  id: string;
  instructor_id: number;
  title: string;
  slug: string;
  short_description?: string;
  description?: string;
  category?: string;
  level: CourseLevel;
  status: CourseStatus;
  estimated_duration_minutes: number;
  thumbnail_url?: string;
  is_free: boolean;
  price?: number;
  created_at: string;
  updated_at?: string;
  published_at?: string;
  instructor_name?: string;
  module_count: number;
  lesson_count: number;
  total_duration_minutes: number;
}

export interface CourseDetail extends Course {
  instructor?: InstructorPublicInfo;
  modules: ModuleSummary[];
}

export interface CourseCreateInput {
  title: string;
  short_description?: string;
  description?: string;
  category?: string;
  level?: CourseLevel;
  thumbnail_url?: string;
  estimated_duration_minutes?: number;
  is_free?: boolean;
  price?: number;
}

export interface CourseUpdateInput {
  title?: string;
  short_description?: string;
  description?: string;
  category?: string;
  level?: CourseLevel;
  thumbnail_url?: string;
  estimated_duration_minutes?: number;
  is_free?: boolean;
  price?: number;
}

export interface CoursePublishChecklist {
  can_publish: boolean;
  reasons: string[];
  module_count: number;
  lesson_count: number;
  has_valid_title: boolean;
  has_valid_description: boolean;
}

export interface CourseListResponse {
  items: Course[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface CourseFilters {
  search?: string;
  category?: string;
  level?: CourseLevel;
  status?: CourseStatus;
  page?: number;
  page_size?: number;
}
