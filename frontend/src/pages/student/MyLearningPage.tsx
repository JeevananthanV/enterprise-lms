import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { learningService } from '../../services/learningService';
import { EnrollmentItem } from '../../types/learning';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { EmptyState } from '../../components/common/EmptyState';
import { Badge } from '../../components/common/Badge';
import { BookOpen, PlayCircle, Sparkles } from 'lucide-react';

export const MyLearningPage: React.FC = () => {
  const [filter, setFilter] = useState<'ALL' | 'IN_PROGRESS' | 'COMPLETED'>('ALL');

  const { data: enrollments, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['myEnrollments'],
    queryFn: () => learningService.getMyEnrollments(),
  });

  const filteredEnrollments = React.useMemo(() => {
    if (!enrollments) return [];
    if (filter === 'IN_PROGRESS') {
      return enrollments.filter((e) => e.status === 'ACTIVE' && e.progress_percentage < 100);
    }
    if (filter === 'COMPLETED') {
      return enrollments.filter((e) => e.status === 'COMPLETED' || e.progress_percentage >= 100);
    }
    return enrollments;
  }, [enrollments, filter]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Header */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-500/20 border border-primary-400/30 text-primary-300 text-xs font-semibold mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            Active Learning Center
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            My Learning & Enrolled Courses
          </h1>
          <p className="mt-1 text-sm text-slate-300 max-w-2xl">
            Pick up right where you left off. Access interactive course curriculums, lesson modules, and quizzes.
          </p>
        </div>

        <div>
          <Link
            to="/courses"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 hover:bg-primary-500 text-white text-xs font-bold rounded-xl shadow transition-colors"
          >
            <BookOpen className="w-4 h-4" /> Explore Course Catalog
          </Link>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-4">
        <button
          onClick={() => setFilter('ALL')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-colors ${
            filter === 'ALL'
              ? 'bg-primary-600 text-white shadow-sm'
              : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100'
          }`}
        >
          All Courses ({enrollments?.length || 0})
        </button>

        <button
          onClick={() => setFilter('IN_PROGRESS')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-colors ${
            filter === 'IN_PROGRESS'
              ? 'bg-primary-600 text-white shadow-sm'
              : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100'
          }`}
        >
          In Progress ({enrollments?.filter((e) => e.progress_percentage < 100).length || 0})
        </button>

        <button
          onClick={() => setFilter('COMPLETED')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-colors ${
            filter === 'COMPLETED'
              ? 'bg-primary-600 text-white shadow-sm'
              : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100'
          }`}
        >
          Completed ({enrollments?.filter((e) => e.progress_percentage >= 100).length || 0})
        </button>
      </div>

      {/* Main Content Area */}
      {isLoading ? (
        <LoadingState message="Loading your enrolled courses..." />
      ) : isError ? (
        <ErrorState
          title="Could not load learning records"
          message={error instanceof Error ? error.message : 'An error occurred fetching enrollments.'}
          onRetry={() => refetch()}
        />
      ) : filteredEnrollments.length === 0 ? (
        <EmptyState
          title={
            filter === 'COMPLETED'
              ? 'No completed courses yet'
              : filter === 'IN_PROGRESS'
              ? 'No courses currently in progress'
              : 'You have not enrolled in any courses yet'
          }
          description="Browse our enterprise course catalog to find hands-on tracks in Cloud, AI, Security, and Engineering."
          actionText="Browse Course Catalog"
          onAction={() => window.location.assign('/courses')}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredEnrollments.map((enrollment: EnrollmentItem) => (
            <div
              key={enrollment.id}
              className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden flex flex-col justify-between hover:shadow-md transition-shadow"
            >
              <div>
                {/* Course Card Header */}
                <div className="h-36 bg-gradient-to-tr from-primary-700 to-indigo-600 p-4 relative flex flex-col justify-between text-white">
                  <div className="flex justify-between items-start">
                    {enrollment.course.category && (
                      <span className="px-2.5 py-0.5 bg-black/40 backdrop-blur-xs rounded text-[11px] font-medium">
                        {enrollment.course.category}
                      </span>
                    )}
                    <Badge variant={enrollment.progress_percentage >= 100 ? 'success' : 'info'}>
                      {enrollment.progress_percentage >= 100 ? 'Completed' : 'In Progress'}
                    </Badge>
                  </div>

                  <div className="text-xs text-white/90">
                    Instructor: {enrollment.course.instructor_name || 'Enterprise Faculty'}
                  </div>
                </div>

                {/* Body Content */}
                <div className="p-5">
                  <h3 className="text-base font-bold text-slate-900 dark:text-white line-clamp-1 hover:text-primary-600">
                    <Link to={`/student/courses/${enrollment.course_id}/learn`}>
                      {enrollment.course.title}
                    </Link>
                  </h3>

                  <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 line-clamp-2">
                    {enrollment.course.short_description || 'Enterprise training curriculum'}
                  </p>

                  {/* Progress Indicator */}
                  <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700 space-y-2">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className="text-slate-600 dark:text-slate-300">Progress</span>
                      <span className="text-primary-600 dark:text-primary-400">
                        {enrollment.progress_percentage}%
                      </span>
                    </div>

                    <div className="w-full bg-slate-100 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-300 ${
                          enrollment.progress_percentage >= 100 ? 'bg-emerald-500' : 'bg-primary-600'
                        }`}
                        style={{ width: `${enrollment.progress_percentage}%` }}
                      />
                    </div>

                    <div className="flex justify-between items-center text-[11px] text-slate-400 pt-1">
                      <span>
                        {enrollment.completed_lesson_count} / {enrollment.total_lesson_count} lessons
                      </span>
                      <span>
                        Enrolled {new Date(enrollment.enrolled_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <div className="p-5 pt-0">
                <Link
                  to={`/student/courses/${enrollment.course_id}/learn`}
                  className={`w-full py-2.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-2 shadow-sm transition-colors ${
                    enrollment.progress_percentage >= 100
                      ? 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:bg-emerald-950/40 dark:text-emerald-300'
                      : 'bg-primary-600 hover:bg-primary-500 text-white'
                  }`}
                >
                  <PlayCircle className="w-3.5 h-3.5" />
                  {enrollment.progress_percentage >= 100
                    ? 'Review Course'
                    : enrollment.progress_percentage > 0
                    ? 'Continue Learning'
                    : 'Start Course'}
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyLearningPage;
