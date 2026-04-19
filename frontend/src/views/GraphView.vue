<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useRoute } from "vue-router";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Maximize2 } from "lucide-vue-next";
import { getResult } from "../api";
import type { ResultModel } from "../models";
import { VueFlow, useVueFlow, MarkerType, type Node, type Edge } from "@vue-flow/core";
import type { CSSProperties } from "vue";
import { Background } from "@vue-flow/background";
import { Controls } from "@vue-flow/controls";
import Footer from "../components/Footer.vue";
import GraphHeader from "../components/graph/GraphHeader.vue";
import NodeDetailsDialog, { type GraphNodeData } from "../components/graph/NodeDetailsDialog.vue";
import GraphLoadingState from "../components/graph/GraphLoadingState.vue";
import {
    forceSimulation,
    forceLink,
    forceManyBody,
    forceX,
    forceY,
    type SimulationNodeDatum,
    type SimulationLinkDatum,
} from "d3-force";

const route = useRoute();
const taskId = Number(route.params.id);

const isLoading = ref(true);
const statusMessage = ref("Loading graph data...");
const nodes = ref<Node<GraphNodeData>[]>([]);
const edges = ref<Edge[]>([]);
const selectedNodeData = ref<GraphNodeData | null>(null);
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

const openDetails = (data: GraphNodeData) => {
    selectedNodeData.value = data;
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

interface SimulationNode extends SimulationNodeDatum {
    id: string;
    label: string;
    data: GraphNodeData;
    class: string;
    style: { borderColor: string };
}

interface SimulationLink extends SimulationLinkDatum<SimulationNode> {
    id: string;
    label: string;
}

const processGraphData = (data: ResultModel) => {
    const simulationNodes: SimulationNode[] = [];
    const simulationLinks: SimulationLink[] = [];
    const nodeToClusterColor = new Map<string, string>();

    const clusterColorMap = new Map<number, string>();
    data.clusters.forEach((_, idx) => {
        const color = CLUSTER_COLORS[idx % CLUSTER_COLORS.length];
        clusterColorMap.set(idx, color);
    });

    data.clusters.forEach((cluster, idx) => {
        const clusterColor = clusterColorMap.get(idx) || "#ccc";
        cluster.documents.forEach((doc) => {
            const node: SimulationNode = {
                id: doc.id,
                label: doc.content
                    ? doc.content.substring(0, 100) + "..."
                    : doc.id,
                data: {
                    clusterId: idx,
                    content: doc.content,
                    color: clusterColor,
                    clusterName: cluster.title || `Cluster ${idx + 1}`,
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

    data.relations.forEach((relation, idx) => {
        simulationLinks.push({
            id: `e-${relation.document_A}-${relation.document_B}-${idx}`,
            source: relation.document_A,
            target: relation.document_B,
            label: relation.relationship,
        });
    });

    const clusterCenters = new Map<number, { x: number; y: number }>();
    data.clusters.forEach((_, idx) => {
        clusterCenters.set(idx, {
            x: (idx % 3) * 1200,
            y: Math.floor(idx / 3) * 1200,
        });
    });

    const simulation = forceSimulation<SimulationNode>(simulationNodes)
        .force(
            "link",
            forceLink<SimulationNode, SimulationLink>(simulationLinks)
                .id((d) => d.id)
                .distance(800),
        )
        .force("charge", forceManyBody().strength(-8000))
        .force(
            "x",
            forceX<SimulationNode>(
                (d) => clusterCenters.get(d.data.clusterId)?.x || 0,
            ).strength(0.1),
        )
        .force(
            "y",
            forceY<SimulationNode>(
                (d) => clusterCenters.get(d.data.clusterId)?.y || 0,
            ).strength(0.1),
        )
        .stop();

    for (let i = 0; i < 300; ++i) simulation.tick();

    nodes.value = simulationNodes.map((n) => ({
        id: n.id,
        type: "custom",
        label: n.label,
        position: { x: n.x || 0, y: n.y || 0 },
        data: n.data,
        class: n.class,
        style: n.style as CSSProperties,
    })) as Node<GraphNodeData>[];

    edges.value = simulationLinks.map((l) => {
        const sourceId = typeof l.source === "object" ? (l.source as SimulationNode).id : (l.source as string);
        const targetId = typeof l.target === "object" ? (l.target as SimulationNode).id : (l.target as string);
        const color = nodeToClusterColor.get(sourceId) || "#3b82f6";
        return {
            id: l.id,
            source: sourceId,
            target: targetId,
            label: l.label,
            animated: true,
            style: { stroke: color, strokeWidth: 3 },
            markerEnd: {
                type: MarkerType.ArrowClosed,
                color: color,
            },
            labelBgPadding: [8, 4] as [number, number],
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

const formattedNodes = ref<Node<GraphNodeData>[]>([]);
const formattedEdges = ref<Edge[]>([]);

watch([nodes, highlightedNodeId, relatedNodeIds], () => {
    formattedNodes.value = nodes.value.map((node): Node<GraphNodeData> => {
        const isHighlighted =
            highlightedNodeId.value === null ||
            relatedNodeIds.value.has(node.id);
        return {
            ...node,
            class: `${node.class} ${!isHighlighted ? "grayscale opacity-20" : ""}`,
        };
    });
}, { immediate: true });

watch([edges, highlightedNodeId], () => {
    formattedEdges.value = edges.value.map((edge): Edge => {
        const isHighlighted =
            highlightedNodeId.value === null ||
            edge.source === highlightedNodeId.value ||
            edge.target === highlightedNodeId.value;
        return {
            ...edge,
            class: !isHighlighted ? "opacity-10 grayscale" : "",
        };
    });
}, { immediate: true });
</script>

<template>
    <div class="h-screen w-screen flex flex-col font-sans bg-background">
        <GraphHeader :task-id="taskId" />

        <main class="flex-1 bg-muted/20 relative overflow-hidden">
            <GraphLoadingState
                :is-loading="isLoading"
                :status-message="statusMessage"
                :has-nodes="nodes.length > 0"
            />

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
                            @click.stop="openDetails(data)"
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

        <NodeDetailsDialog
            v-model:is-open="isDetailOpen"
            :selected-node-data="selectedNodeData"
        />
    </div>
</template>

<style>
.vue-flow__node {
    white-space: normal;
    word-wrap: break-word;
}
</style>
