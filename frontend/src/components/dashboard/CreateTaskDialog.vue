<script setup lang="ts">
import { ref, useTemplateRef } from "vue";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, Upload, FileUp, FileText } from "lucide-vue-next";
import { startTask } from "../../api";

const props = defineProps<{
    onTaskCreated: () => Promise<void>;
}>();

const isUploading = ref(false);
const isModalOpen = ref(false);

const theme = ref("");
const removeSubstrings = ref("");
const clusters = ref<number | undefined>(undefined);
const windowSize = ref<number | undefined>(undefined);
const selectedFile = ref<File | undefined>(undefined);

const fileInput = useTemplateRef<HTMLInputElement>("fileInput");

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
            windowSize.value,
        );
        if (data && data.task_id) {
            isModalOpen.value = false;
            // Reset form
            theme.value = "";
            removeSubstrings.value = "";
            clusters.value = undefined;
            windowSize.value = undefined;
            selectedFile.value = undefined;
            await props.onTaskCreated();
        }
    } catch (error) {
        console.error("Upload failed", error);
    } finally {
        isUploading.value = false;
    }
};

defineExpose({
    isModalOpen,
});
</script>

<template>
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
                        for="windowSize"
                        class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
                        >Window Size</Label
                    >
                    <Input
                        id="windowSize"
                        type="number"
                        v-model="windowSize"
                        placeholder="Default (5)"
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
                                <p class="text-xs text-muted-foreground mt-1">
                                    Maximum size: 50MB
                                </p>
                            </div>
                        </template>
                        <template v-else>
                            <div
                                class="w-12 h-12 rounded-full bg-green-500/10 flex items-center justify-center"
                            >
                                <FileText class="w-6 h-6 text-green-600" />
                            </div>
                            <div class="text-center">
                                <p
                                    class="text-sm font-medium truncate max-w-50"
                                >
                                    {{ selectedFile.name }}
                                </p>
                                <p class="text-xs text-muted-foreground mt-1">
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
</template>
