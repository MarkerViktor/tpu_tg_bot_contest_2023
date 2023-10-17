from pathlib import Path


class TextLoader:
    def __init__(self, static_folder: Path) -> None:
        if not static_folder.is_dir():
            raise NotADirectoryError(f"{static_folder} is not a directory")

        self._static_folder = static_folder

    def __getitem__(self, code: str) -> str:
        relative_path = "/".join(code.split('.'))
        path = self._static_folder / f'{relative_path}.txt'

        try:
            with path.open(mode="r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
