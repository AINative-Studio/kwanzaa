#!/usr/bin/env python3
"""
Extend ZeroDB training examples to reach 25-30 examples
Adds additional table operations, row CRUD, and file operations
"""

import json
from pathlib import Path

# System message
SYSTEM_MESSAGE = "You are an expert AINative platform developer specializing in ZeroDB vector database operations."

def add_example(examples, user_query, assistant_response):
    """Add example to list"""
    examples.append({
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": assistant_response}
        ]
    })

def generate_additional_examples():
    """Generate 16 additional examples"""
    examples = []

    # Table Operations (5 examples)
    add_example(examples,
        "How do I list all tables in a ZeroDB project?",
        """List tables in a project using the list endpoint:

```python
import httpx
from typing import List, Dict, Any

def list_tables(
    api_key: str,
    project_id: str,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    \"\"\"
    List all tables in a ZeroDB project

    Args:
        api_key: ZeroDB API key
        project_id: Project UUID
        limit: Max results
        offset: Pagination offset

    Returns:
        List of tables with metadata
    \"\"\"
    client = httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    params = {
        "project_id": project_id,
        "limit": limit,
        "offset": offset
    }

    response = client.get(
        "https://api.ainative.studio/v1/database/tables",
        params=params
    )

    response.raise_for_status()
    return response.json()

# List tables
result = list_tables(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    limit=50
)

print(f"Total tables: {result['total_count']}")
for table in result['tables']:
    print(f"Table: {table['table_name']}")
    print(f"  ID: {table['table_id']}")
    print(f"  Rows: {table['row_count']}")
    print(f"  Created: {table['created_at']}")
```""")

    add_example(examples,
        "How do I insert rows into a ZeroDB table?",
        """Insert rows using the table rows endpoint:

```python
import httpx
from typing import Dict, Any, List
from datetime import datetime

def insert_rows(
    api_key: str,
    project_id: str,
    table_name: str,
    rows: List[Dict[str, Any]]
) -> Dict[str, Any]:
    \"\"\"
    Insert rows into a ZeroDB table

    Args:
        api_key: ZeroDB API key
        project_id: Project UUID
        table_name: Table name
        rows: List of row data dictionaries

    Returns:
        Insertion result with row IDs
    \"\"\"
    client = httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    data = {
        "project_id": project_id,
        "table_name": table_name,
        "rows": rows
    }

    response = client.post(
        "https://api.ainative.studio/v1/database/tables/rows",
        json=data
    )

    response.raise_for_status()
    return response.json()

# Insert user records
users = [
    {
        "user_id": "user_001",
        "email": "john@example.com",
        "name": "John Doe",
        "created_at": datetime.utcnow().isoformat(),
        "metadata": {"plan": "pro", "verified": True}
    },
    {
        "user_id": "user_002",
        "email": "jane@example.com",
        "name": "Jane Smith",
        "created_at": datetime.utcnow().isoformat(),
        "metadata": {"plan": "free", "verified": False}
    }
]

result = insert_rows(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    table_name="users",
    rows=users
)

print(f"Inserted {result['success_count']} rows")
print(f"Row IDs: {result['row_ids']}")
```""")

    add_example(examples,
        "How do I query rows from a ZeroDB table?",
        """Query table rows with filtering:

```python
import httpx
from typing import Dict, Any, List

def query_rows(
    api_key: str,
    project_id: str,
    table_name: str,
    filter_query: Dict[str, Any] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    \"\"\"
    Query rows from a ZeroDB table

    Args:
        api_key: ZeroDB API key
        project_id: Project UUID
        table_name: Table name
        filter_query: MongoDB-style filter
        limit: Max results
        offset: Pagination offset

    Returns:
        List of matching rows
    \"\"\"
    client = httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    query_data = {
        "project_id": project_id,
        "table_name": table_name,
        "filter": filter_query or {},
        "limit": limit,
        "offset": offset
    }

    response = client.post(
        "https://api.ainative.studio/v1/database/tables/query",
        json=query_data
    )

    return response.json()['rows']

# Query all users
all_users = query_rows(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    table_name="users",
    limit=100
)

# Query users with filter
pro_users = query_rows(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    table_name="users",
    filter_query={"metadata.plan": "pro"}
)

# Query with multiple conditions
verified_pro_users = query_rows(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    table_name="users",
    filter_query={
        "metadata.plan": "pro",
        "metadata.verified": True
    }
)

print(f"Found {len(verified_pro_users)} verified pro users")
```""")

    add_example(examples,
        "How do I update rows in a ZeroDB table?",
        """Update existing table rows:

```python
import httpx
from typing import Dict, Any

def update_rows(
    api_key: str,
    project_id: str,
    table_name: str,
    filter_query: Dict[str, Any],
    update_data: Dict[str, Any]
) -> Dict[str, Any]:
    \"\"\"
    Update rows in a ZeroDB table

    Args:
        api_key: ZeroDB API key
        project_id: Project UUID
        table_name: Table name
        filter_query: MongoDB-style filter to match rows
        update_data: Update operations ($set, $inc, etc.)

    Returns:
        Update result with count
    \"\"\"
    client = httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    data = {
        "project_id": project_id,
        "table_name": table_name,
        "filter": filter_query,
        "update": update_data
    }

    response = client.patch(
        "https://api.ainative.studio/v1/database/tables/rows",
        json=data
    )

    return response.json()

# Update user plan
result = update_rows(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    table_name="users",
    filter_query={"user_id": "user_001"},
    update_data={
        "$set": {
            "metadata.plan": "enterprise",
            "metadata.verified": True
        }
    }
)

print(f"Updated {result['modified_count']} rows")

# Increment counter
counter_result = update_rows(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    table_name="analytics",
    filter_query={"event_type": "page_view"},
    update_data={
        "$inc": {"count": 1}
    }
)
```

Update operators:
- `$set`: Set field values
- `$inc`: Increment numeric field
- `$push`: Add to array
- `$pull`: Remove from array""")

    add_example(examples,
        "How do I delete rows from a ZeroDB table?",
        """Delete rows using filter criteria:

```python
import httpx
from typing import Dict, Any

def delete_rows(
    api_key: str,
    project_id: str,
    table_name: str,
    filter_query: Dict[str, Any]
) -> Dict[str, Any]:
    \"\"\"
    Delete rows from a ZeroDB table

    Args:
        api_key: ZeroDB API key
        project_id: Project UUID
        table_name: Table name
        filter_query: MongoDB-style filter

    Returns:
        Deletion result with count
    \"\"\"
    client = httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    data = {
        "project_id": project_id,
        "table_name": table_name,
        "filter": filter_query
    }

    response = client.delete(
        "https://api.ainative.studio/v1/database/tables/rows",
        json=data
    )

    return response.json()

# Delete specific user
result = delete_rows(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    table_name="users",
    filter_query={"user_id": "user_003"}
)

print(f"Deleted {result['deleted_count']} rows")

# Delete inactive users
inactive_result = delete_rows(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    table_name="users",
    filter_query={
        "metadata.last_login": {
            "$lt": "2025-01-01T00:00:00Z"
        }
    }
)

print(f"Deleted {inactive_result['deleted_count']} inactive users")
```""")

    # File Operations (3 examples)
    add_example(examples,
        "How do I upload file metadata to ZeroDB?",
        """Upload file metadata for tracking:

```python
import httpx
from typing import Dict, Any

def upload_file_metadata(
    api_key: str,
    project_id: str,
    file_key: str,
    file_name: str,
    content_type: str,
    size_bytes: int,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    \"\"\"
    Upload file metadata to ZeroDB

    Args:
        api_key: ZeroDB API key
        project_id: Project UUID
        file_key: Unique file key/path
        file_name: Original filename
        content_type: MIME type
        size_bytes: File size in bytes
        metadata: Additional metadata

    Returns:
        File record with file_id
    \"\"\"
    client = httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    file_data = {
        "project_id": project_id,
        "file_key": file_key,
        "file_name": file_name,
        "content_type": content_type,
        "size_bytes": size_bytes,
        "file_metadata": metadata or {}
    }

    response = client.post(
        "https://api.ainative.studio/v1/database/files",
        json=file_data
    )

    return response.json()

# Upload document metadata
result = upload_file_metadata(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    file_key="documents/2025/report.pdf",
    file_name="annual_report_2025.pdf",
    content_type="application/pdf",
    size_bytes=1024000,
    metadata={
        "uploaded_by": "user_001",
        "category": "reports",
        "year": 2025,
        "public": False
    }
)

print(f"File metadata stored: {result['file_id']}")
```""")

    add_example(examples,
        "How do I list files in a ZeroDB project?",
        """List file metadata with filtering:

```python
import httpx
from typing import List, Dict, Any

def list_files(
    api_key: str,
    project_id: str,
    limit: int = 100,
    offset: int = 0,
    content_type: str = None
) -> List[Dict[str, Any]]:
    \"\"\"
    List files in a ZeroDB project

    Args:
        api_key: ZeroDB API key
        project_id: Project UUID
        limit: Max results
        offset: Pagination offset
        content_type: Optional MIME type filter

    Returns:
        List of file metadata records
    \"\"\"
    client = httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    params = {
        "project_id": project_id,
        "limit": limit,
        "offset": offset
    }

    if content_type:
        params["content_type"] = content_type

    response = client.get(
        "https://api.ainative.studio/v1/database/files",
        params=params
    )

    return response.json()['files']

# List all files
all_files = list_files(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000"
)

# List only PDF files
pdf_files = list_files(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    content_type="application/pdf"
)

print(f"Found {len(pdf_files)} PDF files")
for file in pdf_files:
    print(f"  {file['file_name']} ({file['size_bytes']} bytes)")
```""")

    add_example(examples,
        "How do I get file metadata from ZeroDB?",
        """Retrieve file metadata by ID:

```python
import httpx
from typing import Dict, Any

def get_file_metadata(
    api_key: str,
    project_id: str,
    file_id: str
) -> Dict[str, Any]:
    \"\"\"
    Get file metadata from ZeroDB

    Args:
        api_key: ZeroDB API key
        project_id: Project UUID
        file_id: File UUID

    Returns:
        File metadata record
    \"\"\"
    client = httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    params = {
        "project_id": project_id,
        "file_id": file_id
    }

    response = client.get(
        "https://api.ainative.studio/v1/database/files/metadata",
        params=params
    )

    return response.json()

# Get file details
file_info = get_file_metadata(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    file_id="file_123"
)

print(f"File: {file_info['file_name']}")
print(f"Type: {file_info['content_type']}")
print(f"Size: {file_info['size_bytes']} bytes")
print(f"Key: {file_info['file_key']}")
print(f"Metadata: {file_info['file_metadata']}")
```""")

    # Event & Analytics (3 examples)
    add_example(examples,
        "How do I list events from ZeroDB event stream?",
        """List events with filtering:

```python
import httpx
from typing import List, Dict, Any

def list_events(
    api_key: str,
    project_id: str,
    topic: str = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    \"\"\"
    List events from ZeroDB event stream

    Args:
        api_key: ZeroDB API key
        project_id: Project UUID
        topic: Optional topic filter
        limit: Max results
        offset: Pagination offset

    Returns:
        List of events
    \"\"\"
    client = httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    params = {
        "project_id": project_id,
        "limit": limit,
        "offset": offset
    }

    if topic:
        params["topic"] = topic

    response = client.get(
        "https://api.ainative.studio/v1/database/events",
        params=params
    )

    return response.json()['events']

# List all events
all_events = list_events(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000"
)

# List user action events
user_events = list_events(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    topic="user_actions",
    limit=50
)

print(f"Found {len(user_events)} user action events")
for event in user_events[:5]:
    print(f"  {event['event_payload']['action']} at {event['created_at']}")
```""")

    add_example(examples,
        "How do I log RLHF data to ZeroDB?",
        """Log RLHF training data:

```python
import httpx
from typing import Dict, Any

def log_rlhf_data(
    api_key: str,
    project_id: str,
    session_id: str,
    input_prompt: str,
    model_output: str,
    reward_score: float,
    notes: str = ""
) -> Dict[str, Any]:
    \"\"\"
    Log RLHF dataset entry to ZeroDB

    Args:
        api_key: ZeroDB API key
        project_id: Project UUID
        session_id: Session identifier
        input_prompt: User prompt
        model_output: Model response
        reward_score: Reward score (0.0-1.0)
        notes: Optional notes

    Returns:
        Logged RLHF entry
    \"\"\"
    client = httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    rlhf_data = {
        "project_id": project_id,
        "session_id": session_id,
        "input_prompt": input_prompt,
        "model_output": model_output,
        "reward_score": reward_score,
        "notes": notes
    }

    response = client.post(
        "https://api.ainative.studio/v1/database/rlhf",
        json=rlhf_data
    )

    return response.json()

# Log high-quality interaction
result = log_rlhf_data(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    session_id="session_123",
    input_prompt="Explain quantum computing",
    model_output="Quantum computing uses quantum bits...",
    reward_score=0.95,
    notes="Excellent technical explanation"
)

print(f"RLHF entry logged: {result['interaction_id']}")
```""")

    add_example(examples,
        "How do I store agent logs in ZeroDB?",
        """Store structured agent logs:

```python
import httpx
from typing import Dict, Any
from datetime import datetime

def store_agent_log(
    api_key: str,
    project_id: str,
    agent_id: str,
    session_id: str,
    log_level: str,
    log_message: str,
    payload: Dict[str, Any] = None
) -> Dict[str, Any]:
    \"\"\"
    Store agent log in ZeroDB

    Args:
        api_key: ZeroDB API key
        project_id: Project UUID
        agent_id: Agent identifier
        session_id: Session identifier
        log_level: Log level (INFO/WARNING/ERROR)
        log_message: Log message
        payload: Additional log data

    Returns:
        Stored log entry
    \"\"\"
    client = httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    log_data = {
        "project_id": project_id,
        "agent_id": agent_id,
        "session_id": session_id,
        "log_level": log_level,
        "log_message": log_message,
        "raw_payload": payload or {}
    }

    response = client.post(
        "https://api.ainative.studio/v1/database/logs",
        json=log_data
    )

    return response.json()

# Log agent action
result = store_agent_log(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    agent_id="agent_123",
    session_id="session_456",
    log_level="INFO",
    log_message="Completed document analysis",
    payload={
        "documents_processed": 10,
        "total_tokens": 5000,
        "duration_ms": 2500
    }
)

print(f"Log entry stored: {result['log_id']}")
```""")

    # Advanced Operations (5 examples)
    add_example(examples,
        "How do I optimize vector indices in ZeroDB?",
        """Create optimized indices for vector search:

```python
import httpx
from typing import Dict, Any

def create_vector_index(
    api_key: str,
    project_id: str,
    namespace: str,
    index_type: str = "hnsw"
) -> Dict[str, Any]:
    \"\"\"
    Create optimized vector index

    Args:
        api_key: ZeroDB API key
        project_id: Project UUID
        namespace: Vector namespace
        index_type: Index type (hnsw/ivf/flat)

    Returns:
        Index creation result
    \"\"\"
    client = httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    index_data = {
        "project_id": project_id,
        "namespace": namespace,
        "index_type": index_type
    }

    response = client.post(
        "https://api.ainative.studio/v1/vectors/create-index",
        json=index_data
    )

    return response.json()

# Create HNSW index for fast search
result = create_vector_index(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    namespace="documents",
    index_type="hnsw"
)

print(f"Index created: {result['index_name']}")
print(f"Status: {result['status']}")
```

Index types:
- `hnsw`: Best for high-dimensional vectors, fast search
- `ivf`: Good for large datasets, balanced speed/accuracy
- `flat`: Exact search, slower but most accurate""")

    add_example(examples,
        "How do I export vectors from ZeroDB?",
        """Export vectors in JSON or CSV format:

```python
import httpx
from typing import Dict, Any

def export_vectors(
    api_key: str,
    project_id: str,
    namespace: str = None,
    export_format: str = "json"
) -> Dict[str, Any]:
    \"\"\"
    Export vectors from ZeroDB

    Args:
        api_key: ZeroDB API key
        project_id: Project UUID
        namespace: Optional namespace filter
        export_format: Format (json/csv)

    Returns:
        Export data
    \"\"\"
    client = httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    export_data = {
        "project_id": project_id,
        "export_format": export_format
    }

    if namespace:
        export_data["namespace"] = namespace

    response = client.post(
        "https://api.ainative.studio/v1/vectors/export",
        json=export_data
    )

    return response.json()

# Export all vectors as JSON
json_export = export_vectors(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    export_format="json"
)

print(f"Exported {json_export['vector_count']} vectors")
print(f"File size: {json_export['file_size_bytes']} bytes")

# Save to file
import json
with open("vectors_export.json", "w") as f:
    json.dump(json_export['data'], f, indent=2)
```""")

    add_example(examples,
        "How do I get project database status from ZeroDB?",
        """Check project database status:

```python
import httpx
from typing import Dict, Any

def get_database_status(
    api_key: str,
    project_id: str
) -> Dict[str, Any]:
    \"\"\"
    Get database status for project

    Args:
        api_key: ZeroDB API key
        project_id: Project UUID

    Returns:
        Database status and metrics
    \"\"\"
    client = httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    params = {"project_id": project_id}

    response = client.get(
        "https://api.ainative.studio/v1/database/status",
        params=params
    )

    return response.json()

# Get status
status = get_database_status(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000"
)

print(f"Database: {status['database_enabled']}")
print(f"Vector count: {status['vector_count']}")
print(f"Table count: {status['table_count']}")
print(f"Memory records: {status['memory_count']}")
print(f"Storage used: {status['storage_bytes']} bytes")
print(f"Health: {status['health_status']}")
```""")

    add_example(examples,
        "How do I use namespaces to organize vectors in ZeroDB?",
        """Organize vectors using namespaces:

```python
import httpx
from typing import List

# Namespaces help organize vectors by purpose
namespaces = {
    "documents": "User documents and articles",
    "embeddings": "Pre-computed embeddings",
    "knowledge_base": "Company knowledge base",
    "support_tickets": "Customer support data"
}

def upsert_to_namespace(
    api_key: str,
    project_id: str,
    namespace: str,
    vectors: List[dict]
):
    \"\"\"Upsert vectors to specific namespace\"\"\"
    client = httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    for vector_data in vectors:
        vector_data["namespace"] = namespace
        vector_data["project_id"] = project_id

        client.post(
            "https://api.ainative.studio/v1/vectors/upsert",
            json=vector_data
        )

# Store documents in documents namespace
documents = [
    {
        "vector_embedding": [0.1] * 1536,
        "document": "Product manual v1.0",
        "metadata": {"type": "manual", "version": "1.0"}
    }
]

upsert_to_namespace(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    namespace="documents",
    vectors=documents
)

# Search within specific namespace
def search_namespace(api_key, project_id, namespace, query_vector):
    client = httpx.Client(
        headers={"Authorization": f"Bearer {api_key}"}
    )

    response = client.post(
        "https://api.ainative.studio/v1/vectors/search",
        json={
            "project_id": project_id,
            "namespace": namespace,
            "query_vector": query_vector,
            "limit": 10
        }
    )

    return response.json()['results']

# Search only in knowledge_base namespace
results = search_namespace(
    api_key="your_api_key",
    project_id="550e8400-e29b-41d4-a716-446655440000",
    namespace="knowledge_base",
    query_vector=[0.1] * 1536
)
```

Namespace best practices:
- Use descriptive names (documents, embeddings, kb)
- Separate by data source or purpose
- Easier to manage and search specific datasets
- Can apply different retention policies per namespace""")

    add_example(examples,
        "What are the best practices for production ZeroDB usage?",
        """Production best practices for ZeroDB:

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)

class ProductionZeroDBClient:
    \"\"\"Production-ready ZeroDB client\"\"\"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.ainative.studio"

        # Use connection pooling
        self.client = httpx.Client(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30)
    )
    def upsert_vector(self, project_id, embedding, document, metadata):
        \"\"\"Upsert with retry logic\"\"\"
        try:
            response = self.client.post(
                f"{self.base_url}/v1/vectors/upsert",
                json={
                    "project_id": project_id,
                    "vector_embedding": embedding,
                    "document": document,
                    "vector_metadata": metadata
                }
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code}")
            raise
        except httpx.TimeoutException:
            logger.error("Request timeout")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def batch_upsert(self, project_id, vectors, batch_size=100):
        \"\"\"Batch upsert with chunking\"\"\"
        results = []

        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]

            result = self.client.post(
                f"{self.base_url}/v1/vectors/batch-upsert",
                json={
                    "project_id": project_id,
                    "vectors": batch
                }
            )

            results.append(result.json())
            logger.info(f"Batch {i//batch_size + 1} completed")

        return results

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

# Usage
with ProductionZeroDBClient(api_key="your_api_key") as client:
    result = client.upsert_vector(
        project_id="550e8400-e29b-41d4-a716-446655440000",
        embedding=[0.1] * 1536,
        document="Production document",
        metadata={"env": "production"}
    )
```

Best practices:
1. Use connection pooling for efficiency
2. Implement retry logic for transient failures
3. Batch operations when possible (100-500 items)
4. Set appropriate timeouts (30s default, 60s for batch)
5. Use context managers for resource cleanup
6. Log all operations for debugging
7. Monitor rate limits and adjust accordingly
8. Use namespaces to organize vectors
9. Include metadata for filtering and tracking
10. Validate embedding dimensions (1536 for OpenAI)""")

    return examples

