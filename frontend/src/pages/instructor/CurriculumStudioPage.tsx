import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { courseService } from '../../services/courseService';
import {
  ModuleSummary,
  LessonSummary,
  LessonContentType,
  ModuleCreateInput,
  LessonCreateInput,
} from '../../types/course';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { Badge } from '../../components/common/Badge';

export const CurriculumStudioPage: React.FC = () => {
  const { id: courseId } = useParams<{ id: string }>();
  const queryClient = useQueryClient();

  // State for modals and editing
  const [showAddModule, setShowAddModule] = useState(false);
  const [newModuleTitle, setNewModuleTitle] = useState('');
  const [newModuleDesc, setNewModuleDesc] = useState('');

  const [activeModuleForLesson, setActiveModuleForLesson] = useState<string | null>(null);
  const [newLessonData, setNewLessonData] = useState<LessonCreateInput>({
    title: '',
    content_type: 'VIDEO',
    duration_minutes: 10,
    is_preview: false,
    is_published: true,
  });

  const [editingModule, setEditingModule] = useState<ModuleSummary | null>(null);
  const [editingLesson, setEditingLesson] = useState<LessonSummary | null>(null);

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Queries
  const {
    data: course,
    isLoading: courseLoading,
    isError: courseError,
    error: courseErr,
  } = useQuery({
    queryKey: ['instructorCourse', courseId],
    queryFn: () => courseService.getInstructorCourse(courseId!),
    enabled: !!courseId,
  });

  const { data: checklist, refetch: refetchChecklist } = useQuery({
    queryKey: ['publishChecklist', courseId],
    queryFn: () => courseService.getPublishChecklist(courseId!),
    enabled: !!courseId,
  });

  const refreshAll = () => {
    queryClient.invalidateQueries({ queryKey: ['instructorCourse', courseId] });
    refetchChecklist();
  };

  // Mutations
  const addModuleMutation = useMutation({
    mutationFn: (input: ModuleCreateInput) => courseService.createModule(courseId!, input),
    onSuccess: () => {
      setShowAddModule(false);
      setNewModuleTitle('');
      setNewModuleDesc('');
      setSuccessMessage('Module added.');
      setErrorMessage(null);
      refreshAll();
    },
    onError: (err: any) => {
      setErrorMessage(err.response?.data?.detail || err.message || 'Failed to add module.');
    },
  });

  const updateModuleMutation = useMutation({
    mutationFn: ({ moduleId, input }: { moduleId: string; input: { title: string; description?: string } }) =>
      courseService.updateModule(moduleId, input),
    onSuccess: () => {
      setEditingModule(null);
      setSuccessMessage('Module updated.');
      setErrorMessage(null);
      refreshAll();
    },
    onError: (err: any) => {
      setErrorMessage(err.response?.data?.detail || err.message || 'Failed to update module.');
    },
  });

  const deleteModuleMutation = useMutation({
    mutationFn: (moduleId: string) => courseService.deleteModule(moduleId),
    onSuccess: () => {
      setSuccessMessage('Module deleted.');
      setErrorMessage(null);
      refreshAll();
    },
    onError: (err: any) => {
      setErrorMessage(err.response?.data?.detail || err.message || 'Failed to delete module.');
    },
  });

  const addLessonMutation = useMutation({
    mutationFn: ({ moduleId, input }: { moduleId: string; input: LessonCreateInput }) =>
      courseService.createLesson(moduleId, input),
    onSuccess: () => {
      setActiveModuleForLesson(null);
      setNewLessonData({
        title: '',
        content_type: 'VIDEO',
        duration_minutes: 10,
        is_preview: false,
        is_published: true,
      });
      setSuccessMessage('Lesson added.');
      setErrorMessage(null);
      refreshAll();
    },
    onError: (err: any) => {
      setErrorMessage(err.response?.data?.detail || err.message || 'Failed to add lesson.');
    },
  });

  const updateLessonMutation = useMutation({
    mutationFn: ({ lessonId, input }: { lessonId: string; input: any }) =>
      courseService.updateLesson(lessonId, input),
    onSuccess: () => {
      setEditingLesson(null);
      setSuccessMessage('Lesson updated.');
      setErrorMessage(null);
      refreshAll();
    },
    onError: (err: any) => {
      setErrorMessage(err.response?.data?.detail || err.message || 'Failed to update lesson.');
    },
  });

  const deleteLessonMutation = useMutation({
    mutationFn: (lessonId: string) => courseService.deleteLesson(lessonId),
    onSuccess: () => {
      setSuccessMessage('Lesson deleted.');
      setErrorMessage(null);
      refreshAll();
    },
    onError: (err: any) => {
      setErrorMessage(err.response?.data?.detail || err.message || 'Failed to delete lesson.');
    },
  });

  const reorderModulesMutation = useMutation({
    mutationFn: (moduleIds: string[]) => courseService.reorderModules(courseId!, moduleIds),
    onSuccess: () => {
      setSuccessMessage('Modules reordered successfully.');
      setErrorMessage(null);
      refreshAll();
    },
    onError: (err: any) => {
      setErrorMessage(err.response?.data?.detail || err.message || 'Failed to reorder modules.');
    },
  });

  const reorderLessonsMutation = useMutation({
    mutationFn: ({ moduleId, lessonIds }: { moduleId: string; lessonIds: string[] }) =>
      courseService.reorderLessons(moduleId, lessonIds),
    onSuccess: () => {
      setSuccessMessage('Lessons reordered successfully.');
      setErrorMessage(null);
      refreshAll();
    },
    onError: (err: any) => {
      setErrorMessage(err.response?.data?.detail || err.message || 'Failed to reorder lessons.');
    },
  });

  const publishMutation = useMutation({
    mutationFn: () => courseService.publishCourse(courseId!),
    onSuccess: () => {
      setSuccessMessage('Course published successfully! It is now live on the catalog.');
      setErrorMessage(null);
      refreshAll();
    },
    onError: (err: any) => {
      setErrorMessage(err.response?.data?.detail || err.message || 'Publish prerequisite failed.');
    },
  });

  const unpublishMutation = useMutation({
    mutationFn: () => courseService.unpublishCourse(courseId!),
    onSuccess: () => {
      setSuccessMessage('Course unpublished and moved back to draft status.');
      setErrorMessage(null);
      refreshAll();
    },
    onError: (err: any) => {
      setErrorMessage(err.response?.data?.detail || err.message || 'Failed to unpublish course.');
    },
  });

  // Reorder handlers
  const handleMoveModule = (index: number, direction: 'up' | 'down') => {
    if (!course?.modules) return;
    const items = [...course.modules];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex < 0 || targetIndex >= items.length) return;

    const temp = items[index];
    items[index] = items[targetIndex];
    items[targetIndex] = temp;

    const moduleIds = items.map((m) => m.id);
    reorderModulesMutation.mutate(moduleIds);
  };

  const handleMoveLesson = (module: ModuleSummary, index: number, direction: 'up' | 'down') => {
    if (!module.lessons) return;
    const items = [...module.lessons];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex < 0 || targetIndex >= items.length) return;

    const temp = items[index];
    items[index] = items[targetIndex];
    items[targetIndex] = temp;

    const lessonIds = items.map((l) => l.id);
    reorderLessonsMutation.mutate({ moduleId: module.id, lessonIds });
  };

  if (courseLoading) return <LoadingState message="Loading Curriculum Studio..." />;
  if (courseError || !course) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <ErrorState
          title="Could not load studio"
          message={courseErr instanceof Error ? courseErr.message : 'Course not found or access denied.'}
          onRetry={refreshAll}
        />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Studio Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-6 border-b border-gray-200 dark:border-gray-700 mb-8">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Link
              to="/instructor/courses"
              className="text-xs font-semibold text-gray-500 hover:text-gray-900 dark:hover:text-white"
            >
              ← Courses
            </Link>
            <span className="text-gray-400 text-xs">/</span>
            <span className="text-xs font-semibold text-primary-600 dark:text-primary-400">
              Curriculum Studio
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
            {course.title}
          </h1>
          <div className="flex items-center gap-3 mt-2">
            <Badge
              variant={
                course.status === 'PUBLISHED'
                  ? 'success'
                  : course.status === 'DRAFT'
                  ? 'default'
                  : 'warning'
              }
            >
              {course.status}
            </Badge>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {course.modules.length} Modules • {course.lesson_count} Lessons
            </span>
          </div>
        </div>

        {/* Quick action buttons */}
        <div className="flex flex-wrap items-center gap-3">
          <Link
            to={`/instructor/courses/${courseId}/preview`}
            className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-xs font-semibold rounded-lg hover:bg-gray-200 transition-colors"
          >
            👁️ Preview Course
          </Link>
          <Link
            to={`/instructor/courses/${courseId}/edit`}
            className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-xs font-semibold rounded-lg hover:bg-gray-200 transition-colors"
          >
            ⚙️ Settings
          </Link>

          {course.status === 'PUBLISHED' ? (
            <button
              onClick={() => unpublishMutation.mutate()}
              disabled={unpublishMutation.isPending}
              className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold rounded-lg shadow transition-colors disabled:opacity-50"
            >
              Unpublish Course
            </button>
          ) : (
            <button
              onClick={() => publishMutation.mutate()}
              disabled={publishMutation.isPending || (checklist && !checklist.can_publish)}
              className="px-5 py-2 bg-green-600 hover:bg-green-700 text-white text-xs font-bold rounded-lg shadow transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              title={
                checklist && !checklist.can_publish
                  ? checklist.reasons.join(', ')
                  : 'Publish course to student catalog'
              }
            >
              🚀 Publish Course
            </button>
          )}
        </div>
      </div>

      {/* Alerts */}
      {successMessage && (
        <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-xl text-green-800 dark:text-green-300 text-sm flex justify-between items-center">
          <span>{successMessage}</span>
          <button onClick={() => setSuccessMessage(null)} className="text-green-600 hover:text-green-800">
            ✕
          </button>
        </div>
      )}

      {errorMessage && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl text-red-800 dark:text-red-300 text-sm flex justify-between items-center">
          <span>{errorMessage}</span>
          <button onClick={() => setErrorMessage(null)} className="text-red-600 hover:text-red-800">
            ✕
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Main Curriculum Studio Workspace */}
        <div className="lg:col-span-3 space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">
              Course Structure & Syllabus
            </h2>
            <button
              onClick={() => setShowAddModule(true)}
              className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-xs font-semibold rounded-lg shadow transition-colors flex items-center gap-1.5"
            >
              <span>+</span> Add Module
            </button>
          </div>

          {/* Add Module Modal / Box */}
          {showAddModule && (
            <div className="bg-primary-50/60 dark:bg-gray-800/80 border border-primary-200 dark:border-primary-800 rounded-xl p-5 shadow-sm">
              <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-3">
                Create New Module
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                    Module Title *
                  </label>
                  <input
                    type="text"
                    required
                    value={newModuleTitle}
                    onChange={(e) => setNewModuleTitle(e.target.value)}
                    placeholder="e.g. Module 1: Core Fundamentals"
                    className="w-full px-3 py-2 text-xs rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                    Description (optional)
                  </label>
                  <input
                    type="text"
                    value={newModuleDesc}
                    onChange={(e) => setNewModuleDesc(e.target.value)}
                    placeholder="Brief description of this module's learning goals"
                    className="w-full px-3 py-2 text-xs rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button
                    onClick={() => setShowAddModule(false)}
                    className="px-3 py-1.5 text-xs text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => {
                      if (!newModuleTitle.trim()) return;
                      addModuleMutation.mutate({
                        title: newModuleTitle.trim(),
                        description: newModuleDesc.trim() || undefined,
                      });
                    }}
                    disabled={addModuleMutation.isPending || !newModuleTitle.trim()}
                    className="px-4 py-1.5 bg-primary-600 text-white text-xs font-semibold rounded hover:bg-primary-700 disabled:opacity-50"
                  >
                    Save Module
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Modules List */}
          {course.modules.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-dashed border-gray-300 dark:border-gray-700 p-8 text-center">
              <span className="text-3xl mb-2 block">📂</span>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">No modules added yet</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 max-w-sm mx-auto">
                Break your course into structured sections and modules to start adding lessons.
              </p>
              <button
                onClick={() => setShowAddModule(true)}
                className="mt-4 px-4 py-2 bg-primary-600 text-white text-xs font-semibold rounded-lg hover:bg-primary-700"
              >
                + Add First Module
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {course.modules.map((module, mIdx) => (
                <div
                  key={module.id}
                  className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden"
                >
                  {/* Module Header Bar */}
                  <div className="p-4 bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-700 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <span className="w-7 h-7 rounded-lg bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300 font-bold text-xs flex items-center justify-center">
                        {mIdx + 1}
                      </span>
                      <div>
                        {editingModule?.id === module.id ? (
                          <div className="flex items-center gap-2">
                            <input
                              type="text"
                              value={editingModule.title}
                              onChange={(e) =>
                                setEditingModule({ ...editingModule, title: e.target.value })
                              }
                              className="px-2 py-1 text-xs border rounded"
                            />
                            <button
                              onClick={() =>
                                updateModuleMutation.mutate({
                                  moduleId: module.id,
                                  input: { title: editingModule.title, description: editingModule.description },
                                })
                              }
                              className="px-2 py-1 bg-green-600 text-white text-[11px] rounded"
                            >
                              Save
                            </button>
                            <button
                              onClick={() => setEditingModule(null)}
                              className="text-xs text-gray-500"
                            >
                              Cancel
                            </button>
                          </div>
                        ) : (
                          <div>
                            <h3 className="font-bold text-sm text-gray-900 dark:text-white">
                              {module.title}
                            </h3>
                            {module.description && (
                              <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                                {module.description}
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Module Controls: Reorder, Edit, Delete */}
                    <div className="flex items-center gap-2">
                      <div className="flex items-center border border-gray-200 dark:border-gray-600 rounded bg-white dark:bg-gray-800 overflow-hidden">
                        <button
                          disabled={mIdx === 0}
                          onClick={() => handleMoveModule(mIdx, 'up')}
                          className="px-2 py-1 hover:bg-gray-100 dark:hover:bg-gray-700 text-xs disabled:opacity-30"
                          title="Move module up"
                        >
                          ▲
                        </button>
                        <button
                          disabled={mIdx === course.modules.length - 1}
                          onClick={() => handleMoveModule(mIdx, 'down')}
                          className="px-2 py-1 hover:bg-gray-100 dark:hover:bg-gray-700 text-xs disabled:opacity-30 border-l border-gray-200 dark:border-gray-600"
                          title="Move module down"
                        >
                          ▼
                        </button>
                      </div>

                      <button
                        onClick={() => setEditingModule(module)}
                        className="px-2.5 py-1 text-xs text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
                        title="Edit module name"
                      >
                        Edit
                      </button>

                      <button
                        onClick={() => {
                          if (window.confirm(`Delete module "${module.title}" and its lessons?`)) {
                            deleteModuleMutation.mutate(module.id);
                          }
                        }}
                        className="px-2.5 py-1 text-xs text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 rounded"
                        title="Delete module"
                      >
                        Delete
                      </button>
                    </div>
                  </div>

                  {/* Lessons List within Module */}
                  <div className="p-4 space-y-3">
                    {module.lessons && module.lessons.length > 0 ? (
                      <div className="space-y-2">
                        {module.lessons.map((lesson, lIdx) => (
                          <div
                            key={lesson.id}
                            className="p-3 bg-gray-50 dark:bg-gray-700/30 border border-gray-200 dark:border-gray-700 rounded-lg flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
                          >
                            <div className="flex items-center gap-3">
                              <span className="font-semibold text-gray-400">{lIdx + 1}.</span>
                              <div>
                                {editingLesson?.id === lesson.id ? (
                                  <div className="flex flex-wrap items-center gap-2">
                                    <input
                                      type="text"
                                      value={editingLesson.title}
                                      onChange={(e) =>
                                        setEditingLesson({ ...editingLesson, title: e.target.value })
                                      }
                                      className="px-2 py-1 border rounded text-xs"
                                    />
                                    <select
                                      value={editingLesson.content_type}
                                      onChange={(e) =>
                                        setEditingLesson({
                                          ...editingLesson,
                                          content_type: e.target.value as LessonContentType,
                                        })
                                      }
                                      className="px-2 py-1 border rounded text-xs"
                                    >
                                      <option value="VIDEO">VIDEO</option>
                                      <option value="TEXT">TEXT</option>
                                      <option value="DOCUMENT">DOCUMENT</option>
                                      <option value="QUIZ">QUIZ</option>
                                    </select>
                                    <label className="flex items-center gap-1">
                                      <input
                                        type="checkbox"
                                        checked={editingLesson.is_preview}
                                        onChange={(e) =>
                                          setEditingLesson({
                                            ...editingLesson,
                                            is_preview: e.target.checked,
                                          })
                                        }
                                      />
                                      Preview
                                    </label>
                                    <button
                                      onClick={() =>
                                        updateLessonMutation.mutate({
                                          lessonId: lesson.id,
                                          input: {
                                            title: editingLesson.title,
                                            content_type: editingLesson.content_type,
                                            duration_minutes: editingLesson.duration_minutes,
                                            is_preview: editingLesson.is_preview,
                                          },
                                        })
                                      }
                                      className="px-2 py-1 bg-green-600 text-white rounded text-[11px]"
                                    >
                                      Save
                                    </button>
                                    <button
                                      onClick={() => setEditingLesson(null)}
                                      className="text-gray-500"
                                    >
                                      Cancel
                                    </button>
                                  </div>
                                ) : (
                                  <div className="flex items-center gap-2">
                                    <span className="font-semibold text-gray-900 dark:text-white">
                                      {lesson.title}
                                    </span>
                                    <span className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded text-[10px]">
                                      {lesson.content_type}
                                    </span>
                                    {lesson.is_preview && (
                                      <span className="px-1.5 py-0.5 bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300 rounded text-[10px]">
                                        Preview
                                      </span>
                                    )}
                                    <span className="text-gray-400 text-[11px]">
                                      {lesson.duration_minutes || 0}m
                                    </span>
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* Lesson Reorder & Actions */}
                            <div className="flex items-center gap-2 self-end sm:self-center">
                              <div className="flex items-center border border-gray-200 dark:border-gray-600 rounded bg-white dark:bg-gray-800">
                                <button
                                  disabled={lIdx === 0}
                                  onClick={() => handleMoveLesson(module, lIdx, 'up')}
                                  className="px-1.5 py-0.5 hover:bg-gray-100 text-[11px] disabled:opacity-30"
                                  title="Move lesson up"
                                >
                                  ▲
                                </button>
                                <button
                                  disabled={lIdx === module.lessons.length - 1}
                                  onClick={() => handleMoveLesson(module, lIdx, 'down')}
                                  className="px-1.5 py-0.5 hover:bg-gray-100 text-[11px] disabled:opacity-30 border-l"
                                  title="Move lesson down"
                                >
                                  ▼
                                </button>
                              </div>

                              <button
                                onClick={() => setEditingLesson(lesson)}
                                className="px-2 py-0.5 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded text-xs"
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => {
                                  if (window.confirm(`Delete lesson "${lesson.title}"?`)) {
                                    deleteLessonMutation.mutate(lesson.id);
                                  }
                                }}
                                className="px-2 py-0.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 rounded text-xs"
                              >
                                Delete
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-gray-500 italic py-2">
                        No lessons in this module yet. Add a lesson below.
                      </p>
                    )}

                    {/* Add Lesson inline form / button */}
                    {activeModuleForLesson === module.id ? (
                      <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-700/40 border border-gray-200 dark:border-gray-700 rounded-lg space-y-3">
                        <h4 className="font-semibold text-xs text-gray-900 dark:text-white">
                          Add Lesson to {module.title}
                        </h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          <div>
                            <label className="block text-[11px] font-medium text-gray-600 dark:text-gray-300 mb-1">
                              Lesson Title *
                            </label>
                            <input
                              type="text"
                              value={newLessonData.title}
                              onChange={(e) =>
                                setNewLessonData({ ...newLessonData, title: e.target.value })
                              }
                              placeholder="e.g. Setting up Docker Environment"
                              className="w-full px-2.5 py-1.5 text-xs border rounded dark:bg-gray-700"
                            />
                          </div>

                          <div>
                            <label className="block text-[11px] font-medium text-gray-600 dark:text-gray-300 mb-1">
                              Content Type
                            </label>
                            <select
                              value={newLessonData.content_type}
                              onChange={(e) =>
                                setNewLessonData({
                                  ...newLessonData,
                                  content_type: e.target.value as LessonContentType,
                                })
                              }
                              className="w-full px-2.5 py-1.5 text-xs border rounded dark:bg-gray-700"
                            >
                              <option value="VIDEO">VIDEO</option>
                              <option value="TEXT">TEXT</option>
                              <option value="DOCUMENT">DOCUMENT</option>
                              <option value="QUIZ">QUIZ</option>
                            </select>
                          </div>
                        </div>

                        <div className="flex items-center gap-4 text-xs">
                          <label className="flex items-center gap-1.5">
                            <input
                              type="checkbox"
                              checked={newLessonData.is_preview}
                              onChange={(e) =>
                                setNewLessonData({ ...newLessonData, is_preview: e.target.checked })
                              }
                            />
                            Allow Public Free Preview
                          </label>

                          <div className="flex items-center gap-1.5">
                            <span>Duration (mins):</span>
                            <input
                              type="number"
                              min={1}
                              value={newLessonData.duration_minutes || 10}
                              onChange={(e) =>
                                setNewLessonData({
                                  ...newLessonData,
                                  duration_minutes: parseInt(e.target.value || '1', 10),
                                })
                              }
                              className="w-16 px-2 py-1 text-xs border rounded dark:bg-gray-700"
                            />
                          </div>
                        </div>

                        <div className="flex justify-end gap-2">
                          <button
                            onClick={() => setActiveModuleForLesson(null)}
                            className="px-3 py-1 text-xs text-gray-500"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={() => {
                              if (!newLessonData.title.trim()) return;
                              addLessonMutation.mutate({
                                moduleId: module.id,
                                input: newLessonData,
                              });
                            }}
                            disabled={!newLessonData.title.trim() || addLessonMutation.isPending}
                            className="px-4 py-1 bg-primary-600 text-white text-xs font-semibold rounded hover:bg-primary-700 disabled:opacity-50"
                          >
                            Add Lesson
                          </button>
                        </div>
                      </div>
                    ) : (
                      <button
                        onClick={() => setActiveModuleForLesson(module.id)}
                        className="w-full py-2 border border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-xs font-semibold text-primary-600 dark:text-primary-400 hover:bg-primary-50/50 dark:hover:bg-gray-700/50 transition-colors"
                      >
                        + Add Lesson
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Sidebar: Live Publishing Checklist & Course Health */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm">
            <h3 className="text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider mb-3">
              Publishing Checklist
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
              All rules must be satisfied before this course can be published to students.
            </p>

            {checklist && (
              <div className="space-y-3 text-xs">
                <div className="flex items-center gap-2">
                  <span>{checklist.has_valid_title ? '✅' : '❌'}</span>
                  <span className={checklist.has_valid_title ? 'text-gray-800 dark:text-gray-200' : 'text-red-500'}>
                    Valid Title (min 3 chars)
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span>{checklist.has_valid_description ? '✅' : '❌'}</span>
                  <span className={checklist.has_valid_description ? 'text-gray-800 dark:text-gray-200' : 'text-red-500'}>
                    Description (min 10 chars)
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span>{checklist.module_count >= 1 ? '✅' : '❌'}</span>
                  <span className={checklist.module_count >= 1 ? 'text-gray-800 dark:text-gray-200' : 'text-red-500'}>
                    At least 1 Module ({checklist.module_count} created)
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span>{checklist.lesson_count >= 1 ? '✅' : '❌'}</span>
                  <span className={checklist.lesson_count >= 1 ? 'text-gray-800 dark:text-gray-200' : 'text-red-500'}>
                    At least 1 Lesson ({checklist.lesson_count} created)
                  </span>
                </div>

                <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                  {checklist.can_publish ? (
                    <div className="p-2.5 bg-green-50 dark:bg-green-900/30 text-green-800 dark:text-green-300 rounded-lg text-xs font-semibold text-center">
                      Ready to Publish!
                    </div>
                  ) : (
                    <div className="p-2.5 bg-amber-50 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300 rounded-lg text-xs">
                      <span className="font-bold">Missing requirements:</span>
                      <ul className="list-disc pl-4 mt-1 space-y-1">
                        {checklist.reasons.map((r, i) => (
                          <li key={i}>{r}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CurriculumStudioPage;
