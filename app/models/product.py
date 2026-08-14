from typing import Optional
from sqlmodel import SQLModel, Field

# Esquema base: campos compartidos entre la tabla y los schemas Pydantic
class ProductBase(SQLModel):
    title: str = Field(index=True, min_length=1, max_length=150)
    description: Optional[str] = Field(default=None)
    price: float = Field(ge=0.0)
    stock: int = Field(default=0, ge=0)
    category_id: int = Field(foreign_key="category.id")

# Modelo principal para la Base de Datos
class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

# Schema Público para Lectura (respuesta al cliente)
class ProductPublic(ProductBase):
    id: int

# Schema para Crear (POST)
class ProductCreate(ProductBase):
    pass

# Schema para Actualizar (PATCH, todos los campos opcionales)
class ProductUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0.0)
    stock: Optional[int] = Field(default=None, ge=0)
    category_id: Optional[int] = None
