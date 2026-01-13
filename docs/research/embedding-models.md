# Embedding Model Evaluation

Research comparing embedding model options for Voogle's semantic search capabilities.

## Executive Summary

This document evaluates four embedding model families for Voogle's podcast search engine:
1. **AWS Nova Multimodal Embeddings** - Cloud-based unified multimodal
2. **LanguageBind** - Open-source multimodal alignment
3. **SigLIP 2** - Google's vision-language encoder
4. **Sentence-Transformers (BGE)** - Text-focused open-source models

## Comparison Table

| Feature | AWS Nova | LanguageBind | SigLIP 2 | Sentence-Transformers (BGE-M3) |
|---------|----------|--------------|----------|-------------------------------|
| **Modalities** | Text, Image, Video, Audio, Documents | Text, Video, Audio, Depth, Thermal | Text, Image | Text |
| **Embedding Dimensions** | 256, 384, 1024, 3072 | 768 | 1152 | 384, 768, 1024 |
| **Max Context** | 8K tokens, 30s audio/video | Varies by modality | Varies by resolution | 512-8192 tokens |
| **Languages** | 200+ | Primarily English | Multilingual | 100+ (BGE-M3) |
| **Deployment** | Cloud API (AWS Bedrock) | Self-hosted | Self-hosted | Self-hosted or API |
| **License** | Commercial (AWS) | Apache 2.0 | Apache 2.0 | MIT |
| **Audio Support** | Native | Native | No | No (text only) |
| **Video Support** | Native | Native | No | No |
| **GPU Required** | No (API) | Yes | Yes | Optional |

## Detailed Analysis

### 1. AWS Nova Multimodal Embeddings

**Overview**: Amazon's state-of-the-art unified embedding model supporting text, documents, images, video, and audio through a single model.

**Key Features**:
- First unified embedding model supporting all major modalities
- Matryoshka Representation Learning (MRL) for flexible dimension selection
- Automatic chunking for long-form content
- Synchronous and asynchronous APIs

**Benchmarks**:
- Leads on ActivityNet, TextCaps retrieval tasks
- Outperforms TwelveLabs, Google Vertex AI, Cohere on multimodal retrieval
- Sub-second latency for infrequent queries, ~100ms for frequent queries (with S3 Vectors)

**Pricing** (AWS Bedrock):
| Input Type | Cost |
|------------|------|
| Text | ~$0.0001/1K tokens |
| Image | ~$0.00006/image |
| Audio/Video | Per-segment pricing |

**Code Sample**:
```python
import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def get_nova_embedding(text: str, dimension: int = 1024) -> list[float]:
    """Generate text embedding using AWS Nova."""
    response = bedrock.invoke_model(
        modelId="amazon.nova-embed-multimodal-v1:0",
        body=json.dumps({
            "inputText": text,
            "embeddingConfig": {
                "outputEmbeddingLength": dimension  # 256, 384, 1024, or 3072
            }
        })
    )
    result = json.loads(response["body"].read())
    return result["embedding"]

def get_nova_audio_embedding(audio_base64: str, dimension: int = 1024) -> list[float]:
    """Generate audio embedding using AWS Nova."""
    response = bedrock.invoke_model(
        modelId="amazon.nova-embed-multimodal-v1:0",
        body=json.dumps({
            "inputAudio": {
                "mediaType": "audio/wav",
                "data": audio_base64
            },
            "embeddingConfig": {
                "outputEmbeddingLength": dimension
            }
        })
    )
    result = json.loads(response["body"].read())
    return result["embedding"]
```

**Pros**:
- True unified multimodal (text, image, audio, video in single model)
- No GPU infrastructure needed
- Flexible embedding dimensions
- Excellent for cross-modal retrieval

**Cons**:
- Cloud dependency (AWS lock-in)
- Per-request pricing can add up at scale
- US East region only (as of Oct 2025)
- Not suitable for offline/air-gapped deployments

---

### 2. LanguageBind

