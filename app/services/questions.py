from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import Permissions, ensure_default_or_permission, ensure_permission
from app.core.security import CurrentUser
from app.models.questions import Question
from app.models.question_versions import QuestionVersion
from app.models.test_questions import TestQuestion


# ---------------- Вспомогательные функции ----------------

def _get_question_or_404(db: Session, question_id: int) -> Question:
    question = (
        db.query(Question)
        .filter(Question.id == question_id, Question.is_deleted == False)  # noqa: E712
        .first()
    )
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return question


def _get_question_version_or_404(db: Session, question_id: int, version: int) -> QuestionVersion:
    qv = (
        db.query(QuestionVersion)
        .filter(QuestionVersion.question_id == question_id, QuestionVersion.version == version)
        .first()
    )
    if not qv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question version not found")
    return qv


def _get_latest_question_version(db: Session, question_id: int) -> QuestionVersion:
    qv = (
        db.query(QuestionVersion)
        .filter(QuestionVersion.question_id == question_id)
        .order_by(QuestionVersion.version.desc())
        .first()
    )
    if not qv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No versions for this question")
    return qv


def _is_question_author(question: Question, current_user: CurrentUser) -> bool:
    return question.author_id == current_user.id


def _serialize_latest(question: Question, version: QuestionVersion) -> Dict[str, Any]:
    # Для списка /questions по ТЗ нужно отдавать последнюю версию + author_id.
    return {
        "id": version.id,  # id версии (question_versions.id)
        "question_id": question.id,
        "version": version.version,
        "author_id": question.author_id,
        "title": version.title,
        "text": version.text,
        "options": version.options,
        "correct_index": version.correct_index,
    }


# ---------------- Бизнес-логика ----------------

def list_questions(db: Session, current_user: CurrentUser) -> List[Dict[str, Any]]:
    """
    GET /questions — список вопросов (только последняя версия).

    Доступ:
      - по умолчанию: только свои вопросы
      - permission: quest:list:read — видеть вопросы других авторов
    """
    questions = db.query(Question).filter(Question.is_deleted == False).all()  # noqa: E712
    result: List[Dict[str, Any]] = []

    for q in questions:
        default_allowed = _is_question_author(q, current_user)
        try:
            ensure_default_or_permission(default_allowed, current_user.permissions, Permissions.QUEST_LIST_READ)
        except HTTPException:
            continue

        latest = _get_latest_question_version(db, q.id)
        result.append(_serialize_latest(q, latest))

    return result


def get_question(db: Session, question_id: int, current_user: CurrentUser) -> QuestionVersion:
    """
    GET /questions/{id} — последняя версия вопроса.
    """
    question = _get_question_or_404(db, question_id)
    default_allowed = _is_question_author(question, current_user)
    ensure_default_or_permission(default_allowed, current_user.permissions, Permissions.QUEST_READ)

    return _get_latest_question_version(db, question_id)


def get_question_version(db: Session, question_id: int, version: int, current_user: CurrentUser) -> QuestionVersion:
    """
    GET /questions/{id}/versions/{version} — конкретная версия.
    """
    question = _get_question_or_404(db, question_id)
    default_allowed = _is_question_author(question, current_user)
    ensure_default_or_permission(default_allowed, current_user.permissions, Permissions.QUEST_READ)

    return _get_question_version_or_404(db, question_id, version)


def create_question(db: Session, data, current_user: CurrentUser) -> QuestionVersion:
    """
    POST /questions — создать вопрос и версию 1.
    По ТЗ требуется permission quest:create.
    """
    ensure_permission(
        current_user.permissions,
        Permissions.QUEST_CREATE,
        "You do not have permission to create questions",
    )

    question = Question(author_id=current_user.id, is_deleted=False)
    db.add(question)
    db.commit()
    db.refresh(question)

    v1 = QuestionVersion(
        question_id=question.id,
        version=1,
        title=data.title,
        text=data.text,
        options=data.options,
        correct_index=data.correct_index,
    )
    db.add(v1)

    # Опционально: если передали test_id — добавить вопрос в тест в конец списка
    test_id: Optional[int] = getattr(data, "test_id", None)
    if test_id:
        last = (
            db.query(TestQuestion)
            .filter(TestQuestion.test_id == test_id)
            .order_by(TestQuestion.position.desc())
            .first()
        )
        position = (last.position + 1) if last else 0
        db.add(TestQuestion(test_id=test_id, question_id=question.id, position=position))

    db.commit()
    db.refresh(v1)
    return v1


def create_question_version(db: Session, question_id: int, data, current_user: CurrentUser) -> QuestionVersion:
    """
    POST /questions/{id}/versions — создать новую версию.
    """
    question = _get_question_or_404(db, question_id)
    default_allowed = _is_question_author(question, current_user)
    ensure_default_or_permission(default_allowed, current_user.permissions, Permissions.QUEST_UPDATE)

    last = _get_latest_question_version(db, question_id)
    next_version = last.version + 1

    qv = QuestionVersion(
        question_id=question.id,
        version=next_version,
        title=data.title,
        text=data.text,
        options=data.options,
        correct_index=data.correct_index,
    )
    db.add(qv)
    db.commit()
    db.refresh(qv)
    return qv


from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import Permissions, ensure_default_or_permission
from app.core.security import CurrentUser
from app.models.questions import Question


def delete_question(db: Session, question_id: int, current_user: CurrentUser) -> None:
    """
    DELETE /questions/{id}

    Мягкое удаление: даже если вопрос привязан к тестам, мы не ломаем историю.
    Вопрос исчезает из /questions и не доступен для новых операций,
    но старые тесты/попытки сохраняют ссылочную целостность.
    """
    question = (
        db.query(Question)
        .filter(Question.id == question_id, Question.is_deleted == False)  # noqa: E712
        .first()
    )
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    default_allowed = question.author_id == current_user.id
    ensure_default_or_permission(default_allowed, current_user.permissions, Permissions.QUEST_DEL)

    question.is_deleted = True
    db.add(question)
    db.commit()
