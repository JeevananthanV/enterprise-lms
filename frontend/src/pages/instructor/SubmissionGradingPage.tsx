import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { assessmentService } from '../../services/assessmentService';
import {
  CheckCircle2,
  AlertCircle,
  Award,
} from 'lucide-react';

export const SubmissionGradingPage: React.FC = () => {
  const { submissionId } = useParams<{ submissionId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [score, setScore] = useState<number>(0);
  const [feedback, setFeedback] = useState<string>('');
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const { data: submission, isLoading, error } = useQuery({
    queryKey: ['instructor-submission', submissionId],
    queryFn: () => assessmentService.getSubmissionDetails(submissionId!),
    enabled: !!submissionId,
  });

  useEffect(() => {
    if (submission) {
      if (submission.score !== null && submission.score !== undefined) {
        setScore(submission.score);
      }
      if (submission.instructor_feedback) {
        setFeedback(submission.instructor_feedback);
      }
    }
  }, [submission]);

  const gradeMutation = useMutation({
    mutationFn: () =>
      assessmentService.gradeSubmission(submissionId!, {
        score: Number(score),
        instructor_feedback: feedback,
      }),
    onSuccess: () => {
      setSaveSuccess(true);
      setErrorMsg('');
      queryClient.invalidateQueries({
        queryKey: ['instructor-submission', submissionId],
      });
    },
    onError: (err: any) => {
      setErrorMsg(err.response?.data?.detail || 'Failed to submit grade.');
      setSaveSuccess(false);
    },
  });

  const handleGradeSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const max = submission?.assignment?.max_score || 100;
    if (score < 0 || score > max) {
      setErrorMsg(`Score must be between 0 and ${max}.`);
      return;
    }
    gradeMutation.mutate();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !submission) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12 text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-gray-900 mb-1">Submission Not Found</h2>
        <p className="text-gray-600 mb-6">
          The requested submission does not exist or you do not have permission to view it.
        </p>
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium"
        >
          &larr; Go Back
        </button>
      </div>
    );
  }

  const maxScore = submission.assignment?.max_score || 100;

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Top Breadcrumb */}
      <div className="mb-6">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-3"
        >
          &larr; Back to Submissions
        </button>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-xs uppercase font-bold tracking-wider text-primary-600">
              Grading Portal
            </span>
            <h1 className="text-2xl font-bold text-gray-900">
              {submission.student?.full_name}'s Submission
            </h1>
            <p className="text-xs text-gray-500 mt-0.5">
              Assignment: {submission.assignment?.title}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span
              className={`px-3 py-1 rounded-full text-xs font-semibold ${
                submission.status === 'GRADED'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}
            >
              {submission.status}
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Student Submission Content */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-base font-semibold text-gray-900 mb-4">Student Response</h2>

            {submission.text_content ? (
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-100 text-gray-800 text-sm whitespace-pre-line leading-relaxed mb-4">
                {submission.text_content}
              </div>
            ) : (
              <p className="text-sm text-gray-400 italic mb-4">No text response provided.</p>
            )}

            {/* File Attachment */}
            {submission.file_url ? (
              <div className="border border-gray-200 rounded-lg p-4 flex items-center justify-between bg-gray-50">
                <div className="flex items-center gap-3">
                  <div>
                    <p className="text-sm font-semibold text-gray-900">
                      {submission.file_name || 'Submission Attachment'}
                    </p>
                    {submission.file_size && (
                      <p className="text-xs text-gray-500">
                        {(submission.file_size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    )}
                  </div>
                </div>
                <a
                  href={submission.file_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center px-3 py-1.5 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 text-xs font-semibold rounded-md shadow-sm transition-colors"
                >
                  View / Download
                </a>
              </div>
            ) : (
              <p className="text-xs text-gray-400">No file attachments included.</p>
            )}
          </div>
        </div>

        {/* Grading Form Panel */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Award className="w-5 h-5 text-primary-600" /> Evaluate & Grade
            </h2>

            {saveSuccess && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>Grade recorded successfully!</span>
              </div>
            )}

            {errorMsg && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <form onSubmit={handleGradeSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                  Score (Out of {maxScore})
                </label>
                <div className="relative">
                  <input
                    type="number"
                    min={0}
                    max={maxScore}
                    value={score}
                    onChange={(e) => setScore(Number(e.target.value))}
                    required
                    className="w-full rounded-lg border-gray-300 text-base font-bold pr-12 text-primary-900"
                  />
                  <span className="absolute right-3 top-2.5 text-xs text-gray-400 font-medium">
                    / {maxScore}
                  </span>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                  Instructor Feedback
                </label>
                <textarea
                  rows={6}
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="Provide constructive feedback, praise, or areas for improvement..."
                  className="w-full rounded-lg border-gray-300 text-sm"
                />
              </div>

              <button
                type="submit"
                disabled={gradeMutation.isPending}
                className="w-full py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-semibold text-sm rounded-lg shadow-sm transition-colors disabled:opacity-50"
              >
                {gradeMutation.isPending ? 'Saving Grade...' : 'Save & Publish Grade'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
