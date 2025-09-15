<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import Icon from '@/components/SvgIcon.vue'
import { useRouter } from 'vue-router'

// Get data from router state (hidden from URL)
const queryText = ref('')
const selectedRepo = ref('')

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
})

const maxFont = 32 // px
const minFont = 20 // px
const lengthForMin = 140 // after 80 chars, stop shrinking

const fontSize = computed(() => {
  const len = queryText.value.length
  return Math.max(minFont, maxFont - (len / lengthForMin) * (maxFont - minFont))
})

const isExpanded = ref(false)
const shouldShowToggle = computed(() => queryText.value.length > 186)
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

          <!-- Answer (flattened, Perplexity-like) -->
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
              <p class="mb-4">
                Wrap your table in a scroll container and make the header sticky so it stays pinned
                while rows scroll underneath. Give header cells a solid background and a higher
                stacking order to avoid bleed-through and ensure smooth separation
                <a
                  href="#src-2"
                  class="text-muted-foreground hover:text-foreground align-baseline text-xs underline"
                  >[2]</a
                >.
              </p>

              <div class="text-muted-foreground mb-3 flex items-center gap-2 text-[13px]">
                <svg
                  class="text-muted-foreground h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 6h16M4 10h16M4 14h16M4 18h16"
                  />
                </svg>
                <span class="font-medium">Approach</span>
              </div>
              <ul class="text-foreground ml-5 list-disc space-y-1 text-[15px]">
                <li>
                  Wrap the table with a div that has a fixed height and
                  <code class="bg-fill rounded px-1 py-0.5 text-[13px]">overflow-y-auto</code>.
                </li>
                <li>
                  Apply <code class="bg-fill rounded px-1 py-0.5 text-[13px]">sticky top-0</code> to
                  <code class="bg-fill rounded px-1 py-0.5 text-[13px]">&lt;thead&gt;</code> or
                  header cells and set a solid background
                  <a
                    href="#src-2"
                    class="text-muted-foreground hover:text-foreground align-baseline text-xs underline"
                    >[2]</a
                  >.
                </li>
                <li>
                  Use a subtle bottom shadow or divider for depth and set
                  <code class="bg-fill rounded px-1 py-0.5 text-[13px]">z-10</code> on header cells
                  <a
                    href="#src-4"
                    class="text-muted-foreground hover:text-foreground align-baseline text-xs underline"
                    >[4]</a
                  >.
                </li>
                <li>
                  If you're virtualizing rows, keep the header outside the scrollable region and
                  align columns via grid or measured widths
                  <a
                    href="#src-3"
                    class="text-muted-foreground hover:text-foreground align-baseline text-xs underline"
                    >[3]</a
                  >.
                </li>
              </ul>

              <p class="mt-4">
                For virtualization or dynamic content, keep the header separate from the scroll
                container and sync column widths with CSS grid or measured sizes
                <a
                  href="#src-3"
                  class="text-muted-foreground hover:text-foreground align-baseline text-xs underline"
                  >[3]</a
                >.
              </p>
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
