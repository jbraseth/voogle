# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Router for local assistant endpoint with CLI tools.

This module provides a local-only RAG (Retrieval-Augmented Generation) endpoint
that retrieves relevant fragments from the vector database, builds a prompt with
citations, and shells out to user-installed CLI tools (claude or codex) for
answer generation.

SECURITY: This feature has multiple guard layers:
1. Feature flag (LOCAL_ASSISTANT_ENABLED) must be explicitly enabled
2. Request must come from localhost OR be in explicit allowlist
3. CLI execution uses subprocess.run with list args (no shell injection)
"""

import logging
import shutil
import subprocess
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from voogle import settings as app_settings
from voogle import storage, tasks
from voogle.models import media
from voogle.models.media import ChannelKind
from voogle.schemas import assistant as assistant_schemas

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assistant", tags=["assistant"])


def require_local_assistant_enabled() -> None:
    """Guard Layer 1: Feature flag must be explicitly enabled.

    Raises HTTPException 503 if LOCAL_ASSISTANT_ENABLED is not true.
    """
    if not app_settings.settings.local_assistant_enabled:
        raise HTTPException(
            status_code=503,
            detail="Local assistant feature is not enabled. "
            "Set LOCAL_ASSISTANT_ENABLED=true to enable.",
        )


def require_localhost_or_allowlist(request: Request) -> None:
    """Guard Layer 2: Must be localhost or explicitly allowlisted.

    Raises HTTPException 403 if request is not from localhost and not in allowlist.
    """
    client_host = request.client.host if request.client else None
    if client_host is None:
        raise HTTPException(status_code=403, detail="Cannot determine client IP")

    # Check localhost (IPv4 and IPv6)
    localhost_ips = {"127.0.0.1", "::1"}
    if client_host in localhost_ips:
        return

    # Check allowlist
    allowlist = app_settings.settings.local_assistant_allowlist
    if allowlist:
        allowed_ips = {ip.strip() for ip in allowlist.split(",") if ip.strip()}
        if client_host in allowed_ips:
            return

    raise HTTPException(
        status_code=403,
        detail=f"Access denied: {client_host} is not localhost or allowlisted",
    )


def find_cli_tool() -> str:
    """Find available CLI tool. Fails loud if none found.

    Returns the name of the CLI tool to use (either the preferred one or fallback).

    Raises HTTPException 503 if neither claude nor codex is found in PATH.
    """
    preferred = app_settings.settings.local_assistant_cli_preference

    # Try preferred first
    if shutil.which(preferred):
        return preferred

    # Try alternative
    alternative = "codex" if preferred == "claude" else "claude"
    if shutil.which(alternative):
        logger.info(f"Preferred CLI '{preferred}' not found, using '{alternative}'")
        return alternative

    raise HTTPException(
        status_code=503,
        detail=f"Neither '{preferred}' nor '{alternative}' CLI found in PATH. "
        f"Install one from: https://github.com/anthropics/claude-code "
        f"or https://github.com/openai/codex-cli",
    )


def execute_cli(cli: str, prompt: str) -> str:
    """Execute CLI with prompt via stdin. Fails loud on errors.

    Args:
        cli: Name of the CLI tool to execute
        prompt: The prompt to send via stdin

    Returns:
        The CLI's stdout response

    Raises:
        HTTPException 500 if CLI fails or times out
    """
    timeout = app_settings.settings.local_assistant_cli_timeout

    try:
        result = subprocess.run(
            [cli, "--print"],  # --print for non-interactive output
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as err:
        raise HTTPException(
            status_code=500,
            detail=f"CLI '{cli}' timed out after {timeout} seconds",
        ) from err
    except FileNotFoundError as err:
        # Should not happen since we check with shutil.which, but handle anyway
        raise HTTPException(
            status_code=503,
            detail=f"CLI '{cli}' not found",
        ) from err

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"CLI '{cli}' failed with exit code {result.returncode}: {result.stderr}",
        )

    return result.stdout


def build_prompt(
    query: str, sources: list[assistant_schemas.SourceCitation]
) -> str:
    """Build the prompt for the CLI with citations.

    Args:
        query: The user's question
        sources: List of source citations from search results

    Returns:
        Formatted prompt string
    """
    if not sources:
        return f"""The user asked: {query}

Unfortunately, no relevant sources were found in the database.
Please respond that you cannot answer this question as there are no
relevant transcript excerpts available."""

    source_text = "\n\n".join(
        f"[{s.index}] Episode: {s.episode_title} | Channel: {s.channel_title} | "
        f"Timestamp: {s.start_secs:.0f}s-{s.end_secs:.0f}s\n{s.text}"
        for s in sources
    )

    return f"""Based on the following transcript excerpts, answer the question.

Question: {query}

Sources:
{source_text}

Instructions:
- Answer the question based ONLY on the provided sources
- Cite sources using [1], [2], etc. when referencing specific information
- If the sources don't contain relevant information, say so clearly"""


@router.get(
    "/answer_local",
    summary="Get an answer using local CLI tools (claude/codex)",
    response_model=assistant_schemas.LocalAnswerResponse,
    dependencies=[
        Depends(require_local_assistant_enabled),
        Depends(require_localhost_or_allowlist),
    ],
)
async def answer_local(
    query_text: str,
    k: int = 6,
    channel_id: Optional[UUID] = None,
) -> assistant_schemas.LocalAnswerResponse:
    """Get an answer to a query using local CLI tools.

    This endpoint:
    1. Searches the vector database for relevant fragments
    2. Builds a prompt with citations
    3. Executes a local CLI tool (claude or codex) with the prompt
    4. Returns the answer with source citations

    Args:
        query_text: The question to answer
        k: Number of search results to include (default 6)
        channel_id: Optional channel to scope the search

    Returns:
        LocalAnswerResponse with answer text and source citations
    """
    # Find CLI tool (fails loud if none found)
    cli = find_cli_tool()

    # Search for relevant fragments (reuses existing search logic)
    channel_pk = None
    if channel_id:
        channel = await media.Channel.objects.get(id=channel_id)
        channel_pk = channel.pk

    search_results = tasks.search(query_text, k, channel=channel_pk)

    # Build source citations
    sources: list[assistant_schemas.SourceCitation] = []
    for idx, r in enumerate(search_results, start=1):
        episode = await media.Episode.objects.get(pk=r.episode)
        if episode.channel is None:
            logger.warning(f"Episode {episode.pk} has no associated channel, skipping")
            continue
        channel = await episode.channel.load()

        # Use local media URL for local channels, original URL for podcast channels
        if channel.kind == ChannelKind.local.value:
            media_url = storage.local_media_url(channel, episode)
        else:
            media_url = str(episode.url)

        sources.append(
            assistant_schemas.SourceCitation(
                index=idx,
                episode_title=str(episode.title),
                channel_title=str(channel.title),
                start_secs=r.start_secs,
                end_secs=r.end_secs,
                text=r.text,
                media_url=media_url,
            )
        )

    # Build prompt and execute CLI
    prompt = build_prompt(query_text, sources)
    answer = execute_cli(cli, prompt)

    return assistant_schemas.LocalAnswerResponse(
        answer=answer.strip(),
        sources=sources,
        cli_used=cli,
        query=query_text,
    )
