"use strict";

const API_URL = "http://127.0.0.1:8000";
const SCREEN_URL = `${API_URL}/screen`;

const video = document.getElementById("video");
const preview = document.getElementById("preview");
const canvas = document.getElementById("canvas");
const cameraStatus = document.getElementById("cameraStatus");
const passportNumber = document.getElementById("passportNumber");
const passportHint = document.getElementById("passportHint");
const captureBtn = document.getElementById("captureBtn");
const retakeBtn = document.getElementById("retakeBtn");
const screenBtn = document.getElementById("screenBtn");
const resultCard = document.getElementById("resultCard");
const result = document.getElementById("result");


let cameraStream = null;
let capturedImage = null;
let isScreening = false;

// PAGE LOAD
document.addEventListener("DOMContentLoaded", () => {
    console.log("PAYANAMATIC APP.JS LOADED");

    captureBtn.addEventListener("click", capturePhoto);
    retakeBtn.addEventListener("click", retakePhoto);
    screenBtn.addEventListener("click", screenPassenger);

    startCamera();
});


async function startCamera() {
    setCameraStatus("Requesting camera access...");

    try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error("Camera API is not supported by this browser.");
        }

        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: "user" },
            audio: false
        });

        video.srcObject = cameraStream;
        await video.play();
        setCameraStatus(null);
        console.log("CAMERA STARTED");
    } catch (error) {
        console.error("CAMERA ERROR:", error);
        setCameraStatus("Camera unavailable. Please allow camera access.");
    }
}

function setCameraStatus(message) {
    if (!message) {
        cameraStatus.hidden = true;
        cameraStatus.textContent = "";
        return;
    }

    cameraStatus.textContent = message;
    cameraStatus.hidden = false;
}



function capturePhoto() {
    if (!cameraStream) {
        setCameraStatus("Camera is not ready yet.");
        return;
    }

    if (!video.videoWidth || !video.videoHeight) {
        setCameraStatus("Camera image is not ready yet.");
        return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);

    capturedImage = canvas.toDataURL("image/jpeg", 0.90);

    preview.src = capturedImage;
    preview.hidden = false;
    video.hidden = true;
    retakeBtn.hidden = false;

    passportHint.textContent = "";
    console.log("PHOTO CAPTURED");
}



function retakePhoto() {
    capturedImage = null;

    preview.src = "";
    preview.hidden = true;
    video.hidden = false;
    retakeBtn.hidden = true;

    clearResult();
}



async function screenPassenger() {
    if (isScreening) return;

    const passport = passportNumber.value.trim();
    passportHint.textContent = "";

    if (!passport) {
        passportHint.textContent = "Enter a passport number.";
        passportNumber.focus();
        return;
    }

    if (!capturedImage) {
        passportHint.textContent = "Capture a photo first.";
        return;
    }

    isScreening = true;
    screenBtn.disabled = true;
    captureBtn.disabled = true;
    retakeBtn.disabled = true;
    screenBtn.textContent = "Screening...";

    resultCard.classList.remove("success", "error");
    showLoading();

    try {
        const response = await fetch(SCREEN_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                passport_number: passport,
                face_image: capturedImage
            })
        });

        console.log("HTTP STATUS:", response.status);

        // ---------- HTTP ERROR ----------
        if (!response.ok) {
            let errorMessage = `Screening failed (HTTP ${response.status}).`;

            try {
                const errorData = await response.json();
                let detail = errorData.detail ?? errorData.message;

                // FastAPI 422 returns detail as an array of objects
                if (Array.isArray(detail)) {
                    detail = detail
                        .map(item => item.msg || JSON.stringify(item))
                        .join("; ");
                } else if (detail && typeof detail === "object") {
                    detail = JSON.stringify(detail);
                }

                errorMessage = detail || errorMessage;
            } catch (parseError) {
                console.error("ERROR RESPONSE PARSE FAILED:", parseError);
            }

            throw new Error(errorMessage);
        }

        // ---------- SUCCESS ----------
        const data = await response.json();
        console.log("BACKEND RESPONSE:", data);

        if (!data || !data.result) {
            throw new Error("Backend returned no screening result.");
        }

        displayResult(data.result);
    } catch (error) {
        console.error("SCREENING ERROR:", error);

        // fetch() throws a TypeError when the server is unreachable or CORS blocks it
        const message =
            error instanceof TypeError
                ? "Cannot reach the server. Check that the backend is running and CORS allows this page's address."
                : error.message;

        showError(message);
    } finally {
        isScreening = false;
        screenBtn.disabled = false;
        captureBtn.disabled = false;
        retakeBtn.disabled = false;
        screenBtn.textContent = "Screen Passenger";
    }
}


