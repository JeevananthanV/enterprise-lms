import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { courseService } from '../../services/courseService';
import { CourseLevel, CourseCreateInput } from '../../types/course';

const CATEGORIES = [
  'Software Engineering',
  'Data Science & AI',
  'Cloud & DevOps',
  'Cybersecurity',
  'Business & Leadership',
  'Product Design',
];

export const CourseCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<CourseCreateInput>({
    title: '',
    short_description: '',
    description: '',
    category: 'Software Engineering',
    level: 'BEGINNER',
    estimated_duration_minutes: 60,
    is_free: true,
    price: 0,
  });

  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const createMutation = useMutation({
    mutationFn: (input: CourseCreateInput) => courseService.createCourse(input),
    onSuccess: (course) => {
      navigate(`/instructor/courses/${course.id}/curriculum`);
    },
    onError: (err: any) => {
      setErrorMsg(err.response?.data?.detail || err.message || 'Failed to create course.');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim()) {
      setErrorMsg('Course title is required.');
      return;
    }
    setErrorMsg(null);
    createMutation.mutate(formData);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <Link
          to="/instructor/courses"
          className="text-xs font-semibold text-gray-500 hover:text-gray-900 dark:hover:text-white"
        >
          ← Back to Courses
        </Link>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Create New Course
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
          Set up your basic course information. You can author modules and lessons in the Curriculum Studio next.
        </p>

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
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g. Distributed Systems Architecture & Microservices"
              className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Short Description / Summary
            </label>
            <input
              type="text"
              value={formData.short_description || ''}
              onChange={(e) => setFormData({ ...formData, short_description: e.target.value })}
              placeholder="A brief 1-2 sentence overview for catalog cards"
              className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Detailed Description & Syllabus Goals
            </label>
            <textarea
              rows={4}
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Comprehensive details on prerequisites, learning outcomes, and technical roadmap..."
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
                Course Pricing
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
            <Link
              to="/instructor/courses"
              className="px-5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-semibold rounded-lg shadow disabled:opacity-50 transition-colors"
            >
              {createMutation.isPending ? 'Creating Course...' : 'Continue to Curriculum Studio →'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CourseCreatePage;
