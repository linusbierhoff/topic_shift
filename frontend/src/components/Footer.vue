<script setup lang="ts"></script>

<template>
    <footer
        class="h-14 border-t flex items-center justify-between px-6 bg-white shrink-0 text-sm text-muted-foreground z-10 relative"
    >
        <div>
            &copy; {{ new Date().getFullYear() }}
            <a
                href="https://linusbierhoff.com"
                target="_blank"
                rel="noopener noreferrer"
                class="hover:text-primary transition-colors hover:underline"
                >Linus Bierhoff</a
            >
        </div>
        <div class="flex items-center gap-4">
            <a
                href="https://github.com/linusbierhoff/topic_shift"
                target="_blank"
                rel="noopener noreferrer"
                class="hover:text-primary transition-colors hover:underline"
                >GitHub</a
            >
            <a
                href="#"
                class="hover:text-primary transition-colors hover:underline"
                >Impressum</a
            >
            <a
                href="#"
                class="hover:text-primary transition-colors hover:underline"
                >Privacy Policy</a
            >
        </div>
    </footer>
</template>
