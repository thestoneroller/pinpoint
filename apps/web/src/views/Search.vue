<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import Icon from '@/components/SvgIcon.vue'
import { useRouter } from 'vue-router'

const maxFont = 32 // px
const minFont = 20 // px
const lengthForMin = 140 // after 140 chars, stop shrinking

const fontSize = computed(() => {
  const len = queryText.value.length
  return Math.max(minFont, maxFont - (len / lengthForMin) * (maxFont - minFont))
})

const queryText = ref('')
const selectedRepo = ref('')

const isExpanded = ref(false)
const shouldShowToggle = computed(() => queryText.value.length > 186)

const router = useRouter()

const goBack = () => {
  router.go(-1)
}

onMounted(() => {
  // Get data passed through router state
  const state = history.state
  if (state?.query) {
    queryText.value = state.query
  }
  if (state?.repo) {
    selectedRepo.value = state.repo
  }

  // Start streaming if we have a valid query
  if (queryText.value && queryText.value.length >= 20) {
    startSearchStream()
  }
})

// Streaming state
const geminiResponse = ref('')
const isLoading = ref(false)
const isDone = ref(false)
const error = ref<string | null>(null)
let es: EventSource | null = null

// Animated timeline state
type StepStatus = 'pending' | 'active' | 'done' | 'error'
const steps = [
  { key: 'search_queries', label: 'Generating queries' },
  { key: 'get_repository', label: 'Selecting repository' },
  { key: 'search_issues', label: 'Searching issues' },
  { key: 'get_issues_comments', label: 'Fetching comments' },
  { key: 'generate_streaming_answer', label: 'Generating answer' },
] as const

const stepStatus = ref<Record<string, StepStatus>>({})
const metrics = ref({ totalIssues: 0, totalComments: 0, elapsed: 0 })

function resetSteps() {
  stepStatus.value = Object.fromEntries(steps.map((s) => [s.key, 'pending'])) as Record<
    string,
    StepStatus
  >
  metrics.value = { totalIssues: 0, totalComments: 0, elapsed: 0 }
}

async function startSearchStream() {
  try {
    isLoading.value = true
    isDone.value = false
    error.value = null
    geminiResponse.value = ''
    resetSteps()

    // Close any previous connection
    if (es) {
      es.close()
      es = null
    }

    const params = new URLSearchParams()
    params.set('query', queryText.value)
    if (selectedRepo.value) params.set('repo', selectedRepo.value)

    es = new EventSource(`/api/v1/search?${params.toString()}`)

    const parse = <T,>(e: MessageEvent): T | null => {
      try {
        return JSON.parse(e.data) as T
      } catch {
        return null
      }
    }

    es.addEventListener('search_queries', () => {
      stepStatus.value['search_queries'] = 'active'
    })

    es.addEventListener('get_repository', (ev) => {
      stepStatus.value['search_queries'] = 'done'
      stepStatus.value['get_repository'] = 'active'
      const payload = parse<{ repo: string }>(ev as MessageEvent)
      if (payload?.repo) selectedRepo.value = payload.repo
    })

    es.addEventListener('search_issues', (ev) => {
      stepStatus.value['get_repository'] = 'done'
      stepStatus.value['search_issues'] = 'active'
      const payload = parse<{ total_issues: number }>(ev as MessageEvent)
      if (payload?.total_issues != null)
        metrics.value.totalIssues = Number(payload.total_issues) || 0
    })

    es.addEventListener('get_issues_comments', (ev) => {
      stepStatus.value['search_issues'] = 'done'
      stepStatus.value['get_issues_comments'] = 'active'
      const payload = parse<{ total_comments: number }>(ev as MessageEvent)
      if (payload?.total_comments != null)
        metrics.value.totalComments = Number(payload.total_comments) || 0
    })

    es.addEventListener('generate_streaming_answer_start', () => {
      stepStatus.value['get_issues_comments'] = 'done'
      stepStatus.value['generate_streaming_answer'] = 'active'
    })

    es.addEventListener('streaming_answer_chunk', (ev) => {
      const payload = parse<{ text: string }>(ev as MessageEvent)
      if (payload?.text) geminiResponse.value += payload.text
    })

    es.addEventListener('streaming_answer_end', (ev) => {
      stepStatus.value['generate_streaming_answer'] = 'done'
      isLoading.value = false
      isDone.value = true
      const payload = parse<{ message?: string; elapsed_time_seconds: number }>(ev as MessageEvent)
      if (payload?.elapsed_time_seconds != null)
        metrics.value.elapsed = Number(payload.elapsed_time_seconds) || 0
      if (es) {
        es.close()
        es = null
      }
    })

    es.onerror = () => {
      const activeKey = Object.keys(stepStatus.value).find((k) => stepStatus.value[k] === 'active')
      if (activeKey) stepStatus.value[activeKey] = 'error'
      error.value = 'Something went wrong while streaming the answer.'
      isLoading.value = false
      if (es) {
        es.close()
        es = null
      }
    }
  } catch (e: any) {
    const activeKey = Object.keys(stepStatus.value).find((k) => stepStatus.value[k] === 'active')
    if (activeKey) stepStatus.value[activeKey] = 'error'
    error.value = e?.message || 'Something went wrong while starting the stream.'
    isLoading.value = false
  }
}

