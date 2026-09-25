import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { courseService } from '../../services/courseService';
import { Course, CourseStatus } from '../../types/course';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { EmptyState } from '../../components/common/EmptyState';
import { Badge } from '../../components/common/Badge';

export const InstructorCoursesPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<CourseStatus | ''>('');
  const [actionError, setActionError] = useState<string | null>(null);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['instructorCourses', { search, status: statusFilter }],
    queryFn: () =>
      courseService.getInstructorCourses({
        search: search || undefined,
        status: statusFilter ? statusFilter : undefined,
      }),
  });

  const publishMutation = useMutation({
    mutationFn: (courseId: string) => courseService.publishCourse(courseId),
    onSuccess: () => {
      setActionError(null);
      queryClient.invalidateQueries({ queryKey: ['instructorCourses'] });
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail || err.message || 'Failed to publish course.';
      setActionError(msg);
    },
  });

  const unpublishMutation = useMutation({
    mutationFn: (courseId: string) => courseService.unpublishCourse(courseId),
    onSuccess: () => {
      setActionError(null);
      queryClient.invalidateQueries({ queryKey: ['instructorCourses'] });
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail || err.message || 'Failed to unpublish course.';
      setActionError(msg);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (courseId: string) => courseService.deleteCourse(courseId),
    onSuccess: () => {
      setActionError(null);
      queryClient.invalidateQueries({ queryKey: ['instructorCourses'] });
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail || err.message || 'Failed to delete course.';
      setActionError(msg);
    },
  });

  const handleDelete = (course: Course) => {
    if (window.confirm(`Are you sure you want to delete "${course.title}"? This cannot be undone.`)) {
      deleteMutation.mutate(course.id);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
            Course Management
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Create, author curriculum modules, preview, and publish your enterprise courses.
          </p>
        </div>
        <div>
          <Link
            to="/instructor/courses/new"
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-semibold rounded-lg shadow transition-colors"
          >
            <span>+</span> Create New Course
          </Link>
        </div>
      </div>

      {actionError && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-300 text-sm flex justify-between items-center">
          <span>{actionError}</span>
          <button onClick={() => setActionError(null)} className="text-red-500 hover:text-red-700">
            ✕
          </button>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 mb-6 shadow-sm flex flex-col sm:flex-row gap-4 justify-between items-center">
        <div className="w-full sm:w-80">
          <input
            type="text"
            placeholder="Search courses..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <span className="text-xs font-semibold text-gray-500">Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as CourseStatus | '')}
            className="px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Statuses</option>
            <option value="DRAFT">Draft</option>
            <option value="PUBLISHED">Published</option>
            <option value="UNPUBLISHED">Unpublished</option>
            <option value="ARCHIVED">Archived</option>
          </select>
        </div>
      </div>

      {/* Courses List */}
      {isLoading ? (
        <LoadingState message="Loading your courses..." />
      ) : isError ? (
        <ErrorState
          title="Failed to load courses"
          message={error instanceof Error ? error.message : 'An error occurred fetching your courses.'}
          onRetry={() => refetch()}
        />
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          title="No courses yet"
          description="Get started by creating your first course, setting up modules, and authoring lessons."
          actionText="Create Course"
          onAction={() => window.location.assign('/instructor/courses/new')}
        />
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700/50 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left">Course Details</th>
                  <th scope="col" className="px-6 py-3 text-left">Level</th>
                  <th scope="col" className="px-6 py-3 text-left">Curriculum</th>
                  <th scope="col" className="px-6 py-3 text-left">Status</th>
                  <th scope="col" className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700 text-sm">
                {data.items.map((course: Course) => (
                  <tr key={course.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-gray-900 dark:text-white">
                        <Link
                          to={`/instructor/courses/${course.id}/curriculum`}
                          className="hover:text-primary-600 transition-colors"
                        >
                          {course.title}
                        </Link>
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-1">
                        {course.short_description || course.description || 'No description'}
                      </div>
                      {course.category && (
                        <span className="inline-block mt-1 text-[11px] font-medium text-primary-600 dark:text-primary-400">
                          {course.category}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                        {course.level}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs text-gray-600 dark:text-gray-400">
                      <div>📚 {course.module_count || 0} Modules</div>
                      <div className="mt-0.5">📖 {course.lesson_count || 0} Lessons</div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge
                        variant={
                          course.status === 'PUBLISHED'
                            ? 'success'
                            : course.status === 'DRAFT'
                            ? 'default'
                            : course.status === 'UNPUBLISHED'
                            ? 'warning'
                            : 'error'
                        }
                      >
                        {course.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <Link
                        to={`/instructor/courses/${course.id}/curriculum`}
                        className="inline-flex items-center px-2.5 py-1.5 bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300 rounded text-xs font-semibold hover:bg-primary-100"
                        title="Edit curriculum & lessons"
                      >
                        Curriculum Studio
                      </Link>

                      <Link
                        to={`/instructor/courses/${course.id}/edit`}
                        className="inline-flex items-center px-2.5 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded text-xs font-medium hover:bg-gray-200"
                        title="Edit course settings"
                      >
                        Edit
                      </Link>

                      <Link
                        to={`/instructor/courses/${course.id}/preview`}
                        className="inline-flex items-center px-2.5 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded text-xs font-medium hover:bg-gray-200"
                        title="Preview student view"
                      >
                        Preview
                      </Link>

                      {course.status === 'PUBLISHED' ? (
                        <button
                          onClick={() => unpublishMutation.mutate(course.id)}
                          disabled={unpublishMutation.isPending}
                          className="inline-flex items-center px-2.5 py-1.5 bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300 rounded text-xs font-medium hover:bg-amber-100 disabled:opacity-50"
                        >
                          Unpublish
                        </button>
                      ) : (
                        <button
                          onClick={() => publishMutation.mutate(course.id)}
                          disabled={publishMutation.isPending}
                          className="inline-flex items-center px-2.5 py-1.5 bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300 rounded text-xs font-semibold hover:bg-green-100 disabled:opacity-50"
                        >
                          Publish
                        </button>
                      )}

                      <button
                        onClick={() => handleDelete(course)}
                        disabled={deleteMutation.isPending}
                        className="inline-flex items-center px-2.5 py-1.5 text-red-600 hover:text-red-800 text-xs font-medium"
                        title="Delete course"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default InstructorCoursesPage;
