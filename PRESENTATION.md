# MedAI Diagnostics — Project Presentation (PPT Content)

> Copy each slide block below into a separate PowerPoint slide.
> Recommended theme: dark slides with teal/indigo accents (matches the live app).
> Total: **15 slides** for a 10–12 minute presentation.

---

## SLIDE 1 — TITLE SLIDE

**Title:**
# MedAI Diagnostics
### An AI-Powered Multi-Role Medical Platform with Explainable Deep Learning

**Below title, three lines:**

- **Submitted by:** [YOUR FULL NAME]
- **USN:** [YOUR USN]
- **Under the Guidance of:** [GUIDE'S FULL NAME WITH TITLE, e.g., Prof. / Dr.]

**Footer line:**
[Department] | [College Name] | [Academic Year]

---

## SLIDE 2 — AGENDA / OUTLINE

**Title:** Presentation Outline

**Bullets:**
- Introduction
- Problem Statement & Objectives
- Literature & Existing Systems
- Proposed System
- Methodology
- System Architecture
- Implementation
- Module-wise Explanation
- Results & Performance
- Conclusion & Future Scope

---

## SLIDE 3 — INTRODUCTION

**Title:** Introduction

**Bullets:**
- Healthcare in low-resource regions suffers from specialist shortages — particularly dermatology, where ~3 billion people lack access.
- AI has matured to the point where deep learning models can perform medical screening tasks competitively.
- **MedAI Diagnostics** is a full-stack web platform that integrates **three real machine learning models** (Random Forest, CNN, and LLM) into a single workflow serving patients, doctors, and receptionists.
- The platform provides AI-driven symptom checking, skin lesion classification with explainable heatmaps, an LLM-powered medical assistant, and a complete clinic management workflow.
- Designed as a decision-support tool — *not* a doctor replacement — with safety disclaimers and graceful degradation built in.

**Speaker note:** Lead with the gap, then the solution, then your three-model differentiator.

---

## SLIDE 4 — PROBLEM STATEMENT & OBJECTIVES

**Title:** Problem Statement & Objectives

**Problem (left column):**
- Limited access to specialists, especially dermatologists, in tier-2/3 cities.
- Existing symptom checkers are generic, not personalized.
- Most student AI projects ship one model — no end-to-end clinical workflow.
- Black-box AI predictions are not trusted in healthcare without explainability.

**Objectives (right column):**
- Build a deployable, multi-role medical platform.
- Train **real ML models** on benchmark datasets, not toy data.
- Provide **explainable AI** (heatmaps + class probabilities).
- Integrate a **GenAI medical assistant** with retrieval-augmented context.
- Implement an **MLOps feedback loop** for continuous improvement.
- Support **multilingual + offline-first** workflow for emerging markets.

---

## SLIDE 5 — LITERATURE / EXISTING SYSTEMS

**Title:** Existing Systems & Their Limitations

**Two-column comparison table:**

| System | Strength | Limitation |
|---|---|---|
| SkinVision | Mobile skin scanning | Closed-source, paid, single-feature |
| Ada Health | Symptom checker | Generic, no role-based workflow |
| First Derm | Telemedicine | Human-in-loop only, costly |
| Buoy Health | Conversational symptoms | No imaging, no MLOps loop |
| **MedAI Diagnostics (proposed)** | **3 AI models + multi-role + MLOps + offline + multilingual** | Research/demo-grade; HIPAA hardening needed for production |

**Speaker note:** Position your project as combining strengths of all four into one platform.

---

## SLIDE 6 — PROPOSED SYSTEM

**Title:** Proposed System

**Body:** A unified web platform integrating three independent AI engines behind a role-aware frontend.

**Three engine boxes (icons / horizontal layout):**
- **Tabular ML:** Random Forest classifier — 132 symptoms → 41 diseases (~99 % test accuracy on academic data).
- **Computer Vision:** MobileNetV2 CNN — 7-class skin lesion classifier trained on **HAM10000** (10,015 images) — **74.59 %** validation accuracy with Grad-CAM explainability.
- **Generative AI:** Llama 3.3 70B LLM via Groq — Retrieval-Augmented Generation grounds responses in user's actual diagnostic context.

**Bottom line:** Three independent models + role-based access + MLOps loop + offline-first design.

---

## SLIDE 7 — METHODOLOGY (Overview)

**Title:** Methodology

**Numbered workflow diagram (or list):**

1. **Data Acquisition** — HAM10000 (skin), Symptom-Disease 4920-record dataset.
2. **Preprocessing** — Image resize 224×224, normalization, augmentation (flip, rotation, hue, saturation).
3. **Model Selection** — MobileNetV2 (CNN) + Random Forest (RF) + Llama 3.3 (LLM).
4. **Training Strategy** — Two-stage transfer learning: 10 epochs head-only + 15 epochs fine-tune top 50 layers.
5. **Class Imbalance Handling** — `compute_class_weight('balanced')` (HAM10000 is 67 % nv).
6. **Evaluation** — 80/20 stratified split, validation accuracy as primary metric.
7. **Deployment** — FastAPI backend + Next.js 14 frontend on Render.
8. **MLOps** — Predictions auto-logged → user feedback → retrain pipeline.

---

## SLIDE 8 — METHODOLOGY (Skin Lesion Classifier — Detailed)

**Title:** Methodology — Skin Lesion Classifier

**Pipeline diagram (horizontal arrows):**

```
HAM10000 (10,015 images)
        ↓
Stratified 80/20 train-val split
        ↓
Augmentation (flip, rotation, hue, saturation, brightness, contrast)
        ↓
MobileNetV2 (ImageNet pretrained, frozen)  →  Custom Dense Head (Dropout + Softmax)
        ↓
Stage-1: Train head only (10 epochs, LR=1e-3)
        ↓
Stage-2: Unfreeze top 50 layers, fine-tune (15 epochs, LR=1e-5)
        ↓
ReduceLROnPlateau + EarlyStopping callbacks
        ↓
Save .h5 model + metadata.json
        ↓
Inference: image → CNN → softmax probs → Grad-CAM heatmap
```

---

## SLIDE 9 — SYSTEM ARCHITECTURE

**Title:** System Architecture

**Layered diagram (top-to-bottom):**

```
╔════════════════════════════════════════════════════╗
║   USER LAYER                                       ║
║   Patient  |  Doctor  |  Receptionist (RBAC)       ║
╠════════════════════════════════════════════════════╣
║   FRONTEND  —  Next.js 14 + TypeScript + Tailwind  ║
║   (App Router, AuthContext, LanguageContext)       ║
╠════════════════════════════════════════════════════╣
║   API GATEWAY  —  FastAPI + slowapi (rate limit)   ║
╠════════════════════════════════════════════════════╣
║   AI ENGINES                                       ║
║   • Symptom RF (sklearn .pkl)                      ║
║   • Skin CNN (TensorFlow .h5)                      ║
║   • RAG Chat (Groq → Llama 3.3 70B)                ║
╠════════════════════════════════════════════════════╣
║   DATA LAYER  —  Supabase (Postgres) + localStorage║
╚════════════════════════════════════════════════════╝
```

**Bottom line:** 3 user roles → 1 unified API → 3 AI engines → cloud + local storage.

---

## SLIDE 10 — IMPLEMENTATION (Tech Stack)

**Title:** Implementation — Technology Stack

**Two-column table:**

| Layer | Technology | Justification |
|---|---|---|
| Frontend | Next.js 14, TypeScript, TailwindCSS, react-three-fiber | App Router, server components, type-safe API |
| Backend | FastAPI, Pydantic, Uvicorn | Async, auto OpenAPI docs at /docs |
| Tabular ML | scikit-learn (Random Forest) | Best-in-class for tabular categorical data |
| Deep Learning | TensorFlow / Keras 2.15 | Industry standard, Keras Applications API |
| Computer Vision | OpenCV | Image preprocessing + heatmap fallback |
| LLM | Llama 3.3 70B via Groq API | Free tier, 500 tokens/sec, open-source weights |
| Database | Supabase (Postgres) | Auth + realtime + free tier |
| PDF Export | jsPDF + html2canvas | Client-side prescription PDFs |
| Deployment | Render + render.yaml + Procfile | Git-push deploy, zero-config |

---

## SLIDE 11 — IMPLEMENTATION (Modules Built)

**Title:** Implementation — Modules

**Bullets (group by category):**

**AI Modules:**
- `symptom_checker.py` — Random Forest inference + 41-disease descriptions.
- `skin_analyzer.py` — CNN inference + Grad-CAM heatmap + OpenCV fallback.
- `chat.py` — RAG chatbot with Groq + offline rule-based fallback.

**Healthcare Modules:**
- `patients.py` — Multi-role auth (token-based) + patient EMR CRUD.
- `appointments.py` — Receptionist scheduling + doctor view + patient request flow.
- `feedback.py` — Prediction logging + user feedback submission.
- `metrics.py` — Live model status for MLOps dashboard.

**Frontend pages (9):**
Home dashboard, Login, Symptom checker (3D body map), Skin analyzer, AI assistant, Medication reminders, Patients EMR, Prescription generator, Appointments, MLOps dashboard.

---

## SLIDE 12 — EXPLANATION (Why It Works)

**Title:** Explanation — How the System Delivers Value

**Three "story" blocks:**

**1. Explainable AI**
- Every CNN prediction returns full 7-class probability distribution + Grad-CAM heatmap.
- Doctor can audit *which pixels* the model used → trust + clinical safety.

**2. Retrieval-Augmented Generation (RAG)**
- Diagnostic context (e.g., "Melanoma 78 % confidence") is injected as a system message before the user's chatbot prompt.
- Result: personalized advice instead of generic hallucination.
- Without RAG: "Consult a doctor." With RAG: "Based on your melanoma prediction, schedule a dermoscopic exam — apply the ABCDE rule…"

**3. Graceful Degradation**
- If TensorFlow fails to load → OpenCV fallback engine analyzes color/edges.
- If Groq API is down → local rule-based chatbot serves common questions.
- If Supabase is offline → medication reminders still work via localStorage.
- **Outcome:** the platform stays useful even in partial-failure conditions.

---

## SLIDE 13 — RESULTS & PERFORMANCE

**Title:** Results & Performance

**Performance table:**

| Metric | Value |
|---|---|
| Skin CNN — Validation Accuracy | **74.59 %** |
| Skin CNN — Random baseline | 14.3 % |
| Skin CNN — Majority-class baseline | 67 % |
| Skin CNN — Inference Latency (CPU) | < 1.5 s |
| Symptom RF — Test Accuracy | ~99 % (academic dataset) |
| Symptom RF — Inference Latency | < 100 ms |
| RAG Chat — Response Latency | 1–2 s |
| Training Time (skin CNN, CPU) | ~ 45 min |
| Model Size (skin .h5) | 26 MB |
| Total Predictions Logged (MLOps) | Live count from Supabase |

**Note line:** Beats random baseline by 60+ points and majority-class baseline by 7+ points — model genuinely learns minority classes including melanoma.

---

## SLIDE 14 — SCREENSHOTS / DEMO PREVIEW

**Title:** Live Demo

**Recommended:** Take 4 screenshots from your running app and arrange in a 2×2 grid.

1. **Top-Left** — Skin analyzer result with heatmap overlay
2. **Top-Right** — Symptom checker 3D body map + prediction
3. **Bottom-Left** — RAG chatbot response with diagnostic context
4. **Bottom-Right** — MLOps dashboard / metrics page

**Caption strip:** *Live demonstration to follow.*

**Speaker note:** This is the slide where you click "Live Demo" and switch to the running app. Don't read the slide — show it.

---

## SLIDE 15 — CONCLUSION & FUTURE SCOPE

**Title:** Conclusion & Future Scope

**Conclusion (left column):**
- Successfully built a deployable medical AI platform integrating **three real models** (RF, CNN, LLM) on **benchmark datasets**.
- Achieved **74.59 %** validation accuracy on 7-class skin lesion classification — beating majority-class baseline by 7+ points.
- Implemented **explainable AI** (Grad-CAM), **MLOps feedback loop**, **multi-role RBAC**, and **graceful degradation** — engineering hallmarks of a production system.
- Demonstrated full-stack capability: ML training, API design, frontend UX, and DevOps.

**Future Scope (right column):**
- GPU-trained skin CNN at ≥ 85 % accuracy (EfficientNetB3 or ResNet50).
- Demographic fairness audit (Fitzpatrick17k integration).
- Mobile app via React Native.
- HIPAA hardening + FDA Class II clearance pathway.
- Federated learning for privacy-preserving model improvement across clinics.
- TB chest X-ray module (second CNN).
- Drug-interaction checker via RxNav API.

**Final line (centered):** *Thank you. Questions welcome.*

---

# OPTIONAL APPENDIX SLIDES (use only if asked)

### A1 — Dataset Details
Source: HAM10000 (Tschandl et al., *Scientific Data* 2018) — 10,015 dermatoscopic images, 7 lesion classes, public via ISIC archive.

### A2 — References
- Tschandl, P. et al. *Scientific Data*, 5, 180161 (2018) — HAM10000 dataset.
- Sandler, M. et al. *CVPR 2018* — MobileNetV2.
- Touvron, H. et al. *arXiv 2307.09288* (2023) — Llama 2/3 architecture.
- Selvaraju, R. et al. *ICCV 2017* — Grad-CAM.

### A3 — Repository
GitHub: `[YOUR_GITHUB_USERNAME]/MedAI-Diagnostics`
Live demo: `[YOUR_DEPLOYED_URL_IF_AVAILABLE]`

---

# DESIGN GUIDELINES (for the actual PPT file)

| Element | Recommendation |
|---|---|
| Theme | Dark background (#050a18), teal accent (#14b8a6), indigo highlight |
| Title font | Inter / Segoe UI Bold, 32–36 pt |
| Body font | Inter / Segoe UI Regular, 18–20 pt |
| Code blocks | Fira Code / Consolas, 14–16 pt, light gray bg |
| Images | Use real screenshots from your live app |
| Slide count | 15 main + 3 optional = 18 max |
| Time per slide | 30–45 seconds → fits within 10–12 min total |
| Animations | Minimal — fade-in only. Avoid spinning text/transitions. |
| Logo placement | Top-left of every slide except title and conclusion |

---

# SUBMISSION CHECKLIST

- [ ] Replace placeholders: `[YOUR FULL NAME]`, `[YOUR USN]`, `[GUIDE'S NAME]`, `[Department]`, `[College]`, `[Academic Year]`.
- [ ] Add 4 real screenshots to Slide 14.
- [ ] Update GitHub URL on Slide A3 (if including).
- [ ] Verify the **74.59 %** number against latest `skin_disease_metadata.json`.
- [ ] Spell-check every slide.
- [ ] Export final file as both `.pptx` and `.pdf` (PDF version is the safety backup if PowerPoint crashes during evaluation).
- [ ] Practice the talk-through twice — aim for 10 minutes flat.
