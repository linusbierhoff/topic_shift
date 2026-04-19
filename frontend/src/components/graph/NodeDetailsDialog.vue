<script setup lang="ts">
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

import type { CSSProperties, VNode, Component } from "vue";

export interface GraphNodeData {
    clusterId: number;
    content: string;
    color: string;
    clusterName: string;
}

export interface GraphNode {
    id: string;
    data: GraphNodeData;
    label?: string | VNode | Component;
    class?: string;
    style?: CSSProperties;
    position: { x: number; y: number };
    type?: string;
}

defineProps<{
    isOpen: boolean;
    selectedNodeData: GraphNodeData | null;
}>();

const emit = defineEmits<{
    (e: 'update:isOpen', value: boolean): void;
}>();
</script>

<template>
    <Dialog :open="isOpen" @update:open="emit('update:isOpen', $event)">
        <DialogContent class="sm:max-w-2xl max-h-[90vh] flex flex-col p-0 overflow-hidden">
            <DialogHeader class="p-6 pb-0" v-if="selectedNodeData">
                <div class="flex items-center gap-2 mb-2">
                    <div
                        class="w-3 h-3 rounded-full"
                        :style="{ backgroundColor: selectedNodeData.color }"
                    ></div>
                    <span class="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                        {{ selectedNodeData.clusterName }}
                    </span>
                </div>
                <DialogTitle class="text-xl font-bold">Document Fragment</DialogTitle>
            </DialogHeader>

            <Separator class="my-4" />

            <ScrollArea class="flex-1 px-6 pb-6">
                <div class="text-base leading-relaxed text-foreground/90 whitespace-pre-wrap font-sans">
                    {{ selectedNodeData?.content }}
                </div>
            </ScrollArea>

            <DialogFooter class="p-4 bg-muted/30 border-t">
                <Button @click="emit('update:isOpen', false)" variant="secondary">Close Details</Button>
            </DialogFooter>
        </DialogContent>
    </Dialog>
</template>
