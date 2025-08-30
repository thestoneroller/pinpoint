<script setup lang="ts">
import Navbar from '@/components/NavBar.vue'
import Icon from '@/components/SvgIcon.vue'
</script>

<template>
  <div class="flex h-dvh w-full flex-col items-center">
    <Navbar />
    <!--  Hero Heading & Subheading -->
    <div class="mt-30 flex flex-col items-center justify-center gap-4 md:mt-20">
      <h1
        class="font-alpha text-foreground xs:text-3xl w-96 text-center text-2xl text-pretty sm:w-[28rem] sm:text-[2rem] md:w-[40rem] md:text-[2.5rem]"
      >
        Find solutions to bugs in external libraries from GitHub issues.
      </h1>
      <p
        class="text-muted-foreground hidden w-64 text-center text-xs text-pretty sm:block sm:w-[30rem] sm:text-base md:w-[43rem]"
      >
        The bug you’ve been stuck on all day isn’t unique. Discover the fix in GitHub issues.
      </p>
    </div>
    <!-- Prompt -->
    <div
      class="border-line-primary/50 bg-background shadow-fill/80 relative mt-10 flex w-[90vw] flex-col gap-2 rounded-sm border p-4 shadow-sm md:mt-12 md:w-[42rem] lg:w-[48rem]"
    >
      <textarea
        id="hs-textarea-ex-1"
        class="placeholder:text-muted-foreground/60 text-foreground block h-20 max-h-24 resize-none pb-8 text-sm placeholder:text-sm focus:outline-none disabled:pointer-events-none disabled:opacity-50 sm:pb-12 sm:text-base sm:placeholder:text-base"
        placeholder="Explain the error that’s been driving you crazy…"
        data-hs-textarea-auto-height=""
      ></textarea>

      <!-- Toolbar -->
      <div class="inset-x-px bottom-px">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <!-- Button Group -->
          <div class="flex items-center">
            <button
              type="button"
              class="active:bg-fill/70 hover:bg-fill/70 border-line-primary/60 flex shrink-0 cursor-pointer items-center justify-baseline gap-px rounded-sm border px-3 py-2 transition-transform focus:z-10 focus:outline-hidden active:translate-y-px active:scale-98"
            >
              <Icon name="github" class="fill-foreground h-4 w-4" />
              <Icon name="slash" class="fill-foreground h-4 w-4" />
              <p class="text-foreground text-xs sm:text-sm">Add Repo</p>
            </button>
          </div>

          <!-- Submit Button -->
          <div class="flex items-center gap-x-1">
            <button
              type="button"
              class="bg-brand hover:bg-brand/90 focus:bg-brand/90 inline-flex size-8 shrink-0 cursor-pointer items-center justify-center rounded-sm text-white transition-transform focus:z-10 focus:outline-hidden active:translate-y-px active:scale-98"
            >
              <Icon name="arrow-right" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
