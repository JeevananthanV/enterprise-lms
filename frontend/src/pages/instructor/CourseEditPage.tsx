import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { courseService } from '../../services/courseService';
import { CourseLevel, CourseUpdateInput } from '../../types/course';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';

const CATEGORIES = [
  'Software Engineering',
  'Data Science & AI',
  'Cloud & DevOps',
  'Cybersecurity',
  'Business & Leadership',
  'Product Design',
];

export const CourseEditPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [formData, setFormData] = useState<CourseUpdateInput>({
    title: '',
    short_description: '',
    description: '',
    category: '',
    level: 'BEGINNER',
    estimated_duration_minutes: 60,
    is_free: true,
    price: 0,
  });

  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const { data: course, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['instructorCourse', id],
    queryFn: () => courseService.getInstructorCourse(id!),
    enabled: !!id,
  });

  useEffect(() => {
    if (course) {
      setFormData({
        title: course.title,
        short_description: course.short_description || '',
        description: course.description || '',
        category: course.category || 'Software Engineering',
        level: course.level,
        estimated_duration_minutes: course.estimated_duration_minutes,
        is_free: course.is_free,
        price: course.price || 0,
      });
    }
  }, [course]);

  const updateMutation = useMutation({
    mutationFn: (input: CourseUpdateInput) => courseService.updateCourse(id!, input),
    onSuccess: () => {
      setSuccessMsg('Course details updated successfully.');
      setErrorMsg(null);
    },
    onError: (err: any) => {
      setErrorMsg(err.response?.data?.detail || err.message || 'Failed to update course.');
      setSuccessMsg(null);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title?.trim()) {
      setErrorMsg('Course title cannot be empty.');
      return;
    }
    updateMutation.mutate(formData);
  };

  if (isLoading) return <LoadingState message="Loading course settings..." />;
  if (isError || !course) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <ErrorState
          title="Could not load course"
          message={error instanceof Error ? error.message : 'Course not found or access denied.'}
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <Link
          to="/instructor/courses"
          className="text-xs font-semibold text-gray-500 hover:text-gray-900 dark:hover:text-white"
        >
          ← Back to Courses
        </Link>
        <div className="flex gap-2">
          <Link
            to={`/instructor/courses/${id}/curriculum`}
            className="px-3 py-1.5 bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300 rounded text-xs font-semibold hover:bg-primary-100"
          >
            Curriculum Studio →
          </Link>
          <Link
            to={`/instructor/courses/${id}/preview`}
            className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded text-xs font-medium hover:bg-gray-200"
          >
            Preview Course
          </Link>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Edit Course Settings
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
          Update course metadata, descriptions, category, difficulty level, and pricing.
        </p>

        {successMsg && (
          <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-xl text-green-700 dark:text-green-300 text-sm">
            {successMsg}
          </div>
        )}

        {errorMsg && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-300 text-sm">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Course Title *
            </label>
            <input
              type="text"
              required
              minLength={3}
              value={formData.title || ''}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Short Summary
            </label>
            <input
              type="text"
              value={formData.short_description || ''}
              onChange={(e) => setFormData({ ...formData, short_description: e.target.value })}
              className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Full Description & Syllabus
            </label>
            <textarea
              rows={4}
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Category
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Difficulty Level
              </label>
              <select
                value={formData.level}
                onChange={(e) => setFormData({ ...formData, level: e.target.value as CourseLevel })}
                className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
              >
                <option value="BEGINNER">Beginner</option>
                <option value="INTERMEDIATE">Intermediate</option>
                <option value="ADVANCED">Advanced</option>
                <option value="ALL_LEVELS">All Levels</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Estimated Duration (Minutes)
              </label>
              <input
                type="number"
                min={0}
                value={formData.estimated_duration_minutes || 0}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    estimated_duration_minutes: parseInt(e.target.value || '0', 10),
                  })
                }
                className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Pricing
              </label>
              <div className="flex items-center gap-4 mt-2">
                <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                  <input
                    type="checkbox"
                    checked={formData.is_free}
                    onChange={(e) => setFormData({ ...formData, is_free: e.target.checked })}
                    className="rounded text-primary-600 focus:ring-primary-500"
                  />
                  Free Course
                </label>

                {!formData.is_free && (
                  <div className="flex-1">
                    <input
                      type="number"
                      step="0.01"
                      min={0}
                      value={formData.price || 0}
                      onChange={(e) =>
                        setFormData({ ...formData, price: parseFloat(e.target.value || '0') })
                      }
                      placeholder="Price in USD"
                      className="w-full px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 text-sm"
                    />
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-6 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={() => navigate('/instructor/courses')}
              className="px-5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50"
            >
              Done
            </button>
            <button
              type="submit"
              disabled={updateMutation.isPending}
              className="px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-semibold rounded-lg shadow disabled:opacity-50 transition-colors"
            >
              {updateMutation.isPending ? 'Saving Changes...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CourseEditPage;
