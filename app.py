"""TimeLens — AI-Powered Visual Heritage Comparison.

Streamlit Application — v1.1 Premium Heritage Intelligence Edition.
Powered by Gemma 4 (gemma-4-26b-a4b-it).
"""

import base64
import html
import logging
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

# Configure safe diagnostic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("timelens.app")

from services.image_service import validate_and_process_uploaded_image
from services.gemma_service import analyze_heritage_images, check_credentials, get_config
from services.report_service import format_exportable_report, load_cached_demo
from services.pdf_service import generate_heritage_pdf, calculate_preservation_scorecard

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & THEME STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="TimeLens — Visual Heritage Comparison",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
    /* Global Base */
    .stApp {
        background-color: #0B1220;
        color: #F8FAFC;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Accent badge */
    .accent-badge {
        display: inline-block;
        background: rgba(232, 184, 109, 0.12);
        color: #E8B86D;
        border: 1px solid rgba(232, 184, 109, 0.35);
        border-radius: 9999px;
        padding: 4px 14px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
    }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #F8FAFC;
        margin-bottom: 0.25rem;
    }

    .hero-tagline {
        font-size: 1.25rem;
        font-weight: 500;
        color: #E8B86D;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        font-size: 1.0rem;
        color: #A7B4C7;
        max-width: 820px;
        line-height: 1.5;
        margin-bottom: 1.5rem;
    }

    /* Card styling */
    .heritage-card {
        background-color: #172235;
        border: 1px solid rgba(232, 184, 109, 0.25);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }

    /* Scorecard metrics */
    .scorecard-card {
        background-color: #172235;
        border: 1px solid rgba(232, 184, 109, 0.25);
        border-radius: 10px;
        padding: 1rem 0.75rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    .scorecard-label {
        color: #A7B4C7;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    .scorecard-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #F8FAFC;
    }

    /* Image label badges */
    .image-label-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        margin-bottom: 0.5rem;
    }

    .badge-before {
        background-color: rgba(232, 184, 109, 0.15);
        color: #E8B86D;
        border: 1px solid rgba(232, 184, 109, 0.3);
    }

    .badge-after {
        background-color: rgba(52, 211, 153, 0.15);
        color: #34D399;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }

    /* Status Pills */
    .status-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        margin-right: 0.5rem;
    }

    .pill-comparable {
        background-color: rgba(52, 211, 153, 0.18);
        color: #34D399;
        border: 1px solid rgba(52, 211, 153, 0.4);
    }

    .pill-uncertain {
        background-color: rgba(251, 191, 36, 0.18);
        color: #FBBF24;
        border: 1px solid rgba(251, 191, 36, 0.4);
    }

    .pill-not-comparable {
        background-color: rgba(248, 113, 113, 0.18);
        color: #F87171;
        border: 1px solid rgba(248, 113, 113, 0.4);
    }

    .pill-certainty-high {
        background-color: rgba(52, 211, 153, 0.15);
        color: #34D399;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 700;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }

    .pill-certainty-medium {
        background-color: rgba(232, 184, 109, 0.15);
        color: #E8B86D;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 700;
        border: 1px solid rgba(232, 184, 109, 0.3);
    }

    .pill-certainty-low {
        background-color: rgba(248, 113, 113, 0.15);
        color: #F87171;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 700;
        border: 1px solid rgba(248, 113, 113, 0.3);
    }

    .cached-demo-banner {
        background: rgba(232, 184, 109, 0.12);
        border: 1px solid #E8B86D;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 1rem;
        color: #E8B86D;
    }

    .change-card {
        background-color: #172235;
        border-left: 3px solid #E8B86D;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }

    .change-evidence {
        color: #CBD5E1;
        font-size: 0.88rem;
        line-height: 1.5;
        margin-top: 0.35rem;
        background: rgba(11, 18, 32, 0.5);
        padding: 6px 10px;
        border-radius: 6px;
    }

    /* Buttons */
    div.stButton > button:first-child {
        background-color: #E8B86D !important;
        color: #0B1220 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.25rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease-in-out !important;
        min-height: 48px !important;
    }

    div.stButton > button:first-child:hover {
        background-color: #D6A458 !important;
        box-shadow: 0 4px 14px rgba(232, 184, 109, 0.35) !important;
    }

    div.stDownloadButton > button {
        background-color: transparent !important;
        color: #E8B86D !important;
        border: 1px solid #E8B86D !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.25rem !important;
        transition: all 0.2s ease-in-out !important;
        min-height: 48px !important;
    }

    div.stDownloadButton > button:hover {
        background-color: rgba(232, 184, 109, 0.15) !important;
        border-color: #E8B86D !important;
    }

    /* Footer text */
    .heritage-footer {
        border-top: 1px solid rgba(167, 180, 199, 0.15);
        padding-top: 1.5rem;
        margin-top: 3rem;
        color: #A7B4C7;
        font-size: 0.85rem;
        text-align: center;
        line-height: 1.6;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_interactive_slider(
    before_bytes: bytes,
    after_bytes: bytes,
    before_alt: str = "Historical photograph",
    after_alt: str = "Modern photograph",
):
    """Render a responsive, touch-friendly, keyboard-accessible comparison slider."""
    b64_before = base64.b64encode(before_bytes).decode("ascii")
    b64_after = base64.b64encode(after_bytes).decode("ascii")
    escaped_before_alt = html.escape(before_alt or "Historical photograph")
    escaped_after_alt = html.escape(after_alt or "Modern photograph")

    slider_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      body {{
        background: transparent;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #F8FAFC;
        overflow: hidden;
      }}
      .slider-container {{
        position: relative;
        width: 100%;
        max-width: 960px;
        height: 470px;
        margin: 0 auto;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(232, 184, 109, 0.35);
        background-color: #0B1220;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6);
        user-select: none;
        -webkit-user-select: none;
      }}
      .img-layer {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
      }}
      .img-layer img {{
        width: 100%;
        height: 100%;
        object-fit: contain;
        background-color: #0B1220;
        display: block;
        user-select: none;
        pointer-events: none;
      }}
      .layer-after {{
        clip-path: polygon(50% 0, 100% 0, 100% 100%, 50% 100%);
        will-change: clip-path;
      }}
      .badge-tag {{
        position: absolute;
        top: 14px;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        box-shadow: 0 4px 12px rgba(0,0,0,0.6);
        pointer-events: none;
        z-index: 5;
      }}
      .badge-before {{
        left: 14px;
        background: rgba(23, 34, 53, 0.9);
        color: #E8B86D;
        border: 1px solid rgba(232, 184, 109, 0.6);
      }}
      .badge-after {{
        right: 14px;
        background: rgba(23, 34, 53, 0.9);
        color: #34D399;
        border: 1px solid rgba(52, 211, 153, 0.6);
      }}
      .divider-line {{
        position: absolute;
        top: 0;
        bottom: 0;
        left: 50%;
        width: 3px;
        background: #E8B86D;
        transform: translateX(-50%);
        pointer-events: none;
        z-index: 6;
        box-shadow: 0 0 10px rgba(0,0,0,0.8);
      }}
      .slider-handle {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #172235;
        border: 2px solid #E8B86D;
        box-shadow: 0 0 14px rgba(232, 184, 109, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #E8B86D;
        font-size: 16px;
        font-weight: 900;
        pointer-events: none;
      }}
      .range-input {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0;
        cursor: ew-resize;
        z-index: 10;
        margin: 0;
      }}
    </style>
    </head>
    <body>
    <div class="slider-container" id="sliderContainer">
      <div class="img-layer">
        <img src="data:image/jpeg;base64,{b64_before}" alt="{escaped_before_alt}" />
        <div class="badge-tag badge-before">📜 Historical</div>
      </div>
      <div class="img-layer layer-after" id="afterLayer">
        <img src="data:image/jpeg;base64,{b64_after}" alt="{escaped_after_alt}" />
        <div class="badge-tag badge-after">🏙️ Modern</div>
      </div>
      <div class="divider-line" id="dividerLine">
        <div class="slider-handle">↔</div>
      </div>
      <input type="range" min="0" max="100" value="50" class="range-input" id="rangeInput" aria-label="Slide horizontally to compare historical and modern photographs" />
    </div>
    <script>
      const range = document.getElementById('rangeInput');
      const afterLayer = document.getElementById('afterLayer');
      const dividerLine = document.getElementById('dividerLine');

      function update(val) {{
        afterLayer.style.clipPath = `polygon(${{val}}% 0, 100% 0, 100% 100%, ${{val}}% 100%)`;
        dividerLine.style.left = `${{val}}%`;
      }}

      range.addEventListener('input', (e) => update(e.target.value));
    </script>
    </body>
    </html>
    """
    components.html(slider_html, height=485)


# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "analysis_error" not in st.session_state:
    st.session_state["analysis_error"] = None
if "current_image_hash" not in st.session_state:
    st.session_state["current_image_hash"] = None
if "current_location_analyzed" not in st.session_state:
    st.session_state["current_location_analyzed"] = None
if "use_sample_pair" not in st.session_state:
    st.session_state["use_sample_pair"] = False
if "is_cached_demo" not in st.session_state:
    st.session_state["is_cached_demo"] = False
if "pdf_bytes" not in st.session_state:
    st.session_state["pdf_bytes"] = None

# -----------------------------------------------------------------------------
# SECTION 1: HERO
# -----------------------------------------------------------------------------
_, model_name = get_config()
st.markdown(
    f"""
    <div style="text-align: left; padding: 0.5rem 0 1rem 0;">
        <span class="accent-badge">🏛️ Google Hackathon 2026 • Powered by Gemma 4</span>
        <div class="hero-title">TIMELENS</div>
        <div class="hero-tagline">"Two Photographs. One Place. A Story of Change."</div>
        <div class="hero-subtitle">
            Discover how historical places have evolved using AI-powered visual comparison.
            Structured heritage intelligence reporting on architectural continuity, urban expansion,
            environmental shifts, and preservation scorecards.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

has_creds, cred_err_msg = check_credentials()
if not has_creds:
    st.error(f"⚠️ **API Configuration Required:** {cred_err_msg}")

# -----------------------------------------------------------------------------
# SECTION 2: UPLOAD & INPUTS
# -----------------------------------------------------------------------------
st.markdown("### 📤 Photographic Inputs")

samples_dir = Path(__file__).resolve().parent / "samples"
sample_before_path = samples_dir / "before.jpg"
sample_after_path = samples_dir / "after.jpg"

ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1, 1])
with ctrl_col1:
    location_input = st.text_input(
        "Optional Location Name / Landmark Hint",
        placeholder="e.g., Sydney Harbour, Australia (Unverified user context)",
        help="Optional hint provided to the AI. Note: Gemma will verify against actual visual evidence.",
    )
