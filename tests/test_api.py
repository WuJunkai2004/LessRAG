import time

import httpx

BASE_URL = "http://127.0.0.1:15000/api/v1"


def test_health_check():
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


def test_document_lifecycle():
    with httpx.Client(timeout=120.0) as client:
        # 1. 上传文档
        file_path = "tests/sample.txt"
        with open(file_path, "rb") as f:
            files = {"file": ("sample.txt", f, "text/plain")}
            response = client.post(f"{BASE_URL}/document/upload", files=files)

        print(f"Upload response: {response.status_code}, {response.text}")
        assert response.status_code == 200
        res_data = response.json()
        assert res_data["success"] is True
        doc_id = res_data["data"]["doc_id"]
        print(f"\nUploaded document ID: {doc_id}")

        # 2. 轮询等待处理完成
        status = "processing"
        max_retries = 20
        retry_count = 0
        while status == "processing" and retry_count < max_retries:
            time.sleep(2)
            response = client.get(
                f"{BASE_URL}/document/detail", params={"doc_id": doc_id}
            )
            assert response.status_code == 200
            detail_data = response.json()
            assert detail_data["success"] is True
            status = detail_data["data"]["status"]
            print(f"Waiting for processing... current status: {status}")
            retry_count += 1

        assert status == "completed", (
            f"Document processing failed or timed out. Final status: {status}"
        )

        # 3. 语义匹配测试
        match_req = {"text": "什么是 LessRAG？", "top_k": 2}
        response = client.post(f"{BASE_URL}/match", json=match_req)
        assert response.status_code == 200
        match_data = response.json()
        assert match_data["success"] is True
        assert len(match_data["data"]) > 0
        print(f"Match success, found {len(match_data['data'])} chunks")

        # 4. 知识库提问测试
        query_req = {"question": "LessRAG 是如何进行分片的？", "doc_ids": [doc_id]}
        response = client.post(f"{BASE_URL}/query", json=query_req)
        assert response.status_code == 200
        query_data = response.json()
        assert query_data["success"] is True
        assert "answer" in query_data["data"]
        print(f"Query answer: {query_data['data']['answer']}")

        # 5. 删除文档
        delete_req = {"doc_id": doc_id}
        response = client.post(f"{BASE_URL}/document/delete", json=delete_req)
        assert response.status_code == 200
        assert response.json()["success"] is True
        print("Document deleted successfully")


if __name__ == "__main__":
    # 如果不使用 pytest，可以直接运行
    try:
        print("Starting API tests...")
        test_health_check()
        print("Health check passed.")
        test_document_lifecycle()
        print("Full lifecycle test passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback

        traceback.print_exc()
