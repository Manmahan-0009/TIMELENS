"""Phase 3 Test Suite for TimeLens Structured Heritage Intelligence.

Tests:
1. Valid JSON parsing and schema validation
2. Markdown-fenced JSON handling
3. Invalid JSON string handling
4. Missing required fields detection
5. Invalid certainty values detection
6. Empty changes list handling
7. Identical images deterministic detection
8. Unrelated image handling (not_comparable status)
9. API error handling and credential protection
10. End-to-end integration with real sample images and Gemma 4
"""

import sys
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.report_service import (
    extract_json_from_text,
    validate_report_dict,
    create_identical_images_report,
)
from services.image_service import validate_and_process_uploaded_image
from services.gemma_service import analyze_heritage_images

MOCK_VALID_REPORT = {
    "project": "TimeLens",
    "comparison_status": "comparable",
    "same_location_assessment": "likely_same",
    "location_name": "Sydney Harbour",
    "summary": "Visual comparison summary of the harbour.",
    "before_description": "Historical monochrome image showing the bridge under early conditions.",
    "after_description": "Modern vibrant photograph showing high-density developments.",
    "changes": [
        {
            "category": "Architecture",
            "observation": "High-rise skyline development",
            "before_evidence": "Low-rise waterfront buildings",
            "after_evidence": "Dense cluster of modern skyscrapers",
            "certainty": "high",
        }
    ],
    "preserved_elements": [
        {
            "element": "Arch Bridge",
            "observation": "Steel arch and stone pylons intact",
            "certainty": "high",
        }
    ],
    "uncertain_findings": [
        {
            "claim": "Waterfront pier reconfiguration",
            "reason": "Angle of Image 1 partially obscures pier shoreline",
        }
    ],
    "preservation_insight": "The core transport monument is preserved while urban density increased exponentially.",
    "comparison_warning": None,
}


def test_1_valid_json():
    raw = json.dumps(MOCK_VALID_REPORT)
    parsed, err = extract_json_from_text(raw)
    assert err is None, f"Parsing failed: {err}"
    val, val_err = validate_report_dict(parsed)
    assert val_err is None, f"Validation failed: {val_err}"
    assert val["comparison_status"] == "comparable"
    print("Test 1 (Valid JSON): PASS")


def test_2_markdown_fenced_json():
    raw = f"```json\n{json.dumps(MOCK_VALID_REPORT)}\n```"
    parsed, err = extract_json_from_text(raw)
    assert err is None, f"Parsing fenced failed: {err}"
    val, val_err = validate_report_dict(parsed)
    assert val_err is None
    print("Test 2 (Markdown-Fenced JSON): PASS")


def test_3_invalid_json():
    raw = "{ invalid json string here "
    parsed, err = extract_json_from_text(raw)
    assert parsed is None
    assert err is not None
    print("Test 3 (Invalid JSON Handling): PASS")


def test_4_missing_required_fields():
    broken = dict(MOCK_VALID_REPORT)
    del broken["summary"]
    val, err = validate_report_dict(broken)
    assert val is None
    assert "summary" in err
    print("Test 4 (Missing Required Fields): PASS")


def test_5_invalid_certainty_values():
    broken = json.loads(json.dumps(MOCK_VALID_REPORT))
    broken["changes"][0]["certainty"] = "99.8%"  # Invalid enum value
    val, err = validate_report_dict(broken)
    assert val is None
    assert "certainty" in err
    print("Test 5 (Invalid Certainty Values): PASS")


def test_6_empty_changes_list():
    no_changes = json.loads(json.dumps(MOCK_VALID_REPORT))
    no_changes["changes"] = []
    val, err = validate_report_dict(no_changes)
    assert err is None
    assert len(val["changes"]) == 0
    print("Test 6 (Empty Changes List): PASS")