with ctrl_col2:
    st.write("")
    sample_btn = st.button(
        "⚡ Load Samples",
        help="Instantly load the Sydney Harbour historical & modern sample photograph pair.",
        use_container_width=True,
    )
    if sample_btn:
        logger.info("⚡ Load Samples button clicked")
        st.session_state["use_sample_pair"] = True
        st.session_state["is_cached_demo"] = False
        st.session_state["analysis_error"] = None
        st.session_state["pdf_bytes"] = None

with ctrl_col3:
    st.write("")
    cached_demo_btn = st.button(
        "📁 Cached Demo",
        help="Instantly load the verified offline Gemma 4 analysis of Sydney Harbour without calling the API.",
        use_container_width=True,
    )
    if cached_demo_btn:
        logger.info("📁 Cached Demo button clicked")
        cached_data, cached_err = load_cached_demo()
        if cached_data:
            st.session_state["use_sample_pair"] = True
            st.session_state["analysis_result"] = cached_data
            st.session_state["is_cached_demo"] = True
            st.session_state["analysis_error"] = None
            st.session_state["pdf_bytes"] = None
            st.session_state["current_location_analyzed"] = cached_data.get("location_name") or "Sydney Harbour"
            logger.info("Cached demo loaded into session state")
        else:
            st.session_state["analysis_error"] = f"Failed loading cached demo: {cached_err}"
            logger.error(f"Failed loading cached demo: {cached_err}")

