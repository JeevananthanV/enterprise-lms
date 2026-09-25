import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { courseService } from '../../services/courseService';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { Badge } from '../../components/common/Badge';

export const CoursePreviewPage: React.FC = () => {
  const { id: courseId } = useParams<{ id: string }>();
  const [selectedLesson, setSelectedLesson] = useState<any | null>(null);

  const { data: course, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['previewCourse', courseId],
    queryFn: () => courseService.previewCourse(courseId!),
    enabled: !!courseId,
  });

  if (isLoading) return <LoadingState message="Loading instructor course preview..." />;
  if (isError || !course) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <ErrorState
          title="Preview unavailable"
          message={error instanceof Error ? error.message : 'Unable to preview course.'}
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-16">
      {/* Top Preview Alert Bar */}
      <div className="bg-amber-500 text-slate-900 px-4 py-2 text-xs font-bold flex justify-between items-center shadow-sm">
        <div className="flex items-center gap-2">
          <span>⚠️ INSTRUCTOR PREVIEW MODE</span>
          <span className="font-normal text-[11px] opacity-90">
            (Viewing private draft and unpublished modules as a learner)
          </span>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to={`/instructor/courses/${courseId}/curriculum`}
            className="px-2.5 py-1 bg-slate-900 text-white rounded text-[11px] hover:bg-slate-800"
          >
            ← Exit Preview to Studio
          </Link>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-8 shadow-sm mb-8">
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <Badge variant="warning">{course.status}</Badge>
            <Badge variant="info">{course.level}</Badge>
            {course.category && (
              <span className="text-xs font-semibold text-primary-600 dark:text-primary-400">
                {course.category}
              </span>
            )}
          </div>

          <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white">
            {course.title}
          </h1>

          <p className="mt-3 text-sm text-gray-600 dark:text-gray-300">
            {course.short_description || course.description}
          </p>
        </div>

        {/* Syllabus / Content Preview */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
              <h2 className="text-base font-bold text-gray-900 dark:text-white mb-4">
                Lesson Content Player Preview
              </h2>
              {selectedLesson ? (
                <div className="p-6 bg-gray-900 text-white rounded-xl shadow-inner">
                  <div className="flex justify-between items-center pb-3 border-b border-gray-700 mb-4">
                    <h3 className="font-bold text-base">{selectedLesson.title}</h3>
                    <Badge variant="info">{selectedLesson.content_type}</Badge>
                  </div>
                  <div className="py-8 text-center text-gray-400 text-sm">
                    <span>🎬 [{selectedLesson.content_type} Content Viewer Simulation]</span>
                    <p className="text-xs mt-2">
                      Duration: {selectedLesson.duration_minutes || 0} minutes
                    </p>
                  </div>
                </div>
              ) : (
                <div className="p-12 text-center text-gray-400 border border-dashed rounded-xl text-sm">
                  Select a lesson from the curriculum sidebar to preview its content.
                </div>
              )}
            </div>
          </div>

          {/* Modules and Lessons list */}
          <div className="lg:col-span-1 space-y-4">
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm">
              <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-3">
                Curriculum Outline
              </h3>
              <div className="space-y-4">
                {course.modules.map((m, mIdx) => (
                  <div key={m.id} className="border-t border-gray-100 dark:border-gray-700 pt-3">
                    <h4 className="text-xs font-bold text-gray-800 dark:text-gray-200 mb-2">
                      Module {mIdx + 1}: {m.title}
                    </h4>
                    <div className="space-y-1">
                      {m.lessons?.map((l) => (
                        <button
                          key={l.id}
                          onClick={() => setSelectedLesson(l)}
                          className={`w-full text-left px-3 py-2 rounded text-xs flex justify-between items-center transition-colors ${
                            selectedLesson?.id === l.id
                              ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/40 dark:text-primary-300 font-semibold'
                              : 'hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300'
                          }`}
                        >
                          <span className="truncate">{l.title}</span>
                          <span className="text-[10px] text-gray-400">{l.duration_minutes}m</span>
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoursePreviewPage;
