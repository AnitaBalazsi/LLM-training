<template>
  <div class="fixed bottom-6 right-6 z-40">
    <!-- Always visible cart panel -->
    <div class="bg-white rounded-lg shadow-xl border border-border w-96 max-h-96 overflow-hidden">
      <!-- Cart header -->
      <div class="p-4 border-b border-border">
        <h3 class="text-primary text-lg font-medium">Shopping Cart</h3>
        <!-- Stock error notifications -->
        <div v-if="cartValidation.hasErrors" class="mt-2 p-2 bg-red-50 border border-red-200 rounded text-red-700 text-xs">
          <p class="font-medium">Stock Issues:</p>
          <ul class="mt-1 space-y-1">
            <li v-for="error in cartValidation.errors" :key="error.productId">
              {{ error.productName }}: Only {{ error.available }} in stock (requested {{ error.requested }})
            </li>
          </ul>
        </div>
      </div>

      <!-- Cart items -->
      <div v-if="cartItems.length === 0" class="p-4 text-center text-muted">
        Your cart is empty
      </div>
      
      <div v-else class="max-h-64 overflow-y-auto">
        <div v-for="item in cartItems" :key="item.id" 
             class="flex items-center justify-between p-4 border-b border-border last:border-b-0"
             :class="{ 'bg-red-50': hasStockError(item.id) }">
          <div class="flex-1">
            <h4 class="text-primary text-sm font-medium">{{ item.name }}</h4>
            <p class="text-muted text-xs">${{ item.price.toFixed(2) }} each</p>
            <p v-if="hasStockError(item.id)" class="text-red-600 text-xs font-medium">
              Insufficient stock!
            </p>
          </div>
          <div class="flex items-center gap-3">
            <div class="flex items-center gap-2">
              <button @click="decreaseQuantity(item.id)" 
                      class="w-6 h-6 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-sm">
                -
              </button>
              <span class="text-sm font-medium w-8 text-center"
                    :class="{ 'text-red-600': hasStockError(item.id) }">
                {{ item.quantity }}
              </span>
              <button @click="increaseQuantity(item.id)" 
                      class="w-6 h-6 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-sm">
                +
              </button>
            </div>
            <div class="text-right">
              <p class="text-primary text-sm font-medium">${{ (item.price * item.quantity).toFixed(2) }}</p>
            </div>
            <button @click="removeFromCart(item.id)" 
                    class="text-red-500 hover:text-red-700 p-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Cart footer -->
      <div v-if="cartItems.length > 0" class="p-4 border-t border-border bg-gray-50">
        <div class="flex justify-between items-center mb-3">
          <span class="text-primary font-medium">Total:</span>
          <span class="text-primary font-bold text-lg">${{ totalPrice.toFixed(2) }}</span>
        </div>
        <button 
          @click="$emit('checkout')"
          :disabled="!cartValidation.canCheckout || isLoading"
          :class="[
            'w-full py-2 rounded-lg transition-colors',
            cartValidation.canCheckout && !isLoading
              ? 'bg-primary text-white hover:bg-primary/90' 
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          ]"
        >
          <span v-if="isLoading">Processing...</span>
          <span v-else-if="cartValidation.canCheckout">Checkout</span>
          <span v-else>Cannot Checkout - Stock Issues</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  cartItems: {
    type: Array,
    default: () => []
  },
  cartValidation: {
    type: Object,
    default: () => ({ hasErrors: false, errors: [], canCheckout: false })
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['increaseQuantity', 'decreaseQuantity', 'removeFromCart', 'checkout'])

const totalPrice = computed(() => {
  return props.cartItems.reduce((total, item) => total + (item.price * item.quantity), 0)
})

const hasStockError = (productId) => {
  return props.cartValidation.errors.some(error => error.productId === productId)
}

const increaseQuantity = (productId) => {
  emit('increaseQuantity', productId)
}

const decreaseQuantity = (productId) => {
  emit('decreaseQuantity', productId)
}

const removeFromCart = (productId) => {
  emit('removeFromCart', productId)
}
</script>
