from typing import Any
from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep, CurrentUser
from app.models.review import ReviewIn, ReviewCreate, ReviewPublic
from app.services import review_service, product_service

router = APIRouter()

@router.post("/{product_id}/reviews", response_model=ReviewPublic, status_code=201)
def create_review(
    product_id: int,
    review_in: ReviewIn,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Crea una review para un producto.
    - `product_id` viene de la URL (no del body).
    - `user_id` se extrae del token JWT via `current_user.id` (nunca del body).
    """
    # Verificar que el producto existe
    product = product_service.get_product_by_id(session=session, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Construir el schema interno inyectando user_id y product_id de forma segura
    review_data = ReviewCreate(
        rating=review_in.rating,
        comment=review_in.comment,
        user_id=current_user.id,   # ← del token JWT, nunca del body
        product_id=product_id,     # ← de la URL, nunca del body
    )
    return review_service.create_review(session=session, review_in=review_data)

@router.get("/{product_id}/reviews", response_model=list[ReviewPublic])
def read_reviews_by_product(
    product_id: int,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Lista todas las reviews de un producto. Retorna 404 si el producto no existe."""
    product = product_service.get_product_by_id(session=session, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return review_service.get_reviews_by_product(session=session, product_id=product_id, skip=skip, limit=limit)

@router.delete("/{product_id}/reviews/{review_id}", status_code=200)
def delete_review(
    product_id: int,
    review_id: int,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Elimina una review. Solo el autor puede eliminarla.
    Retorna 404 si no existe y 403 si el usuario no es el autor.
    """
    review = review_service.get_review_by_id(session=session, review_id=review_id)
    if not review or review.product_id != product_id:
        raise HTTPException(status_code=404, detail="Review no encontrada")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta review")
    review_service.delete_review(session=session, db_item=review)
    return {"message": f"Review {review_id} eliminada exitosamente"}
