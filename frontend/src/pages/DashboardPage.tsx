import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Server,
  Database,
  Layers,
  Sparkles,
  RefreshCw,
  CheckCircle2,
  Clock,
  BookOpen,
  Users,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react';
import { UserRole } from '../types';
import { healthService } from '../services/healthService';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';

export interface DashboardPageProps {
  activeRole: UserRole;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ activeRole }) => {
  const [showDemoLoading, setShowDemoLoading] = useState(false);
  const [showDemoError, setShowDemoError] = useState(false);
  const [showDemoEmpty, setShowDemoEmpty] = useState(false);

  // TanStack Query for Backend Health Check
  const {
    data: health,
    isLoading,
    isError,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['systemHealth'],
    queryFn: healthService.checkHealth,
    refetchInterval: 15000,
    retry: 1,
  });

  return (
    <div className="space-y-8">
      {/* Top Banner / Welcome Area */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-slate-800 to-sky-950 text-white p-6 md:p-8 rounded-2xl shadow-md">
        <div className="space-y-1.5">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-sky-500/20 border border-sky-400/30 text-sky-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            Phase 1 Foundation Operational
          </div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
            {activeRole === 'STUDENT' && 'Welcome to Your Learning Workspace'}
            {activeRole === 'INSTRUCTOR' && 'Instructor Authoring Studio'}
            {activeRole === 'PLATFORM_ADMIN' && 'Enterprise LMS Platform Control'}
          </h1>
          <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
            {activeRole === 'STUDENT' &&
              'Track your enrolled courses, resume active modules, and prepare for upcoming milestone assessments.'}
            {activeRole === 'INSTRUCTOR' &&
              'Build rich multimedia curriculums, organize course modules, and evaluate student submissions.'}
            {activeRole === 'PLATFORM_ADMIN' &&
              'Oversee tenant health, manage role-based permissions, monitor audit events, and govern catalog publishing.'}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isFetching}
            className="text-white border-white/20 hover:bg-white/10 gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
            Refresh Status
          </Button>
        </div>
      </div>

      {/* Backend & Subsystem Health Card */}
      <Card
        title="Infrastructure & API Health Status"
        subtitle="Live connection diagnostics verifying 3-tier decoupling"
        action={
          <Badge variant={isError ? 'error' : health?.status === 'healthy' ? 'success' : 'warning'}>
            {isError ? 'Backend Disconnected' : health?.status || 'Connecting...'}
          </Badge>
        }
      >
        {isLoading ? (
          <LoadingState message="Probing FastAPI backend..." />
        ) : isError ? (
          <ErrorState
            title="Unable to reach API Server"
            message={`Connection to FastAPI backend at /health failed. Ensure the backend server is running.`}
            onRetry={() => refetch()}
          />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* FastAPI Backend */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 flex items-start gap-3">
              <div className="p-2.5 rounded-lg bg-sky-100 text-sky-700">
                <Server className="w-5 h-5" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold text-slate-500 uppercase">FastAPI Core</p>
                <p className="text-sm font-bold text-slate-900 truncate">v{health?.version}</p>
                <span className="text-[11px] text-emerald-600 font-medium inline-flex items-center gap-1 mt-0.5">
                  <CheckCircle2 className="w-3 h-3" /> Online ({health?.environment})
                </span>
              </div>
            </div>

            {/* PostgreSQL */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 flex items-start gap-3">
              <div className="p-2.5 rounded-lg bg-indigo-100 text-indigo-700">
                <Database className="w-5 h-5" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold text-slate-500 uppercase">PostgreSQL (Relational)</p>
                <p className="text-sm font-bold text-slate-900 truncate">Source of Truth</p>
                <span className="text-[11px] text-slate-600 font-medium inline-flex items-center gap-1 mt-0.5">
                  {health?.subsystems?.postgresql}
                </span>
              </div>
            </div>

            {/* MongoDB */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 flex items-start gap-3">
              <div className="p-2.5 rounded-lg bg-emerald-100 text-emerald-700">
                <Layers className="w-5 h-5" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold text-slate-500 uppercase">MongoDB (Content)</p>
                <p className="text-sm font-bold text-slate-900 truncate">Document Store</p>
                <span className="text-[11px] text-slate-600 font-medium inline-flex items-center gap-1 mt-0.5">
                  {health?.subsystems?.mongodb}
                </span>
              </div>
            </div>

            {/* Redis */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 flex items-start gap-3">
              <div className="p-2.5 rounded-lg bg-rose-100 text-rose-700">
                <Clock className="w-5 h-5" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold text-slate-500 uppercase">Redis (Cache)</p>
                <p className="text-sm font-bold text-slate-900 truncate">Ephemeral & Cache</p>
                <span className="text-[11px] text-slate-600 font-medium inline-flex items-center gap-1 mt-0.5">
                  {health?.subsystems?.redis}
                </span>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* Metric Summary Cards Placeholder */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <Card className="hover:border-slate-300 transition-colors">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase">Catalog Courses</span>
            <div className="p-2 rounded-lg bg-sky-50 text-sky-600">
              <BookOpen className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">--</p>
          <p className="text-xs text-slate-400 mt-1">Ready for Phase 2 Authoring</p>
        </Card>

        <Card className="hover:border-slate-300 transition-colors">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase">Learners & Instructors</span>
            <div className="p-2 rounded-lg bg-purple-50 text-purple-600">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">--</p>
          <p className="text-xs text-slate-400 mt-1">Ready for RBAC & Auth</p>
        </Card>

        <Card className="hover:border-slate-300 transition-colors">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase">Assessments Active</span>
            <div className="p-2 rounded-lg bg-amber-50 text-amber-600">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">--</p>
          <p className="text-xs text-slate-400 mt-1">Planned for Phase 4</p>
        </Card>

        <Card className="hover:border-slate-300 transition-colors">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase">Audit Records</span>
            <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">0</p>
          <p className="text-xs text-slate-400 mt-1">Immutable Log Engine</p>
        </Card>
      </div>

      {/* Component States Interactive Showcase */}
      <Card
        title="UI State Architecture & Component Previews"
        subtitle="Verify responsive loading, error, and empty states"
        action={
          <div className="flex items-center gap-2">
            <Button
              variant={showDemoLoading ? 'primary' : 'outline'}
              size="sm"
              onClick={() => {
                setShowDemoLoading(!showDemoLoading);
                setShowDemoError(false);
                setShowDemoEmpty(false);
              }}
            >
              Loading State
            </Button>
            <Button
              variant={showDemoError ? 'danger' : 'outline'}
              size="sm"
              onClick={() => {
                setShowDemoError(!showDemoError);
                setShowDemoLoading(false);
                setShowDemoEmpty(false);
              }}
            >
              Error State
            </Button>
            <Button
              variant={showDemoEmpty ? 'secondary' : 'outline'}
              size="sm"
              onClick={() => {
                setShowDemoEmpty(!showDemoEmpty);
                setShowDemoLoading(false);
                setShowDemoError(false);
              }}
            >
              Empty State
            </Button>
          </div>
        }
      >
        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/60">
          {showDemoLoading ? (
            <LoadingState message="Simulating asynchronous curriculum data loading..." />
          ) : showDemoError ? (
            <ErrorState
              title="Assessment Submission Failed"
              message="The server rejected the payload due to validation or network timeout. Please verify your connection."
              onRetry={() => setShowDemoError(false)}
            />
          ) : showDemoEmpty ? (
            <EmptyState
              title="No Courses Enrolled Yet"
              description="Explore the course catalog to enroll in your first interactive enterprise learning path."
              actionText="Browse Course Catalog"
              onAction={() => setShowDemoEmpty(false)}
            />
          ) : (
            <div className="text-center py-6">
              <p className="text-sm font-medium text-slate-700">
                Interactive State Preview Mode Active
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Click the buttons above to preview deterministic Loading, Error, and Empty state components.
              </p>
            </div>
          )}
        </div>
      </Card>

      {/* Architecture & Roadmap Callout */}
      <div className="p-6 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1">
          <h3 className="text-base font-bold text-slate-900">
            Phase 1 Foundation Complete • Ready for Phase 2
          </h3>
          <p className="text-xs text-slate-500 max-w-2xl">
            Decoupled 3-tier backend, multi-DB connection abstractions, modular domain routes, and React TypeScript frontend shell are established.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-sky-600 bg-sky-50 px-3 py-1.5 rounded-lg border border-sky-100">
            Next: Course Management & Studio
          </span>
        </div>
      </div>
    </div>
  );
};
