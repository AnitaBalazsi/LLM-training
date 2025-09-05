<template>
  <div class="bg-card border border-border rounded-[12.75px] w-[264.25px] h-[234.75px] p-4 flex flex-col shadow-card">
    <h4 class="text-primary text-[13.2px] font-normal leading-[1.0606060759em]">{{ product.name }}</h4>
    <div class="mt-[13.25px] flex-1">
      <p class="text-muted text-[11.3px] leading-[1.548672540em]">{{ product.description }}</p>
    </div>
    <div class="mt-[11px] flex justify-between items-center">
      <span class="text-[12.8px] font-medium leading-[1.6406249756em] text-primary">${{ product.price.toFixed(2) }}</span>
      <span class="text-muted text-[11.3px] leading-[1.548672540em]">Stock: {{ product.stock }}</span>
    </div>
    <div class="mt-[15px] flex gap-[7px]">
      <button 
        @click="$emit('view', product)" 
        class="flex items-center justify-center gap-[7px] h-7 px-[22.64px] py-[4.5px] text-[11.3px] font-medium leading-[1.548672540em] text-primary border border-border rounded-[6.75px] hover:bg-input/50 transition-colors"
      >
        <icon-eye class="w-[14px] h-[14px]" />
        <span>View</span>
      </button>
      <button 
        @click="$emit('edit', product)" 
        class="flex items-center justify-center gap-[7px] h-7 px-[25.25px] py-[4.5px] text-[11.3px] font-medium leading-[1.548672540em] text-primary border border-border rounded-[6.75px] hover:bg-input/50 transition-colors"
      >
        <icon-edit class="w-[14px] h-[14px]" />
        <span>Edit</span>
      </button>
      <button 
        @click="$emit('delete', product)" 
        class="flex items-center justify-center h-7 w-[31.5px] bg-accent rounded-[6.75px] hover:bg-accent/90 transition-colors"
      >
        <icon-trash class="w-[14px] h-[14px] text-white" />
      </button>
    </div>
  </div>
</template>

<script setup>
import IconEye from './icons/IconEye.vue'
import IconEdit from './icons/IconEdit.vue'
import IconTrash from './icons/IconTrash.vue'

defineProps({
  product: {
    type: Object,
    required: true
  }
})

defineEmits(['view', 'edit', 'delete'])
</script>
