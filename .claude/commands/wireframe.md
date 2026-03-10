# /wireframe — ASCII Wireframe Then Build

Three-step flow: generate an ASCII wireframe (no code), iterate with 1–2 changes, then build the artifact from the final wireframe and stack so layout matches exactly.

## Variables

artifact: $ARGUMENTS (e.g. `Dashboard`, `landing page for product X`, `n8n workflow for alerts`, or short description). If empty, ask for one or offer: Dashboard, slides, workflow, schema, landing page.

## Flow detection

- **Step 1:** User invokes `/wireframe [artifact]` → run Generate (output only ASCII wireframe).
- **Step 2:** User sends a follow-up with 1–2 specific changes and does not paste a full wireframe with "Build" → run Iterate (redraw wireframe only).
- **Step 3:** User sends a message that includes "Build" (or equivalent intent) plus a pasted wireframe and stack/requirements → run Build (implement artifact to match wireframe exactly).

---

## Step 1 — Generate

Before writing any code, generate a detailed ASCII wireframe of the requested artifact. Use box-drawing characters (─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼) and arrows for flow. Do not write any code. Output only the ASCII.

**Instructions:**

1. If no artifact was provided in $ARGUMENTS, ask the user for one, or offer examples: Dashboard, slides, workflow, schema, landing page (or a short description like "landing page for a SaaS signup").
2. Generate a **detailed ASCII wireframe** of the requested artifact.
3. Use **box-drawing characters**: `─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼` (and optionally `═ ║ ╔ ╗ ╚ ╝`) and **arrows** for flow: `→ ← ↑ ↓` (and optionally `⇒ ⇐ ⇑ ⇓`).
4. Do **not** write any code. Output **only** the ASCII wireframe. You may add a single short caption above it (e.g. "Wireframe: Portfolio dashboard") and nothing else.

**Artifact types:**

- **Dashboard** — layout of panels, widgets, nav, filters
- **Slides** — slide deck structure (title, sections, bullet blocks, visuals)
- **Workflows** — nodes, edges, triggers, branches (e.g. n8n-style or BPMN-lite)
- **Schemas** — entities, relations, cardinality (ER or data-model style)
- **Landing pages** — sections, hero, CTA, footer, navigation

---

## Step 2 — Iterate

[1–2 specific changes]. Redraw. Nothing else changes.

**Instructions:**

1. When the user provides **1–2 specific changes** (e.g. "move filters to the top; add a second chart on the right"), treat the message as Step 2.
2. Apply only those changes to the **previous** wireframe and **redraw** the full ASCII wireframe.
3. Output only the revised ASCII (and optional one-line caption). No code, no other changes.

---

## Step 3 — Build

Build the artifact using this wireframe as the exact specification: [paste wireframe] [stack + requirements]. Match the wireframe exactly. Every layout decision is already made.

**Instructions:**

1. When the user indicates they want to **build** and provides (a) the **exact wireframe** (pasted) and (b) **stack + requirements** (e.g. "React + Tailwind", "HTML/CSS only", "n8n workflow", "Postgres schema"), treat the message as Step 3.
2. Build the artifact so it **matches the wireframe exactly**. Every layout decision (placement, sections, flow, boxes) is specified in the wireframe; implementation must follow it.
3. If the user pastes a wireframe but does not say "Build" or does not give stack/requirements, ask for the stack and confirm they want to proceed to build.
4. If Step 3 produces files, you may place them in `outputs/` or as specified by the user; the command does not require a specific output location.
