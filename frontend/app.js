const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const captureBtn = document.getElementById("captureBtn");
const screenBtn = document.getElementById("screenBtn");
const preview = document.getElementById("preview");
const resultDiv = document.getElementById("result");

let capturedImage = null;

// Start Webcam
async function startCamera() {

    try {

        const stream =
            await navigator.mediaDevices.getUserMedia({
                video: true
            });

        video.srcObject = stream;

    } catch (error) {

        alert("Unable to access camera");

        console.error(error);
    }
}

startCamera();


// Capture Image
captureBtn.addEventListener("click", () => {

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");

    ctx.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );

    capturedImage =
        canvas.toDataURL("image/jpeg");

    preview.src = capturedImage;
    preview.style.display = "block";
});


// Screen Passenger
screenBtn.addEventListener("click", async () => {

    const passportNumber =
        document
        .getElementById("passportNumber")
        .value
        .trim();

    if (!passportNumber) {

        alert("Enter passport number");

        return;
    }

    if (!capturedImage) {

        alert("Capture image first");

        return;
    }

    resultDiv.innerHTML =
        "<p>Screening in progress...</p>";

    try {

        const response =
            await fetch(
                "http://localhost:8000/screen",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        passport_number:
                            passportNumber,

                        face_image:
                            capturedImage

                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Screening failed"
            );
        }

        displayResult(data.result);

    } catch (error) {

        resultDiv.innerHTML = `
            <p style="color:red;">
                ${error.message}
            </p>
        `;
    }
});


// Display Result
function displayResult(result) {

    const riskClass =
        result.risk_level.toLowerCase();

    const verifyClass =
        result.verification_status === "VERIFIED"
        ? "verified"
        : "not-verified";

    let reasonsHTML = "";

    if (
        result.reasons &&
        result.reasons.length > 0
    ) {

        reasonsHTML =
            "<ul>" +
            result.reasons
            .map(reason =>
                `<li>${reason}</li>`
            )
            .join("") +
            "</ul>";

    } else {

        reasonsHTML =
            "<p>No risk indicators found.</p>";
    }

    resultDiv.innerHTML = `
        <div class="result-card">

            <p>
                <strong>Name:</strong>
                ${result.full_name}
            </p>

            <p>
                <strong>Passport:</strong>
                ${result.passport_number}
            </p>

            <p>
                <strong>Similarity:</strong>
                ${result.similarity_score}
            </p>

            <p>
                <strong>Verification:</strong>
                <span class="${verifyClass}">
                    ${result.verification_status}
                </span>
            </p>

            <p>
                <strong>Risk Score:</strong>
                ${result.risk_score}
            </p>

            <p>
                <strong>Risk Level:</strong>
                <span class="${riskClass}">
                    ${result.risk_level}
                </span>
            </p>

            <p>
                <strong>Assigned Lane:</strong>
                ${result.assigned_lane}
            </p>

            <p>
                <strong>Decision:</strong>
                ${result.final_decision}
            </p>

            <h4>Reasons</h4>

            ${reasonsHTML}

        </div>
    `;
}