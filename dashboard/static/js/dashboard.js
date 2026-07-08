const replayButton = document.getElementById("replayButton");
const refreshButton = document.getElementById("refreshButton");
const statusMessage = document.getElementById("statusMessage");
const participantTable = document.getElementById("participantTable");

const interviewIdEl = document.getElementById("interviewId");
const candidateNameEl = document.getElementById("candidateName");
const interviewerNamesEl = document.getElementById("interviewerNames");
const participantCountEl = document.getElementById("participantCount");

const api = {
  interview: "/interview/",
  replay: "/replay/",
  predict: "/ml/predict",
};

function updateStatus(message) {
  statusMessage.textContent = message;
}

function statusBadge(text, severity = "info") {
  const prefix =
    severity === "success"
      ? "🟢 "
      : severity === "warning"
        ? "🟡 "
        : severity === "error"
          ? "🔴 "
          : "";

  updateStatus(`${prefix}${text}`);
}

function renderParticipants(participants) {
  participantTable.innerHTML = "";

  if (!participants.length) {
    participantTable.innerHTML =
      '<tr><td colspan="5" class="empty-state">No participants available.</td></tr>';
    return;
  }

  participants.forEach((item, index) => {
    const row = document.createElement("tr");
    const medals = ["🥇", "🥈", "🥉"];
    const medal = medals[index] || "";

    const confidenceClass =
      item.confidence >= 0.95
        ? "confidence-green"
        : item.confidence >= 0.7
          ? "confidence-blue"
          : item.confidence >= 0.5
            ? "confidence-orange"
            : "confidence-red";

    row.innerHTML = `
      <td><strong>${item.participant_id}</strong> ${medal ? `<span class="medal">${medal}</span>` : ""}</td>
      <td class="${confidenceClass}">${(item.confidence * 100).toFixed(1)}%</td>
      <td>${(item.model_probability * 100).toFixed(1)}%</td>
      <td>${item.evidence_count}</td>
      <td>${item.latest_reason || "—"}</td>
    `;

    participantTable.appendChild(row);
  });
}

async function loadInterview() {
  try {
    const response = await fetch(api.interview);
    if (!response.ok) {
      throw new Error("Interview request failed.");
    }

    const data = await response.json();
    interviewIdEl.textContent = data.interview_id || "—";
    candidateNameEl.textContent = data.candidate_name || "—";
    interviewerNamesEl.textContent = data.interviewer_names.join(", ") || "—";
    participantCountEl.textContent = data.participant_count?.toString() || "0";
  } catch (error) {
    updateStatus("Unable to load interview metadata.");
  }
}

async function loadPredictions() {
  try {
    const response = await fetch(api.predict);
    if (!response.ok) {
      throw new Error("Prediction request failed.");
    }

    const data = await response.json();
    const preds = data.predictions || [];

    renderParticipants(preds);

    // refresh interview metadata (participant count, names)
    await loadInterview();

    // ensure participant count matches predictions when available
    participantCountEl.textContent = (preds.length || 0).toString();

    statusBadge(
      `Latest results loaded (${preds.length} participants)`,
      "success",
    );
  } catch (error) {
    statusBadge("Unable to load model predictions.", "error");
  }
}

async function runReplay() {
  replayButton.disabled = true;
  refreshButton.disabled = true;
  replayButton.textContent = "Running...";
  statusBadge("Running replay...", "warning");

  try {
    const response = await fetch(api.replay, {
      method: "POST",
    });

    if (!response.ok) {
      throw new Error("Replay request failed.");
    }

    await response.json();
    await loadPredictions();
    statusBadge("Replay completed.", "success");
  } catch (error) {
    statusBadge("Replay failed.", "error");
  } finally {
    replayButton.disabled = false;
    refreshButton.disabled = false;
    replayButton.textContent = "Run Replay";
  }
}

replayButton.addEventListener("click", runReplay);
refreshButton.addEventListener("click", loadPredictions);

loadInterview();
loadPredictions();
