<script setup lang="ts">
import Navbar from '@/components/NavBar.vue'
import Icon from '@/components/SvgIcon.vue'
import RepoSelectModal from '@/components/RepoSelectModal.vue'
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import { generateUniqueEndpointName } from '@/utils/urlUtils'

const router = useRouter()

// Modal state
const isModalOpen = ref(false)
const selectedRepository = ref('')

// Keyboard-aware positioning
const chatboxBottom = ref('1rem')

const userText = ref('')
const isValidPrompt = computed(() => userText.value.trim().length >= 20)

const updateChatboxPosition = () => {
  if (!window.visualViewport) return

  const viewportHeight = window.visualViewport.height
  const windowHeight = window.innerHeight
  const keyboardHeight = windowHeight - viewportHeight

  if (keyboardHeight > 100) {
    chatboxBottom.value = `${keyboardHeight + 16}px`
  } else {
    chatboxBottom.value = '1rem'
  }
}

const openModal = () => {
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

const handleRepositorySelect = (repository: string) => {
  selectedRepository.value = repository
  closeModal()
}

const navigateToSearch = () => {
  const promptText = userText.value.trim()

  if (!isValidPrompt.value) {
    textareaRef.value?.focus()
    return
  }

  const endpoint = generateUniqueEndpointName(promptText)

  router.push({
    name: 'search',
    params: { endpoint },
    state: {
      query: promptText,
      repo: selectedRepository.value || null,
    },
  })
}

const typingTexts = [
  'Explain the error that’s been driving you crazy…',
  'Paste your stack trace or error message…',
  'Describe what you already tried…',
]

const typingSpeed = 50
const deletingSpeed = 50
const pauseDuration = 300

const placeholderText = ref('')
const currentTextIndex = ref(0)
const currentCharIndex = ref(0)
const isDeleting = ref(false)
const isPaused = ref(false)
let timer: ReturnType<typeof setTimeout> | null = null

const clearTimer = () => {
  if (timer) clearTimeout(timer)
  timer = null
}

const pauseTyping = () => {
  isPaused.value = true
  clearTimer()
}

const resumeTyping = () => {
  if (isPaused.value) {
    isPaused.value = false
    if (!timer) timer = setTimeout(tick, 300)
  }
}

const tick = () => {
  if (isPaused.value) return
  const fullText = typingTexts[currentTextIndex.value]

  if (isDeleting.value) {
    if (placeholderText.value.length === 0) {
      // Move to next phrase
      isDeleting.value = false
      currentTextIndex.value = (currentTextIndex.value + 1) % typingTexts.length
      currentCharIndex.value = 0
      timer = setTimeout(tick, pauseDuration)
    } else {
      placeholderText.value = placeholderText.value.slice(0, -1)
      timer = setTimeout(tick, deletingSpeed)
    }
  } else {
    if (currentCharIndex.value < fullText.length) {
      placeholderText.value += fullText[currentCharIndex.value]
      currentCharIndex.value += 1
      timer = setTimeout(tick, typingSpeed)
    } else {
      // Finished typing, wait, then start deleting
      timer = setTimeout(() => {
        if (isPaused.value) return
        isDeleting.value = true
        timer = setTimeout(tick, deletingSpeed)
      }, pauseDuration)
    }
  }
}

const textareaRef = ref<HTMLTextAreaElement | null>(null)

const onInput = (e: Event) => {
  const val = (e.target as HTMLTextAreaElement).value
  userText.value = val
  if (val && val.length > 0) {
    pauseTyping()
  } else {
    resumeTyping()
  }
}

const onBlur = (e: Event) => {
  const val = (e.target as HTMLTextAreaElement).value
  if (!val || val.length === 0) {
    resumeTyping()
  }
}

onMounted(() => {
  timer = setTimeout(tick, 300)

  // If the textarea is pre-filled (e.g. browser restore), pause immediately
  const el = textareaRef.value
  if (el && el.value && el.value.length > 0) {
    pauseTyping()
    userText.value = el.value
  }

  // Listen for keyboard changes
  if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', updateChatboxPosition)
    window.visualViewport.addEventListener('scroll', updateChatboxPosition)
  }
})

