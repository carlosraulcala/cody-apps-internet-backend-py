from typing import Optional
from sqlmodel import SQLModel, Field

# Esquema base: campos compartidos entre la tabla y los schemas Pydantic
class ReviewBase(SQLModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=1, max_length=1000)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")

# Modelo principal para la Base de Datos
class Review(ReviewBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

# Schema Público para Lectura (respuesta al cliente)
class ReviewPublic(ReviewBase):
    id: int

# Schema de Input del Cliente (body del POST)
# SEGURIDAD: nunca expone user_id ni product_id al cliente.
class ReviewIn(SQLModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=1, max_length=1000)

# Schema para Crear (uso interno: service layer)
class ReviewCreate(ReviewBase):
    pass
