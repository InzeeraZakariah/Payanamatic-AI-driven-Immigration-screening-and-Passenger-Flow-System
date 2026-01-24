// app.js

const BACKEND_SCREEN_URL = "http://localhost:8000/screen-through-n8n";
const BACKEND_RESULT_URL = "http://localhost:8000/get-result";
let capturedImage = null;

window.onload = () => {
    startCamera();
    loadDashboard();
};

function showTab(tabId) {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.getElementById(tabId).classList.add("active");
}

function startCamera() {
    const video = document.getElementById("video");
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => video.srcObject = stream)
        .catch(err => { alert("Camera access denied"); console.error(err); });
}

function capturePhoto() {
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
    capturedImage = canvas.toDataURL("image/jpeg");
    alert("Image captured");
}

async function screenPassenger() {
    const passport = document.getElementById("passport").value.trim();
    if (!passport) { alert("Enter passport"); return; }
    if (!capturedImage) { alert("Capture photo"); return; }

    try {
        const res = await fetch(BACKEND_SCREEN_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ passport_number: passport, face_image: capturedImage })
        });

        const result = await res.json();
        renderResult(result.result);
        updateLocalStats(result.result);
    } catch(err) {
        console.error(err);
        alert(err.message);
    }
}
function renderResult(res) {
    const card = document.getElementById("resultCard");
    const div = document.getElementById("result");
    card.style.display = "block";
    card.style.borderLeft = res.verification_status === "Verified Successfully" ? "6px solid green" : "6px solid red";
    div.innerHTML = `
        <p><strong>Passport:</strong> ${res.passport_number}</p>
        <p><strong>Name:</strong> ${res.full_name}</p>
        <p><strong>Risk Score:</strong> ${res.risk_score}</p>
        <p><strong>Risk Level:</strong> ${res.risk_level}</p>
        <p><strong>Assigned Lane:</strong> ${res.assigned_lane}</p>
        <p><strong>Status:</strong> ${res.verification_status}</p>
        <p><strong>Decision:</strong> ${res.final_decision || "N/A"}</p>
    `;
}

// --- Dashboard Stats ---
function updateLocalStats(result) {
    const stats = JSON.parse(localStorage.getItem("stats") || "{}");
    stats.total = (stats.total || 0) + 1;
    const lane = result.assigned_lane;
    if (lane === "FAST_LANE" || lane === "NORMAL_LANE") {
        stats.normal = (stats.normal || 0) + 1;
    } else if (lane === "ASSISTED_COUNTER" || lane === "RISK_LANE" || lane === "SECONDARY_SCREENING") {
        stats.risk = (stats.risk || 0) + 1;
    } else {
        stats.detain = (stats.detain || 0) + 1;
    }
    localStorage.setItem("stats", JSON.stringify(stats));
    loadDashboard();
}

function loadDashboard() {
    const stats = JSON.parse(localStorage.getItem("stats") || "{}");
    document.getElementById("total").innerText = stats.total || 0;
    document.getElementById("normal").innerText = stats.normal || 0;
    document.getElementById("risk").innerText = stats.risk || 0;
    document.getElementById("detain").innerText = stats.detain || 0;
}