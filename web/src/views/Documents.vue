<script setup>
import { ref, onMounted } from "vue";
import { api } from "../utils/api";
import { useToast } from "primevue/usetoast";
import { useConfirm } from "primevue/useconfirm";

const toast = useToast();
const confirm = useConfirm();

const documents = ref([]);
const loading = ref(false);
const uploading = ref(false);

const fetchDocuments = async () => {
  loading.ref = true;
  try {
    const data = await api.listDocuments();
    documents.value = data;
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Error",
      detail: error.message,
      life: 3000,
    });
  } finally {
    loading.value = false;
  }
};

const onUpload = async (event) => {
  const file = event.files[0];
  if (!file) return;

  uploading.value = true;
  try {
    await api.uploadDocumentManual(file);
    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Document uploaded",
      life: 3000,
    });
    fetchDocuments();
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Error",
      detail: error.message,
      life: 3000,
    });
  } finally {
    uploading.value = false;
  }
};

const deleteDocument = (doc_id) => {
  confirm.require({
    message: "Are you sure you want to delete this document?",
    header: "Confirmation",
    icon: "pi pi-exclamation-triangle",
    rejectProps: {
      label: "Cancel",
      severity: "secondary",
      outlined: true,
    },
    acceptProps: {
      label: "Delete",
      severity: "danger",
    },
    accept: async () => {
      try {
        await api.deleteDocument(doc_id);
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Document deleted",
          life: 3000,
        });
        fetchDocuments();
      } catch (error) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: error.message,
          life: 3000,
        });
      }
    },
  });
};

const getStatusSeverity = (status) => {
  switch (status) {
    case "completed":
      return "success";
    case "processing":
      return "info";
    case "failed":
      return "danger";
    default:
      return "secondary";
  }
};

onMounted(() => {
  fetchDocuments();
});
</script>

<template>
  <div class="card p-4">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2 class="m-0">Documents</h2>
      <div class="flex gap-2">
        <Button
          icon="pi pi-refresh"
          outlined
          @click="fetchDocuments"
          :loading="loading"
        />
        <FileUpload
          mode="basic"
          name="file"
          auto
          chooseLabel="Upload"
          class="p-button-primary"
          @uploader="onUpload"
          customUpload
          :disabled="uploading"
        />
      </div>
    </div>

    <DataTable :value="documents" :loading="loading" responsiveLayout="scroll">
      <template #empty> No documents found. </template>
      <Column field="filename" header="Name"></Column>
      <Column field="status" header="Status">
        <template #body="slotProps">
          <Tag
            :value="slotProps.data.status"
            :severity="getStatusSeverity(slotProps.data.status)"
          />
        </template>
      </Column>
      <Column field="created_at" header="Created At">
        <template #body="slotProps">
          {{ new Date(slotProps.data.created_at).toLocaleString() }}
        </template>
      </Column>
      <Column header="Actions" alignFrozen="right" frozen>
        <template #body="slotProps">
          <Button
            icon="pi pi-trash"
            severity="danger"
            text
            rounded
            @click="deleteDocument(slotProps.data.doc_id)"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>
