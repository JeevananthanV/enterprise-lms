import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AppShell } from './components/layout/AppShell';
import { RoleGuard } from './components/layout/RoleGuard';
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { StudentDashboard } from './pages/student/StudentDashboard';
import { MyLearningPage } from './pages/student/MyLearningPage';
import { CoursePlayerPage } from './pages/student/CoursePlayerPage';
import { ProgressDashboardPage } from './pages/student/ProgressDashboardPage';
import { AssignmentSubmissionPage } from './pages/student/AssignmentSubmissionPage';
import { TimedQuizRunnerPage } from './pages/student/TimedQuizRunnerPage';
import { CertificatePage } from './pages/student/CertificatePage';
import { CertificateVerificationPage } from './pages/public/CertificateVerificationPage';
import { InstructorDashboard } from './pages/instructor/InstructorDashboard';
import { InstructorCoursesPage } from './pages/instructor/InstructorCoursesPage';
import { CourseCreatePage } from './pages/instructor/CourseCreatePage';
import { CourseEditPage } from './pages/instructor/CourseEditPage';
import { CurriculumStudioPage } from './pages/instructor/CurriculumStudioPage';
import { CoursePreviewPage } from './pages/instructor/CoursePreviewPage';
import { InstructorAssignmentsPage } from './pages/instructor/InstructorAssignmentsPage';
import { SubmissionGradingPage } from './pages/instructor/SubmissionGradingPage';
import { CourseCatalogPage } from './pages/courses/CourseCatalogPage';
import { CourseDetailsPage } from './pages/courses/CourseDetailsPage';
import { AdminDashboard } from './pages/admin/AdminDashboard';
import { UserManagementPage } from './pages/admin/UserManagementPage';
import { CourseModerationPage } from './pages/admin/CourseModerationPage';
import { AuditLogsPage } from './pages/admin/AuditLogsPage';
import { SystemDiagnosticsPage } from './pages/admin/SystemDiagnosticsPage';
import { ToastProvider } from './context/ToastContext';
import { PlaceholderPage } from './pages/PlaceholderPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { LoadingState } from './components/common/LoadingState';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 30,
      refetchOnWindowFocus: false,
    },
  },
});

