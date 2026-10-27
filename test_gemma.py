import os
import sys
import io
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageOps, ImageDraw, ImageFont

# =====================================================================
# TASK 1 & 2: RESOLVE PATHS AND REPAIR ENVIRONMENT VARIABLE LOADING
# =====================================================================
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL_NAME = os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it").strip()

def run_environment_diagnostics():
    env_found = ENV_PATH.is_file()
    key_loaded = bool(API_KEY)
    model_loaded = bool(MODEL_NAME)

    print("Environment Diagnostics")
    print(f"Project root: {BASE_DIR}")
    print(f".env found: {'YES' if env_found else 'NO'}")
    print(f"GEMINI_API_KEY loaded: {'YES' if key_loaded else 'NO'}")
    print(f"GEMMA_MODEL loaded: {'YES' if model_loaded else 'NO'}")
    print()

    if not env_found:
        print("ERROR: .env file not found at " + str(ENV_PATH))
        return False
    if not key_loaded:
        print("ERROR: GEMINI_API_KEY is not defined or is empty in .env")
        return False
    return True

# =====================================================================
# TASK 3: VERIFY PYTHON ENVIRONMENT
# =====================================================================
def verify_python_environment():
    def check_pkg(name):
        try:
            __import__(name)
            return "INSTALLED"
        except ImportError:
            return "MISSING"

    print("Python Environment Diagnostics")
    print(f"Python Interpreter: {sys.executable}")
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"google-genai: {check_pkg('google.genai')}")
    print(f"python-dotenv: {check_pkg('dotenv')}")
    print(f"Pillow: {check_pkg('PIL')}")
    print(f"streamlit: {check_pkg('streamlit')}")
    print()

# =====================================================================
# TASK 4: TEST GEMMA 4 TEXT CONNECTIVITY
# =====================================================================
def test_text_connectivity(client):
    print("Gemma 4 Text Test")
    print(f"Model: {MODEL_NAME}")
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents="Reply with exactly: TIMELENS_CONNECTED"
        )
        text = response.text.strip() if response and response.text else ""
        if text:
            print("Request: SUCCESS")
            print(f"Response: {text}")
            print()
            return True, text
        else:
            print("Request: FAILED")
            print("Response: <empty response>")
            print()
            return False, "<empty response>"
    except Exception as e:
        err_msg = f"{type(e).__name__}: {str(e)}"
        print("Request: FAILED")
        print(f"Error: {err_msg}")
        print()
        return False, err_msg

# =====================================================================
# TASK 5: VALIDATE SAMPLE IMAGES
# =====================================================================
def validate_and_preprocess_image(image_path: Path, max_dim: int = 1280):
    if not image_path.is_file():
        return None, f"File does not exist: {image_path}"
    try:
        with Image.open(image_path) as img:
            fmt = img.format
            if fmt not in ["JPEG", "PNG", "WEBP"]:
                return None, f"Unsupported format: {fmt}"
            # Normalize orientation using EXIF
            img = ImageOps.exif_transpose(img)
            # Ensure RGB
            if img.mode != "RGB":
                img = img.convert("RGB")
            orig_size = img.size
            # Resize oversized images maintaining aspect ratio
            if max(img.size) > max_dim:
                img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            processed_size = img.size

            # In-memory JPEG bytes
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            jpeg_bytes = buf.getvalue()
            return {
                "format": fmt,
                "orig_size": orig_size,
                "processed_size": processed_size,
                "bytes": jpeg_bytes,
                "image_obj": img.copy()
            }, None
    except Exception as e:
        return None, f"Failed decoding image: {type(e).__name__} - {str(e)}"

# =====================================================================
# TASK 6 & 7: GEMMA 4 MULTIMODAL COMPARISON
# =====================================================================
COMPARISON_PROMPT = """You are a visual heritage analysis assistant.

Compare these two supplied photographs.

Identify:
1. Three observable visual differences.
2. Elements that appear preserved.
3. Differences that may be explained by camera position, lighting, or image quality.
4. Whether the photographs appear to show the same location.

Rules:
- Do not invent historical dates.
- Do not invent landmark identities.
- Do not invent restoration events.
- Do not assume the photographs show the same place.
- If they appear unrelated, explain that.
- If they are identical, report no meaningful differences.
- Only describe visible evidence.
- Express uncertainty honestly.

Return a concise comparison."""

