<script setup>
import { ref, computed, onMounted } from 'vue'
import ProductCard from './components/ProductCard.vue'
import ProductDetails from './components/ProductDetails.vue'
import ProductEdit from './components/ProductEdit.vue'
import ProductDelete from './components/ProductDelete.vue'
import AddProduct from './components/AddProduct.vue'
import CartWidget from './components/CartWidget.vue'
import IconSearch from './components/icons/IconSearch.vue'
import IconPlus from './components/icons/IconPlus.vue'

const products = ref([])
const searchQuery = ref('')
const selectedProduct = ref(null)
const showDetails = ref(false)
const showEdit = ref(false)
const showDelete = ref(false)
const showAdd = ref(false)
const isLoading = ref(false)
const error = ref(null)
const notification = ref({ show: false, message: '', type: 'success' })
const cartItems = ref([])
const sessionId = ref('')

const API_URL = 'http://localhost:8000'

// Session configuration
const SESSION_EXPIRY_HOURS = 24 // 24 hours session expiry
const SESSION_PREFIX = 'cart_'

// Validate session ID format (UUID v4 pattern)
const isValidSessionId = (sessionId) => {
  if (!sessionId || typeof sessionId !== 'string') return false
  
  // Check if it has the correct prefix
  if (!sessionId.startsWith(SESSION_PREFIX)) return false
  
  // Extract UUID part and validate format
  const uuidPart = sessionId.substring(SESSION_PREFIX.length)
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
  return uuidRegex.test(uuidPart)
}

// Check if session has expired
const isSessionExpired = (timestamp) => {
  if (!timestamp) return true
  const now = Date.now()
  const expiryTime = timestamp + (SESSION_EXPIRY_HOURS * 60 * 60 * 1000)
  return now > expiryTime
}

// Generate or get session ID from localStorage with validation and expiration
const initializeSession = () => {
  let storedSessionId = localStorage.getItem('cart_session_id')
  let sessionTimestamp = localStorage.getItem('cart_session_timestamp')
  
  // Parse timestamp
  const timestamp = sessionTimestamp ? parseInt(sessionTimestamp, 10) : null
  
  // Validate existing session
  if (storedSessionId && 
      isValidSessionId(storedSessionId) && 
      !isSessionExpired(timestamp)) {
    sessionId.value = storedSessionId
    return
  }
  
  // Generate new session if validation fails or session expired
  const newSessionId = SESSION_PREFIX + crypto.randomUUID()
  const newTimestamp = Date.now().toString()
  
  localStorage.setItem('cart_session_id', newSessionId)
  localStorage.setItem('cart_session_timestamp', newTimestamp)
  sessionId.value = newSessionId
  
  // Clear any existing cart data if session was invalid/expired
  if (storedSessionId) {
    showNotification('Session expired - cart cleared for security', 'info')
  }
}

// Refresh session timestamp on user activity
const refreshSession = () => {
  if (sessionId.value && isValidSessionId(sessionId.value)) {
    const newTimestamp = Date.now().toString()
    localStorage.setItem('cart_session_timestamp', newTimestamp)
  }
}

const showNotification = (message, type = 'success') => {
  notification.value = { show: true, message, type }
  setTimeout(() => (notification.value.show = false), 3000)
}

const fetchProducts = async () => {
  isLoading.value = true
  error.value = null
  try {
    const res = await fetch(`${API_URL}/products`)
    if (!res.ok) throw new Error('Failed to fetch products')
    const data = await res.json()
    products.value = Array.isArray(data) ? data : []
  } catch (e) {
    error.value = e.message || 'Failed to fetch products'
  } finally {
    isLoading.value = false
  }
}

