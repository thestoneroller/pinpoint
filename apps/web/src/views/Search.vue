<script setup lang="ts">
import { computed, ref } from 'vue'
import Icon from '@/components/SvgIcon.vue'

// const props = defineProps<{ keyword: string }>()

const test = ref(
  'How can I use the same image for multiple backgrounds with a length that would be longer than 80 characters to demonstrate the shrinking of the font size? Wrap your table in a scroll container and make the header sticky so it stays pinned while rows scroll underneath. Give header cells a solid background and a higher stacking order to avoid bleed-through and ensure smooth separation.',
)
const maxFont = 32 // px
const minFont = 16 // px
const lengthForMin = 80 // after 80 chars, stop shrinking

const fontSize = computed(() => {
  const len = test.value.length
  return Math.max(minFont, maxFont - (len / lengthForMin) * (maxFont - minFont))
})

const isExpanded = ref(false)
const shouldShowToggle = computed(() => test.value.length > 186)
</script>

<template>
  <div class="bg-background text-foreground min-h-dvh antialiased">
    <main class="w-full px-4 py-10 md:px-20">
      <div class="grid w-full grid-cols-1 gap-24 lg:grid-cols-12">
        <!-- Main content -->
        <section class="w-full lg:col-span-8">
          <!-- Meta row -->
          <div class="flex flex-wrap items-center justify-between gap-3 md:gap-4">
            <!-- Repo chip -->
            <a
              href="#"
              class="border-line-secondary bg-fill text-foreground hover:border-brand/30 hover:bg-brand/5 inline-flex items-center gap-1 rounded-lg border px-2 py-1 text-sm transition-transform active:scale-98"
            >
              <Icon
                name="github"
                class="fill-foreground focus:fill-brand/90 h-4 w-4 cursor-pointer transition-transform"
              />
              <span class="font-medium">acme-ui/shadcn-kit</span>
            </a>
          </div>
          <!-- Question -->
          <div class="mt-4 mb-10 w-full space-y-3">
            <div class="group relative">
              <p
                class="text-foreground w-full tracking-tight break-words transition-all duration-300"
                :class="{
                  'line-clamp-3': !isExpanded && shouldShowToggle,
                  'overflow-hidden': !isExpanded && shouldShowToggle,
                }"
                :style="{
                  fontSize: fontSize + 'px',
                  maskImage:
                    !isExpanded && shouldShowToggle
                      ? 'linear-gradient(to bottom, black 80%, transparent 100%)'
                      : 'none',
                  WebkitMaskImage:
                    !isExpanded && shouldShowToggle
                      ? 'linear-gradient(to bottom, black 80%, transparent 100%)'
                      : 'none',
                }"
              >
                {{ test }}
              </p>

              <!-- Show more/less button -->
              <div class="mt-2 flex items-center justify-between">
                <button
                  v-if="shouldShowToggle"
                  @click="isExpanded = !isExpanded"
                  class="text-muted-foreground hover:text-foreground hover:bg-fill hover:border-line-secondary -ml-2 flex cursor-pointer items-center gap-1 rounded-lg border border-transparent px-2 py-1 text-sm transition-all duration-200"
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
                  class="hover:border-line-secondary hover:bg-fill inline-flex cursor-pointer items-center gap-1 rounded-lg border border-transparent px-2 py-1 opacity-0 transition-all duration-150 group-hover:opacity-100"
                >
                  <Icon name="copy" class="fill-muted-foreground" />
                  <p class="text-xs">Copy</p>
                </button>
              </div>
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
              <div class="flex gap-2">
                <Icon name="info" />
                <span class="text-muted-foreground text-xs">82% Confidence</span>
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
          </div>

          <!-- Source item -->
          <a
            id="src-1"
            href="#"
            class="border-line-secondary bg-background hover:bg-fill/30 block rounded-xl border transition"
          >
            <div class="p-4">
              <div class="flex items-start gap-3">
                <img
                  src="https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?q=80&w=96&auto=format&fit=crop"
                  class="h-9 w-9 rounded-full object-cover"
                  alt="avatar"
                />
                <div class="min-w-0 flex-1">
                  <div class="flex items-center gap-2">
                    <span class="text-foreground font-medium">WASasquatch</span>
                    <span class="text-muted-foreground/60">·</span>
                    <span class="text-muted-foreground text-xs">Issue · #1289</span>
                  </div>
                  <div class="text-muted-foreground mt-1 line-clamp-2 text-[13px]">
                    There is no scale for the upscaling node for model based upscaling. This means
                    most good models will be forcing...
                  </div>
                  <div class="text-muted-foreground mt-2 flex items-center gap-2 text-xs">
                    <svg class="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 24 24">
                      <path
                        d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
                      />
                    </svg>
                    <span>acme-ui/shadcn-kit</span>
                    <span>•</span>
                    <span>3 days ago</span>
                  </div>
                </div>
              </div>
            </div>
          </a>

          <a
            id="src-2"
            href="#"
            class="border-line-secondary bg-background hover:bg-fill/30 block rounded-xl border transition"
          >
            <div class="p-4">
              <div class="flex items-start gap-3">
                <img
                  src="https://images.unsplash.com/photo-1519340241574-2cec6aef0c01?q=80&w=96&auto=format&fit=crop"
                  class="h-9 w-9 rounded-full object-cover"
                  alt="avatar"
                />
                <div class="min-w-0 flex-1">
                  <div class="flex items-center gap-2">
                    <span class="text-foreground font-medium">devin</span>
                    <span class="text-muted-foreground/60">·</span>
                    <span class="text-muted-foreground text-xs">Comment</span>
                  </div>
                  <div class="text-muted-foreground mt-1 line-clamp-2 text-[13px]">
                    Use thead with sticky top-0 and set a background to avoid transparency when
                    scrolling the rows...
                  </div>
                  <div class="text-muted-foreground mt-2 flex items-center gap-2 text-xs">
                    <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                      />
                    </svg>
                    <span>View discussion</span>
                    <span>•</span>
                    <span>5 days ago</span>
                  </div>
                </div>
              </div>
            </div>
          </a>

          <a
            id="src-3"
            href="#"
            class="border-line-secondary bg-background hover:bg-fill/30 block rounded-xl border transition"
          >
            <div class="p-4">
              <div class="flex items-start gap-3">
                <img
                  src="https://images.unsplash.com/photo-1527980965255-d3b416303d12?q=80&w=96&auto=format&fit=crop"
                  class="h-9 w-9 rounded-full object-cover"
                  alt="avatar"
                />
                <div class="min-w-0 flex-1">
                  <div class="flex items-center gap-2">
                    <span class="text-foreground font-medium">sara</span>
                    <span class="text-muted-foreground/60">·</span>
                    <span class="text-muted-foreground text-xs">Issue · #1192</span>
                  </div>
                  <div class="text-muted-foreground mt-1 line-clamp-2 text-[13px]">
                    When using shadcn table + virtualization, keep header outside the scroll
                    container...
                  </div>
                  <div class="text-muted-foreground mt-2 flex items-center gap-2 text-xs">
                    <svg class="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 24 24">
                      <path
                        d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
                      />
                    </svg>
                    <span>acme-ui/shadcn-kit</span>
                    <span>•</span>
                    <span>1 week ago</span>
                  </div>
                </div>
              </div>
            </div>
          </a>

          <a
            id="src-4"
            href="#"
            class="border-line-secondary bg-background hover:bg-fill/30 block rounded-xl border transition"
          >
            <div class="p-4">
              <div class="flex items-start gap-3">
                <img
                  src="https://images.unsplash.com/photo-1531123897727-8f129e1688ce?q=80&w=96&auto=format&fit=crop"
                  class="h-9 w-9 rounded-full object-cover"
                  alt="avatar"
                />
                <div class="min-w-0 flex-1">
                  <div class="flex items-center gap-2">
                    <span class="text-foreground font-medium">jake</span>
                    <span class="text-muted-foreground/60">·</span>
                    <span class="text-muted-foreground text-xs">Comment</span>
                  </div>
                  <div class="text-muted-foreground mt-1 line-clamp-2 text-[13px]">
                    Add z-10 and a subtle bottom shadow to the sticky header to separate it from
                    scrolling content.
                  </div>
                  <div class="text-muted-foreground mt-2 flex items-center gap-2 text-xs">
                    <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                      />
                    </svg>
                    <span>View discussion</span>
                    <span>•</span>
                    <span>10 days ago</span>
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
