"""
MCP (Model Context Protocol) Server for Medical Dataset Ingestion

This module provides an MCP-compatible server for ingesting third-party
medical datasets into the RAG system.
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from langchain_core.documents import Document

try:
    from mcp import Server, StdioServerParameters
    from mcp.server import NotificationOptions
    from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from src.helper import load_json_file, load_csv_file, load_mixed_data


@dataclass
class DatasetMetadata:
    """Metadata for ingested datasets."""
    name: str
    source_path: str
    format: str  # 'json', 'csv', 'pdf', 'mixed'
    record_count: int
    ingestion_date: str
    schema: Optional[Dict[str, Any]] = None


class MedicalDatasetMCPServer:
    """MCP Server for ingesting medical datasets."""
    
    # Class-level storage for persistence within a process
    _shared_datasets: List[DatasetMetadata] = []
    _shared_documents: List[Document] = []
    
    def __init__(self, data_dir: str = "Data/"):
        self.data_dir = Path(data_dir)
        self.metadata_file = Path("Data/.mcp_metadata.json")
        
        # Use class-level storage for in-memory persistence
        if not hasattr(self.__class__, '_initialized'):
            self.__class__._initialized = True
            self.__class__._shared_datasets = []
            self.__class__._shared_documents = []
            # Load from disk if exists
            self._load_metadata_from_disk()
        
        # Instance references point to class-level storage
        self.ingested_datasets = self.__class__._shared_datasets
        self.documents = self.__class__._shared_documents
    
    def _load_metadata_from_disk(self):
        """Load dataset metadata from disk."""
        if self.metadata_file.exists():
            try:
                import json
                from datetime import datetime
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        metadata = DatasetMetadata(
                            name=item['name'],
                            source_path=item['source_path'],
                            format=item['format'],
                            record_count=item['record_count'],
                            ingestion_date=item['ingestion_date'],
                            schema=item.get('schema')
                        )
                        self.__class__._shared_datasets.append(metadata)
            except Exception as e:
                print(f"Warning: Could not load metadata from disk: {e}")
    
    def _save_metadata_to_disk(self):
        """Save dataset metadata to disk."""
        try:
            import json
            self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
            data = []
            for metadata in self.__class__._shared_datasets:
                data.append({
                    'name': metadata.name,
                    'source_path': metadata.source_path,
                    'format': metadata.format,
                    'record_count': metadata.record_count,
                    'ingestion_date': metadata.ingestion_date,
                    'schema': metadata.schema
                })
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save metadata to disk: {e}")
        
    def ingest_dataset(self, file_path: str, format_type: Optional[str] = None) -> DatasetMetadata:
        """
        Ingest a dataset file.
        
        Args:
            file_path: Path to the dataset file
            format_type: Optional format hint ('json', 'csv', 'pdf', 'auto')
        
        Returns:
            DatasetMetadata object
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Dataset file not found: {file_path}")
        
        # Auto-detect format if not specified
        if format_type is None or format_type == 'auto':
            format_type = file_path_obj.suffix[1:].lower()
        
        documents = []
        
        if format_type == 'json':
            documents = load_json_file(str(file_path_obj))
        elif format_type == 'csv':
            documents = load_csv_file(str(file_path_obj))
        elif format_type == 'pdf':
            from src.helper import load_pdf_file
            documents = load_pdf_file(str(file_path_obj.parent))
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        # Store documents
        self.documents.extend(documents)
        
        # Create metadata
        from datetime import datetime
        metadata = DatasetMetadata(
            name=file_path_obj.stem,
            source_path=str(file_path_obj),
            format=format_type,
            record_count=len(documents),
            ingestion_date=datetime.now().isoformat()
        )
        
        self.ingested_datasets.append(metadata)
        
        # Save metadata to disk for persistence across processes
        self._save_metadata_to_disk()
        
        return metadata
    
    def ingest_from_url(self, url: str, format_type: str = 'json') -> DatasetMetadata:
        """
        Ingest dataset from a URL (requires download).
        
        Args:
            url: URL to the dataset
            format_type: Expected format
        
        Returns:
            DatasetMetadata object
        """
        import urllib.request
        import tempfile
        
        # Download file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format_type}") as tmp_file:
            urllib.request.urlretrieve(url, tmp_file.name)
            return self.ingest_dataset(tmp_file.name, format_type)
    
    def get_ingested_datasets(self) -> List[Dict[str, Any]]:
        """Get list of all ingested datasets."""
        return [
            {
                "name": ds.name,
                "source_path": ds.source_path,
                "format": ds.format,
                "record_count": ds.record_count,
                "ingestion_date": ds.ingestion_date
            }
            for ds in self.ingested_datasets
        ]
    
    def get_documents(self) -> List[Document]:
        """Get all ingested documents."""
        return self.documents
    
    def search_documents(self, query: str, dataset_name: str = None) -> List[Document]:
        """
        Search ingested documents for relevant content.
        
        Args:
            query: Search query (e.g., "hypertension symptoms")
            dataset_name: Optional specific dataset to search in
            
        Returns:
            List of relevant documents/chunks matching query
        """
        if not self.documents:
            return []
        
        # Simple keyword search in documents
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for doc in self.documents:
            content_lower = doc.page_content.lower()
            
            # Check if dataset matches (if specified)
            if dataset_name:
                doc_dataset = doc.metadata.get('source', '').lower()
                if dataset_name.lower() not in doc_dataset:
                    continue
            
            # Count matching words
            matching_words = sum(1 for word in query_words if word in content_lower)
            
            # Include if has matching words
            if matching_words > 0:
                # Add relevance score to metadata
                doc.metadata['relevance_score'] = matching_words / len(query_words)
                results.append(doc)
        
        # Sort by relevance
        results.sort(key=lambda x: x.metadata.get('relevance_score', 0), reverse=True)
        
        return results[:10]  # Return top 10 results
    
    def clear_documents(self):
        """Clear all ingested documents."""
        self.documents.clear()
        self.ingested_datasets.clear()


