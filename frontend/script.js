const API_URL = "http://127.0.0.1:8000/chat";

let session_id = localStorage.getItem("session_id");
if (!session_id) {
    session_id = Math.random().toString(36).substring(2);
    localStorage.setItem("session_id", session_id);
}

// collect form data and call backend
async function generatePlan() {
    const source = document.getElementById("source").value;
    const destination = document.getElementById("destination").value;
    const travelers = document.getElementById("travelers").value;
    const budget = document.getElementById("budget").value;
    const days = document.getElementById("days").value;
    const food = document.getElementById("food").value;
    const specs = document.getElementById("specs").value;

    const query = `
Source: ${source}
Destination: ${destination}
Travelers: ${travelers}
Duration: ${days} days
Budget: ${budget}
Food Preference: ${food}
Preferences: ${specs}
`;

    document.getElementById("output").innerHTML = "Generating...";

    const res = await fetch(API_URL, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            user_input: query,
            session_id: session_id
        })
    });

    const data = await res.json();

    document.getElementById("output").innerHTML = formatResponse(data.response);
}

// add message into chat UI
function addChat(text, cls) {
    const box = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = cls;

    div.innerHTML = formatResponse(text);

    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

// send chat message
async function sendChat() {
    const input = document.getElementById("chat-input");
    const text = input.value;

    if (!text) return;

    addChat("You: " + text, "user");
    input.value = "";

    const res = await fetch(API_URL, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            user_input: text,
            session_id: session_id
        })
    });

    const data = await res.json();

    addChat("JujupiJourney: " + data.response, "bot");
}

// convert markdown links to clickable links
function formatResponse(text) {
    text = text.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
    text = text.replace(/\n/g, "<br>");
    return text;
}

// allow enter key to send message
document.getElementById("chat-input").addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        sendChat();
    }
});

// auto-detect user location and set source
async function setDefaultSource() {
    try {
        const res = await fetch("https://ipapi.co/json/");
        const data = await res.json();

        if (!document.getElementById("source").value) {
            document.getElementById("source").value =
                `${data.city}, ${data.country_name}`;
        }
    } catch (e) {
        console.log("Location fetch failed");
    }
}

setDefaultSource();