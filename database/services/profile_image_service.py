"""
Serviço de gerenciamento de imagens de perfil de usuários.

Salva a imagem em disco no diretório ``src/img/profiles/``
usando o e-mail do usuário como nome do arquivo (único).
No banco de dados armazena apenas o nome do arquivo.
"""

from __future__ import annotations

import os
from pathlib import Path


# Diretório de imagens de perfil
_PROFILE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "src", "img", "profiles",
)


def _ensure_profile_dir() -> str:
    """Garante que o diretório de perfis exista."""
    os.makedirs(_PROFILE_DIR, exist_ok=True)
    return _PROFILE_DIR


def save_profile_image(
    email: str,
    image_bytes: bytes,
    extension: str = ".png",
) -> str:
    """
    Salva imagem de perfil em disco com o e-mail como nome.

    Args:
        email: E-mail do usuário (usado como nome do arquivo).
        image_bytes: Conteúdo binário da imagem.
        extension: Extensão do arquivo (ex.: .png, .jpg).

    Returns:
        Nome do arquivo salvo (ex.: ``usuario@email.com.png``).
    """
    _ensure_profile_dir()
    if not extension.startswith("."):
        extension = f".{extension}"
    filename = f"{email}{extension}"
    filepath = os.path.join(_PROFILE_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(image_bytes)
    return filename


def get_profile_image_path(filename: str) -> str | None:
    """
    Retorna o caminho absoluto da imagem de perfil ou None
    se o arquivo não existir.
    """
    filepath = os.path.join(_PROFILE_DIR, filename)
    if os.path.exists(filepath):
        return filepath
    return None


def delete_profile_image(filename: str) -> bool:
    """Remove a imagem de perfil do disco."""
    filepath = os.path.join(_PROFILE_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def list_profile_images() -> list[str]:
    """Lista todos os arquivos de imagem no diretório de perfis."""
    _ensure_profile_dir()
    return [
        f for f in os.listdir(_PROFILE_DIR)
        if os.path.isfile(os.path.join(_PROFILE_DIR, f))
    ]
