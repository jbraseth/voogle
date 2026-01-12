# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Job queue monitoring and management page."""

import asyncio
from datetime import datetime, timezone

import streamlit as st

from voogle import job_manager
from voogle.management import utils as m_utils


def format_datetime(dt: datetime | None) -> str:
    """Format a datetime for display."""
    if dt is None:
        return "-"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def display_job_card(job: job_manager.JobInfo) -> None:
    """Display a job card with details."""
    status_colors = {
        job_manager.JobStatus.QUEUED: "blue",
        job_manager.JobStatus.STARTED: "orange",
        job_manager.JobStatus.FINISHED: "green",
        job_manager.JobStatus.FAILED: "red",
    }
    color = status_colors.get(job.status, "gray")

    with st.expander(f":{color}[{job.status.value.upper()}] {job.func_name}"):
        st.markdown(f"**Job ID:** `{job.job_id}`")
        st.markdown(f"**Function:** `{job.func_name}`")
        st.markdown(f"**Status:** :{color}[{job.status.value}]")
        st.markdown(f"**Enqueued:** {format_datetime(job.enqueued_at)}")
        st.markdown(f"**Started:** {format_datetime(job.started_at)}")
        st.markdown(f"**Ended:** {format_datetime(job.ended_at)}")

        if job.retries_left > 0:
            st.markdown(f"**Retries left:** {job.retries_left}")

        # Show progress if available
        progress = job_manager.get_job_progress(job.job_id)
        if progress:
            current = progress["current"]
            total = progress["total"]
            if total > 0:
                st.progress(current / total, text=f"{current}/{total}")
            if progress["message"]:
                st.markdown(f"**Progress:** {progress['message']}")

        if job.exc_info:
            st.error("Error Details:")
            st.code(job.exc_info, language="python")

        # Actions for failed jobs
        if job.status == job_manager.JobStatus.FAILED:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Retry", key=f"retry_{job.job_id}"):
                    if job_manager.retry_failed_job(job.job_id):
                        st.success("Job requeued successfully")
                        st.rerun()
                    else:
                        st.error("Failed to requeue job")
            with col2:
                if st.button("Delete", key=f"delete_{job.job_id}"):
                    if job_manager.delete_failed_job(job.job_id):
                        st.success("Job deleted")
                        st.rerun()
                    else:
                        st.error("Failed to delete job")


async def queue_stats() -> None:
    """Display queue statistics."""
    st.header("Queue Statistics")

    stats = job_manager.get_queue_stats()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Queued", stats["queued"])
    col2.metric("Running", stats["started"])
    col3.metric("Completed", stats["finished"])
    col4.metric("Failed", stats["failed"])


async def active_jobs() -> None:
    """Display currently running jobs."""
    st.header("Running Jobs")

    jobs = job_manager.list_active_jobs()
    if not jobs:
        st.info("No jobs currently running")
        return

    for job in jobs:
        display_job_card(job)


async def queued_jobs() -> None:
    """Display jobs waiting in queue."""
    st.header("Queued Jobs")

    jobs = job_manager.list_queued_jobs()
    if not jobs:
        st.info("No jobs in queue")
        return

    st.markdown(f"**{len(jobs)} jobs waiting**")
    for job in jobs:
        display_job_card(job)


async def failed_jobs() -> None:
    """Display failed jobs (dead letter queue)."""
    st.header("Failed Jobs (Dead Letter Queue)")

    jobs = job_manager.list_failed_jobs()
    if not jobs:
        st.success("No failed jobs")
        return

    st.warning(f"**{len(jobs)} failed jobs**")

    # Bulk actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Retry All Failed", use_container_width=True):
            success, failed = job_manager.retry_all_failed_jobs()
            if success > 0:
                st.success(f"Requeued {success} jobs")
            if failed > 0:
                st.error(f"Failed to requeue {failed} jobs")
            st.rerun()
    with col2:
        if st.button("Clear All Failed", use_container_width=True):
            count = job_manager.clear_failed_jobs()
            st.success(f"Deleted {count} jobs")
            st.rerun()

    st.divider()

    for job in jobs:
        display_job_card(job)


async def main() -> None:
    st.set_page_config(page_title="Voogle - Jobs", page_icon="📊")
    st.title("📊 Job Queue Monitor")

    if m_utils.login_message(st.session_state):  # type: ignore[arg-type]
        st.markdown(
            """Monitor and manage background jobs. Jobs are automatically retried
            with exponential backoff (1min, 5min, 15min) before moving to the
            dead letter queue."""
        )

        # Auto-refresh toggle
        auto_refresh = st.toggle("Auto-refresh (5s)", value=False)
        if auto_refresh:
            st.markdown("*Page will refresh every 5 seconds*")

        await queue_stats()
        st.divider()
        await active_jobs()
        st.divider()
        await queued_jobs()
        st.divider()
        await failed_jobs()

        if auto_refresh:
            import time

            time.sleep(5)
            st.rerun()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
