# TimeLens 🏛️

> *"Two Photographs. One Place. A Story of Change."*

TimeLens is an open-source visual heritage intelligence application developed for the Google Hackathon. It compares archival historical photographs with modern contemporary photographs to detect architectural modifications, preserved structural anchors, environmental shifts, and viewpoint discrepancies.

TimeLens is **Powered by Gemma 4 26B (`gemma-4-26b-a4b-it`) through the Google Gemini API**, utilizing advanced multimodal reasoning to deliver evidence-backed structured JSON intelligence reports, interactive split-screen comparisons, preservation scorecards, and publication-ready PDF exports.

---

## 1. Project Overview
Across the globe, rapid urbanization, conflict, and climate change alter cultural landmarks and urban landscapes. Archival photography captures our shared heritage, but manual visual comparison across decades is labor-intensive and subjective. TimeLens provides historians, urban planners, conservators, and citizens with an AI-powered visual heritage comparison platform.

---

## 2. Problem Statement
Historical visual comparison faces three key challenges:
- **Perspective Distortion**: Differences in camera angles, altitudes, focal lengths, and lighting are frequently mistaken for physical architectural changes.
- **AI Hallucination**: Generative AI models often fabricate historical dates, architects, or restoration events not visible in the photographs.
- **Unstructured Observations**: Free-form text descriptions are difficult to categorize, verify, or integrate into heritage archival registries.

---

## 3. Proposed Solution
TimeLens addresses these challenges by:
1. **Multimodal Dual-Image Orchestration**: Passing historical and modern photographs in a single prompt labeled explicitly as `IMAGE 1 = HISTORICAL / BEFORE` and `IMAGE 2 = MODERN / AFTER`.
2. **Evidence-Based Heritage Intelligence Schema**: Enforcing structured JSON reporting with distinct fields for observable changes, physical evidence from each photograph, certainty ratings (`high`, `medium`, `low`), preserved elements, and explicit documentation of uncertain findings.
3. **Strict Non-Hallucination Guardrails**: Prompts and validators strictly prohibit fabricating unverified dates, demolition claims, or landmarks, enforcing explicit distinction between visual evidence and interpretation.
4. **Deterministic Duplicate Detection**: Automatically computing SHA-256 hashes of normalized images to intercept identical image submissions without making unnecessary API calls.
5. **Deterministic Preservation Scorecard**: Evaluating comparative reliability via a transparent mathematical rubric based on observable continuity versus uncertainty.
6. **Publication-Ready PDF Reports**: Producing archival-grade vector PDF reports with embedded photographic evidence, scorecard KPIs, and multi-page layout.

---

## 4. Core Features

### 🏛️ Heritage Preservation Scorecard (v1.1)
- **KPI Metrics Dashboard**: Instant tally of observed changes, continuous preserved structures, and visual uncertainties.
- **Transparent Reliability Rubric**: Categorizes comparison confidence deterministically into `HIGH`, `MEDIUM`, `LOW`, or `NOT COMPARABLE` with explicit reasoning.

### 📸 Interactive Split-Screen Comparison Slider (v1.1)
- **Responsive Slider**: Smooth draggable vertical divider revealing historical archival photography underneath modern imagery.
- **Touch & Keyboard Accessible**: Native touch-drag support for mobile devices and keyboard navigation (`Left`/`Right` arrow keys).
- **Side-by-Side Dual Plate Fallback**: Immediate toggle to side-by-side mode for side-by-side inspections.
- **Perspective Alignment Notice**: Transparent disclaimers regarding vintage focal length and vantage shifts.

### 🔍 Interactive Visual Change Explorer (v1.1)
- **Thematic Category Filtering**: Filter findings dynamically by category (Architecture, Infrastructure, Environment, Waterfront, etc.) with zero additional API latency.
- **Evidence-Backed Observation Cards**: Independent Historical Evidence and Modern Evidence callouts for every claim.