onBeforeUnmount(() => {
  clearTimer()

  // Clean up keyboard listeners
  if (window.visualViewport) {
    window.visualViewport.removeEventListener('resize', updateChatboxPosition)
    window.visualViewport.removeEventListener('scroll', updateChatboxPosition)
  }
})
</script>

<template>
  <Navbar />

  <!-- Background Gradient -->
  <div class="absolute inset-0 -z-20 h-dvh w-full overflow-hidden opacity-90 dark:opacity-70">
    <div class="absolute inset-0 mt-0 h-full">
      <div
        class="absolute -bottom-96 left-1/2 aspect-square h-[105%] w-[125%] -translate-x-1/2 overflow-hidden sm:-bottom-40 sm:h-full md:w-[100%] lg:w-[100%] xl:w-[100%] 2xl:mx-auto"
        style="
          background-image: url('/background/gradient.png');
          background-size: cover;
          background-repeat: no-repeat;
          background-position: center top;
        "
      ></div>
    </div>
  </div>

  <div
    class="absolute inset-0 -z-10 opacity-10"
    style="
      background-image: url(/background/grain.png);
      background-size: 100px 100px;
      background-repeat: repeat;
      background-position: left top;
    "
  ></div>

  <!--  Hero Heading & Subheading -->
  <div class="mt-30 flex flex-col items-center justify-center gap-4 md:mt-12">
    <Icon name="hero-logo" />
    <h1
      class="text-foreground mx-auto line-clamp-1 flex w-fit gap-3 text-center text-3xl tracking-tighter text-pretty sm:text-[2rem] md:min-w-fit md:text-[3rem]"
    >
      Find solutions from GitHub
    </h1>
    <p class="text-foreground/80 text-center text-xs sm:min-w-fit sm:text-base">
      Search across Github issues and discover how others fixed similar problems
    </p>
  </div>
  <!-- Prompt -->
  <div
    class="border-line-secondary bg-background absolute mt-10 flex w-[90vw] flex-col gap-2 rounded-3xl border p-4 shadow-xl sm:relative md:mt-12 md:w-[42rem] lg:w-[48rem]"
    :style="{ bottom: chatboxBottom }"
  >
    <textarea
      ref="textareaRef"
      id="hs-textarea-ex-1"
      class="placeholder:text-muted-foreground/60 text-foreground block h-20 max-h-24 resize-none pb-8 text-sm placeholder:text-sm focus:outline-none disabled:pointer-events-none disabled:opacity-50 sm:pb-12 sm:text-base sm:placeholder:text-base"
      autofocus
      :placeholder="placeholderText"
      data-hs-textarea-auto-height=""
      @input="onInput"
      @blur="onBlur"
    ></textarea>

    <!-- Toolbar -->
    <div class="inset-x-px bottom-px">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <!-- Button Group -->
        <div class="flex items-center">
          <button
            type="button"
            @click="openModal"
            class="active:bg-fill bg-fill/40 border-line-secondary flex shrink-0 cursor-pointer items-center justify-baseline gap-2 rounded-lg border px-4 py-2 transition-all duration-100 hover:shadow-sm focus:z-10 focus:outline-hidden active:translate-y-px active:scale-98"
            :class="{
              'bg-brand/10 border-brand/30': selectedRepository,
            }"
          >
            <Icon name="github" class="fill-foreground h-4 w-4" />
            <p class="text-foreground text-xs sm:text-sm">
              {{ selectedRepository || 'Select Repo' }}
            </p>
          </button>
        </div>

        <!-- Submit Button -->
        <div class="flex items-center gap-x-1">
          <button
            type="button"
            @click="navigateToSearch"
            :disabled="!isValidPrompt"
            class="bg-brand hover:bg-brand/90 focus:bg-brand/90 disabled:bg-brand/50 inline-flex size-8 shrink-0 cursor-pointer items-center justify-center rounded-lg text-white transition-transform focus:z-10 focus:outline-hidden active:translate-y-px active:scale-98 disabled:cursor-not-allowed"
          >
            <Icon name="arrow-right" />
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Repository Selection Modal -->
  <RepoSelectModal :is-open="isModalOpen" @close="closeModal" @submit="handleRepositorySelect" />
</template>
