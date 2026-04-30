# Database Design

## Overview
This document describes the database schema and design principles for the LessRAG project. The database stores document collections, document metadata, processed semantic chunks, and their corresponding vector embeddings.

## Standards
- **Normalization**: All tables satisfy 3NF.
- **Primary Keys**: Every table uses `id = AutoField()` as the primary key.
- **Consistency**: This file must be kept in sync with `server/database/models.py`.
- **Naming**: Table names are pluralized (e.g., `collections`, `documents`, `chunks`).

## Tables

### collections
Groups related documents together for organized retrieval and management.
- `id`: Integer, Auto Increment, Primary Key.
- `name`: String, Unique, Name of the collection.
- `description`: Text, Optional description of the collection.
- `created_at`: DateTime, Timestamp of creation.

### documents
Stores metadata for uploaded documents and tracks their processing status.
- `id`: Integer, Auto Increment, Primary Key.
- `doc_id`: String, Unique, UUID for external reference.
- `collection_id`: Integer, Foreign Key to `collections.id`, uses `SET NULL` on delete.
- `filename`: String, Original filename.
- `file_path`: String, Local path to the stored file.
- `status`: String, Processing status (e.g., `processing`, `completed`, `failed`).
- `created_at`: DateTime, Timestamp of creation.

### chunks
Stores individual semantic segments of a document and their vector representations.
- `id`: Integer, Auto Increment, Primary Key.
- `document_id`: Integer, Foreign Key to `documents.id`, uses `CASCADE` on delete.
- `content`: Text, The actual content of the chunk.
- `embedding`: Blob, The vector embedding data (OpenAI Embedding).
- `created_at`: DateTime, Timestamp of creation.

## Relationships
- A **Collection** can contain many **Documents**.
- A **Document** can optionally belong to one **Collection**.
- A **Document** can have many **Chunks**.
- A **Chunk** belongs to exactly one **Document**.
- Deleting a **Collection** will set the `collection_id` of associated **Documents** to `NULL` (Set Null).
- Deleting a **Document** will automatically delete all its associated **Chunks** (Cascade Delete).

## Views
(None at this time)
