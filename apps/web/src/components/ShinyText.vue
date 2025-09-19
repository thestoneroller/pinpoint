<script setup lang="ts">
import { computed } from 'vue'

interface ShinyTextProps {
  text: string
  disabled?: boolean
  speed?: number
  className?: string
}

const props = withDefaults(defineProps<ShinyTextProps>(), {
  text: '',
  disabled: false,
  speed: 3,
  className: '',
})

const animationDuration = computed(() => `${props.speed}s`)
</script>

<template>
  <div
    :class="`shiny-text text-brand/70 dark:bg-brand/90 bg-clip-text text-sm ${!props.disabled ? 'animate-shine' : ''} ${props.className}`"
    :style="{
      backgroundImage:
        'linear-gradient(120deg, rgba(255, 255, 255, 0) 40%, var(--shine-color) 50%, rgba(255, 255, 255, 0) 60%)',
      backgroundSize: '200% 100%',
      WebkitBackgroundClip: 'text',
      animationDuration: animationDuration,
    }"
  >
    {{ props.text }}
  </div>
</template>

<style scoped>
.shiny-text {
  --shine-color: var(--color-muted-foreground);
  position: relative;
  display: inline-block;
}
:global(.dark) .shiny-text {
  --shine-color: rgba(255, 255, 255, 0.8);
}

@keyframes shine {
  0% {
    background-position: 120% 0;
  }
  100% {
    background-position: -20% 0;
  }
}

.animate-shine {
  animation-name: shine;
  animation-duration: var(--shine-duration, 3s);
  animation-iteration-count: infinite;
}
</style>