col_before, col_after = st.columns(2)

before_file = None
after_file = None

with col_before:
    st.markdown('<span class="image-label-badge badge-before">IMAGE 1: HISTORICAL (BEFORE)</span>', unsafe_allow_html=True)
    uploaded_before = st.file_uploader(
        "Upload Historical Photograph",
        type=["jpg", "jpeg", "png"],
        key="uploader_before",
        help="Upload an archival or historic photograph (max 10MB).",
    )

with col_after:
    st.markdown('<span class="image-label-badge badge-after">IMAGE 2: MODERN (AFTER)</span>', unsafe_allow_html=True)
    uploaded_after = st.file_uploader(
        "Upload Modern Photograph",
        type=["jpg", "jpeg", "png"],
        key="uploader_after",
        help="Upload a contemporary photograph of the same perspective (max 10MB).",
    )

if uploaded_before is not None:
    before_file = uploaded_before
    st.session_state["use_sample_pair"] = False
    st.session_state["is_cached_demo"] = False
    st.session_state["pdf_bytes"] = None
elif st.session_state["use_sample_pair"] and sample_before_path.is_file():
    before_file = sample_before_path.read_bytes()

if uploaded_after is not None:
    after_file = uploaded_after
    st.session_state["use_sample_pair"] = False
    st.session_state["is_cached_demo"] = False
    st.session_state["pdf_bytes"] = None
