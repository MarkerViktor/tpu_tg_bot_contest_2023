from pathlib import Path

from aiogram.types import InputFile, FSInputFile
from databases import Database


class StaticLoader:
    """Загрузчик статических данных."""

    def __init__(self, db: Database, default_text: str, default_image_path: str, static_root: Path) -> None:
        self._db = db
        self._static_root = static_root
        self._default_text = default_text
        self._default_image_path = default_image_path

    async def get_text(self, code: str) -> str:
        """Получить текст по коду."""
        stmt = "select t.text from texts as t where t.code = :code"
        text = await self._db.fetch_val(stmt, {"code": code})
        if text is None:
            return self._default_text
        return text

    async def get_file(self, code: str) -> InputFile:
        """Получить файл по коду."""
        stmt = "select i.path from files as i where i.code = :code"
        image_path: str = await self._db.fetch_val(stmt, {"code": code})
        if image_path is None:
            return InputFile(self._default_image_path)

        file_path = self._static_root / image_path
        return FSInputFile(file_path.absolute(), filename=file_path.name)
