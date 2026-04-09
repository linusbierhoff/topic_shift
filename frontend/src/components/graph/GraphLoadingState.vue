<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Loader2, Info } from "lucide-vue-next";
import { useRouter } from "vue-router";

defineProps<{
    isLoading: boolean;
    statusMessage: string;
    hasNodes: boolean;
}>();

const router = useRouter();
</script>

<template>
    <div
        v-if="isLoading"
        class="absolute inset-0 flex flex-col items-center justify-center text-muted-foreground z-10 bg-background/80 backdrop-blur-sm gap-4"
    >
        <div class="flex flex-col items-center gap-2">
            <Loader2 class="w-10 h-10 animate-spin text-primary" />
            <p class="font-medium animate-pulse">{{ statusMessage }}</p>
        </div>
    </div>

    <div
        v-else-if="!hasNodes"
        class="absolute inset-0 flex items-center justify-center z-10 p-6"
    >
        <Card class="max-w-md w-full text-center p-8">
            <CardHeader>
                <div class="mx-auto w-12 h-12 rounded-full bg-destructive/10 flex items-center justify-center mb-4">
                    <Info class="w-6 h-6 text-destructive" />
                </div>
                <CardTitle>Unable to Load Graph</CardTitle>
            </CardHeader>
            <CardContent>
                <p class="text-muted-foreground">{{ statusMessage }}</p>
            </CardContent>
            <CardFooter class="justify-center">
                <Button variant="outline" @click="router.push('/')">Return to Dashboard</Button>
            </CardFooter>
        </Card>
    </div>
</template>
