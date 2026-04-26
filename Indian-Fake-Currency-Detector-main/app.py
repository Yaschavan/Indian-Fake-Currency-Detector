from pathlib import Path
import shutil

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from Helper import analyze_note_image


app = Flask(__name__)
OUTPUT_DIR = Path("static/Output")
SORTED_DIR = Path("static/Sorted")
REAL_THRESHOLD = 0.65
SUPPORTED_NOTES = {"10", "20", "50", "100", "200", "500"}


def ensure_output_dirs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SORTED_DIR.mkdir(parents=True, exist_ok=True)

    for note_value in SUPPORTED_NOTES:
        (SORTED_DIR / note_value).mkdir(parents=True, exist_ok=True)


def clear_output_dir():
    ensure_output_dirs()

    for directory in (OUTPUT_DIR, SORTED_DIR):
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                file_path.unlink()

    ensure_output_dirs()


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/index/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    images = [img for img in request.files.getlist("image") if img and img.filename]
    option = request.form.get("optradio")

    if not images:
        return render_template("index.html", error="Please upload at least one note image.")

    if option and option not in SUPPORTED_NOTES:
        return render_template("index.html", error="Please select a supported note value.")

    clear_output_dir()

    results = []
    genuine_count = 0
    fake_count = 0
    detected_count = 0
    undetected_count = 0
    genuine_total = 0
    note_breakdown = {note_value: 0 for note_value in sorted(SUPPORTED_NOTES, key=int)}

    for index, img in enumerate(images, start=1):
        filename = secure_filename(img.filename) or f"note_{index}.jpg"
        saved_image = OUTPUT_DIR / filename
        img.save(saved_image)

        analysis = analyze_note_image(str(saved_image), option or None)
        score = analysis["score"]
        detected_note = analysis["note_type"]
        is_genuine = detected_note is not None and score >= REAL_THRESHOLD
        detection_status = "Denomination could not be detected."
        sorted_path = None

        if detected_note is not None:
            detected_count += 1
            note_breakdown[detected_note] += 1
            sorted_path = SORTED_DIR / detected_note / filename
            shutil.copy2(saved_image, sorted_path)
            detection_status = f"Detected as Rs. {detected_note}"
        else:
            undetected_count += 1

        if is_genuine:
            genuine_count += 1
            genuine_total += int(detected_note)
            authenticity_status = "The note is Genuine"
        elif detected_note is not None:
            fake_count += 1
            authenticity_status = "The note is Fake"
        else:
            authenticity_status = "Authenticity could not be checked because the denomination was not detected."

        results.append(
            {
                "filename": filename,
                "image_path": saved_image.as_posix(),
                "sorted_path": sorted_path.as_posix() if sorted_path else None,
                "note_value": detected_note,
                "detection_status": detection_status,
                "status": authenticity_status,
                "score": round(score * 100, 2),
            }
        )

    summary = {
        "uploaded_count": len(results),
        "detected_count": detected_count,
        "undetected_count": undetected_count,
        "genuine_count": genuine_count,
        "fake_count": fake_count,
        "genuine_total": genuine_total,
        "selected_note_value": option,
        "note_breakdown": {key: value for key, value in note_breakdown.items() if value},
    }

    return render_template("prediction.html", results=results, summary=summary)


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/timeline/")
def timeline():
    return render_template("timeline.html")


if __name__ == "__main__":
    app.run(debug=True)