elif st.session_state["use_sample_pair"] and sample_after_path.is_file():
    after_file = sample_after_path.read_bytes()

before_data, before_err = None, None
after_data, after_err = None, None

if before_file:
    before_data, before_err = validate_and_process_uploaded_image(before_file)
    if before_err:
        logger.warning(f"Historical image validation error: {before_err}")
        with col_before:
            st.error(f"❌ Historical image error: {before_err}")
    else:
        logger.info(f"Historical image validated: size={before_data['processed_size']}, bytes={len(before_data['jpeg_bytes'])}")

if after_file:
    after_data, after_err = validate_and_process_uploaded_image(after_file)
    if after_err:
        logger.warning(f"Modern image validation error: {after_err}")
        with col_after:
            st.error(f"❌ Modern image error: {after_err}")
    else:
        logger.info(f"Modern image validated: size={after_data['processed_size']}, bytes={len(after_data['jpeg_bytes'])}")

# Cache invalidation logic: only invalidate when an existing valid pair is replaced by a DIFFERENT pair
if before_data and after_data:
    combined_hash = f"{before_data['hash']}_{after_data['hash']}"
    if st.session_state["current_image_hash"] and st.session_state["current_image_hash"] != combined_hash:
        if not st.session_state["is_cached_demo"]:
            logger.info("New image pair uploaded; resetting previous analysis")
            st.session_state["analysis_result"] = None
            st.session_state["analysis_error"] = None
            st.session_state["current_location_analyzed"] = None
            st.session_state["pdf_bytes"] = None
    st.session_state["current_image_hash"] = combined_hash

