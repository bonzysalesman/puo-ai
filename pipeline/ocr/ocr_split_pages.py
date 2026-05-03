import argparse
import json
import shutil
import subprocess
from pathlib import Path

import fitz


def render_split_images(pdf_path, output_dir, start_page, end_page, dpi):
    output_dir.mkdir(parents=True, exist_ok=True)
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    manifest = []
    doc = fitz.open(pdf_path)
    try:
        for page_idx in range(start_page, end_page + 1):
            page = doc[page_idx]
            rect = page.rect
            mid_x = rect.x0 + (rect.width / 2.0)

            left_rect = fitz.Rect(rect.x0, rect.y0, mid_x, rect.y1)
            right_rect = fitz.Rect(mid_x, rect.y0, rect.x1, rect.y1)

            for col_name, clip_rect in (("left", left_rect), ("right", right_rect)):
                pix = page.get_pixmap(matrix=matrix, clip=clip_rect, alpha=False)
                img_name = f"page_{page_idx + 1:03d}_{col_name}.png"
                img_path = output_dir / img_name
                pix.save(str(img_path))
                manifest.append(
                    {
                        "page_index": page_idx,
                        "page_number": page_idx + 1,
                        "column": col_name,
                        "image": img_name,
                    }
                )
    finally:
        doc.close()
    return manifest


def run_tesseract(manifest, output_dir, lang, psm):
    tesseract_bin = shutil.which("tesseract")
    if not tesseract_bin:
        return False, 0

    ocr_count = 0
    for row in manifest:
        image_path = output_dir / row["image"]
        txt_path = image_path.with_suffix(".txt")
        cmd = [
            tesseract_bin,
            str(image_path),
            str(txt_path.with_suffix("")),
            "-l",
            lang,
            "--psm",
            str(psm),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            row["ocr_text"] = txt_path.name
            ocr_count += 1
        else:
            row["ocr_error"] = proc.stderr.strip()
    return True, ocr_count


def parse_args():
    parser = argparse.ArgumentParser(
        description="Render PDF pages to split-column images and OCR each column with tesseract when available."
    )
    parser.add_argument("--pdf", required=True, help="Path to source PDF.")
    parser.add_argument("--output-dir", default="ocr_splits")
    parser.add_argument("--start-page", type=int, required=True, help="0-based start page index.")
    parser.add_argument("--end-page", type=int, required=True, help="0-based end page index.")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--lang", default="eng")
    parser.add_argument("--psm", type=int, default=6)
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    manifest = render_split_images(
        pdf_path=args.pdf,
        output_dir=output_dir,
        start_page=args.start_page,
        end_page=args.end_page,
        dpi=args.dpi,
    )
    has_tesseract, ocr_count = run_tesseract(
        manifest=manifest,
        output_dir=output_dir,
        lang=args.lang,
        psm=args.psm,
    )
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"Rendered split images: {len(manifest)} -> {output_dir}")
    if has_tesseract:
        print(f"OCR text files written: {ocr_count}")
    else:
        print("Tesseract not found; OCR skipped (images + manifest created).")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
