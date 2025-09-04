<!-- Simple dialog overlay component -->
<template>
  <transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div class="fixed inset-0 z-50">
      <slot></slot>
    </div>
  </transition>
</template>
