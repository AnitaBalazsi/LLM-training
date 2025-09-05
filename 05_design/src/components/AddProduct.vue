<script setup>
import DialogOverlay from './DialogOverlay.vue'
import IconX from '../components/icons/IconX.vue'
import { ref, watch } from 'vue'
const emit = defineEmits(['close', 'add'])
const props = defineProps({ visible: { type: Boolean, default: false } })

const form = ref({ name: '', description: '', price: 0, stock: 0 })

watch(() => props.visible, (val) => {
  if (val) {
    form.value = { name: '', description: '', price: 0, stock: 0 }
  }
})

const handleAdd = () => {
  if (!form.value.name.trim()) return
  emit('add', { ...form.value })
  emit('close')
}
</script>

<template>
  <dialog-overlay v-if="visible">
    <div class="fixed inset-0 bg-black/20 flex items-center justify-center">
      <div class="bg-card rounded-md max-w-md w-full p-6 mx-4">
        <div class="flex justify-between items-start">
          <h2 class="text-primary text-base font-semibold">Add New Product</h2>
          <button @click="$emit('close')" class="p-1.5 hover:bg-input/50 rounded-sm transition-colors">
            <icon-x class="text-muted" />
          </button>
        </div>

        <div class="mt-6 flex flex-col gap-4">
          <label class="text-primary text-xs font-medium">Product Name</label>
          <input
            v-model="form.name"
            type="text"
            class="w-full h-8 px-3 py-2 bg-input rounded-md text-xs text-primary focus:outline-none focus:ring-1"
            placeholder="Enter product name"
          />

          <label class="text-primary text-xs font-medium">Description</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="w-full px-3 py-2 bg-input rounded-md text-xs text-primary focus:outline-none focus:ring-1 resize-none"
            placeholder="Enter product description"
          ></textarea>

          <div class="flex gap-4">
            <div class="flex-1">
              <label class="text-primary text-xs font-medium">Price ($)</label>
              <input
                v-model.number="form.price"
                type="number"
                min="0"
                step="0.01"
                class="w-full h-8 px-3 py-2 bg-input rounded-md text-xs text-primary focus:outline-none focus:ring-1"
              />
            </div>
            <div class="flex-1">
              <label class="text-primary text-xs font-medium">Stock</label>
              <input
                v-model.number="form.stock"
                type="number"
                min="0"
                class="w-full h-8 px-3 py-2 bg-input rounded-md text-xs text-primary focus:outline-none focus:ring-1"
              />
            </div>
          </div>
        </div>

        <div class="mt-6 flex justify-end gap-2">
          <button
            type="button"
            @click="$emit('close')"
            class="h-8 px-4 py-1.5 border border-border rounded-md text-xs"
          >
            Cancel
          </button>
          <button
            type="button"
            @click="handleAdd"
            class="h-8 px-4 py-1.5 bg-primary text-white rounded-md text-xs"
          >
            Add Product
          </button>
        </div>
      </div>
    </div>
  </dialog-overlay>
</template>
