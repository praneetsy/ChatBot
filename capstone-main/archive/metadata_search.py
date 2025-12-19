from dataclasses import dataclass
from typing import List, Dict, Any, Set, Tuple
from langchain_core.messages import HumanMessage, SystemMessage
import json

@dataclass
class SearchResult:
    content: str
    metadata: Dict[str, Any]
    score: float
    agent: str

class MetadataSearchEngine:
    def __init__(self, db, folder_map: Dict[str, List[str]], llm):
        self.db = db
        self.folder_map = folder_map
        self.llm = llm
        self.document_metadata = self._build_metadata_map()
    
    def _build_metadata_map(self) -> Dict[str, Dict[str, Any]]:
        metadata_map = {}
        for category, documents in self.folder_map.items():
            for doc in documents:
                # Extract title from document content
                title = self._extract_title(doc)
                metadata_map[doc] = {
                    "category": category,
                    "title": title,
                    "content_length": len(doc),
                    "agent": self._map_category_to_agent(category)
                }
        return metadata_map
    
    def _extract_title(self, content: str) -> str:
        lines = content.split('\n')
        for line in lines:
            if line.startswith('Title:'):
                return line.replace('Title:', '').strip()
        return ""
    
    def _map_category_to_agent(self, category: str) -> str:
        return category.lower()
    
    def search_with_metadata(self, query: str, top_k: int = 3) -> List[SearchResult]:
        # Perform similarity search
        search_results = self.db.similarity_search_with_score(query, k=top_k)
        
        enhanced_results = []
        for doc, score in search_results:
            metadata = self.document_metadata.get(doc.page_content, {})
            enhanced_results.append(
                SearchResult(
                    content=doc.page_content,
                    metadata=metadata,
                    score=score,
                    agent=metadata.get("agent", "internet_search")
                )
            )
        
        return enhanced_results
    
    def get_relevant_agents(self, results: List[SearchResult]) -> Set[str]:
        return {result.agent for result in results}
    
    def route_query(self, query: str, current_agent: str = "internet_search") -> Tuple[str, List[SearchResult]]:
        # First, perform metadata-enabled search
        search_results = self.search_with_metadata(query)
        relevant_agents = self.get_relevant_agents(search_results)
        
        # Create system message for routing
        system_message = SystemMessage(content=f"""
        Determine if the question needs redirection to another agent or if the current agent can answer it.
        The current agent is {current_agent}.
        Based on similarity search, these agents may have relevant information: {relevant_agents}
        Available agents: internet_search, customer_database_search, organizational_information
        ONLY CHOOSE FROM THESE AGENTS. DO NOT CHOOSE ANY OTHER AGENT.
        """)
        
        # Create conversation history
        conversation = [
            system_message,
            HumanMessage(content=query)
        ]
        
        # Get routing decision
        response = self.llm.invoke(conversation)
        routing_decision = json.loads(response.content)
        
        return routing_decision["agent"], search_results