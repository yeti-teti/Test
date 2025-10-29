"""
MCP Client for Flask app to interact with MCP server for dataset ingestion.

This module provides a client interface that can be used by the Flask app
to ingest third-party datasets during chat interactions.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path

from src.mcp_server import ingest_third_party_dataset, MCP_AVAILABLE


class MCPDatasetClient:
    """MCP Client for dataset ingestion from Flask app."""
    
    def __init__(self):
        """Initialize MCP client."""
        self.mcp_available = MCP_AVAILABLE
    
    def ingest_dataset(self, file_path: str, format_type: str = "auto") -> Dict[str, Any]:
        """
        Ingest a dataset file.
        
        Args:
            file_path: Path to the dataset file (relative to project root or absolute)
            format_type: Format type ('json', 'csv', 'pdf', 'auto')
        
        Returns:
            Dictionary with ingestion results
        """
        try:
            # Resolve file path - check if it's relative to Data/ or absolute
            file_path_obj = Path(file_path)
            
            # If not absolute, try Data/ directory first
            if not file_path_obj.is_absolute():
                project_root = Path(__file__).parent.parent
                data_path = project_root / "Data" / file_path_obj
                if data_path.exists():
                    file_path_obj = data_path
                elif (project_root / file_path_obj).exists():
                    file_path_obj = project_root / file_path_obj
            
            if not file_path_obj.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}. Please provide a valid file path."
                }
            
            # Use persistent server instance for ingestion
            server = get_mcp_server_instance()
            metadata = server.ingest_dataset(str(file_path_obj), format_type)
            
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
            
        except FileNotFoundError as e:
            return {
                "success": False,
                "error": f"File not found: {str(e)}"
            }
        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid format: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error during ingestion: {str(e)}"
            }
    
    def list_datasets(self) -> Dict[str, Any]:
        """
        List all ingested datasets.
        
        Returns:
            Dictionary with list of datasets
        """
        try:
            # Use persistent server instance
            server = get_mcp_server_instance()
            datasets = server.get_ingested_datasets()
            
            return {
                "success": True,
                "datasets": datasets,
                "count": len(datasets)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error listing datasets: {str(e)}"
            }


# Global client instance
_mcp_client = None
_mcp_server_instance = None  # Persistent server instance

def get_mcp_client() -> MCPDatasetClient:
    """Get or create MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPDatasetClient()
    return _mcp_client

def get_mcp_server_instance():
    """Get persistent MCP server instance."""
    global _mcp_server_instance
    if _mcp_server_instance is None:
        from src.mcp_server import MedicalDatasetMCPServer
        _mcp_server_instance = MedicalDatasetMCPServer()
    return _mcp_server_instance

