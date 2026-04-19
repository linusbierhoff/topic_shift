<script setup lang="ts">
import { useRouter } from "vue-router";
import {
    Card,

    CardDescription,
    CardHeader,
    CardTitle,
    CardFooter,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";
import type { FullTaskModel } from "../../models";
import {
    Loader2,
    FileText,
    Trash2,
    BarChart3,
    Download,
    MessageSquare,
} from "lucide-vue-next";

const props = defineProps<{
    task: FullTaskModel;
    onDelete: (taskId: number) => Promise<void>;
}>();

const router = useRouter();

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
</script>

<template>
    <Card class="group hover:shadow-md transition-all duration-300 border-muted/60">
        <CardHeader class="pb-3">
            <div class="flex items-start justify-between">
                <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                    <FileText class="w-5 h-5" />
                </div>
                <Badge :variant="getStatusVariant(task.status)" class="capitalize">
                    <Loader2 v-if="task.status === 'in_progress'" class="w-3 h-3 mr-1 animate-spin" />
                    {{ task.status.replace("_", " ") }}
                </Badge>
            </div>
            <CardTitle class="mt-4 text-lg">Task #{{ task.task_id }}</CardTitle>
            <CardDescription class="line-clamp-1 font-medium text-foreground">
                {{ task.theme }}
            </CardDescription>
        </CardHeader>
        <Separator />
        <CardFooter class="p-3 flex items-center justify-between gap-2">
            <div class="flex gap-1">
                <TooltipProvider>
                    <Tooltip>
                        <TooltipTrigger as-child>
                            <Button
                                variant="ghost"
                                size="icon"
                                class="h-9 w-9"
                                :disabled="task.status !== 'completed'"
                                @click="router.push(`/graph/${task.task_id}`)"
                            >
                                <BarChart3 class="w-4 h-4" />
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent>View Graph</TooltipContent>
                    </Tooltip>
                </TooltipProvider>

                <TooltipProvider>
                    <Tooltip>
                        <TooltipTrigger as-child>
                            <Button
                                variant="ghost"
                                size="icon"
                                class="h-9 w-9"
                                :disabled="task.status !== 'completed'"
                            >
                                <Download class="w-4 h-4" />
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent>Export Topics</TooltipContent>
                    </Tooltip>
                </TooltipProvider>

                <TooltipProvider>
                    <Tooltip>
                        <TooltipTrigger as-child>
                            <Button
                                variant="ghost"
                                size="icon"
                                class="h-9 w-9"
                                :disabled="task.status !== 'completed'"
                            >
                                <MessageSquare class="w-4 h-4" />
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent>Chat</TooltipContent>
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
                            @click="onDelete(task.task_id)"
                        >
                            <Trash2 class="w-4 h-4" />
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent>Delete Task</TooltipContent>
                </Tooltip>
            </TooltipProvider>
        </CardFooter>
    </Card>
</template>
