import json
from typing import List, Optional

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.completion_create_params import ResponseFormat

from server.utils.config import config
from server.utils.logger import log


class ProviderClient:
    def __init__(self, config_key: str):
        self.model = config.get(f"{config_key}.model")
        self.api_key = config.get(f"{config_key}.api_key", "")
        self.api_url = self._clean_url(config.get(f"{config_key}.api_url"))
        self.client = OpenAI(api_key=self.api_key, base_url=self.api_url)

    def _clean_url(self, url: Optional[str]) -> str:
        """将完整的接口 URL 转换为 OpenAI SDK 需要的 base_url"""
        if not url:
            return ""
        # 如果用户配置了完整的 endpoint，移除后缀
        for suffix in ["/chat/completions", "/embeddings"]:
            if url.endswith(suffix):
                return url[: -len(suffix)]
        return url

    @property
    def embeddings(self):
        return self.client.embeddings

    @property
    def chat(self):
        return self.client.chat


class OpenAIClient:
    def __init__(self):
        if not config.all_required:
            log("openai").error(
                "Missing required OpenAI configuration. Please check your config.toml."
            )
            exit(1)
        # LLM 配置
        self.model_client = ProviderClient("model")
        self.embed_client = ProviderClient("embedding")

    def get_embedding(self, text: str) -> List[float]:
        """获取文本的向量表示"""
        response = self.embed_client.embeddings.create(
            input=[text], model=self.embed_client.model
        )
        return response.data[0].embedding

    def chat_completion(
        self,
        messages: List[ChatCompletionMessageParam],
        response_format: Optional[ResponseFormat] = None,
    ):
        """通用对话接口"""
        if response_format:
            return self.model_client.chat.completions.create(
                model=self.model_client.model,
                messages=messages,
                response_format=response_format,
            )
        else:
            return self.model_client.chat.completions.create(
                model=self.model_client.model, messages=messages
            )

    def smart_chunking(self, text: str) -> List[str]:
        """利用 LLM 进行智能分片"""
        if not text.strip():
            return []

        # 如果文本较短，直接返回
        if len(text) < 500:
            return [text]

        system_prompt = """你是一个文档处理专家。你的任务是将输入的长文本切分为多个语义完整的分片（Chunks）。
切分原则：
1. 保持语义完整性：确保每个分片包含完整的逻辑意思。
2. 长度适中：每个分片建议在 300-800 字之间。
3. 结构识别：识别标题、段落、列表等结构，不要在逻辑中途切断。

输出格式：必须返回一个 JSON 对象，格式为 ["分片1内容", "分片2内容", ...]。"""

        prompt = f"请对以下文本进行智能分片：\n\n{text[:4000]}"  # 限制输入长度以防超出 Token 限制

        try:
            response = self.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("LLM did not return any content for chunking.")
            chunks = json.loads(content)

            # 如果 LLM 没能切分，或者返回为空，则进行兜底处理
            if not chunks:
                return [text]
            return chunks
        except Exception as e:
            log("openai").error(f"Smart chunking failed: {e}")
            # 兜底：简单按段落切分
            return [p.strip() for p in text.split("\n\n") if p.strip()]


# 单例导出
ai_client = OpenAIClient()
