import os
import json
from typing import Dict, List, Optional

# Knowledge Base Storage
class KnowledgeBase:
    def __init__(self, file_path: str = "knowledge_base.json"):
        self.file_path = file_path
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                return json.load(f)
        return {"concepts": {}, "relationships": []}
    
    def save_data(self):
        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=2)
    
    def add_concept(self, name: str, attributes: Dict):
        """Add or update a concept in the knowledge base"""
        self.data["concepts"][name] = attributes
        self.save_data()
    
    def add_relationship(self, source: str, relation: str, target: str):
        """Add a relationship between concepts"""
        rel = {"source": source, "relation": relation, "target": target}
        if rel not in self.data["relationships"]:
            self.data["relationships"].append(rel)
            self.save_data()
    
    def query_concept(self, name: str) -> Optional[Dict]:
        """Query information about a specific concept"""
        return self.data["concepts"].get(name)
    
    def query_relationships(self, concept: str) -> List[Dict]:
        """Find all relationships involving a concept"""
        return [
            rel for rel in self.data["relationships"] 
            if rel["source"] == concept or rel["target"] == concept
        ]
    
    def query_by_attribute(self, attribute: str, value: str) -> List[str]:
        """Find concepts that have a specific attribute value"""
        return [
            name for name, attrs in self.data["concepts"].items()
            if attrs.get(attribute) == value
        ]