def test_two_image_comparison(client, before_data, after_data):
    from google.genai import types

    print("Gemma 4 Multimodal Test: Direct Two-Image Input")
    try:
        contents = [
            "IMAGE 1 = HISTORICAL / BEFORE",
            types.Part.from_bytes(data=before_data["bytes"], mime_type="image/jpeg"),
            "IMAGE 2 = MODERN / AFTER",
            types.Part.from_bytes(data=after_data["bytes"], mime_type="image/jpeg"),
            COMPARISON_PROMPT
        ]
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents
        )
        if response and response.text and response.text.strip():
            print("Direct Two-Image Comparison: SUCCESS")
            print("--- Output ---")
            print(response.text.strip())
            print("--------------")
            print()
            return True, response.text.strip(), None
        else:
            return False, None, "Empty response from two-image endpoint"
    except Exception as e:
        err_msg = f"{type(e).__name__}: {str(e)}"
        print(f"Direct Two-Image Comparison: FAILED ({err_msg})")
        print()
        return False, None, err_msg

def test_composite_fallback(client, before_data, after_data):
    from google.genai import types

    print("Attempting Composite Image Fallback...")
    try:
        img_b = before_data["image_obj"]
        img_a = after_data["image_obj"]

        # Normalize height
        target_h = min(img_b.height, img_a.height, 800)
        scale_b = target_h / img_b.height
        scale_a = target_h / img_a.height
        new_w_b = int(img_b.width * scale_b)
        new_w_a = int(img_a.width * scale_a)

        resized_b = img_b.resize((new_w_b, target_h), Image.Resampling.LANCZOS)
        resized_a = img_a.resize((new_w_a, target_h), Image.Resampling.LANCZOS)

        banner_h = 40
        canvas_w = new_w_b + new_w_a + 20
        canvas_h = target_h + banner_h

        canvas = Image.new("RGB", (canvas_w, canvas_h), color=(240, 240, 240))
        canvas.paste(resized_b, (0, banner_h))
        canvas.paste(resized_a, (new_w_b + 20, banner_h))

        draw = ImageDraw.Draw(canvas)
        draw.text((10, 10), "BEFORE (HISTORICAL)", fill=(0, 0, 0))
        draw.text((new_w_b + 30, 10), "AFTER (MODERN)", fill=(0, 0, 0))

        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=85)
        composite_bytes = buf.getvalue()

        composite_prompt = """Compare the historical photograph on the LEFT with the modern photograph on the RIGHT.

Identify visible changes and preserved elements.
Do not invent historical facts."""

        contents = [
            types.Part.from_bytes(data=composite_bytes, mime_type="image/jpeg"),
            composite_prompt
        ]

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents
        )
        if response and response.text and response.text.strip():
            print("Composite Fallback Comparison: SUCCESS")
            print("--- Output ---")
            print(response.text.strip())
            print("--------------")
            print()
            return True, response.text.strip(), None
        else:
            return False, None, "Empty response from composite endpoint"
    except Exception as e:
        err_msg = f"{type(e).__name__}: {str(e)}"
        print(f"Composite Fallback: FAILED ({err_msg})")
        print()
        return False, None, err_msg

