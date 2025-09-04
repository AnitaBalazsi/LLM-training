<script setup>
import IconX from '../components/icons/IconX.vue'
import DialogOverlay from './DialogOverlay.vue'
defineProps({
  show: {
    type: Boolean,
    default: false
  },
  product: {
    type: Object,
    required: true
  }
})

defineEmits(['close'])
</script>

<template>
  <dialog-overlay v-if="show">
    <div class="fixed inset-0 bg-black/20 flex items-center justify-center">
      <div class="bg-card rounded-md max-w-md w-full p-6 mx-4">
        <div class="flex justify-between items-start">
          <h2 class="text-primary text-base font-semibold">Product Details</h2>
          <button @click="$emit('close')" class="p-1.5 hover:bg-input/50 rounded-sm transition-colors">
            <icon-x class="w-3.5 h-3.5" />
          </button>
        </div>
        
        <h3 class="mt-4 text-primary text-base font-medium">{{ product.name }}</h3>
        <p class="mt-3 text-muted text-base leading-6">{{ product.description }}</p>
        
        <div class="mt-4 h-[1px] bg-border" />
        
        <div class="mt-4 flex flex-col gap-8">
          <div class="flex gap-12">
            <div>
              <span class="text-muted text-xs">Price:</span>
              <p class="text-primary text-xs font-medium mt-1">${{ product.price.toFixed(2) }}</p>
            </div>
            <div>
              <span class="text-muted text-xs">Stock:</span>
              <p class="text-muted text-xs mt-1">{{ product.stock }} units</p>
            </div>
          </div>
          <div>
            <span class="text-muted text-xs">Product ID:</span>
            <p class="text-primary text-[11px] mt-1">{{ product.id }}</p>
          </div>
        </div>
      </div>
    </div>
  </dialog-overlay>
</template>
