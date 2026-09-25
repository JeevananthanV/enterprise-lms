import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  BookOpen,
  Search,
  Layers,
} from 'lucide-react';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';
import { Tabs } from '../../components/common/Tabs';
import { courseService } from '../../services/courseService';
import { Course } from '../../types/course';

export const CourseModerationPage: React.FC = () => {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const { data: coursesData } = useQuery({
    queryKey: ['public-courses', search],
    queryFn: () => courseService.getPublicCourses({ search: search || undefined, page_size: 50 }),
  });

  const courses: Course[] = coursesData?.items || [];

  const filteredCourses = courses.filter((c: Course) => {
    if (statusFilter === 'ALL') return true;
    return c.status === statusFilter;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Course Moderation & Quality Control
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Oversee course publishing standards, verify curriculum completeness, and manage platform-wide offerings.
          </p>
        </div>
      </div>

      {/* Status Tabs */}
      <Tabs
        tabs={[
          { id: 'ALL', label: 'All Courses', count: courses.length },
          { id: 'PUBLISHED', label: 'Published & Live', count: courses.filter((c: Course) => c.status === 'PUBLISHED').length },
          { id: 'DRAFT', label: 'Drafts', count: courses.filter((c: Course) => c.status === 'DRAFT').length },
          { id: 'ARCHIVED', label: 'Archived', count: courses.filter((c: Course) => c.status === 'ARCHIVED').length },
        ]}
        activeTab={statusFilter}
        onChange={setStatusFilter}
      />

      {/* Search Bar */}
      <div className="flex items-center justify-between gap-4">
        <div className="relative max-w-sm w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search courses by title, instructor, slug..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 rounded-xl focus:outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-100 transition-all shadow-xs"
          />
        </div>
        <span className="text-xs text-slate-500 font-medium">
          Showing {filteredCourses.length} of {courses.length} courses
        </span>
      </div>

      {/* Course List Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/80 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                <th className="py-3.5 px-4">Course Title</th>
                <th className="py-3.5 px-4">Category / Level</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4">Curriculum</th>
                <th className="py-3.5 px-4 text-right">Moderation Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs">
              {filteredCourses.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-400">
                    No courses match the current moderation criteria.
                  </td>
                </tr>
              ) : (
                filteredCourses.map((course: Course) => (
                  <tr key={course.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-sky-100 text-sky-700 flex items-center justify-center font-bold text-xs shrink-0">
                          <BookOpen className="w-4 h-4" />
                        </div>
                        <div>
                          <p className="font-semibold text-slate-900 leading-tight">{course.title}</p>
                          <p className="text-[11px] text-slate-400 font-mono mt-0.5">/{course.slug}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="space-y-1">
                        <span className="text-slate-700 font-medium">{course.category || 'General'}</span>
                        <div>
                          <Badge variant="info" className="text-[10px] px-1.5 py-0">
                            {course.level}
                          </Badge>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <Badge
                        variant={
                          course.status === 'PUBLISHED'
                            ? 'success'
                            : course.status === 'DRAFT'
                            ? 'warning'
                            : 'default'
                        }
                      >
                        {course.status}
                      </Badge>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600">
                      <div className="flex items-center gap-1.5">
                        <Layers className="w-3.5 h-3.5 text-slate-400" />
                        <span>
                          {course.module_count || 0} Modules • {course.lesson_count || 0} Lessons
                        </span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => navigate(`/courses/${course.id}`)}
                          className="text-[11px] py-1"
                        >
                          Inspect
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => navigate(`/instructor/courses/${course.id}/curriculum`)}
                          className="text-[11px] py-1"
                        >
                          Curriculum
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
