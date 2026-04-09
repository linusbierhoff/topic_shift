<script setup lang="ts">
import { ref, onMounted, onUnmounted, useTemplateRef } from "vue";
import { useRouter } from "vue-router";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
    CardFooter,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Loader2,
    FileText,
    CheckCircle,
    XCircle,
    Trash2,
    Upload,
    FileUp,
    BarChart3,
    Download,
    MessageSquare,
} from "lucide-vue-next";
import { getAllTasks, startTask, deleteTask } from "../api";
import Footer from "../components/Footer.vue";

const router = useRouter();
const tasks = ref<any[]>([]);
const isUploading = ref(false);
const isModalOpen = ref(false);

const theme = ref("");
const removeSubstrings = ref("");
const clusters = ref<number | null>(null);
const selectedFile = ref<File | null>(null);

const fileInput = useTemplateRef<HTMLInputElement>("fileInput");

let pollInterval: number | undefined;

const fetchTasks = async () => {
    try {
        tasks.value = await getAllTasks();
    } catch (error) {
        console.error("Failed to fetch tasks", error);
    }
};

const getStatusVariant = (status: string) => {
    switch (status) {
        case "completed":
            return "default";
        case "in_progress":
            return "secondary";
        case "failed":
            return "destructive";
        default:
            return "outline";
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

const onFileSelect = (event: Event) => {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file && file.type === "application/pdf") {
        selectedFile.value = file;
    } else if (file) {
        alert("Please select a valid PDF file.");
    }
};

const handleStartTask = async () => {
    if (!theme.value) {
        alert("Please provide a theme.");
        return;
    }
    if (!selectedFile.value) {
        alert("Please select a PDF file.");
        return;
    }

    isUploading.value = true;
    try {
        const substrings = removeSubstrings.value
            ? removeSubstrings.value.split(",").map((s) => s.trim())
            : [];
        const data = await startTask(
            selectedFile.value,
            theme.value,
            substrings,
            clusters.value,
        );
        if (data && data.task_id) {
            isModalOpen.value = false;
            // Reset form
            theme.value = "";
            removeSubstrings.value = "";
            clusters.value = null;
            selectedFile.value = null;
            await fetchTasks();
        }
    } catch (error) {
        console.error("Upload failed", error);
    } finally {
        isUploading.value = false;
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

            <Dialog v-model:open="isModalOpen">
                <DialogTrigger as-child>
                    <Button shadow="sm">
                        <Upload class="w-4 h-4 mr-2" />
                        New Analysis
                    </Button>
                </DialogTrigger>
                <DialogContent class="sm:max-w-106.25">
                    <DialogHeader>
                        <DialogTitle>Start New Analysis</DialogTitle>
                        <DialogDescription>
                            Upload a PDF to extract topics and map their shifts.
                        </DialogDescription>
                    </DialogHeader>
                    <div class="grid gap-6 py-4">
                        <div class="grid gap-2">
                            <Label
                                for="theme"
                                class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
                                >Focus Theme</Label
                            >
                            <Input
                                id="theme"
                                v-model="theme"
                                placeholder="e.g. Artificial Intelligence"
                                class="h-10"
                            />
                        </div>
                        <div class="grid gap-2">
                            <Label
                                for="removeSubstrings"
                                class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
                                >Noise Removal</Label
                            >
                            <Input
                                id="removeSubstrings"
                                v-model="removeSubstrings"
                                placeholder="e.g. Confidential, Page 1"
                                class="h-10"
                            />
                        </div>
                        <div class="grid gap-2">
                            <Label
                                for="clusters"
                                class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
                                >Target Clusters</Label
                            >
                            <Input
                                id="clusters"
                                type="number"
                                v-model="clusters"
                                placeholder="Auto-detect (leave empty)"
                                class="h-10"
                            />
                        </div>

                        <div class="grid gap-2">
                            <Label
                                class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
                                >Source Document</Label
                            >
                            <div
                                class="border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center gap-3 cursor-pointer hover:bg-accent/50 hover:border-primary/50 transition-all group"
                                @click="fileInput?.click()"
                            >
                                <input
                                    type="file"
                                    accept="application/pdf"
                                    class="hidden"
                                    ref="fileInput"
                                    @change="onFileSelect"
                                />
                                <template v-if="!selectedFile">
                                    <div
                                        class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center group-hover:scale-110 transition-transform"
                                    >
                                        <FileUp class="w-6 h-6 text-primary" />
                                    </div>
                                    <div class="text-center">
                                        <p class="text-sm font-medium">
                                            Click to select PDF
                                        </p>
                                        <p
                                            class="text-xs text-muted-foreground mt-1"
                                        >
                                            Maximum size: 50MB
                                        </p>
                                    </div>
                                </template>
                                <template v-else>
                                    <div
                                        class="w-12 h-12 rounded-full bg-green-500/10 flex items-center justify-center"
                                    >
                                        <FileText
                                            class="w-6 h-6 text-green-600"
                                        />
                                    </div>
                                    <div class="text-center">
                                        <p
                                            class="text-sm font-medium truncate max-w-5"
                                        >
                                            {{ selectedFile.name }}
                                        </p>
                                        <p
                                            class="text-xs text-muted-foreground mt-1"
                                        >
                                            {{
                                                (
                                                    selectedFile.size /
                                                    (1024 * 1024)
                                                ).toFixed(2)
                                            }}
                                            MB
                                        </p>
                                    </div>
                                </template>
                            </div>
                        </div>
                    </div>
                    <DialogFooter>
                        <Button
                            type="submit"
                            class="w-full"
                            :disabled="isUploading || !theme || !selectedFile"
                            @click="handleStartTask"
                        >
                            <Loader2
                                v-if="isUploading"
                                class="w-4 h-4 mr-2 animate-spin"
                            />
                            {{
                                isUploading
                                    ? "Processing Document..."
                                    : "Initialize Analysis"
                            }}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </header>

        <main class="flex-1 overflow-hidden p-6 bg-muted/20">
            <div class="max-w-5xl mx-auto h-full flex flex-col gap-6">
                <div class="flex items-center justify-between">
                    <div>
                        <h2 class="text-2xl font-bold tracking-tight">
                            Analyses
                        </h2>
                        <p class="text-muted-foreground">
                            Manage and view your document processing tasks.
                        </p>
                    </div>
                </div>

                <ScrollArea class="flex-1 pr-4 -mr-4">
                    <div
                        v-if="tasks.length === 0"
                        class="h-100 flex items-center justify-center"
                    >
                        <Card
                            class="w-full max-w-md text-center p-12 bg-transparent border-dashed"
                        >
                            <CardContent
                                class="flex flex-col items-center gap-4"
                            >
                                <div
                                    class="w-16 h-16 rounded-full bg-muted flex items-center justify-center"
                                >
                                    <FileText
                                        class="w-8 h-8 text-muted-foreground"
                                    />
                                </div>
                                <div>
                                    <h3 class="text-lg font-semibold">
                                        No analyses yet
                                    </h3>
                                    <p class="text-muted-foreground mt-1">
                                        Upload your first PDF to begin
                                        extracting topics.
                                    </p>
                                </div>
                                <Button
                                    variant="outline"
                                    class="mt-4"
                                    @click="isModalOpen = true"
                                >
                                    Get Started
                                </Button>
                            </CardContent>
                        </Card>
                    </div>

                    <div
                        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                        v-else
                    >
                        <Card
                            v-for="task in tasks.slice().reverse()"
                            :key="task.task_id"
                            class="group hover:shadow-md transition-all duration-300 border-muted/60"
                        >
                            <CardHeader class="pb-3">
                                <div class="flex items-start justify-between">
                                    <div
                                        class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary"
                                    >
                                        <FileText class="w-5 h-5" />
                                    </div>
                                    <Badge
                                        :variant="getStatusVariant(task.status)"
                                        class="capitalize"
                                    >
                                        <Loader2
                                            v-if="task.status === 'in_progress'"
                                            class="w-3 h-3 mr-1 animate-spin"
                                        />
                                        {{ task.status.replace("_", " ") }}
                                    </Badge>
                                </div>
                                <CardTitle class="mt-4 text-lg"
                                    >Task #{{ task.task_id }}</CardTitle
                                >
                                <CardDescription
                                    class="line-clamp-1 font-medium text-foreground"
                                >
                                    {{ task.theme }}
                                </CardDescription>
                            </CardHeader>
                            <Separator />
                            <CardFooter
                                class="p-3 flex items-center justify-between gap-2"
                            >
                                <div class="flex gap-1">
                                    <TooltipProvider>
                                        <Tooltip>
                                            <TooltipTrigger as-child>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    class="h-9 w-9"
                                                    :disabled="
                                                        task.status !==
                                                        'completed'
                                                    "
                                                    @click="
                                                        router.push(
                                                            `/graph/${task.task_id}`,
                                                        )
                                                    "
                                                >
                                                    <BarChart3
                                                        class="w-4 h-4"
                                                    />
                                                </Button>
                                            </TooltipTrigger>
                                            <TooltipContent
                                                >View Graph</TooltipContent
                                            >
                                        </Tooltip>
                                    </TooltipProvider>

                                    <TooltipProvider>
                                        <Tooltip>
                                            <TooltipTrigger as-child>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    class="h-9 w-9"
                                                    :disabled="
                                                        task.status !==
                                                        'completed'
                                                    "
                                                >
                                                    <Download class="w-4 h-4" />
                                                </Button>
                                            </TooltipTrigger>
                                            <TooltipContent
                                                >Export Topics</TooltipContent
                                            >
                                        </Tooltip>
                                    </TooltipProvider>

                                    <TooltipProvider>
                                        <Tooltip>
                                            <TooltipTrigger as-child>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    class="h-9 w-9"
                                                    :disabled="
                                                        task.status !==
                                                        'completed'
                                                    "
                                                >
                                                    <MessageSquare
                                                        class="w-4 h-4"
                                                    />
                                                </Button>
                                            </TooltipTrigger>
                                            <TooltipContent
                                                >Chat</TooltipContent
                                            >
                                        </Tooltip>
                                    </TooltipProvider>
                                </div>

                                <TooltipProvider>
                                    <Tooltip>
                                        <TooltipTrigger as-child>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                class="h-9 w-9 text-destructive hover:bg-destructive/10 hover:text-destructive"
                                                @click="
                                                    handleDeleteTask(
                                                        task.task_id,
                                                    )
                                                "
                                            >
                                                <Trash2 class="w-4 h-4" />
                                            </Button>
                                        </TooltipTrigger>
                                        <TooltipContent
                                            >Delete Task</TooltipContent
                                        >
                                    </Tooltip>
                                </TooltipProvider>
                            </CardFooter>
                        </Card>
                    </div>
                </ScrollArea>
            </div>
        </main>
        <Footer />
    </div>
</template>
