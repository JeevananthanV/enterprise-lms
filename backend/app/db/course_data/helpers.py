from app.models.lesson import LessonContentType
from app.models.quiz import QuestionType

def make_lesson(
    title: str,
    slug: str,
    order_index: int,
    duration_minutes: int,
    description: str,
    objectives: list,
    content_body: str,
    key_concepts: list,
    practical_example: str,
    completion_req: str,
    is_free_preview: bool = False,
):
    obj_md = '\n'.join(f'- {o}' for o in objectives)
    kc_md = '\n'.join(f'- {k}' for k in key_concepts)
    
    full_markdown = (
        f'# {title}\n\n'
        f'## Description\n{description}\n\n'
        f'## Learning Objectives\n{obj_md}\n\n'
        f'## Detailed Lesson Content\n{content_body}\n\n'
        f'## Key Concepts\n{kc_md}\n\n'
        f'## Practical Example\n{practical_example}\n\n'
        f'## Completion Requirement\n{completion_req}'
    )

    return {
        'title': title,
        'slug': slug,
        'content_type': LessonContentType.TEXT,
        'duration_minutes': duration_minutes,
        'order_index': order_index,
        'is_free_preview': is_free_preview,
        'description': description,
        'content': full_markdown,
    }

def make_question(order_index: int, text: str, correct: str, wrongs: list, explanation: str, points: int = 1):
    answers = [{'answer_text': correct, 'is_correct': True, 'order_index': 1}]
    for idx, w in enumerate(wrongs, start=2):
        answers.append({'answer_text': w, 'is_correct': False, 'order_index': idx})
    return {
        'question_text': text,
        'question_type': QuestionType.SINGLE_CHOICE,
        'points': points,
        'order_index': order_index,
        'explanation': explanation,
        'answers': answers,
    }
