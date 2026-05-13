def mask_sensitive(text: str, keep_chars: int = 4) -> str:
    """Mask sensitive text, keeping only the first and last few characters."""
    if not text or len(text) <= keep_chars * 2:
        return "***"
    return text[:keep_chars] + "***" + text[-keep_chars:]