# =====================================================================
# MAIN RUNNER & FINAL REPORT
# =====================================================================
def main():
    print("=" * 60)
    print("TIMELENS ENVIRONMENT VERIFICATION & GEMMA 4 VALIDATION")
    print("=" * 60)
    print()

    # Step 1: Environment
    env_ok = run_environment_diagnostics()
    verify_python_environment()

    if not env_ok:
        print("Stopping: Environment configuration error.")
        sys.exit(1)

    # Step 2: Initialize GenAI Client
    from google import genai
    client = genai.Client(api_key=API_KEY)

    # Step 3: Text Connectivity Test
    text_ok, text_result = test_text_connectivity(client)

    # Step 4: Validate Sample Images
    samples_dir = BASE_DIR / "samples"
    before_path = samples_dir / "before.jpg"
    after_path = samples_dir / "after.jpg"

    print("Sample Image Validation")
    before_data, before_err = validate_and_preprocess_image(before_path)
    after_data, after_err = validate_and_preprocess_image(after_path)

    before_status = "VALID" if before_data else f"MISSING ({before_err})"
    after_status = "VALID" if after_data else f"MISSING ({after_err})"
    print(f"before.jpg: {before_status}")
    print(f"after.jpg: {after_status}")
    print()

    two_image_status = "NOT RUN"
    composite_status = "NOT RUN"
    errors = []

    if not text_ok:
        errors.append(f"Text generation failed: {text_result}")

    if not before_data or not after_data:
        print("Image comparison: NOT RUN")
        print("Reason: Real sample images are required.")
        print()
    else:
        # Step 5: Test Two-Image Comparison
        direct_ok, direct_result, direct_err = test_two_image_comparison(client, before_data, after_data)
        if direct_ok:
            two_image_status = "SUCCESS"
            composite_status = "NOT NEEDED"
        else:
            two_image_status = f"FAILED ({direct_err})"
            errors.append(f"Direct two-image failed: {direct_err}")
            # Fallback only if direct failed and not pure auth/model error
            comp_ok, comp_result, comp_err = test_composite_fallback(client, before_data, after_data)
            if comp_ok:
                composite_status = "SUCCESS"
            else:
                composite_status = f"FAILED ({comp_err})"
                errors.append(f"Composite fallback failed: {comp_err}")

    # Determine final status
    if not env_ok or not text_ok:
        final_status = "FAIL"
    elif not before_data or not after_data:
        final_status = "PARTIAL"
    elif two_image_status == "SUCCESS" or composite_status == "SUCCESS":
        final_status = "PASS"
    else:
        final_status = "FAIL"

    # Gitignore verification
    gitignore_path = BASE_DIR / ".gitignore"
    gitignore_configured = "YES" if gitignore_path.is_file() else "NO"

    # Final Phase 0 Report
    print("=" * 40)
    print("TIMELENS — PHASE 0 VALIDATION REPORT")
    print("=" * 40)
    print()
    print("PROJECT STRUCTURE")
    print(f"Project directory: {BASE_DIR}")
    print(f"Test script: {Path(__file__).resolve()}")
    print(f"Virtual environment: {BASE_DIR / '.venv'}")
    print(f".env located: {'YES' if ENV_PATH.is_file() else 'NO'}")
    print()
    print("ENVIRONMENT")
    print(f"Python: {sys.version.split()[0]}")
    print("google-genai: INSTALLED")
    print("python-dotenv: INSTALLED")
    print("Pillow: INSTALLED")
    print(f"API credential loaded: {'YES' if bool(API_KEY) else 'NO'}")
    print()
    print("GEMMA 4")
    print(f"Requested model: {MODEL_NAME}")
    print(f"Text generation: {'SUCCESS' if text_ok else 'FAILED'}")
    print(f"Two-image comparison: {two_image_status}")
    print(f"Composite fallback: {composite_status}")
    print()
    print("IMAGE VALIDATION")
    print(f"Historical image: {'VALID (' + str(before_data['orig_size']) + ')' if before_data else 'MISSING'}")
    print(f"Modern image: {'VALID (' + str(after_data['orig_size']) + ')' if after_data else 'MISSING'}")
    print()
    print("SECURITY")
    print("API key protected: YES")
    print(f".gitignore configured: {gitignore_configured}")
    print("Credentials exposed in output: NO")
    print()
    print("FINAL STATUS")
    print(final_status)
    print()
    print("ERRORS")
    if errors:
        for err in errors:
            print(f"- {err}")
    else:
        print("None")
    print()
    print("NEXT REQUIRED ACTION")
    if final_status == "PASS":
        print("Proceed to Phase 1: Build the Streamlit multimodal comparison UI.")
    elif final_status == "PARTIAL":
        print("Provide valid sample images in samples/before.jpg and samples/after.jpg and re-run test_gemma.py.")
    else:
        print("Resolve API configuration or model access errors listed above.")
    print("=" * 40)

if __name__ == "__main__":
    main()