// Root index redirect based on user role
const RootRedirect: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <LoadingState message="Loading LMS session..." />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role === 'PLATFORM_ADMIN') {
    return <Navigate to="/admin/dashboard" replace />;
  } else if (user.role === 'INSTRUCTOR') {
    return <Navigate to="/instructor/dashboard" replace />;
  } else {
    return <Navigate to="/student/dashboard" replace />;
  }
};

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ToastProvider>
          <BrowserRouter>
            <Routes>
              {/* Public Authentication Routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />

              {/* Public Credential Verification */}
              <Route path="/verify/certificate" element={<CertificateVerificationPage />} />
              <Route
                path="/verify/certificate/:certificateNumber"
                element={<CertificateVerificationPage />}
              />

              {/* Root Dispatcher */}
              <Route path="/" element={<RootRedirect />} />

              {/* Public / Authenticated Course Discovery Routes */}
              <Route
                path="/courses"
                element={
                  <AppShell>
                    <CourseCatalogPage />
                  </AppShell>
                }
              />
              <Route
                path="/courses/:id"
                element={
                  <AppShell>
                    <CourseDetailsPage />
                  </AppShell>
                }
              />

              {/* Protected Student Routes */}
              <Route
                path="/student/dashboard"
                element={
                  <RoleGuard allowedRoles={['STUDENT', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <StudentDashboard />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/student/my-learning"
                element={
                  <RoleGuard allowedRoles={['STUDENT', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <MyLearningPage />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/enrollments"
                element={<Navigate to="/student/my-learning" replace />}
              />
              <Route
                path="/student/progress"
                element={
                  <RoleGuard allowedRoles={['STUDENT', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <ProgressDashboardPage />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/progress"
                element={<Navigate to="/student/progress" replace />}
              />
              <Route
                path="/student/courses"
                element={<Navigate to="/courses" replace />}
              />
              <Route
                path="/student/courses/:courseId/learn"
                element={
                  <RoleGuard allowedRoles={['STUDENT', 'PLATFORM_ADMIN']}>
                    <CoursePlayerPage />
                  </RoleGuard>
                }
              />
              <Route
                path="/student/courses/:courseId/assignments/:assignmentId"
                element={
                  <RoleGuard allowedRoles={['STUDENT', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <AssignmentSubmissionPage />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/student/courses/:courseId/quizzes/:quizId"
                element={
                  <RoleGuard allowedRoles={['STUDENT', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <TimedQuizRunnerPage />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/student/courses/:courseId/certificate"
                element={
                  <RoleGuard allowedRoles={['STUDENT', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <CertificatePage />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/student/certificates/:certificateId"
                element={
                  <RoleGuard allowedRoles={['STUDENT', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <CertificatePage />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/assessments"
                element={
                  <RoleGuard allowedRoles={['STUDENT', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <PlaceholderPage
                        title="Quizzes & Assessments"
                        domain="assessment"
                        scheduledPhase="Phase 6"
                        description="Take timed quizzes and view score breakdowns directly from your enrolled courses."
                      />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/certificates"
                element={
                  <RoleGuard allowedRoles={['STUDENT', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <PlaceholderPage
                        title="Certificates of Completion"
                        domain="progress / certificates"
                        scheduledPhase="Phase 6"
                        description="View and verify completed curriculum certificates from your progress dashboard."
                      />
                    </AppShell>
                  </RoleGuard>
                }
              />

              {/* Protected Instructor Routes */}
              <Route
                path="/instructor/dashboard"
                element={
                  <RoleGuard allowedRoles={['INSTRUCTOR', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <InstructorDashboard />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/instructor/courses"
                element={
                  <RoleGuard allowedRoles={['INSTRUCTOR', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <InstructorCoursesPage />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/instructor/courses/new"
                element={
                  <RoleGuard allowedRoles={['INSTRUCTOR', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <CourseCreatePage />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/instructor/courses/:id/edit"
                element={
                  <RoleGuard allowedRoles={['INSTRUCTOR', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <CourseEditPage />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/instructor/courses/:id/curriculum"
                element={
                  <RoleGuard allowedRoles={['INSTRUCTOR', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <CurriculumStudioPage />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/instructor/courses/:id/assignments"
                element={
                  <RoleGuard allowedRoles={['INSTRUCTOR', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <InstructorAssignmentsPage />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/instructor/submissions/:submissionId"
                element={
                  <RoleGuard allowedRoles={['INSTRUCTOR', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <SubmissionGradingPage />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/instructor/courses/:id/preview"
                element={
                  <RoleGuard allowedRoles={['INSTRUCTOR', 'PLATFORM_ADMIN']}>
                    <CoursePreviewPage />
                  </RoleGuard>
                }
              />
              <Route
                path="/authoring"
                element={<Navigate to="/instructor/courses" replace />}
              />
              <Route
                path="/modules"
                element={<Navigate to="/instructor/courses" replace />}
              />
              <Route
                path="/grading"
                element={
                  <RoleGuard allowedRoles={['INSTRUCTOR', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <InstructorCoursesPage />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/analytics"
                element={
                  <RoleGuard allowedRoles={['INSTRUCTOR', 'PLATFORM_ADMIN']}>
                    <AppShell>
                      <PlaceholderPage
                        title="Learning Analytics"
                        domain="analytics"
                        scheduledPhase="Phase 7"
                        description="Inspect student engagement drop-off and score distributions."
                      />
                    </AppShell>
                  </RoleGuard>
                }
              />

              {/* Protected Platform Admin Routes */}
              <Route
                path="/admin/dashboard"
                element={
                  <RoleGuard allowedRoles={['PLATFORM_ADMIN']}>
                    <AppShell>
                      <AdminDashboard />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/admin/users"
                element={
                  <RoleGuard allowedRoles={['PLATFORM_ADMIN']}>
                    <AppShell>
                      <UserManagementPage />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/admin/courses"
                element={
                  <RoleGuard allowedRoles={['PLATFORM_ADMIN']}>
                    <AppShell>
                      <CourseModerationPage />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/admin/audit"
                element={
                  <RoleGuard allowedRoles={['PLATFORM_ADMIN']}>
                    <AppShell>
                      <AuditLogsPage />
                    </AppShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/admin/diagnostics"
                element={
                  <RoleGuard allowedRoles={['PLATFORM_ADMIN']}>
                    <AppShell>
                      <SystemDiagnosticsPage />
                    </AppShell>
                  </RoleGuard>
                }
              />

              {/* Fallback 404 Route */}
              <Route
                path="*"
                element={
                  <AppShell>
                    <NotFoundPage />
                  </AppShell>
                }
              />
            </Routes>
          </BrowserRouter>
        </ToastProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
