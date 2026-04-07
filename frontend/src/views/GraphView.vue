<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { Button } from "@/components/ui/button";
import { getTask } from "../api";
import { VueFlow } from "@vue-flow/core";
import { Background } from "@vue-flow/background";
import { Controls } from "@vue-flow/controls";
import { Loader2, ArrowLeft } from "lucide-vue-next";
import Footer from "../components/Footer.vue";

const router = useRouter();
const route = useRoute();
const taskId = Number(route.params.id);

const isLoading = ref(true);
const statusMessage = ref("Loading graph data...");
const nodes = ref<any[]>([]);
const edges = ref<any[]>([]);

let pollInterval: number | undefined;

const fetchTaskData = async () => {
    try {
        const data = await getTask(taskId);
        if (!data) {
            statusMessage.value = "Task not found.";
            isLoading.value = false;
            return;
        }

        if (data.clusters && data.relations) {
            processGraphData(data);
            isLoading.value = false;
            if (pollInterval) clearInterval(pollInterval);
        } else if (data.status === "failed") {
            statusMessage.value = "Task failed processing.";
            isLoading.value = false;
            if (pollInterval) clearInterval(pollInterval);
        } else {
            statusMessage.value = "Task is still processing...";
        }
    } catch (error) {
        console.error("Error fetching task", error);
        statusMessage.value = "Error loading graph.";
        isLoading.value = false;
        if (pollInterval) clearInterval(pollInterval);
    }
};

onMounted(() => {
    fetchTaskData();
    // Poll just in case the task is not yet completed
    pollInterval = window.setInterval(fetchTaskData, 10000);
});

onUnmounted(() => {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
});

const processGraphData = (data: any) => {
    const newNodes: any[] = [];
    const newEdges: any[] = [];

    data.clusters.forEach((cluster: any, clusterIdx: number) => {
        cluster.documents.forEach((doc: any, docIdx: number) => {
            newNodes.push({
                id: doc.id,
                label: doc.content
                    ? doc.content.substring(0, 100) + "..."
                    : doc.id,
                position: { x: clusterIdx * 400, y: docIdx * 150 },
                data: { clusterId: cluster.id, content: doc.content },
                class: "bg-white border-2 border-primary rounded-md p-4 shadow-sm w-[300px] text-sm",
            });
        });
    });

    data.relations.forEach((relation: any, idx: number) => {
        newEdges.push({
            id: `e-${relation.document_A}-${relation.document_B}-${idx}`,
            source: relation.document_A,
            target: relation.document_B,
            label: relation.relationship,
            animated: true,
            style: { stroke: "currentColor" },
            labelBgPadding: [8, 4],
            labelBgBorderRadius: 4,
            labelBgStyle: { fill: "#fff", color: "#000", fillOpacity: 0.7 },
        });
    });

    nodes.value = newNodes;
    edges.value = newEdges;
};
</script>

<template>
    <div class="h-screen w-screen flex flex-col font-sans">
        <header
            class="h-16 border-b flex items-center justify-between px-6 bg-white shrink-0 z-10"
        >
            <div class="flex items-center gap-4">
                <Button variant="ghost" size="icon" @click="router.push('/')">
                    <ArrowLeft class="w-5 h-5" />
                </Button>
                <h1 class="text-xl font-bold text-primary">
                    Topic Shift Graph (Task #{{ taskId }})
                </h1>
            </div>
        </header>

        <main class="flex-1 bg-gray-50/50 relative">
            <div
                v-if="isLoading"
                class="absolute inset-0 flex flex-col items-center justify-center text-muted-foreground z-10 bg-white/50 backdrop-blur-sm gap-4"
            >
                <Loader2 class="w-8 h-8 animate-spin text-primary" />
                <p>{{ statusMessage }}</p>
            </div>

            <div
                v-else-if="nodes.length === 0"
                class="absolute inset-0 flex items-center justify-center text-muted-foreground z-10"
            >
                <div class="text-center">
                    <p class="text-lg font-medium">No graph data</p>
                    <p class="text-sm text-red-500 mt-2">{{ statusMessage }}</p>
                </div>
            </div>

            <VueFlow
                v-show="nodes.length > 0 && !isLoading"
                :nodes="nodes"
                :edges="edges"
                class="h-full w-full"
                :fit-view-on-init="true"
            >
                <Background />
                <Controls />
            </VueFlow>
        </main>
        <Footer />
    </div>
</template>
<style>
.vue-flow__node {
    white-space: normal;
    word-wrap: break-word;
}
</style>
