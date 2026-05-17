# Sheet Music Rename Reference

The bitwize source directory `tools/sheet-music/` has been renamed to `tools/sheet_music/` during the porting process. This is because Python module names cannot contain hyphens.

This change means that any dynamic loader call sites in the handlers (which will be ported in spec 004 redo) that previously referenced `tools.sheet-music.*` will need to be adjusted to `agency_mcp.tools.sheet_music.*`.