### 📄 Professional PDF Heritage Report Export (v1.1)
- **Publication-Ready Layout**: In-memory generated A4 portrait document styled with Digital Heritage Navy (`#0B1220`) and Warm Gold (`#E8B86D`).
- **Embedded Photographs**: Side-by-side Plate A (Historical) and Plate B (Modern) maintaining exact aspect ratios.
- **Dynamic Two-Pass Page Numbering**: Built with custom `NumberedCanvas` displaying `"Page X of Y"`.
- **Complete Archival Summary**: Includes Executive Summary, preservation scorecard, itemized changes table, preserved monuments, and methodology notices.

### 🛡️ Privacy & Security
- **In-Memory Sanitization**: All images processed strictly in memory (`io.BytesIO`) — zero disk writes for uploaded user photographs.
- **Decompression Bomb Protection**: Hard limits on pixel resolution and 10MB file caps.
- **Zero Credential Exposure**: API keys loaded securely from `.env` and excluded from error messages, reports, and Git.

---

## 5. Gemma 4 Integration Explanation
TimeLens is **Powered by Gemma 4 26B through the Google Gemini API** (`gemma-4-26b-a4b-it`) via the modern official Google GenAI Python SDK (`google-genai`).

Gemma 4 was selected for its exceptional multimodal spatial reasoning, nuanced visual comprehension, and ability to follow strict analytical schemas. The integration uses:
- Two-image multimodal input structure preserving chronological ordering.
- Dual-mode JSON generation (structured JSON MIME mode with automatic prompt-based fallback).
- Single-retry self-correction for malformed outputs.
- Normalized schema validation ensuring all enum values and required categories conform to heritage standards.

*Note: TimeLens runs inference remotely through the Google Gemini API hosted service.*

---

## 6. Technology Stack
- **Language**: Python 3.13.5
- **Web Interface**: Streamlit 1.66.1
- **AI SDK**: Google GenAI SDK (`google-genai==2.33.0`)
- **Multimodal Model**: Google Gemma 4 26B (`gemma-4-26b-a4b-it`)
- **PDF Generation**: ReportLab 5.1.0 & PyPDF 6.21.2
- **Image Processing**: Pillow 13.0.0 (EXIF transposition, RGB conversion, Lanczos resizing)
- **Configuration**: python-dotenv 1.2.4

---

## 7. Architecture

```text
timelens/
│
├── app.py                      # Streamlit frontend, slider component & reactive UI
│
├── services/
│   ├── __init__.py             # Package init
│   ├── gemma_service.py        # Google GenAI SDK client & Gemma 4 inference
│   ├── image_service.py        # In-memory validation, EXIF normalization, hashing
│   ├── report_service.py       # JSON schema enforcement, normalization & export
│   └── pdf_service.py          # Publication-ready PDF generation & scorecard rubric
│
├── demo/
│   └── example_analysis.json   # Verified genuine Gemma 4 cached analysis
│
├── samples/
│   ├── before.jpg              # Sydney Harbour historical photograph (~1930s)
│   ├── after.jpg               # Sydney Harbour modern photograph (21st century)
│   └── SOURCES.md              # Image provenance & copyright documentation
│
├── .agents/skills/             # Development skills (context-keeper, security-first, etc.)
├── .streamlit/
│   └── config.toml             # Theme settings (#0B1220, #172235, #E8B86D)
│
├── .context.md                 # Real-time project context tracker
├── .env.example                # Example environment template
├── .gitignore                  # VCS exclusion rules
├── LICENSE                     # Apache-2.0 open-source license
├── requirements.txt            # Tested dependencies (pinned)
├── test_gemma.py               # Phase 0 connectivity & multimodal test suite
├── test_phase3.py              # Phase 3 schema & integration test suite
├── test_phase5.py              # Phase 5 QA & reliability test suite
└── test_phase_v1_1.py          # Phase v1.1 PDF, slider & scorecard test suite
```

---

## 8. Installation Instructions

### Prerequisites
- Python 3.10+ (tested on Python 3.13.5)
- Google Gemini API key with access to Gemma 4

### Step 1: Clone Repository
```bash
git clone https://github.com/Manmahan-0009/TIMELENS.git
cd TIMELENS
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 9. Environment Configuration
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMMA_MODEL=gemma-4-26b-a4b-it
```
*(A template is provided in `.env.example`).*

