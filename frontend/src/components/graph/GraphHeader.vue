<script setup lang="ts">
import { useRouter } from "vue-router";
import { Button } from "@/components/ui/button";
import { ArrowLeft, BarChart3 } from "lucide-vue-next";

defineProps<{
    taskId: number;
}>();

const router = useRouter();
</script>

<template>
    <header class="h-16 border-b flex items-center justify-between px-6 bg-card shrink-0 z-10">
        <div class="flex items-center gap-4">
            <Button variant="ghost" size="icon" @click="router.push('/')">
                <ArrowLeft class="w-5 h-5" />
            </Button>
            <div class="flex items-center gap-2">
                <BarChart3 class="w-5 h-5 text-primary" />
                <h1 class="text-xl font-bold tracking-tight">
                    Topic Analysis Graph <span class="text-muted-foreground font-normal ml-1">#{{ taskId }}</span>
                </h1>
            </div>
        </div>
    </header>
</template>