# -----------------------------------------------------------------------------
# INTERACTIVE COMPARISON VIEWER SECTION
# -----------------------------------------------------------------------------
if before_data and after_data:
    st.markdown("### 📸 Interactive Comparison Viewer")
    viewer_mode = st.radio(
        "Viewing Mode:",
        ["Interactive Split-Screen Slider", "Side-by-Side Dual View"],
        horizontal=True,
        key="viewer_mode_selection",
    )

    report_cached = st.session_state.get("analysis_result") or {}
    before_desc = report_cached.get("before_description") or "Historical archival photograph"
    after_desc = report_cached.get("after_description") or "Modern contemporary photograph"

    if viewer_mode == "Interactive Split-Screen Slider":
        render_interactive_slider(
            before_bytes=before_data["jpeg_bytes"],
            after_bytes=after_data["jpeg_bytes"],
            before_alt=before_desc,
            after_alt=after_desc,
        )
    else:
        pv_col1, pv_col2 = st.columns(2)
        with pv_col1:
            st.image(
                before_data["pil_image"],
                caption=f"Historical Photograph ({before_data['original_size'][0]}×{before_data['original_size'][1]})",
                use_container_width=True,
            )
        with pv_col2:
            st.image(
                after_data["pil_image"],
                caption=f"Modern Photograph ({after_data['original_size'][0]}×{after_data['original_size'][1]})",
                use_container_width=True,
            )

    st.caption(
        "ℹ️ *Visual Alignment Notice: Historical and contemporary photographic angles, focal lengths, "
        "and camera vantage points may differ. The slider offers comparative visual context.*"
    )
elif before_data and not after_data:
    with col_before:
        st.image(before_data["pil_image"], caption="Historical Photograph Preview", use_container_width=True)
    with col_after:
        st.info("Awaiting modern photograph upload.")
elif after_data and not before_data:
    with col_before:
        st.info("Awaiting historical photograph upload.")
    with col_after:
        st.image(after_data["pil_image"], caption="Modern Photograph Preview", use_container_width=True)

location_changed = (
    st.session_state["analysis_result"] is not None
    and location_input.strip() != ""
    and location_input.strip() != (st.session_state.get("current_location_analyzed") or "")
)

# -----------------------------------------------------------------------------
# SECTION 3: ANALYSIS TRIGGER
# -----------------------------------------------------------------------------
st.markdown("---")

can_analyze = (
    before_data is not None
    and after_data is not None
    and has_creds
)

btn_col, info_col = st.columns([1, 2])

with btn_col:
    analyze_btn = st.button(
        "🔍 Analyze Heritage",
        type="primary",
        disabled=not can_analyze,
        use_container_width=True,
    )

with info_col:
    if not has_creds:
        st.warning("⚠️ Enter a valid GEMINI_API_KEY in `.env` to enable live analysis.")
    elif not before_data or not after_data:
        st.info("💡 Please upload both a Historical and Modern photograph to proceed.")
    elif before_data and after_data and before_data["hash"] == after_data["hash"]:
        st.info("ℹ️ Identical photographs detected: Analysis will execute deterministically without API calls.")
    elif st.session_state["is_cached_demo"]:
        st.caption("Displaying cached example. Click 'Analyze Heritage' above to perform a live inference call.")
    elif location_changed:
        st.caption("ℹ️ Location hint updated. Click 'Analyze Heritage' to re-run comparison.")
    else:
        st.caption(f"Ready for live structured analysis using **{model_name}**.")

# Handle Analysis Execution
if analyze_btn and can_analyze:
    logger.info(f"Analyze Heritage button clicked. Initiating analysis with model={model_name}...")
    with st.spinner(f"Extracting structured heritage intelligence with {model_name}..."):
        result_report, err_msg = analyze_heritage_images(
            before_image_bytes=before_data["jpeg_bytes"],
            after_image_bytes=after_data["jpeg_bytes"],
            location_name=location_input,
        )

        if err_msg:
            logger.error(f"Analysis failed: {err_msg}")
            st.session_state["analysis_error"] = err_msg
            st.session_state["analysis_result"] = None
            st.session_state["pdf_bytes"] = None
        else:
            logger.info("Analysis succeeded. Updating session state...")
            st.session_state["analysis_result"] = result_report
            st.session_state["analysis_error"] = None
            st.session_state["is_cached_demo"] = False
            st.session_state["pdf_bytes"] = None
            st.session_state["current_location_analyzed"] = location_input.strip()

# Display persistent error if present
if st.session_state.get("analysis_error"):
    st.error(f"❌ Analysis failed: {st.session_state['analysis_error']}")

# -----------------------------------------------------------------------------
# SECTION 4: STRUCTURED REPORT RESULTS DISPLAY
# -----------------------------------------------------------------------------
report: dict = st.session_state.get("analysis_result")

