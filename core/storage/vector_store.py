# START OF FILE core/storage/vector_store.py
"""
HAI-Net Vector Database Integration
Constitutional compliance: Privacy First + Community Focus
Vector storage for AI knowledge with constitutional protection
"""

import json
import time
import hashlib
import secrets
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from dataclasses import dataclass
import threading
import sqlite3
from contextlib import contextmanager

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.identity.did import ConstitutionalViolationError
from .database import ConstitutionalMetadata, DataRecord


@dataclass
class VectorDocument:
    """Represents a document with vector embedding"""
    doc_id: str
    content: str
    embedding: np.ndarray
    metadata: Dict[str, Any]
    created_at: float
    constitutional_version: str
    privacy_level: str = "private"
    user_consent: bool = False


@dataclass
class VectorSearchResult:
    """Search result with similarity score"""
    document: VectorDocument
    similarity_score: float
    distance: float


class ConstitutionalVectorStore:
    """
    Constitutional compliance vector database
    Local vector storage with privacy protection and constitutional enforcement
    """
    
    def __init__(self, store_path: Path, dimension: int = 384):
        self.store_path = store_path
        self.dimension = dimension
        self.logger = get_logger("storage.vector_store")
        
        # Constitutional compliance
        self.constitutional_version = "1.0"
        self.max_document_size = 1024 * 1024  # 1MB max per document
        self.max_documents = 100000  # Community-focused: reasonable limits
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Vector storage (in-memory for now, can be upgraded to Qdrant/FAISS later)
        self.documents: Dict[str, VectorDocument] = {}
        self.embeddings_matrix: Optional[np.ndarray] = None
        self.doc_id_to_index: Dict[str, int] = {}
        self.index_to_doc_id: Dict[int, str] = {}
        
        # Initialize storage
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize vector storage with constitutional compliance"""
        try:
            # Create storage directory
            self.store_path.mkdir(parents=True, exist_ok=True)
            
            # Load existing data if available
            self._load_stored_data()
            
            self.logger.log_privacy_event(
                "vector_store_initialized",
                "local_embeddings_storage",
                user_consent=True
            )
            
        except Exception as e:
            raise ConstitutionalViolationError(f"Vector store initialization failed: {e}")
    
    def add_document(self, doc_id: str, content: str, embedding: np.ndarray, 
                    metadata: Optional[Dict[str, Any]] = None,
                    privacy_level: str = "private", user_consent: bool = False) -> bool:
        """
        Add document with vector embedding
        Constitutional compliance: Privacy First + User consent
        
        Args:
            doc_id: Unique document identifier
            content: Document text content
            embedding: Vector embedding (numpy array)
            metadata: Optional document metadata
            privacy_level: Privacy classification
            user_consent: Whether user has consented to storage
            
        Returns:
            True if added successfully
        """
        try:
            with self._lock:
                # Validate constitutional compliance
                if not self._validate_document_compliance(content, privacy_level, user_consent):
                    raise ConstitutionalViolationError("Document violates constitutional principles")
                
                # Check storage limits (community focus: reasonable resource usage)
                if len(self.documents) >= self.max_documents:
                    self.logger.log_violation("storage_limit_exceeded", {
                        "current_count": len(self.documents),
                        "max_allowed": self.max_documents
                    })
                    return False
                
                # Validate embedding dimensions
                if len(embedding.shape) != 1 or embedding.shape[0] != self.dimension:
                    raise ConstitutionalViolationError(f"Embedding dimension mismatch: expected {self.dimension}")
                
                # Create document
                document = VectorDocument(
                    doc_id=doc_id,
                    content=content,
                    embedding=embedding.copy(),  # Constitutional principle: data isolation
                    metadata=metadata or {},
                    created_at=time.time(),
                    constitutional_version=self.constitutional_version,
                    privacy_level=privacy_level,
                    user_consent=user_consent
                )
                
                # Store document
                self.documents[doc_id] = document
                
                # Update embeddings matrix
                self._rebuild_embeddings_matrix()
                
                # Persist to disk
                self._save_document_to_disk(document)
                
                self.logger.log_privacy_event(
                    "document_added",
                    f"vector_embedding_{privacy_level}",
                    user_consent=user_consent
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to add document: {e}")
            return False
    
    def search_similar(self, query_embedding: np.ndarray, k: int = 10, 
                      privacy_level_filter: Optional[str] = None,
                      user_consent_verified: bool = False) -> List[VectorSearchResult]:
        """
        Search for similar documents using vector similarity
        Constitutional compliance: Privacy filtering
        
        Args:
            query_embedding: Query vector embedding
            k: Number of results to return
            privacy_level_filter: Filter by privacy level
            user_consent_verified: Whether user consent has been verified
            
        Returns:
            List of search results ordered by similarity
        """
        try:
            with self._lock:
                if self.embeddings_matrix is None or len(self.documents) == 0:
                    return []
                
                # Validate query embedding
                if len(query_embedding.shape) != 1 or query_embedding.shape[0] != self.dimension:
                    raise ConstitutionalViolationError(f"Query embedding dimension mismatch")
                
                # Constitutional filter: privacy-first access control
                eligible_docs = []
                eligible_embeddings = []
                
                for doc_id, document in self.documents.items():
                    # Privacy filter
                    if privacy_level_filter and document.privacy_level != privacy_level_filter:
                        continue
                    
                    # Constitutional compliance: personal data requires consent
                    if document.privacy_level == "private" and not user_consent_verified:
                        continue
                    
                    eligible_docs.append(document)
                    eligible_embeddings.append(document.embedding)
                
                if not eligible_embeddings:
                    return []
                
                # Calculate similarities using cosine similarity
                eligible_matrix = np.vstack(eligible_embeddings)
                
                # Normalize vectors for cosine similarity
                query_norm = query_embedding / np.linalg.norm(query_embedding)
                doc_norms = eligible_matrix / np.linalg.norm(eligible_matrix, axis=1, keepdims=True)
                
                # Calculate cosine similarities
                similarities = np.dot(doc_norms, query_norm)
                
                # Get top-k results
                top_indices = np.argsort(similarities)[::-1][:k]
                
                results = []
                for idx in top_indices:
                    document = eligible_docs[idx]
                    similarity = similarities[idx]
                    distance = 1.0 - similarity  # Convert to distance
                    
                    result = VectorSearchResult(
                        document=document,
                        similarity_score=float(similarity),
                        distance=float(distance)
                    )
                    results.append(result)
                
                # Create audit trail
                self.logger.log_privacy_event(
                    "vector_search_performed",
                    f"results_{len(results)}",
                    user_consent=user_consent_verified
                )
                
                return results
                
        except Exception as e:
            self.logger.error(f"Vector search failed: {e}")
            return []
    
    def get_document(self, doc_id: str, user_consent_verified: bool = False) -> Optional[VectorDocument]:
        """
        Retrieve specific document by ID
        Constitutional compliance: Privacy protection
        
        Args:
            doc_id: Document identifier
            user_consent_verified: Whether user consent has been verified
            
        Returns:
            Document if found and accessible, None otherwise
        """
        try:
            with self._lock:
                if doc_id not in self.documents:
                    return None
                
                document = self.documents[doc_id]
                
                # Constitutional compliance check
                if document.privacy_level == "private" and not user_consent_verified:
                    self.logger.log_violation("unauthorized_document_access", {
                        "doc_id": doc_id,
                        "reason": "User consent not verified for private document"
                    })
                    return None
                
                self.logger.log_privacy_event(
                    "document_retrieved",
                    document.privacy_level,
                    user_consent=user_consent_verified
                )
                
                return document
                
        except Exception as e:
            self.logger.error(f"Document retrieval failed: {e}")
            return None
    
    def delete_document(self, doc_id: str, user_consent_verified: bool = False) -> bool:
        """
        Delete document (right to be forgotten)
        Constitutional compliance: Human rights protection
        
        Args:
            doc_id: Document identifier
            user_consent_verified: Whether user consent has been verified
            
        Returns:
            True if deleted successfully
        """
        try:
            with self._lock:
                if doc_id not in self.documents:
                    return False
                
                document = self.documents[doc_id]
                
                # Constitutional compliance: user consent for personal data
                if document.privacy_level == "private" and not user_consent_verified:
                    self.logger.log_violation("unauthorized_document_deletion", {
                        "doc_id": doc_id,
                        "reason": "User consent not verified for private document deletion"
                    })
                    return False
                
                # Remove from memory
                del self.documents[doc_id]
                
                # Rebuild embeddings matrix
                self._rebuild_embeddings_matrix()
                
                # Remove from disk
                self._delete_document_from_disk(doc_id)
                
                self.logger.log_human_rights_event(
                    "document_deleted_user_request",
                    user_control=True
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Document deletion failed: {e}")
            return False
    
    def update_document_metadata(self, doc_id: str, metadata: Dict[str, Any], 
                                user_consent_verified: bool = False) -> bool:
        """
        Update document metadata
        Constitutional compliance: User control
        
        Args:
            doc_id: Document identifier
            metadata: New metadata
            user_consent_verified: Whether user consent has been verified
            
        Returns:
            True if updated successfully
        """
        try:
            with self._lock:
                if doc_id not in self.documents:
                    return False
                
                document = self.documents[doc_id]
                
                # Constitutional compliance check
                if document.privacy_level == "private" and not user_consent_verified:
                    return False
                
                # Update metadata
                document.metadata.update(metadata)
                
                # Persist changes
                self._save_document_to_disk(document)
                
                self.logger.log_privacy_event(
                    "document_metadata_updated",
                    document.privacy_level,
                    user_consent=user_consent_verified
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Metadata update failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        with self._lock:
            privacy_counts = {}
            for doc in self.documents.values():
                privacy_counts[doc.privacy_level] = privacy_counts.get(doc.privacy_level, 0) + 1
            
            return {
                "total_documents": len(self.documents),
                "dimension": self.dimension,
                "privacy_level_counts": privacy_counts,
                "max_documents": self.max_documents,
                "constitutional_version": self.constitutional_version,
                "storage_path": str(self.store_path)
            }
    
    def cleanup_expired_documents(self, max_age_seconds: int = 86400 * 30) -> int:
        """
        Clean up old documents based on age
        Constitutional principle: Data minimization
        
        Args:
            max_age_seconds: Maximum age in seconds (default: 30 days)
            
        Returns:
            Number of documents cleaned up
        """
        try:
            with self._lock:
                current_time = time.time()
                expired_docs = []
                
                for doc_id, document in self.documents.items():
                    if current_time - document.created_at > max_age_seconds:
                        expired_docs.append(doc_id)
                
                # Remove expired documents
                cleanup_count = 0
                for doc_id in expired_docs:
                    if self.delete_document(doc_id, user_consent_verified=True):
                        cleanup_count += 1
                
                if cleanup_count > 0:
                    self.logger.log_privacy_event(
                        "expired_documents_cleanup",
                        f"count_{cleanup_count}",
                        user_consent=True
                    )
                
                return cleanup_count
                
        except Exception as e:
            self.logger.error(f"Document cleanup failed: {e}")
            return 0
    
    def _validate_document_compliance(self, content: str, privacy_level: str, user_consent: bool) -> bool:
        """Validate document storage compliance with constitutional principles"""
        
        # Check content size
        if len(content.encode()) > self.max_document_size:
            return False
        
        # Privacy First: personal content requires consent
        if privacy_level == "private" and not user_consent:
            return False
        
        # Check for sensitive data patterns
        content_lower = content.lower()
        sensitive_patterns = ['password', 'private_key', 'secret', 'ssn', 'credit_card']
        if any(pattern in content_lower for pattern in sensitive_patterns):
            return False
        
        # Validate privacy level
        valid_levels = ['private', 'community', 'public']
        if privacy_level not in valid_levels:
            return False
        
        return True
    
    def _rebuild_embeddings_matrix(self):
        """Rebuild the embeddings matrix for efficient similarity search"""
        if not self.documents:
            self.embeddings_matrix = None
            self.doc_id_to_index.clear()
            self.index_to_doc_id.clear()
            return
        
        # Create mapping between doc_ids and matrix indices
        doc_ids = list(self.documents.keys())
        embeddings = [self.documents[doc_id].embedding for doc_id in doc_ids]
        
        self.embeddings_matrix = np.vstack(embeddings)
        self.doc_id_to_index = {doc_id: idx for idx, doc_id in enumerate(doc_ids)}
        self.index_to_doc_id = {idx: doc_id for idx, doc_id in enumerate(doc_ids)}
    
    def _save_document_to_disk(self, document: VectorDocument):
        """Save document to disk for persistence"""
        try:
            doc_file = self.store_path / f"{document.doc_id}.json"
            
            # Prepare data for serialization
            doc_data = {
                "doc_id": document.doc_id,
                "content": document.content,
                "embedding": document.embedding.tolist(),  # Convert numpy array to list
                "metadata": document.metadata,
                "created_at": document.created_at,
                "constitutional_version": document.constitutional_version,
                "privacy_level": document.privacy_level,
                "user_consent": document.user_consent
            }
            
            # Save to file
            with open(doc_file, 'w', encoding='utf-8') as f:
                json.dump(doc_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save document to disk: {e}")
    
    def _load_stored_data(self):
        """Load previously stored documents from disk"""
        try:
            if not self.store_path.exists():
                return
            
            loaded_count = 0
            for doc_file in self.store_path.glob("*.json"):
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        doc_data = json.load(f)
                    
                    # Reconstruct document
                    document = VectorDocument(
                        doc_id=doc_data["doc_id"],
                        content=doc_data["content"],
                        embedding=np.array(doc_data["embedding"]),
                        metadata=doc_data["metadata"],
                        created_at=doc_data["created_at"],
                        constitutional_version=doc_data["constitutional_version"],
                        privacy_level=doc_data["privacy_level"],
                        user_consent=doc_data["user_consent"]
                    )
                    
                    self.documents[document.doc_id] = document
                    loaded_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to load document {doc_file}: {e}")
                    continue
            
            # Rebuild embeddings matrix
            self._rebuild_embeddings_matrix()
            
            if loaded_count > 0:
                self.logger.info(f"Loaded {loaded_count} documents from disk")
                
        except Exception as e:
            self.logger.error(f"Failed to load stored data: {e}")
    
    def _delete_document_from_disk(self, doc_id: str):
        """Delete document file from disk"""
        try:
            doc_file = self.store_path / f"{doc_id}.json"
            if doc_file.exists():
                doc_file.unlink()
        except Exception as e:
            self.logger.error(f"Failed to delete document file: {e}")


class VectorStore:
    """
    High-level vector store manager for HAI-Net
    Manages multiple vector collections with constitutional compliance
    """
    
    def __init__(self, settings: HAINetSettings):
        self.settings = settings
        self.logger = get_logger("storage.vector_store_manager", settings)
        
        # Vector store paths
        self.models_dir = settings.models_dir
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Constitutional compliance
        self.constitutional_version = "1.0"
        
        # Vector store instances
        self.stores: Dict[str, ConstitutionalVectorStore] = {}
        
        # Initialize default stores
        self._initialize_default_stores()
    
    def _initialize_default_stores(self):
        """Initialize default vector store collections"""
        try:
            # Knowledge base store
            knowledge_path = self.models_dir / "knowledge_vectors"
            self.stores["knowledge"] = ConstitutionalVectorStore(knowledge_path)
            
            # Agent memory store
            memory_path = self.models_dir / "agent_memory_vectors"
            self.stores["memory"] = ConstitutionalVectorStore(memory_path)
            
            # Community content store
            community_path = self.models_dir / "community_vectors"
            self.stores["community"] = ConstitutionalVectorStore(community_path)
            
            self.logger.log_privacy_event(
                "vector_stores_initialized",
                "multiple_collections",
                user_consent=True
            )
            
        except Exception as e:
            raise ConstitutionalViolationError(f"Vector store manager initialization failed: {e}")
    
    def get_store(self, collection_name: str) -> Optional[ConstitutionalVectorStore]:
        """Get vector store by collection name"""
        return self.stores.get(collection_name)
    
    def create_store(self, collection_name: str, dimension: int = 384) -> ConstitutionalVectorStore:
        """Create new vector store collection"""
        store_path = self.models_dir / f"{collection_name}_vectors"
        store = ConstitutionalVectorStore(store_path, dimension)
        self.stores[collection_name] = store
        
        self.logger.log_community_event(
            f"vector_collection_created: {collection_name}",
            community_benefit=True
        )
        
        return store
    
    def store_knowledge(self, content: str, embedding: np.ndarray, 
                       metadata: Optional[Dict[str, Any]] = None,
                       user_consent: bool = True) -> bool:
        """Store knowledge with vector embedding"""
        doc_id = f"knowledge_{int(time.time())}_{secrets.token_hex(8)}"
        return self.stores["knowledge"].add_document(
            doc_id=doc_id,
            content=content,
            embedding=embedding,
            metadata=metadata,
            privacy_level="community",
            user_consent=user_consent
        )
    
    def store_agent_memory(self, agent_id: str, content: str, embedding: np.ndarray,
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store agent memory with vector embedding"""
        doc_id = f"agent_{agent_id}_{int(time.time())}_{secrets.token_hex(4)}"
        return self.stores["memory"].add_document(
            doc_id=doc_id,
            content=content,
            embedding=embedding,
            metadata=metadata or {"agent_id": agent_id},
            privacy_level="private",
            user_consent=True
        )
    
    def search_knowledge(self, query_embedding: np.ndarray, k: int = 10) -> List[VectorSearchResult]:
        """Search knowledge base"""
        return self.stores["knowledge"].search_similar(
            query_embedding=query_embedding,
            k=k,
            privacy_level_filter="community",
            user_consent_verified=True
        )
    
    def search_agent_memory(self, agent_id: str, query_embedding: np.ndarray, 
                           k: int = 10) -> List[VectorSearchResult]:
        """Search agent memory"""
        results = self.stores["memory"].search_similar(
            query_embedding=query_embedding,
            k=k,
            privacy_level_filter="private",
            user_consent_verified=True
        )
        
        # Filter by agent_id
        agent_results = []
        for result in results:
            if result.document.metadata.get("agent_id") == agent_id:
                agent_results.append(result)
        
        return agent_results
    
    def cleanup_all_stores(self) -> Dict[str, int]:
        """Clean up expired documents from all stores"""
        cleanup_results = {}
        
        for name, store in self.stores.items():
            cleanup_results[name] = store.cleanup_expired_documents()
        
        return cleanup_results
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all vector stores"""
        stats = {
            "constitutional_version": self.constitutional_version,
            "stores": {}
        }
        
        for name, store in self.stores.items():
            stats["stores"][name] = store.get_stats()
        
        return stats


def create_vector_store(settings: HAINetSettings) -> VectorStore:
    """
    Create and configure constitutional vector store manager
    
    Args:
        settings: HAI-Net settings
        
    Returns:
        Configured VectorStore instance
    """
    return VectorStore(settings)


if __name__ == "__main__":
    # Test the constitutional vector store system
    from core.config.settings import HAINetSettings
    
    print("HAI-Net Constitutional Vector Store Test")
    print("=" * 45)
    
    # Create test settings
    settings = HAINetSettings()
    
    # Create vector store manager
    vector_store = create_vector_store(settings)
    
    try:
        # Test knowledge storage
        test_embedding = np.random.rand(384)  # Random embedding for testing
        
        success = vector_store.store_knowledge(
            content="Constitutional AI principles guide HAI-Net development.",
            embedding=test_embedding,
            metadata={"topic": "constitutional_ai", "importance": "high"},
            user_consent=True
        )
        print(f"✅ Knowledge stored: {success}")
        
        # Test agent memory storage
        success = vector_store.store_agent_memory(
            agent_id="test_agent_001",
            content="Completed constitutional compliance check successfully.",
            embedding=np.random.rand(384),
            metadata={"task": "compliance_check", "result": "success"}
        )
        print(f"✅ Agent memory stored: {success}")
        
        # Test knowledge search
        search_results = vector_store.search_knowledge(
            query_embedding=test_embedding,
            k=5
        )
        print(f"🔍 Knowledge search results: {len(search_results)}")
        
        if search_results:
            print(f"   Top result similarity: {search_results[0].similarity_score:.3f}")
        
        # Test agent memory search
        memory_results = vector_store.search_agent_memory(
            agent_id="test_agent_001",
            query_embedding=np.random.rand(384),
            k=5
        )
        print(f"🧠 Agent memory search results: {len(memory_results)}")
        
        # Test statistics
        stats = vector_store.get_all_stats()
        print(f"📊 Vector store stats: {stats}")
        
        # Test cleanup
        cleanup_results = vector_store.cleanup_all_stores()
        print(f"🧹 Cleanup results: {cleanup_results}")
        
        print("\n🎉 Constitutional Vector Store System Working!")
        
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
