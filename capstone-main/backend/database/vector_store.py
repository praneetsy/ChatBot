from langchain_community.vectorstores import SQLiteVSS
from documents.embeddings import HTTPEmbeddingModel
from chromadb.config import Settings
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
import uuid


class VectorStore:
    def add_texts(self, texts, metadata):
        raise NotImplementedError

    def similarity_search_docs(self, query_text, k=5):
        raise NotImplementedError

    def add_agent_metadata(self, agent_name, metadata):
        raise NotImplementedError

    def similarity_search_agents(self, query_text, k=5):
        raise NotImplementedError


class SQLLiteVectorStore(VectorStore):
    def __init__(self, db_path: str, embedding_function=None):
        self.db_path = db_path
        connection = SQLiteVSS.create_connection(db_file=db_path)
        if embedding_function is None:
            embedding_function = HTTPEmbeddingModel()

        self.db = SQLiteVSS(
            table="embeddings", embedding=embedding_function, connection=connection
        )
        self.agent_db = SQLiteVSS(
            table="agents", connection=connection, embedding=embedding_function
        )

    def add_texts(self, texts, filename):
        self.db.add_texts(
            texts, metadata=[{"source": "user", "filename": filename} for _ in texts]
        )

    def similarity_search_docs(self, query_text, k=5):
        return self.db.similarity_search(query_text, k)

    def add_agent_metadata(self, agent_name, metadata, filename):
        self.agent_db.add_texts(
            [
                metadata["capabilities"],
                metadata["description"],
                metadata["specialization keywords"],
            ],
            filename=agent_name,
            metadatas=[
                {"agent_name": agent_name, "filename": filename},
            ],
        )

    def similarity_search_agents(self, query_text, k=5):
        print("Searching for similar agents...")
        print("Query:", query_text)
        print("k:", k)
        try:
            return self.agent_db.similarity_search_with_score(query_text, k)
        except Exception as e:
            print("Faiss error:", e)
            return None


class ChromaDBVectorStore(VectorStore):
    def __init__(self, db_path: str, embedding_function=None):
        self.db_path = db_path

        # Initialize the ChromaDB client
        self.client = PersistentClient(path=db_path)

        # Set up embedding function
        if embedding_function is None:
            embedding_function = DefaultEmbeddingFunction()

        # Create or get collections for documents and agents
        self.docs_collection = self.client.get_or_create_collection(
            name="documents", embedding_function=embedding_function
        )
        self.agents_collection = self.client.get_or_create_collection(
            name="agents", embedding_function=embedding_function
        )

    def add_texts(self, texts, filename):
        # Add documents to the `documents` collection
        self.docs_collection.add(
            documents=texts,
            metadatas=[{"source": "user", "filename": filename} for _ in texts],
            ids=[f"{filename}_{i}" for i in range(len(texts))],
        )

    def similarity_search_docs(self, query_text, k=5):
        # Perform similarity search on the `documents` collection
        results = self.docs_collection.query(query_texts=[query_text], n_results=k)
        return results

    def add_agent_metadata(self, agent_name, metadata, filename):
        # Add agent metadata to the `agents` collection
        texts = [
            metadata["capabilities"],
            metadata["description"],
            metadata["keywords"],
        ]
        metadatas = [
            {"agent_name": agent_name, "filename": filename, "type": "capabilities"},
            {"agent_name": agent_name, "filename": filename, "type": "description"},
            {"agent_name": agent_name, "filename": filename, "type": "keywords"},
        ]
        uuid_str = str(uuid.uuid4())
        self.agents_collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=[
                f"{agent_name}_capabilities_{uuid_str}",
                f"{agent_name}_description_{uuid_str}",
                f"{agent_name}_keywords_{uuid_str}",
            ],
        )

    def similarity_search_agents(self, query_text, k=5):
        print("Searching for similar agents...")
        print("Query:", query_text)
        print("k:", k)
        try:
            results = self.agents_collection.query(
                query_texts=[query_text], n_results=k
            )
            threshold = 1.5  # Set your desired threshold
            filtered_results = {
                'ids': [],
                'documents': [],
                'metadatas': [],
                'distances': []
            }

            # Iterate through the results
            for i, distances in enumerate(results['distances']):
                for j, distance in enumerate(distances):
                    if distance <= threshold:
                        # Append the filtered items
                        filtered_results['ids'].append(results['ids'][i][j])
                        filtered_results['documents'].append(results['documents'][i][j])
                        filtered_results['metadatas'].append(results['metadatas'][i][j])
                        filtered_results['distances'].append(distance)
            print("Filtered results:", filtered_results)
            return filtered_results
        except Exception as e:
            print("ChromaDB error:", e)
            return None
