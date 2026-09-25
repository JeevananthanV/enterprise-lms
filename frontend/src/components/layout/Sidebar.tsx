import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  BookOpen,
  GraduationCap,
  CheckCircle2,
  FileQuestion,
  Award,
  PenTool,
  Users,
  BarChart3,
  ShieldAlert,
  Activity,
  ChevronRight,
  Lock,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Badge } from '../common/Badge';

export interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

interface MenuItem {
  name: string;
  path: string;
  icon: React.ReactNode;
  badge?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
}) => {
  const { user } = useAuth();
  const role = user?.role || 'STUDENT';

  // Define navigation hierarchy per persona
  const getNavSections = (): { title: string; items: MenuItem[] }[] => {
    if (role === 'STUDENT') {
      return [
        {
          title: 'Student Navigation',
          items: [
            { name: 'Dashboard', path: '/student/dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
            { name: 'Course Catalog', path: '/courses', icon: <BookOpen className="w-4 h-4" />, badge: 'Catalog' },
            { name: 'My Learning', path: '/student/my-learning', icon: <GraduationCap className="w-4 h-4" /> },
            { name: 'Learning Progress', path: '/student/progress', icon: <CheckCircle2 className="w-4 h-4" /> },
            { name: 'Quizzes & Tests', path: '/assessments', icon: <FileQuestion className="w-4 h-4" /> },
            { name: 'Certificates', path: '/certificates', icon: <Award className="w-4 h-4" /> },
          ],
        },
      ];
    } else if (role === 'INSTRUCTOR') {
      return [
        {
          title: 'Instructor Studio',
          items: [
            { name: 'Studio Dashboard', path: '/instructor/dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
            { name: 'My Courses', path: '/instructor/courses', icon: <PenTool className="w-4 h-4" />, badge: 'Studio' },
            { name: 'Create Course', path: '/instructor/courses/new', icon: <BookOpen className="w-4 h-4" /> },
            { name: 'Course Catalog', path: '/courses', icon: <GraduationCap className="w-4 h-4" /> },
            { name: 'Grading & Submissions', path: '/grading', icon: <FileQuestion className="w-4 h-4" /> },
            { name: 'Student Analytics', path: '/analytics', icon: <BarChart3 className="w-4 h-4" /> },
          ],
        },
      ];
    } else {
      return [
        {
          title: 'Platform Administration',
          items: [
            { name: 'Admin Dashboard', path: '/admin/dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
            { name: 'User Governance & RBAC', path: '/admin/users', icon: <Users className="w-4 h-4" />, badge: 'RBAC' },
            { name: 'Course Moderation', path: '/admin/courses', icon: <BookOpen className="w-4 h-4" /> },
            { name: 'Security & Audit Logs', path: '/admin/audit', icon: <ShieldAlert className="w-4 h-4" /> },
            { name: 'System Diagnostics', path: '/admin/diagnostics', icon: <Activity className="w-4 h-4" /> },
          ],
        },
      ];
    }
  };

  const navSections = getNavSections();

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-xs md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-16 bottom-0 left-0 z-40 w-64 border-r border-slate-200 bg-white transition-transform duration-200 ease-in-out md:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } flex flex-col justify-between`}
      >
        <div className="flex-1 overflow-y-auto px-4 py-5">
          {/* Active Persona Banner */}
          <div className="mb-6 px-3 py-2.5 bg-slate-50 rounded-xl border border-slate-200/80">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">
                RBAC Role
              </span>
              <Badge
                variant={
                  role === 'PLATFORM_ADMIN'
                    ? 'error'
                    : role === 'INSTRUCTOR'
                    ? 'warning'
                    : 'info'
                }
              >
                {role}
              </Badge>
            </div>
            <p className="text-xs font-semibold text-slate-800 mt-1 truncate">
              {user?.full_name || 'Authenticated User'}
            </p>
            <p className="text-[11px] text-slate-500 truncate">{user?.email}</p>
          </div>

          {/* Navigation Sections */}
          {navSections.map((section, idx) => (
            <div key={idx} className="mb-6">
              <h4 className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                {section.title}
              </h4>
              <nav className="space-y-1">
                {section.items.map((item) => (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center justify-between px-3 py-2 text-xs font-medium rounded-lg transition-colors ${
                        isActive
                          ? 'bg-sky-50 text-sky-700 font-semibold border-l-2 border-sky-600'
                          : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                      }`
                    }
                    onClick={() => {
                      if (window.innerWidth < 768) onClose();
                    }}
                  >
                    <div className="flex items-center gap-2.5">
                      {item.icon}
                      <span>{item.name}</span>
                    </div>
                    {item.badge ? (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-200 text-slate-600 font-medium">
                        {item.badge}
                      </span>
                    ) : (
                      <ChevronRight className="w-3.5 h-3.5 opacity-30" />
                    )}
                  </NavLink>
                ))}
              </nav>
            </div>
          ))}

          {/* RBAC Security Box */}
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl mt-4">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-800">
              <Lock className="w-3.5 h-3.5 text-sky-600" />
              <span>JWT Authentication</span>
            </div>
            <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
              Tokens securely verified on server. Permissions enforced via FastAPI dependencies.
            </p>
          </div>
        </div>

        {/* Footer Meta */}
        <div className="p-4 border-t border-slate-100 text-center">
          <p className="text-[11px] text-slate-400 font-medium">
            Enterprise LMS • v0.2.0-auth
          </p>
          <p className="text-[10px] text-slate-400">Target: 18 Sep 2026</p>
        </div>
      </aside>
    </>
  );
};
