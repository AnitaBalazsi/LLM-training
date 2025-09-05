import { test, expect } from "@playwright/test";

const BASE_URL = "http://localhost:5173";

const sampleProducts = [
  {
    id: 1,
    name: "Product One",
    description: "First product",
    price: 10,
    stock: 10,
  },
  {
    id: 2,
    name: "Product Two",
    description: "Second product",
    price: 10,
    stock: 10,
  },
];

test.describe("Product Management Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.route("**/products", async (route) => {
      const req = route.request();
      if (req.method() === "GET") {
        route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(sampleProducts),
        });
      } else if (req.method() === "POST") {
        const postData = await req.postDataJSON();
        route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ id: 999, ...postData }),
        });
      }
    });

    await page.route("**/products/*", async (route) => {
      const req = route.request();
      const method = req.method();

      if (method === "PUT") {
        const putData = await req.postDataJSON();
        route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(putData),
        });
      } else if (method === "DELETE") {
        route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({}),
        });
      }
    });

    await page.goto(BASE_URL);
  });

  test("should display loading spinner initially", async ({ page }) => {
    await page.route("**/products", async (route) => {
      await new Promise((res) => setTimeout(res, 150));
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(sampleProducts),
      });
    });

    await page.goto(BASE_URL);

    const spinner = page.locator("div.animate-spin");
    await expect(spinner).toBeVisible();
  });

  test("should show products after loading", async ({ page }) => {
    const productOne = page.locator('.bg-card:has-text("Product One")');
    const productTwo = page.locator('.bg-card:has-text("Product Two")');

    await expect(productOne).toBeVisible();
    await expect(productTwo).toBeVisible();
  });

  test("should filter products when searching", async ({ page }) => {
    const searchInput = page.locator('input[placeholder="Search products..."]');
    await searchInput.fill("Product One");

    const productOne = page.locator('.bg-card:has-text("Product One")');
    const productTwo = page.locator('.bg-card:has-text("Product Two")');

    await expect(productOne).toBeVisible();
    await expect(productTwo).not.toBeVisible();
  });

  test("should open add product modal", async ({ page }) => {
    const addBtn = page.locator('button:has-text("Add Product")').first();
    await addBtn.click();

    const addModal = page.locator('h2:has-text("Add New Product")');
    await expect(addModal).toBeVisible();
  });

  test("should add a new product", async ({ page }) => {
    const addBtn = page.locator('button:has-text("Add Product")').first();
    await addBtn.click();

    const addModal = page.locator('h2:has-text("Add New Product")');
    await expect(addModal).toBeVisible();

    const nameInput = page.locator('input[placeholder="Enter product name"]');
    const descInput = page.locator(
      'textarea[placeholder="Enter product description"]'
    );
    const submitBtn = page.locator('button:has-text("Add Product")').nth(1);

    await nameInput.fill("New Product");
    await descInput.fill("New Product Description");
    await submitBtn.click();

    const notification = page.locator(
      'div.fixed div p:has-text("Product added successfully")'
    );
    await expect(notification).toBeVisible();

    const newProductCard = page.locator('.bg-card:has-text("New Product")');
    await expect(newProductCard).toBeVisible();
  });

  test("should edit a product", async ({ page }) => {
    const firstEditBtn = page
      .locator('.bg-card button:has-text("Edit")')
      .first();
    await firstEditBtn.click();

    const editModalHeader = page.locator('h2:has-text("Edit Product")');
    await expect(editModalHeader).toBeVisible();

    const nameInput = page.locator('input[placeholder="Enter product name"]');
    const descInput = page.locator(
      'textarea[placeholder="Enter product description"]'
    );

    await nameInput.fill("Updated Product One");
    await descInput.fill("Updated description");

    const submitBtn = page.locator('button:has-text("Update Product")');
    await submitBtn.click();

    const notification = page.locator(
      'div.fixed div p:has-text("Product updated")'
    );
    await expect(notification).toBeVisible();

    const updatedCard = page.locator(
      '.bg-card:has-text("Updated Product One")'
    );
    await expect(updatedCard).toBeVisible();
  });

  test("should delete a product", async ({ page }) => {
    const firstCard = page.locator(".bg-card").first();
    const deleteBtn = firstCard.locator("button.bg-accent").first();
    await deleteBtn.click();

    const deleteModal = page.locator('h2:has-text("Delete Product")');
    await expect(deleteModal).toBeVisible();

    const confirmDeleteBtn = page.locator(
      'button.bg-accent:has-text("Delete Product")'
    );
    await expect(confirmDeleteBtn).toBeVisible();
    await expect(confirmDeleteBtn).toBeEnabled();
    await confirmDeleteBtn.click();

    const notification = page.locator(
      'div.fixed div p:has-text("Product deleted")'
    );
    await expect(notification).toBeVisible();
  });

  test("should show error when fetch fails", async ({ page }) => {
    await page.route("**/products", (route) => {
      route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ message: "Server error" }),
      });
    });

    await page.goto(BASE_URL);

    const errorMsg = page.locator('p:has-text("Failed to fetch products")');
    await expect(errorMsg).toBeVisible();

    const retryBtn = page.locator('button:has-text("Try Again")');
    await expect(retryBtn).toBeVisible();
  });
});