def test_7_identical_images():
    samples_dir = PROJECT_ROOT / "samples"
    b_bytes = (samples_dir / "before.jpg").read_bytes()
    b_data, _ = validate_and_process_uploaded_image(b_bytes)

    # Submit identical bytes to analyze_heritage_images
    report, err = analyze_heritage_images(b_data["jpeg_bytes"], b_data["jpeg_bytes"], "Test")
    assert err is None
    assert report is not None
    assert report["changes"] == []
    assert "Deterministic Duplicate Detection" in report.get("comparison_warning", "")
    print("Test 7 (Identical Images Deterministic Handling): PASS")


def test_8_unrelated_image_handling():
    unrelated_report = json.loads(json.dumps(MOCK_VALID_REPORT))
    unrelated_report["comparison_status"] = "not_comparable"
    unrelated_report["same_location_assessment"] = "likely_different"
    unrelated_report["changes"] = [
        {"category": "A", "observation": "B", "before_evidence": "C", "after_evidence": "D", "certainty": "high"}
    ]
    val, err = validate_report_dict(unrelated_report)
    assert err is None
    # Schema validation must enforce empty changes list for not_comparable
    assert len(val["changes"]) == 0
    assert val["comparison_status"] == "not_comparable"
    print("Test 8 (Unrelated Image Handling): PASS")


def test_9_api_error_handling():
    # Test error handling when bad key provided
    import os
    orig_key = os.environ.get("GEMINI_API_KEY", "")
    try:
        os.environ["GEMINI_API_KEY"] = ""
        report, err = analyze_heritage_images(b"123", b"456")
        assert report is None
        assert "GEMINI_API_KEY is not configured" in err
    finally:
        os.environ["GEMINI_API_KEY"] = orig_key
    print("Test 9 (API Error Handling & Secret Protection): PASS")


def test_10_real_sample_gemma_call():
    print("Executing genuine Gemma 4 inference with sample photographs...")
    samples_dir = PROJECT_ROOT / "samples"
    b_bytes = (samples_dir / "before.jpg").read_bytes()
    a_bytes = (samples_dir / "after.jpg").read_bytes()

    b_data, b_err = validate_and_process_uploaded_image(b_bytes)
    a_data, a_err = validate_and_process_uploaded_image(a_bytes)
    assert b_err is None and a_err is None

    report, err = analyze_heritage_images(
        before_image_bytes=b_data["jpeg_bytes"],
        after_image_bytes=a_data["jpeg_bytes"],
        location_name="Sydney Harbour",
    )

    assert err is None, f"Real Gemma 4 call failed: {err}"
    assert report is not None
    assert report["project"] == "TimeLens"
    assert report["comparison_status"] in ["comparable", "uncertain", "not_comparable"]
    assert report["same_location_assessment"] in ["likely_same", "uncertain", "likely_different"]
    assert len(report["summary"]) > 20
    assert len(report["changes"]) >= 1
    assert len(report["preserved_elements"]) >= 1

    print("--- Real Gemma 4 Report Excerpt ---")
    print(f"Comparison Status: {report['comparison_status']}")
    print(f"Location Assessment: {report['same_location_assessment']}")
    print(f"Summary: {report['summary']}")
    print(f"Changes count: {len(report['changes'])}")
    print(f"Preserved count: {len(report['preserved_elements'])}")
    print("-----------------------------------")
    print("Test 10 (Real Gemma 4 Multimodal Structured Integration): PASS")


def main():
    print("=" * 60)
    print("RUNNING TIMELENS PHASE 3 TEST SUITE")
    print("=" * 60)
    test_1_valid_json()
    test_2_markdown_fenced_json()
    test_3_invalid_json()
    test_4_missing_required_fields()
    test_5_invalid_certainty_values()
    test_6_empty_changes_list()
    test_7_identical_images()
    test_8_unrelated_image_handling()
    test_9_api_error_handling()
    test_10_real_sample_gemma_call()
    print("=" * 60)
    print("ALL 10 PHASE 3 TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()

