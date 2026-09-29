// dashboard.js — Officer Dashboard page

const API_URL = "http://localhost:8000";
const AUTO_REFRESH_MS = 10000;

// Timestamps from the backend that have no timezone suffix (e.g. "2026-09-29T10:15:30")
// are treated as UTC and converted to the device's local time.
// If the times still look wrong, set this to false (backend stores local time).
const NAIVE_TIMESTAMPS_ARE_UTC = true;

const tbody = document.querySelector("#screeningTable tbody");
const emptyState = document.getElementById("emptyState");
const dashboardHint = document.getElementById("dashboardHint");
const refreshBtn = document.getElementById("refreshBtn");
const clearBtn = document.getElementById("clearBtn");

let isPaused = false;
let pendingApprovals = 0;

// Screenings approved in this session, so the button stays "Approved ✓"
// after the table re-renders on auto-refresh.
const approvedIds = new Set();

// Uses the device's own language, date order and timezone
const dateTimeFormatter = new Intl.DateTimeFormat(undefined, {
  dateStyle: "medium",
  timeStyle: "medium",
});

document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();
  refreshBtn.addEventListener("click", () => {
    isPaused = false;
    setHint("");
    loadDashboard();
  });
  clearBtn.addEventListener("click", clearTable);
  setInterval(() => {
    if (!isPaused) loadDashboard();
  }, AUTO_REFRESH_MS);
});

function setHint(message, isError = false) {
  dashboardHint.textContent = message;
  dashboardHint.style.color = isError ? "#dc2626" : "#6b7280";
}

// ---------- Date / time ----------

function formatDateTime(value) {
  if (!value) return "—";

  let text = String(value).trim().replace(" ", "T");
  text = text.replace(/(\.\d{3})\d+/, "$1"); // keep milliseconds only (Safari-safe)

  const hasZone = /(Z|[+-]\d{2}:?\d{2})$/i.test(text);
  if (!hasZone && NAIVE_TIMESTAMPS_ARE_UTC) text += "Z";

  const date = new Date(text);
  return Number.isNaN(date.getTime()) ? String(value) : dateTimeFormatter.format(date);
}

function prettyLabel(value) {
  return String(value ?? "").replaceAll("_", " ");
}

// ---------- Load ----------

async function loadDashboard() {
  if (isPaused || pendingApprovals > 0) return;

  try {
    const response = await fetch(`${API_URL}/dashboard/summary`);
    if (!response.ok) throw new Error(`Server responded with ${response.status}`);
    const data = await response.json();

    setText("total", data.total_screenings);
    setText("verified", data.verified);
    setText("manual", data.manual_review);
    setText("low", data.risk_distribution?.LOW);
    setText("medium", data.risk_distribution?.MEDIUM);
    setText("high", data.risk_distribution?.HIGH);

    renderTable(data.recent_screenings || []);
  } catch (error) {
    console.error(error);
    setHint("Couldn't load dashboard data. Check the backend connection.", true);
  }
}

function setText(id, value) {
  document.getElementById(id).textContent = value ?? 0;
}

// ---------- Table ----------

function renderTable(screenings) {
  tbody.innerHTML = "";
  emptyState.textContent = "No screenings recorded yet.";
  emptyState.hidden = screenings.length > 0;

  screenings.forEach(screening => {
    const row = document.createElement("tr");
    row.dataset.screeningId = screening.id;

    row.innerHTML = `
      <td>${escapeHtml(screening.full_name)}</td>
      <td>${escapeHtml(screening.passport_number)}</td>
      <td>${escapeHtml(screening.risk_level)}</td>
      <td>${escapeHtml(prettyLabel(screening.verification_status))}</td>
      <td class="decision-cell">${escapeHtml(prettyLabel(screening.final_decision))}</td>
      <td>${escapeHtml(formatDateTime(screening.screened_at))}</td>
    `;

    const actionCell = document.createElement("td");

    if (screening.final_decision === "MANUAL_REVIEW") {
      const btn = document.createElement("button");
      btn.className = "approve-btn";
      btn.textContent = "Approve";
      btn.addEventListener("click", () => approvePassenger(screening.id, row, btn));
      actionCell.appendChild(btn);
    } else if (approvedIds.has(screening.id)) {
      actionCell.appendChild(createApprovedButton());
    } else {
      actionCell.textContent = "—";
    }

    row.appendChild(actionCell);
    tbody.appendChild(row);
  });
}

function createApprovedButton() {
  const btn = document.createElement("button");
  btn.className = "approve-btn approved";
  btn.textContent = "Approved ✓";
  btn.disabled = true;
  return btn;
}

// ---------- Approve ----------

async function approvePassenger(screeningId, row, btn) {
  const originalLabel = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Approving…";
  pendingApprovals++;

  let approved = false;

  try {
    // Matches the backend route: PATCH /screening/{id}/decision
    const response = await fetch(`${API_URL}/screening/${screeningId}/decision`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision: "CLEARED" }),
    });

    const rawText = await response.text();
    let data = {};
    try { data = JSON.parse(rawText); } catch { /* non-JSON body, ignore */ }

    if (!response.ok) {
      let detail = data.detail ?? data.message;
      if (Array.isArray(detail)) detail = detail.map(d => d.msg || JSON.stringify(d)).join("; ");
      throw new Error(detail || `Approval failed (status ${response.status})`);
    }

    approved = true;
    approvedIds.add(screeningId);

    // Button becomes "Approved ✓" and stays that way
    btn.className = "approve-btn approved";
    btn.textContent = "Approved ✓";
    btn.disabled = true;

    const decisionCell = row.querySelector(".decision-cell");
    if (decisionCell) decisionCell.textContent = "CLEARED";

    setHint(`Screening #${screeningId} approved.`);
  } catch (error) {
    console.error("Approval error:", error);
    btn.disabled = false;
    btn.textContent = originalLabel;
    setHint(`Approval failed for #${screeningId}: ${error.message}`, true);
  } finally {
    pendingApprovals--;
  }

  // Refresh the summary numbers (the approved button is kept by approvedIds)
  if (approved) loadDashboard();
}


function clearTable() {
  isPaused = true;
  tbody.innerHTML = "";
  emptyState.textContent = "Table cleared — click Refresh to reload.";
  emptyState.hidden = false;
  setHint("Auto-refresh paused. Click Refresh to resume.");
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[ch]));
}
