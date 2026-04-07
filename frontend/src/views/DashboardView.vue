<script setup lang="ts">
import { ref, onMounted, onUnmounted, useTemplateRef } from "vue";
import { useRouter } from "vue-router";
import { Button } from "@/components/ui/button";
import {
    Loader2,
    FileText,
    CheckCircle,
    XCircle,
    Trash2,
} from "lucide-vue-next";
import { getAllTasks, startTask, deleteTask } from "../api";
import Footer from "../components/Footer.vue";

const router = useRouter();
const tasks = ref<any[]>([]);
const isUploading = ref(false);
const fileInput = useTemplateRef<HTMLInputElement>("fileInput");
let pollInterval: number | undefined;

const fetchTasks = async () => {
    try {
        tasks.value = await getAllTasks();
    } catch (error) {
        console.error("Failed to fetch tasks", error);
    }
};

const handleDeleteTask = async (taskId: number) => {
    if (!confirm("Are you sure you want to delete this task?")) return;
    try {
        await deleteTask(taskId);
        await fetchTasks();
    } catch (error) {
        console.error("Failed to delete task", error);
    }
};

const onFileChange = async (event: Event) => {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (!file) return;

    isUploading.value = true;
    try {
        const data = await startTask(file);
        if (data && data.task_id) {
            await fetchTasks();
        }
    } catch (error) {
        console.error("Upload failed", error);
    } finally {
        isUploading.value = false;
        if (fileInput.value) {
            fileInput.value.value = "";
        }
    }
};

onMounted(() => {
    fetchTasks();
    pollInterval = window.setInterval(fetchTasks, 5000); // refresh list every 5 seconds
});

onUnmounted(() => {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
});
</script>

<template>
    <div class="h-screen w-screen flex flex-col font-sans bg-gray-50/50">
        <header
            class="h-16 border-b flex items-center justify-between px-6 bg-white shrink-0"
        >
            <h1 class="text-xl font-bold text-primary">
                Topic Shift Dashboard
            </h1>

            <div class="flex items-center gap-4">
                <input
                    type="file"
                    accept="application/pdf"
                    class="hidden"
                    ref="fileInput"
                    @change="onFileChange"
                />
                <Button :disabled="isUploading" @click="fileInput?.click()">
                    <Loader2
                        v-if="isUploading"
                        class="w-4 h-4 mr-2 animate-spin"
                    />
                    {{ isUploading ? "Uploading..." : "Upload PDF" }}
                </Button>
            </div>
        </header>

        <main class="flex-1 p-6 overflow-y-auto">
            <div class="max-w-4xl mx-auto space-y-4">
                <h2 class="text-lg font-semibold mb-4">Processed Documents</h2>

                <div
                    v-if="tasks.length === 0"
                    class="text-center p-10 bg-white border rounded-md shadow-sm"
                >
                    <p class="text-muted-foreground">
                        No processing tasks found. Upload a PDF to get started.
                    </p>
                </div>

                <div
                    v-for="task in tasks.slice().reverse()"
                    :key="task.task_id"
                    class="bg-white border p-4 rounded-md shadow-sm flex items-center justify-between hover:border-primary/50 transition-colors"
                >
                    <div class="flex items-center gap-4">
                        <div
                            class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary"
                        >
                            <FileText class="w-5 h-5" />
                        </div>
                        <div>
                            <p class="font-medium">Task #{{ task.task_id }}</p>
                            <div
                                class="flex items-center gap-1.5 mt-1 text-sm text-muted-foreground"
                            >
                                <Loader2
                                    v-if="task.status === 'in_progress'"
                                    class="w-3 h-3 animate-spin text-blue-500"
                                />
                                <CheckCircle
                                    v-else-if="task.status === 'completed'"
                                    class="w-3 h-3 text-green-500"
                                />
                                <XCircle
                                    v-else-if="task.status === 'failed'"
                                    class="w-3 h-3 text-red-500"
                                />
                                <span class="capitalize">{{
                                    task.status.replace("_", " ")
                                }}</span>
                            </div>
                        </div>
                    </div>

                    <div class="flex items-center gap-2">
                        <Button
                            v-if="task.status === 'completed'"
                            variant="outline"
                            @click="router.push(`/graph/${task.task_id}`)"
                        >
                            View Graph
                        </Button>
                        <Button
                            v-else-if="task.status === 'in_progress'"
                            variant="outline"
                            disabled
                        >
                            Processing...
                        </Button>
                        <Button
                            v-else-if="task.status === 'failed'"
                            variant="outline"
                            disabled
                        >
                            Failed
                        </Button>
                        <Button
                            variant="ghost"
                            size="icon"
                            class="text-destructive hover:bg-destructive/10 hover:text-destructive"
                            @click="handleDeleteTask(task.task_id)"
                            title="Delete Task"
                        >
                            <Trash2 class="w-4 h-4" />
                        </Button>
                    </div>
                </div>
            </div>
        </main>
        <Footer />
    </div>
</template>
