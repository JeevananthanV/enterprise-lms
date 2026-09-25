import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { learningService } from '../../services/learningService';
import { contentService } from '../../services/contentService';
import {
  PlayerLessonItem,
  QuizAttemptResponse,
} from '../../types/learning';
import { LoadingState } from '../../components/common/LoadingState';

import { ErrorState } from '../../components/common/ErrorState';
import { Badge } from '../../components/common/Badge';
import {
  CheckCircle2,
  ChevronRight,
  PlayCircle,
  HelpCircle,
  Award,
  FileText,
  BookOpen,
} from 'lucide-react';



export const CoursePlayerPage: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const queryClient = useQueryClient();

  const [activeLessonId, setActiveLessonId] = useState<string | null>(null);
  const [openModules, setOpenModules] = useState<Record<string, boolean>>({});

  // Quiz interactive state
  const [quizAnswers, setQuizAnswers] = useState<Record<string, string[]>>({});
  const [quizResult, setQuizResult] = useState<QuizAttemptResponse | null>(null);
  const [quizSubmitting, setQuizSubmitting] = useState(false);
  const [showTranscript, setShowTranscript] = useState(false);

  // Fetch course player data
  const {
    data: playerData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['coursePlayer', courseId],
    queryFn: () => learningService.getCoursePlayerData(courseId!),
    enabled: !!courseId,
  });

  // Flatten all lessons across modules for sequential next/previous navigation
  const allLessons: PlayerLessonItem[] = React.useMemo(() => {
    if (!playerData?.modules) return [];
    return playerData.modules.flatMap((m) => m.lessons);
  }, [playerData]);

  // Set initial active lesson on load
  useEffect(() => {
    if (allLessons.length > 0 && !activeLessonId) {
      if (playerData?.last_accessed_lesson_id) {
        setActiveLessonId(playerData.last_accessed_lesson_id);
      } else {
        setActiveLessonId(allLessons[0].id);
      }
    }
  }, [allLessons, playerData, activeLessonId]);

  // Active lesson object
  const activeLesson = allLessons.find((l) => l.id === activeLessonId) || allLessons[0];
  const activeIndex = allLessons.findIndex((l) => l.id === activeLessonId);
  const prevLesson = activeIndex > 0 ? allLessons[activeIndex - 1] : null;
  const nextLesson = activeIndex < allLessons.length - 1 ? allLessons[activeIndex + 1] : null;

  // Fetch flexible lesson content from MongoDB
  const { data: contentData } = useQuery({
    queryKey: ['lessonContent', activeLesson?.id],
    queryFn: () => contentService.getLessonContent(activeLesson!.id),
    enabled: !!activeLesson?.id,
    retry: false,
  });

  // Fetch quiz details if active lesson is a QUIZ or has quiz_id
  const activeQuizId = activeLesson?.quiz_id;

  const { data: quizData, isLoading: isQuizLoading } = useQuery({
    queryKey: ['quiz', activeQuizId],
    queryFn: () => learningService.getQuiz(activeQuizId!),
    enabled: !!activeQuizId,
  });

  // Toggle module open/close in sidebar
  const toggleModule = (moduleId: string) => {
    setOpenModules((prev) => ({
      ...prev,
      [moduleId]: prev[moduleId] !== undefined ? !prev[moduleId] : false,
    }));
  };

  // Mutation for updating lesson progress
  const progressMutation = useMutation({
    mutationFn: ({ lessonId, isCompleted }: { lessonId: string; isCompleted: boolean }) =>
      learningService.updateLessonProgress(lessonId, isCompleted),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['coursePlayer', courseId] });
      queryClient.invalidateQueries({ queryKey: ['myEnrollments'] });
      queryClient.invalidateQueries({ queryKey: ['myProgress'] });
    },
  });

  const handleToggleComplete = () => {
    if (!activeLesson) return;
    const newStatus = !activeLesson.is_completed;
    progressMutation.mutate({ lessonId: activeLesson.id, isCompleted: newStatus });
  };

  const handleSelectAnswer = (questionId: string, answerId: string, isSingle: boolean) => {
    setQuizAnswers((prev) => {
      if (isSingle) {
        return { ...prev, [questionId]: [answerId] };
      } else {
        const current = prev[questionId] || [];
        const exists = current.includes(answerId);
        const updated = exists ? current.filter((id) => id !== answerId) : [...current, answerId];
        return { ...prev, [questionId]: updated };
      }
    });
  };

  const handleSubmitQuiz = async () => {
    if (!activeQuizId || !quizData) return;
    setQuizSubmitting(true);
    try {
      const submissions = quizData.questions.map((q) => ({
        question_id: q.id,
        selected_answer_ids: quizAnswers[q.id] || [],
      }));

      const res = await learningService.submitQuizAttempt(activeQuizId, submissions);
      setQuizResult(res);
      queryClient.invalidateQueries({ queryKey: ['coursePlayer', courseId] });
      queryClient.invalidateQueries({ queryKey: ['myProgress'] });
    } catch (err: any) {
      alert(err.response?.data?.detail || err.message || 'Failed to submit quiz attempt.');
    } finally {
      setQuizSubmitting(false);
    }
  };

  if (isLoading) return <LoadingState message="Loading interactive Course Player..." />;
  if (isError || !playerData) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <ErrorState
          title="Could not load Course Player"
          message={error instanceof Error ? error.message : 'Course not found or access denied.'}
          onRetry={() => refetch()}
        />
        <div className="mt-6 text-center">
          <Link to="/student/my-learning" className="text-primary-600 font-semibold text-sm">
            ← Back to My Learning
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
      {/* Top Player Navigation Bar */}
      <header className="h-14 bg-slate-950 border-b border-slate-800 px-4 flex items-center justify-between z-30 sticky top-0">
        <div className="flex items-center gap-3">
          <Link
            to="/student/my-learning"
            className="flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
          >
            <ChevronRight className="w-4 h-4 rotate-180" />
            <span className="hidden sm:inline">My Learning</span>
          </Link>
          <span className="text-slate-700">|</span>
          <h1 className="text-sm font-bold text-white truncate max-w-xs md:max-w-md">
            {playerData.title}
          </h1>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-2">
            <span className="text-xs text-slate-400">Progress:</span>
            <div className="w-28 bg-slate-800 rounded-full h-2 overflow-hidden">
              <div
                className="bg-emerald-500 h-full rounded-full transition-all duration-300"
                style={{ width: `${playerData.progress_percentage}%` }}
              />
            </div>
            <span className="text-xs font-bold text-emerald-400">
              {playerData.progress_percentage}%
            </span>
          </div>

          <button
            onClick={handleToggleComplete}
            disabled={progressMutation.isPending || !activeLesson}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
              activeLesson?.is_completed
                ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            {activeLesson?.is_completed ? 'Completed' : 'Mark Complete'}
          </button>
        </div>
      </header>

      {/* Main Workspace Layout */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Left Sidebar: Curriculum Tree */}
        <aside className="w-full lg:w-80 bg-slate-950/80 border-r border-slate-800 overflow-y-auto max-h-64 lg:max-h-[calc(100vh-3.5rem)] flex-shrink-0">
          <div className="p-4 border-b border-slate-800/80">
            <div className="flex justify-between items-center text-xs text-slate-400 mb-2">
              <span>Course Syllabus</span>
              <span>
                {playerData.completed_lessons} / {playerData.total_lessons} completed
              </span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
              <div
                className="bg-emerald-500 h-full rounded-full"
                style={{ width: `${playerData.progress_percentage}%` }}
              />
            </div>
          </div>

          <div className="divide-y divide-slate-800/60">
            {playerData.modules.map((m, mIdx) => {
              const isOpen = openModules[m.id] ?? true;
              return (
                <div key={m.id}>
                  <button
                    onClick={() => toggleModule(m.id)}
                    className="w-full px-4 py-3 bg-slate-900/50 hover:bg-slate-900 text-left flex justify-between items-center text-xs transition-colors"
                  >
                    <span className="font-bold text-slate-200 truncate pr-2">
                      Module {mIdx + 1}: {m.title}
                    </span>
                    <span className="text-slate-500">{isOpen ? '▲' : '▼'}</span>
                  </button>

                  {isOpen && (
                    <div className="py-1 bg-slate-950/40">
                      {m.lessons.map((l) => {
                        const isActive = l.id === activeLesson?.id;
                        return (
                          <button
                            key={l.id}
                            onClick={() => {
                              setActiveLessonId(l.id);
                              setQuizResult(null);
                            }}
                            className={`w-full px-4 py-2.5 text-left flex items-start gap-2.5 text-xs transition-colors ${
                              isActive
                                ? 'bg-primary-950/60 border-l-2 border-primary-500 text-white font-semibold'
                                : 'hover:bg-slate-900 text-slate-400 hover:text-slate-200'
                            }`}
                          >
                            <div className="mt-0.5 flex-shrink-0">
                              {l.is_completed ? (
                                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                              ) : (
                                <div className="w-4 h-4 rounded-full border border-slate-600" />
                              )}
                            </div>
                            <div className="flex-1 truncate">
                              <p className="truncate">{l.title}</p>
                              <div className="flex items-center gap-2 text-[10px] text-slate-500 mt-0.5">
                                <span>{l.content_type}</span>
                                {l.duration_minutes > 0 && <span>• {l.duration_minutes}m</span>}
                                {l.quiz_id && <span className="text-amber-400">• Quiz</span>}
                              </div>
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 bg-slate-900 overflow-y-auto p-4 sm:p-8 flex flex-col justify-between max-h-[calc(100vh-3.5rem)]">
          {activeLesson ? (
            <div className="max-w-4xl mx-auto w-full space-y-6">
              {/* Lesson Title Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-800">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs text-primary-400 font-semibold uppercase tracking-wider">
                      {activeLesson.content_type} Lesson
                    </span>
                    {activeLesson.is_completed && (
                      <Badge variant="success">Completed</Badge>
                    )}
                  </div>
                  <h2 className="text-2xl font-bold text-white">{activeLesson.title}</h2>
                </div>

                <div className="text-xs text-slate-400">
                  Estimated: {activeLesson.duration_minutes || 10} minutes
                </div>
              </div>

              {/* MongoDB Content Badge & Version Indicator if active */}
              {contentData && (
                <div className="flex items-center gap-3 px-3 py-1.5 bg-slate-950/80 border border-slate-800 rounded-lg text-xs text-slate-400">
                  <div className="flex items-center gap-1 text-emerald-400 font-medium">
                    <BookOpen className="w-3.5 h-3.5" />
                    <span>Rich Content (MongoDB v{contentData.version})</span>
                  </div>
                  <span>•</span>
                  <span>Format: {contentData.content_type}</span>
                  {contentData.published_at && (
                    <>
                      <span>•</span>
                      <span>Published {new Date(contentData.published_at).toLocaleDateString()}</span>
                    </>
                  )}
                </div>
              )}

              {/* Video Player / Stream Canvas */}
              {(activeLesson.content_type === 'VIDEO' || contentData?.content_type === 'VIDEO' || contentData?.video_metadata) && (
                <div className="bg-black rounded-2xl overflow-hidden aspect-video flex flex-col items-center justify-center border border-slate-800 shadow-2xl relative group">
                  <div className="p-6 text-center">
                    <PlayCircle className="w-16 h-16 text-primary-500 mx-auto mb-3 opacity-90 group-hover:opacity-100 group-hover:scale-105 cursor-pointer transition-all" />
                    <p className="text-sm font-semibold text-slate-300">
                      High-Definition Video Lecture Stream
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      {activeLesson.title} • {contentData?.video_metadata?.resolution || '1080p'} • Provider: {contentData?.video_metadata?.provider?.toUpperCase() || 'S3'}
                    </p>
                    {contentData?.video_metadata?.video_url && (
                      <p className="text-[11px] text-primary-400/80 font-mono mt-2 truncate max-w-md mx-auto">
                        Source: {contentData.video_metadata.video_url}
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* PDF Document Metadata & Reader */}
              {(contentData?.content_type === 'PDF' || contentData?.pdf_metadata) && (
                <div className="bg-slate-950 rounded-2xl p-6 border border-slate-800 shadow-lg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
                      <FileText className="w-6 h-6" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white">
                        {contentData.pdf_metadata?.file_name || `${activeLesson.title}.pdf`}
                      </h4>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {contentData.pdf_metadata?.page_count ? `${contentData.pdf_metadata.page_count} Pages` : 'PDF Document'}
                        {contentData.pdf_metadata?.file_size_bytes && ` • ${(contentData.pdf_metadata.file_size_bytes / 1024 / 1024).toFixed(2)} MB`}
                      </p>
                    </div>
                  </div>
                  {contentData.pdf_metadata?.downloadable !== false && (
                    <a
                      href={contentData.pdf_metadata?.file_url || '#'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl flex items-center gap-1.5 transition-colors"
                    >
                      <FileText className="w-4 h-4" />
                      <span>Download Resource</span>
                    </a>
                  )}
                </div>
              )}

              {/* Rich Text / Markdown Lesson Body */}
              {(contentData?.body || activeLesson.content || (!contentData?.video_metadata && !contentData?.pdf_metadata && activeLesson.content_type !== 'VIDEO')) && (
                <div className="bg-slate-950 rounded-2xl p-6 border border-slate-800 shadow-lg">
                  <div className="prose prose-invert max-w-none text-slate-300 leading-relaxed whitespace-pre-line text-sm">
                    {contentData?.body ||
                      activeLesson.content ||
                      `Welcome to "${activeLesson.title}".\n\nIn this lesson, we cover the core principles, architecture, and practical implementation patterns.\n\nReview the technical concepts outlined above and check off the lesson when you are ready to proceed.`}
                  </div>
                </div>
              )}

              {/* Interactive Collapsible Transcript */}
              {contentData?.transcript && (
                <div className="bg-slate-950 rounded-2xl border border-slate-800 overflow-hidden shadow-lg">
                  <button
                    onClick={() => setShowTranscript((prev) => !prev)}
                    className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-slate-900/50 transition-colors"
                  >
                    <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
                      <FileText className="w-4 h-4 text-primary-400" />
                      <span>Lecture Transcript ({contentData.transcript.language.toUpperCase()})</span>
                    </div>
                    <span className="text-xs text-primary-400 font-medium">
                      {showTranscript ? 'Hide Transcript' : 'Show Transcript'}
                    </span>
                  </button>
                  {showTranscript && (
                    <div className="px-6 pb-6 pt-2 border-t border-slate-800/60 bg-slate-900/30">
                      <div className="text-xs text-slate-300 font-mono leading-relaxed max-h-60 overflow-y-auto whitespace-pre-line">
                        {contentData.transcript.content}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Supplementary External Resources */}
              {contentData?.external_resources && contentData.external_resources.length > 0 && (
                <div className="bg-slate-950 rounded-2xl p-6 border border-slate-800 shadow-lg space-y-4">
                  <h4 className="text-sm font-bold text-white flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-primary-400" />
                    <span>Supplementary Learning Resources</span>
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {contentData.external_resources.map((res, idx) => (
                      <a
                        key={idx}
                        href={res.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-3 bg-slate-900/60 hover:bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl transition-all block group"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-semibold text-slate-200 group-hover:text-primary-400 transition-colors truncate">
                            {res.title}
                          </span>
                          <ChevronRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-primary-400 transition-colors" />
                        </div>
                        {res.description && (
                          <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                            {res.description}
                          </p>
                        )}
                        <span className="inline-block text-[10px] text-slate-500 font-medium uppercase mt-2">
                          {res.resource_type}
                        </span>
                      </a>
                    ))}
                  </div>
                </div>
              )}



              {/* Interactive Quiz Section if lesson has Quiz */}
              {activeQuizId && (
                <div className="bg-slate-950 rounded-2xl p-6 border border-amber-500/30 shadow-xl space-y-6">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                    <div className="flex items-center gap-2">
                      <HelpCircle className="w-5 h-5 text-amber-400" />
                      <h3 className="text-base font-bold text-white">
                        {quizData?.title || 'Lesson Quiz Check'}
                      </h3>
                    </div>
                    {quizData && (
                      <span className="text-xs text-amber-400 font-semibold">
                        Passing Score: {quizData.passing_score}%
                      </span>
                    )}
                  </div>

                  {isQuizLoading ? (
                    <LoadingState message="Loading quiz assessment..." />
                  ) : quizData ? (
                    <div className="space-y-6">
                      {quizResult && (
                        <div
                          className={`p-4 rounded-xl border ${
                            quizResult.passed
                              ? 'bg-emerald-950/40 border-emerald-500 text-emerald-200'
                              : 'bg-rose-950/40 border-rose-500 text-rose-200'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-sm">
                              {quizResult.passed ? '🎉 Congratulations! You Passed!' : '❌ Did not pass'}
                            </span>
                            <span className="text-sm font-extrabold">
                              Score: {quizResult.score}%
                            </span>
                          </div>
                          <p className="text-xs mt-1">
                            Passing score is {quizResult.passing_score}%.{' '}
                            {quizResult.passed
                              ? 'Lesson marked as complete!'
                              : 'You can review the material and retake the quiz.'}
                          </p>
                        </div>
                      )}

                      {quizData.questions.map((q, qIdx) => (
                        <div key={q.id} className="space-y-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                          <p className="text-xs font-semibold text-slate-200">
                            {qIdx + 1}. {q.question_text}
                          </p>

                          <div className="space-y-2">
                            {q.answers.map((ans) => {
                              const isSelected = (quizAnswers[q.id] || []).includes(ans.id);
                              return (
                                <button
                                  key={ans.id}
                                  onClick={() =>
                                    handleSelectAnswer(
                                      q.id,
                                      ans.id,
                                      q.question_type === 'SINGLE_CHOICE' || q.question_type === 'TRUE_FALSE'
                                    )
                                  }
                                  className={`w-full text-left px-3 py-2 rounded-lg text-xs flex items-center gap-2.5 transition-colors ${
                                    isSelected
                                      ? 'bg-primary-600 text-white font-semibold'
                                      : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                                  }`}
                                >
                                  <div
                                    className={`w-3.5 h-3.5 rounded-full border flex items-center justify-center ${
                                      isSelected
                                        ? 'border-white bg-white text-primary-600'
                                        : 'border-slate-500'
                                    }`}
                                  >
                                    {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-primary-600" />}
                                  </div>
                                  <span>{ans.answer_text}</span>
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      ))}

                      <div className="flex justify-end">
                        <button
                          onClick={handleSubmitQuiz}
                          disabled={quizSubmitting}
                          className="px-5 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold rounded-xl shadow transition-colors disabled:opacity-50"
                        >
                          {quizSubmitting ? 'Evaluating...' : 'Submit Answers'}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <p className="text-xs text-slate-400">Quiz details could not be loaded.</p>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-20 text-slate-400 text-sm">
              Select a lesson from the curriculum outline to begin learning.
            </div>
          )}

          {/* Sequential Prev/Next Footer Navigation */}
          <footer className="mt-8 pt-6 border-t border-slate-800 flex justify-between items-center">
            {prevLesson ? (
              <button
                onClick={() => {
                  setActiveLessonId(prevLesson.id);
                  setQuizResult(null);
                }}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl flex items-center gap-1.5 transition-colors"
              >
                <ChevronRight className="w-4 h-4 rotate-180" /> Previous Lesson
              </button>
            ) : (
              <div />
            )}

            {nextLesson ? (
              <button
                onClick={() => {
                  setActiveLessonId(nextLesson.id);
                  setQuizResult(null);
                }}
                className="px-5 py-2 bg-primary-600 hover:bg-primary-500 text-white text-xs font-semibold rounded-xl flex items-center gap-1.5 transition-colors shadow-md"
              >
                Next Lesson <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <Link
                to="/student/my-learning"
                className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl flex items-center gap-1.5 transition-colors shadow-md"
              >
                <Award className="w-4 h-4" /> Course Completed! Back to My Learning
              </Link>
            )}
          </footer>
        </main>
      </div>
    </div>
  );
};

export default CoursePlayerPage;