const createProductRequest = async (plainProduct) => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/products`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(plainProduct),
    })
    if (!res.ok) {
      let msg = 'Failed to add product'
      try {
        const body = await res.json()
        if (body?.message) msg = body.message
      } catch {}
      throw new Error(msg)
    }
    const newProduct = await res.json()
    return { ok: true, data: newProduct }
  } catch (e) {
    return { ok: false, error: e.message || 'Failed to add product' }
  } finally {
    isLoading.value = false
  }
}
const onAddProduct = async (payload) => {
  const result = await createProductRequest(payload)
  if (result.ok) {
    products.value.push(result.data)
    showNotification('Product added successfully', 'success')
    showAdd.value = false
  } else {
    showNotification(result.error, 'error')
  }
}

const updateProduct = async (product) => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/products/${product.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(product),
    })
    if (!res.ok) throw new Error('Failed to update product')
    const updated = await res.json()
    const idx = products.value.findIndex(p => p.id === updated.id)
    if (idx !== -1) {
      products.value[idx] = updated
      // Update cart item price if it exists
      updateCartItemPrice(updated.id, updated.price)
    }
    showNotification('Product updated', 'success')
  } catch (e) {
    showNotification(e.message || 'Failed to update product', 'error')
  } finally {
    isLoading.value = false
  }
}

const deleteProduct = async (product) => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/products/${product.id}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Failed to delete product')
    products.value = products.value.filter(p => p.id !== product.id)
    showNotification('Product deleted', 'success')
  } catch (e) {
    showNotification(e.message || 'Failed to delete product', 'error')
  } finally {
    isLoading.value = false
  }
}

const filteredProducts = computed(() => {
  if (!searchQuery.value) return products.value
  const q = searchQuery.value.toLowerCase()
  return products.value.filter(p =>
    String(p.name).toLowerCase().includes(q) ||
    String(p.description).toLowerCase().includes(q)
  )
})

onMounted(() => {
  initializeSession()
  fetchProducts()
  loadCart()
})

// Load cart from backend
const loadCart = async () => {
  try {
    const res = await fetch(`${API_URL}/cart/${sessionId.value}`)
    if (res.ok) {
      const cartData = await res.json()
      cartItems.value = cartData.items.map(item => ({
        id: item.product.id,
        name: item.product.name,
        price: item.product.price, // Use current price from product
        quantity: item.quantity
      }))
    }
  } catch (e) {
    console.error('Failed to load cart:', e)
  }
}

// Cart functionality
const addToCart = async (product) => {
  refreshSession() // Refresh session on user activity
  
  const existingItem = cartItems.value.find(item => item.id === product.id)
  
  if (existingItem) {
    // Check if we can add one more item
    if (existingItem.quantity < product.stock) {
      try {
        const res = await fetch(`${API_URL}/cart/${sessionId.value}/items`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            product_id: product.id,
            quantity: 1
          })
        })
        
        if (res.ok) {
          existingItem.quantity += 1
          existingItem.price = product.price
          showNotification(`${product.name} added to cart`, 'success')
        } else {
          throw new Error('Failed to add to cart')
        }
      } catch (e) {
        showNotification('Failed to add item to cart', 'error')
      }
    } else {
      showNotification(`Cannot add more ${product.name} - insufficient stock`, 'error')
    }
  } else {
    // Check if product has stock
    if (product.stock > 0) {
      try {
        const res = await fetch(`${API_URL}/cart/${sessionId.value}/items`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            product_id: product.id,
            quantity: 1
          })
        })
        
        if (res.ok) {
          cartItems.value.push({
            id: product.id,
            name: product.name,
            price: product.price,
            quantity: 1
          })
          showNotification(`${product.name} added to cart`, 'success')
        } else {
          throw new Error('Failed to add to cart')
        }
      } catch (e) {
        showNotification('Failed to add item to cart', 'error')
      }
    } else {
      showNotification(`${product.name} is out of stock`, 'error')
    }
  }
}

// Update cart item price when product is updated
const updateCartItemPrice = (productId, newPrice) => {
  const cartItem = cartItems.value.find(item => item.id === productId)
  if (cartItem) {
    cartItem.price = newPrice
    showNotification('Cart updated with new price', 'info')
  }
}

// Get current product stock for cart validation
const getProductStock = (productId) => {
  const product = products.value.find(p => p.id === productId)
  return product ? product.stock : 0
}

// Validate cart items against current stock
const cartValidation = computed(() => {
  const errors = []
  let hasStockErrors = false
  
  cartItems.value.forEach(item => {
    const currentStock = getProductStock(item.id)
    if (item.quantity > currentStock) {
      errors.push({
        productId: item.id,
        productName: item.name,
        requested: item.quantity,
        available: currentStock
      })
      hasStockErrors = true
    }
  })
  
  return {
    hasErrors: hasStockErrors,
    errors: errors,
    canCheckout: !hasStockErrors && cartItems.value.length > 0
  }
})

const increaseQuantity = async (productId) => {
  refreshSession() // Refresh session on user activity
  
  const item = cartItems.value.find(item => item.id === productId)
  const currentStock = getProductStock(productId)
  
  if (item) {
    if (item.quantity < currentStock) {
      try {
        const res = await fetch(`${API_URL}/cart/${sessionId.value}/items/${productId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            quantity: item.quantity + 1
          })
        })
        
        if (res.ok) {
          item.quantity += 1
        } else {
          throw new Error('Failed to update cart')
        }
      } catch (e) {
        showNotification('Failed to update cart', 'error')
      }
    } else {
      showNotification('Not enough stock available', 'error')
    }
  }
}

