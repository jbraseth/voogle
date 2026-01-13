# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Qdrant collection schema for multimodal fragment storage.

Defines the collection configuration supporting multimodal fragments with
named vectors and payload-based partitioning. The schema supports:

- Named vectors for different embedding types (text_dense, text_sparse, image, multimodal)
- Payload schema matching Fragment and Location types
- Quantization configuration for storage efficiency
- Payload indexes for optimal filter performance with tenant isolation

Usage:
    from voogle.vector_schema import get_collection_config, create_collection_with_schema

    config = get_collection_config()
    create_collection_with_schema(client, "my_collection", config)

    # Get payload index definitions
    from voogle.vector_schema import get_payload_indexes
    indexes = get_payload_indexes()
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from qdrant_client import QdrantClient, models


class VectorName(str, Enum):
    """Named vector identifiers for multimodal embeddings.

    Each vector type supports a different embedding modality:
    - TEXT_DENSE: Dense text embeddings (e.g., sentence-transformers, OpenAI)
    - TEXT_SPARSE: Sparse text embeddings (e.g., SPLADE, BM25)
    - IMAGE: Image embeddings (e.g., CLIP visual encoder)
    - MULTIMODAL: Joint text-image embeddings (e.g., CLIP joint space)
    """

    TEXT_DENSE = "text_dense"
    TEXT_SPARSE = "text_sparse"
    IMAGE = "image"
    MULTIMODAL = "multimodal"


@dataclass(frozen=True)
class VectorConfig:
    """Configuration for a single named vector.

    Attributes:
        name: Identifier for this vector type.
        size: Dimensionality of the vector.
        distance: Distance metric for similarity computation.
        is_sparse: Whether this is a sparse vector.
        quantization: Optional quantization config for storage efficiency.
    """

    name: VectorName
    size: int
    distance: models.Distance = models.Distance.COSINE
    is_sparse: bool = False
    quantization: Optional[models.QuantizationConfig] = None


# Default vector dimensions for common embedding models
DEFAULT_TEXT_DENSE_DIM = 384  # sentence-transformers/all-MiniLM-L6-v2
DEFAULT_IMAGE_DIM = 512  # CLIP ViT-B/32
DEFAULT_MULTIMODAL_DIM = 512  # CLIP joint embedding space


@dataclass(frozen=True)
class PayloadIndexConfig:
    """Configuration for a payload field index.

    Payload indexes enable efficient filtering on fields. Tenant fields
    receive special handling for multi-tenant isolation.

    Attributes:
        field_name: Name of the payload field to index.
        field_type: Qdrant payload schema type for this field.
        is_tenant: If True, this field is used for tenant isolation.
                   Tenant fields get priority indexing and are always indexed.
    """

    field_name: str
    field_type: models.PayloadSchemaType
    is_tenant: bool = False


# Primary payload indexes for optimal filter performance
# These indexes are critical for query performance and tenant isolation
PRIMARY_PAYLOAD_INDEXES: tuple[PayloadIndexConfig, ...] = (
    # Tenant isolation index - always indexed, used for corpus partitioning
    PayloadIndexConfig(
        field_name="corpus_id",
        field_type=models.PayloadSchemaType.KEYWORD,
        is_tenant=True,
    ),
    # Content type for filtering by modality (text, image, audio, video)
    PayloadIndexConfig(
        field_name="content_type",
        field_type=models.PayloadSchemaType.KEYWORD,
        is_tenant=False,
    ),
    # Source identifier for filtering by data source
    PayloadIndexConfig(
        field_name="source_id",
        field_type=models.PayloadSchemaType.UUID,
        is_tenant=False,
    ),
    # Timestamp for time-range filtering
    PayloadIndexConfig(
        field_name="created_at",
        field_type=models.PayloadSchemaType.DATETIME,
        is_tenant=False,
    ),
)


@dataclass
class CollectionConfig:
    """Configuration for a Qdrant collection supporting multimodal fragments.

    Attributes:
        vectors_config: Mapping of vector names to their configurations.
            This includes both dense vectors (VectorParams) and sparse vectors
            (SparseVectorParams) in a unified dictionary.
        payload_schema: Schema for payload fields (for validation/indexing).
        quantization_config: Default quantization for all vectors.
        on_disk_payload: Whether to store payloads on disk.
        replication_factor: Number of replicas for each shard.
        write_consistency_factor: Number of replicas that must acknowledge writes.
    """

    vectors_config: dict[str, models.VectorParams | models.SparseVectorParams] = field(
        default_factory=dict
    )
    payload_schema: dict[str, models.PayloadSchemaType] = field(default_factory=dict)
    quantization_config: Optional[models.QuantizationConfig] = None
    on_disk_payload: bool = False
    replication_factor: int = 1
    write_consistency_factor: int = 1


