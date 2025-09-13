<script setup lang="ts">
import { ref, watch } from 'vue'
import Icon from './SvgIcon.vue'

interface Props {
  isOpen: boolean
}

interface Emits {
  (e: 'close'): void
  (e: 'submit', repository: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const repository = ref('')
const isSubmitting = ref(false)

// Reset form when modal opens
watch(
  () => props.isOpen,
  (newValue) => {
    if (newValue) {
      repository.value = ''
      isSubmitting.value = false
    }
  },
)

const closeModal = () => {
  emit('close')
}

const handleBackdropClick = (event: MouseEvent) => {
  if (event.target === event.currentTarget) {
    closeModal()
  }
}

const handleSubmit = () => {
  if (!repository.value.trim() || !isValidRepository(repository.value)) {
    return
  }

  isSubmitting.value = true

  emit('submit', repository.value.trim())

  setTimeout(() => {
    isSubmitting.value = false
    closeModal()
  }, 500)
}

const isValidRepository = (repo: string) => {
  const repoPattern = /^[a-zA-Z0-9._-]+\/[a-zA-Z0-9._-]+$/
  return repoPattern.test(repo.trim())
}

const canSubmit = () => {
  return repository.value.trim() && isValidRepository(repository.value) && !isSubmitting.value
}
</script>

<template>
  <!-- Modal Backdrop -->
  <Transition
    enter-active-class="transition-opacity duration-200 ease-out"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-200 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/30 px-4 pt-16 pb-4 backdrop-blur-sm md:items-center md:pt-0"
      @click="handleBackdropClick"
    >
      <!-- Modal Content -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 scale-95 translate-y-4"
        enter-to-class="opacity-100 scale-100 translate-y-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 scale-100 translate-y-0"
        leave-to-class="opacity-0 scale-95 translate-y-4"
      >
        <div
          v-if="isOpen"
          class="bg-background border-line-secondary relative mx-4 w-full max-w-md rounded-3xl border p-6 shadow-2xl"
          @click.stop
        >
          <!-- Header -->
          <div class="mb-6 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <h2 class="text-foreground text-xl font-semibold">Select Repository</h2>
            </div>
            <button
              @click="closeModal"
              class="text-muted-foreground hover:text-foreground cursor-pointer transition-colors active:scale-98"
              aria-label="Close modal"
            >
              <Icon name="close" />
            </button>
          </div>

          <!-- Form -->
          <div class="space-y-6">
            <!-- Repository Input -->
            <div>
              <label for="repository" class="text-foreground mb-2 block text-sm font-medium">
                Repository
              </label>
              <input
                id="repository"
                v-model="repository"
                type="text"
                placeholder="username/repo"
                class="border-line-secondary bg-background text-foreground placeholder:text-muted-foreground/60 focus:border-brand focus:ring-brand/20 w-full rounded-xl border px-4 py-3 text-sm focus:ring-2 focus:outline-none"
                :class="{
                  'border-red-500 focus:border-red-500 focus:ring-red-500/20':
                    repository && !isValidRepository(repository),
                }"
                @keydown.enter="handleSubmit"
              />
            </div>
          </div>

          <!-- Footer -->
          <div class="mt-8 flex justify-end gap-3">
            <button
              @click="closeModal"
              class="border-line-secondary text-foreground hover:bg-fill/40 cursor-pointer rounded-lg border px-6 py-2.5 text-sm font-medium transition-all duration-100 active:scale-98"
            >
              Cancel
            </button>
            <button
              @click="handleSubmit"
              :disabled="!canSubmit()"
              class="bg-brand hover:bg-brand/90 focus:bg-brand/90 disabled:bg-brand/50 inline-flex cursor-pointer items-center gap-2 rounded-lg px-6 py-2.5 text-sm font-medium text-white transition-all duration-100 active:scale-98 disabled:cursor-not-allowed"
            >
              <span v-if="isSubmitting">
                <Icon name="loading" />
              </span>
              <span>{{ isSubmitting ? 'Selecting...' : 'Select Repository' }}</span>
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>
