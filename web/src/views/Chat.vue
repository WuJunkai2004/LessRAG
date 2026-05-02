<script setup>
import { ref, onMounted, nextTick } from "vue";
import { api } from "../utils/api";
import { useToast } from "primevue/usetoast";

const toast = useToast();

const question = ref("");
const messages = ref([]);
const loading = ref(false);
const documents = ref([]);
const selectedDocs = ref([]);
const chatContainer = ref(null);

const fetchDocuments = async () => {
  try {
    const data = await api.listDocuments();
    documents.value = data.filter((d) => d.status === "completed");
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Error",
      detail: error.message,
      life: 3000,
    });
  }
};

const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

const sendQuery = async () => {
  if (!question.value.trim() || loading.value) return;

  const userMessage = { role: "user", content: question.value };
  messages.value.push(userMessage);

  const currentQuestion = question.value;
  question.value = "";
  loading.value = true;

  await scrollToBottom();

  try {
    const docIds = selectedDocs.value.map((d) => d.doc_id);
    const result = await api.query(currentQuestion, docIds);

    messages.value.push({
      role: "assistant",
      content: result.answer,
      context: result.context,
    });
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Error",
      detail: error.message,
      life: 3000,
    });
    messages.value.push({
      role: "assistant",
      content: "Sorry, I encountered an error while processing your request.",
      isError: true,
    });
  } finally {
    loading.value = false;
    await scrollToBottom();
  }
};

onMounted(() => {
  fetchDocuments();
});
</script>

<template>
  <div class="flex h-full gap-4 p-4">
    <!-- Sidebar for document selection -->
    <div
      class="flex flex-column gap-3 w-3 card p-3 shadow-1 border-round bg-white overflow-y-auto"
    >
      <div class="flex justify-content-between align-items-center">
        <h3 class="m-0">Knowledge Base</h3>
        <Button
          icon="pi pi-refresh"
          text
          rounded
          @click="fetchDocuments"
          size="small"
        />
      </div>
      <p class="text-sm text-gray-600 m-0">Select documents to query from:</p>
      <div v-if="documents.length === 0" class="text-sm text-gray-400 italic">
        No completed documents available.
      </div>
      <div
        v-for="doc in documents"
        :key="doc.doc_id"
        class="flex align-items-center"
      >
        <Checkbox
          v-model="selectedDocs"
          :inputId="doc.doc_id"
          name="doc"
          :value="doc"
        />
        <label
          :for="doc.doc_id"
          class="ml-2 text-sm overflow-hidden text-overflow-ellipsis white-space-nowrap"
          :title="doc.filename"
        >
          {{ doc.filename }}
        </label>
      </div>
    </div>

    <!-- Main Chat Area -->
    <div
      class="flex flex-column flex-1 card p-0 shadow-1 border-round bg-white overflow-hidden relative"
    >
      <div
        ref="chatContainer"
        class="flex-1 overflow-y-auto p-4 flex flex-column gap-4 pb-8"
      >
        <div
          v-if="messages.length === 0"
          class="flex flex-column align-items-center justify-content-center h-full text-gray-400"
        >
          <i class="pi pi-comments text-6xl mb-3"></i>
          <p>Start a conversation by asking a question.</p>
        </div>

        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="[
            'flex',
            msg.role === 'user'
              ? 'justify-content-end'
              : 'justify-content-start',
          ]"
        >
          <div
            :class="[
              'max-w-9 p-3 border-round shadow-1',
              msg.role === 'user'
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-800',
              msg.isError
                ? 'bg-red-50 text-red-600 border-red-200 border-1'
                : '',
            ]"
          >
            <div class="white-space-pre-wrap">{{ msg.content }}</div>

            <div
              v-if="msg.context && msg.context.length > 0"
              class="mt-3 pt-3 border-top-1 border-gray-300"
            >
              <p class="text-xs font-bold mb-2 text-gray-500">Sources:</p>
              <div class="flex flex-column gap-2">
                <div
                  v-for="(ctx, cIdx) in msg.context"
                  :key="cIdx"
                  class="text-xs p-2 bg-white border-round border-1 border-gray-200"
                >
                  <div class="font-medium text-primary mb-1">
                    Source {{ cIdx + 1 }} (Score: {{ ctx.score.toFixed(2) }})
                  </div>
                  <div class="line-height-3 text-gray-700">
                    {{ ctx.content }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="loading" class="flex justify-content-start">
          <div class="bg-gray-100 p-3 border-round shadow-1">
            <i class="pi pi-spin pi-spinner mr-2"></i> Thinking...
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div
        class="absolute bottom-0 left-0 right-0 p-3 bg-white border-top-1 border-gray-200"
      >
        <div class="flex gap-2">
          <InputText
            v-model="question"
            placeholder="Ask a question..."
            class="flex-1"
            @keyup.enter="sendQuery"
            :disabled="loading"
          />
          <Button
            icon="pi pi-send"
            @click="sendQuery"
            :loading="loading"
            :disabled="!question.trim()"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.max-w-9 {
  max-width: 85%;
}
</style>
