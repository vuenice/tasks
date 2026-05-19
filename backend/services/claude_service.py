"""
Claude service — two public functions:

  summarize_comments(task_title, comment_texts) -> str
      Calls `claude -p` to produce a 2-3 sentence summary of comments.

  run_task_with_claude(title, description, claude_md, skill_md, cwd) -> str
      Constructs a full prompt from CLAUDE.md + SKILL.md + task details,
      then invokes `claude -p "..." --no-permission-prompts` via subprocess.
      Returns stdout (the execution report) or an error string.

Both functions use the `claude` CLI that ships with Claude Code, so no
separate API key is needed — Claude Code's existing auth is reused.
"""
import logging
import subprocess
import textwrap

logger = logging.getLogger(__name__)

# Timeout for each claude CLI call (seconds)
CLAUDE_TIMEOUT = 180


def _run_claude(prompt: str, cwd: str = ".") -> str:
    """
    Run `claude -p <prompt> --no-permission-prompts` and return stdout.
    Raises RuntimeError on non-zero exit.
    """
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--no-permission-prompts"],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=CLAUDE_TIMEOUT,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            err = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(f"claude exited {result.returncode}: {err}")
    except FileNotFoundError:
        raise RuntimeError(
            "The `claude` CLI was not found. "
            "Make sure Claude Code is installed and `claude` is on your PATH."
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"claude timed out after {CLAUDE_TIMEOUT}s")


def summarize_comments(task_title: str, comment_texts: list[str]) -> str:
    """
    Ask Claude to produce a concise summary of all comments on a task.
    Returns the summary string.  On any error, returns a fallback message.
    """
    if not comment_texts:
        return ""

    formatted = "\n".join(
        f"{i + 1}. {text}" for i, text in enumerate(comment_texts)
    )

    prompt = textwrap.dedent(f"""
        You are a task management assistant. Summarise the following comments
        for the task "{task_title}" in 2-3 concise sentences.
        Focus on: key decisions made, current progress, and any open action items.
        Do not add any preamble — output the summary only.

        Comments:
        {formatted}
    """).strip()

    try:
        return _run_claude(prompt)
    except Exception as exc:
        logger.error("summarize_comments error: %s", exc)
        # Return a lightweight fallback so the task is not left without a summary
        return f"[Auto-summary unavailable: {exc}]"


def run_task_with_claude(
    task_title: str,
    task_description: str,
    claude_md: str,
    skill_md: str,
    cwd: str = ".",
) -> str:
    """
    Execute a task autonomously using the Claude CLI.

    The full prompt is:
      - Instructions from CLAUDE.md
      - Available skills from SKILL.md
      - The task to perform

    Claude is instructed NOT to ask questions and to report what it did.
    Returns the execution report, or an error message.
    """
    instructions_section = (
        f"## Agent Instructions (CLAUDE.md)\n\n{claude_md.strip()}\n"
        if claude_md.strip()
        else ""
    )
    skills_section = (
        f"## Available Skills (SKILL.md)\n\n{skill_md.strip()}\n"
        if skill_md.strip()
        else ""
    )

    prompt = textwrap.dedent(f"""
        You are an automated agent executing a scheduled task.
        IMPORTANT: Do not ask any questions. Execute the task directly and report what you did.

        {instructions_section}
        {skills_section}
        ## Task to Execute

        Title: {task_title}
        Description: {task_description or "(no description provided)"}

        Execute this task now. After completing it, write a concise execution report
        (2-5 sentences) describing exactly what was done and the outcome.
        Output only the report — no preamble.
    """).strip()

    try:
        return _run_claude(prompt, cwd=cwd)
    except Exception as exc:
        logger.error("run_task_with_claude error for '%s': %s", task_title, exc)
        return f"[Execution error: {exc}]"