const decreaseQuantity = async (productId) => {
  refreshSession() // Refresh session on user activity
  
  const item = cartItems.value.find(item => item.id === productId)
  if (item) {
    if (item.quantity > 1) {
      try {
        const res = await fetch(`${API_URL}/cart/${sessionId.value}/items/${productId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            quantity: item.quantity - 1
          })
        })
        
        if (res.ok) {
          item.quantity -= 1
        } else {
          throw new Error('Failed to update cart')
        }
      } catch (e) {
        showNotification('Failed to update cart', 'error')
      }
    } else {
      removeFromCart(productId)
    }
  }
}

const removeFromCart = async (productId) => {
  refreshSession() // Refresh session on user activity
  
  const index = cartItems.value.findIndex(item => item.id === productId)
  if (index !== -1) {
    const item = cartItems.value[index]
    
    try {
      const res = await fetch(`${API_URL}/cart/${sessionId.value}/items/${productId}`, {
        method: 'DELETE'
      })
      
      if (res.ok) {
        cartItems.value.splice(index, 1)
        showNotification(`${item.name} removed from cart`, 'success')
      } else {
        throw new Error('Failed to remove from cart')
      }
    } catch (e) {
      showNotification('Failed to remove item from cart', 'error')
    }
  }
}

// Checkout functionality
const checkout = async () => {
  refreshSession() // Refresh session on user activity
  
  if (!cartValidation.value.canCheckout) {
    showNotification('Cannot checkout - please resolve stock issues first', 'error')
    return
  }
  
  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/cart/${sessionId.value}/checkout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    
    const result = await res.json()
    
    if (res.ok && result.success) {
      // Clear local cart
      cartItems.value = []
      
      // Refresh products to show updated stock
      await fetchProducts()
      
      showNotification(
        `Checkout successful! Total: $${result.checkout_details.total_amount.toFixed(2)} for ${result.checkout_details.items_processed} items`,
        'success'
      )
    } else {
      // Show error messages
      const errorMessage = result.errors?.join(', ') || result.message || 'Checkout failed'
      showNotification(errorMessage, 'error')
    }
  } catch (e) {
    showNotification('Checkout failed - please try again', 'error')
  } finally {
    isLoading.value = false
  }
}

const openAdd = (ev) => {
  ev?.preventDefault?.()
  ev?.stopPropagation?.()
  showAdd.value = true
}
</script>

<template>
  <main class="min-h-screen bg-[#FAFAFA] py-5">
    <transition
      enter-active-class="transform ease-out duration-300 transition"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition ease-in duration-100"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="notification.show" class="fixed top-4 right-4 z-50">
        <div :class="{
            'bg-green-50 text-green-800': notification.type === 'success',
            'bg-red-50 text-red-800': notification.type === 'error',
            'bg-blue-50 text-blue-800': notification.type === 'info'
          }" class="rounded-lg p-4 shadow-md">
          <p class="text-sm font-medium">{{ notification.message }}</p>
        </div>
      </div>
    </transition>

    <div class="max-w-7xl mx-auto px-4">
      <h1 class="text-primary text-[13.2px]">Product Management</h1>

      <div class="mt-8 flex items-center justify-between">
        <div class="relative w-[392px]">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search products..."
            @keydown.enter.prevent
            class="w-full h-[31.5px] pl-[35px] pr-4 py-[8.4px] bg-input rounded-[6.75px] text-[10.7px] leading-[1.3738em] text-primary placeholder-muted focus:outline-none focus:ring-1 focus:ring-border"
          />
          <div class="absolute left-3 top-2 w-3.5 h-3.5">
            <icon-search class="text-muted" />
          </div>
        </div>

        <button
          type="button"
          @click.stop.prevent="openAdd"
          class="flex items-center h-[31.5px] px-4 py-1 bg-primary text-white rounded-[6.75px] text-[11.3px] font-medium hover:bg-primary/90 transition-colors"
        >
          <icon-plus class="w-[14px] h-[14px] stroke-[1.17px] mr-2" />
          Add Product
        </button>
      </div>

      <div class="mt-6">
        <div v-if="isLoading" class="min-h-[320px] flex items-center justify-center">
          <div class="animate-spin rounded-full h-10 w-10 border-[2.5px] border-primary border-t-transparent"></div>
        </div>

        <div v-else-if="error" class="min-h-[320px] flex flex-col items-center justify-center">
          <p class="text-accent text-[13.2px] leading-[1.06em]">{{ error }}</p>
          <button @click="fetchProducts" class="mt-4 h-8 px-4 py-1.5 bg-primary text-white rounded-[6.75px] text-xs">Try Again</button>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <template v-if="filteredProducts.length > 0">
            <product-card
              v-for="product in filteredProducts"
              :key="product.id"
              :product="product"
              @view="(p) => { selectedProduct = p; showDetails = true }"
              @edit="(p) => { selectedProduct = p; showEdit = true }"
              @delete="(p) => { selectedProduct = p; showDelete = true }"
              @addToCart="addToCart"
            />
          </template>
          <div v-else class="col-span-full min-h-[320px] flex items-center justify-center">
            <p class="text-muted text-[13.2px] leading-[1.06em]">No products found</p>
          </div>
        </div>
      </div>
    </div>

    <product-details
      v-if="selectedProduct"
      :show="showDetails"
      :product="selectedProduct"
      @close="showDetails = false"
    />

    <product-edit
      v-if="selectedProduct"
      :show="showEdit"
      :product="selectedProduct"
      @close="showEdit = false"
      @update="updateProduct"
    />

    <product-delete
      v-if="selectedProduct"
      :show="showDelete"
      :product="selectedProduct"
      @close="showDelete = false"
      @delete="deleteProduct"
    />

    <add-product
      v-if="showAdd"
      :visible="showAdd"
      @close="showAdd = false"
      @add="onAddProduct"
    />

    <!-- Cart Widget -->
    <cart-widget
      :cart-items="cartItems"
      :cart-validation="cartValidation"
      :is-loading="isLoading"
      @increase-quantity="increaseQuantity"
      @decrease-quantity="decreaseQuantity"
      @remove-from-cart="removeFromCart"
      @checkout="checkout"
    />
  </main>
</template>
