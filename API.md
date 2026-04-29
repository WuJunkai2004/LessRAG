# LessRAG API 接口文档

本文档定义了 LessRAG 项目的对外 API 接口。所有接口均采用 JSON 格式进行数据交互（除文件上传外），并仅使用 `GET` 和 `POST` 请求方法。

## 1. 通用响应格式
所有响应将遵循以下基础结构：
```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

---

## 2. 文档管理接口

### 2.1 上传文档
上传 PDF 或 Word 文档，系统将自动开始智能分片与向量化。

- **URL**: `/api/v1/document/upload`
- **方法**: `POST`
- **请求体**: `multipart/form-data`
  - `file`: 文件对象 (支持 .pdf, .docx)
- **响应数据**:
  ```json
  {
    "doc_id": "string (UUID)",
    "filename": "string",
    "status": "processing"
  }
  ```

### 2.2 获取文档列表
查看所有已上传文档的简要信息。

- **URL**: `/api/v1/document/list`
- **方法**: `GET`
- **请求参数**: 无
- **响应数据**:
  ```json
  [
    {
      "doc_id": "string",
      "filename": "string",
      "status": "completed",
      "created_at": "string (ISO8601)"
    }
  ]
  ```

### 2.3 获取文档详情
根据 `doc_id` 查询文档的详细处理状态。

- **URL**: `/api/v1/document/detail`
- **方法**: `GET`
- **请求参数**:
  - `doc_id`: 文档 ID
- **响应数据**:
  ```json
  {
    "doc_id": "string",
    "filename": "string",
    "status": "completed/processing/failed",
    "chunks_count": 10,
    "error_message": null,
    "created_at": "string"
  }
  ```

### 2.4 删除文档
删除指定文档及其关联的所有分片与向量数据。

- **URL**: `/api/v1/document/delete`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "doc_id": "string"
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "document deleted successfully"
  }
  ```

---

## 3. 检索与生成接口

### 3.1 知识库提问
基于上传的文档进行检索并生成回答。

- **URL**: `/api/v1/query`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "question": "string",
    "stream": false,
    "doc_ids": ["string"] (可选，指定文档范围)
  }
  ```
- **响应数据**:
  ```json
  {
    "answer": "string",
    "context": [
      {
        "content": "string",
        "doc_id": "string",
        "score": 0.95
      }
    ]
  }
  ```

### 3.2 语义匹配
仅执行向量检索，返回最相关的文档分片列表。

- **URL**: `/api/v1/match`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "text": "string",
    "top_k": 5,
    "doc_ids": ["string"] (可选)
  }
  ```
- **响应数据**:
  ```json
  [
    {
      "content": "string",
      "doc_id": "string",
      "score": 0.95
    }
  ]
  ```

---

## 4. 系统接口

### 4.1 健康检查
检查系统运行状态。

- **URL**: `/api/v1/health`
- **方法**: `GET`
- **响应数据**:
  ```json
  {
    "status": "healthy",
    "version": "0.1.0"
  }
  ```
