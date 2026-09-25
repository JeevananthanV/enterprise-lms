import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { learningService } from '../../services/learningService';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import {
  BookOpen,
  CheckCircle2,
  PlayCircle,
  Award,
  Sparkles,
  TrendingUp,
  ChevronRight,
} from 'lucide-react';
import { apiClient } from '../../services/apiClient';

export const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const [probeResult, setProbeResult] = useState<string | null>(null);

  const { data: enrollments } = useQuery({
    queryKey: ['myEnrollments'],
    queryFn: () => learningService.getMyEnrollments(),
  });

  const { data: progressData } = useQuery({
    queryKey: ['myProgress'],
    queryFn: () => learningService.getMyProgress(),
  });

  const testStudentEndpoint = async () => {
    try {
      const res = await apiClient.get('/api/v1/users/student-only');
      setProbeResult(`Success (200): ${JSON.stringify(res.data)}`);
    } catch (err: any) {
      setProbeResult(`Error (${err.status}): ${err.message}`);
    }
  };

  const testAdminEndpointAsStudent = async () => {
    try {
      const res = await apiClient.get('/api/v1/users/admin-only');
      setProbeResult(
        `Unexpected Success (200): ${JSON.stringify(res.data)}`
      );
    } catch (err: any) {
      setProbeResult(`Expected Denied (${err.status}): ${err.message}`);
    }
  };

  // Normalize enrollment API response into an array
  const rawEnrollments: any = enrollments;

  const enrollmentList: any[] = Array.isArray(rawEnrollments)
    ? rawEnrollments
    : Array.isArray(rawEnrollments?.items)
      ? rawEnrollments.items
      : Array.isArray(rawEnrollments?.data)
        ? rawEnrollments.data
        : [];

  // Find most recently accessed or active course to resume
  const continueCourse =
    enrollmentList.length > 0
      ? enrollmentList.find(
          (e: any) => Number(e?.progress_percentage || 0) < 100
        ) || enrollmentList[0]
      : null;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Student Welcome Hero */}
      <div className="bg-gradient-to-r from-sky-900 via-indigo-950 to-slate-900 text-white p-6 sm:p-8 rounded-2xl shadow-md flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-sky-500/20 border border-sky-400/30 text-sky-300 text-xs font-semibold mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            Phase 5 Student Learning Hub Active
          </div>

          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
            Welcome back, {user?.full_name || 'Learner'}!
          </h1>

          <p className="text-sm text-sky-200 mt-1 max-w-2xl">
            Account Role:{' '}
            <span className="font-semibold text-white">STUDENT</span>{' '}
            ({user?.email}). Track your progress, launch immersive lesson
            players, and take interactive quizzes.
          </p>
        </div>

        <div className="flex gap-3">
          <Link
            to="/courses"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-bold rounded-xl shadow transition-colors"
          >
            <BookOpen className="w-4 h-4" />
            Browse Catalog
          </Link>

          <Link
            to="/student/my-learning"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-xl border border-sky-500/30 transition-colors"
          >
            My Learning
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <Card>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase">
              Enrolled Courses
            </span>

            <div className="p-2 rounded-lg bg-sky-50 text-sky-600">
              <BookOpen className="w-4 h-4" />
            </div>
          </div>

          <p className="text-2xl font-bold text-slate-900 mt-2">
            {enrollmentList.length}
          </p>

          <p className="text-xs text-slate-400 mt-1">
            {progressData?.in_progress_courses || 0} In Progress
          </p>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase">
              Completed Lessons
            </span>

            <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>

          <p className="text-2xl font-bold text-slate-900 mt-2">
            {progressData?.total_completed_lessons || 0}
          </p>

          <p className="text-xs text-slate-400 mt-1">
            of {progressData?.total_lessons_available || 0} total units
          </p>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase">
              Overall Progress
            </span>

            <div className="p-2 rounded-lg bg-amber-50 text-amber-600">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>

          <p className="text-2xl font-bold text-slate-900 mt-2">
            {progressData?.overall_completion_percentage || 0}%
          </p>

          <p className="text-xs text-slate-400 mt-1">
            Weighted course average
          </p>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase">
              Courses Completed
            </span>

            <div className="p-2 rounded-lg bg-purple-50 text-purple-600">
              <Award className="w-4 h-4" />
            </div>
          </div>

          <p className="text-2xl font-bold text-slate-900 mt-2">
            {progressData?.completed_courses || 0}
          </p>

          <p className="text-xs text-slate-400 mt-1">
            100% curriculum completion
          </p>
        </Card>
      </div>

      {/* Continue Learning CTA Banner */}
      {continueCourse && (
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-sky-200 dark:border-slate-700 p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full bg-sky-100 text-sky-800 text-[10px] font-bold uppercase tracking-wider">
                Resume Where You Left Off
              </span>

              {continueCourse?.course?.category && (
                <span className="text-xs text-slate-500">
                  {continueCourse.course.category}
                </span>
              )}
            </div>

            <h2 className="text-lg font-bold text-slate-900 dark:text-white">
              {continueCourse?.course?.title || 'Course'}
            </h2>

            <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
              <span>
                {continueCourse?.completed_lesson_count || 0} /{' '}
                {continueCourse?.total_lesson_count || 0} lessons
              </span>

              <span>•</span>

              <span className="font-semibold text-primary-600">
                {continueCourse?.progress_percentage || 0}% completed
              </span>
            </div>
          </div>

          <Link
            to={`/student/courses/${continueCourse.course_id}/learn`}
            className="px-6 py-3 bg-primary-600 hover:bg-primary-500 text-white text-xs font-bold rounded-xl flex items-center justify-center gap-2 shadow-md transition-colors self-start sm:self-center"
          >
            <PlayCircle className="w-4 h-4" />
            Continue Learning
          </Link>
        </div>
      )}

      {/* Enrolled Courses Summary */}
      <Card
        title="My Enrolled Courses"
        subtitle="Recent active courses and direct links to the course player"
      >
        {enrollmentList.length > 0 ? (
          <div className="divide-y divide-slate-100 dark:divide-slate-700">
            {enrollmentList.slice(0, 4).map((e: any) => (
              <div
                key={e.id}
                className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                      {e?.course?.title || 'Untitled Course'}
                    </h3>

                    <Badge
                      variant={
                        Number(e?.progress_percentage || 0) >= 100
                          ? 'success'
                          : 'info'
                      }
                    >
                      {Number(e?.progress_percentage || 0) >= 100
                        ? 'Completed'
                        : `${e?.progress_percentage || 0}%`}
                    </Badge>
                  </div>

                  <p className="text-xs text-slate-500 mt-1">
                    {e?.completed_lesson_count || 0} /{' '}
                    {e?.total_lesson_count || 0} lessons • Instructor:{' '}
                    {e?.course?.instructor_name || 'N/A'}
                  </p>
                </div>

                <Link
                  to={`/student/courses/${e.course_id}/learn`}
                  className="px-4 py-1.5 bg-sky-50 text-sky-700 hover:bg-sky-100 dark:bg-sky-950/40 dark:text-sky-300 rounded-lg text-xs font-semibold flex items-center gap-1.5 self-start sm:self-center"
                >
                  <PlayCircle className="w-3 h-3" />
                  Enter Player
                </Link>
              </div>
            ))}

            <div className="pt-4 text-center">
              <Link
                to="/student/my-learning"
                className="text-xs font-bold text-primary-600 hover:text-primary-500 inline-flex items-center gap-1"
              >
                View All Enrolled Courses
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        ) : (
          <div className="py-8 text-center text-xs text-slate-500 space-y-3">
            <p>You haven't enrolled in any courses yet.</p>

            <Link
              to="/courses"
              className="inline-block px-4 py-2 bg-primary-600 text-white rounded-xl text-xs font-bold hover:bg-primary-500"
            >
              Explore Course Catalog →
            </Link>
          </div>
        )}
      </Card>

      {/* RBAC Verification Sandbox */}
      <Card
        title="Live Server-Side RBAC Verification"
        subtitle="Verify that your JWT token communicates with authenticated backend endpoints"
      >
        <div className="space-y-4">
          <p className="text-xs text-slate-600">
            Click the buttons below to test live API calls against protected
            FastAPI dependencies:
          </p>

          <div className="flex flex-wrap gap-3">
            <Button
              variant="primary"
              size="sm"
              onClick={testStudentEndpoint}
            >
              Probe /api/v1/users/student-only
            </Button>

            <Button
              variant="danger"
              size="sm"
              onClick={testAdminEndpointAsStudent}
            >
              Probe /api/v1/users/admin-only (Should Fail with 403)
            </Button>
          </div>

          {probeResult && (
            <div className="p-3 bg-slate-900 text-slate-100 rounded-lg text-xs font-mono">
              {probeResult}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default StudentDashboard;