function showLoading() {
    result.innerHTML = `
        <div class="loading-result">
            <div class="loader"></div>
            <h3>Screening Passenger...</h3>
            <p>Verifying identity and calculating risk.</p>
            <p class="loading-note">Please wait...</p>
        </div>
    `;
}

function displayResult(data) {
    if (!data) {
        showError("No result received.");
        return;
    }

    const verification = data.verification_status || "-";
    const riskLevel = data.risk_level || "-";
    const finalDecision = data.final_decision || "-";

    const verified = verification === "VERIFIED";
    const cleared = finalDecision === "CLEARED";

    const reasons = Array.isArray(data.reasons) ? data.reasons : [];

    const reasonsHTML = reasons.length > 0
        ? `<ul class="reason-list">
               ${reasons.map(reason => `<li>${escapeHtml(reason)}</li>`).join("")}
           </ul>`
        : `<p class="no-reasons">No risk indicators found.</p>`;

    // Similarity as a percentage, e.g. 0.8234 -> 82.34%
    const similarity = Number(data.similarity_score);
    const similarityText = Number.isFinite(similarity)
        ? `${(similarity * 100).toFixed(2)}%`
        : "-";

    // Card colour follows the FINAL decision, not just face verification
    resultCard.classList.remove("success", "error");
    resultCard.classList.add(cleared ? "success" : "error");

    result.innerHTML = `
        <div class="final-result">

            <div class="result-header">
                <div>
                    <h3>Screening Completed</h3>
                    <p class="result-subtitle">
                        Screening ID: ${escapeHtml(data.screening_id)}
                    </p>
                </div>

                <span class="decision-badge decision-${escapeHtml(finalDecision.toLowerCase())}">
                    ${escapeHtml(finalDecision.replaceAll("_", " "))}
                </span>
            </div>

            <div class="result-grid">

                <div class="result-item">
                    <span>Name</span>
                    <strong>${escapeHtml(data.full_name)}</strong>
                </div>

                <div class="result-item">
                    <span>Passport</span>
                    <strong>${escapeHtml(data.passport_number)}</strong>
                </div>

                <div class="result-item">
                    <span>Gender</span>
                    <strong>${escapeHtml(data.gender)}</strong>
                </div>

                <div class="result-item">
                    <span>Nationality</span>
                    <strong>${escapeHtml(data.nationality)}</strong>
                </div>

                <div class="result-item">
                    <span>Face Similarity</span>
                    <strong>${escapeHtml(similarityText)}</strong>
                </div>

                <div class="result-item">
                    <span>Verification</span>
                    <strong class="${verified ? "verified" : "not-verified"}">
                        ${escapeHtml(verification.replaceAll("_", " "))}
                    </strong>
                </div>

                <div class="result-item">
                    <span>Risk Score</span>
                    <strong>${escapeHtml(data.risk_score)}</strong>
                </div>

                <div class="result-item">
                    <span>Risk Level</span>
                    <strong class="risk-${escapeHtml(riskLevel.toLowerCase())}">
                        ${escapeHtml(riskLevel)}
                    </strong>
                </div>

                <div class="result-item">
                    <span>Assigned Lane</span>
                    <strong>${escapeHtml(data.assigned_lane)}</strong>
                </div>

                <div class="result-item">
                    <span>Final Decision</span>
                    <strong>${escapeHtml(finalDecision.replaceAll("_", " "))}</strong>
                </div>

                <div class="result-item">
                    <span>Email Notification</span>
                    <strong>${data.email_sent ? "Sent" : "Not Sent"}</strong>
                </div>

            </div>

            <div class="risk-section">
                <h4>Risk Indicators</h4>
                ${reasonsHTML}
            </div>

        </div>
    `;

    setTimeout(() => {
        resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 50);
}



function showError(message) {
    resultCard.classList.remove("success");
    resultCard.classList.add("error");

    result.innerHTML = `
        <div class="error-result">
            <h3>Screening Error</h3>
            <p>${escapeHtml(message)}</p>
        </div>
    `;
}



function clearResult() {
    resultCard.classList.remove("success", "error");

    result.innerHTML = `
        <div class="empty-result">
            <p>Capture a photo and screen a passenger to see results here.</p>
        </div>
    `;
}


function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => {
        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        };
        return entities[character];
    });
}

window.addEventListener("beforeunload", () => {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
    }
});