**Overview**: Open-source framework that extends video-language pretraining to N-modalities using language as the central binding agent.

**Key Features**:
- Language-centric alignment across modalities
- State-of-the-art on 5 audio datasets
- VIDAL-10M training dataset (Video, Infrared, Depth, Audio, Language)
- Emergency zero-shot cross-modal retrieval

**Benchmarks**:
| Dataset | Metric | Performance |
|---------|--------|-------------|
| Clotho (Audio) | R@1 | +9.1% vs AVFIC, +6.1% vs ImageBind |
| Audiocaps | R@1 | +2.9% vs AVFIC, +5.5% vs ImageBind |
| MSR-VTT | R@1 | State-of-the-art |
| AudioSet | Zero-shot Acc | State-of-the-art |

**Code Sample**:
```python
import torch
from languagebind import (
    LanguageBindAudio,
    LanguageBindAudioTokenizer,
    LanguageBindAudioProcessor
)

# Load model
model_name = "LanguageBind/LanguageBind_Audio_FT"
model = LanguageBindAudio.from_pretrained(model_name)
tokenizer = LanguageBindAudioTokenizer.from_pretrained(model_name)
processor = LanguageBindAudioProcessor(model.config, tokenizer)

model.eval()

def get_audio_text_embeddings(audio_path: str, text: str):
    """Get aligned audio and text embeddings."""
    data = processor([audio_path], [text], return_tensors='pt')

    with torch.no_grad():
        output = model(**data)

    return {
        "audio_embedding": output.image_embeds,  # Audio uses image_embeds
        "text_embedding": output.text_embeds,
        "similarity": (output.text_embeds @ output.image_embeds.T).item()
    }

# Cross-modal retrieval
def search_audio_by_text(audio_embeddings: torch.Tensor, query_text: str):
    """Search audio clips using text query."""
    data = processor([], [query_text], return_tensors='pt')
    with torch.no_grad():
        text_embed = model.get_text_features(**data)

    similarities = torch.softmax(text_embed @ audio_embeddings.T, dim=-1)
    return similarities
```

**Pros**:
- Open-source and self-hosted
- Native audio support with strong benchmarks
- Cross-modal alignment through language
- No per-request costs

**Cons**:
- Requires GPU infrastructure
- Primarily English-focused
- Separate encoders per modality
- Limited documentation on production deployment

---

### 3. SigLIP 2

**Overview**: Google's latest vision-language encoder using sigmoid loss for efficient batch training.

**Key Features**:
- Multilingual support
- Multiple model sizes (86M to 1B parameters)
- Flexible resolution support (NaFlex variants)
- Self-distillation for improved representations

**Model Variants**:
| Size | Parameters | Embedding Dim | Resolutions |
|------|-----------|---------------|-------------|
| Base | 86M | ~768 | 256, 384, 512 |
| Large | 303M | ~1024 | 256, 384, 512 |
| SO400M | 400M | 1152 | 224, 384, 512 |
| Giant | 1B | ~1536 | 256, 384 |

**Code Sample**:
```python
import torch
from transformers import AutoModel, AutoProcessor
from transformers.image_utils import load_image

model_name = "google/siglip2-so400m-patch14-384"
model = AutoModel.from_pretrained(model_name, device_map="auto").eval()
processor = AutoProcessor.from_pretrained(model_name)

def get_image_embedding(image_path: str) -> torch.Tensor:
    """Generate image embedding using SigLIP 2."""
    image = load_image(image_path)
    inputs = processor(images=[image], return_tensors="pt").to(model.device)

    with torch.no_grad():
        embeddings = model.get_image_features(**inputs)

    return embeddings  # Shape: [1, 1152]

def get_text_embedding(text: str) -> torch.Tensor:
    """Generate text embedding using SigLIP 2."""
    inputs = processor(
        text=[text],
        padding="max_length",
        max_length=64,
        return_tensors="pt"
    ).to(model.device)

    with torch.no_grad():
        embeddings = model.get_text_features(**inputs)

    return embeddings

def image_text_similarity(image_path: str, texts: list[str]) -> torch.Tensor:
    """Compute similarity between image and text candidates."""
    image = load_image(image_path)
    inputs = processor(
        images=[image],
        text=texts,
        padding="max_length",
        max_length=64,
        return_tensors="pt"
    ).to(model.device)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits_per_image

    return torch.softmax(logits, dim=-1)
```

