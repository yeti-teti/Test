#!/usr/bin/env python3
"""
Script to ingest third-party medical datasets using MCP server.

Usage:
    python ingest_dataset.py <file_path> [format_type]
    python ingest_dataset.py --mcp-server  # Start MCP server

Examples:
    python ingest_dataset.py Data/medical_conditions.json json
    python ingest_dataset.py Data/medical_data.csv csv
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_server import ingest_third_party_dataset, MedicalDatasetMCPServer, MCP_AVAILABLE
import json


def main():
    parser = argparse.ArgumentParser(description='Ingest medical datasets via MCP')
    parser.add_argument('file_path', nargs='?', help='Path to dataset file')
    parser.add_argument('format_type', nargs='?', choices=['json', 'csv', 'pdf', 'auto'], 
                       default='auto', help='Dataset format type')
    parser.add_argument('--mcp-server', action='store_true', 
                       help='Start MCP server (requires MCP SDK)')
    parser.add_argument('--list', action='store_true',
                       help='List all ingested datasets')
    
    args = parser.parse_args()
    
    if args.mcp_server:
        if not MCP_AVAILABLE:
            print("Error: MCP SDK not installed. Install with: pip install mcp")
            sys.exit(1)
        
        # Lazily import server factory and run over stdio
        try:
            import asyncio
            from src.mcp_server import create_mcp_server  # only defined when MCP is available
            from mcp import StdioServerParameters
        except Exception as e:
            print(f"Failed to initialize MCP server: {e}")
            sys.exit(1)
        
        print("Starting MCP server on stdio... (waiting for MCP client)")
        try:
            server = create_mcp_server()
            asyncio.run(server.run(StdioServerParameters()))
        except KeyboardInterrupt:
            print("MCP server stopped")
        except Exception as e:
            print(f"MCP server error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        return
    
    if args.list:
        server = MedicalDatasetMCPServer()
        datasets = server.get_ingested_datasets()
        
        if datasets:
            print(f"\nFound {len(datasets)} ingested dataset(s):")
            for ds in datasets:
                print(f"  - {ds['name']} ({ds['format']}, {ds['record_count']} records)")
        else:
            print("No datasets ingested yet.")
        return
    
    if not args.file_path:
        parser.print_help()
        print("\nExample:")
        print("  python ingest_dataset.py Data/medical_conditions.json json")
        sys.exit(1)
    
    file_path = Path(args.file_path)
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    print(f"Ingesting dataset: {file_path}")
    print(f"Format: {args.format_type}")
    
    try:
        result = ingest_third_party_dataset(str(file_path), args.format_type)
        
        if result['success']:
            print("\n✓ Dataset ingested successfully!")
            print(f"  Name: {result['metadata']['name']}")
            print(f"  Format: {result['metadata']['format']}")
            print(f"  Records: {result['metadata']['record_count']}")
            print(f"  Total documents: {result['documents']}")
            print("\nNote: Run 'python store_index.py' to update the vector index.")
        else:
            print("Error: Failed to ingest dataset")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
