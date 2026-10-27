# TimeLens 🏛️

> *"Two Photographs. One Place. A Story of Change."*

TimeLens is an open-source visual heritage intelligence application developed for the Google Hackathon. It compares archival historical photographs with modern contemporary photographs to detect architectural modifications, preserved structural anchors, environmental shifts, and viewpoint discrepancies.

TimeLens is **Powered by Gemma 4 26B (`gemma-4-26b-a4b-it`) through the Google Gemini API**, utilizing advanced multimodal reasoning to deliver evidence-backed structured JSON intelligence reports.

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

---

## 4. Core Features
- **Dual Independent Uploaders**: Supports JPG, JPEG, and PNG photographs up to 10MB per file with in-memory decompression bomb protection.
- **Digital Heritage Archive UI**: Built with a custom palette (`#0B1220` background, `#172235` surface cards, `#E8B86D` gold accents, `#F8FAFC` high-contrast text) responsive across mobile (375px), tablet (768px), and desktop (1440px).
- **One-Click Benchmark & Offline Demo**: Includes instant "⚡ Load Samples" and "📁 Cached Demo" modes with pre-validated Gemma 4 analysis of Sydney Harbour for fail-safe hackathon presentations.
- **Structured JSON Intelligence Report**: Generates structured reports containing executive summaries, historical/modern overviews, classified visual changes with certainty pills, preserved monuments, and heritage preservation insights.
- **Downloadable Report Export**: Exports validated results to `timelens_heritage_report.json` complete with timestamps, metadata, and AI verification disclaimers.
- **Ephemeral & Secure Processing**: User photographs are processed entirely in memory and never written to permanent disk storage.

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
- **Image Processing**: Pillow 13.0.0 (EXIF transposition, RGB conversion, Lanczos resizing)
- **Configuration**: python-dotenv 1.2.4

---

## 7. Architecture

```text
timelens/
│
├── app.py                      # Streamlit frontend & reactive UI
│
├── services/
│   ├── __init__.py             # Package init
│   ├── gemma_service.py        # Google GenAI SDK client & Gemma 4 inference
│   ├── image_service.py        # In-memory validation, EXIF normalization, hashing
│   └── report_service.py       # JSON schema enforcement, normalization & export
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
├── requirements.txt            # Tested dependencies
├── test_gemma.py               # Phase 0 connectivity & multimodal test suite
├── test_phase3.py              # Phase 3 schema & integration test suite
└── test_phase5.py              # Phase 5 QA & reliability test suite
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
# Run Phase 0 Gemma 4 validation
python test_gemma.py

# Run Phase 3 structured schema tests
python test_phase3.py

# Run Phase 5 QA reliability suite
python test_phase5.py
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
+-----------------------------------------+-----------------------------------------+
|  IMAGE 1: HISTORICAL (BEFORE)           |  IMAGE 2: MODERN (AFTER)                |
|  [ Photograph Preview: ~1930s ]         |  [ Photograph Preview: 21st Century ]   |
+-----------------------------------------+-----------------------------------------+
|                       [ 🔍 Analyze Heritage ]                                     |
+-----------------------------------------------------------------------------------+
|  🏛️ STRUCTURED HERITAGE INTELLIGENCE REPORT                                       |
|  [COMPARABLE]  [📍 LIKELY SAME LOCATION]  Target: Sydney Harbour                  |
|                                                                                   |
|  Executive Summary:                                                               |
|  Dramatic urban densification from low-rise industrial waterfront to high-density  |
|  metropolis, centered around a preserved steel arch bridge.                       |
|                                                                                   |
|  🔍 Observable Changes (3):                                                       |
|  - High-Rise Skyline Development (HIGH CERTAINTY)                                 |
|  - Introduction of Sydney Opera House (HIGH CERTAINTY)                            |
|  - Shoreline Modernization & Reclamation (MEDIUM CERTAINTY)                       |
|                                                                                   |
|  🏛️ Preserved Structures:                                                        |
|  - Steel Arch Bridge & Stone Pylons (HIGH CERTAINTY)                              |
|  - Natural Harbour Topography (HIGH CERTAINTY)                                    |
|                                                                                   |
|  [💾 Download Heritage Report (JSON)]  [🔍 View Raw JSON Intelligence Schema]     |
+-----------------------------------------------------------------------------------+
```

---

## 12. Example Output
Sample extract from `demo/example_analysis.json`:
```json
{
  "project": "TimeLens",
  "comparison_status": "comparable",
  "same_location_assessment": "likely_same",
  "location_name": "Sydney Harbour",
  "summary": "A comparison of a historical aerial view and a modern aerial view showing massive urban densification and the introduction of landmark architecture around a central steel arch bridge.",
  "changes": [
    {
      "category": "Architecture",
      "observation": "Significant increase in verticality and urban density.",
      "before_evidence": "The skyline and surrounding areas consist almost exclusively of low-rise buildings.",
      "after_evidence": "A dense cluster of modern high-rise skyscrapers defines the skyline.",
      "certainty": "high"
    },
    {
      "category": "Architecture",
      "observation": "Introduction of a major landmark structure.",
      "before_evidence": "The shoreline on the left side of the bridge lacks distinctive shell-shaped structures.",
      "after_evidence": "A prominent, white, shell-shaped landmark is clearly visible on the left shoreline.",
      "certainty": "high"
    }
  ],
  "preserved_elements": [
    {
      "element": "Steel Arch Bridge",
      "observation": "The primary architectural feature, the large steel arch bridge, remains the central landmark.",
      "certainty": "high"
    }
  ],
  "preservation_insight": "While the core identity of the site is preserved through the continued presence of the arch bridge, the surrounding landscape has undergone a total transformation from a low-rise maritime environment to a high-density metropolitan core."
}
```

---

## 13. Privacy & Security Considerations
- **In-Memory Image Sanitization**: Uploaded files are converted into RGB JPEG byte streams in volatile memory and discarded upon session completion. No photographs are written to permanent server storage.
- **Zero Credential Exposure**: `.env` and `.streamlit/secrets.toml` are strictly git-ignored. API keys are loaded directly by backend services and redacted from error logs.
- **Decompression Bomb Protection**: Pillow pixel limits (`Image.MAX_IMAGE_PIXELS = 50_000_000`) and 10MB file caps prevent memory exhaustion attacks.
- **Safe HTML Escaping**: All model-generated strings are HTML-escaped before display in UI cards to prevent DOM injection.

---

## 14. Known Limitations
- **No Independent Authentication**: Visual AI analysis compares observable pixels; it cannot independently authenticate the chronological provenance or historical date of an archival photograph without external metadata.
- **Resolution Dependent**: Severely degraded, blurry, or low-resolution historical photographs will reduce feature detection certainty.
- **API Network Latency**: Live multimodal inference takes 30–60 seconds depending on network conditions and Google Gemini API quota tiers.

---

## 15. License Information
- **Application Code**: Licensed under the [Apache License 2.0](LICENSE).
- **Google Gemma**: Subject to the [Gemma Terms of Use](https://ai.google.dev/gemma/terms).
- **Sample Images**: See [`samples/SOURCES.md`](samples/SOURCES.md) for provenance and licensing details.

---

## 16. Hackathon Attribution
- **Event**: Google Hackathon 2026 (Open Source Track)
- **Developed by**: Solo Open-Source Developer
- **Dedication**: Dedicated to World Audiovisual Heritage & Cultural Preservation
