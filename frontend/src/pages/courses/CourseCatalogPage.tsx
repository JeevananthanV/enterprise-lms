import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useSearchParams } from 'react-router-dom';

import { courseService } from '../../services/courseService';
import { CourseLevel, Course } from '../../types/course';

const CATEGORIES = [
  'All Categories',
  'Software Engineering',
  'Data Science & AI',
  'Cloud & DevOps',
  'Cybersecurity',
  'Business & Leadership',
  'Product Design',
];

const LEVELS: { label: string; value?: CourseLevel }[] = [
  { label: 'All Levels', value: undefined },
  { label: 'Beginner', value: 'BEGINNER' },
  { label: 'Intermediate', value: 'INTERMEDIATE' },
  { label: 'Advanced', value: 'ADVANCED' },
];

export const CourseCatalogPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const search = searchParams.get('search') || '';
  const category = searchParams.get('category') || '';
  const level =
    (searchParams.get('level') as CourseLevel | null) || undefined;

  const page = Math.max(
    1,
    parseInt(searchParams.get('page') || '1', 10)
  );

  const [searchInput, setSearchInput] = useState(search);

  const {
    data,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: [
      'publicCourses',
      {
        search,
        category,
        level,
        page,
      },
    ],

    queryFn: () =>
      courseService.getPublicCourses({
        search: search || undefined,
        category:
          category && category !== 'All Categories'
            ? category
            : undefined,
        level,
        page,
        page_size: 12,
      }),
  });

  /*
   * API returns:
   *
   * {
   *   items: [...],
   *   total: number,
   *   page: number,
   *   page_size: number,
   *   pages: number
   * }
   *
   * courseService already returns res.data.
   */

  const response = data as any;

  const courseItems: Course[] = Array.isArray(response?.items)
    ? response.items
    : [];

  const totalCourses =
    typeof response?.total === 'number'
      ? response.total
      : courseItems.length;

  const totalPages =
    typeof response?.pages === 'number'
      ? Math.max(1, response.pages)
      : Math.max(
          1,
          Math.ceil(totalCourses / 12)
        );

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const params = new URLSearchParams(searchParams);

    if (searchInput.trim()) {
      params.set('search', searchInput.trim());
    } else {
      params.delete('search');
    }

    params.set('page', '1');

    setSearchParams(params);
  };

  const handleCategoryChange = (value: string) => {
    const params = new URLSearchParams(searchParams);

    if (value && value !== 'All Categories') {
      params.set('category', value);
    } else {
      params.delete('category');
    }

    params.set('page', '1');

    setSearchParams(params);
  };

  const handleLevelChange = (
    e: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const params = new URLSearchParams(searchParams);

    if (e.target.value) {
      params.set('level', e.target.value);
    } else {
      params.delete('level');
    }

    params.set('page', '1');

    setSearchParams(params);
  };

  const handlePageChange = (newPage: number) => {
    if (newPage < 1 || newPage > totalPages) {
      return;
    }

    const params = new URLSearchParams(searchParams);
    params.set('page', String(newPage));

    setSearchParams(params);
  };

  const clearFilters = () => {
    setSearchInput('');
    setSearchParams(new URLSearchParams());
  };

  /*
   * Loading
   */
  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
        <div className="max-w-7xl mx-auto px-6 py-16">
          <div className="animate-pulse space-y-6">
            <div className="h-10 bg-slate-200 dark:bg-slate-800 rounded w-1/3" />
            <div className="h-5 bg-slate-200 dark:bg-slate-800 rounded w-2/3" />

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-10">
              {[1, 2, 3, 4, 5, 6].map((item) => (
                <div
                  key={item}
                  className="h-72 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800"
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  /*
   * Error
   */
  if (isError) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
        <div className="max-w-3xl mx-auto px-6 py-20 text-center">
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-red-200 dark:border-red-900 p-10">
            <div className="text-5xl mb-4">⚠️</div>

            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
              Unable to load courses
            </h2>

            <p className="mt-3 text-slate-500 dark:text-slate-400">
              {(error as Error)?.message ||
                'Something went wrong while loading the course catalog.'}
            </p>

            <button
              onClick={() => refetch()}
              className="mt-6 px-5 py-3 rounded-lg bg-primary-600 text-white font-semibold hover:bg-primary-700"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  /*
   * Main page
   */
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">

      {/* Hero */}
      <div className="bg-primary-600 dark:bg-primary-900 text-white">
        <div className="max-w-7xl mx-auto px-6 py-12">

          <span className="inline-block text-sm font-semibold tracking-wide uppercase text-primary-100">
            Course Catalog
          </span>

          <h1 className="mt-2 text-3xl sm:text-4xl font-extrabold tracking-tight">
            Explore Enterprise Skills & Programs
          </h1>

          <p className="mt-3 text-lg text-primary-100 max-w-3xl">
            Browse high-impact, expert-led training programs curated for
            engineering, cloud, AI, and leadership excellence.
          </p>

          {/* Search */}
          <form
            onSubmit={handleSearchSubmit}
            className="mt-6 flex gap-2 max-w-xl"
          >
            <div className="relative flex-1">
              <input
                type="text"
                value={searchInput}
                onChange={(e) =>
                  setSearchInput(e.target.value)
                }
                placeholder="Search courses by title, topic, or keyword..."
                className="w-full pl-10 pr-4 py-3 rounded-lg text-gray-900 placeholder-gray-500 bg-white shadow focus:outline-none focus:ring-2 focus:ring-primary-400 text-sm"
              />

              <span className="absolute left-3 top-3.5 text-gray-400">
                🔍
              </span>
            </div>

            <button
              type="submit"
              className="px-5 py-3 bg-primary-500 hover:bg-primary-400 text-white font-semibold rounded-lg shadow transition-colors text-sm"
            >
              Search
            </button>
          </form>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">

        {/* Filters */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5">

          <div className="flex flex-col lg:flex-row lg:items-center gap-5">

            {/* Categories */}
            <div className="flex-1">
              <div className="flex flex-wrap gap-2">

                {CATEGORIES.map((item) => {
                  const active =
                    item === 'All Categories'
                      ? !category
                      : category === item;

                  return (
                    <button
                      key={item}
                      onClick={() =>
                        handleCategoryChange(item)
                      }
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                        active
                          ? 'bg-primary-600 text-white'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                      }`}
                    >
                      {item}
                    </button>
                  );
                })}

              </div>
            </div>

            {/* Level */}
            <div className="flex items-center gap-3">
              <label
                htmlFor="level"
                className="text-sm font-semibold text-slate-600 dark:text-slate-300"
              >
                Level:
              </label>

              <select
                id="level"
                value={level || ''}
                onChange={handleLevelChange}
                className="px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-700 dark:text-white text-sm"
              >
                {LEVELS.map((item) => (
                  <option
                    key={item.label}
                    value={item.value || ''}
                  >
                    {item.label}
                  </option>
                ))}
              </select>
            </div>

          </div>
        </div>

        {/* Result Count */}
        <div className="flex justify-between items-center mt-8 mb-5">

          <p className="text-sm text-slate-500 dark:text-slate-400">
            Showing{' '}
            <span className="font-semibold text-slate-900 dark:text-white">
              {courseItems.length}
            </span>{' '}
            of{' '}
            <span className="font-semibold text-slate-900 dark:text-white">
              {totalCourses}
            </span>{' '}
            courses
          </p>

          {(search || category || level) && (
            <button
              onClick={clearFilters}
              className="text-sm font-semibold text-primary-600 hover:text-primary-700"
            >
              Clear Filters
            </button>
          )}

        </div>

        {/* Empty State */}
        {courseItems.length === 0 ? (
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-dashed border-slate-300 dark:border-slate-700 p-16 text-center">

            <div className="text-5xl mb-5">
              📚
            </div>

            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              No courses found
            </h2>

            <p className="mt-2 text-slate-500 dark:text-slate-400">
              Try adjusting your search criteria or filters to find what
              you're looking for.
            </p>

            <button
              onClick={clearFilters}
              className="mt-6 px-5 py-3 rounded-lg bg-primary-600 text-white font-semibold hover:bg-primary-700"
            >
              Clear Filters
            </button>

          </div>
        ) : (

          /* Course Grid */
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">

            {courseItems.map((course) => (
              <CourseCard
                key={course.id}
                course={course}
              />
            ))}

          </div>
        )}

        {/* Pagination */}
        {courseItems.length > 0 && totalPages > 1 && (
          <div className="flex justify-center items-center gap-2 mt-10">

            <button
              disabled={page <= 1}
              onClick={() =>
                handlePageChange(page - 1)
              }
              className="px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-700 disabled:opacity-40 disabled:cursor-not-allowed bg-white dark:bg-slate-900"
            >
              Previous
            </button>

            {Array.from(
              { length: totalPages },
              (_, index) => index + 1
            ).map((pageNumber) => (
              <button
                key={pageNumber}
                onClick={() =>
                  handlePageChange(pageNumber)
                }
                className={`w-10 h-10 rounded-lg font-semibold ${
                  pageNumber === page
                    ? 'bg-primary-600 text-white'
                    : 'border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300'
                }`}
              >
                {pageNumber}
              </button>
            ))}

            <button
              disabled={page >= totalPages}
              onClick={() =>
                handlePageChange(page + 1)
              }
              className="px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-700 disabled:opacity-40 disabled:cursor-not-allowed bg-white dark:bg-slate-900"
            >
              Next
            </button>

          </div>
        )}

      </div>
    </div>
  );
};


/* =========================================================
   COURSE CARD
   ========================================================= */

interface CourseCardProps {
  course: Course;
}

const CourseCard: React.FC<CourseCardProps> = ({
  course,
}) => {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden hover:shadow-lg transition-shadow">

      {/* Thumbnail */}
      <div className="h-40 bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">

        {course.thumbnail_url ? (
          <img
            src={course.thumbnail_url}
            alt={course.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-6xl">
            📘
          </div>
        )}

      </div>

      {/* Details */}
      <div className="p-5">

        <div className="flex items-center justify-between gap-2 mb-3">

          <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300">
            {course.level || 'ALL LEVELS'}
          </span>

          {course.price !== undefined && (
            <span className="text-sm font-bold text-slate-900 dark:text-white">
              ₹{course.price}
            </span>
          )}

        </div>

        <h2 className="text-lg font-bold text-slate-900 dark:text-white line-clamp-2">
          {course.title}
        </h2>

        {course.description && (
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400 line-clamp-2">
            {course.description}
          </p>
        )}

        {/* Course Information */}
        <div className="mt-4 flex flex-wrap gap-3 text-xs text-slate-500 dark:text-slate-400">

          {course.module_count !== undefined && (
            <span>
              📚 {course.module_count} modules
            </span>
          )}

          {course.lesson_count !== undefined && (
            <span>
              🎥 {course.lesson_count} lessons
            </span>
          )}

        </div>

        {/* View Course */}
        <div className="mt-5">
          <Link
            to={`/courses/${course.id}`}
            className="w-full block text-center px-4 py-3 rounded-lg bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-semibold hover:bg-primary-100 dark:hover:bg-primary-900/50 transition"
          >
            View Course & Syllabus →
          </Link>
        </div>

      </div>
    </div>
  );
};

export default CourseCatalogPage;