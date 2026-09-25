import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { learningService } from '../../services/learningService';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import {
  BookOpen,
  CheckCircle2,
  Award,
  TrendingUp,
  Activity,
  PlayCircle,
} from 'lucide-react';

export const ProgressDashboardPage: React.FC = () => {
  const { data: progress, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['myProgress'],
    queryFn: () => learningService.getMyProgress(),
  });

  if (isLoading) return <LoadingState message="Loading your progress dashboard..." />;
  if (isError || !progress) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <ErrorState
          title="Could not load progress data"
          message={error instanceof Error ? error.message : 'Failed to retrieve progress statistics.'}
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Hero Analytics Header */}
      <div className="bg-gradient-to-r from-slate-900 via-primary-950 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-500/20 border border-primary-400/30 text-primary-300 text-xs font-semibold mb-2">
            <TrendingUp className="w-3.5 h-3.5" />
            Learning Analytics & Completion Tracker
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Learning Progress Dashboard
          </h1>
          <p className="mt-1 text-sm text-slate-300 max-w-2xl">
            Real-time analytics on enrolled courses, completed lesson milestones, and study momentum.
          </p>
        </div>

        <div className="flex items-center gap-4 bg-slate-950/60 p-4 rounded-xl border border-slate-800">
          <div className="text-center">
            <div className="text-2xl font-extrabold text-emerald-400">
              {progress.overall_completion_percentage}%
            </div>
            <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider">
              Overall Completion
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <Card>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase">Enrolled Courses</span>
            <div className="p-2 rounded-lg bg-primary-50 text-primary-600">
              <BookOpen className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">
            {progress.total_enrolled_courses}
          </p>
          <p className="text-xs text-slate-400 mt-1">Total active registrations</p>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase">In Progress</span>
            <div className="p-2 rounded-lg bg-amber-50 text-amber-600">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">
            {progress.in_progress_courses}
          </p>
          <p className="text-xs text-slate-400 mt-1">Ongoing curricula</p>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase">Completed Courses</span>
            <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
              <Award className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">
            {progress.completed_courses}
          </p>
          <p className="text-xs text-slate-400 mt-1">100% completion milestone</p>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase">Lessons Finished</span>
            <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">
            {progress.total_completed_lessons} / {progress.total_lessons_available}
          </p>
          <p className="text-xs text-slate-400 mt-1">Total completed lesson units</p>
        </Card>
      </div>

      {/* Course-by-Course Progress Breakdown */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6">
        <h2 className="text-base font-bold text-slate-900 dark:text-white mb-4">
          Course-by-Course Progress
        </h2>

        {progress.courses.length === 0 ? (
          <p className="text-xs text-slate-500 italic py-4">No enrolled courses to track yet.</p>
        ) : (
          <div className="space-y-4">
            {progress.courses.map((c) => (
              <div
                key={c.course_id}
                className="p-4 rounded-xl border border-slate-100 dark:border-slate-700/60 bg-slate-50/50 dark:bg-slate-800/40 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold text-sm text-slate-900 dark:text-white">
                      {c.course_title}
                    </h3>
                    <Badge variant={c.progress_percentage >= 100 ? 'success' : 'info'}>
                      {c.progress_percentage >= 100 ? 'Completed' : 'In Progress'}
                    </Badge>
                  </div>

                  <div className="mt-2 w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden max-w-md">
                    <div
                      className={`h-full rounded-full transition-all duration-300 ${
                        c.progress_percentage >= 100 ? 'bg-emerald-500' : 'bg-primary-600'
                      }`}
                      style={{ width: `${c.progress_percentage}%` }}
                    />
                  </div>

                  <div className="mt-1 flex items-center gap-4 text-xs text-slate-400">
                    <span>
                      {c.completed_lessons} of {c.total_lessons} lessons completed
                    </span>
                    <span>•</span>
                    <span>{c.progress_percentage}% Complete</span>
                  </div>
                </div>

                <Link
                  to={`/student/courses/${c.course_id}/learn`}
                  className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-xs font-semibold rounded-xl flex items-center gap-1.5 self-start sm:self-center shadow-sm"
                >
                  <PlayCircle className="w-3.5 h-3.5" /> Continue
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent Activity Stream */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6">
        <h2 className="text-base font-bold text-slate-900 dark:text-white mb-4">
          Recent Learning Activity
        </h2>

        {progress.recent_activity.length === 0 ? (
          <p className="text-xs text-slate-500 italic py-4">No recent lesson activity recorded.</p>
        ) : (
          <div className="divide-y divide-slate-100 dark:divide-slate-700">
            {progress.recent_activity.map((act, i) => (
              <div key={i} className="py-3 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2.5">
                  <CheckCircle2
                    className={`w-4 h-4 ${
                      act.is_completed ? 'text-emerald-500' : 'text-slate-400'
                    }`}
                  />
                  <div>
                    <p className="font-semibold text-slate-800 dark:text-slate-200">
                      {act.lesson_title}
                    </p>
                    <p className="text-[11px] text-slate-400">
                      Status: {act.is_completed ? 'Completed' : 'Viewed'}
                    </p>
                  </div>
                </div>
                <div className="text-[11px] text-slate-400">
                  {new Date(act.last_accessed_at).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressDashboardPage;
