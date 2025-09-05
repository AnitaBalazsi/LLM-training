<script setup>
import { ref, watch } from 'vue'
import IconX from '../components/icons/IconX.vue'
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

const emit = defineEmits(['close', 'update'])
const errors = ref({})

const form = ref({
  name: '',
  description: '',
  price: 0,
  stock: 0
})

watch(() => props.product, (newProduct) => {
  form.value = {
    name: newProduct.name,
    description: newProduct.description,
    price: newProduct.price,
    stock: newProduct.stock
  }
}, { immediate: true })

const validateForm = () => {
  errors.value = {}
  if (!form.value.name.trim()) {
    errors.value.name = 'Product name is required'
  }
  if (form.value.price <= 0) {
    errors.value.price = 'Price must be greater than 0'
  }
  if (form.value.stock < 0) {
    errors.value.stock = 'Stock cannot be negative'
  }
  return Object.keys(errors.value).length === 0
}

const handleSubmit = () => {
  if (!validateForm()) return

  emit('update', {
    ...props.product,
    ...form.value
  })
  emit('close')
}
</script>

<template>
  <dialog-overlay v-if="show">
    <div class="fixed inset-0 bg-black/20 flex items-center justify-center">
      <div class="bg-card rounded-[8.75px] w-[388px] p-6 mx-4">
        <div class="flex justify-between items-start">
          <h2 class="text-primary text-base font-semibold leading-[0.984375em]">Edit Product</h2>
          <button @click="$emit('close')" class="p-1.5 hover:bg-input/50 rounded-sm transition-colors">
            <icon-x class="w-3.5 h-3.5" />
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="flex flex-col mt-2">
          <div>
            <label class="text-primary text-xs font-medium leading-[1.0208333333em]">Product Name</label>
            <div class="relative mt-[18px]">
              <input 
                v-model="form.name"
                type="text"
                class="w-[344px] h-8 px-3 py-2 bg-input rounded-[6.75px] text-xs text-primary leading-[1.2102272511em] focus:outline-none focus:ring-1"
                :class="errors.name ? 'ring-1 ring-red-500' : 'focus:ring-border'"
                placeholder="Enter product name"
              />
              <p v-if="errors.name" class="absolute -bottom-5 left-0 text-xs text-red-500">{{ errors.name }}</p>
            </div>
          </div>

          <div>
            <label class="text-primary text-xs font-medium leading-[1.0208333333em]">Description</label>
            <div class="relative mt-[18px]">
              <textarea 
                v-model="form.description"
                rows="3"
                class="w-[344px] h-[69px] px-3 py-2 bg-input rounded-[6.75px] text-xs text-primary leading-[1.2102272511em] focus:outline-none focus:ring-1 resize-none"
                :class="errors.description ? 'ring-1 ring-red-500' : 'focus:ring-border'"
                placeholder="Enter product description"
              ></textarea>
              <p v-if="errors.description" class="absolute -bottom-5 left-0 text-xs text-red-500">{{ errors.description }}</p>
            </div>
          </div>

          <div class="flex gap-4">
            <div>
              <label class="text-primary text-xs font-medium leading-[1.0208333333em]">Price ($)</label>
              <div class="relative mt-[18px]">
                <input 
                  v-model="form.price"
                  type="number"
                  step="0.01"
                  min="0"
                  class="w-[165px] h-8 px-3 py-2 bg-input rounded-[6.75px] text-xs text-primary leading-[1.2102272511em] focus:outline-none focus:ring-1"
                  :class="errors.price ? 'ring-1 ring-red-500' : 'focus:ring-border'"
                />
                <p v-if="errors.price" class="absolute -bottom-5 left-0 text-xs text-red-500">{{ errors.price }}</p>
              </div>
            </div>
            <div>
              <label class="text-primary text-xs font-medium leading-[1.0208333333em]">Stock</label>
              <div class="relative mt-[18px]">
                <input 
                  v-model="form.stock"
                  type="number"
                  min="0"
                  class="w-[165px] h-8 px-3 py-2 bg-input rounded-[6.75px] text-xs text-primary leading-[1.2102272511em] focus:outline-none focus:ring-1"
                  :class="errors.stock ? 'ring-1 ring-red-500' : 'focus:ring-border'"
                />
                <p v-if="errors.stock" class="absolute -bottom-5 left-0 text-xs text-red-500">{{ errors.stock }}</p>
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-2 mt-8">
            <button 
              type="button"
              @click="$emit('close')"
              class="h-8 px-4 py-1.5 border border-border rounded-[6.75px] text-xs font-medium leading-[1.548672540em] hover:bg-input/50 transition-colors"
            >
              Cancel
            </button>
            <button 
              type="submit"
              class="h-8 px-4 py-1.5 bg-primary text-white rounded-[6.75px] text-xs font-medium leading-[1.548672540em] hover:bg-primary/90 transition-colors"
            >
              Update Product
            </button>
          </div>
        </form>
      </div>
    </div>
  </dialog-overlay>
</template>
