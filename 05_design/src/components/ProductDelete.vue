<script setup>
import DialogOverlay from './DialogOverlay.vue'
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  product: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'delete'])

const handleDelete = () => {
  emit('delete', props.product)
  emit('close')
}
</script>

<template>
  <dialog-overlay v-if="show">
    <div class="fixed inset-0 bg-black/20 flex items-center justify-center">
      <div class="bg-card rounded-md max-w-md w-full p-6 mx-4">
        <h2 class="text-primary text-base font-semibold">Delete Product</h2>
        
        <p class="mt-4 text-muted text-xs leading-[1.45]">
          Are you sure you want to delete "{{ product.name }}"? This action cannot be undone.
        </p>

        <div class="flex justify-end gap-2 mt-6">
          <button 
            @click="$emit('close')"
            class="px-4 py-1.5 border border-border rounded-sm text-xs font-medium hover:bg-input/50 transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="handleDelete"
            class="px-4 py-1.5 bg-accent text-white rounded-sm text-xs font-medium hover:bg-accent/90 transition-colors"
          >
            Delete Product
          </button>
        </div>
      </div>
    </div>
  </dialog-overlay>
</template>