def _create_default_quantization() -> models.ScalarQuantization:
    """Create default scalar quantization config for storage efficiency.

    Uses INT8 quantization which reduces memory by ~4x while maintaining
    good accuracy for most use cases.
    """
    return models.ScalarQuantization(
        scalar=models.ScalarQuantizationConfig(
            type=models.ScalarType.INT8,
            quantile=0.99,
            always_ram=True,
        )
    )


def _create_vectors_config(
    text_dense_dim: int = DEFAULT_TEXT_DENSE_DIM,
    image_dim: int = DEFAULT_IMAGE_DIM,
    multimodal_dim: int = DEFAULT_MULTIMODAL_DIM,
) -> dict[str, models.VectorParams | models.SparseVectorParams]:
    """Create named vectors configuration for multimodal support.

    Includes both dense vectors and sparse vectors for hybrid search.

    Args:
        text_dense_dim: Dimension for dense text embeddings.
        image_dim: Dimension for image embeddings.
        multimodal_dim: Dimension for multimodal embeddings.

    Returns:
        Dictionary mapping vector names to their configurations.
    """
    return {
        VectorName.TEXT_DENSE.value: models.VectorParams(
            size=text_dense_dim,
            distance=models.Distance.COSINE,
        ),
        VectorName.TEXT_SPARSE.value: models.SparseVectorParams(
            modifier=models.Modifier.IDF,
        ),
        VectorName.IMAGE.value: models.VectorParams(
            size=image_dim,
            distance=models.Distance.COSINE,
        ),
        VectorName.MULTIMODAL.value: models.VectorParams(
            size=multimodal_dim,
            distance=models.Distance.COSINE,
        ),
    }


def _create_payload_schema() -> dict[str, models.PayloadSchemaType]:
    """Create payload schema matching Fragment and Location types.

    The schema supports:
    - Fragment fields: id, text, score, source_id, source_type, deep_link, metadata
    - Location fields: location_type + type-specific fields
    - Legacy fields: episode, channel, start_secs, end_secs (for backward compatibility)
    - Metadata fields: embedding_model, embedding_provider, embedded_at

    Returns:
        Dictionary mapping field names to their schema types.
    """
    return {
        # Fragment core fields
        "fragment_id": models.PayloadSchemaType.KEYWORD,
        "text": models.PayloadSchemaType.TEXT,
        "source_id": models.PayloadSchemaType.KEYWORD,
        "source_type": models.PayloadSchemaType.KEYWORD,
        "deep_link": models.PayloadSchemaType.KEYWORD,
        # Location discriminator
        "location_type": models.PayloadSchemaType.KEYWORD,
        # TimestampLocation fields
        "start_time": models.PayloadSchemaType.FLOAT,
        "end_time": models.PayloadSchemaType.FLOAT,
        # PageBboxLocation fields
        "page": models.PayloadSchemaType.INTEGER,
        "bbox_x": models.PayloadSchemaType.FLOAT,
        "bbox_y": models.PayloadSchemaType.FLOAT,
        "bbox_width": models.PayloadSchemaType.FLOAT,
        "bbox_height": models.PayloadSchemaType.FLOAT,
        # CodeLocation fields
        "file_path": models.PayloadSchemaType.KEYWORD,
        "start_line": models.PayloadSchemaType.INTEGER,
        "end_line": models.PayloadSchemaType.INTEGER,
        "column": models.PayloadSchemaType.INTEGER,
        # SlideLocation fields
        "slide_number": models.PayloadSchemaType.INTEGER,
        "element_id": models.PayloadSchemaType.KEYWORD,
        # ImageRegionLocation fields (reuses bbox_* fields)
        # ElementSelectorLocation fields
        "selector": models.PayloadSchemaType.KEYWORD,
        "selector_type": models.PayloadSchemaType.KEYWORD,
        "text_match": models.PayloadSchemaType.TEXT,
        # Legacy fields for backward compatibility
        "episode": models.PayloadSchemaType.INTEGER,
        "channel": models.PayloadSchemaType.INTEGER,
        "start_secs": models.PayloadSchemaType.INTEGER,
        "end_secs": models.PayloadSchemaType.INTEGER,
        # Embedding metadata
        "embedding_model": models.PayloadSchemaType.KEYWORD,
        "embedding_provider": models.PayloadSchemaType.KEYWORD,
        "embedded_at": models.PayloadSchemaType.DATETIME,
        # Corpus/partition fields
        "corpus_id": models.PayloadSchemaType.KEYWORD,
        "partition": models.PayloadSchemaType.KEYWORD,
    }


