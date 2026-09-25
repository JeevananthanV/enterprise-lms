import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../context/AuthContext';
import { courseService } from '../../services/courseService';
import { learningService } from '../../services/learningService';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { Badge } from '../../components/common/Badge';

export const CourseDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user, isAuthenticated } = useAuth();

  const [openModules, setOpenModules] = useState<Record<string, boolean>>({});
  const [enrollError, setEnrollError] = useState<string | null>(null);

  const { data: course, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['publicCourse', id],
    queryFn: () => courseService.getPublicCourseById(id!),
    enabled: !!id,
  });

  // Check student enrollments if logged in
  const { data: myEnrollments } = useQuery({
    queryKey: ['myEnrollments'],
    queryFn: () => learningService.getMyEnrollments(),
    enabled: isAuthenticated && user?.role === 'STUDENT',
  });

  const isEnrolled = myEnrollments?.some((e) => e.course_id === id);

  const enrollMutation = useMutation({
    mutationFn: () => learningService.enrollCourse(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myEnrollments'] });
      queryClient.invalidateQueries({ queryKey: ['myProgress'] });
      navigate(`/student/courses/${id}/learn`);
    },
    onError: (err: any) => {
      setEnrollError(err.response?.data?.detail || err.message || 'Failed to enroll in course.');
    },
  });

  const handleEnrollOrResume = () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    if (isEnrolled) {
      navigate(`/student/courses/${id}/learn`);
      return;
    }
    enrollMutation.mutate();
  };

  const toggleModule = (moduleId: string) => {
    setOpenModules((prev) => ({
      ...prev,
      [moduleId]: !prev[moduleId],
    }));
  };

  if (isLoading) {
    return <LoadingState message="Loading course syllabus and overview..." />;
  }

  if (isError || !course) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <ErrorState
          title="Course Not Found"
          message={error instanceof Error ? error.message : 'Unable to find or load the requested course.'}
          onRetry={() => refetch()}
        />
        <div className="text-center mt-6">
          <Link
            to="/courses"
            className="text-primary-600 hover:text-primary-500 font-medium text-sm"
          >
            ← Back to Course Catalog
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-16">
      {/* Hero Header */}
      <div className="bg-slate-900 text-white border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <div className="mb-4">
            <Link
              to="/courses"
              className="inline-flex items-center text-xs font-medium text-gray-400 hover:text-white transition-colors"
            >
              ← Back to Catalog
            </Link>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <div className="flex flex-wrap items-center gap-2 mb-3">
                {course.category && (
                  <span className="px-3 py-1 bg-primary-600/30 border border-primary-500/40 text-primary-300 rounded-full text-xs font-medium">
                    {course.category}
                  </span>
                )}
                <Badge
                  variant={
                    course.level === 'BEGINNER'
                      ? 'success'
                      : course.level === 'INTERMEDIATE'
                      ? 'warning'
                      : 'error'
                  }
                >
                  {course.level}
                </Badge>
                <span className="text-xs text-gray-400">
                  Updated {new Date(course.updated_at || course.created_at).toLocaleDateString()}
                </span>
              </div>

              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                {course.title}
              </h1>

              <p className="mt-4 text-base text-gray-300 leading-relaxed">
                {course.short_description || course.description}
              </p>

              <div className="mt-6 flex flex-wrap items-center gap-6 text-sm text-gray-300">
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">👨‍🏫 Instructor:</span>
                  <span className="font-semibold text-white">
                    {course.instructor?.full_name || course.instructor_name || 'Enterprise Faculty'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">📚 Modules:</span>
                  <span className="font-semibold text-white">{course.module_count || course.modules.length}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">📖 Lessons:</span>
                  <span className="font-semibold text-white">{course.lesson_count}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">⏱️ Est. Duration:</span>
                  <span className="font-semibold text-white">
                    {course.total_duration_minutes || course.estimated_duration_minutes || 0} mins
                  </span>
                </div>
              </div>
            </div>

            {/* Course Card Summary Box */}
            <div className="lg:col-span-1">
              <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 shadow-xl">
                <div className="h-44 bg-gradient-to-tr from-primary-700 to-indigo-600 rounded-xl flex items-center justify-center text-4xl shadow-inner mb-6">
                  🎓
                </div>

                <div className="text-2xl font-bold text-white mb-2">
                  {course.is_free ? 'Free Enrollment' : `$${course.price?.toFixed(2) || '0.00'}`}
                </div>
                <p className="text-xs text-gray-400 mb-6">
                  Full lifetime access to comprehensive curriculum, lessons, and exercises.
                </p>

                {enrollError && (
                  <div className="mb-4 p-3 bg-red-900/40 border border-red-700 rounded-lg text-red-200 text-xs">
                    {enrollError}
                  </div>
                )}

                <button
                  type="button"
                  onClick={handleEnrollOrResume}
                  disabled={enrollMutation.isPending}
                  className={`w-full py-3 px-4 text-white font-bold rounded-xl shadow-lg transition-colors text-sm ${
                    isEnrolled
                      ? 'bg-emerald-600 hover:bg-emerald-500'
                      : 'bg-primary-500 hover:bg-primary-400'
                  }`}
                >
                  {enrollMutation.isPending
                    ? 'Processing Enrollment...'
                    : isEnrolled
                    ? '▶ Resume Course in Player'
                    : 'Enroll in Course Now'}
                </button>

                <div className="mt-4 text-center">
                  <span className="text-xs text-gray-400">Enterprise Verified Certificate Track</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Course Details Content & Curriculum */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            {/* Description */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                Course Description
              </h2>
              <div className="prose dark:prose-invert max-w-none text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                {course.description || 'No detailed syllabus description provided yet.'}
              </div>
            </div>

            {/* Curriculum Breakdown */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                    Curriculum & Modules
                  </h2>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {course.modules.length} modules • {course.lesson_count} lessons total
                  </p>
                </div>
              </div>

              {course.modules.length === 0 ? (
                <p className="text-sm text-gray-500 italic">No public modules available for this course yet.</p>
              ) : (
                <div className="space-y-3">
                  {course.modules.map((module, idx) => {
                    const isOpen = openModules[module.id] ?? true;
                    return (
                      <div
                        key={module.id}
                        className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden"
                      >
                        <button
                          type="button"
                          onClick={() => toggleModule(module.id)}
                          className="w-full flex justify-between items-center px-5 py-4 bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 text-left transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/50 text-primary-700 dark:text-primary-300 text-xs font-bold flex items-center justify-center">
                              {idx + 1}
                            </span>
                            <div>
                              <h3 className="font-semibold text-sm text-gray-900 dark:text-white">
                                {module.title}
                              </h3>
                              {module.description && (
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-1">
                                  {module.description}
                                </p>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                            <span>{module.lessons?.length || 0} lessons</span>
                            <span>{isOpen ? '▲' : '▼'}</span>
                          </div>
                        </button>

                        {isOpen && module.lessons && module.lessons.length > 0 && (
                          <div className="divide-y divide-gray-100 dark:divide-gray-700/60 bg-white dark:bg-gray-800">
                            {module.lessons.map((lesson, lIdx) => (
                              <div
                                key={lesson.id}
                                className="px-5 py-3 flex items-center justify-between text-xs hover:bg-gray-50/50 dark:hover:bg-gray-700/20"
                              >
                                <div className="flex items-center gap-3">
                                  <span className="text-gray-400">{lIdx + 1}.</span>
                                  <span className="font-medium text-gray-800 dark:text-gray-200">
                                    {lesson.title}
                                  </span>
                                  {lesson.is_preview && (
                                    <span className="px-2 py-0.5 bg-blue-50 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300 rounded text-[10px] font-semibold">
                                      Preview Available
                                    </span>
                                  )}
                                </div>
                                <div className="flex items-center gap-3 text-gray-400">
                                  <span>{lesson.content_type}</span>
                                  <span>{lesson.duration_minutes || 0}m</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Instructor Sidebar Bio */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
              <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-4">
                Instructor Profile
              </h3>
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-full bg-primary-600 text-white font-bold flex items-center justify-center text-lg">
                  {course.instructor?.full_name?.charAt(0) || 'I'}
                </div>
                <div>
                  <h4 className="text-base font-bold text-gray-900 dark:text-white">
                    {course.instructor?.full_name || course.instructor_name || 'Enterprise Faculty'}
                  </h4>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {course.instructor?.email || 'Verified Instructor'}
                  </p>
                </div>
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
                Senior engineering specialist and domain instructor delivering enterprise-grade learning tracks.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseDetailsPage;
