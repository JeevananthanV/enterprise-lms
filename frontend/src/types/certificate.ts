export interface Certificate {
  id: string;
  certificate_number: string;
  enrollment_id: string;
  student_id: number;
  student_name: string;
  course_id: string;
  course_title: string;
  instructor_name: string;
  issued_at: string;
  completion_date: string;
  verification_hash: string;
  pdf_url?: string;
}

export interface CertificateVerification {
  is_valid: boolean;
  certificate_number: string;
  student_name: string;
  course_title: string;
  issued_at: string;
  completion_date: string;
  verification_hash: string;
  verification_url?: string;
}
