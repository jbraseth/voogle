#!/usr/bin/env python
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Migration script for Qdrant collection upgrade.

Migrates existing podcast-only collections to the unified multimodal schema
with zero-downtime support.

Usage:
    # Dry run (no changes)
    python scripts/migrate_collection.py --dry-run

    # Full migration
    python scripts/migrate_collection.py

    # Custom collection names
    python scripts/migrate_collection.py --source vectordb --target vectordb_v2

    # Skip verification
    python scripts/migrate_collection.py --no-verify
"""

import argparse
import logging
import sys
from pathlib import Path

# Add backend src to path for imports
backend_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_path))

from voogle import settings
from voogle.vector_migration import (
    MigrationPlan,
    MigrationStatus,
    execute_migration,
    rollback_migration,
)

# Import storage after settings are loaded
from voogle import storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Migrate Qdrant collection to unified multimodal schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--source",
        default="vectordb",
        help="Source collection name (default: vectordb)",
    )
    parser.add_argument(
        "--target",
        default="vectordb_unified",
        help="Target collection name (default: vectordb_unified)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Batch size for export/import (default: 1000)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate migration without making changes",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip point count verification after migration",
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback a failed migration",
    )
    parser.add_argument(
        "--backup-collection",
        help="Name for backup collection (auto-generated if not specified)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


def main() -> int:
    """Run the migration script."""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Starting collection migration")
    logger.info(f"  Source: {args.source}")
    logger.info(f"  Target: {args.target}")
    logger.info(f"  Batch size: {args.batch_size}")
    logger.info(f"  Dry run: {args.dry_run}")

    # Get Qdrant client
    try:
        # Try to import from voogle.vector for get_configured_client
        from voogle import vector
        client = vector.get_configured_client()
    except (ImportError, AttributeError):
        # Fallback: create client directly from settings
        import qdrant_client
        if settings.settings.qdrant_use_file:
            client = qdrant_client.QdrantClient(path=str(storage.vectordb_path()))
        else:
            client = qdrant_client.QdrantClient(
                host=settings.settings.qdrant_host,
                port=settings.settings.qdrant_port,
            )

    # Create migration plan
    plan = MigrationPlan(
        source_collection=args.source,
        target_collection=args.target,
        batch_size=args.batch_size,
        backup_collection=args.backup_collection,
        verify_counts=not args.no_verify,
    )

    # Handle rollback mode
    if args.rollback:
        logger.info("Rollback mode - attempting to restore from backup")
        success = rollback_migration(client, plan)
        if success:
            logger.info("Rollback completed successfully")
            return 0
        else:
            logger.error("Rollback failed")
            return 1

    # Execute migration
    try:
        result = execute_migration(client, plan, dry_run=args.dry_run)

        if result.status == MigrationStatus.COMPLETED:
            logger.info("Migration completed successfully!")
            logger.info(f"  Points exported: {result.points_exported}")
            logger.info(f"  Points imported: {result.points_imported}")
            if result.started_at and result.completed_at:
                duration = result.completed_at - result.started_at
                logger.info(f"  Duration: {duration}")
            return 0
        else:
            logger.error(f"Migration failed with status: {result.status}")
            if result.error_message:
                logger.error(f"  Error: {result.error_message}")
            return 1

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        logger.info("Run with --rollback to restore from backup")
        return 1


if __name__ == "__main__":
    sys.exit(main())