onBeforeUnmount(() => {
  if (es) es.close()
})
</script>

<template>
  <div class="bg-background text-foreground min-h-dvh antialiased">
    <main class="w-full px-4 py-10 md:px-20">
      <!-- Back button -->
      <button
        @click="goBack"
        class="text-muted-foreground hover:text-foreground mb-2 flex cursor-pointer items-center gap-2 rounded-lg text-sm transition-all duration-200"
      >
        <Icon name="arrow-left" class="h-4 w-4" />
        <span>Back</span>
      </button>

      <div class="grid w-full grid-cols-1 gap-24 lg:grid-cols-12">
        <!-- Main content -->
        <section class="w-full lg:col-span-8">
          <!-- Activity timeline -->
          <div class="border-line-secondary bg-background mb-4 rounded-xl border p-4">
            <div class="mb-3 flex items-center justify-between">
              <span class="text-sm font-medium">Activity</span>
              <span class="text-muted-foreground text-xs" v-if="isLoading">Working…</span>
            </div>
            <ol class="space-y-3">
              <li v-for="s in steps" :key="s.key" class="flex items-start gap-3">
                <span class="mt-0.5 inline-flex h-5 w-5 items-center justify-center">
                  <template v-if="stepStatus[s.key] === 'done'">
                    <svg
                      class="h-4 w-4 text-green-500"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <path d="M20 6L9 17l-5-5" />
                    </svg>
                  </template>
                  <template v-else-if="stepStatus[s.key] === 'active'">
                    <Icon name="loading" class="h-4 w-4 animate-spin" />
                  </template>
                  <template v-else-if="stepStatus[s.key] === 'error'">
                    <svg
                      class="h-4 w-4 text-red-500"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <path d="M18 6L6 18M6 6l12 12" />
                    </svg>
                  </template>
                  <template v-else>
                    <span class="bg-muted-foreground/40 h-2 w-2 rounded-full"></span>
                  </template>
                </span>
                <div class="flex-1 text-sm">
                  <span
                    :class="{
                      'text-foreground': stepStatus[s.key] !== 'pending',
                      'text-muted-foreground': stepStatus[s.key] === 'pending',
                    }"
                    >{{ s.label }}</span
                  >
                  <span
                    v-if="s.key === 'search_issues' && metrics.totalIssues"
                    class="text-muted-foreground ml-2 text-xs"
                    >({{ metrics.totalIssues }} issues)</span
                  >
                  <span
                    v-if="s.key === 'get_issues_comments' && metrics.totalComments"
                    class="text-muted-foreground ml-2 text-xs"
                    >({{ metrics.totalComments }} comments)</span
                  >
                  <span
                    v-if="s.key === 'generate_streaming_answer' && isDone && metrics.elapsed"
                    class="text-muted-foreground ml-2 text-xs"
                    >({{ metrics.elapsed }}s)</span
                  >
                </div>
              </li>
            </ol>
          </div>
          <!-- Query -->
          <div class="mt-4 mb-6 w-full space-y-3">
            <div class="group relative" :class="{ 'pb-6': shouldShowToggle }">
              <p
                class="text-foreground mb-2 w-full tracking-tight break-words transition-all duration-300"
                :class="{
                  'line-clamp-2': !isExpanded && shouldShowToggle,
                  'overflow-hidden': !isExpanded && shouldShowToggle,
                }"
                :style="{
                  fontSize: fontSize + 'px',
                  maskImage:
                    !isExpanded && shouldShowToggle
                      ? 'linear-gradient(to bottom, black 60%, transparent 100%)'
                      : 'none',
                  WebkitMaskImage:
                    !isExpanded && shouldShowToggle
                      ? 'linear-gradient(to bottom, black 60%, transparent 100%)'
                      : 'none',
                }"
              >
                {{ queryText }}
              </p>

              <button
                v-if="shouldShowToggle"
                @click="isExpanded = !isExpanded"
                class="text-muted-foreground hover:text-foreground hover:bg-fill hover:border-line-secondary absolute bottom-0 left-0 -ml-2 flex cursor-pointer items-center gap-1 rounded-lg border border-transparent px-2 py-1 text-xs transition-all duration-200"
              >
                <span>{{ isExpanded ? 'Show less' : 'Show more' }}</span>
                <svg
                  class="h-4 w-4 transition-transform duration-200"
                  :class="{ 'rotate-180': isExpanded }"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>
              <button
                id="copyQuery"
                class="border-line-secondary bg-fill absolute right-0 bottom-0 flex shrink-0 cursor-pointer items-center gap-1 rounded-lg border px-2 py-1 opacity-0 transition-all duration-150 group-hover:opacity-100"
                :class="{ 'mb-2': !shouldShowToggle }"
              >
                <Icon name="copy" class="fill-muted-foreground" />
                <p class="text-xs">Copy</p>
              </button>
            </div>
          </div>

          <!-- Answer (dynamic) -->
          <section id="answerSection" class="space-y-4">
            <header class="flex items-center justify-between">
              <div class="text-muted-foreground flex items-center justify-between">
                <div class="flex items-center gap-1">
                  <Icon name="pinpoint-dark" class="h-4 w-4" />
                  <span id="answer-label" class="text-foreground text-sm font-semibold"
                    >Answer</span
                  >
                </div>
              </div>
            </header>

            <div class="border-line-secondary text-foreground border-t pt-4 leading-7">
              <div v-if="error" class="mb-3 text-sm text-red-500">{{ error }}</div>
              <div v-else class="whitespace-pre-wrap">{{ geminiResponse }}</div>
            </div>

            <!-- Moved Copy to end -->
            <div class="border-line-secondary border-t pt-3">
              <div class="flex items-center justify-end">
                <button
                  id="copyAnswer"
                  class="hover:border-line-secondary hover:bg-fill inline-flex cursor-pointer items-center gap-1 rounded-lg border border-transparent px-2 py-1 transition-all duration-150"
                >
                  <Icon name="copy" class="fill-muted-foreground" />
                  <p class="text-xs">Copy</p>
                </button>
              </div>
            </div>
          </section>
        </section>

        <!-- Sidebar: Sources -->
        <aside class="space-y-4 lg:sticky lg:top-8 lg:col-span-4">
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold tracking-tight">Sources</h2>
            <div class="flex flex-wrap items-center justify-between gap-3 md:gap-4">
              <a
                href="#"
                class="border-line-secondary bg-fill text-foreground hover:border-brand/30 hover:bg-brand/5 inline-flex items-center gap-1 rounded-lg border px-2 py-1 text-sm transition-transform active:scale-98"
              >
                <Icon
                  name="github"
                  class="fill-foreground focus:fill-brand/90 h-4 w-4 cursor-pointer transition-transform"
                />
                <span class="font-medium">{{ selectedRepo }}</span>
              </a>
            </div>
          </div>

          <!-- Source item -->
          <a
            id="src-1"
            href="#"
            class="border-line-secondary bg-background hover:bg-fill block rounded-xl border transition"
          >
            <div class="p-4">
              <div class="flex items-start gap-4">
                <div class="min-w-0 flex-1">
                  <div class="flex items-center justify-between gap-2">
                    <span class="text-foreground font-medium">WASasquatch</span>

                    <span class="text-muted-foreground text-xs">Issue #1289</span>
                  </div>
                  <div class="text-muted-foreground mt-1 line-clamp-2 text-[13px]">
                    There is no scale for the upscaling node for model based upscaling. This means
                    most good models will be forcing...
                  </div>
                  <div class="text-muted-foreground mt-2 flex items-center gap-2 text-xs">
                    <Icon name="github" class="h-3 w-3" />
                    <span>shadcn-ui/ui</span>
                  </div>
                </div>
              </div>
            </div>
          </a>
        </aside>
      </div>
    </main>
  </div>
</template>
