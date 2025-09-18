<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import Icon from '@/components/SvgIcon.vue'
import ShinyText from '@/components/ShinyText.vue'
import { useRouter } from 'vue-router'
import markdownit from 'markdown-it'
import Shiki from '@shikijs/markdown-it'

const md = markdownit({
  linkify: true,
  html: true,
  typographer: true,
})

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

const geminiResponse = ref('')
const renderedGeminiResponse = computed(() => {
  if (!geminiResponse.value) return ''
  // Convert escaped newlines to real newlines and render markdown
  const normalizedResponse = geminiResponse.value.replace(/\\n/g, '\n')
  return md.render(normalizedResponse)
})

const responseTime = ref<number | null>(null)

onMounted(async () => {
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

  // Initialize Shiki for syntax highlighting
  try {
    md.use(
      await Shiki({
        themes: {
          light: 'catppuccin-frappe',
          dark: 'catppuccin-mocha',
        },
      }),
    )
  } catch (error) {
    console.error('Failed to load Shiki:', error)
    // Keep the basic markdown rendering if Shiki fails
  }
})

// Streaming state
const isLoading = ref(false)
const isDone = ref(false)
const error = ref<string | null>(null)
let es: EventSource | null = null

// Activity feed (progressive steps)
type FeedItem = {
  id: string
  title: string
  tags?: string[]
  status: 'active' | 'done'
}

const feedItems = ref<FeedItem[]>([])
const currentQueries = ref<string[]>([])

const sources = ref<CitationSource[]>([])

function pushFeed(item: Omit<FeedItem, 'id' | 'status'> & { status?: 'active' | 'done' }) {
  const last = feedItems.value[feedItems.value.length - 1]
  if (last && last.status === 'active') last.status = 'done'
  feedItems.value.push({
    id: Math.random().toString(36).slice(2, 10),
    status: item.status ?? 'active',
    title: item.title,
    tags: item.tags,
  })
}

