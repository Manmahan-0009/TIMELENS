"""Structured Heritage Intelligence Report Service for TimeLens.

Defines the JSON schema, validation rules, enums, export formatter,
and demo loader helpers for multimodal comparative heritage analysis.
"""

import json
import re
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("timelens.report_service")

ALLOWED_COMPARISON_STATUSES = {"comparable", "uncertain", "not_comparable"}
ALLOWED_LOCATION_ASSESSMENTS = {"likely_same", "uncertain", "likely_different"}
ALLOWED_CERTAINTIES = {"high", "medium", "low"}


def extract_json_from_text(raw_text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Clean markdown code fences and extract valid JSON dict from model response text."""
    if not raw_text or not raw_text.strip():
        logger.warning("Empty response received in extract_json_from_text")
        return None, "Empty response received from model."

    text = raw_text.strip()

    # Pattern 1: Markdown code fences: ```json ... ``` or ``` ... ```
    fence_pattern = r"^```(?:json)?\s*([\s\S]*?)\s*```$"
    match = re.match(fence_pattern, text, re.IGNORECASE)
    if match:
        text = match.group(1).strip()
    else:
        # Fallback: Find outermost JSON object {...}
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            text = text[first_brace : last_brace + 1].strip()

    try:
        data = json.loads(text)
        if not isinstance(data, dict):
            logger.error("Parsed JSON root is not an object/dictionary")
            return None, "Parsed JSON root is not an object/dictionary."
        logger.info("JSON parsing successful from model response")
        return data, None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {str(e)}")
        return None, f"JSON decoding error: {str(e)}"


def _normalize_certainty(val: Any) -> str:
    """Normalize certainty to high/medium/low."""
    if not isinstance(val, str):
        return "medium"
    v = val.strip().lower()
    if "high" in v:
        return "high"
    if "low" in v:
        return "low"
    if "med" in v or "mod" in v:
        return "medium"
    return "medium"


def _normalize_location_assessment(val: Any) -> str:
    """Normalize location assessment enum."""
    if not isinstance(val, str):
        return "uncertain"
    v = val.strip().lower().replace(" ", "_").replace("-", "_")
    if "same" in v or "likely_same" in v or v == "yes":
        return "likely_same"
    if "diff" in v or "likely_diff" in v or v == "no":
        return "likely_different"
    if "uncert" in v or "unknown" in v:
        return "uncertain"
    return "uncertain"


def _normalize_comparison_status(val: Any) -> str:
    """Normalize comparison status enum."""
    if not isinstance(val, str):
        return "comparable"
    v = val.strip().lower().replace(" ", "_").replace("-", "_")
    if "not" in v or "incomp" in v or "diff" in v:
        return "not_comparable"
    if "uncert" in v or "partial" in v:
        return "uncertain"
    if "comp" in v or "valid" in v:
        return "comparable"
    return "comparable"


def validate_report_dict(data: Any) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Validate and normalize a dictionary against the TimeLens Structured Heritage Report schema.

    Returns:
        (sanitized_dict, error_message)
    """
    if not isinstance(data, dict):
        return None, "Report data must be a dictionary."

    # 1. Project name (default to TimeLens if missing)
    if not data.get("project"):
        data["project"] = "TimeLens"

    # 2. Required string fields check
    # Check summary
    if "summary" not in data and "overview" in data:
        data["summary"] = data["overview"]
    if "summary" not in data or not isinstance(data["summary"], str) or not data["summary"].strip():
        return None, "Missing or invalid required string field: 'summary'."

    # Check before_description
    if "before_description" not in data:
        for syn in ["historical_description", "image_1_description", "before"]:
            if syn in data:
                data["before_description"] = data[syn]
                break
    if "before_description" not in data or not isinstance(data["before_description"], str) or not data["before_description"].strip():
        return None, "Missing or invalid required string field: 'before_description'."

    # Check after_description
    if "after_description" not in data:
        for syn in ["modern_description", "image_2_description", "after"]:
            if syn in data:
                data["after_description"] = data[syn]
                break
    if "after_description" not in data or not isinstance(data["after_description"], str) or not data["after_description"].strip():
        return None, "Missing or invalid required string field: 'after_description'."

    # Check preservation_insight
    if "preservation_insight" not in data:
        for syn in ["conclusion", "insight", "heritage_insight"]:
            if syn in data:
                data["preservation_insight"] = data[syn]
                break
    if "preservation_insight" not in data or not isinstance(data["preservation_insight"], str) or not data["preservation_insight"].strip():
        return None, "Missing or invalid required string field: 'preservation_insight'."

    # 3. Enums validation and normalization
    raw_status = data.get("comparison_status")
    if not isinstance(raw_status, str):
        return None, "Missing or invalid required string field: 'comparison_status'."
    norm_status = raw_status.strip().lower().replace(" ", "_").replace("-", "_")
    if norm_status not in ALLOWED_COMPARISON_STATUSES:
        return None, f"Invalid comparison_status '{raw_status}'. Must be one of {sorted(ALLOWED_COMPARISON_STATUSES)}."
    data["comparison_status"] = norm_status

    raw_loc = data.get("same_location_assessment")
    if not isinstance(raw_loc, str):
        return None, "Missing or invalid required string field: 'same_location_assessment'."
    norm_loc = raw_loc.strip().lower().replace(" ", "_").replace("-", "_")
    if norm_loc not in ALLOWED_LOCATION_ASSESSMENTS:
        return None, f"Invalid same_location_assessment '{raw_loc}'. Must be one of {sorted(ALLOWED_LOCATION_ASSESSMENTS)}."
    data["same_location_assessment"] = norm_loc

    # 4. Location Name (optional)
    loc_val = data.get("location_name")
    if loc_val is not None and not isinstance(loc_val, str):
        return None, "'location_name' must be a string or null."
    data["location_name"] = loc_val.strip() if loc_val else None

    # 5. Warning (optional)
    warn_val = data.get("comparison_warning")
    if warn_val is not None and not isinstance(warn_val, str):
        return None, "'comparison_warning' must be a string or null."
    data["comparison_warning"] = warn_val.strip() if warn_val else None

    # 6. Changes list validation and normalization
    if "changes" not in data or not isinstance(data["changes"], list):
        return None, "Field 'changes' must be a list."

    normalized_changes: List[Dict[str, str]] = []
    for idx, item in enumerate(data["changes"]):
        if not isinstance(item, dict):
            return None, f"Item at index {idx} in 'changes' is not an object."

        cat = item.get("category") or "Architecture"
        obs = item.get("observation") or item.get("change") or item.get("description")
        b_ev = item.get("before_evidence") or item.get("historical_evidence") or item.get("before")
        a_ev = item.get("after_evidence") or item.get("modern_evidence") or item.get("after")
        cert_raw = item.get("certainty")

        if not isinstance(cat, str) or not isinstance(obs, str) or not isinstance(b_ev, str) or not isinstance(a_ev, str):
            return None, f"Item {idx} in 'changes' is missing or has non-string observation or evidence fields."

        if not isinstance(cert_raw, str):
            return None, f"Item {idx} in 'changes' has invalid certainty. Must be one of {sorted(ALLOWED_CERTAINTIES)}."
        cert = cert_raw.strip().lower()
        if cert in ["moderate", "mid"]:
            cert = "medium"
        if cert not in ALLOWED_CERTAINTIES:
            return None, f"Item {idx} in 'changes' has invalid certainty '{cert_raw}'. Must be one of {sorted(ALLOWED_CERTAINTIES)}."

        normalized_changes.append({
            "category": cat.strip(),
            "observation": obs.strip(),
            "before_evidence": b_ev.strip(),
            "after_evidence": a_ev.strip(),
            "certainty": cert,
        })
    data["changes"] = normalized_changes

    if data["comparison_status"] == "not_comparable":
        data["changes"] = []

    # 7. Preserved elements validation and normalization
    if "preserved_elements" not in data or not isinstance(data["preserved_elements"], list):
        return None, "Field 'preserved_elements' must be a list."

    normalized_preserved: List[Dict[str, str]] = []
    for idx, elem in enumerate(data["preserved_elements"]):
        if not isinstance(elem, dict):
            return None, f"Item at index {idx} in 'preserved_elements' is not an object."

        name = elem.get("element") or elem.get("structure") or elem.get("feature") or elem.get("name")
        obs = elem.get("observation") or elem.get("description")
        cert_raw = elem.get("certainty") or "high"

        if not isinstance(name, str) or not isinstance(obs, str):
            return None, f"Item {idx} in 'preserved_elements' is missing or has non-string 'element' or 'observation'."

        if not isinstance(cert_raw, str):
            return None, f"Item {idx} in 'preserved_elements' has invalid certainty."
        cert = cert_raw.strip().lower()
        if cert in ["moderate", "mid"]:
            cert = "medium"
        if cert not in ALLOWED_CERTAINTIES:
            return None, f"Item {idx} in 'preserved_elements' has invalid certainty '{cert_raw}'. Must be one of {sorted(ALLOWED_CERTAINTIES)}."

        normalized_preserved.append({
            "element": name.strip(),
            "observation": obs.strip(),
            "certainty": cert,
        })
    data["preserved_elements"] = normalized_preserved

    # 8. Uncertain findings validation and normalization
    if "uncertain_findings" not in data or not isinstance(data["uncertain_findings"], list):
        return None, "Field 'uncertain_findings' must be a list."

    normalized_uncertain: List[Dict[str, str]] = []
    for idx, finding in enumerate(data["uncertain_findings"]):
        if not isinstance(finding, dict):
            return None, f"Item at index {idx} in 'uncertain_findings' is not an object."

        claim = finding.get("claim") or finding.get("observation") or finding.get("finding")
        reason = finding.get("reason") or finding.get("explanation")

        if not isinstance(claim, str) or not isinstance(reason, str):
            return None, f"Item {idx} in 'uncertain_findings' is missing or has non-string 'claim' or 'reason'."

        normalized_uncertain.append({
            "claim": claim.strip(),
            "reason": reason.strip(),
        })
    data["uncertain_findings"] = normalized_uncertain

    logger.info(
        f"Schema validation passed: {len(data['changes'])} changes, "
        f"{len(data['preserved_elements'])} preserved, status={data['comparison_status']}"
    )
    return data, None


def create_identical_images_report(location_name: Optional[str] = None) -> Dict[str, Any]:
    """Generate a deterministic report when identical photographs are submitted."""
    loc = (location_name or "").strip() or "Identical Photograph Pair"
    return {
        "project": "TimeLens",
        "comparison_status": "comparable",
        "same_location_assessment": "likely_same",
        "location_name": loc,
        "summary": "Identical photographs provided. No visual, architectural, or environmental differences exist between the two submitted files.",
        "before_description": "Historical photograph input.",
        "after_description": "Modern photograph input is bit-for-bit identical to the historical photograph.",
        "changes": [],
        "preserved_elements": [
            {
                "element": "Complete Visual Composition",
                "observation": "All structural, environmental, and spatial elements are identical between both inputs.",
                "certainty": "high",
            }
        ],
        "uncertain_findings": [],
        "preservation_insight": "Duplicate photograph pair detected via deterministic SHA-256 analysis. Temporal changes cannot be evaluated on identical files.",
        "comparison_warning": "Deterministic Duplicate Detection: Both uploaded files are identical. No model inference was required.",
    }


def format_exportable_report(
    report: Dict[str, Any],
    model_name: str,
    user_location: Optional[str] = None,
    is_cached: bool = False,
) -> str:
    """Format and serialize report into exportable JSON containing metadata and disclaimers."""
    export_payload = {
        "application_name": "TimeLens",
        "tagline": "Two Photographs. One Place. A Story of Change.",
        "model_used": model_name,
        "is_cached_demo": is_cached,
        "generated_timestamp": datetime.now(timezone.utc).isoformat(),
        "user_supplied_location": user_location or report.get("location_name"),
        "comparison_status": report.get("comparison_status"),
        "same_location_assessment": report.get("same_location_assessment"),
        "summary": report.get("summary"),
        "before_description": report.get("before_description"),
        "after_description": report.get("after_description"),
        "changes": report.get("changes", []),
        "preserved_elements": report.get("preserved_elements", []),
        "uncertain_findings": report.get("uncertain_findings", []),
        "preservation_insight": report.get("preservation_insight"),
        "comparison_warning": report.get("comparison_warning"),
        "ai_disclaimer": "TimeLens outputs are generated by AI (Google Gemma 4) for visual heritage analysis and should be verified against historical records.",
    }
    return json.dumps(export_payload, indent=2)


def load_cached_demo(base_dir: Optional[Path] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Load and validate the verified genuine Gemma 4 demo analysis from demo/example_analysis.json."""
    root = base_dir or Path(__file__).resolve().parent.parent
    demo_file = root / "demo" / "example_analysis.json"

    if not demo_file.is_file():
        logger.error(f"Demo file not found at: {demo_file}")
        return None, f"Demo file not found at: {demo_file}"

    try:
        text = demo_file.read_text(encoding="utf-8")
        data = json.loads(text)
        validated, err = validate_report_dict(data)
        if err:
            logger.error(f"Demo file schema invalid: {err}")
            return None, f"Demo file contains invalid schema: {err}"
        logger.info("Cached demo loaded and validated successfully")
        return validated, None
    except Exception as e:
        logger.error(f"Failed reading cached demo file: {str(e)}")
        return None, f"Failed reading cached demo file: {str(e)}"
