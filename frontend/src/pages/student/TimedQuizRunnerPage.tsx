import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { assessmentService } from '../../services/assessmentService';
import { QuizAttemptResponse } from '../../types/assessment';
import {
  CheckCircle2,
  AlertTriangle,
  Award,
} from 'lucide-react';

export const TimedQuizRunnerPage: React.FC = () => {
  const { courseId, quizId } = useParams<{ courseId: string; quizId: string }>();

  const [activeAttempt, setActiveAttempt] = useState<QuizAttemptResponse | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [timeRemainingSeconds, setTimeRemainingSeconds] = useState<number | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const [resultAttempt, setResultAttempt] = useState<any | null>(null);
  const [errorMsg, setErrorMsg] = useState('');

  // Start attempt mutation
  const startMutation = useMutation({
    mutationFn: () => assessmentService.startQuizAttempt(quizId!),
    onSuccess: (data) => {
      setActiveAttempt(data);
      if (data.expires_at) {
        const remaining = Math.max(
          0,
          Math.floor((new Date(data.expires_at).getTime() - Date.now()) / 1000)
        );
        setTimeRemainingSeconds(remaining);
      }
    },
    onError: (err: any) => {
      setErrorMsg(err.response?.data?.detail || 'Failed to start quiz attempt.');
    },
  });

  // Submit attempt mutation
  const submitMutation = useMutation({
    mutationFn: () => {
      const answersPayload = Object.entries(selectedAnswers).map(([qId, aId]) => ({
        question_id: qId,
        selected_answer_id: aId,
      }));
      return assessmentService.submitQuizAttempt(
        quizId!,
        activeAttempt!.id,
        answersPayload
      );
    },
    onSuccess: (data) => {
      setIsCompleted(true);
      setResultAttempt(data);
    },
    onError: (err: any) => {
      setErrorMsg(err.response?.data?.detail || 'Failed to submit quiz attempt.');
    },
  });

  // Server-authoritative timer countdown effect
  useEffect(() => {
    if (timeRemainingSeconds === null || isCompleted) return;

    if (timeRemainingSeconds <= 0) {
      // Auto-submit when time expires
      submitMutation.mutate();
      return;
    }

    const interval = setInterval(() => {
      setTimeRemainingSeconds((prev) => (prev !== null && prev > 0 ? prev - 1 : 0));
    }, 1000);

    return () => clearInterval(interval);
  }, [timeRemainingSeconds, isCompleted]);

  const handleSelectAnswer = (questionId: string, answerId: string) => {
    if (isCompleted) return;
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: answerId,
    }));
  };

  const formatTime = (totalSeconds: number) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Not started yet
  if (!activeAttempt && !isCompleted) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 text-center">
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Award className="w-8 h-8 text-primary-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Quiz Assessment</h1>
          <p className="text-gray-600 mb-6">
            Ready to test your knowledge? Once started, questions will appear in randomized order and the timer will begin.
          </p>

          {errorMsg && (
            <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-500 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <div className="flex items-center justify-center gap-4">
            <Link
              to={`/student/courses/${courseId}/learn`}
              className="px-5 py-2.5 border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg text-sm font-medium transition-colors"
            >
              &larr; Back to Course
            </Link>
            <button
              onClick={() => startMutation.mutate()}
              disabled={startMutation.isPending}
              className="px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors disabled:opacity-50"
            >
              {startMutation.isPending ? 'Starting Quiz...' : 'Start Quiz Attempt'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Completed State
  if (isCompleted && resultAttempt) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 text-center">
          <div
            className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 ${
              resultAttempt.passed ? 'bg-green-100' : 'bg-red-100'
            }`}
          >
            {resultAttempt.passed ? (
              <Award className="w-8 h-8 text-green-600" />
            ) : (
              <AlertTriangle className="w-8 h-8 text-red-600" />
            )}
          </div>

          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            {resultAttempt.passed ? 'Congratulations! You Passed!' : 'Attempt Completed'}
          </h1>
          <p className="text-gray-600 mb-6">
            {resultAttempt.passed
              ? 'Great job on completing this quiz!'
              : 'You did not achieve the required passing score. You can review your lessons and try again.'}
          </p>

          <div className="bg-gray-50 rounded-xl p-6 mb-8 border border-gray-100">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase">Your Score</p>
                <p className="text-3xl font-extrabold text-gray-900 mt-1">
                  {resultAttempt.score}%
                </p>
              </div>
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase">Result</p>
                <p
                  className={`text-lg font-bold mt-2 ${
                    resultAttempt.passed ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {resultAttempt.passed ? 'PASSED' : 'FAILED'}
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-center gap-4">
            <Link
              to={`/student/courses/${courseId}/learn`}
              className="px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors"
            >
              Continue Course
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Active Quiz in Progress
  const questions = activeAttempt?.questions || [];
  const currentQ = questions[currentQuestionIndex];
  const progressPercent = questions.length
    ? Math.round(((currentQuestionIndex + 1) / questions.length) * 100)
    : 0;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      {/* Quiz Header with Timer */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6 flex items-center justify-between">
        <div>
          <span className="text-xs font-semibold text-primary-600 uppercase tracking-wide">
            Question {currentQuestionIndex + 1} of {questions.length}
          </span>
          <h2 className="text-lg font-bold text-gray-900">
            {activeAttempt?.quiz_title || 'Timed Assessment'}
          </h2>
        </div>

        {timeRemainingSeconds !== null && (
          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border font-mono font-bold text-sm ${
              timeRemainingSeconds < 60
                ? 'bg-red-50 text-red-700 border-red-200 animate-pulse'
                : 'bg-gray-100 text-gray-800 border-gray-200'
            }`}
          >
            <span>Time Left: {formatTime(timeRemainingSeconds)}</span>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 h-2 rounded-full mb-6 overflow-hidden">
        <div
          className="bg-primary-600 h-2 transition-all duration-300 rounded-full"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {errorMsg && (
        <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-red-500 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Question Card */}
      {currentQ && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-start justify-between gap-4 mb-4">
            <p className="text-lg font-medium text-gray-900">{currentQ.question_text}</p>
            <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded font-semibold shrink-0">
              {currentQ.points} pt{currentQ.points > 1 ? 's' : ''}
            </span>
          </div>

          <div className="space-y-3 mt-6">
            {currentQ.answers.map((ans) => {
              const isSelected = selectedAnswers[currentQ.id] === ans.id;
              return (
                <button
                  key={ans.id}
                  onClick={() => handleSelectAnswer(currentQ.id, ans.id)}
                  className={`w-full text-left p-4 rounded-lg border transition-all flex items-center justify-between ${
                    isSelected
                      ? 'border-primary-600 bg-primary-50 text-primary-900 font-medium'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-800'
                  }`}
                >
                  <span>{ans.answer_text}</span>
                  <div
                    className={`w-5 h-5 rounded-full border flex items-center justify-center ${
                      isSelected
                        ? 'border-primary-600 bg-primary-600'
                        : 'border-gray-300'
                    }`}
                  >
                    {isSelected && <div className="w-2 h-2 rounded-full bg-white" />}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setCurrentQuestionIndex((prev) => Math.max(0, prev - 1))}
          disabled={currentQuestionIndex === 0}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:hover:bg-white flex items-center gap-1 transition-colors"
        >
          &larr; Previous
        </button>

        {currentQuestionIndex < questions.length - 1 ? (
          <button
            onClick={() =>
              setCurrentQuestionIndex((prev) => Math.min(questions.length - 1, prev + 1))
            }
            className="px-5 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-medium flex items-center gap-1 transition-colors"
          >
            Next &rarr;
          </button>
        ) : (
          <button
            onClick={() => submitMutation.mutate()}
            disabled={submitMutation.isPending}
            className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-semibold flex items-center gap-2 shadow-sm transition-colors disabled:opacity-50"
          >
            <CheckCircle2 className="w-4 h-4" />
            {submitMutation.isPending ? 'Submitting...' : 'Finish & Submit Quiz'}
          </button>
        )}
      </div>
    </div>
  );
};
