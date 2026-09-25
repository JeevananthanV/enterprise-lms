export type ContentTypeEnum =
  | 'TEXT'
  | 'RICH_TEXT'
  | 'VIDEO'
  | 'PDF'
  | 'TRANSCRIPT'
  | 'EXTERNAL_RESOURCE';

export interface VideoMetadata {
  video_url: string;
  duration_seconds?: number;
  resolution?: string;
  provider?: string;
  captions_url?: string | null;
  thumbnail_url?: string | null;
}

export interface PdfMetadata {
  file_url: string;
  file_name: string;
  file_size_bytes?: number | null;
  page_count?: number | null;
  downloadable: boolean;
}

export interface TranscriptData {
  language: string;
  content: string;
  format: string;
}

export interface ExternalResource {
  title: string;
  url: string;
  resource_type: string;
  description?: string | null;
}

export interface LessonContent {
  id: string;
  lesson_id: string;
  course_id?: string | null;
  content_type: ContentTypeEnum;
  body?: string | null;
  video_metadata?: VideoMetadata | null;
  pdf_metadata?: PdfMetadata | null;
  transcript?: TranscriptData | null;
  external_resources: ExternalResource[];
  custom_properties: Record<string, any>;
  version: number;
  is_published: boolean;
  published_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface LessonContentCreateInput {
  content_type: ContentTypeEnum;
  body?: string | null;
  video_metadata?: VideoMetadata | null;
  pdf_metadata?: PdfMetadata | null;
  transcript?: TranscriptData | null;
  external_resources?: ExternalResource[];
  custom_properties?: Record<string, any>;
}

export interface LessonContentUpdateInput {
  content_type?: ContentTypeEnum;
  body?: string | null;
  video_metadata?: VideoMetadata | null;
  pdf_metadata?: PdfMetadata | null;
  transcript?: TranscriptData | null;
  external_resources?: ExternalResource[];
  custom_properties?: Record<string, any>;
}
