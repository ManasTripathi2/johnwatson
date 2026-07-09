# Dr. John Watson

**An AI system that answers one deceptively hard question: *who, in this room, is actually the candidate?***

> *"You know my method. It is founded upon the observation of trifles."*
> - Sherlock Holmes

Built for the **Sherlock** interview-fraud-detection platform, whose fraud detectors - deepfake detection, voice cloning, behavioral analysis - are only as good as their input. Point them at the wrong participant and you've built a very expensive way to fraud-check the interviewer. This is the piece that makes sure that never happens.

It's named John Watson on purpose, not Sherlock. Holmes gets the glory for leaps of genius; Watson is the one who actually shows up every time, writes down what he observed, dates the entry, and never claims more certainty than the evidence supports. That's the job description for this system, almost exactly. No leaps. No hunches. Just observation, written down, accumulated over time, and a clear account of *why* it believes what it believes.

---

## The Case

A candidate joins a live interview. In a perfect world they join as "Manas Tripathi," say their own name, and sit quietly until asked a question. In the world this actually has to work in:

- They join as **"MacBook Pro."**
- They join as a nickname nobody put in the calendar invite.
- The interviewer typed the wrong name into the scheduling tool.
- There are three interviewers in the room, not one.
- The candidate renames themselves halfway through the call because their laptop auto-corrected something.
- Someone silent joins to observe and never says a word.

None of these are edge cases. Taken together, they're closer to the median case. Any system that identifies the candidate by trusting a single field - display name, self-reported role, whoever the interviewer *says* is the candidate - breaks on contact with a normal Tuesday. So this system doesn't trust any single field. It trusts an accumulation of weak, individually fallible observations, weighed against each other, updated continuously, and never allowed to overcommit on thin evidence.

## Why Watson, Not Holmes

The tempting shortcut here is: pipe the transcript into an LLM, ask it "who's the candidate," get an answer back. It would demo well for about thirty seconds and then fall apart the moment someone asks *why* it picked that person, or the interviewer's name changes mid-call, or two people plausibly look like candidates. An LLM asked to just "decide" is a black box wearing a confident tone of voice - exactly the failure mode this system exists to avoid, on a platform whose entire job is catching people being someone they're not.

So instead: **every signal is a witness, not a judge.** Each one is only allowed to say, in effect, *"based on what I personally observed, here's how much more or less likely I think this person is the candidate"* - expressed as a bounded log-likelihood-ratio, not a verdict. Nothing gets to shout. Everything gets logged. A separate fusion engine is the only component allowed to combine testimony into a conclusion, and even then it's required to say "I'm not sure yet" out loud when the evidence doesn't clear the bar - rather than confidently guessing, which is the one thing this system is explicitly designed never to do.

*Data! Data! Data! I can't make bricks without clay* - Holmes' complaint, and the design constraint this whole engine is built around. No signal manufactures certainty out of a vibe.

## Architecture

```
                     Meeting Platform (Meet / Teams / Zoom)
                                    │
                                    ▼
                         Event Stream (per-participant:
                    join/leave, name change, speech, screen
                       share, camera state, transcript)
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │        Signal Engine            │
                    │  (independent witnesses, run    │
                    │   against every incoming event)  │
                    ├───────────────────────────────┤
                    │ • name_match                     │
                    │ • known_interviewer (negative)   │
                    │ • speaking_pattern                │
                    │ • addressed_by_name                │
                    │ • join_time                        │
                    │ • screen_share                     │
                    └───────────────┬───────────────┘
                                    │  Evidence(participant, signal, score, reason)
                                    ▼
                    ┌───────────────────────────────┐
                    │   Bayesian Fusion Engine          │
                    │   running log-odds per participant │
                    └───────────────┬───────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                                 ▼
        Confidence State + Audit Trail        ML Re-ranker (XGBoost)
        ("Watson's case notes" - every         trained on engineered
         update, timestamped, explained)       features, second opinion
                    │                                 │
                    └───────────────┬───────────────┘
                                    ▼
                     FastAPI (/confidence, /ml/predict,
                        /interview, /replay, /dashboard)
                                    │
                                    ▼
                          Live Dashboard (HTML/JS)
```

