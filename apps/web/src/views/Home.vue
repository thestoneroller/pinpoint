<script setup lang="ts">
import Navbar from '@/components/NavBar.vue'
import Icon from '@/components/SvgIcon.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const navigateToSearch = () => {
  router.push('/search/example')
}
</script>

<template>
  <Navbar />

  <!-- Background Gradient -->
  <div class="absolute inset-0 -z-20 h-dvh w-full overflow-hidden opacity-90">
    <div class="absolute inset-0 mt-0 h-full">
      <div
        class="absolute left-1/2 aspect-square h-[105%] w-[125%] -translate-x-1/2 overflow-hidden sm:-bottom-40 sm:h-full md:w-[100%] lg:w-[100%] xl:w-[100%] 2xl:mx-auto"
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
    class="absolute inset-0 -z-10 opacity-5"
    style="
      background-image: url(/background/grain.png);
      background-size: 100px 100px;
      background-repeat: repeat;
      background-position: left top;
    "
  ></div>

  <!--  Hero Heading & Subheading -->
  <div class="mt-30 flex flex-col items-center justify-center gap-4 md:mt-28">
    <h1
      class="xs:text-3xl text-foreground mx-auto line-clamp-1 flex w-fit gap-3 text-center text-2xl tracking-tighter text-pretty sm:w-[28rem] sm:text-[2rem] md:min-w-fit md:text-[3rem]"
    >
      Find solutions from GitHub.
    </h1>
    <p
      class="text-foreground/80 line-clamp-1 hidden min-w-fit text-center text-xs sm:block sm:text-base"
    >
      Search across Github issues and discover how others fixed the same problems.
    </p>
  </div>
  <!-- Prompt -->
  <div
    class="border-line-secondary bg-background relative mt-10 flex w-[90vw] flex-col gap-2 rounded-2xl border p-4 shadow-xl md:mt-12 md:w-[42rem] lg:w-[48rem]"
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
            class="active:bg-fill border-line-secondary flex shrink-0 cursor-pointer items-center justify-baseline gap-2 rounded-lg border px-4 py-2 transition-all duration-100 hover:shadow-sm focus:z-10 focus:outline-hidden active:translate-y-px active:scale-98"
          >
            <Icon name="github" class="fill-foreground h-4 w-4" />
            <p class="text-foreground text-xs sm:text-sm">Select Repo</p>
          </button>
        </div>

        <!-- Submit Button -->
        <div class="flex items-center gap-x-1">
          <button
            type="button"
            @click="navigateToSearch"
            class="bg-brand hover:bg-brand/90 focus:bg-brand/90 inline-flex size-8 shrink-0 cursor-pointer items-center justify-center rounded-lg text-white transition-transform focus:z-10 focus:outline-hidden active:translate-y-px active:scale-98"
          >
            <Icon name="arrow-right" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
