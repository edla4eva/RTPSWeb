import csv, json

def create_from_csvs(master_csv, candidate1_csv, out_jsonl="train.jsonl"):
    # Load master
    master = {}
    with open(master_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            master[r["Name"].strip()] = r["MatricNumber"].strip()

    
    candidate1_rows = []
    with open(candidate1_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            candidate1_rows.append({
                "Name": r["Name"].strip(),
                "MatricNumber": r["MatricNumber"].strip()
            })

    # Write JSONL
    with open(out_jsonl, "w", encoding='utf-8') as fout:
        for row in candidate1_rows:
            name = row["Name"]
            cand = row["MatricNumber"]
            truth = master.get(name, "")
            if truth == "":
                continue

            instr = f"Compare: File1: {name} {truth} | File2: {name} {cand}"
            if truth == cand:
                out = f"{name}'s matric number matches. No correction needed."
            else:
                out = f"Correct {name}'s matric number from {cand} to {truth}."
            fout.write(json.dumps({"instruction": instr, "output": out}) + "\n")

    print("train.jsonl created with examples.")

if __name__ == "__main__":
    create_from_csvs("master.csv", "candidate1.csv")

