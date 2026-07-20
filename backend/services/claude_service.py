"""
Claude service.

  summarize_comments(task_title, comment_texts) -> str
      Calls the claude CLI to produce a 2-3 sentence summary of comments.

  run_task_with_claude(title, description, claude_md, skill_md, cwd) -> str
      Constructs a prompt from CLAUDE.md + SKILL.md + task details and invokes
      the claude CLI.  Returns stdout (the execution report) or an error string.

Binary resolution order (see _find_claude_bin for details):
  1. CLAUDE_BIN environment variable
  2. shutil.which("claude") -- standard PATH
  3. shutil.which("claude.cmd") -- Windows npm wrapper
  4. %APPDATA%\npm\claude.cmd / claude -- Windows npm global dir
"""
import logging
import os
import platform
import shutil
import subprocess
import textwrap

logger = logging.getLogger(__name__)

# Timeout for each claude CLI call (seconds)
CLAUDE_TIMEOUT = 180


def _find_claude_bin() -> str:
    """
    Locate the claude CLI binary and log the result at startup.

    Resolution order:
      1. CLAUDE_BIN env var (explicit override -- set this if auto-detection fails)
      2. shutil.which("claude") -- works on Linux / macOS / Windows with correct PATH
      3. Windows: shutil.which("claude.cmd")
      4. Windows: %APPDATA%\\npm\\claude.cmd  (npm global bin directory)
      5. Windows: %LOCALAPPDATA%\\npm\\claude.cmd

    Logs a warning if the binary cannot be found so the problem shows in the
    server log immediately on startup, not silently when a routine fires.
    """
    # 1. Explicit override via environment variable
    env_bin = os.environ.get("CLAUDE_BIN", "").strip()
    if env_bin:
        if os.path.isfile(env_bin):
            logger.info("claude CLI resolved from CLAUDE_BIN: %s", env_bin)
            return env_bin
        else:
            logger.warning(
                "CLAUDE_BIN is set to '%s' but that file does not exist -- ignoring.",
                env_bin,
            )

    # 2. Standard PATH lookup
    found = shutil.which("claude")
    if found:
        logger.info("claude CLI found on PATH: %s", found)
        return found

    # 3-4. Windows-specific fallbacks
    if platform.system() == "Windows":
        # npm installs CLI wrappers as .cmd files on Windows
        found = shutil.which("claude.cmd")
        if found:
            logger.info("claude CLI found as claude.cmd: %s", found)
            return found

        appdata = os.environ.get("APPDATA", "")
        local_appdata = os.environ.get("LOCALAPPDATA", "")
        candidates = [
            os.path.join(appdata, "npm", "claude.cmd"),
            os.path.join(appdata, "npm", "claude"),
            os.path.join(local_appdata, "npm", "claude.cmd"),
        ]
        for candidate in candidates:
            if os.path.isfile(candidate):
                logger.info("claude CLI found at: %s", candidate)
                return candidate

    logger.warning(
        "claude CLI not found. Scheduled routines and comment summarisation "
        "will fail until this is resolved.\n"
        "Fix options:\n"
        "  1. Ensure 'claude' is on the PATH that uvicorn inherits.\n"
        "  2. Set CLAUDE_BIN to the full path of the claude executable, e.g.:\n"
        "     CLAUDE_BIN=C:\\Users\\you\\AppData\\Roaming\\npm\\claude.cmd"
    )
    return "claude"  # will raise FileNotFoundError when actually invoked


# Resolved once at import time.
_CLAUDE_BIN: str = _find_claude_bin()


def _run_claude(prompt: str, cwd: str = ".") -> str:
    """
    Run the claude CLI with -p <prompt> and return stdout.
    Raises RuntimeError on non-zero exit or if the binary is not found.
    """
    try:
        result = subprocess.run(
            [_CLAUDE_BIN, "-p", prompt, "--no-permission-prompts"],
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
            f"The claude CLI was not found at '{_CLAUDE_BIN}'. "
            "Set the CLAUDE_BIN environment variable to the full path of the "
            "claude executable and restart the server."
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"claude timed out after {CLAUDE_TIMEOUT}s")


def summarize_comments(task_title: str, comment_texts: list) -> str:
    """
    Ask Claude to produce a concise summary of all comments on a task.
    Returns the summary string. On any error returns a fallback message.
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
        Do not add any preamble -- output the summary only.

        Comments:
        {formatted}
    """).strip()

    try:
        return _run_claude(prompt)
    except Exception as exc:
        logger.error("summarize_comments error: %s", exc)
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
    Returns the execution report, or an error message string on failure.
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
        Output only the report -- no preamble.
    """).strip()

    try:
        return _run_claude(prompt, cwd=cwd)
    except Exception as exc:
        logger.error("run_task_with_claude error for '%s': %s", task_title, exc)
        return f"[Execution error: {exc}]"
