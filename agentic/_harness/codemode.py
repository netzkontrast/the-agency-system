def wrap_for_codemode(handler_func, tool_name: str, codemode_set: set[str]):
    """If tool_name in codemode_set, set prefers_codemode=True on the response."""

    def wrapped(*args, **kwargs):
        result = handler_func(*args, **kwargs)
        if tool_name in codemode_set:
            if isinstance(result, dict):
                result["prefers_codemode"] = True
        return result

    return wrapped
