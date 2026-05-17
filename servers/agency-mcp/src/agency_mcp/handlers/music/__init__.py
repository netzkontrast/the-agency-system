from typing import Any
from . import core, album_ops, gates, database, ideas, streaming, content, health, maintenance, promo, lyrics_analysis, text_analysis, audio, mixing, sheet_music, video

def register_music_handlers(mcp: Any) -> None:
    core.register(mcp)
    album_ops.register(mcp)
    gates.register(mcp)
    database.register(mcp)
    ideas.register(mcp)
    streaming.register(mcp)
    content.register(mcp)
    health.register(mcp)
    maintenance.register(mcp)
    promo.register(mcp)
    lyrics_analysis.register(mcp)
    text_analysis.register(mcp)
    audio.register(mcp)
    mixing.register(mcp)
    sheet_music.register(mcp)
    video.register(mcp)
