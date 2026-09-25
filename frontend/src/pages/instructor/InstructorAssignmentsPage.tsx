import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { assessmentService } from '../../services/assessmentService';
import { Assignment } from '../../types/assessment';
import {
  FileText,
  Plus,
  Users,
  ChevronRight,
  AlertCircle,
} from 'lucide-react';

export const InstructorAssignmentsPage: React.FC = () => {
  const { id: courseId } = useParams<{ id: string }>();
  const queryClient = useQueryClient();

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedAssignment, setSelectedAssignment] = useState<Assignment | null>(null);

  // Form State
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [instructions, setInstructions] = useState('');
  const [maxScore, setMaxScore] = useState(100);
  const [dueDate, setDueDate] = useState('');
  const [allowedFileTypes] = useState('pdf,zip');
  const [maxFileSizeMb] = useState(10);
  const [formError, setFormError] = useState('');

  const { data: assignments, isLoading } = useQuery({
    queryKey: ['instructor-assignments', courseId],
    queryFn: () => assessmentService.getInstructorCourseAssignments(courseId!),
    enabled: !!courseId,
  });

  const { data: submissions, isLoading: loadingSubmissions } = useQuery({
    queryKey: ['assignment-submissions', selectedAssignment?.id],
    queryFn: () => assessmentService.getAssignmentSubmissions(selectedAssignment!.id),
    enabled: !!selectedAssignment,
  });

  const createMutation = useMutation({
    mutationFn: () =>
      assessmentService.createAssignment(courseId!, {
        title,
        description,
        instructions,
        max_score: Number(maxScore),
        due_date: dueDate ? new Date(dueDate).toISOString() : undefined,
        allowed_file_types: allowedFileTypes.split(',').map((s) => s.trim()),
        max_file_size_mb: Number(maxFileSizeMb),
        is_published: true,
      }),
    onSuccess: () => {
      setShowCreateModal(false);
      setTitle('');
      setDescription('');
      setInstructions('');
      setFormError('');
      queryClient.invalidateQueries({ queryKey: ['instructor-assignments', courseId] });
    },
    onError: (err: any) => {
      setFormError(err.response?.data?.detail || 'Failed to create assignment.');
    },
  });

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setFormError('Title is required');
      return;
    }
    createMutation.mutate();
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <Link
          to={`/instructor/courses/${courseId}/edit`}
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-3"
        >
          &larr; Back to Course Studio
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Assignments & Submissions</h1>
            <p className="text-sm text-gray-500">
              Create hands-on assignments and grade student submissions.
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors"
          >
            <Plus className="w-4 h-4 mr-2" /> New Assignment
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Assignments List */}
        <div className="lg:col-span-1 space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500 px-1">
            Course Assignments
          </h2>

          {isLoading ? (
            <div className="p-8 text-center text-gray-400">Loading assignments...</div>
          ) : assignments?.length === 0 ? (
            <div className="bg-white rounded-xl p-6 text-center border border-gray-200">
              <FileText className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-600">No assignments created yet.</p>
            </div>
          ) : (
            assignments?.map((item) => {
              const isSelected = selectedAssignment?.id === item.id;
              return (
                <div
                  key={item.id}
                  onClick={() => setSelectedAssignment(item)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-primary-50 border-primary-500 shadow-sm'
                      : 'bg-white border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3
                        className={`font-semibold text-sm ${
                          isSelected ? 'text-primary-900' : 'text-gray-900'
                        }`}
                      >
                        {item.title}
                      </h3>
                      <p className="text-xs text-gray-500 mt-1">
                        Max Score: {item.max_score} pts
                      </p>
                    </div>
                    <ChevronRight
                      className={`w-4 h-4 ${
                        isSelected ? 'text-primary-600' : 'text-gray-400'
                      }`}
                    />
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Submissions Table / View */}
        <div className="lg:col-span-2">
          {selectedAssignment ? (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="p-5 border-b border-gray-200 flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-gray-900">{selectedAssignment.title}</h3>
                  <p className="text-xs text-gray-500 mt-0.5">
                    Viewing all enrolled student submissions
                  </p>
                </div>
                <span className="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded-full font-medium">
                  {submissions?.length || 0} Submissions
                </span>
              </div>

              {loadingSubmissions ? (
                <div className="p-8 text-center text-gray-400">Loading submissions...</div>
              ) : submissions?.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  No submissions received for this assignment yet.
                </div>
              ) : (
                <div className="divide-y divide-gray-100">
                  {submissions?.map((sub) => (
                    <div
                      key={sub.id}
                      className="p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-sm text-gray-900">
                            {sub.student?.full_name || 'Student'}
                          </span>
                          <span className="text-xs text-gray-400">({sub.student?.email})</span>
                        </div>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span>
                            Status:{' '}
                            <span
                              className={`font-semibold ${
                                sub.status === 'GRADED'
                                  ? 'text-green-600'
                                  : sub.status === 'SUBMITTED'
                                  ? 'text-blue-600'
                                  : 'text-yellow-600'
                              }`}
                            >
                              {sub.status}
                            </span>
                          </span>
                          {sub.score !== null && sub.score !== undefined && (
                            <span className="font-medium text-gray-700">
                              Score: {sub.score} / {selectedAssignment.max_score}
                            </span>
                          )}
                          {sub.submitted_at && (
                            <span>{new Date(sub.submitted_at).toLocaleDateString()}</span>
                          )}
                        </div>
                      </div>

                      <Link
                        to={`/instructor/submissions/${sub.id}`}
                        className="inline-flex items-center px-3 py-1.5 bg-primary-50 text-primary-700 hover:bg-primary-100 rounded-lg text-xs font-semibold transition-colors"
                      >
                        {sub.status === 'GRADED' ? 'View / Re-grade' : 'Grade Submission'}
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center text-gray-500">
              <Users className="w-10 h-10 text-gray-300 mx-auto mb-2" />
              Select an assignment on the left to view and grade student submissions.
            </div>
          )}
        </div>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Create New Assignment</h3>

            {formError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{formError}</span>
              </div>
            )}

            <form onSubmit={handleCreateSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                  Title
                </label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Distributed System Architecture Capstone"
                  className="w-full rounded-lg border-gray-300 text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                  Description
                </label>
                <textarea
                  rows={2}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Brief overview of what students will accomplish"
                  className="w-full rounded-lg border-gray-300 text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                  Detailed Instructions
                </label>
                <textarea
                  rows={4}
                  value={instructions}
                  onChange={(e) => setInstructions(e.target.value)}
                  placeholder="Step-by-step instructions or rubric details"
                  className="w-full rounded-lg border-gray-300 text-sm font-mono text-xs"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                    Max Marks / Score
                  </label>
                  <input
                    type="number"
                    min={1}
                    value={maxScore}
                    onChange={(e) => setMaxScore(Number(e.target.value))}
                    className="w-full rounded-lg border-gray-300 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                    Due Date (Optional)
                  </label>
                  <input
                    type="date"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="w-full rounded-lg border-gray-300 text-sm"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="px-5 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-semibold disabled:opacity-50"
                >
                  {createMutation.isPending ? 'Creating...' : 'Create Assignment'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
