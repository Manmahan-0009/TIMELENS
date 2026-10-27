"""TimeLens — AI-Powered Visual Heritage Comparison.

Streamlit Application.
Powered by Gemma 4 (gemma-4-26b-a4b-it).
"""

import html
import logging
import streamlit as st
from pathlib import Path

# Configure safe diagnostic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("timelens.app")

from services.image_service import validate_and_process_uploaded_image
from services.gemma_service import analyze_heritage_images, check_credentials, get_config
from services.report_service import format_exportable_report, load_cached_demo

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
        max-width: 800px;
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
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }

    .pill-certainty-medium {
        background-color: rgba(251, 191, 36, 0.15);
        color: #FBBF24;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid rgba(251, 191, 36, 0.3);
    }

    .pill-certainty-low {
        background-color: rgba(167, 180, 199, 0.15);
        color: #A7B4C7;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid rgba(167, 180, 199, 0.3);
    }

    /* Change Item Card */
    .change-card {
        background-color: #131D2E;
        border-left: 3px solid #E8B86D;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }

    .change-evidence {
        font-size: 0.88rem;
        color: #CBD5E1;
        margin-top: 0.4rem;
        line-height: 1.4;
    }

    /* Cached Demo Banner */
    .cached-demo-banner {
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 8px;
        padding: 0.85rem 1.25rem;
        margin-bottom: 1.25rem;
        color: #38BDF8;
        font-size: 0.95rem;
    }

    /* Primary Analyze button */
    div.stButton > button[kind="primary"] {
        background-color: #E8B86D !important;
        color: #0B1220 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.5rem !important;
        font-size: 1.05rem !important;
        transition: all 0.2s ease-in-out !important;
        width: 100%;
        min-height: 48px;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #dca354 !important;
        box-shadow: 0 4px 16px rgba(232, 184, 109, 0.3) !important;
    }

    div.stDownloadButton > button {
        background-color: #172235 !important;
        color: #E8B86D !important;
        border: 1px solid rgba(232, 184, 109, 0.4) !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        min-height: 48px !important;
        transition: all 0.2s ease-in-out !important;
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
            and environmental shifts.
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
elif st.session_state["use_sample_pair"] and sample_before_path.is_file():
    before_file = sample_before_path.read_bytes()

if uploaded_after is not None:
    after_file = uploaded_after
    st.session_state["use_sample_pair"] = False
    st.session_state["is_cached_demo"] = False
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

with col_before:
    if before_data:
        st.image(
            before_data["pil_image"],
            caption=f"Historical Photograph ({before_data['original_size'][0]}×{before_data['original_size'][1]})",
            use_container_width=True,
        )
    elif not before_err:
        st.info("Awaiting historical photograph upload.")

with col_after:
    if after_data:
        st.image(
            after_data["pil_image"],
            caption=f"Modern Photograph ({after_data['original_size'][0]}×{after_data['original_size'][1]})",
            use_container_width=True,
        )
    elif not after_err:
        st.info("Awaiting modern photograph upload.")

# Cache invalidation logic: only invalidate when an existing valid pair is replaced by a DIFFERENT pair
if before_data and after_data:
    combined_hash = f"{before_data['hash']}_{after_data['hash']}"
    if st.session_state["current_image_hash"] and st.session_state["current_image_hash"] != combined_hash:
        if not st.session_state["is_cached_demo"]:
            logger.info("New image pair uploaded; resetting previous analysis")
            st.session_state["analysis_result"] = None
            st.session_state["analysis_error"] = None
            st.session_state["current_location_analyzed"] = None
    st.session_state["current_image_hash"] = combined_hash

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
        else:
            logger.info("Analysis succeeded. Updating session state...")
            st.session_state["analysis_result"] = result_report
            st.session_state["analysis_error"] = None
            st.session_state["is_cached_demo"] = False
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

    # Section: Observable Visual & Architectural Changes
    changes = report.get("changes", [])
    st.markdown(f"#### 🔍 Observable Visual Changes ({len(changes)})")
    if changes:
        for idx, item in enumerate(changes):
            cert = str(item.get("certainty", "medium")).lower()
            cert_cls = f"pill-certainty-{cert}"
            st.markdown(
                f"""
                <div class="change-card">
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
        st.info("No architectural or physical changes identified between the supplied photographs.")

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
                    <div style="background-color: #131D2E; border-left: 3px solid #34D399; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;">
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
                    <div style="background-color: #131D2E; border-left: 3px solid #FBBF24; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;">
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

    # Download Report & Raw JSON row
    dl_col, json_col = st.columns([1, 1])

    with dl_col:
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
            help="Download the validated report including metadata and AI disclaimer.",
            use_container_width=True,
        )

    with json_col:
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
