"""Chroma implementation of VectorStore. Requires the ``chroma`` extra."""

from __future__ import annotations

from groundedrag.schemas import Chunk


class ChromaStore:
    """Persists chunks and vectors in a local, embedded Chroma collection.

    Chroma is given pre-computed vectors (groundedrag always owns embedding
    via an :class:`~groundedrag.embeddings.base.Embedder`), so no embedding
    function is configured on the collection itself.
    """

    def __init__(
        self,
        collection_name: str = "groundedrag",
        persist_dir: str | None = None,
    ) -> None:
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self._collection = None

    def _get_collection(self):
        if self._collection is None:
            try:
                import chromadb
            except ImportError as exc:
                raise ImportError(
                    "ChromaStore requires the 'chromadb' package. "
                    "Install it with: pip install groundedrag[chroma]"
                ) from exc
            client = (
                chromadb.PersistentClient(path=self.persist_dir)
                if self.persist_dir
                else chromadb.EphemeralClient()
            )
            self._collection = client.get_or_create_collection(self.collection_name)
        return self._collection

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have the same length")
        if not chunks:
            return
        collection = self._get_collection()
        collection.upsert(
            ids=[chunk.id for chunk in chunks],
            embeddings=vectors,
            documents=[chunk.text for chunk in chunks],
            metadatas=[{"document_id": chunk.document_id, **chunk.metadata} for chunk in chunks],
        )

    def query(
        self,
        vector: list[float],
        *,
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[Chunk]:
        collection = self._get_collection()
        where = {"document_id": {"$in": document_ids}} if document_ids is not None else None
        result = collection.query(
            query_embeddings=[vector],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas"],
        )
        if not result["ids"] or not result["ids"][0]:
            return []
        chunks = []
        for chunk_id, text, metadata in zip(
            result["ids"][0], result["documents"][0], result["metadatas"][0], strict=True
        ):
            metadata = dict(metadata)
            document_id = metadata.pop("document_id")
            chunks.append(
                Chunk(id=chunk_id, document_id=document_id, text=text, metadata=metadata)
            )
        return chunks
