import { ref, onMounted, watch } from 'vue'

export const dark = ref(false)

export const setTheme = (isDark: boolean) => {
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
