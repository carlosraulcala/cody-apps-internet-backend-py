from typing import Any
from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep, CurrentUser
from app.models.cart_item import CartItemIn, CartItemCreate, CartItemPublic, CartItemUpdate
from app.services import cart_service, product_service

router = APIRouter()

@router.post("/", response_model=CartItemPublic, status_code=201)
def add_to_cart(
    item_in: CartItemIn,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Agrega un producto al carrito del usuario autenticado.
    - `product_id` viene del body.
    - `user_id` se extrae del token JWT via `current_user.id` (nunca del body).
    """
    # Verificar que el producto existe
    product = product_service.get_product_by_id(session=session, product_id=item_in.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Construir el schema interno inyectando user_id de forma segura
    item_data = CartItemCreate(
        product_id=item_in.product_id,
        quantity=item_in.quantity,
        user_id=current_user.id,  # ← del token JWT, nunca del body
    )
    return cart_service.add_item(session=session, item_in=item_data)

@router.get("/", response_model=list[CartItemPublic])
def read_cart(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Lista todos los items del carrito del usuario autenticado."""
    return cart_service.get_cart_by_user(session=session, user_id=current_user.id, skip=skip, limit=limit)

@router.patch("/{item_id}", response_model=CartItemPublic)
def update_cart_item(
    item_id: int,
    item_in: CartItemUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Actualiza la cantidad de un item del carrito.
    Retorna 404 si no existe y 403 si el item no pertenece al usuario.
    """
    item = cart_service.get_item_by_id(session=session, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado en el carrito")
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este item")
    return cart_service.update_item(session=session, db_item=item, item_in=item_in)

@router.delete("/{item_id}", status_code=200)
def remove_from_cart(
    item_id: int,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Elimina un item del carrito.
    Retorna 404 si no existe y 403 si el item no pertenece al usuario.
    """
    item = cart_service.get_item_by_id(session=session, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado en el carrito")
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este item")
    cart_service.remove_item(session=session, db_item=item)
    return {"message": f"Item {item_id} eliminado del carrito exitosamente"}

@router.delete("/", status_code=200)
def clear_cart(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Vacía todo el carrito del usuario autenticado."""
    count = cart_service.clear_cart(session=session, user_id=current_user.id)
    return {"message": f"Carrito vaciado. {count} item(s) eliminado(s)"}
