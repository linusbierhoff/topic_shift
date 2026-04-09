<script setup lang="ts">
import { Separator } from "@/components/ui/separator";
</script>

<template>
    <footer class="bg-card border-t py-4 px-6 shrink-0 z-10 relative">
        <div
            class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground"
        >
            <div class="flex items-center gap-2">
                <p>&copy; {{ new Date().getFullYear() }}</p>
                <Separator orientation="vertical" class="h-3 mx-1" />
                <a
                    href="https://linusbierhoff.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="font-medium hover:text-primary transition-colors"
                >
                    Linus Bierhoff
                </a>
            </div>

            <nav class="flex items-center gap-6">
                <a
                    href="https://github.com/linusbierhoff/topic_shift"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="hover:text-primary transition-colors flex items-center gap-1"
                >
                    Source Code
                </a>
                <a href="#" class="hover:text-primary transition-colors">
                    Legal
                </a>
                <a href="#" class="hover:text-primary transition-colors">
                    Privacy
                </a>
            </nav>
        </div>
    </footer>
</template>
