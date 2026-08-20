import os
import json
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI

from app.api.deps import SessionDep, CurrentUser
from app.models.task import TaskCreate, TaskPublic, TaskUpdate
from app.services import task_service


router = APIRouter()


class PromptRequest(BaseModel):
    prompt: str


client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)


@router.post("/ai-suggest")
def suggest_task(request: PromptRequest):
    """
    Recibe un texto en lenguaje natural y la IA extrae
    el título y la descripción.
    """

    system_prompt = """
    Eres un asistente de productividad. El usuario te dará una frase
    en lenguaje natural sobre algo que tiene que hacer.

    Tu trabajo es extraer un 'title' corto y conciso,
    y una 'description' más detallada.

    Debes responder EXCLUSIVAMENTE en formato JSON válido,
    sin Markdown, con esta estructura exacta:

    {"title": "string", "description": "string"}
    """

    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.prompt}
        ],
        temperature=0.3,
    )

    ai_result = json.loads(
        response.choices[0].message.content
    )

    return ai_result


@router.get("/", response_model=list[TaskPublic])
def leer_tareas(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100
) -> Any:
    return task_service.get_tasks(
        session=session,
        skip=skip,
        limit=limit
    )


@router.post("/", response_model=TaskPublic)
def crear_tarea(
    session: SessionDep,
    current_user: CurrentUser,
    task_in: TaskCreate
) -> Any:
    return task_service.create_task(
        session=session,
        task_in=task_in
    )


@router.post("/ai", response_model=TaskPublic)
def crear_tarea_con_ia(
    session: SessionDep,
    current_user: CurrentUser,
    task_in: TaskCreate
) -> Any:
    return task_service.create_task_ai(
        session=session,
        task_in=task_in
    )


@router.patch("/{task_id}", response_model=TaskPublic)
def actualizar_tarea(
    session: SessionDep,
    current_user: CurrentUser,
    task_id: int,
    task_in: TaskUpdate
) -> Any:
    task_db = task_service.update_task(
        session=session,
        task_id=task_id,
        task_in=task_in
    )

    if not task_db:
        raise HTTPException(
            status_code=404,
            detail="Tarea no encontrada ❌"
        )

    return task_db


@router.delete("/{task_id}")
def borrar_tarea(
    session: SessionDep,
    current_user: CurrentUser,
    task_id: int
) -> dict:

    deleted = task_service.delete_task(
        session=session,
        task_id=task_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Tarea no encontrada ❌"
        )

    return {
        "mensaje": f"Tarea {task_id} borrada exitosamente de la base de datos"
    }