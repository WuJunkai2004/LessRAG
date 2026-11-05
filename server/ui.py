import asyncio
import json
from dataclasses import field

import mesop as me
import mesop.labs as mel

from server.database.models import Chunk, Document
from server.tasks.manager import task_manager
from server.tasks.process import process_document_task
from server.utils.config import DATA_PATH
from server.utils.openai import ai_client
from server.utils.vector import rank_chunks

worker_loop = None


def get_worker_loop():
    global worker_loop
    if worker_loop is None:
        worker_loop = asyncio.get_event_loop()
    return worker_loop


UPLOAD_DIR = DATA_PATH / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@me.stateclass
class State:
    input: str = ""
    selected_docs: list[str] = field(default_factory=list)
    is_uploading: bool = False


def on_upload(event: me.UploadEvent):
    state = me.state(State)
    state.is_uploading = True
    yield

    try:
        file_path = UPLOAD_DIR / f"{Document().doc_id}_{event.file.name}"
        with file_path.open("wb") as buffer:
            buffer.write(event.file.read())

        doc = Document.create(
            filename=event.file.name, file_path=str(file_path), status="processing"
        )

        # 异步处理任务，线程安全地将任务推送到 worker 所在的 loop
        loop = get_worker_loop()
        if loop and loop.is_running():
            asyncio.run_coroutine_threadsafe(
                task_manager.add_task(process_document_task, doc.doc_id), loop
            )
        else:
            loop.run_until_complete(
                task_manager.add_task(process_document_task, doc.doc_id)
            )

    finally:
        state.is_uploading = False
        yield


def transform(input: str, history: list[mel.ChatMessage]):
    state = me.state(State)

    # 1. 检索相关分片
    query_vector = ai_client.get_embedding(input)

    query = Chunk.select(Chunk, Document.doc_id).join(Document)
    if state.selected_docs:
        query = query.where(Document.doc_id << state.selected_docs)

    candidate_chunks = []
    for chunk in query:
        if chunk.embedding:
            candidate_chunks.append(
                {
                    "content": chunk.content,
                    "embedding": json.loads(chunk.embedding.decode("utf-8")),
                    "doc_id": chunk.document.doc_id,
                }
            )

    if not candidate_chunks:
        yield "抱歉，在知识库中没有找到相关的背景信息来回答您的问题。"
        return

    ranked_results = rank_chunks(query_vector, candidate_chunks, top_k=5)
    contexts = ranked_results

    # 2. 构建 Prompt 并调用 LLM 生成回答
    context_text = "\n---\n".join(
        [f"[来源文档: {r['doc_id']}]\n{r['content']}" for r in contexts]
    )

    system_prompt = """你是一个专业的 AI 助手。请根据提供的“背景资料”来回答用户的“问题”。
要求：
1. 仅根据背景资料中的内容进行回答，不要编造事实。
2. 如果背景资料中没有相关信息，请诚实告知。
3. 回答要简洁、专业、逻辑清晰。"""

    user_prompt = f"背景资料：\n{context_text}\n\n问题：{input}"

    try:
        response = ai_client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        answer = response.choices[0].message.content or "抱歉，LLM 没有生成有效的回答。"
        yield answer
    except Exception as e:
        yield f"LLM generation failed: {str(e)}"


@me.page(
    path="/", security_policy=me.SecurityPolicy(dangerously_disable_trusted_types=True)
)
def page():
    state = me.state(State)
    with me.box(style=me.Style(display="flex", flex_direction="row", height="100vh")):
        # 侧边栏
        with me.box(
            style=me.Style(
                width="300px",
                border=me.Border(
                    right=me.BorderSide(width=1, style="solid", color="#ccc")
                ),
                padding=me.Padding.all(20),
                overflow_y="auto",
            )
        ):
            me.text("LessRAG 管理", type="headline-5")
            me.divider()

            me.text(
                "上传文档", type="subtitle-1", style=me.Style(margin=me.Margin(top=20))
            )
            me.uploader(
                label="选择文件",
                on_upload=on_upload,
                type="flat",
                color="primary",
                style=me.Style(width="100%"),
            )
            if state.is_uploading:
                me.progress_spinner()

            with me.box(style=me.Style(margin=me.Margin(top=20, bottom=20))):
                me.divider()

            me.text("文档列表", type="subtitle-1")
            docs = Document.select().order_by(Document.created_at.desc())
            for d in docs:
                with me.box(
                    style=me.Style(
                        display="flex",
                        align_items="center",
                        margin=me.Margin(bottom=10),
                    )
                ):
                    me.checkbox(
                        key=d.doc_id,
                        label=f"{d.filename} ({d.status})",
                        checked=d.doc_id in state.selected_docs,
                        on_change=on_doc_select,
                    )

        # 主聊天区
        with me.box(
            style=me.Style(flex_grow=1, display="flex", flex_direction="column")
        ):
            mel.chat(transform, title="LessRAG Chat", bot_user="LessRAG Bot")


def on_doc_select(e: me.CheckboxChangeEvent):
    state = me.state(State)
    doc_id = e.key
    if e.checked:
        if doc_id not in state.selected_docs:
            state.selected_docs.append(doc_id)
    else:
        if doc_id in state.selected_docs:
            state.selected_docs.remove(doc_id)
