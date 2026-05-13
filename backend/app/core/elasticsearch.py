"""PulseStack AI — Elasticsearch Client."""

from elasticsearch import AsyncElasticsearch

from app.core.config import get_settings

settings = get_settings()

es_client = AsyncElasticsearch(
    hosts=[settings.ELASTICSEARCH_URL],
    request_timeout=30,
    max_retries=3,
    retry_on_timeout=True,
)

# Log index mapping template
LOG_INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "timestamp": {"type": "date"},
            "org_id": {"type": "keyword"},
            "service": {"type": "keyword"},
            "level": {"type": "keyword"},
            "message": {"type": "text", "analyzer": "standard"},
            "source": {"type": "keyword"},
            "host": {"type": "keyword"},
            "environment": {"type": "keyword"},
            "trace_id": {"type": "keyword"},
            "span_id": {"type": "keyword"},
            "metadata": {"type": "object", "enabled": True},
        }
    },
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "index.lifecycle.name": "logs-policy",
    },
}


async def ensure_log_index() -> None:
    """Create the log index if it doesn't exist."""
    index_name = settings.ES_LOG_INDEX
    exists = await es_client.indices.exists(index=index_name)
    if not exists:
        await es_client.indices.create(index=index_name, body=LOG_INDEX_MAPPING)


async def get_es() -> AsyncElasticsearch:
    """FastAPI dependency — returns the async ES client."""
    return es_client
