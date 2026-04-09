<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
} from "@/components/ui/card";
import { FileText } from "lucide-vue-next";

defineProps<{
    onAction: () => void;
}>();
</script>

<template>
    <div class="h-100 flex items-center justify-center">
        <Card class="w-full max-w-md text-center p-12 bg-transparent border-dashed">
            <CardContent class="flex flex-col items-center gap-4">
                <div class="w-16 h-16 rounded-full bg-muted flex items-center justify-center">
                    <FileText class="w-8 h-8 text-muted-foreground" />
                </div>
                <div>
                    <h3 class="text-lg font-semibold">No analyses yet</h3>
                    <p class="text-muted-foreground mt-1">
                        Upload your first PDF to begin extracting topics.
                    </p>
                </div>
                <Button variant="outline" class="mt-4" @click="onAction">
                    Get Started
                </Button>
            </CardContent>
        </Card>
    </div>
</template>