async function startSearchStream() {
  try {
    isLoading.value = true
    isDone.value = false
    error.value = null
    responseTime.value = null
    geminiResponse.value = ''
    feedItems.value = []
    sources.value = []

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

    es.addEventListener('search_queries', (ev) => {
      const payload = parse<{ queries: string[]; technology?: string; confidence?: number }>(
        ev as MessageEvent,
      )
      currentQueries.value = payload?.queries ?? []
      // Do not show tags for the generating queries step
      pushFeed({ title: 'Generating queries', tags: currentQueries.value.slice(0, 3) })
    })

    es.addEventListener('get_repository', (ev) => {
      const payload = parse<{ repo: string }>(ev as MessageEvent)
      if (payload?.repo) selectedRepo.value = payload.repo
      pushFeed({ title: 'Selecting repository', tags: payload?.repo ? [payload.repo] : undefined })
    })

    es.addEventListener('search_issues', (ev) => {
      const payload = parse<{ total_issues: number }>(ev as MessageEvent)
      const issueCount = payload?.total_issues ?? 0
      pushFeed({
        title: `Searching ${issueCount} issue${issueCount !== 1 ? 's' : ''}`,
      })
    })

    es.addEventListener('get_issues_comments', (ev) => {
      const payload = parse<{ total_comments: number }>(ev as MessageEvent)
      const commentCount = payload?.total_comments ?? 0
      pushFeed({
        title: `Reading ${commentCount} comment${commentCount !== 1 ? 's' : ''}`,
      })
    })

    es.addEventListener('generate_streaming_answer_start', () => {
      pushFeed({ title: 'Generating answer...' })
    })

    es.addEventListener('streaming_answer_chunk', (ev) => {
      const payload = parse<string>(ev as MessageEvent)
      if (payload) geminiResponse.value += payload
    })

    // Receive sources as they become available
    es.addEventListener('sources_update', (ev) => {
      const payload = parse<CitationSource[]>(ev as MessageEvent)
      console.log('sources_update', payload)
      if (payload && Array.isArray(payload)) {
        sources.value = payload
      }
    })

    es.addEventListener('streaming_answer_end', (ev) => {
      const last = feedItems.value[feedItems.value.length - 1]
      if (last) last.status = 'done'
      isLoading.value = false
      isDone.value = true
      const elapsed_time = parse<{ message?: string; elapsed_time_seconds: number }>(
        ev as MessageEvent,
      )
      if (elapsed_time?.elapsed_time_seconds) {
        responseTime.value = elapsed_time.elapsed_time_seconds
      }
      if (es) {
        es.close()
        es = null
      }
    })

    es.onerror = () => {
      error.value = 'Something went wrong while streaming the answer.'
      isLoading.value = false
      if (es) {
        es.close()
        es = null
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (e: any) {
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
    <main class="w-full px-4 py-10 md:px-16">
      <!-- Back button -->
      <button
        @click="goBack"
        class="text-muted-foreground hover:text-brand mb-2 flex cursor-pointer items-center gap-2 rounded-lg text-sm transition-all duration-200"
      >
        <Icon name="arrow-left" class="h-4 w-4" />
        <span>Back</span>
      </button>

      <div class="grid w-full grid-cols-1 gap-8 lg:grid-cols-4">
        <section class="w-[90%] lg:col-span-3">
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

          <!-- Answer -->
          <section id="answerSection" class="space-y-4">
            <header class="flex items-center justify-between">
              <div class="text-muted-foreground flex w-full items-baseline justify-between">
                <div class="flex items-center gap-2">
                  <Icon name="pinpoint-dark" :class="['h-4 w-4', !isDone ? 'pin-rotate' : '']" />
                  <span id="answer-label" class="text-foreground text-sm font-semibold"
                    >Answer</span
                  >
                </div>
                <div
                  v-if="responseTime"
                  class="text-muted-foreground flex items-center gap-1 text-xs"
                >
                  <Icon name="clock" class="h-3 w-3" />
                  <span>{{ responseTime }}s</span>
                </div>
              </div>
            </header>

            <div class="border-line-secondary text-foreground border-t pt-4 leading-7">
              <div v-if="error" class="mb-3 text-sm text-red-500">{{ error }}</div>

              <!-- Event feed -->
              <template v-else>
                <div class="event-feed-container">
                  <transition-group
                    v-if="!isDone"
                    name="fade-slide"
                    tag="ol"
                    class="feed-timeline relative space-y-4"
                  >
                    <li
                      v-for="item in feedItems"
                      :key="item.id"
                      class="feed-item flex items-start gap-3"
                    >
                      <span
                        class="relative z-10 mt-0.5 inline-flex h-5 w-5 items-center justify-center"
                      >
                        <template v-if="item.status === 'done'">
                          <!-- Static grey dot for completed step -->
                          <span
                            class="pulse-dot is-static text-muted-foreground"
                            aria-hidden="true"
                          ></span>
                        </template>
                        <template v-else>
                          <!-- Animated brand dot for active step -->
                          <span
                            class="pulse-dot force-animate text-brand"
                            role="status"
                            aria-label="loading"
                          ></span>
                        </template>
                      </span>

                      <div class="flex-1">
                        <div class="text-sm">
                          <ShinyText
                            :text="item.title"
                            :disabled="item.status === 'done'"
                            :speed="1"
                            :class="[
                              'font-medium',
                              item.status === 'done' ? 'text-muted-foreground' : '',
                            ]"
                          />
                        </div>
                        <div v-if="item.tags?.length" class="mt-2 flex flex-wrap gap-2">
                          <span
                            v-for="t in item.tags"
                            :key="t"
                            class="border-line-secondary bg-fill rounded-full border px-2 py-0.5 text-xs"
                            >{{ t }}</span
                          >
                        </div>
                      </div>
                    </li>
                  </transition-group>

                  <!-- Answer content -->
                  <div
                    v-if="geminiResponse"
                    class="markdown-content space-y-4"
                    v-html="renderedGeminiResponse"
                  ></div>
                </div>
              </template>
            </div>

            <div v-if="isDone" class="border-line-secondary border-t pt-3">
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
        <aside class="w-full lg:col-span-1">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-xl font-semibold tracking-tight">Sources</h2>
            <div class="flex flex-wrap items-center justify-between gap-3 md:gap-4">
              <a
                :href="`https://github.com/${selectedRepo}`"
                target="_blank"
                rel="noopener noreferrer"
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

          <!-- Source items -->
          <div v-if="sources.length === 0" class="text-muted-foreground text-sm">
            Sources will appear here as the answer streams...
          </div>
          <ul v-else class="space-y-3">
            <li v-for="(s, idx) in sources" :key="s.id + '-' + idx">
              <a
                :href="s.url"
                target="_blank"
                rel="noopener noreferrer"
                class="border-line-secondary bg-fill hover:bg-brand/10 block rounded-xl border transition"
              >
                <div class="p-4">
                  <div class="flex items-start gap-4">
                    <div class="min-w-0 flex-1">
                      <div class="flex items-center justify-between gap-2">
                        <span class="text-foreground font-medium">{{ s.title }}</span>
                        <span class="text-muted-foreground text-xs"
                          >Issue #{{ s.issue_number }}</span
                        >
                      </div>
                      <div
                        v-if="s.preview"
                        class="text-muted-foreground mt-1 line-clamp-2 text-[13px]"
                      >
                        {{ s.preview }}
                      </div>
                      <div class="text-muted-foreground mt-2 flex items-center gap-2 text-xs">
                        <Icon name="github" class="h-3 w-3" />
                        <span>{{ selectedRepo }}</span>
                        <span
                          class="border-line-secondary text-muted-foreground ml-auto rounded px-1.5 py-0.5 text-[10px]"
                          >[{{ idx + 1 }}]</span
                        >
                      </div>
                    </div>
                  </div>
                </div>
              </a>
            </li>
          </ul>
        </aside>
      </div>
    </main>
  </div>
</template>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 200ms ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.pulse-dot {
  position: relative;
  display: inline-block;
  width: var(--pulse-size, 8px);
  height: var(--pulse-size, 8px);
}

.pulse-dot::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  width: 200%;
  height: 200%;
  border-radius: 9999px;
  background-color: currentColor;
  opacity: 0.22;
  transform: translate(-50%, -50%);
  animation: pulse-ring var(--pulse-duration, 1.25s) cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
}

.pulse-dot::after {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  border-radius: 9999px;
  background-color: currentColor;
  box-shadow: 0 0 6px color-mix(in oklab, currentColor 35%, transparent);
  animation: pulse-dot var(--pulse-duration, 1.25s) cubic-bezier(0.455, 0.03, 0.515, 0.955) -0.4s
    infinite;
}

@keyframes pulse-ring {
  0% {
    transform: translate(-50%, -50%) scale(0.33);
    opacity: 0.22;
  }
  80%,
  100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0;
  }
}

@keyframes pulse-dot {
  0% {
    transform: scale(0.8);
  }
  50% {
    transform: scale(1);
  }
  100% {
    transform: scale(0.8);
  }
}

.pulse-dot.is-static::before,
.pulse-dot.is-static::after {
  animation: none;
}

@media (prefers-reduced-motion: reduce) {
  .pulse-dot:not(.force-animate)::before,
  .pulse-dot:not(.force-animate)::after {
    animation: none;
  }
}

/* Timeline connectors between dots */
.feed-timeline {
  --feed-gap: 16px;
  --connector-x: 10px;
  --connector-gap: 6px;
}

.feed-item {
  position: relative;
}

.feed-item::before,
.feed-item::after {
  content: '';
  position: absolute;
  left: var(--connector-x);
  width: 2px;
  background: var(--color-line-secondary);
  z-index: 0;
}

.feed-item::before {
  top: calc(-0.5 * var(--feed-gap));
  bottom: calc(12px + var(--connector-gap));
}

.feed-item::after {
  margin-top: 1px;
  top: calc(12px + var(--connector-gap));
  bottom: calc(-0.5 * var(--feed-gap));
}

/* Hide extraneous segments at the ends */
.feed-timeline > .feed-item:first-child::before {
  display: none;
}
.feed-timeline > .feed-item:last-child::after {
  display: none;
}

/* For completed steps, hide the pulse ring entirely */
.pulse-dot.is-static::before {
  display: none;
}
.pulse-dot.is-static::after {
  animation: none;
}

/* Local icon spin for Answer header */
@keyframes pin-rotate {
  to {
    transform: rotate(360deg);
  }
}
.pin-rotate {
  animation: pin-rotate 1s linear infinite;
}

/* Event feed fade-in animation */
.event-feed-container {
  animation: feed-fade-in 0.4s ease-out;
}

@keyframes feed-fade-in {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* More ChatGPT-like styling */
:deep(.markdown-content pre) {
  background-color: #f8f8f8;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
  padding: 12px 16px;
  margin: 12px 0;
  overflow-x: auto;
  font-family:
    'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.45;
  color: #24292f;
}

:global(.dark) :deep(.markdown-content pre) {
  background-color: #0d1117;
  border-color: #30363d;
  color: #e6edf3;
}

:deep(.markdown-content code) {
  background-color: var(--color-fill);
  border-radius: 4px;
  padding: 2px 6px;
  font-family:
    'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
  font-size: 0.875rem;
  color: var(--color-foreground);
  border: 1px solid var(--color-line-secondary);
}

:deep(.markdown-content pre code) {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
  border: none;
  font-size: 13px;
}

:global(.dark) :deep(.markdown-content code) {
  background-color: var(--color-line-secondary);
  border-color: var(--color-line-secondary);
}

:global(.dark) :deep(.markdown-content pre code) {
  background-color: transparent;
  border: none;
}

/* Markdown heading styles - only within .markdown-content */
:deep(.markdown-content h1) {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.2;
  color: hsl(var(--foreground));
}

:deep(.markdown-content h2) {
  font-size: 1.5rem;
  font-weight: 600;
  line-height: 1.3;

  color: hsl(var(--foreground));
}

:deep(.markdown-content h3) {
  font-size: 1.25rem;
  font-weight: 600;
  line-height: 1.4;

  color: hsl(var(--foreground));
}

:deep(.markdown-content h4) {
  font-size: 1.125rem;
  font-weight: 600;
  line-height: 1.4;

  color: hsl(var(--foreground));
}

:deep(.markdown-content h5) {
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.5;

  color: hsl(var(--foreground));
}

:deep(.markdown-content h6) {
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1.5;

  color: hsl(var(--muted-foreground));
}

/* Paragraph and list spacing - only apply to markdown content */
:deep(.markdown-content p) {
  line-height: 1.6;
}

:deep(.markdown-content ul) {
  padding-left: 1.5rem;

  list-style-type: disc;
}

:deep(.markdown-content ol) {
  padding-left: 1.5rem;

  list-style-type: decimal;
}

:deep(.markdown-content ul ul) {
  list-style-type: circle;
}

:deep(.markdown-content ul ul ul) {
  list-style-type: square;
}

:deep(.markdown-content ol ol) {
  list-style-type: lower-alpha;
}

:deep(.markdown-content ol ol ol) {
  list-style-type: lower-roman;
}

:deep(.markdown-content li) {
  line-height: 1.6;
  margin: 0.75rem 0;
  display: list-item;
}

:deep(.markdown-content blockquote) {
  border-left: 4px solid hsl(var(--border));
  padding-left: 1rem;
  color: hsl(var(--muted-foreground));
  font-style: italic;
}

:deep(.markdown-content strong) {
  font-weight: 600;
  color: hsl(var(--foreground));
}
</style>
