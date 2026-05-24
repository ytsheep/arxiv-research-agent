"""MCP resources for local paper library."""

import os
from app.storage.file_manager import FileManager

file_manager = FileManager()

LIBRARY_RESOURCES: dict[str, dict] = {
    "library://paper/{arxiv_id}/report": {
        "name": "Paper Report",
        "description": "Chinese deep reading report (markdown) for a stored paper. Replace {arxiv_id} with the paper's arXiv ID.",
        "mimeType": "text/markdown",
    },
    "library://paper/{arxiv_id}/metadata": {
        "name": "Paper Metadata",
        "description": "Metadata JSON for a stored paper (title, authors, abstract, dates, URLs).",
        "mimeType": "application/json",
    },
    "library://paper/{arxiv_id}/parsed": {
        "name": "Parsed Full Text",
        "description": "Structured markdown of the parsed full text of a paper.",
        "mimeType": "text/markdown",
    },
}


def _is_library_paper_uri(uri: str) -> tuple[bool, str, str]:
    """Check if URI matches library://paper/{arxiv_id}/{file_type}.
    Returns (matched, arxiv_id, file_type)."""
    prefix = "library://paper/"
    if not uri.startswith(prefix):
        return False, "", ""
    rest = uri[len(prefix):]
    parts = rest.split("/", 1)
    if len(parts) != 2:
        return False, "", ""
    return True, parts[0], parts[1]


async def read_library_resource(uri: str) -> dict:
    matched, arxiv_id, file_type = _is_library_paper_uri(uri)
    if not matched:
        return {"contents": [{"uri": uri, "text": f"Unrecognized library URI: {uri}", "mimeType": "text/plain"}]}

    paper_dir = file_manager.get_paper_dir(arxiv_id)

    if file_type == "report":
        path = os.path.join(paper_dir, "report.md")
    elif file_type == "metadata":
        path = os.path.join(paper_dir, "metadata.json")
    elif file_type == "parsed":
        path = os.path.join(paper_dir, "parsed.md")
    else:
        return {"contents": [{"uri": uri, "text": f"Unknown file type: {file_type}", "mimeType": "text/plain"}]}

    if not os.path.exists(path):
        return {"contents": [{"uri": uri, "text": f"Resource not found: {file_type} for {arxiv_id}", "mimeType": "text/plain"}]}

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    mime = "application/json" if file_type == "metadata" else "text/markdown"
    return {"contents": [{"uri": uri, "text": content, "mimeType": mime}]}
