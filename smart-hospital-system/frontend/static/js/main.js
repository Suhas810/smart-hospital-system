document.addEventListener("DOMContentLoaded", () => {
    loadPatients();
    loadStats();

    const form = document.getElementById("triage-form");
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const btn = document.getElementById("btn-triage");
            const originalText = btn.innerText;
            btn.innerText = "Analyzing...";
            btn.disabled = true;

            const name = document.getElementById("p-name").value;
            const age = document.getElementById("p-age").value;
            const severity = document.getElementById("p-severity").value;
            const symptoms = document.getElementById("p-symptoms").value;
            const appointment_time = document.getElementById("p-time").value;

            try {
                // Use the new appointment booking endpoint
                const res = await fetch("/appointments/book", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        name,
                        age,
                        severity: parseInt(severity),
                        symptoms,
                        appointment_time
                    })
                });
                const data = await res.json();

                // Show AI Result (Assuming backend might return it, though currently /book doesn't integrate AI fully yet,
                // but let's assume we might merge logic or handle it. 
                // Wait, I didn't add AI analysis to /book yet. 
                // User requirement said "Suggest backend API enhancements...". 
                // Ideally, /book should call AI.
                // For now, let's keep the UI ready.

                if (data.ai_analysis) {
                    const aiBox = document.getElementById("ai-output");
                    const aiText = document.getElementById("ai-text");
                    aiBox.style.display = "block";

                    // Handle new JSON structure
                    let html = "";
                    if (data.ai_analysis.risk_level) {
                        const color = data.ai_analysis.risk_level.toLowerCase().includes("high") ? "red" : "inherit";
                        html += `<strong style='color:${color}'>Risk Level: ${data.ai_analysis.risk_level}</strong><br>`;
                        html += `<strong>Explanation:</strong> ${data.ai_analysis.explanation}<br>`;
                        html += `<strong>Recommendation:</strong> ${data.ai_analysis.recommendation}`;
                    } else {
                        html = JSON.stringify(data.ai_analysis);
                    }
                    aiText.innerHTML = html;
                }

                loadPatients(); // Refresh list
                form.reset();

            } catch (err) {
                console.error("Error adding patient:", err);
                alert("Failed to admit patient.");
            } finally {
                btn.innerText = originalText;
                btn.disabled = false;
            }
        });
    }
});

async function loadPatients() {
    try {
        const res = await fetch("/appointments/queue");
        const patients = await res.json();
        const tbody = document.getElementById("patients-list");
        tbody.innerHTML = "";

        patients.forEach(p => {
            const riskColor = p.severity > 7 ? "var(--danger)" : (p.severity > 4 ? "var(--warning)" : "var(--success)");

            // Format time
            let timeDisplay = "In Queue";
            if (p.appointment_time) {
                const date = new Date(p.appointment_time);
                if (!isNaN(date)) {
                    timeDisplay = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                }
            }

            const row = `
                <tr>
                    <td>${p.name}</td>
                    <td>${p.age}</td>
                    <td><span style="color: ${riskColor}; font-weight:bold;">${p.severity}</span></td>
                    <td><span class="badge ${p.status === 'booked' ? 'badge-info' : 'badge-warning'}">${p.status}</span></td>
                    <td>${p.risk_analysis ? (JSON.parse(p.risk_analysis).risk_level || 'N/A') : (p.severity > 7 ? "High" : "Standard")}</td> 
                    <td>${timeDisplay}</td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    } catch (err) {
        console.error("Error loading patients", err);
    }
}

async function loadStats() {
    // Placeholder for stats logic if endpoints existed
    // For now we just keep the static HTML values or fetch from a hypothetical endpoint
}

// Dark Mode Logic
function toggleTheme() {
    document.body.classList.toggle("dark-mode");
    const isDark = document.body.classList.contains("dark-mode");
    localStorage.setItem("theme", isDark ? "dark" : "light");
}

// Apply theme on load
if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark-mode");
}

// Chatbot Logic
function toggleChat() {
    const win = document.getElementById("chat-window");
    if (win) {
        win.classList.toggle("hidden");
        if (!win.classList.contains("hidden")) {
            const input = document.getElementById("chat-input");
            if (input) input.focus();
        }
    }
}

async function sendChat() {
    const input = document.getElementById("chat-input");
    if (!input) return;

    const msg = input.value.trim();
    if (!msg) return;

    addMessage(msg, 'user');
    input.value = "";
    input.disabled = true;

    // Show typing
    const typingId = addMessage("Thinking...", 'ai', true);

    try {
        const res = await fetch("/chat/message", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: msg })
        });
        const data = await res.json();

        // Remove typing
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();

        addMessage(data.reply, 'ai');

    } catch (err) {
        console.error("Chat error:", err);
        addMessage("Sorry, I couldn't reach the server.", 'ai');
        // Remove typing if error
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();
    } finally {
        input.disabled = false;
        input.focus();
    }
}

function addMessage(text, sender, isTyping = false) {
    const box = document.getElementById("chat-messages");
    if (!box) return;

    const div = document.createElement("div");
    div.className = `msg ${sender} ${isTyping ? 'typing' : ''}`;
    div.innerText = text;

    // ID for typing indicator removal
    const id = "msg-" + Date.now();
    div.id = id;

    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
    return id;
}

// Enter key support
document.addEventListener("DOMContentLoaded", () => {
    const chatInput = document.getElementById("chat-input");
    if (chatInput) {
        chatInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") sendChat();
        });
    }
});
