import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { assessmentService } from '../../services/assessmentService';
import {
  FileText,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';

export const AssignmentSubmissionPage: React.FC = () => {
  const { courseId, assignmentId } = useParams<{ courseId: string; assignmentId: string }>();
  const queryClient = useQueryClient();
  const [textContent, setTextContent] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const { data: assignment, isLoading: loadingAssignment } = useQuery({
    queryKey: ['assignment', assignmentId],
    queryFn: () => assessmentService.getAssignmentDetails(assignmentId!),
    enabled: !!assignmentId,
  });

  const { data: mySubmission, isLoading: loadingSubmission } = useQuery({
    queryKey: ['my-submission', assignmentId],
    queryFn: () => assessmentService.getMySubmission(assignmentId!),
    enabled: !!assignmentId,
  });

  useEffect(() => {
    if (mySubmission?.text_content) {
      setTextContent(mySubmission.text_content);
    }
  }, [mySubmission]);

  const submitMutation = useMutation({
    mutationFn: () =>
      assessmentService.submitAssignment(assignmentId!, {
        text_content: textContent,
        file: selectedFile || undefined,
      }),
    onSuccess: () => {
      setSuccessMessage('Assignment submitted successfully!');
      setErrorMessage('');
      queryClient.invalidateQueries({ queryKey: ['my-submission', assignmentId] });
      queryClient.invalidateQueries({ queryKey: ['course-completion', courseId] });
    },
    onError: (err: any) => {
      setErrorMessage(
        err.response?.data?.detail || 'Failed to submit assignment. Please try again.'
      );
      setSuccessMessage('');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!textContent.trim() && !selectedFile && !mySubmission?.file_url) {
      setErrorMessage('Please provide either text content or upload a file.');
      return;
    }
    submitMutation.mutate();
  };

  if (loadingAssignment || loadingSubmission) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!assignment) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Assignment not found.</p>
        <Link
          to={`/student/courses/${courseId}/learn`}
          className="mt-4 inline-flex items-center text-primary-600 hover:text-primary-700 font-medium"
        >
          &larr; Back to Course
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header / Breadcrumbs */}
      <div className="mb-6">
        <Link
          to={`/student/courses/${courseId}/learn`}
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-3"
        >
          &larr; Back to Course
        </Link>
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mb-2">
              Assignment
            </span>
            <h1 className="text-2xl font-bold text-gray-900">{assignment.title}</h1>
          </div>
          <div className="flex items-center gap-3 text-sm text-gray-600">
            <span className="font-medium bg-gray-100 px-3 py-1.5 rounded-lg border border-gray-200">
              Max Score: {assignment.max_score} pts
            </span>
            {assignment.due_date && (
              <span className="text-gray-500">
                Due: {new Date(assignment.due_date).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Instructions */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">Instructions</h2>
            {assignment.description && (
              <p className="text-gray-700 mb-4">{assignment.description}</p>
            )}
            {assignment.instructions && (
              <div className="prose max-w-none text-gray-700 bg-gray-50 p-4 rounded-lg border border-gray-100">
                <p className="whitespace-pre-line">{assignment.instructions}</p>
              </div>
            )}
          </div>

          {/* Submission Form */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Your Submission</h2>

            {successMessage && (
              <div className="mb-4 p-4 rounded-lg bg-green-50 border border-green-200 text-green-700 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0" />
                <span>{successMessage}</span>
              </div>
            )}

            {errorMessage && (
              <div className="mb-4 p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Text Answer / Explanation
                </label>
                <textarea
                  rows={5}
                  value={textContent}
                  onChange={(e) => setTextContent(e.target.value)}
                  placeholder="Type your submission content or response here..."
                  className="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  File Attachment (Optional)
                </label>
                <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-primary-400 transition-colors">
                  <div className="space-y-1 text-center">
                    <div className="flex text-sm text-gray-600 justify-center">
                      <label className="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500">
                        <span>Upload a file</span>
                        <input
                          type="file"
                          className="sr-only"
                          onChange={(e) => {
                            if (e.target.files && e.target.files[0]) {
                              setSelectedFile(e.target.files[0]);
                            }
                          }}
                        />
                      </label>
                      <p className="pl-1">or drag and drop</p>
                    </div>
                    <p className="text-xs text-gray-500">
                      Max {assignment.max_file_size_mb || 10}MB (PDF, DOCX, ZIP, TXT)
                    </p>
                    {selectedFile && (
                      <p className="text-sm font-semibold text-primary-700 mt-2">
                        Selected: {selectedFile.name} (
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                      </p>
                    )}
                  </div>
                </div>
              </div>

              <div className="pt-2 flex items-center justify-end gap-3">
                <button
                  type="submit"
                  disabled={submitMutation.isPending}
                  className="inline-flex items-center px-5 py-2.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg shadow-sm transition-colors disabled:opacity-50"
                >
                  {submitMutation.isPending
                    ? 'Submitting...'
                    : mySubmission
                    ? 'Resubmit Assignment'
                    : 'Submit Assignment'}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Status & Feedback Panel */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-base font-semibold text-gray-900 mb-4">Submission Status</h3>

            {mySubmission ? (
              <div className="space-y-4">
                <div>
                  <span className="text-xs font-medium text-gray-500 uppercase">Status</span>
                  <div className="mt-1">
                    <span
                      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${
                        mySubmission.status === 'GRADED'
                          ? 'bg-green-100 text-green-800'
                          : mySubmission.status === 'SUBMITTED'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {mySubmission.status}
                    </span>
                  </div>
                </div>

                {mySubmission.submitted_at && (
                  <div>
                    <span className="text-xs font-medium text-gray-500 uppercase">Submitted On</span>
                    <p className="text-sm text-gray-700">
                      {new Date(mySubmission.submitted_at).toLocaleString()}
                    </p>
                  </div>
                )}

                {mySubmission.file_name && (
                  <div>
                    <span className="text-xs font-medium text-gray-500 uppercase">Uploaded File</span>
                    <div className="flex items-center gap-2 mt-1 text-sm text-gray-700">
                      <span className="truncate">{mySubmission.file_name}</span>
                    </div>
                  </div>
                )}

                {mySubmission.status === 'GRADED' && (
                  <div className="border-t border-gray-200 pt-4 mt-4 space-y-3">
                    <div>
                      <span className="text-xs font-medium text-gray-500 uppercase">Grade</span>
                      <p className="text-2xl font-bold text-gray-900 mt-1">
                        {mySubmission.score}{' '}
                        <span className="text-sm font-normal text-gray-500">
                          / {assignment.max_score} pts
                        </span>
                      </p>
                    </div>

                    {mySubmission.instructor_feedback && (
                      <div>
                        <span className="text-xs font-medium text-gray-500 uppercase">
                          Instructor Feedback
                        </span>
                        <div className="mt-1 p-3 bg-gray-50 rounded-lg border border-gray-100 text-sm text-gray-700">
                          {mySubmission.instructor_feedback}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-6 text-gray-500 text-sm">
                <FileText className="w-8 h-8 mx-auto text-gray-300 mb-2" />
                Not submitted yet.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
