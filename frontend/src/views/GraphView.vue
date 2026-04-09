<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardHeader,
    CardTitle,
    CardContent,
    CardFooter,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/dialog";
import { getResult } from "../api";
import { VueFlow, useVueFlow, MarkerType } from "@vue-flow/core";
import { Background } from "@vue-flow/background";
import { Controls } from "@vue-flow/controls";
import {
    Loader2,
    ArrowLeft,
    X,
    Maximize2,
    BarChart3,
    Info,
} from "lucide-vue-next";
import Footer from "../components/Footer.vue";
import {
    forceSimulation,
    forceLink,
    forceManyBody,
    forceX,
    forceY,
} from "d3-force";

const router = useRouter();
const route = useRoute();
const taskId = Number(route.params.id);

const isLoading = ref(true);
const statusMessage = ref("Loading graph data...");
const nodes = ref<any[]>([]);
const edges = ref<any[]>([]);
const selectedNode = ref<any>(null);
const isDetailOpen = ref(false);
const highlightedNodeId = ref<string | null>(null);
const relatedNodeIds = ref<Set<string>>(new Set());

const CLUSTER_COLORS = [
    "#3b82f6", // blue
    "#10b981", // emerald
    "#f59e0b", // amber
    "#ef4444", // red
    "#8b5cf6", // violet
    "#ec4899", // pink
    "#06b6d4", // cyan
    "#f97316", // orange
];

let pollInterval: number | undefined;

const { fitView, onNodeClick, onPaneClick } = useVueFlow();

onNodeClick((event) => {
    const nodeId = event.node.id;
    highlightedNodeId.value = nodeId;

    // Find related nodes
    const related = new Set<string>();
    related.add(nodeId);
    edges.value.forEach((edge) => {
        if (edge.source === nodeId) related.add(edge.target);
        if (edge.target === nodeId) related.add(edge.source);
    });
    relatedNodeIds.value = related;
});

onPaneClick(() => {
    highlightedNodeId.value = null;
    relatedNodeIds.value = new Set();
});

const openDetails = (node: any) => {
    selectedNode.value = node;
    isDetailOpen.value = true;
};

const fetchTaskData = async () => {
    try {
        const data = await getResult(taskId);
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
    pollInterval = window.setInterval(fetchTaskData, 10000);
});

onUnmounted(() => {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
});

const processGraphData = (data: any) => {
    const simulationNodes: any[] = [];
    const simulationLinks: any[] = [];
    const nodeToClusterColor = new Map();

    const clusterColorMap = new Map();
    data.clusters.forEach((cluster: any, idx: number) => {
        const color = CLUSTER_COLORS[idx % CLUSTER_COLORS.length];
        clusterColorMap.set(idx, color);
    });

    data.clusters.forEach((cluster: any, idx: number) => {
        const clusterColor = clusterColorMap.get(idx);
        cluster.documents.forEach((doc: any) => {
            const node = {
                id: doc.id,
                label: doc.content
                    ? doc.content.substring(0, 100) + "..."
                    : doc.id,
                data: {
                    clusterId: cluster.id,
                    content: doc.content,
                    color: clusterColor,
                    clusterName: cluster.name || `Cluster ${idx + 1}`,
                },
                class: "bg-white border-2 rounded-xl p-4 shadow-sm w-[300px] text-sm cursor-pointer hover:shadow-md transition-all",
                style: { borderColor: clusterColor },
                x: (Math.random() - 0.5) * 1000,
                y: (Math.random() - 0.5) * 1000,
            };
            simulationNodes.push(node);
            nodeToClusterColor.set(doc.id, clusterColor);
        });
    });

    data.relations.forEach((relation: any, idx: number) => {
        simulationLinks.push({
            id: `e-${relation.document_A}-${relation.document_B}-${idx}`,
            source: relation.document_A,
            target: relation.document_B,
            label: relation.relationship,
        });
    });

    const clusterCenters = new Map();
    data.clusters.forEach((cluster: any, idx: number) => {
        clusterCenters.set(cluster.id, {
            x: (idx % 3) * 1200,
            y: Math.floor(idx / 3) * 1200,
        });
    });

    const simulation = forceSimulation(simulationNodes)
        .force(
            "link",
            forceLink(simulationLinks)
                .id((d: any) => d.id)
                .distance(800),
        )
        .force("charge", forceManyBody().strength(-8000))
        .force(
            "x",
            forceX(
                (d: any) => clusterCenters.get(d.data.clusterId)?.x || 0,
            ).strength(0.1),
        )
        .force(
            "y",
            forceY(
                (d: any) => clusterCenters.get(d.data.clusterId)?.y || 0,
            ).strength(0.1),
        )
        .stop();

    for (let i = 0; i < 300; ++i) simulation.tick();

    nodes.value = simulationNodes.map((n) => ({
        id: n.id,
        type: "custom",
        label: n.label,
        position: { x: n.x, y: n.y },
        data: n.data,
        class: n.class,
        style: n.style,
    }));

    edges.value = simulationLinks.map((l) => {
        const sourceId = typeof l.source === "object" ? l.source.id : l.source;
        const color = nodeToClusterColor.get(sourceId) || "#3b82f6";
        return {
            id: l.id,
            source: sourceId,
            target: typeof l.target === "object" ? l.target.id : l.target,
            label: l.label,
            animated: true,
            style: { stroke: color, strokeWidth: 3 },
            markerEnd: {
                type: MarkerType.ArrowClosed,
                color: color,
            },
            labelBgPadding: [8, 4],
            labelBgBorderRadius: 4,
            labelBgStyle: {
                fill: "#fff",
                color: color,
                fillOpacity: 0.9,
                fontWeight: "bold",
            },
        };
    });

    setTimeout(() => {
        fitView();
    }, 200);
};

