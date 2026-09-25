import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, LayoutDashboard } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  path?: string;
}

export interface BreadcrumbsProps {
  items?: BreadcrumbItem[];
  className?: string;
}

// Human-friendly mapping for common URL segments
const ROUTE_LABELS: Record<string, string> = {
  student: 'Student',
  instructor: 'Instructor Studio',
  admin: 'Administration',
  courses: 'Course Catalog',
  'my-learning': 'My Learning',
  progress: 'Learning Progress',
  assessments: 'Assessments',
  certificates: 'Certificates',
  dashboard: 'Dashboard',
  new: 'Create Course',
  edit: 'Edit Course',
  curriculum: 'Curriculum Studio',
  preview: 'Course Preview',
  assignments: 'Assignments',
  submissions: 'Submissions',
  users: 'User Governance',
  audit: 'Audit Logs',
  diagnostics: 'System Diagnostics',
  learn: 'Course Player',
};

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ items, className = '' }) => {
  const location = useLocation();

  // If custom items not provided, automatically deduce from URL pathname
  const deducedItems: BreadcrumbItem[] = React.useMemo(() => {
    if (items && items.length > 0) return items;

    const segments = location.pathname.split('/').filter(Boolean);
    if (segments.length === 0) return [];

    const breadcrumbs: BreadcrumbItem[] = [];
    let currentPath = '';

    segments.forEach((seg, index) => {
      currentPath += `/${seg}`;
      const isLast = index === segments.length - 1;

      // Handle UUIDs or dynamic IDs by displaying clean truncated label
      let label = ROUTE_LABELS[seg];
      if (!label) {
        if (/^[0-9a-fA-F-]{8,}$/.test(seg) || /^\d+$/.test(seg)) {
          label = `Item #${seg.substring(0, 8)}`;
        } else {
          label = seg.charAt(0).toUpperCase() + seg.slice(1).replace(/-/g, ' ');
        }
      }

      breadcrumbs.push({
        label,
        path: isLast ? undefined : currentPath,
      });
    });

    return breadcrumbs;
  }, [items, location.pathname]);

  if (deducedItems.length <= 1 && location.pathname === '/') {
    return null;
  }

  return (
    <nav
      aria-label="Breadcrumb"
      className={`flex items-center text-xs font-medium text-slate-500 py-2 overflow-x-auto no-scrollbar ${className}`}
    >
      <Link
        to="/"
        className="flex items-center gap-1 hover:text-slate-900 transition-colors shrink-0"
        title="Home"
      >
        <LayoutDashboard className="w-3.5 h-3.5 text-slate-400" />
      </Link>

      {deducedItems.map((item, idx) => {
        const isLast = idx === deducedItems.length - 1;
        return (
          <React.Fragment key={idx}>
            <ChevronRight className="w-3.5 h-3.5 mx-1.5 text-slate-300 shrink-0" />
            {item.path && !isLast ? (
              <Link
                to={item.path}
                className="hover:text-slate-900 hover:underline transition-colors shrink-0 max-w-[160px] truncate"
              >
                {item.label}
              </Link>
            ) : (
              <span className="font-semibold text-slate-800 shrink-0 max-w-[200px] truncate">
                {item.label}
              </span>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};
