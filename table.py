import json
from pathlib import Path

res = json.loads(Path("results_easy.json").read_text(encoding="utf-8"))
enq = json.loads(Path("data/enquiries.json").read_text(encoding="utf-8"))
roles = ["policy_officer", "front_desk", "auditor", "bilingual_clerk"]

print("| Enquiry | " + " | ".join(roles) + " |")
print("|---|---|---|---|---|")
agree = {r: 0 for r in roles}
for e in enq:
    cells = []
    for r in roles:
        p = res[r][e["id"]]["parsed"] or {}
        d = p.get("decision", "?")
        ok = all(
            sorted(p.get(f) or []) == sorted(e["expected"][f])
            if f == "missing_documents" else p.get(f) == e["expected"][f]
            for f in ["found", "decision", "amount", "missing_documents"]
        )
        agree[r] += ok
        cells.append(f"{d} ({'agrees' if ok else 'differs'})")
    print(f"| {e['id']} | " + " | ".join(cells) + " |")
print("| **agrees with expected** | " + " | ".join(f"{agree[r]}/10" for r in roles) + " |")

print("\n--- E-07 bilingual_clerk raw ---")
print(res["bilingual_clerk"]["E-07"]["raw"])
print("\n--- E-03 front_desk raw (decision moved) ---")
print(res["front_desk"]["E-03"]["raw"])