if report and isinstance(report, dict):
    logger.info("Rendering analysis dashboard")
    st.markdown("### 🏛️ Structured Heritage Intelligence Report")

    # Differentiate live vs cached example
    if st.session_state.get("is_cached_demo"):
        st.markdown(
            """
            <div class="cached-demo-banner">
                <strong>ℹ️ Cached Example — Previously Generated by Gemma 4</strong><br>
                <span style="font-size: 0.88rem; opacity: 0.9;">
                    This analysis is pre-loaded from verified offline benchmark data (Sydney Harbour) to demonstrate application capability without invoking the live API.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Status & Meta Row
    comp_status = str(report.get("comparison_status", "comparable"))
    loc_assess = str(report.get("same_location_assessment", "likely_same"))
    loc_display = str(report.get("location_name") or "Unspecified Location")

    pill_cls = f"pill-{comp_status.replace('_', '-')}"
    loc_badge_text = {
        "likely_same": "📍 Likely Same Location",
        "uncertain": "❓ Location Uncertain",
        "likely_different": "❌ Likely Different Locations",
    }.get(loc_assess, loc_assess)

    meta_html = f"""
    <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; margin-bottom: 1.25rem;">
        <span class="status-pill {pill_cls}">{html.escape(comp_status.replace('_', ' '))}</span>
        <span class="status-pill pill-comparable" style="background-color: rgba(232, 184, 109, 0.15); color: #E8B86D; border-color: rgba(232, 184, 109, 0.3);">{html.escape(loc_badge_text)}</span>
        <span style="color: #A7B4C7; font-size: 0.9rem; margin-left: auto;">Target: <strong style="color: #F8FAFC;">{html.escape(loc_display)}</strong></span>
    </div>
    """
    st.markdown(meta_html, unsafe_allow_html=True)

    if report.get("comparison_warning"):
        st.warning(f"⚠️ {report['comparison_warning']}")

    # -------------------------------------------------------------------------
    # PRESERVATION SCORECARD DASHBOARD
    # -------------------------------------------------------------------------
    scorecard = calculate_preservation_scorecard(report)
    sc1, sc2, sc3, sc4 = st.columns(4)

    rel_colors = {
        "HIGH": "#34D399",
        "MEDIUM": "#E8B86D",
        "LOW": "#F59E0B",
        "NOT COMPARABLE": "#F87171",
    }
    rel_color = rel_colors.get(scorecard["reliability"], "#E8B86D")

    with sc1:
        st.markdown(
            f"""
            <div class="scorecard-card">
                <div class="scorecard-label">Observed Changes</div>
                <div class="scorecard-value" style="color: #E8B86D;">{scorecard['total_changes']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sc2:
        st.markdown(
            f"""
            <div class="scorecard-card">
                <div class="scorecard-label">Preserved Structures</div>
                <div class="scorecard-value" style="color: #34D399;">{scorecard['preserved_count']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sc3:
        st.markdown(
            f"""
            <div class="scorecard-card">
                <div class="scorecard-label">Uncertain Findings</div>
                <div class="scorecard-value" style="color: #FBBF24;">{scorecard['uncertain_count']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sc4:
        st.markdown(
            f"""
            <div class="scorecard-card">
                <div class="scorecard-label">Preservation Reliability</div>
                <div class="scorecard-value" style="color: {rel_color}; font-size: 1.45rem;">{scorecard['reliability']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(f"📊 **Scorecard Reliability Assessment:** {scorecard['rationale']}")
    st.write("")

    # Executive Summary Card
    st.markdown(
        f"""
        <div class="heritage-card">
            <div style="color: #E8B86D; font-weight: 700; font-size: 1.05rem; margin-bottom: 0.5rem;">Executive Summary</div>
            <div style="color: #F8FAFC; line-height: 1.6; font-size: 0.98rem;">{html.escape(str(report.get('summary', '')))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Independent Photographic Overviews
    desc_col1, desc_col2 = st.columns(2)
    with desc_col1:
        st.markdown(
            f"""
            <div class="heritage-card" style="border-left: 3px solid #E8B86D;">
                <div style="color: #E8B86D; font-weight: 700; font-size: 0.95rem; margin-bottom: 0.35rem;">📜 Historical Era Overview</div>
                <div style="color: #CBD5E1; font-size: 0.9rem; line-height: 1.5;">{html.escape(str(report.get('before_description', '')))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with desc_col2:
        st.markdown(
            f"""
            <div class="heritage-card" style="border-left: 3px solid #34D399;">
                <div style="color: #34D399; font-weight: 700; font-size: 0.95rem; margin-bottom: 0.35rem;">🏙️ Modern Era Overview</div>
                <div style="color: #CBD5E1; font-size: 0.9rem; line-height: 1.5;">{html.escape(str(report.get('after_description', '')))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -------------------------------------------------------------------------
    # INTERACTIVE VISUAL CHANGE EXPLORER (P1)
    # -------------------------------------------------------------------------
    changes = report.get("changes", [])
    st.markdown(f"#### 🔍 Visual Change Explorer ({len(changes)} Findings)")

    # Collect unique categories
    raw_categories = [str(item.get("category", "General")).strip() for item in changes if item.get("category")]
    unique_categories = sorted(list(set(raw_categories)))
    filter_options = ["All Findings"] + unique_categories

    sel_cat = st.selectbox(
        "Filter Findings by Thematic Category:",
        filter_options,
        index=0,
        help="Filter observable evolutions dynamically without invoking additional AI calls.",
        key="category_filter_dropdown",
    )

    filtered_changes = [
        item for item in changes
        if sel_cat == "All Findings" or str(item.get("category", "")).strip().lower() == sel_cat.lower()
    ]

    if filtered_changes:
        for idx, item in enumerate(filtered_changes):
            cert = str(item.get("certainty", "medium")).lower()
            cert_cls = f"pill-certainty-{cert}"
            st.markdown(
                f"""
                <div class="change-card" aria-label="Finding {idx+1}: {html.escape(str(item.get('observation', '')))}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                        <span style="color: #E8B86D; font-weight: 700; font-size: 0.95rem;">{html.escape(str(item.get('category', 'Change')))} • {html.escape(str(item.get('observation', '')))}</span>
                        <span class="{cert_cls}">{html.escape(cert.upper())} CERTAINTY</span>
                    </div>
                    <div class="change-evidence"><strong>Historical Evidence:</strong> {html.escape(str(item.get('before_evidence', 'N/A')))}</div>
                    <div class="change-evidence"><strong>Modern Evidence:</strong> {html.escape(str(item.get('after_evidence', 'N/A')))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info(f"No changes matching category '{sel_cat}'.")

    # Two columns: Preserved Elements & Uncertain Findings
    elem_col, uncert_col = st.columns(2)

    with elem_col:
        preserved = report.get("preserved_elements", [])
        st.markdown(f"#### 🏛️ Preserved Structures ({len(preserved)})")
        if preserved:
            for item in preserved:
                cert = str(item.get("certainty", "high")).lower()
                cert_cls = f"pill-certainty-{cert}"
                st.markdown(
                    f"""
                    <div style="background-color: #131D2E; border-left: 3px solid #34D399; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;" aria-label="Preserved structure: {html.escape(str(item.get('element', '')))}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong style="color: #34D399; font-size: 0.92rem;">{html.escape(str(item.get('element', '')))}</strong>
                            <span class="{cert_cls}">{html.escape(cert.upper())}</span>
                        </div>
                        <div style="color: #CBD5E1; font-size: 0.85rem; margin-top: 0.3rem; line-height: 1.4;">{html.escape(str(item.get('observation', '')))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No continuous structural elements identified.")

    with uncert_col:
        uncertain = report.get("uncertain_findings", [])
        st.markdown(f"#### ❓ Uncertain Observations ({len(uncertain)})")
        if uncertain:
            for item in uncertain:
                st.markdown(
                    f"""
                    <div style="background-color: #131D2E; border-left: 3px solid #FBBF24; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;" aria-label="Uncertain observation: {html.escape(str(item.get('claim', '')))}">
                        <strong style="color: #FBBF24; font-size: 0.92rem;">{html.escape(str(item.get('claim', '')))}</strong>
                        <div style="color: #CBD5E1; font-size: 0.85rem; margin-top: 0.3rem; line-height: 1.4;"><strong>Reason:</strong> {html.escape(str(item.get('reason', '')))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No ambiguous or uncertain findings documented.")

    # Preservation Insight Callout
    if report.get("preservation_insight"):
        st.markdown(
            f"""
            <div style="background: rgba(232, 184, 109, 0.08); border: 1px solid rgba(232, 184, 109, 0.4); border-radius: 10px; padding: 1.25rem; margin-top: 1rem; margin-bottom: 1.5rem;">
                <div style="color: #E8B86D; font-weight: 700; font-size: 0.98rem; margin-bottom: 0.35rem;">🌱 Heritage Preservation Insight</div>
                <div style="color: #F8FAFC; font-size: 0.93rem; line-height: 1.5;">{html.escape(str(report.get('preservation_insight', '')))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -------------------------------------------------------------------------
    # EXPORT ROW: PROFESSIONAL PDF & STRUCTURED JSON
    # -------------------------------------------------------------------------
    st.markdown("#### 📥 Archival Intelligence Exports")
    dl_pdf_col, dl_json_col = st.columns(2)

    with dl_pdf_col:
        # Cache generated PDF in session state to prevent slow repeated builds
        if st.session_state.get("pdf_bytes") is None and before_data and after_data:
            with st.spinner("Compiling publication-grade PDF report..."):
                try:
                    st.session_state["pdf_bytes"] = generate_heritage_pdf(
                        report=report,
                        before_image_bytes=before_data["jpeg_bytes"],
                        after_image_bytes=after_data["jpeg_bytes"],
                        location_name=st.session_state.get("current_location_analyzed") or report.get("location_name") or "",
                        model_name=model_name,
                        is_cached=st.session_state.get("is_cached_demo", False),
                    )
                except Exception as pdf_err:
                    logger.error(f"Failed to generate PDF: {pdf_err}")
                    st.session_state["pdf_bytes"] = None

        if st.session_state.get("pdf_bytes"):
            st.download_button(
                label="📄 Download Heritage Report (PDF)",
                data=st.session_state["pdf_bytes"],
                file_name="timelens_heritage_report.pdf",
                mime="application/pdf",
                help="Download multi-page PDF report with embedded photographs, preservation scorecard, and archival intelligence.",
                use_container_width=True,
            )
        else:
            st.button("📄 PDF Report Unavailable", disabled=True, use_container_width=True)

    with dl_json_col:
        export_json_str = format_exportable_report(
            report=report,
            model_name=model_name,
            user_location=st.session_state.get("current_location_analyzed"),
            is_cached=st.session_state.get("is_cached_demo", False),
        )

        st.download_button(
            label="💾 Download Heritage Report (JSON)",
            data=export_json_str,
            file_name="timelens_heritage_report.json",
            mime="application/json",
            help="Download the validated JSON report schema including metadata and AI disclaimer.",
            use_container_width=True,
        )

    with st.expander("🔍 View Raw JSON Intelligence Schema"):
        st.json(report)

# -----------------------------------------------------------------------------
# SECTION 5: FOOTER & PRIVACY
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="heritage-footer">
        <div><strong>TimeLens</strong> — Dedicated to World Audiovisual Heritage & Cultural Preservation.</div>
        <div style="margin-top: 0.25rem;">Open-source visual heritage analytics under the Apache 2.0 / MIT license.</div>
        <div style="margin-top: 0.5rem; color: #7E8D9F; font-size: 0.78rem;">
            <strong>Privacy & AI Notice:</strong> Photographs are processed in-memory and transmitted securely to Google's hosted inference API solely for real-time comparison. No uploaded images are permanently stored on this server. Model outputs are AI-generated and should be verified against historical records.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
