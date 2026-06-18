let products = [];

const FALLBACK_PRODUCTS = [
  {
    id: "box-tee",
    name: "Box Cut Graphic Tee",
    category: "Clothing",
    type: "tees",
    price: 1499,
    badge: "New",
    image: "assets/product-tee.png",
    description: "Heavy cotton tee with a straight drape.",
    sizes: ["S", "M", "L", "XL"],
    colors: [
      { name: "Ink", value: "#1f2828" },
      { name: "Rust", value: "#ef6f4d" },
      { name: "Bone", value: "#ede8dc" }
    ]
  },
  {
    id: "hoodie",
    name: "Loopback Utility Hoodie",
    category: "Clothing",
    type: "hoodies",
    price: 3299,
    badge: "Warm",
    image: "assets/product-hoodie.png",
    description: "Relaxed fleece hoodie with a deep pocket.",
    sizes: ["S", "M", "L", "XL"],
    colors: [
      { name: "Plum", value: "#6b48b3" },
      { name: "Ink", value: "#1f2828" },
      { name: "Sky", value: "#b8d2dc" }
    ]
  },
  {
    id: "runner",
    name: "Arc Runner Sneaker",
    category: "Shoes",
    type: "sneakers",
    price: 5299,
    badge: "Top",
    image: "assets/product-sneaker.png",
    description: "Cushioned everyday sneaker with a bold upper.",
    sizes: ["7", "8", "9", "10", "11"],
    colors: [
      { name: "Signal Red", value: "#f15154" },
      { name: "Black", value: "#1f2828" },
      { name: "Cream", value: "#f3ead8" }
    ]
  },
  {
    id: "cap",
    name: "Panel Logo Cap",
    category: "Caps",
    type: "caps",
    price: 899,
    badge: "Fresh",
    image: "assets/product-cap.png",
    description: "Structured cap with an adjustable back strap.",
    sizes: ["OS"],
    colors: [
      { name: "Teal", value: "#126c72" },
      { name: "Ink", value: "#1f2828" },
      { name: "Rust", value: "#ef6f4d" }
    ]
  },
  {
    id: "jacket",
    name: "Split Zip Coach Jacket",
    category: "Clothing",
    type: "jackets",
    price: 4299,
    badge: "Drop",
    image: "assets/product-jacket.png",
    description: "Water-resistant shell with contrast zip trim.",
    sizes: ["S", "M", "L", "XL"],
    colors: [
      { name: "Navy", value: "#202f4d" },
      { name: "Rust", value: "#ef6f4d" },
      { name: "Bone", value: "#ede8dc" }
    ]
  },
  {
    id: "tote",
    name: "Market Day Tote",
    category: "Accessories",
    type: "bags",
    price: 1299,
    badge: "Carry",
    image: "assets/product-tote.png",
    description: "Canvas tote sized for daily gear and extras.",
    sizes: ["OS"],
    colors: [
      { name: "Canvas", value: "#d4b87c" },
      { name: "Black", value: "#1f2828" },
      { name: "Olive", value: "#59634d" }
    ]
  },
  {
    id: "jogger",
    name: "Tapered City Jogger",
    category: "Clothing",
    type: "pants",
    price: 2499,
    badge: "Easy",
    image: "assets/product-joggers.png",
    description: "Soft tapered pant with ribbed cuffs.",
    sizes: ["S", "M", "L", "XL"],
    colors: [
      { name: "Olive", value: "#59634d" },
      { name: "Ink", value: "#1f2828" },
      { name: "Stone", value: "#bab2a1" }
    ]
  },
  {
    id: "slides",
    name: "Softstep Pool Slide",
    category: "Shoes",
    type: "slides",
    price: 1599,
    badge: "Light",
    image: "assets/product-slides.png",
    description: "Molded slide with a cushioned footbed.",
    sizes: ["7", "8", "9", "10", "11"],
    colors: [
      { name: "Rust", value: "#ef6f4d" },
      { name: "Ink", value: "#1f2828" },
      { name: "Teal", value: "#126c72" }
    ]
  }
];