Every participant is tracked by `participant_id`, never by display name. Names lie, get mistyped, and change mid-call. IDs don't. This one decision is why a mid-call rename doesn't reset the system's memory of a participant - it just re-evaluates the new string against the same accumulated evidence.

## The Method - What Watson Actually Watches

Six signals, each one individually weak, none of them individually trusted:

| Signal | What it observes | Why it's not enough on its own |
|---|---|---|
| `name_match` | Fuzzy similarity between display name and candidate name | Nicknames, device names ("MacBook Pro"), typos all defeat it cleanly |
| `known_interviewer` | Fuzzy match against the known interviewer list (negative evidence) | Interviewer list itself can be incomplete or stale |
| `speaking_pattern` | Speaking-time share and turn count relative to the room | A quiet candidate or a chatty interviewer inverts it easily |
| `addressed_by_name` | Candidate's name spoken aloud in the transcript, attributed to whoever responds | Depends on the interviewer actually using the name, and on speaker attribution being reliable |
| `join_time` | Proximity to the scheduled interview start time | Interviewers often join on time too - low discriminative power alone |
| `screen_share` | Who starts sharing their screen | Interviewers share screens too, e.g. to present a problem statement |

No signal is allowed to swing the verdict by itself - each one's contribution is bounded, so a cluster of correlated weak evidence can't accidentally act like one strong, unaccountable one. This is the whole point: the system's confidence in a wrong answer should never be able to climb as fast as its confidence in a right one, no matter which single signal happens to fire hardest.

## The Deduction Engine

Every participant carries a running **log-odds score** - "how much more likely is this person the candidate, given everything observed so far." Every new piece of evidence just adds its log-likelihood-ratio to that running total. This is naive-Bayes updating, stripped down to arithmetic:

```
log_odds(candidate | evidence) = log_odds(prior) + Σ llr(each piece of evidence)
confidence = sigmoid(log_odds)
```

Two properties fall out of this almost for free, and both matter more than they look:

- **It's fully auditable.** Confidence at any timestamp is just a sum of logged, timestamped, human-readable reasons. Ask "why did you pick this person" and the honest answer is a list, not a shrug.
- **It degrades gracefully.** No evidence in → confidence stays near the prior, not a false 100% or a blank. A participant who never triggers a single signal doesn't get quietly ignored - they stay visible, correctly unconfident, which is exactly what you want for a silent observer sitting in on the call.

> *"When you have eliminated the impossible, whatever remains, however improbable, must be the truth."*
> Practically: strong negative evidence (a confident interviewer-name match) doesn't just fail to help a participant - it actively rules them out, the same way a confirmed alibi rules out a suspect.

## Case Files

The scenarios this was actually built to survive:

- **The Case of the Borrowed Device** - candidate joins as "MacBook Pro." Name signal contributes nothing; behavioral and addressed-by-name signals carry the weight instead.
- **The Case of the Wrong Name on the Invite** - interviewer metadata says one name, reality says another. Because metadata is one witness among several, not an oracle, the system isn't hostage to a typo in a calendar entry.
- **The Case of the Crowded Room** - multiple interviewers present. Their evidence trends *down*, not just "not up," via the known-interviewer signal.
- **The Case of the Midnight Rename** - display name changes mid-call. Identity is tracked by `participant_id`; the name change is just a new observation about an existing suspect, not a new suspect.
- **The Case of the Silent Observer** - someone joins, says nothing, does nothing. This is the Sherlock-Holmes "dog that didn't bark" problem: the *absence* of evidence is itself informative, and the system is built to represent that as low, visible confidence - not silence, not a crash, not a guess.

## Setup - Assembling the Kit

