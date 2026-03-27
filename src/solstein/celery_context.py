"""Celery task context propagation.

Propagates request context (request_id, correlation_id, tenant_id, user_id)
to Celery tasks via task headers.
"""

from celery.signals import before_task_publish, task_postrun, task_prerun

from .utils.context import get_current_context, reset_context, set_context


@before_task_publish.connect
def add_context_to_task_headers(headers=None, body=None, **kwargs):
    """Add current context to task headers before publishing."""
    if headers is None:
        return
    context = get_current_context()
    if context:
        headers["_context"] = context


@task_prerun.connect
def restore_context_from_headers(task_id=None, task=None, **other):
    """Restore context from task headers when task starts."""
    # Access request context from task request
    request = task.request
    context = getattr(request, "headers", {}).get("_context", {})

    if context:
        # Store tokens on task instance for cleanup
        task._context_tokens = set_context(**context)


@task_postrun.connect
def clear_task_context(task_id=None, task=None, **kwargs):
    """Clear context after task completes."""
    tokens = getattr(task, "_context_tokens", [])
    if tokens:
        reset_context(tokens)
        task._context_tokens = []