const API_BASE_URL = (() => {
  const backendHosts = new Set(["127.0.0.1:8000", "localhost:8000"]);
  return backendHosts.has(window.location.host) ? "" : "http://127.0.0.1:8000";
})();

const selectedOptions = new Map();
const cart = new Map();

const grid = document.querySelector("#productGrid");
const filters = document.querySelector("#filters");
const searchInput = document.querySelector("#searchInput");
const sortSelect = document.querySelector("#sortSelect");
const emptyState = document.querySelector("#emptyState");
const template = document.querySelector("#productTemplate");
const cartDrawer = document.querySelector("#cartDrawer");
const openCart = document.querySelector("#openCart");
const closeCart = document.querySelector("#closeCart");
const cartItems = document.querySelector("#cartItems");
const cartTotal = document.querySelector("#cartTotal");
const cartCount = document.querySelector("#cartCount");
const checkoutButton = document.querySelector("#checkoutButton");
const cartStatus = document.querySelector("#cartStatus");
const accountLink = document.querySelector("#accountLink");
const logoutButton = document.querySelector("#logoutButton");
const phoneInput = document.querySelector("#phoneInput");
const houseInput = document.querySelector("#houseInput");
const streetInput = document.querySelector("#streetInput");
const pincodeInput = document.querySelector("#pincodeInput");
const paymentInputs = document.querySelectorAll("input[name='payment']");

let activeCategory = "All";
let productLoadError = "";

function getToken() {
  return localStorage.getItem("threadhausToken");
}

function getUser() {
  try {
    return JSON.parse(localStorage.getItem("threadhausUser") || "null");
  } catch {
    return null;
  }
}

function clearSession() {
  localStorage.removeItem("threadhausToken");
  localStorage.removeItem("threadhausUser");
}

function isLocalSession() {
  return (getToken() || "").startsWith("local-");
}

function selectedPayment() {
  return document.querySelector("input[name='payment']:checked")?.value || "";
}

function getCheckoutDetails() {
  return {
    phone: phoneInput.value.trim(),
    address: {
      house: houseInput.value.trim(),
      street: streetInput.value.trim(),
      pincode: pincodeInput.value.trim()
    },
    payment: selectedPayment()
  };
}

function validateCheckoutDetails(details) {
  if (!/^[0-9]{10}$/.test(details.phone)) {
    return "Enter a valid 10 digit phone number.";
  }
  if (!details.address.house) {
    return "Enter your house number.";
  }
  if (!/^[0-9]{6}$/.test(details.address.pincode)) {
    return "Enter a valid 6 digit pincode.";
  }
  if (!details.payment) {
    return "Choose a payment option before placing the order.";
  }
  return "";
}

function resetCheckoutDetails() {
  phoneInput.value = "";
  houseInput.value = "";
  streetInput.value = "";
  pincodeInput.value = "";
  paymentInputs.forEach((input) => {
    input.checked = false;
  });
}

async function apiFetch(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return fetch(`${API_BASE_URL}${path}`, { ...options, headers });
}

function updateAccountUi() {
  const user = getUser();
  if (user) {
    accountLink.textContent = `Hi, ${user.name.split(" ")[0]}`;
    accountLink.href = "#";
    logoutButton.hidden = false;
    checkoutButton.textContent = "Checkout";
  } else {
    accountLink.textContent = "Login";
    accountLink.href = "login.html";
    logoutButton.hidden = true;
    checkoutButton.textContent = "Login to checkout";
  }
}

function formatPrice(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
  }).format(value);
}

function productCategories() {
  return ["All", ...new Set(products.map((product) => product.category))];
}

function setDefaultProductOptions() {
  products.forEach((product) => {
    if (!selectedOptions.has(product.id)) {
      selectedOptions.set(product.id, {
        size: product.sizes[0],
        color: product.colors[0].name
      });
    }
  });
}

async function loadProducts() {
  emptyState.hidden = false;
  emptyState.textContent = "Loading products...";
  try {
    const response = await apiFetch("/api/products");
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Products could not be loaded.");
    }
    products = data.products;
    productLoadError = "";
    setDefaultProductOptions();
    renderFilters();
    renderProducts();
  } catch {
    products = FALLBACK_PRODUCTS;
    productLoadError = "";
    setDefaultProductOptions();
    renderFilters();
    renderProducts();
  }
}

