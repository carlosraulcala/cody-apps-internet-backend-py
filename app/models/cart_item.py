from typing import Optional
from sqlmodel import SQLModel, Field

# Esquema base: campos compartidos entre la tabla y los schemas Pydantic
class CartItemBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(default=1, ge=1)

# Modelo principal para la Base de Datos
class CartItem(CartItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

# Schema Público para Lectura (respuesta al cliente)
class CartItemPublic(CartItemBase):
    id: int

# Schema de Input del Cliente (body del POST)
# SEGURIDAD: nunca expone user_id al cliente.
class CartItemIn(SQLModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)

# Schema para Crear (uso interno: service layer)
class CartItemCreate(CartItemBase):
    pass

# Schema para Actualizar cantidad (PATCH)
class CartItemUpdate(SQLModel):
    quantity: int = Field(ge=1)
