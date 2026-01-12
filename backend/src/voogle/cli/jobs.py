# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Manage job queue: list, retry, and clear failed jobs.

Commands for monitoring and managing the RQ job queue, including
the dead letter queue for permanently failed jobs.
"""
import argparse
import logging
import sys
from datetime import datetime, timezone

from voogle import job_manager

logger = logging.getLogger(__name__)


def format_datetime(dt: datetime | None) -> str:
    """Format a datetime for display."""
    if dt is None:
        return "-"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def print_job(job: job_manager.JobInfo, verbose: bool = False) -> None:
    """Print job information."""
    status_icons = {
        job_manager.JobStatus.QUEUED: "[QUEUED]",
        job_manager.JobStatus.STARTED: "[RUNNING]",
        job_manager.JobStatus.FINISHED: "[DONE]",
        job_manager.JobStatus.FAILED: "[FAILED]",
    }
    icon = status_icons.get(job.status, "[???]")
    print(f"{icon} {job.job_id[:8]}... {job.func_name}")

    if verbose:
        print(f"    Enqueued: {format_datetime(job.enqueued_at)}")
        print(f"    Started:  {format_datetime(job.started_at)}")
        print(f"    Ended:    {format_datetime(job.ended_at)}")
        if job.retries_left > 0:
            print(f"    Retries:  {job.retries_left} left")
        if job.exc_info:
            print(f"    Error:\n{job.exc_info}")


def cmd_stats() -> None:
    """Show queue statistics."""
    stats = job_manager.get_queue_stats()
    print("Queue Statistics:")
    print(f"  Queued:    {stats['queued']}")
    print(f"  Running:   {stats['started']}")
    print(f"  Completed: {stats['finished']}")
    print(f"  Failed:    {stats['failed']}")


def cmd_list(job_type: str, verbose: bool) -> None:
    """List jobs by type."""
    if job_type == "all":
        types = ["queued", "running", "failed"]
    else:
        types = [job_type]

    for t in types:
        if t == "queued":
            jobs = job_manager.list_queued_jobs()
            header = "Queued Jobs"
        elif t == "running":
            jobs = job_manager.list_active_jobs()
            header = "Running Jobs"
        elif t == "failed":
            jobs = job_manager.list_failed_jobs()
            header = "Failed Jobs"
        else:
            continue

        print(f"\n{header}:")
        if not jobs:
            print("  (none)")
        else:
            for job in jobs:
                print_job(job, verbose)


def cmd_retry_failed(job_id: str | None) -> None:
    """Retry failed jobs."""
    if job_id:
        # Retry specific job
        if job_manager.retry_failed_job(job_id):
            print(f"Job {job_id} requeued successfully")
        else:
            print(f"Failed to requeue job {job_id}")
            sys.exit(1)
    else:
        # Retry all failed jobs
        success, failed = job_manager.retry_all_failed_jobs()
        print(f"Requeued {success} jobs")
        if failed > 0:
            print(f"Failed to requeue {failed} jobs")
            sys.exit(1)


def cmd_clear_failed() -> None:
    """Clear all failed jobs."""
    count = job_manager.clear_failed_jobs()
    print(f"Deleted {count} failed jobs")


def cmd_info(job_id: str) -> None:
    """Show detailed info about a specific job."""
    info = job_manager.get_job_info(job_id)
    if not info:
        print(f"Job {job_id} not found")
        sys.exit(1)

    print(f"Job ID:    {info.job_id}")
    print(f"Function:  {info.func_name}")
    print(f"Status:    {info.status.value}")
    print(f"Enqueued:  {format_datetime(info.enqueued_at)}")
    print(f"Started:   {format_datetime(info.started_at)}")
    print(f"Ended:     {format_datetime(info.ended_at)}")
    print(f"Retries:   {info.retries_left}")

    progress = job_manager.get_job_progress(job_id)
    if progress:
        print(f"Progress:  {progress['current']}/{progress['total']} - {progress['message']}")

    if info.exc_info:
        print(f"\nError:\n{info.exc_info}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # stats command
    subparsers.add_parser("stats", help="Show queue statistics")

    # list command
    list_parser = subparsers.add_parser("list", help="List jobs")
    list_parser.add_argument(
        "type",
        choices=["all", "queued", "running", "failed"],
        default="all",
        nargs="?",
        help="Type of jobs to list (default: all)",
    )
    list_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed info"
    )

    # retry command
    retry_parser = subparsers.add_parser("retry", help="Retry failed jobs")
    retry_parser.add_argument(
        "job_id",
        nargs="?",
        default=None,
        help="Specific job ID to retry (default: retry all)",
    )

    # clear command
    subparsers.add_parser("clear", help="Clear all failed jobs")

    # info command
    info_parser = subparsers.add_parser("info", help="Show job details")
    info_parser.add_argument("job_id", help="Job ID to inspect")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.command == "stats":
        cmd_stats()
    elif args.command == "list":
        cmd_list(args.type, args.verbose)
    elif args.command == "retry":
        cmd_retry_failed(args.job_id)
    elif args.command == "clear":
        cmd_clear_failed()
    elif args.command == "info":
        cmd_info(args.job_id)
    else:
        # No command - show stats by default
        cmd_stats()


if __name__ == "__main__":
    main()
