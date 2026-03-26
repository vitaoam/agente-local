const messagesEl = document.getElementById("messages");
const confirmationBar = document.getElementById("confirmation-bar");
const confirmationText = document.getElementById("confirmation-text");
const userInput = document.getElementById("user-input");
const btnSend = document.getElementById("btn-send");
const chatForm = document.getElementById("chat-form");

let pendingActionId = null;

function addMessage(text, type) {
    const div = document.createElement("div");
    div.className = "message " + type;
    div.textContent = text;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function showLoading() {
    const div = document.createElement("div");
    div.className = "loading";
    div.id = "loading-indicator";
    div.innerHTML = "<span></span><span></span><span></span>";
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function hideLoading() {
    const el = document.getElementById("loading-indicator");
    if (el) el.remove();
}

function showConfirmation(message, actionId) {
    pendingActionId = actionId;
    confirmationText.textContent = "Aguardando confirmação...";
    confirmationBar.classList.remove("hidden");
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function hideConfirmation() {
    pendingActionId = null;
    confirmationBar.classList.add("hidden");
}

function setInputEnabled(enabled) {
    userInput.disabled = !enabled;
    btnSend.disabled = !enabled;
}

function handleResponse(data) {
    if (data.type === "confirmation") {
        addMessage(data.message, "confirmation");
        showConfirmation(data.message, data.action_id);
    } else if (data.type === "error") {
        addMessage(data.message, "error");
    } else {
        addMessage(data.message, "agent");
    }
}

async function sendMessage(event) {
    event.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    addMessage(message, "user");
    userInput.value = "";
    setInputEnabled(false);
    showLoading();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message }),
        });
        const data = await response.json();
        hideLoading();
        handleResponse(data);
    } catch (err) {
        hideLoading();
        addMessage("Erro de conexão com o servidor.", "error");
    }

    setInputEnabled(true);
    userInput.focus();
}

async function confirmAction() {
    if (!pendingActionId) return;
    const actionId = pendingActionId;

    hideConfirmation();
    addMessage("Sim, confirmo.", "user");
    setInputEnabled(false);
    showLoading();

    try {
        const response = await fetch("/confirm", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action_id: actionId }),
        });
        const data = await response.json();
        hideLoading();
        handleResponse(data);
    } catch (err) {
        hideLoading();
        addMessage("Erro ao confirmar ação.", "error");
    }

    setInputEnabled(true);
    userInput.focus();
}

async function cancelAction() {
    if (!pendingActionId) return;
    const actionId = pendingActionId;

    hideConfirmation();
    addMessage("Não, cancelar.", "user");
    setInputEnabled(false);
    showLoading();

    try {
        const response = await fetch("/cancel", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action_id: actionId }),
        });
        const data = await response.json();
        hideLoading();
        handleResponse(data);
    } catch (err) {
        hideLoading();
        addMessage("Erro ao cancelar ação.", "error");
    }

    setInputEnabled(true);
    userInput.focus();
}

chatForm.addEventListener("submit", sendMessage);