const formattedNodes = computed(() => {
    return nodes.value.map((node) => {
        const isHighlighted =
            highlightedNodeId.value === null ||
            relatedNodeIds.value.has(node.id);
        return {
            ...node,
            class: `${node.class} ${!isHighlighted ? "grayscale opacity-20" : ""}`,
        };
    });
});

const formattedEdges = computed(() => {
    return edges.value.map((edge) => {
        const isHighlighted =
            highlightedNodeId.value === null ||
            edge.source === highlightedNodeId.value ||
            edge.target === highlightedNodeId.value;
        return {
            ...edge,
            class: !isHighlighted ? "opacity-10 grayscale" : "",
        };
    });
});
</script>

<template>
    <div class="h-screen w-screen flex flex-col font-sans bg-background">
        <header
            class="h-16 border-b flex items-center justify-between px-6 bg-card shrink-0 z-10"
        >
            <div class="flex items-center gap-4">
                <Button variant="ghost" size="icon" @click="router.push('/')">
                    <ArrowLeft class="w-5 h-5" />
                </Button>
                <div class="flex items-center gap-2">
                    <BarChart3 class="w-5 h-5 text-primary" />
                    <h1 class="text-xl font-bold tracking-tight">
                        Topic Analysis Graph
                        <span class="text-muted-foreground font-normal ml-1"
                            >#{{ taskId }}</span
                        >
                    </h1>
                </div>
            </div>
        </header>

        <main class="flex-1 bg-muted/20 relative overflow-hidden">
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
                v-else-if="nodes.length === 0"
                class="absolute inset-0 flex items-center justify-center z-10 p-6"
            >
                <Card class="max-w-md w-full text-center p-8">
                    <CardHeader>
                        <div
                            class="mx-auto w-12 h-12 rounded-full bg-destructive/10 flex items-center justify-center mb-4"
                        >
                            <Info class="w-6 h-6 text-destructive" />
                        </div>
                        <CardTitle>Unable to Load Graph</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p class="text-muted-foreground">{{ statusMessage }}</p>
                    </CardContent>
                    <CardFooter class="justify-center">
                        <Button variant="outline" @click="router.push('/')"
                            >Return to Dashboard</Button
                        >
                    </CardFooter>
                </Card>
            </div>

            <VueFlow
                v-show="nodes.length > 0 && !isLoading"
                :nodes="formattedNodes"
                :edges="formattedEdges"
                class="h-full w-full"
                :fit-view-on-init="true"
            >
                <template #node-custom="{ data, label }">
                    <Card
                        class="border-0 shadow-none bg-transparent group relative"
                    >
                        <div class="pr-8">
                            {{ label }}
                        </div>
                        <Button
                            variant="secondary"
                            size="icon"
                            class="absolute top-0 right-0 opacity-0 group-hover:opacity-100 transition-opacity h-7 w-7"
                            @click.stop="openDetails({ data, label })"
                        >
                            <Maximize2 class="w-3.5 h-3.5" />
                        </Button>
                    </Card>
                </template>
                <Background />
                <Controls />
            </VueFlow>
        </main>
        <Footer />

        <!-- Node Detail Dialog -->
        <Dialog v-model:open="isDetailOpen">
            <DialogContent
                class="sm:max-w-2xl max-h-[90vh] flex flex-col p-0 overflow-hidden"
            >
                <DialogHeader class="p-6 pb-0" v-if="selectedNode">
                    <div class="flex items-center gap-2 mb-2">
                        <div
                            class="w-3 h-3 rounded-full"
                            :style="{
                                backgroundColor: selectedNode.data.color,
                            }"
                        ></div>
                        <span
                            class="text-xs font-bold uppercase tracking-wider text-muted-foreground"
                        >
                            {{ selectedNode.data.clusterName }}
                        </span>
                    </div>
                    <DialogTitle class="text-xl font-bold"
                        >Document Fragment</DialogTitle
                    >
                </DialogHeader>

                <Separator class="my-4" />

                <ScrollArea class="flex-1 px-6 pb-6">
                    <div
                        class="text-base leading-relaxed text-foreground/90 whitespace-pre-wrap font-sans"
                    >
                        {{ selectedNode?.data.content }}
                    </div>
                </ScrollArea>
            </DialogContent>
        </Dialog>
    </div>
</template>

<style>
.vue-flow__node {
    white-space: normal;
    word-wrap: break-word;
}
</style>