```bash
git clone https://github.com/ManasTripathi2/johnwatson.git
cd johnwatson

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

**Run it directly:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Or run it in Docker (no local Python setup required):**
```bash
docker compose up --build
```

Either way, the app comes up on `http://localhost:8000`.

**Train the ML re-ranker** (optional - the rule-based fusion engine works standalone):
```bash
python -m app.services.synthetic_generator   # generates data/synthetic/interviews.json
python -c "from app.services.model_trainer import ModelTrainer; ModelTrainer().train('data/synthetic/interviews.json', 'data/processed/xgboost_model.joblib')"
python scripts/evaluate_model.py             # writes docs/confusion_matrix.png
```

**Replay a recorded interview** (this is the demo path - no live meeting integration required):
```bash
python scripts/run_replay.py
```

## Running It

| Endpoint | Method | What it does |
|---|---|---|
| `/health` | GET | Liveness check |
| `/interview` | GET | Current interview + participant roster |
| `/replay` | POST | Replays `data/replay/sample_interview.json` through the full pipeline |
| `/confidence` | GET | Current ranked confidence per participant, with latest reasoning |
| `/ml/predict` | GET | XGBoost re-ranker's opinion alongside the rule-based confidence |
| `/dashboard` | GET | Live HTML dashboard - confidence bars + evidence trail |

Open `/dashboard`, hit "Replay," watch the confidence bars move as evidence comes in, and read the reasoning trail next to whoever's currently in the lead. That trail *is* the product, arguably more than the final number is.

## Assumptions

- The platform (Meet/Teams/Zoom) exposes, at minimum: participant join/leave events, display name, speaking activity per participant, and a speaker-attributed transcript. Where a platform doesn't expose participant email, the `name_match` signal simply contributes less - it doesn't fail.
- Calendar/ATS metadata (candidate name, email, interviewer names, scheduled start) is available but is treated as **evidence, not ground truth** - it can be wrong, stale, or incomplete, by design.
- Live meeting-platform integration (an actual Zoom/Teams bot) is out of scope for this prototype. The system is built against a platform-agnostic event schema and a replay harness, so wiring in a real adapter is a matter of implementing one interface, not a rewrite.
- "Candidate" is assumed to be exactly one person per interview session. The fusion engine explicitly reports "ambiguous" or "gathering evidence" states rather than forcing a pick when that assumption is under-evidenced.

## Evaluation

- **Scenario replay**: each Case File above has a corresponding recorded event sequence run through `run_replay.py`, checked for correct top candidate and a sane confidence trend.
- **Ablation**: signals can be selectively disabled in `SignalEngine` to measure each one's individual contribution to final accuracy - this is what justifies keeping every individual signal weak rather than leaning on one strong heuristic.
- **ML re-ranker**: trained via `ModelTrainer`, evaluated via `scripts/evaluate_model.py` (accuracy / precision / recall / F1 / confusion matrix, written to `docs/confusion_matrix.png`).
- **Known limitation**: synthetic training data is currently sampled from hand-picked distributions rather than generated by running real event streams through the actual signal engine - meaning the re-ranker's numbers should be read as a proof of concept, not a production accuracy claim, until that's closed.

## What's Still Open

Watson's case notes, kept honest:

- Live platform adapters (Zoom/Teams/Meet) - replay harness exists, real-time ingestion doesn't yet.
- Streaming confidence updates (WebSocket/SSE) - currently the dashboard reads state after a replay completes rather than watching it evolve live.
- Synthetic training data generated from real engine output, not hand-sampled ranges, to close the train/serve gap.
- Continuous learning from real (labeled) interview outcomes, per the platform's long-term goal.

## Tech Stack

FastAPI · Python 3.11 · rapidfuzz · XGBoost · scikit-learn · joblib · Docker · Kubernetes · vanilla HTML/JS dashboard (no framework, no build step, no ceremony).

---

*Case notes maintained throughout. Every confidence score in this system can be traced back to what was actually observed, and when. 
it's the entire design.*

- J.W.