try:
    from fastapi import APIRouter, HTTPException, status
except Exception:  # pragma: no cover - fallback for environments without FastAPI
    # Provide minimal stubs so linters/IDEs won't error when FastAPI isn't installed.
    from types import SimpleNamespace

    def APIRouter(*args, **kwargs):
        return None

    class HTTPException(Exception):
        def __init__(self, status_code: int = None, detail: str | None = None):
            self.status_code = status_code
            self.detail = detail

    status = SimpleNamespace(HTTP_201_CREATED=201, HTTP_404_NOT_FOUND=404)

from database import get_connection
from schemas import AlunoCreate, AlunoResponse, AlunoUpdate, MessageResponse


router = APIRouter(prefix="/alunos", tags=["Alunos"])


def row_to_dict(row) -> dict:
    """
    Converte o retorno do pyodbc para um dicionário simples.
    """
    return {"id": row.id, "nome": row.nome}


@router.get("/", response_model=list[AlunoResponse])
def listar_alunos():
    """
    Retorna todos os alunos cadastrados.
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, nome FROM dbo.Aluno ORDER BY id")
        rows = cursor.fetchall()

    return [row_to_dict(row) for row in rows]


@router.get("/{aluno_id}", response_model=AlunoResponse)
def buscar_aluno(aluno_id: int):
    """
    Busca um aluno pelo ID.
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, nome FROM dbo.Aluno WHERE id = ?",
            aluno_id,
        )
        row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado.",
        )

    return row_to_dict(row)


@router.post("/", response_model=AlunoResponse, status_code=status.HTTP_201_CREATED)
def criar_aluno(aluno: AlunoCreate):
    """
    Cria um novo aluno na tabela dbo.Aluno.

    Usamos OUTPUT INSERTED para devolver o registro criado sem precisar fazer
    outra consulta depois do INSERT.
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO dbo.Aluno (nome)
            OUTPUT INSERTED.id, INSERTED.nome
            VALUES (?)
            """,
            aluno.nome,
        )
        row = cursor.fetchone()
        connection.commit()

    return row_to_dict(row)


@router.put("/{aluno_id}", response_model=AlunoResponse)
def atualizar_aluno(aluno_id: int, aluno: AlunoUpdate):
    """
    Atualiza o nome de um aluno existente.
    """
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM dbo.Aluno WHERE id = ?", aluno_id)
        existing_row = cursor.fetchone()

        if existing_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aluno não encontrado.",
            )

        cursor.execute(
            """
            UPDATE dbo.Aluno
            SET nome = ?
            WHERE id = ?
            """,
            aluno.nome,
            aluno_id,
        )
        connection.commit()

        cursor.execute(
            "SELECT id, nome FROM dbo.Aluno WHERE id = ?",
            aluno_id,
        )
        updated_row = cursor.fetchone()

    return row_to_dict(updated_row)


@router.delete("/{aluno_id}", response_model=MessageResponse)
def excluir_aluno(aluno_id: int):
    """
    Remove um aluno pelo ID.
    """
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM dbo.Aluno WHERE id = ?", aluno_id)
        existing_row = cursor.fetchone()

        if existing_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aluno não encontrado.",
            )

        cursor.execute("DELETE FROM dbo.Aluno WHERE id = ?", aluno_id)
        connection.commit()

    return {"message": "Aluno excluído com sucesso."}
