import json
from functools import wraps
from typing import Any, Callable

from agency_mcp.lib.codemode.views import BODY_PREVIEW_CHARS, View


def _truncate_body_fields(data: dict[str, Any]) -> dict[str, Any]:
    """Truncates long text fields and sets truncated_marker if truncated."""
    fields_to_truncate = {"body", "content", "lyrics", "description"}
    truncated = False

    result = data.copy()

    for field in fields_to_truncate:
        if field in result and isinstance(result[field], str):
            if len(result[field]) > BODY_PREVIEW_CHARS:
                result[field] = result[field][:BODY_PREVIEW_CHARS]
                truncated = True

    if truncated:
        result["truncated_marker"] = True

    return result


def project(obj: Any, view: str | View = View.summary, fields: list[str] | None = None) -> dict[str, Any]:
    """Projects an object to a dictionary based on view and fields.

    Args:
        obj: A dict or Pydantic model.
        view: The view tier (id, summary, preview, full).
        fields: Explicit fields to include (overrides view).
    """
    if hasattr(obj, "model_dump"):
        data = obj.model_dump()
    elif hasattr(obj, "dict"):
        data = obj.dict()
    elif isinstance(obj, dict):
        data = obj
    elif isinstance(obj, str):
        try:
            data = json.loads(obj)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON string in project()"}
    else:
        raise ValueError(f"Cannot project object of type {type(obj)}")

    if "error" in data and len(data) == 1:
         return data

    if fields is not None:
        return {k: v for k, v in data.items() if k in fields}

    if view == View.id:
        if "id" in data:
            return {"id": data["id"]}
        return {}

    elif view == View.summary:
        summary_keys = {"id", "name", "state", "title", "status"} # Added title, status for better summary on other types
        return {k: v for k, v in data.items() if k in summary_keys}

    elif view == View.preview:
        summary_keys = {"id", "name", "state", "title", "status", "body", "content", "lyrics", "description"}
        preview_data = {k: v for k, v in data.items() if k in summary_keys}
        return _truncate_body_fields(preview_data)

    elif view == View.full:
        return data

    return data


def apply_view(func: Callable) -> Callable:
    """Decorator to apply projection to the result of an MCP tool."""
    import inspect

    # We need to preserve the asyncness of the original function
    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, view: View = View.summary, fields: list[str] | None = None, **kwargs) -> Any:
            result = await func(*args, **kwargs)
            return _handle_result(result, view, fields)

        # Add the new parameters to the signature
        sig = inspect.signature(func)
        params = list(sig.parameters.values())

        view_param = inspect.Parameter(
            "view",
            inspect.Parameter.KEYWORD_ONLY,
            default=View.summary.value,
            annotation=str
        )
        fields_param = inspect.Parameter(
            "fields",
            inspect.Parameter.KEYWORD_ONLY,
            default=None,
            annotation=list[str] | None
        )

        # Remove *args and **kwargs if present and put them back at the end
        regular_params = [p for p in params if p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)]
        new_params = regular_params + [view_param, fields_param]

        async_wrapper.__signature__ = sig.replace(parameters=new_params) # type: ignore

        # Pydantic (used by FastMCP) also checks __annotations__ directly
        if hasattr(async_wrapper, '__annotations__'):
            async_wrapper.__annotations__['view'] = str
            async_wrapper.__annotations__['fields'] = list[str] | None

        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, view: View = View.summary, fields: list[str] | None = None, **kwargs) -> Any:
            result = func(*args, **kwargs)
            return _handle_result(result, view, fields)

        # Add the new parameters to the signature
        sig = inspect.signature(func)
        params = list(sig.parameters.values())

        view_param = inspect.Parameter(
            "view",
            inspect.Parameter.KEYWORD_ONLY,
            default=View.summary.value,
            annotation=str
        )
        fields_param = inspect.Parameter(
            "fields",
            inspect.Parameter.KEYWORD_ONLY,
            default=None,
            annotation=list[str] | None
        )

        regular_params = [p for p in params if p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)]
        new_params = regular_params + [view_param, fields_param]

        sync_wrapper.__signature__ = sig.replace(parameters=new_params) # type: ignore

        # Pydantic (used by FastMCP) also checks __annotations__ directly
        if hasattr(sync_wrapper, '__annotations__'):
            sync_wrapper.__annotations__['view'] = str
            sync_wrapper.__annotations__['fields'] = list[str] | None

        return sync_wrapper

def _handle_result(result: Any, view: View, fields: list[str] | None) -> Any:
    """Helper to apply projection to the result, handling strings and dicts."""
    if isinstance(result, str):
        try:
            data = json.loads(result)
        except json.JSONDecodeError:
            return result # Not JSON, return as is

        # If the result has an 'error' key, don't project it away
        if isinstance(data, dict) and "error" in data:
            return result

        # If the result is a dict, it might be an envelope
        if isinstance(data, dict):
            # Check if it has a common envelope key structure, or if it IS the object.
            # Usually, envelope structures will have top-level keys like "data", "sessions", "albums", "tracks", "skill"
            # And primitive keys like "success", "error", "warnings", "count"
            has_common_envelope_keys = any(k in ["success", "error", "warnings", "found", "ok", "next_cursor", "count", "data", "sessions", "albums", "tracks", "skill", "activities", "track", "album", "session"] for k in data.keys())

            if has_common_envelope_keys:
                new_data = {}
                for k, v in data.items():
                    if isinstance(v, list):
                        new_data[k] = [project(item, view, fields) for item in v]
                    elif isinstance(v, dict):
                        new_data[k] = project(v, view, fields)
                    else:
                        new_data[k] = v
                return json.dumps(new_data)
            else:
                return json.dumps(project(data, view, fields))

        elif isinstance(data, list):
            projected_list = [project(item, view, fields) for item in data]
            return json.dumps(projected_list)

    elif isinstance(result, dict):
        if "error" in result:
            return result

        has_common_envelope_keys = any(k in ["success", "error", "warnings", "found", "ok", "next_cursor", "count", "data", "sessions", "albums", "tracks", "skill", "activities", "track", "album", "session"] for k in result.keys())

        if has_common_envelope_keys:
            new_data = {}
            for k, v in result.items():
                if isinstance(v, list):
                    new_data[k] = [project(item, view, fields) for item in v]
                elif isinstance(v, dict):
                    new_data[k] = project(v, view, fields)
                else:
                    new_data[k] = v
            return new_data
        else:
            return project(result, view, fields)

    elif isinstance(result, list):
        return [project(item, view, fields) for item in result]

    elif hasattr(result, "model_dump") or hasattr(result, "dict"):
        return project(result, view, fields)

    return result
