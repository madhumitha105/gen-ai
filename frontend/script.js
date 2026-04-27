//address for the fastAPI server
const API_URL = "http://127.0.0.1:8000/chat";

//setup session id to keep track of chat history
let session_id = localStorage.getItem("session_id");
if (!session_id) {
    session_id = Math.random().toString(36).substring(2);
    localStorage.setItem("session_id", session_id);
}

//collect all data from the form and send to backend
async function generatePlan() {
    const source = document.getElementById("source").value;
    const destination = document.getElementById("destination").value;
    const travel_date = document.getElementById("travel_date").value;
    const adults = document.getElementById("adults").value;
    const children = document.getElementById("children").value;
    const budget = document.getElementById("budget").value;
    const days = document.getElementById("days").value;
    const food = document.getElementById("food").value;
    const specs = document.getElementById("specs").value;

    document.getElementById("output").innerHTML = "Generating your itinerary...";

    //sending structured data so backend knows it is a new plan request
    const res = await fetch(API_URL, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            session_id: session_id,
            source: source,
            destination: destination,
            travel_date: travel_date,
            adults: parseInt(adults),
            children: parseInt(children),
            budget: budget,
            days: days,
            food_pref: food,
            specs: specs
        })
    });

    const data = await res.json();
    document.getElementById("output").innerHTML = formatResponse(data.response || data.error);
}

//displaying message in the chat box
function addChat(text, cls) {
    const box = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = cls;

    div.innerHTML = formatResponse(text);

    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

//sending a follow up message in the chat section
async function sendChat() {
    const input = document.getElementById("chat-input");
    const text = input.value;

    if (!text) return;

    addChat("You: " + text, "user");
    input.value = "";

    //standard chat call using user_input field
    const res = await fetch(API_URL, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            user_input: text,
            session_id: session_id
        })
    });

    const data = await res.json();
    addChat("AI: " + (data.response || data.error), "bot");
}

//making links clickable and handling line breaks
function formatResponse(text) {
    if (!text) return "";
    text = text.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
    text = text.replace(/\n/g, "<br>");
    return text;
}

//pressing enter sends the chat message
document.getElementById("chat-input").addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        sendChat();
    }
});

//automatically finding user location for source field
async function setDefaultSource() {
    try {
        const res = await fetch("https://ipapi.co/json/");
        const data = await res.json();

        if (!document.getElementById("source").value) {
            document.getElementById("source").value =
                `${data.city}, ${data.country_name}`;
        }
    } catch (e) {
        console.log("location fetch failed");
    }
}

setDefaultSource();