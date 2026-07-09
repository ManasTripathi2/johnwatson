const replayButton = document.getElementById("replayButton");
const refreshButton = document.getElementById("refreshButton");
const statusMessage = document.getElementById("statusMessage");
const participantTable = document.getElementById("participantTable");

const interviewIdEl = document.getElementById("interviewId");
const candidateNameEl = document.getElementById("candidateName");
const interviewerNamesEl = document.getElementById("interviewerNames");
const participantCountEl = document.getElementById("participantCount");

const leadNameEl = document.getElementById("leadName");
const leadMetaEl = document.getElementById("leadMeta");
const leadBadgeEl = document.getElementById("leadBadge");
const leadBarEl = document.getElementById("leadBar");
const leadConfidenceEl = document.getElementById("leadConfidence");
const leadModelEl = document.getElementById("leadModel");
const leadEvidenceEl = document.getElementById("leadEvidence");

const api = {
  interview: "/interview/",
  replay: "/replay/",
  predict: "/ml/predict",
};

const statusDot = document.createElement("span");
const statusLabel = document.createElement("span");
statusDot.className = "run-dot";
statusLabel.textContent = "Ready";
statusMessage.replaceChildren(statusDot, statusLabel);

function setStatus(message, severity = "info") {
  statusMessage.className = "run-state";

  if (severity !== "info") {
    statusMessage.classList.add(`is-${severity}`);
  }

  statusLabel.textContent = message;
}

function setText(element, value, fallback = "-") {
  element.textContent = value || fallback;
}

function formatPercent(value) {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "-";
  }

  return `${(value * 100).toFixed(1)}%`;
}

function scoreTone(value) {
  if (value >= 0.82) {
    return "strong";
  }

  if (value >= 0.55) {
    return "watch";
  }

  return "risk";
}

function participantName(item) {
  return item.display_name || item.participant_id || "Unknown participant";
}

function createCell(className) {
  const cell = document.createElement("td");

  if (className) {
    cell.className = className;
  }

  return cell;
}

function renderScore(value) {
  const wrapper = document.createElement("div");
  const label = document.createElement("div");
  const percent = document.createElement("span");
  const track = document.createElement("div");
  const bar = document.createElement("div");
  const tone = scoreTone(value);

  wrapper.className = "score-cell";
  label.className = "score-label";
  track.className = "score-track";
  bar.className = `score-bar is-${tone}`;
  bar.style.width = `${Math.max(0, Math.min(value || 0, 1)) * 100}%`;

  percent.textContent = formatPercent(value);
  label.append(percent);
  track.append(bar);
  wrapper.append(label, track);

  return wrapper;
}

function renderParticipantIdentity(item) {
  const wrapper = document.createElement("div");
  const name = document.createElement("span");
  const id = document.createElement("span");
  const note = document.createElement("span");

  name.className = "participant-name";
  id.className = "participant-id";
  note.className = "participant-note";
  name.textContent = participantName(item);
  id.textContent = item.participant_id || "-";
  note.textContent = item.latest_reason || "";

  wrapper.append(name, id);

  if (item.latest_reason) {
    wrapper.append(note);
  }

  return wrapper;
}

function renderLead(participants) {
  const lead = participants[0];

  if (!lead) {
    leadNameEl.textContent = "No candidate selected";
    leadMetaEl.textContent = "Run the replay to populate participant evidence.";
    leadBadgeEl.textContent = "waiting";
    leadBadgeEl.className = "lead-badge";
    leadBarEl.style.width = "0%";
    leadConfidenceEl.textContent = "-";
    leadModelEl.textContent = "-";
    leadEvidenceEl.textContent = "-";
    return;
  }

  const tone = scoreTone(lead.confidence);

  leadNameEl.textContent = participantName(lead);
  leadMetaEl.textContent = `${lead.participant_id} is ranked first after ${lead.evidence_count} evidence updates.`;
  leadBadgeEl.textContent =
    tone === "strong" ? "high confidence" : tone === "watch" ? "review" : "weak signal";
  leadBadgeEl.className = `lead-badge is-${tone}`;
  leadBarEl.style.width = `${Math.max(0, Math.min(lead.confidence || 0, 1)) * 100}%`;
  leadConfidenceEl.textContent = formatPercent(lead.confidence);
  leadModelEl.textContent = formatPercent(lead.model_probability);
  leadEvidenceEl.textContent = String(lead.evidence_count || 0);
}

function renderParticipants(participants) {
  participantTable.replaceChildren();
  renderLead(participants);

  if (!participants.length) {
    const row = document.createElement("tr");
    const cell = createCell("empty-state");

    cell.colSpan = 5;
    cell.textContent = "No participants available.";
    row.append(cell);
    participantTable.append(row);
    return;
  }

  participants.forEach((item, index) => {
    const row = document.createElement("tr");
    const rankCell = createCell("rank");
    const participantCell = createCell();
    const confidenceCell = createCell();
    const modelCell = createCell();
    const evidenceCell = createCell("evidence-count");

    rankCell.textContent = String(index + 1).padStart(2, "0");
    participantCell.append(renderParticipantIdentity(item));
    confidenceCell.append(renderScore(item.confidence));
    modelCell.append(renderScore(item.model_probability));
    evidenceCell.textContent = String(item.evidence_count || 0);

    row.append(
      rankCell,
      participantCell,
      confidenceCell,
      modelCell,
      evidenceCell,
    );
    participantTable.append(row);
  });
}

async function loadInterview() {
  try {
    const response = await fetch(api.interview);

    if (!response.ok) {
      throw new Error("Interview request failed.");
    }

    const data = await response.json();
    setText(interviewIdEl, data.interview_id);
    setText(candidateNameEl, data.candidate_name);
    setText(interviewerNamesEl, (data.interviewer_names || []).join(", "));
    participantCountEl.textContent = String(data.participant_count || 0);
  } catch (error) {
    setStatus("Interview metadata unavailable", "error");
  }
}

async function loadPredictions() {
  try {
    const response = await fetch(api.predict);

    if (!response.ok) {
      throw new Error("Prediction request failed.");
    }

    const data = await response.json();
    const predictions = data.predictions || [];

    renderParticipants(predictions);
    await loadInterview();
    participantCountEl.textContent = String(predictions.length || 0);
    setStatus(`Loaded ${predictions.length} participant results`, "success");
  } catch (error) {
    renderParticipants([]);
    setStatus("Model predictions unavailable", "error");
  }
}

async function runReplay() {
  replayButton.disabled = true;
  refreshButton.disabled = true;
  replayButton.textContent = "Running";
  setStatus("Running replay", "warning");

  try {
    const response = await fetch(api.replay, {
      method: "POST",
    });

    if (!response.ok) {
      throw new Error("Replay request failed.");
    }

    await response.json();
    await loadPredictions();
    setStatus("Replay complete", "success");
  } catch (error) {
    setStatus("Replay failed", "error");
  } finally {
    replayButton.disabled = false;
    refreshButton.disabled = false;
    replayButton.textContent = "Run replay";
  }
}

replayButton.addEventListener("click", runReplay);
refreshButton.addEventListener("click", loadPredictions);

loadInterview();
loadPredictions();