def get_collection_config(
    text_dense_dim: int = DEFAULT_TEXT_DENSE_DIM,
    image_dim: int = DEFAULT_IMAGE_DIM,
    multimodal_dim: int = DEFAULT_MULTIMODAL_DIM,
    enable_quantization: bool = True,
    on_disk_payload: bool = False,
) -> CollectionConfig:
    """Get the collection configuration for multimodal fragment storage.

    Creates a configuration supporting:
    - Named vectors for text (dense/sparse), image, and multimodal embeddings
    - Payload schema matching Fragment and Location types
    - Optional INT8 quantization for storage efficiency

    Args:
        text_dense_dim: Dimension for dense text embeddings (default: 384).
        image_dim: Dimension for image embeddings (default: 512).
        multimodal_dim: Dimension for multimodal embeddings (default: 512).
        enable_quantization: Whether to enable INT8 quantization (default: True).
        on_disk_payload: Whether to store payloads on disk (default: False).

    Returns:
        CollectionConfig with named vectors and payload schema.
    """
    quantization = _create_default_quantization() if enable_quantization else None

    return CollectionConfig(
        vectors_config=_create_vectors_config(
            text_dense_dim=text_dense_dim,
            image_dim=image_dim,
            multimodal_dim=multimodal_dim,
        ),
        payload_schema=_create_payload_schema(),
        quantization_config=quantization,
        on_disk_payload=on_disk_payload,
    )


def create_collection_with_schema(
    client,
    collection_name: str,
    config: CollectionConfig,
    recreate: bool = False,
) -> None:
    """Create a Qdrant collection with the given schema configuration.

    Args:
        client: Qdrant client instance.
        collection_name: Name for the new collection.
        config: Collection configuration with vectors and payload schema.
        recreate: If True, delete existing collection first.

    Raises:
        ValueError: If collection exists and recreate is False.
    """
    if client.collection_exists(collection_name):
        if recreate:
            client.delete_collection(collection_name)
        else:
            raise ValueError(
                f"Collection '{collection_name}' already exists. "
                "Set recreate=True to overwrite."
            )

    # Separate dense and sparse vector configs
    dense_vectors: dict[str, models.VectorParams] = {}
    sparse_vectors: dict[str, models.SparseVectorParams] = {}

    for name, vec_config in config.vectors_config.items():
        if isinstance(vec_config, models.SparseVectorParams):
            sparse_vectors[name] = vec_config
        else:
            dense_vectors[name] = vec_config

    # Create collection with named vectors
    client.create_collection(
        collection_name=collection_name,
        vectors_config=dense_vectors,
        sparse_vectors_config=sparse_vectors if sparse_vectors else None,
        quantization_config=config.quantization_config,
        on_disk_payload=config.on_disk_payload,
        replication_factor=config.replication_factor,
        write_consistency_factor=config.write_consistency_factor,
    )

    # Create payload indexes for efficient filtering
    for field_name, schema_type in config.payload_schema.items():
        client.create_payload_index(
            collection_name=collection_name,
            field_name=field_name,
            field_schema=schema_type,
        )


def get_vector_name_for_modality(modality: str) -> VectorName:
    """Get the appropriate vector name for a content modality.

    Args:
        modality: Content modality string ('text', 'image', 'audio', 'video').

    Returns:
        VectorName enum value for the modality.

    Raises:
        ValueError: If modality is not supported.
    """
    modality_mapping = {
        "text": VectorName.TEXT_DENSE,
        "image": VectorName.IMAGE,
        "audio": VectorName.MULTIMODAL,  # Audio uses multimodal embeddings
        "video": VectorName.MULTIMODAL,  # Video uses multimodal embeddings
    }

    if modality not in modality_mapping:
        raise ValueError(
            f"Unsupported modality: {modality}. "
            f"Supported: {list(modality_mapping.keys())}"
        )

    return modality_mapping[modality]


