import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { certificateService } from '../../services/certificateService';
import {
  Award,
} from 'lucide-react';

export const CertificatePage: React.FC = () => {
  const { courseId, certificateId } = useParams<{
    courseId?: string;
    certificateId?: string;
  }>();

  const { data: certificate, isLoading, error } = useQuery({
    queryKey: ['certificate', courseId || certificateId],
    queryFn: () =>
      courseId
        ? certificateService.getCourseCertificate(courseId)
        : certificateService.getCertificateById(certificateId!),
    enabled: !!(courseId || certificateId),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !certificate) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12 text-center">
        <Award className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Certificate Not Found or Ineligible
        </h2>
        <p className="text-gray-600 mb-6">
          To receive a verified certificate of completion, ensure all required lessons, quizzes, and assignments have been fulfilled.
        </p>
        <Link
          to={courseId ? `/student/courses/${courseId}/learn` : '/student/dashboard'}
          className="inline-flex items-center px-5 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-medium transition-colors"
        >
          &larr; Back to Learning
        </Link>
      </div>
    );
  }

  const handlePrint = () => {
    window.print();
  };

  const handleShare = () => {
    const url = `${window.location.origin}/verify/certificate/${certificate.certificate_number}`;
    navigator.clipboard.writeText(url);
    alert('Verification link copied to clipboard!');
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Top Bar / Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 print:hidden">
        <Link
          to={courseId ? `/student/courses/${courseId}/learn` : '/student/dashboard'}
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
        >
          &larr; Back
        </Link>
        <div className="flex items-center gap-3">
          <button
            onClick={handleShare}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Share Link
          </button>
          <button
            onClick={handlePrint}
            className="inline-flex items-center px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-medium shadow-sm transition-colors"
          >
            Print / Save PDF
          </button>
        </div>
      </div>

      {/* Certificate Frame */}
      <div className="bg-white border-8 border-double border-primary-900 rounded-2xl p-8 sm:p-12 shadow-2xl relative overflow-hidden print:border-4 print:shadow-none print:m-0">
        {/* Decorative corner accents */}
        <div className="absolute top-0 left-0 w-24 h-24 bg-gradient-to-br from-primary-800 to-transparent opacity-10" />
        <div className="absolute bottom-0 right-0 w-24 h-24 bg-gradient-to-tl from-primary-800 to-transparent opacity-10" />

        <div className="text-center space-y-6">
          <div className="flex items-center justify-center">
            <div className="w-20 h-20 bg-primary-50 border-2 border-primary-200 rounded-full flex items-center justify-center">
              <Award className="w-10 h-10 text-primary-700" />
            </div>
          </div>

          <div>
            <span className="text-xs uppercase tracking-widest text-primary-800 font-bold">
              Enterprise Academy • Certificate of Completion
            </span>
            <h1 className="text-3xl sm:text-4xl font-serif font-bold text-gray-900 mt-2">
              Certificate of Achievement
            </h1>
          </div>

          <p className="text-sm text-gray-500 font-sans">
            This is proudly and authoritatively presented to
          </p>

          <div className="py-2 border-b-2 border-gray-300 max-w-md mx-auto">
            <p className="text-2xl sm:text-3xl font-bold text-primary-950 font-serif">
              {certificate.student_name || 'Accomplished Scholar'}
            </p>
          </div>

          <p className="text-sm text-gray-600 max-w-lg mx-auto leading-relaxed">
            for successfully completing all curriculum requirements, objective assessments, and rigorous practical projects in
          </p>

          <div className="py-1">
            <p className="text-xl sm:text-2xl font-bold text-gray-900">
              {certificate.course_title || 'Advanced Enterprise Specialization'}
            </p>
          </div>

          {/* Metadata Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-6 border-t border-gray-200 text-left sm:text-center max-w-2xl mx-auto">
            <div>
              <span className="text-xs text-gray-400 uppercase font-semibold">Issue Date</span>
              <p className="text-sm font-medium text-gray-800 mt-0.5">
                {new Date(certificate.issued_at).toLocaleDateString(undefined, {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
            </div>
            <div>
              <span className="text-xs text-gray-400 uppercase font-semibold">Certificate ID</span>
              <p className="text-sm font-mono font-bold text-primary-800 mt-0.5">
                {certificate.certificate_number}
              </p>
            </div>
            <div>
              <span className="text-xs text-gray-400 uppercase font-semibold">Verification</span>
              <div className="flex items-center justify-start sm:justify-center gap-1 text-green-600 font-semibold text-xs mt-1">
                Cryptographically Verified
              </div>
            </div>
          </div>

          {/* Verification Hash Footer */}
          <div className="pt-4 text-center">
            <p className="text-[10px] font-mono text-gray-400 break-all">
              Verification Hash: {certificate.verification_hash}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
