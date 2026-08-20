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


# ==============================
# CONFIGURACIÓN DE ZHIPU AI
# ==============================

client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)


# ==============================
# MODELO PARA LA IA
# ==============================

class PromptRequest(BaseModel):
    prompt: str


# ==============================
# SUGERENCIA DE TAREA CON IA
# ==============================

@router.post("/ai-suggest")
def suggest_task(request: PromptRequest):
    """
    Recibe una descripción de una tarea en lenguaje natural
    y devuelve un título y una descripción generados por IA.
    """

    system_prompt = """
    Eres un asistente de productividad.

    El usuario te dará una frase en lenguaje natural
    describiendo algo que necesita hacer.

    Tu trabajo es extraer:

    1. title:
       Un título corto, claro y conciso.

    2. description:
       Una descripción más detallada de la tarea.

    Debes responder EXCLUSIVAMENTE con JSON válido,
    sin Markdown, sin ``` y sin texto adicional.

    Utiliza exactamente esta estructura:

    {
        "title": "string",
        "description": "string"
    }
    """

    try:

        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": request.prompt
                }
            ],
            temperature=0.3,
        )

        content = response.choices[0].message.content

        if not content:
            raise HTTPException(
                status_code=500,
                detail="La IA no devolvió ningún resultado"
            )

        ai_result = json.loads(content)

        return ai_result

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="La IA no devolvió un JSON válido"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar la IA: {str(e)}"
        )


# ==============================
# OBTENER TAREAS
# ==============================

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


# ==============================
# CREAR TAREA
# ==============================

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


# ==============================
# CREAR TAREA CON IA
# ==============================

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


# ==============================
# ACTUALIZAR TAREA
# ==============================

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


# ==============================
# ELIMINAR TAREA
# ==============================

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