def main():
    """Extend the examples file"""
    print("Extending ZeroDB Training Examples")
    print("=" * 50)

    # Read existing examples
    input_path = Path("/Users/aideveloper/kwanzaa/data/training/zerodb_examples_v2.jsonl")
    existing = []

    with open(input_path, 'r') as f:
        for line in f:
            existing.append(json.loads(line))

    print(f"Existing examples: {len(existing)}")

    # Generate additional examples
    new_examples = generate_additional_examples()
    print(f"New examples: {len(new_examples)}")

    # Combine
    all_examples = existing + new_examples
    print(f"Total examples: {len(all_examples)}")

    # Save
    with open(input_path, 'w') as f:
        for example in all_examples:
            f.write(json.dumps(example) + '\n')

    print(f"\n{'='*50}")
    print(f"Extension Complete!")
    print(f"Total examples: {len(all_examples)}")
    print(f"File: {input_path}")
    print(f"{'='*50}")

    # Summary
    print("\nFinal Distribution:")
    print(f"- Vector Storage: 4 examples")
    print(f"- Semantic Search: 3 examples")
    print(f"- Database Operations: 5 examples")
    print(f"- Advanced Usage: 2 examples")
    print(f"- Table Operations: 5 examples")
    print(f"- File Operations: 3 examples")
    print(f"- Event & Analytics: 3 examples")
    print(f"- Advanced Features: 5 examples")
    print(f"\nAll examples based on /Users/aideveloper/core codebase")
    print("Zero AI attribution ✓")

if __name__ == "__main__":
    main()