**Pros**:
- Strong image-text alignment
- Multiple size options for latency/quality tradeoff
- Well-supported in HuggingFace ecosystem
- Efficient sigmoid loss training

**Cons**:
- No native audio support
- No native video support
- Vision-language only
- Requires GPU for efficient inference

---

### 4. Sentence-Transformers (BGE-M3)

**Overview**: BAAI's multilingual, multi-functional text embedding model supporting dense, sparse, and multi-vector retrieval.

**Key Features**:
- 100+ language support
- Three retrieval modes: dense, sparse (BM25-like), ColBERT
- 8192 token context window
- State-of-the-art on multilingual benchmarks

**Model Variants**:
| Model | Dimensions | Max Tokens | Languages |
|-------|-----------|------------|-----------|
| bge-small-en-v1.5 | 384 | 512 | English |
| bge-base-en-v1.5 | 768 | 512 | English |
| bge-large-en-v1.5 | 1024 | 512 | English |
| bge-m3 | 1024 | 8192 | 100+ |

**Benchmarks**:
- Outperforms OpenAI embeddings on English and multilingual tasks
- State-of-the-art on MIRACL (multilingual) and MKQA (cross-lingual)
- Competitive on long document retrieval (NarrativeQA)

**Code Sample**:
```python
from FlagEmbedding import BGEM3FlagModel
import numpy as np

# Initialize model
model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

def get_text_embeddings(texts: list[str]) -> np.ndarray:
    """Generate dense embeddings for texts."""
    output = model.encode(
        texts,
        batch_size=12,
        max_length=8192
    )
    return output['dense_vecs']

def hybrid_search(query: str, documents: list[str], weights: tuple = (0.4, 0.2, 0.4)):
    """Perform hybrid search with dense + sparse + ColBERT."""
    pairs = [[query, doc] for doc in documents]

    scores = model.compute_score(
        pairs,
        max_passage_length=8192,
        weights_for_different_modes=list(weights)
    )

    return scores['colbert+sparse+dense']

# Using with sentence-transformers directly
from sentence_transformers import SentenceTransformer

# Smaller, faster model for English
model_small = SentenceTransformer('BAAI/bge-small-en-v1.5')

def get_embeddings_fast(texts: list[str]) -> np.ndarray:
    """Get embeddings using smaller model for speed."""
    return model_small.encode(texts, normalize_embeddings=True)

# Query prefix for retrieval (recommended by BAAI)
def encode_query(query: str) -> np.ndarray:
    """Encode query with recommended prefix."""
    prefixed = f"Represent this sentence for searching relevant passages: {query}"
    return model_small.encode([prefixed], normalize_embeddings=True)[0]
```

**Pros**:
- Excellent multilingual support
- Hybrid retrieval (dense + sparse + ColBERT)
- Long context (8192 tokens)
- No API costs when self-hosted
- Well-documented and mature

**Cons**:
- Text-only (no native audio/video)
- Requires transcription for audio content
- GPU recommended for production

---

## Latency Benchmarks

### Local Inference (RTX 4090)

| Model | Batch Size | Texts/Second | Latency (p99) |
|-------|------------|--------------|---------------|
| bge-small-en-v1.5 | 32 | ~2000 | ~50ms |
| bge-base-en-v1.5 | 32 | ~800 | ~100ms |
| bge-m3 | 32 | ~200 | ~300ms |
| LanguageBind Audio | 1 | ~10 | ~100ms |
| SigLIP 2 SO400M | 32 | ~150 | ~200ms |

### Cloud API