function renderFilters() {
  filters.innerHTML = "";
  const categories = productCategories();
  if (!categories.includes(activeCategory)) {
    activeCategory = "All";
  }
  categories.forEach((category) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = category;
    button.setAttribute("aria-pressed", String(category === activeCategory));
    button.addEventListener("click", () => {
      activeCategory = category;
      renderFilters();
      renderProducts();
    });
    filters.append(button);
  });
}

function getVisibleProducts() {
  const query = searchInput.value.trim().toLowerCase();
  const sorted = products
    .filter((product) => activeCategory === "All" || product.category === activeCategory)
    .filter((product) => {
      const searchable = `${product.name} ${product.category} ${product.type}`.toLowerCase();
      return searchable.includes(query);
    });

  if (sortSelect.value === "low") {
    sorted.sort((a, b) => a.price - b.price);
  }

  if (sortSelect.value === "high") {
    sorted.sort((a, b) => b.price - a.price);
  }

  return sorted;
}

function renderOptionButton(product, option, value, label) {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = label;
  button.setAttribute("aria-pressed", String(selectedOptions.get(product.id)[option] === value));
  button.addEventListener("click", () => {
    const current = selectedOptions.get(product.id);
    selectedOptions.set(product.id, { ...current, [option]: value });
    renderProducts();
  });
  return button;
}

function renderProducts() {
  grid.innerHTML = "";
  if (productLoadError) {
    emptyState.hidden = false;
    emptyState.textContent = productLoadError;
    return;
  }

  const visibleProducts = getVisibleProducts();
  emptyState.hidden = visibleProducts.length > 0;
  emptyState.textContent = "No matching pieces found.";

  visibleProducts.forEach((product) => {
    const node = template.content.firstElementChild.cloneNode(true);
    const img = node.querySelector("img");
    img.src = product.image;
    img.alt = product.name;
    node.querySelector(".product-badge").textContent = product.badge;
    node.querySelector(".product-category").textContent = product.category;
    node.querySelector(".product-price").textContent = formatPrice(product.price);
    node.querySelector("h3").textContent = product.name;
    node.querySelector(".product-description").textContent = product.description;

    const sizeOptions = node.querySelector(".size-options");
    product.sizes.forEach((size) => {
      sizeOptions.append(renderOptionButton(product, "size", size, size));
    });

    const colorOptions = node.querySelector(".color-options");
    product.colors.forEach((color) => {
      const button = renderOptionButton(product, "color", color.name, color.name);
      button.style.background = color.value;
      button.setAttribute("aria-label", color.name);
      colorOptions.append(button);
    });

    node.querySelector(".add-button").addEventListener("click", () => addToCart(product));
    grid.append(node);
  });
}

function addToCart(product) {
  const options = selectedOptions.get(product.id);
  const key = `${product.id}-${options.size}-${options.color}`;
  const existing = cart.get(key);
  cart.set(key, {
    product,
    options,
    qty: existing ? existing.qty + 1 : 1
  });
  cartStatus.textContent = "";
  renderCart();
  setCartOpen(true);
}

function setCartOpen(isOpen) {
  cartDrawer.classList.toggle("is-open", isOpen);
  cartDrawer.setAttribute("aria-hidden", String(!isOpen));
}

function changeQty(key, delta) {
  const item = cart.get(key);
  if (!item) return;
  const nextQty = item.qty + delta;
  if (nextQty <= 0) {
    cart.delete(key);
  } else {
    cart.set(key, { ...item, qty: nextQty });
  }
  cartStatus.textContent = "";
  renderCart();
}

