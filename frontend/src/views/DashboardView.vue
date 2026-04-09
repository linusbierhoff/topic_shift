<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { ScrollArea } from "@/components/ui/scroll-area";
import { BarChart3 } from "lucide-vue-next";
import { getAllTasks, deleteTask } from "../api";
import Footer from "../components/Footer.vue";
import CreateTaskDialog from "../components/dashboard/CreateTaskDialog.vue";
import TaskCard from "../components/dashboard/TaskCard.vue";
import EmptyState from "../components/dashboard/EmptyState.vue";

const tasks = ref<any[]>([]);
const createTaskDialogRef = ref<any>(null);

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

const openCreateModal = () => {
    if (createTaskDialogRef.value) {
        createTaskDialogRef.value.isModalOpen = true;
    }
};

onMounted(() => {
    fetchTasks();
    pollInterval = window.setInterval(fetchTasks, 5000);
});

onUnmounted(() => {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
});
</script>

<template>
    <div class="h-screen w-screen flex flex-col font-sans bg-background">
        <header
            class="h-16 border-b flex items-center justify-between px-6 bg-card shrink-0"
        >
            <div class="flex items-center gap-2">
                <div
                    class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-primary-foreground"
                >
                    <BarChart3 class="w-5 h-5" />
                </div>
                <h1 class="text-xl font-bold tracking-tight">Topic Shift</h1>
            </div>

            <CreateTaskDialog
                ref="createTaskDialogRef"
                :on-task-created="fetchTasks"
            />
        </header>

        <main class="flex-1 overflow-hidden p-6 bg-muted/20">
            <div class="max-w-5xl mx-auto h-full flex flex-col gap-6">
                <div>
                    <h2 class="text-2xl font-bold tracking-tight">Analyses</h2>
                    <p class="text-muted-foreground">
                        Manage and view your document processing tasks.
                    </p>
                </div>

                <ScrollArea class="flex-1 pr-4 -mr-4">
                    <EmptyState
                        v-if="tasks.length === 0"
                        :on-action="openCreateModal"
                    />

                    <div
                        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                        v-else
                    >
                        <TaskCard
                            v-for="task in tasks.slice().reverse()"
                            :key="task.task_id"
                            :task="task"
                            :on-delete="handleDeleteTask"
                        />
                    </div>
                </ScrollArea>
            </div>
        </main>
        <Footer />
    </div>
</template>
