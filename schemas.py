from pydantic import BaseModel, Field


class AlunoBase(BaseModel):
    # O nome foi limitado a 255 porque é o tamanho da coluna na tabela.
    nome: str = Field(..., max_length=255, examples=["Maria da Silva"])


class AlunoCreate(AlunoBase):
    # Nesta aula, para criar um aluno, só precisamos do nome.
    pass


class AlunoUpdate(AlunoBase):
    # Para atualizar, também vamos receber apenas o nome.
    pass


class AlunoResponse(AlunoBase):
    id: int


class MessageResponse(BaseModel):
    message: str