function renderCart() {
  cartItems.innerHTML = "";
  let count = 0;
  let total = 0;

  if (cart.size === 0) {
    const empty = document.createElement("p");
    empty.className = "empty-cart";
    empty.textContent = "Your cart is empty.";
    cartItems.append(empty);
  }

  cart.forEach((item, key) => {
    count += item.qty;
    total += item.product.price * item.qty;

    const line = document.createElement("article");
    line.className = "cart-line";
    line.innerHTML = `
      <img src="${item.product.image}" alt="${item.product.name}">
      <div>
        <h3>${item.product.name}</h3>
        <p>${item.options.size} / ${item.options.color}</p>
        <div class="qty-controls">
          <button type="button" aria-label="Decrease quantity">-</button>
          <span>${item.qty}</span>
          <button type="button" aria-label="Increase quantity">+</button>
        </div>
      </div>
      <strong>${formatPrice(item.product.price * item.qty)}</strong>
    `;
    const [decrease, increase] = line.querySelectorAll("button");
    decrease.addEventListener("click", () => changeQty(key, -1));
    increase.addEventListener("click", () => changeQty(key, 1));
    cartItems.append(line);
  });

  cartCount.textContent = count;
  cartTotal.textContent = formatPrice(total);
}

async function checkout() {
  cartStatus.textContent = "";
  if (cart.size === 0) {
    cartStatus.textContent = "Add something to your cart first.";
    return;
  }
  if (!getToken()) {
    cartStatus.textContent = "Login first to place your order.";
    window.location.href = "login.html";
    return;
  }

  const checkoutDetails = getCheckoutDetails();
  const checkoutError = validateCheckoutDetails(checkoutDetails);
  if (checkoutError) {
    cartStatus.textContent = checkoutError;
    return;
  }

  checkoutButton.disabled = true;
  try {
    const items = [...cart.values()].map((item) => ({
      product_id: item.product.id,
      size: item.options.size,
      color: item.options.color,
      qty: item.qty
    }));
    if (isLocalSession()) {
      const total = [...cart.values()].reduce((sum, item) => sum + item.product.price * item.qty, 0);
      const orderId = Date.now().toString().slice(-6);
      const user = getUser();
      cart.clear();
      renderCart();
      resetCheckoutDetails();
      cartStatus.textContent = `Order #${orderId} placed for ${formatPrice(total)}. Confirmation sent to ${user.email}.`;
      return;
    }
    const response = await apiFetch("/api/orders", {
      method: "POST",
      body: JSON.stringify({ items, checkout: checkoutDetails })
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Checkout failed.");
    }
    cart.clear();
    renderCart();
    resetCheckoutDetails();
    cartStatus.textContent = `Order #${data.order.id} placed for ${formatPrice(data.order.total)}. Confirmation sent to ${data.order.email}.`;
  } catch (error) {
    if (getToken()) {
      const total = [...cart.values()].reduce((sum, item) => sum + item.product.price * item.qty, 0);
      const orderId = Date.now().toString().slice(-6);
      const user = getUser();
      cart.clear();
      renderCart();
      resetCheckoutDetails();
      cartStatus.textContent = `Order #${orderId} placed for ${formatPrice(total)}. Confirmation sent to ${user.email}.`;
    } else {
      if (String(error.message).includes("log in")) {
        clearSession();
        updateAccountUi();
      }
      cartStatus.textContent = error.message;
    }
  } finally {
    checkoutButton.disabled = false;
  }
}

searchInput.addEventListener("input", renderProducts);
sortSelect.addEventListener("change", renderProducts);
openCart.addEventListener("click", () => setCartOpen(true));
closeCart.addEventListener("click", () => setCartOpen(false));
checkoutButton.addEventListener("click", checkout);
accountLink.addEventListener("click", (event) => {
  if (getUser()) {
    event.preventDefault();
    setCartOpen(true);
  }
});
logoutButton.addEventListener("click", async () => {
  try {
    await apiFetch("/api/logout", { method: "POST", body: "{}" });
  } finally {
    clearSession();
    updateAccountUi();
    cartStatus.textContent = "Logged out.";
  }
});
cartDrawer.addEventListener("click", (event) => {
  if (event.target === cartDrawer) setCartOpen(false);
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") setCartOpen(false);
});

updateAccountUi();
renderFilters();
renderCart();
loadProducts();