---

## 10. Application Launch Instructions
Run the Streamlit application:
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

To run automated test suites:
```bash
# Run Phase v1.1 PDF, slider & scorecard validation
python test_phase_v1_1.py

# Run Phase 5 QA reliability suite
python test_phase5.py

# Run Phase 3 structured schema tests
python test_phase3.py

# Run Phase 0 Gemma 4 validation
python test_gemma.py
```

---

## 11. Interface Preview

```text
+-----------------------------------------------------------------------------------+
|  🏛️ GOOGLE HACKATHON 2026 • POWERED BY GEMMA 4                                    |
|  TIMELENS                                                                         |
|  "Two Photographs. One Place. A Story of Change."                                 |
+-----------------------------------------------------------------------------------+
|  Location Hint: [ Sydney Harbour Bridge, Australia         ]  [⚡ Load] [📁 Cached] |
+-----------------------------------------------------------------------------------+
|  📸 INTERACTIVE COMPARISON VIEWER                                                 |
|  (•) Interactive Split-Screen Slider   ( ) Side-by-Side Dual View                 |
|  [=== [HISTORICAL] ================ [MODERN] ===================================] |
|  [========================== < [ ↔ ] > =========================================] |
|  *Disclaimer: Visual alignment is approximate; perspective differences may occur.*|
+-----------------------------------------------------------------------------------+
|                       [ 🔍 Analyze Heritage ]                                     |
+-----------------------------------------------------------------------------------+
|  🏛️ STRUCTURED HERITAGE INTELLIGENCE REPORT                                       |
|  [COMPARABLE]  [📍 LIKELY SAME LOCATION]  Target: Sydney Harbour                  |
|                                                                                   |
|  PRESERVATION SCORECARD:                                                          |
|  [ 3 Changes ]  [ 2 Preserved ]  [ 0 Uncertain ]  [ HIGH Reliability ]            |
|                                                                                   |
|  Executive Summary:                                                               |
|  Dramatic urban densification from low-rise industrial waterfront to high-density  |
|  metropolis, centered around a preserved steel arch bridge.                       |
|                                                                                   |
|  🔍 Visual Change Explorer:                                                       |
|  Filter: [ All Findings                                                         ] |
|  - High-Rise Skyline Development (HIGH CERTAINTY)                                 |
|  - Introduction of Sydney Opera House (HIGH CERTAINTY)                            |
|                                                                                   |
|  🏛️ Preserved Structures (2):                                                     |
|  - Steel Arch Bridge & Stone Pylons (HIGH CERTAINTY)                              |
|                                                                                   |
|  [📄 Download Heritage Report (PDF)]   [💾 Download Heritage Report (JSON)]       |
+-----------------------------------------------------------------------------------+
```

---

## 12. Privacy & Security Considerations
- **In-Memory Image Sanitization**: Uploaded files are converted into RGB JPEG byte streams in volatile memory and discarded upon session completion. No photographs are written to permanent server storage.
- **Zero Credential Exposure**: `.env` and `.streamlit/secrets.toml` are strictly git-ignored. API keys are loaded directly by backend services and redacted from error logs.
- **Decompression Bomb Protection**: Pillow pixel limits (`Image.MAX_IMAGE_PIXELS = 50_000_000`) and 10MB file caps prevent memory exhaustion attacks.
- **Safe HTML Escaping**: All model-generated strings are HTML-escaped before display in UI cards to prevent DOM injection.

---

## 13. License Information
- **Application Code**: Licensed under the [Apache License 2.0](LICENSE).
- **Google Gemma**: Subject to the [Gemma Terms of Use](https://ai.google.dev/gemma/terms).
- **Sample Images**: See [`samples/SOURCES.md`](samples/SOURCES.md) for provenance and licensing details.

---

## 14. Hackathon Attribution
- **Event**: Google Hackathon 2026 (Open Source Track)
- **Developed by**: Solo Open-Source Developer
- **Dedication**: Dedicated to World Audiovisual Heritage & Cultural Preservation