def get_payload_indexes() -> list[PayloadIndexConfig]:
    """Get the list of payload index configurations.

    Returns:
        List of PayloadIndexConfig objects defining the primary indexes
        for optimal filter performance and tenant isolation.

    Example:
        >>> indexes = get_payload_indexes()
        >>> for idx in indexes:
        ...     print(f"{idx.field_name}: {idx.field_type}, tenant={idx.is_tenant}")
        corpus_id: PayloadSchemaType.KEYWORD, tenant=True
        content_type: PayloadSchemaType.KEYWORD, tenant=False
        source_id: PayloadSchemaType.UUID, tenant=False
        created_at: PayloadSchemaType.DATETIME, tenant=False
    """
    return list(PRIMARY_PAYLOAD_INDEXES)


def get_tenant_indexes() -> list[PayloadIndexConfig]:
    """Get only the tenant isolation indexes.

    Returns:
        List of PayloadIndexConfig objects marked as tenant fields.
        These fields are used for multi-tenant data isolation.
    """
    return [idx for idx in PRIMARY_PAYLOAD_INDEXES if idx.is_tenant]


@dataclass
class PayloadIndexStatus:
    """Status of a payload index in a collection.

    Attributes:
        field_name: Name of the indexed field.
        indexed: Whether the field has an index.
        index_type: Type of index if indexed, None otherwise.
        points_count: Approximate number of indexed values.
    """

    field_name: str
    indexed: bool
    index_type: Optional[str] = None
    points_count: Optional[int] = None


@dataclass
class CollectionIndexReport:
    """Report on payload indexes for a collection.

    Attributes:
        collection_name: Name of the collection.
        indexes: List of index statuses.
        missing_primary_indexes: List of primary indexes not found in collection.
        has_tenant_index: Whether tenant isolation index exists.
    """

    collection_name: str
    indexes: list[PayloadIndexStatus]
    missing_primary_indexes: list[str]
    has_tenant_index: bool


def get_collection_index_status(
    client: QdrantClient,
    collection_name: str,
) -> CollectionIndexReport:
    """Get the status of payload indexes for a collection.

    Queries the collection to determine which payload fields are indexed
    and reports on missing primary indexes.

    Args:
        client: Qdrant client instance.
        collection_name: Name of the collection to check.

    Returns:
        CollectionIndexReport with index status and coverage analysis.

    Raises:
        ValueError: If collection does not exist.
    """
    if not client.collection_exists(collection_name):
        raise ValueError(f"Collection '{collection_name}' does not exist")

    collection_info = client.get_collection(collection_name)
    payload_schema = collection_info.payload_schema or {}

    # Build index status list from collection schema
    indexes = []
    indexed_fields = set()

    for field_name, field_info in payload_schema.items():
        indexed_fields.add(field_name)
        indexes.append(
            PayloadIndexStatus(
                field_name=field_name,
                indexed=True,
                index_type=str(field_info.data_type) if hasattr(field_info, 'data_type') else None,
                points_count=field_info.points if hasattr(field_info, 'points') else None,
            )
        )

    # Check for missing primary indexes
    primary_fields = {idx.field_name for idx in PRIMARY_PAYLOAD_INDEXES}
    missing = [f for f in primary_fields if f not in indexed_fields]

    # Check tenant index
    tenant_fields = {idx.field_name for idx in get_tenant_indexes()}
    has_tenant = bool(tenant_fields & indexed_fields)

    return CollectionIndexReport(
        collection_name=collection_name,
        indexes=indexes,
        missing_primary_indexes=missing,
        has_tenant_index=has_tenant,
    )


def ensure_primary_indexes(
    client: QdrantClient,
    collection_name: str,
) -> list[str]:
    """Ensure all primary payload indexes exist on a collection.

    Creates any missing primary indexes. This is idempotent - existing
    indexes are not modified.

    Args:
        client: Qdrant client instance.
        collection_name: Name of the collection to update.

    Returns:
        List of field names that were newly indexed.

    Raises:
        ValueError: If collection does not exist.
    """
    if not client.collection_exists(collection_name):
        raise ValueError(f"Collection '{collection_name}' does not exist")

    report = get_collection_index_status(client, collection_name)
    created = []

    for field_name in report.missing_primary_indexes:
        # Find the config for this field
        config = next(
            (idx for idx in PRIMARY_PAYLOAD_INDEXES if idx.field_name == field_name),
            None,
        )
        if config is None:
            continue

        client.create_payload_index(
            collection_name=collection_name,
            field_name=config.field_name,
            field_schema=config.field_type,
        )
        created.append(field_name)

    return created
