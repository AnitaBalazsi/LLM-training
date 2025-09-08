from contextlib import asynccontextmanager
from typing import List
import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config import settings
from database import Product, Cart, CartItem, create_tables, get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductDTO(BaseModel):
    id: int
    name: str
    price: float
    description: str | None = None
    stock: int

class ProductCreateDTO(BaseModel):
    name: str
    price: float
    description: str | None = None
    stock: int

class ProductUpdateDTO(BaseModel):
    name: str | None = None
    price: float | None = None
    description: str | None = None
    stock: int | None = None


# Cart DTOs
class CartItemDTO(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_when_added: float
    product: ProductDTO

class CartDTO(BaseModel):
    id: int
    session_id: str
    items: List[CartItemDTO]

class CartItemCreateDTO(BaseModel):
    product_id: int
    quantity: int

class CartItemUpdateDTO(BaseModel):
    quantity: int

class CheckoutDTO(BaseModel):
    session_id: str
    total_amount: float
    items_processed: int

class CheckoutResponseDTO(BaseModel):
    success: bool
    message: str
    checkout_details: CheckoutDTO | None = None
    errors: List[str] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Template"}


@app.post("/products/", response_model=ProductDTO)
async def create_product(product: ProductCreateDTO, db: AsyncSession = Depends(get_db)):
    db_product = Product(name=product.name, price=product.price, description=product.description, stock=product.stock)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@app.get("/products/", response_model=List[ProductDTO])
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products

@app.put("/products/{id}", response_model=ProductDTO)
async def update_product(id: int, product: ProductUpdateDTO, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Product).where(Product.id == id))
        db_product = result.scalar_one_or_none()

        if db_product is None:
            raise HTTPException(status_code=404, detail="Product not found!")
        
        update_data = product.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        await db.commit()
        await db.refresh(db_product)
        return db_product
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update product {id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update product")

@app.delete("/products/{id}")
async def delete_product(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == id))
    db_product = result.scalar_one_or_none()

    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found!")
    
    await db.delete(db_product)
    await db.commit()

    return {"message": "Product deleted successfully"}

@app.get("/products/{id}", response_model=ProductDTO)
async def get_product(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.id == id))
    db_product = result.scalar_one_or_none()

    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found!")
    
    return db_product


# Cart endpoints
@app.post("/cart/{session_id}/checkout", response_model=CheckoutResponseDTO)
async def checkout_cart(session_id: str, db: AsyncSession = Depends(get_db)):
    # Get cart with items
    result = await db.execute(
        select(Cart)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
        .where(Cart.session_id == session_id)
    )
    cart = result.scalar_one_or_none()
    
    if cart is None or not cart.items:
        raise HTTPException(status_code=404, detail="Cart not found or empty!")
    
    errors = []
    total_amount = 0
    items_processed = 0
    
    # Check stock availability for all items first
    for cart_item in cart.items:
        if cart_item.product.stock < cart_item.quantity:
            errors.append(
                f"Insufficient stock for {cart_item.product.name}. "
                f"Available: {cart_item.product.stock}, Requested: {cart_item.quantity}"
            )
    
    # If there are stock errors, return them without processing
    if errors:
        return CheckoutResponseDTO(
            success=False,
            message="Checkout failed due to insufficient stock",
            errors=errors
        )
    
    # Process the checkout - update stock for each item
    try:
        for cart_item in cart.items:
            # Update product stock
            cart_item.product.stock -= cart_item.quantity
            total_amount += cart_item.quantity * cart_item.product.price
            items_processed += cart_item.quantity
        
        # Clear the cart by deleting all cart items
        await db.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
        
        # Commit all changes
        await db.commit()
        
        checkout_details = CheckoutDTO(
            session_id=session_id,
            total_amount=total_amount,
            items_processed=items_processed
        )
        
        return CheckoutResponseDTO(
            success=True,
            message="Checkout completed successfully",
            checkout_details=checkout_details
        )
        
    except Exception as e:
        await db.rollback()
        # Log the specific error for debugging
        logger.error(f"Checkout failed for session {session_id}: {str(e)}")
        # Return generic error message to client
        raise HTTPException(status_code=500, detail="Checkout processing failed. Please try again.")


@app.get("/cart/{session_id}", response_model=CartDTO)
async def get_cart(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Cart)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
        .where(Cart.session_id == session_id)
    )
    cart = result.scalar_one_or_none()
    
    if cart is None:
        # Create a new cart if it doesn't exist
        cart = Cart(session_id=session_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
    
    return cart


@app.post("/cart/{session_id}/items", response_model=CartDTO)
async def add_to_cart(session_id: str, item: CartItemCreateDTO, db: AsyncSession = Depends(get_db)):
    # Get or create cart
    result = await db.execute(
        select(Cart)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
        .where(Cart.session_id == session_id)
    )
    cart = result.scalar_one_or_none()
    
    if cart is None:
        cart = Cart(session_id=session_id)
        db.add(cart)
        await db.flush()  # Get the cart ID
    
    # Get product details
    product_result = await db.execute(select(Product).where(Product.id == item.product_id))
    product = product_result.scalar_one_or_none()
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found!")
    
    # Check if item already exists in cart
    existing_item_result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item.product_id
        )
    )
    existing_item = existing_item_result.scalar_one_or_none()
    
    if existing_item:
        # Update quantity and price
        existing_item.quantity += item.quantity
        existing_item.price_when_added = product.price
    else:
        # Create new cart item
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_when_added=product.price
        )
        db.add(cart_item)
    
    await db.commit()
    await db.refresh(cart)
    
    # Reload cart with items
    result = await db.execute(
        select(Cart)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
        .where(Cart.id == cart.id)
    )
    cart = result.scalar_one()
    
    return cart


@app.put("/cart/{session_id}/items/{product_id}", response_model=CartDTO)
async def update_cart_item(session_id: str, product_id: int, update: CartItemUpdateDTO, db: AsyncSession = Depends(get_db)):
    # Get cart
    result = await db.execute(
        select(Cart)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
        .where(Cart.session_id == session_id)
    )
    cart = result.scalar_one_or_none()
    
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found!")
    
    # Find cart item
    item_result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        )
    )
    cart_item = item_result.scalar_one_or_none()
    
    if cart_item is None:
        raise HTTPException(status_code=404, detail="Item not found in cart!")
    
    if update.quantity <= 0:
        await db.delete(cart_item)
    else:
        cart_item.quantity = update.quantity
    
    await db.commit()
    await db.refresh(cart)
    
    # Reload cart with items
    result = await db.execute(
        select(Cart)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
        .where(Cart.id == cart.id)
    )
    cart = result.scalar_one()
    
    return cart


@app.delete("/cart/{session_id}/items/{product_id}")
async def remove_from_cart(session_id: str, product_id: int, db: AsyncSession = Depends(get_db)):
    # Get cart
    result = await db.execute(select(Cart).where(Cart.session_id == session_id))
    cart = result.scalar_one_or_none()
    
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found!")
    
    # Delete cart item
    await db.execute(
        delete(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        )
    )
    
    await db.commit()
    return {"message": "Item removed from cart"}


@app.delete("/cart/{session_id}")
async def clear_cart(session_id: str, db: AsyncSession = Depends(get_db)):
    # Get cart
    result = await db.execute(select(Cart).where(Cart.session_id == session_id))
    cart = result.scalar_one_or_none()
    
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found!")
    
    # Delete all cart items
    await db.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
    await db.commit()
    
    return {"message": "Cart cleared"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
