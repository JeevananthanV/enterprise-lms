# Enterprise LMS Course & Curriculum Data Generator
from app.models.lesson import LessonContentType
from app.models.quiz import QuestionType
from app.models.course import CourseLevel, CourseStatus

def build_lesson(title, slug, order, duration, desc, objectives, content_md, key_concepts, example_code, is_preview=False):
    objs = '\n'.join(f'- {o}' for o in objectives)
    kcs = '\n'.join(f'- {k}' for k in key_concepts)
    full_md = (
        f'# {title}\n\n'
        f'## Description\n{desc}\n\n'
        f'## Learning Objectives\n{objs}\n\n'
        f'## Detailed Lesson Content\n{content_md}\n\n'
        f'## Key Concepts\n{kcs}\n\n'
        f'## Practical Example\n{example_code}\n\n'
        f'## Completion Requirement\nComplete the lesson review, review the practical example, and achieve mastery before proceeding.'
    )
    return {
        'title': title,
        'slug': slug,
        'content_type': LessonContentType.TEXT,
        'duration_minutes': duration,
        'order_index': order,
        'is_free_preview': is_preview,
        'description': desc,
        'content': full_md,
    }

def build_question(order, text, correct, wrongs, explanation, points=1):
    answers = [{'answer_text': correct, 'is_correct': True, 'order_index': 1}]
    for idx, w in enumerate(wrongs, start=2):
        answers.append({'answer_text': w, 'is_correct': False, 'order_index': idx})
    return {
        'question_text': text,
        'question_type': QuestionType.SINGLE_CHOICE,
        'points': points,
        'order_index': order,
        'explanation': explanation,
        'answers': answers,
    }
