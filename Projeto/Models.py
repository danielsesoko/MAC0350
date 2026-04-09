from sqlmodel import SQLModel, Field, Relationship

class Local(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    itens: list["Item"] = Relationship(back_populates="local")

class Categoria(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field
    itens: list["Item"] = Relationship(back_populates="categoria")

class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    cor: str
    nome_pessoa: str | None = None
    local_encontrado: str
    status: str = Field(default="Aberto")
    
    local_id: int = Field(foreign_key="local.id")
    local: Local | None = Relationship(back_populates="itens")

    categoria_id: int = Field(foreign_key="categoria.id")
    categoria: Categoria | None = Relationship(back_populates="itens")