# MCP Server Implementation (if MCP SDK is available)
if MCP_AVAILABLE:
    async def handle_list_resources() -> List[Resource]:
        """List available dataset resources."""
        server = MedicalDatasetMCPServer()
        datasets = server.get_ingested_datasets()
        
        resources = []
        for ds in datasets:
            resources.append(
                Resource(
                    uri=f"dataset://{ds['name']}",
                    name=ds['name'],
                    description=f"Medical dataset: {ds['name']} ({ds['format']}, {ds['record_count']} records)",
                    mimeType="application/json"
                )
            )
        return resources
    
    async def handle_read_resource(uri: str) -> str:
        """Read a dataset resource."""
        # Extract dataset name from URI
        dataset_name = uri.replace("dataset://", "")
        server = MedicalDatasetMCPServer()
        
        # Find and return dataset
        for ds in server.ingested_datasets:
            if ds.name == dataset_name:
                with open(ds.source_path, 'r') as f:
                    return f.read()
        
        raise ValueError(f"Dataset not found: {dataset_name}")
    
    async def handle_ingest_dataset_tool(arguments: Dict[str, Any]) -> str:
        """Tool to ingest a new dataset."""
        file_path = arguments.get("file_path")
        format_type = arguments.get("format_type", "auto")
        
        if not file_path:
            return json.dumps({"error": "file_path is required"})
        
        server = MedicalDatasetMCPServer()
        try:
            metadata = server.ingest_dataset(file_path, format_type)
            return json.dumps({
                "status": "success",
                "dataset": {
                    "name": metadata.name,
                    "format": metadata.format,
                    "record_count": metadata.record_count
                }
            })
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def create_mcp_server():
        """Create and configure MCP server."""
        server = Server("medical-dataset-ingestion")
        
        # Register resources
        server.list_resources(handle_list_resources)
        server.read_resource(handle_read_resource)
        
        # Register tools
        server.list_tools(lambda: [
            Tool(
                name="ingest_dataset",
                description="Ingest a medical dataset file (JSON, CSV, or PDF) into the system",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the dataset file"
                        },
                        "format_type": {
                            "type": "string",
                            "enum": ["json", "csv", "pdf", "auto"],
                            "description": "Format type (auto-detect if not specified)"
                        }
                    },
                    "required": ["file_path"]
                }
            )
        ])
        
        server.call_tool("ingest_dataset", handle_ingest_dataset_tool)
        
        return server


# Standalone function for non-MCP usage
def ingest_third_party_dataset(file_path: str, format_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Standalone function to ingest a third-party dataset.
    
    Args:
        file_path: Path to dataset file
        format_type: Optional format hint
    
    Returns:
        Dictionary with ingestion results
    """
    server = MedicalDatasetMCPServer()
    metadata = server.ingest_dataset(file_path, format_type)
    
    return {
        "success": True,
        "metadata": {
            "name": metadata.name,
            "source_path": metadata.source_path,
            "format": metadata.format,
            "record_count": metadata.record_count,
            "ingestion_date": metadata.ingestion_date
        },
        "documents": len(server.documents)
    }


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        format_type = sys.argv[2] if len(sys.argv) > 2 else None
        
        result = ingest_third_party_dataset(file_path, format_type)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python mcp_server.py <file_path> [format_type]")
        print("Example: python mcp_server.py data/medical_qa.json json")
