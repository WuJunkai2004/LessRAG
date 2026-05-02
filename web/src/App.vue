<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();

const items = ref([
  {
    label: "Chat",
    icon: "pi pi-comments",
    route: "/chat",
  },
  {
    label: "Documents",
    icon: "pi pi-file",
    route: "/documents",
  },
]);
</script>

<template>
  <div class="min-h-screen flex flex-column bg-gray-50">
    <ConfirmDialog />
    <Toast />

    <header
      class="bg-primary text-white p-3 shadow-2 flex justify-content-between align-items-center"
    >
      <div class="flex align-items-center gap-2">
        <i class="pi pi-bolt text-2xl"></i>
        <h1 class="m-0 text-xl font-bold">LessRAG</h1>
      </div>
      <nav class="flex gap-3">
        <router-link
          v-for="item in items"
          :key="item.route"
          :to="item.route"
          class="no-underline text-white px-3 py-2 border-round transition-colors transition-duration-200 hover:bg-white-alpha-20"
          :class="{ 'bg-white-alpha-20 font-bold': route.path === item.route }"
        >
          <i :class="item.icon" class="mr-2"></i>
          {{ item.label }}
        </router-link>
      </nav>
    </header>

    <main class="flex-1 overflow-hidden">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>
