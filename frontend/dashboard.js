const API_URL =
    "http://localhost:8000";

async function loadDashboard() {

    try {

        const response = await fetch(`${API_URL}/dashboard/summary`);

        const data =
            await response.json();

        document.getElementById(
            "total"
        ).textContent =
            data.total_screenings;

        document.getElementById(
            "verified"
        ).textContent =
            data.verified;

        document.getElementById(
            "manual"
        ).textContent =
            data.manual_review;

        document.getElementById(
            "low"
        ).textContent =
            data.risk_distribution.LOW;

        document.getElementById(
            "medium"
        ).textContent =
            data.risk_distribution.MEDIUM;

        document.getElementById(
            "high"
        ).textContent =
            data.risk_distribution.HIGH;

        const tbody =
            document.querySelector(
                "#screeningTable tbody"
            );

        tbody.innerHTML = "";

        data.recent_screenings.forEach(
            screening => {

                let actionButton = "";

                if (screening.final_decision === "MANUAL_REVIEW") {
                    actionButton = `
                        <button
                            class="approve-btn"
                            onclick="approvePassenger(${screening.id})">
                            Approve
                        </button>
                    `;
                }

                tbody.innerHTML += `
                    <tr>
                        <td>${screening.full_name}</td>
                        <td>${screening.passport_number}</td>
                        <td>${screening.risk_level}</td>
                        <td>${screening.verification_status}</td>
                        <td>${screening.final_decision}</td>
                        <td>${screening.screened_at}</td>
                        <td>${actionButton}</td>
                    </tr>
                `;
            }
        );

    } catch(error) {

        console.error(error);

    }
}

loadDashboard();

async function approvePassenger(screeningId) {

    try {

        const response = await fetch(
            `${API_URL}/approve-screening/${screeningId}`,
            {
                method: "PUT"
            }
        );

        const data = await response.json();

        alert(data.message);

        loadDashboard();

    } catch(error) {

        console.error(error);

        alert("Approval failed");

    }
}

setInterval(
    loadDashboard,
    10000
);