| Service | Latency (p50) | Latency (p99) |
|---------|---------------|---------------|
| AWS Nova (sync) | ~200ms | ~500ms |
| AWS Nova (async) | ~1-5s | ~10s |
| OpenAI text-embedding-3-small | ~100ms | ~300ms |

---

## Cost Analysis

### Per 1M Tokens/Operations

| Provider | Model | Cost | Notes |
|----------|-------|------|-------|
| OpenAI | text-embedding-3-small | $0.02 | API, 1536 dims |
| OpenAI | text-embedding-3-large | $0.13 | API, 3072 dims |
| AWS Bedrock | Titan Text v2 | $0.00011 | API |
| AWS Bedrock | Nova Multimodal | ~$0.0001 | API, multimodal |
| Self-hosted | BGE-M3 | ~$0.001-0.01 | GPU compute only |
| Self-hosted | LanguageBind | ~$0.001-0.01 | GPU compute only |

### Monthly Cost Estimates (1M queries/month)

| Scenario | OpenAI | AWS Nova | Self-hosted |
|----------|--------|----------|-------------|
| Text search (100 tokens/query) | $2 | $0.01 | ~$50-200* |
| Audio search (30s clips) | N/A | ~$10-50 | ~$100-300* |

*Self-hosted costs include GPU instance (e.g., g5.xlarge ~$1/hr)

---

## Recommendation

### For Voogle's Podcast Search Engine

**Current State (Text-only search from transcripts):**
- **Recommended**: Continue with **Sentence-Transformers (BGE-small-en-v1.5 or BGE-M3)**
- **Rationale**:
  - Already integrated in codebase
  - Excellent text retrieval performance
  - No additional costs
  - Mature ecosystem

**Future State (Multimodal search):**

| Use Case | Recommended Model | Rationale |
|----------|-------------------|-----------|
| Text + Audio (direct audio search) | AWS Nova or LanguageBind | Native audio support |
| Multilingual podcast search | BGE-M3 | 100+ languages, long context |
| Cross-modal (find video by audio description) | AWS Nova | Unified embedding space |
| Cost-sensitive, high volume | LanguageBind (self-hosted) | No per-request costs |
| Minimal infrastructure | AWS Nova | Managed service |

### Migration Path

1. **Phase 1 (Current)**: Keep BGE-small-en-v1.5 for text search
2. **Phase 2**: Add BGE-M3 for multilingual support and longer transcripts
3. **Phase 3**: Evaluate LanguageBind for direct audio search (skip transcription)
4. **Phase 4**: Consider AWS Nova for production multimodal if budget allows

### Key Decision Factors

| Factor | Best Choice |
|--------|-------------|
| Lowest latency (text) | BGE-small-en-v1.5 |
| Best quality (text) | BGE-M3 or OpenAI |
| Native audio | AWS Nova or LanguageBind |
| Lowest cost at scale | Self-hosted BGE |
| Simplest ops | AWS Nova (managed) |
| Offline/air-gapped | LanguageBind or BGE |

---

## References

- [AWS Nova Multimodal Embeddings Blog](https://aws.amazon.com/blogs/aws/amazon-nova-multimodal-embeddings-now-available-in-amazon-bedrock/)
- [Amazon Nova Technical Report](https://www.amazon.science/publications/amazon-nova-multimodal-embeddings-technical-report-and-model-card)
- [LanguageBind Paper (arXiv)](https://arxiv.org/abs/2310.01852)
- [LanguageBind Audio on HuggingFace](https://huggingface.co/LanguageBind/LanguageBind_Audio)
- [SigLIP 2 Blog](https://huggingface.co/blog/siglip2)
- [SigLIP 2 Paper](https://arxiv.org/abs/2502.14786)
- [BGE-M3 on HuggingFace](https://huggingface.co/BAAI/bge-m3)
- [Sentence-Transformers Documentation](https://sbert.net/)
- [OpenAI Embeddings Pricing](https://platform.openai.com/docs/pricing)
- [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
