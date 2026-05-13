"""File manager for paper library storage. Placeholder for Phase 2."""

import os
from app.core.config import settings


class FileManager:
    def get_paper_dir(self, arxiv_id: str) -> str:
        return os.path.join(settings.paper_library_dir, "papers", arxiv_id)

    def ensure_paper_dir(self, arxiv_id: str) -> str:
        path = self.get_paper_dir(arxiv_id)
        os.makedirs(path, exist_ok=True)
        return path

    def paper_exists(self, arxiv_id: str) -> bool:
        path = self.get_paper_dir(arxiv_id)
        return os.path.isdir(path)
