import os
from contextlib import contextmanager

import pyodbc
from dotenv import load_dotenv


# Carrega variáveis do arquivo .env, se ele existir.
load_dotenv()


def get_sql_server_driver() -> str:
    """
    Tenta descobrir um driver ODBC válido para SQL Server.

    Se o driver informado no .env existir na máquina, ele será usado.
    Caso contrário, tentamos alguns nomes comuns.
    """
    configured_driver = os.getenv("DB_DRIVER", "").strip()
    available_drivers = pyodbc.drivers()

    if configured_driver and configured_driver in available_drivers:
        return configured_driver

    common_drivers = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "SQL Server",
    ]

    for driver in common_drivers:
        if driver in available_drivers:
            return driver

    raise RuntimeError(
        "Nenhum driver ODBC para SQL Server foi encontrado. "
        "Instale o ODBC Driver 17 ou 18."
    )


def build_connection_string() -> str:
    """
    Monta a string de conexão com base nas variáveis de ambiente.
    """
    driver = get_sql_server_driver()
    server = os.getenv("DB_SERVER", "localhost")
    database = os.getenv("DB_DATABASE", "")
    trusted_connection = os.getenv("DB_TRUSTED_CONNECTION", "yes").lower()
    trust_server_certificate = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")
    username = os.getenv("DB_USERNAME", "")
    password = os.getenv("DB_PASSWORD", "")

    if not database:
        raise RuntimeError("A variável DB_DATABASE precisa estar preenchida.")

    connection_parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        f"DATABASE={database}",
        f"TrustServerCertificate={trust_server_certificate}",
    ]

    # Se estiver usando autenticação do Windows, não precisa de usuário e senha.
    if trusted_connection == "yes":
        connection_parts.append("Trusted_Connection=yes")
    else:
        connection_parts.append(f"UID={username}")
        connection_parts.append(f"PWD={password}")

    return ";".join(connection_parts)


@contextmanager
def get_connection():
    """
    Abre e fecha a conexão automaticamente.

    Usar com 'with' deixa o código mais limpo e evita esquecer de fechar a conexão.
    """
    connection = pyodbc.connect(build_connection_string())
    try:
        yield connection
    finally:
        connection.close()
