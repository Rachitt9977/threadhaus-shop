const form = document.querySelector("#authForm");
const nameField = document.querySelector("#nameField");
const nameInput = document.querySelector("#nameInput");
const emailInput = document.querySelector("#emailInput");
const passwordInput = document.querySelector("#passwordInput");
const authTitle = document.querySelector("#authTitle");
const authSubmit = document.querySelector("#authSubmit");
const authStatus = document.querySelector("#authStatus");
const tabs = document.querySelectorAll(".auth-tab");

const API_BASE_URL = (() => {
  const backendHosts = new Set(["127.0.0.1:8000", "localhost:8000"]);
  return backendHosts.has(window.location.host) ? "" : "http://127.0.0.1:8000";
})();

let mode = "login";

function readLocalUsers() {
  try {
    return JSON.parse(localStorage.getItem("threadhausLocalUsers") || "[]");
  } catch {
    return [];
  }
}

function saveLocalUsers(users) {
  localStorage.setItem("threadhausLocalUsers", JSON.stringify(users));
}

function createLocalSession(user) {
  localStorage.setItem("threadhausToken", `local-${Date.now()}`);
  localStorage.setItem("threadhausUser", JSON.stringify(user));
}

function localAuth(payload) {
  const email = payload.email.toLowerCase();
  const users = readLocalUsers();

  if (mode === "register") {
    if (!payload.name) {
      throw new Error("Name is required.");
    }
    if (users.some((user) => user.email === email)) {
      throw new Error("That email is already registered.");
    }
    const user = {
      id: Date.now(),
      name: payload.name,
      email,
      password: payload.password
    };
    users.push(user);
    saveLocalUsers(users);
    createLocalSession({ id: user.id, name: user.name, email: user.email });
    return;
  }

  const user = users.find((item) => item.email === email && item.password === payload.password);
  if (!user) {
    throw new Error("Email or password is incorrect. Create an account first if you are new.");
  }
  createLocalSession({ id: user.id, name: user.name, email: user.email });
}

function setMode(nextMode) {
  mode = nextMode;
  const isRegister = mode === "register";
  authTitle.textContent = isRegister ? "Create account" : "Login";
  authSubmit.textContent = isRegister ? "Create account" : "Login";
  nameField.hidden = !isRegister;
  nameInput.required = isRegister;
  passwordInput.autocomplete = isRegister ? "new-password" : "current-password";
  authStatus.textContent = "";
  tabs.forEach((tab) => tab.classList.toggle("is-active", tab.dataset.mode === mode));
}

async function submitAuth(event) {
  event.preventDefault();
  authStatus.textContent = "";
  authSubmit.disabled = true;
  const payload = {
    email: emailInput.value.trim(),
    password: passwordInput.value
  };
  if (mode === "register") {
    payload.name = nameInput.value.trim();
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/${mode}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Something went wrong.");
    }
    localStorage.setItem("threadhausToken", data.token);
    localStorage.setItem("threadhausUser", JSON.stringify(data.user));
    authStatus.textContent = "Signed in. Taking you back to the shop.";
    window.location.href = "index.html";
  } catch (error) {
    try {
      localAuth(payload);
      authStatus.textContent = "Signed in. Taking you back to the shop.";
      window.location.href = "index.html";
    } catch (localError) {
      authStatus.textContent = localError.message || error.message;
    }
  } finally {
    authSubmit.disabled = false;
  }
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => setMode(tab.dataset.mode));
});
form.addEventListener("submit", submitAuth);
setMode("login");
