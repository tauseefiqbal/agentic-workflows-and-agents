"""Create MongoDB Atlas Search and Vector Search indexes programmatically."""

import asyncio
import logging
from pymongo import AsyncMongoClient
from pymongo.operations import SearchIndexModel
from src.settings import load_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def create_search_indexes() -> None:
    """
    Create vector search and text search indexes on the chunks collection.

    Requires:
        - Data already ingested into the chunks collection
        - MongoDB Atlas cluster (M0 free tier works)

    Raises:
        ConnectionFailure: If MongoDB connection fails
        OperationFailure: If index creation fails
    """
    settings = load_settings()
    client = AsyncMongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=10000)

    try:
        # Verify connection
        await client.admin.command("ping")
        logger.info("Connected to MongoDB Atlas")

        db = client[settings.mongodb_database]
        collection = db[settings.mongodb_collection_chunks]

        # Check that chunks collection has data
        count = await collection.count_documents({})
        if count == 0:
            logger.error(
                "No documents found in '%s.%s'. Run ingestion first: "
                "uv run python -m src.ingestion.ingest -d ./documents",
                settings.mongodb_database,
                settings.mongodb_collection_chunks,
            )
            return

        logger.info("Found %d chunks in collection", count)

        # List existing search indexes to avoid duplicates
        existing_indexes: list[str] = []
        cursor = await collection.list_search_indexes()
        async for idx in cursor:
            existing_indexes.append(idx["name"])
        logger.info("Existing search indexes: %s", existing_indexes or "(none)")

        # 1. Vector Search Index
        if settings.mongodb_vector_index not in existing_indexes:
            vector_index = SearchIndexModel(
                definition={
                    "fields": [
                        {
                            "type": "vector",
                            "path": "embedding",
                            "numDimensions": settings.embedding_dimension,
                            "similarity": "cosine",
                        }
                    ]
                },
                name=settings.mongodb_vector_index,
                type="vectorSearch",
            )
            result = await collection.create_search_index(vector_index)
            logger.info("Created vector search index: %s", result)
        else:
            logger.info("Vector search index '%s' already exists, skipping", settings.mongodb_vector_index)

        # 2. Atlas Full-Text Search Index
        if settings.mongodb_text_index not in existing_indexes:
            text_index = SearchIndexModel(
                definition={
                    "mappings": {
                        "dynamic": False,
                        "fields": {
                            "content": {
                                "type": "string",
                                "analyzer": "lucene.standard",
                            }
                        },
                    }
                },
                name=settings.mongodb_text_index,
                type="search",
            )
            result = await collection.create_search_index(text_index)
            logger.info("Created text search index: %s", result)
        else:
            logger.info("Text search index '%s' already exists, skipping", settings.mongodb_text_index)

        logger.info(
            "Done! Indexes may take 1-5 minutes to build. "
            "Check status in Atlas UI: Database → Search and Vector Search"
        )

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(create_search_indexes())
