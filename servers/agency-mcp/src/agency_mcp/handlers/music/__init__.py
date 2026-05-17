from typing import Any

from agency_mcp.handlers.music import (
    core,
    audio,
    mixing,
    sheet_music,
    video,
    lyrics_analysis,
    text_analysis,
    album_ops,
    gates,
    database,
    ideas,
    streaming,
    content,
    health,
    maintenance,
    promo,
)

def register_music_handlers(mcp: Any) -> None:
    """Register all music domain handlers."""
    core.register(mcp)
    audio.register(mcp)
    mixing.register(mcp)
    sheet_music.register(mcp)
    video.register(mcp)
    lyrics_analysis.register(mcp)
    text_analysis.register(mcp)
    album_ops.register(mcp)
    gates.register(mcp)
    database.register(mcp)
    ideas.register(mcp)
    streaming.register(mcp)
    content.register(mcp)
    health.register(mcp)
    maintenance.register(mcp)
    promo.register(mcp)
