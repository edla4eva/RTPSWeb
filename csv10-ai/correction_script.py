import os
import csv
import shutil
from datetime import datetime
from pathlib import Path

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    MODEL_DIR = "./flan_t5_lora_output"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_DIR)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    USE_AI = True
except Exception as e:
    # If model loading fails, continue without AI explanations
    print("Could not load local fine-tuned model for explanations. AI explanations will be skipped.")
    print("Reason:", e)
    tokenizer = None
    model = None
    device = None
    USE_AI = False

def ask_model_explanation(ref_row, cand_row):
    """Ask the LLM for a natural-language explanation (best-effort).
       If no model loaded, returns an empty string.
    """
    if not USE_AI:
        return ""
    instruction = (
        "Compare these two CSV records and correct only the matriculation number if it is wrong.\n\n"
        f"CSV1 (reference): Name={ref_row.get('Name','')}, MatricNo={ref_row.get('MatricNo','')}\n"
        f"CSV2 (candidate): Name={cand_row.get('Name','')}, MatricNo={cand_row.get('MatricNo','')}\n\n"
        "Respond briefly explaining whether a correction is needed and what the correct MatricNo should be."
    )
    inputs = tokenizer(instruction, return_tensors="pt", truncation=True).to(device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=60,
            temperature=0.0,
            do_sample=False
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

def load_csv_rows(path):
    """Return list of OrderedDict rows (as plain dicts) and header order."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [dict(row) for row in reader]
        headers = reader.fieldnames if reader.fieldnames is not None else []
    return rows, headers

def write_csv_rows(path, rows, headers):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            # ensure every header key exists
            row_out = {h: r.get(h, "") for h in headers}
            writer.writerow(row_out)

def main(reference_path="reference.csv", candidate_path="candidate.csv"):
    # check files exist
    if not Path(reference_path).exists():
        raise FileNotFoundError(f"Reference file not found: {reference_path}")
    if not Path(candidate_path).exists():
        raise FileNotFoundError(f"Candidate file not found: {candidate_path}")

    # load both CSVs
    ref_rows, ref_headers = load_csv_rows(reference_path)
    cand_rows, cand_headers = load_csv_rows(candidate_path)

    # build maps keyed by lowercased name for robust matching
    ref_map = {}
    for r in ref_rows:
        name_key = r.get("Name", "").strip().lower()
        if name_key:
            ref_map[name_key] = r

    cand_map = {}
    for r in cand_rows:
        name_key = r.get("Name", "").strip().lower()
        if name_key:
            cand_map[name_key] = r

    # union of headers (preserve candidate headers order first, then any new from reference)
    headers_union = list(cand_headers) if cand_headers else []
    for h in ref_headers:
        if h not in headers_union:
            headers_union.append(h)
    if "Name" not in headers_union:
        headers_union.insert(0, "Name")
    if "MatricNo" not in headers_union:
        # ensure MatricNo exists
        headers_union.append("MatricNo")

    corrected_rows = []
    report_lines = []
    corrections_made = 0
    additions_made = 0

    # process existing candidate rows (preserves candidate order)
    for orig_row in cand_rows:
        name = orig_row.get("Name", "").strip()
        key = name.lower()
        cand_matric = orig_row.get("MatricNo", "").strip()
        if key in ref_map:
            ref_row = ref_map[key]
            ref_matric = ref_row.get("MatricNo", "").strip()

            if cand_matric != ref_matric:
                # ask model for explanation (best-effort)
                explanation = ask_model_explanation(ref_row, orig_row)
                # apply deterministic correction (use reference)
                old_value = cand_matric
                orig_row["MatricNo"] = ref_matric
                corrections_made += 1
                report_lines.append(
                    f"{name}: corrected MatricNo {old_value} -> {ref_matric} | AI: {explanation}"
                )
                print(f"{name}: {old_value} -> {ref_matric}")
            else:
                explanation = ask_model_explanation(ref_row, orig_row)
                report_lines.append(f"{name}: no change needed | AI: {explanation}")
                print(f"{name}: no change")
            corrected_rows.append(orig_row)
        else:
            # candidate has student not in reference — keep as-is, log
            report_lines.append(f"{name}: not found in reference, kept MatricNo={cand_matric}")
            print(f" {name}: not found in reference, kept")
            corrected_rows.append(orig_row)

    # add students present in reference but missing from candidate
    for key, ref_row in ref_map.items():
        if key not in cand_map:
            # create a new row with union headers; fill available values from ref_row
            new_row = {h: ref_row.get(h, "") for h in headers_union}
            corrected_rows.append(new_row)
            additions_made += 1
            report_lines.append(f"{ref_row.get('Name','')}: added to candidate with MatricNo={ref_row.get('MatricNo','')}")
            print(f"Added {ref_row.get('Name','')} to candidate")

    # If corrections or additions happened, archive original candidate file (rename it to mark as wrong)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    if corrections_made > 0 or additions_made > 0:
        archived_name = f"{Path(candidate_path).stem}_wrong_{timestamp}{Path(candidate_path).suffix}"
        archived_path = Path(candidate_path).with_name(archived_name)
        shutil.move(candidate_path, archived_path)  # move original file to archived name
        print(f"Original candidate file moved to: {archived_path}")

    # write corrected CSV back to the original candidate filename
    write_csv_rows(candidate_path, corrected_rows, headers_union)
    print(f"Corrected candidate file written to: {candidate_path}")

    # write report
    report_path = "corrections_report.txt"
    with open(report_path, "w", encoding="utf-8") as rf:
        rf.write("CSV Corrections Report\n")
        rf.write("======================\n")
        rf.write(f"Timestamp: {datetime.now().isoformat()}\n")
        rf.write(f"Original candidate file archived (if changes): { ('yes' if corrections_made or additions_made else 'no') }\n")
        rf.write(f"Corrections made: {corrections_made}\n")
        rf.write(f"Additions made: {additions_made}\n\n")
        for line in report_lines:
            rf.write(line + "\n")
    print(f"Report saved to: {report_path}")

if __name__ == "__main__":
    # call main() with default names. Change args if your files have other names.
    main("reference.csv", "candidate.csv")

