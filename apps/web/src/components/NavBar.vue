<script setup lang="ts">
import Icon from '@/components/SvgIcon.vue'
import { ref, watch, onMounted } from 'vue'

const dark = ref(false)

const setTheme = (isDark: boolean) => {
  dark.value = isDark
  if (isDark) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    setTheme(savedTheme === 'dark')
  } else {
    setTheme(window.matchMedia('(prefers-color-scheme: dark)').matches)
  }
})

watch(dark, (isDark) => {
  setTheme(isDark)
})
</script>

<template>
  <nav class="flex w-full items-center justify-between gap-2 px-4 py-6 md:px-20">
    <div class="flex items-center justify-center gap-2">
      <Icon name="pinpoint" />
      <p class="font-alpha text-foreground text-xl sm:text-2xl">pinpoint</p>
    </div>
    <div class="flex items-center justify-center gap-4 md:gap-6">
      <a
        href="https://github.com/thestoneroller/pinpoint"
        target="_blank"
        rel="noopener noreferrer"
      >
        <Icon
          name="github"
          class="fill-foreground hover:fill-brand/90 active:fill-brand/90 focus:fill-brand/90 dark:hover:fill-brand/100 cursor-pointer transition-transform active:translate-y-px active:scale-98"
        />
      </a>
      <Icon
        @click="setTheme(!dark)"
        :name="dark ? 'light-theme' : 'dark-theme'"
        class="fill-foreground hover:fill-brand/90 active:fill-brand/90 focus:fill-brand/90 dark:hover:fill-brand/100 cursor-pointer transition-transform active:translate-y-px active:scale-98"
      />
    </div>
  </nav>
</template>
