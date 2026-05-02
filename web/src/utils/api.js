const BASE_URL = "/api/v1";

async function request(url, options = {}) {
  const response = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  const result = await response.json();
  if (result.code !== 200 && result.code !== undefined) {
    throw new Error(result.message || "Request failed");
  }
  return result.data !== undefined ? result.data : result;
}

export const api = {
  uploadDocument(file) {
    const formData = new FormData();
    formData.append("file", file);
    return request("/document/upload", {
      method: "POST",
      body: formData,
      headers: {
        "Content-Type": undefined, // Let the browser set the boundary
      },
    });
  },

  async uploadDocumentManual(file) {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${BASE_URL}/document/upload`, {
      method: "POST",
      body: formData,
    });
    return await response.json();
  },

  listDocuments() {
    return request("/document/list");
  },

  getDocumentDetail(doc_id) {
    return request(`/document/detail?doc_id=${doc_id}`);
  },

  deleteDocument(doc_id) {
    return request("/document/delete", {
      method: "POST",
      body: JSON.stringify({ doc_id }),
    });
  },

  query(question, doc_ids = [], stream = false) {
    return request("/query", {
      method: "POST",
      body: JSON.stringify({ question, doc_ids, stream }),
    });
  },

  match(text, top_k = 5, doc_ids = []) {
    return request("/match", {
      method: "POST",
      body: JSON.stringify({ text, top_k, doc_ids }),
    });
  },

  health() {
    return request("/health");
  },
};
