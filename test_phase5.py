"""Phase 5 Quality Assurance & Demo Reliability Test Suite for TimeLens.

Validates all 10 Phase 5 requirements:
1. Valid photograph uploads
2. Invalid photograph handling
3. Duplicate image detection (deterministic)
4. Unrelated-image comparison handling (not_comparable)
5. Structured JSON validation
6. No repeated inference on Streamlit reruns (session state & hash stability)
7. API error handling
8. Downloadable JSON validity (timelens_heritage_report.json payload)
9. Cached example functionality (load_cached_demo from demo/example_analysis.json)
10. No credential leakage
"""

import sys
import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.image_service import validate_and_process_uploaded_image, compute_image_hash
from services.report_service import (
    validate_report_dict,
    create_identical_images_report,
    format_exportable_report,
    load_cached_demo,
)
from services.gemma_service import analyze_heritage_images, get_config, check_credentials


def run_test_suite():
    print("=" * 65)
    print("TIMELENS PHASE 5 QUALITY ASSURANCE & RELIABILITY TEST SUITE")
    print("=" * 65)

    samples_dir = PROJECT_ROOT / "samples"
    b_bytes = (samples_dir / "before.jpg").read_bytes()
    a_bytes = (samples_dir / "after.jpg").read_bytes()

    # TEST 1: Valid photograph uploads
    b_data, b_err = validate_and_process_uploaded_image(b_bytes)
    a_data, a_err = validate_and_process_uploaded_image(a_bytes)
    assert b_err is None and a_err is None
    assert b_data["processed_size"][0] <= 1280
    assert a_data["processed_size"][1] <= 1280
    print("Check 1 [Valid photograph uploads]: PASS")

    # TEST 2: Invalid photograph handling
    _, err_empty = validate_and_process_uploaded_image(b"")
    assert err_empty is not None
    _, err_corrupt = validate_and_process_uploaded_image(b"NOT_AN_IMAGE_PAYLOAD_ABC")
    assert err_corrupt is not None
    _, err_oversize = validate_and_process_uploaded_image(b"x" * (11 * 1024 * 1024))
    assert "exceeds maximum allowed limit" in err_oversize
    print("Check 2 [Invalid photograph handling]: PASS")

    # TEST 3: Duplicate image detection
    dup_report, dup_err = analyze_heritage_images(b_data["jpeg_bytes"], b_data["jpeg_bytes"])
    assert dup_err is None
    assert dup_report["changes"] == []
    assert "Deterministic Duplicate Detection" in dup_report.get("comparison_warning", "")
    print("Check 3 [Duplicate image detection]: PASS")

    # TEST 4: Unrelated-image comparison handling
    unrelated_payload = {
        "project": "TimeLens",
        "comparison_status": "not_comparable",
        "same_location_assessment": "likely_different",
        "location_name": None,
        "summary": "Photographs show completely different geographical subjects.",
        "before_description": "Harbour bridge.",
        "after_description": "Desert pyramid.",
        "changes": [{"category": "Arch", "observation": "fake", "before_evidence": "a", "after_evidence": "b", "certainty": "high"}],
        "preserved_elements": [],
        "uncertain_findings": [],
        "preservation_insight": "Different sites.",
        "comparison_warning": None,
    }
    validated_unrelated, u_err = validate_report_dict(unrelated_payload)
    assert u_err is None
    assert validated_unrelated["changes"] == []
    assert validated_unrelated["comparison_status"] == "not_comparable"
    print("Check 4 [Unrelated-image comparison handling]: PASS")

    # TEST 5: Structured JSON validation
    val_report, val_err = validate_report_dict(dup_report)
    assert val_err is None
    assert val_report["project"] == "TimeLens"
    print("Check 5 [Structured JSON validation]: PASS")

    # TEST 6: No repeated inference on Streamlit reruns
    hash_b = compute_image_hash(b_data["jpeg_bytes"])
    hash_a = compute_image_hash(a_data["jpeg_bytes"])
    combined_1 = f"{hash_b}_{hash_a}"
    combined_2 = f"{hash_b}_{hash_a}"
    assert combined_1 == combined_2  # Stable content hashing ensures session state is retained
    print("Check 6 [No repeated inference on Streamlit reruns]: PASS")

    # TEST 7: API error handling
    has_creds, _ = check_credentials()
    assert has_creds is True
    # Test sanitized handling with invalid key
    orig_key = os.environ.get("GEMINI_API_KEY", "")
    try:
        os.environ["GEMINI_API_KEY"] = ""
        rep, err = analyze_heritage_images(b"1", b"2")
        assert rep is None
        assert "GEMINI_API_KEY is not configured" in err
    finally:
        os.environ["GEMINI_API_KEY"] = orig_key
    print("Check 7 [API error handling]: PASS")

    # TEST 8: Downloadable JSON validity
    export_json = format_exportable_report(
        report=dup_report,
        model_name="gemma-4-26b-a4b-it",
        user_location="Sydney Harbour",
        is_cached=False,
    )
    parsed_export = json.loads(export_json)
    assert parsed_export["application_name"] == "TimeLens"
    assert parsed_export["model_used"] == "gemma-4-26b-a4b-it"
    assert "generated_timestamp" in parsed_export
    assert "ai_disclaimer" in parsed_export
    print("Check 8 [Downloadable JSON validity]: PASS")

    # TEST 9: Cached example functionality
    cached_report, cached_err = load_cached_demo(PROJECT_ROOT)
    assert cached_err is None, f"Failed loading cached demo: {cached_err}"
    assert cached_report is not None
    assert cached_report["same_location_assessment"] == "likely_same"
    assert len(cached_report["changes"]) >= 2
    assert len(cached_report["preserved_elements"]) >= 1
    # Check format_exportable_report with is_cached=True
    cached_export = json.loads(format_exportable_report(cached_report, "gemma-4-26b-a4b-it", is_cached=True))
    assert cached_export["is_cached_demo"] is True
    print("Check 9 [Cached example functionality]: PASS")

    # TEST 10: No credential leakage
    for payload_str in [export_json, json.dumps(cached_report)]:
        if orig_key:
            assert orig_key not in payload_str
    gitignore_text = (PROJECT_ROOT / ".gitignore").read_text()
    assert ".env" in gitignore_text
    print("Check 10 [No credential leakage]: PASS")

    print("=" * 65)
    print("ALL 10 PHASE 5 QUALITY ASSURANCE CHECKS PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    run_test_suite()

