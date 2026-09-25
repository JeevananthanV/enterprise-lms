import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { PenTool, Users, FileCheck, Sparkles, ShieldCheck, Plus, BookOpen } from 'lucide-react';
import { apiClient } from '../../services/apiClient';
import { courseService } from '../../services/courseService';

export const InstructorDashboard: React.FC = () => {
  const { user } = useAuth();
  const [probeResult, setProbeResult] = useState<string | null>(null);

  const { data: coursesData } = useQuery({
    queryKey: ['instructorCoursesCount'],
    queryFn: () => courseService.getInstructorCourses({ page_size: 5 }),
  });

  const testInstructorEndpoint = async () => {
    try {
      const res = await apiClient.get('/api/v1/users/instructor-only');
      setProbeResult(`Success (200): ${JSON.stringify(res.data)}`);
    } catch (err: any) {
      setProbeResult(`Error (${err.status}): ${err.message}`);
    }
  };

  const testAdminEndpointAsInstructor = async () => {
    try {
      const res = await apiClient.get('/api/v1/users/admin-only');
      setProbeResult(`Unexpected Success (200): ${JSON.stringify(res.data)}`);
    } catch (err: any) {
      setProbeResult(`Expected Denied (${err.status}): ${err.message}`);
    }
  };

  const totalCourses = coursesData?.total ?? 0;
  const publishedCount = coursesData?.items?.filter((c) => c.status === 'PUBLISHED').length ?? 0;
  const draftCount = coursesData?.items?.filter((c) => c.status === 'DRAFT').length ?? 0;

  return (
    <div className="space-y-8">
      {/* Instructor Hero Banner */}
      <div className="bg-gradient-to-r from-amber-900 via-amber-800 to-slate-900 text-white p-6 md:p-8 rounded-2xl shadow-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-amber-500/20 border border-amber-400/30 text-amber-300 text-xs font-semibold mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              Phase 4 Curriculum Studio Active
            </div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight">
              Instructor Studio • {user?.full_name}
            </h1>
            <p className="text-sm text-amber-200 mt-1 max-w-2xl">
              Account Role: <span className="font-semibold text-white">INSTRUCTOR</span> ({user?.email}). Manage courses, author modules and lessons in Curriculum Studio, and publish to students.
            </p>
          </div>

          <div className="flex gap-3">
            <Link
              to="/instructor/courses/new"
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-900 text-xs font-bold rounded-xl shadow transition-colors"
            >
              <Plus className="w-4 h-4" /> Create Course
            </Link>
            <Link
              to="/instructor/courses"
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-xl border border-amber-500/30 transition-colors"
            >
              <BookOpen className="w-4 h-4" /> Course Studio
            </Link>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <Card>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase">Authored Courses</span>
            <div className="p-2 rounded-lg bg-amber-50 text-amber-600">
              <PenTool className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">{totalCourses}</p>
          <p className="text-xs text-slate-400 mt-1">{publishedCount} Published • {draftCount} Drafts</p>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase">Active Students</span>
            <div className="p-2 rounded-lg bg-sky-50 text-sky-600">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">0</p>
          <p className="text-xs text-slate-400 mt-1">Ready for Phase 5 Enrollment</p>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase">Pending Submissions</span>
            <div className="p-2 rounded-lg bg-purple-50 text-purple-600">
              <FileCheck className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">0</p>
          <p className="text-xs text-slate-400 mt-1">Gradebook & Rubrics</p>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase">Security Clearance</span>
            <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">Verified</p>
          <p className="text-xs text-slate-400 mt-1">Author & Grading Privileges</p>
        </Card>
      </div>

      {/* Quick Access to Courses */}
      <Card
        title="Recent Authored Courses"
        subtitle="Quick access to curriculum editing and previewing"
      >
        {coursesData && coursesData.items.length > 0 ? (
          <div className="divide-y divide-gray-100 dark:divide-gray-700">
            {coursesData.items.map((c) => (
              <div key={c.id} className="py-3 flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 dark:text-white">
                    {c.title}
                  </h4>
                  <p className="text-xs text-gray-500">
                    {c.module_count || 0} Modules • {c.lesson_count || 0} Lessons • Status: {c.status}
                  </p>
                </div>
                <div className="flex gap-2">
                  <Link
                    to={`/instructor/courses/${c.id}/curriculum`}
                    className="px-3 py-1 bg-primary-50 text-primary-700 text-xs font-semibold rounded hover:bg-primary-100"
                  >
                    Curriculum Studio
                  </Link>
                  <Link
                    to={`/instructor/courses/${c.id}/preview`}
                    className="px-3 py-1 bg-gray-100 text-gray-700 text-xs rounded hover:bg-gray-200"
                  >
                    Preview
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-6 text-center text-xs text-gray-500">
            No courses authored yet.{' '}
            <Link to="/instructor/courses/new" className="text-primary-600 font-semibold hover:underline">
              Create your first course →
            </Link>
          </div>
        )}
      </Card>

      {/* RBAC Verification Sandbox */}
      <Card
        title="Instructor RBAC Authorization Testing"
        subtitle="Validate server-side role enforcement for instructor routes"
      >
        <div className="space-y-4">
          <p className="text-xs text-slate-600">
            Verify instructor privileges against FastAPI backend endpoints:
          </p>
          <div className="flex flex-wrap gap-3">
            <Button variant="primary" size="sm" onClick={testInstructorEndpoint}>
              Probe /api/v1/users/instructor-only (Should Succeed 200)
            </Button>
            <Button variant="danger" size="sm" onClick={testAdminEndpointAsInstructor}>
              Probe /api/v1/users/admin-only (Should Fail 403)
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

export default InstructorDashboard;
