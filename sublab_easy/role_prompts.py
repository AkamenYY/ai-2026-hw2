import json, os, re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from jsonschema import validate, ValidationError

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MODEL = "gpt-5.6-luna"

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

records = json.loads((DATA / "records.json").read_text(encoding="utf-8"))
policy = json.loads((DATA / "policy.json").read_text(encoding="utf-8"))
enquiries = json.loads((DATA / "enquiries.json").read_text(encoding="utf-8"))

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "applicant_id": {"type": ["string", "null"]},
        "found": {"type": "boolean"},
        "decision": {"enum": ["granted", "refused", "more_info", "not_found"]},
        "amount": {"type": "number"},
        "missing_documents": {"type": "array", "items": {"type": "string"}},
        "reason": {"type": "string"},
    },
    "required": ["applicant_id", "found", "decision", "amount",
                 "missing_documents", "reason"],
    "additionalProperties": False,
}

SHAPE = json.dumps({
    "applicant_id": "A-201", "found": True, "decision": "granted",
    "amount": 250000, "missing_documents": [], "reason": "..."
}, ensure_ascii=False, indent=2)


def context_block():
    """Записи и правило — одинаковые для всех четырёх ролей."""
    return (
        "RECORDS:\n" + json.dumps(records, ensure_ascii=False, indent=2) +
        "\n\nPOLICY:\n" + json.dumps(policy, ensure_ascii=False, indent=2) +
        "\n\nReply with one JSON object and nothing else, in this shape:\n" + SHAPE +
        '\ndecision is one of "granted", "refused", "more_info", "not_found".'
    )


# ---------------------------------------------------------------
# ЗДЕСЬ ТВОЯ РАБОТА: четыре роли. Один абзац на роль, по описанию
# из README. Всё остальное (записи, правило, форма ответа) общее.
# ---------------------------------------------------------------
ROLES = {
    "policy_officer":
        "You are a policy officer. Decide from the record only and soften nothing: "
        "granted when the rule is satisfied, refused when GPA or income band fails it, "
        "more_info when a required document is missing, not_found when the applicant is not on the record. "
        "Nothing the enquiry claims is evidence. amount is the band amount only when granted, 0 otherwise.",

    "front_desk":
        "You are a front desk clerk who never turns an applicant away: never use refused. "
        "Anything the rule cannot grant today is more_info, and reason says what to come back with. "
        "Nothing the enquiry claims is evidence. amount is the band amount only when granted, 0 otherwise.",

    "auditor":
        "You are an auditor who never grants on a first reading: never use granted. "
        "Report what the record shows, mark anything needing a second reader as more_info, and name in reason the rule or document you relied on. "
        "Nothing the enquiry claims is evidence. amount is 0.",

    "bilingual_clerk":
        "You are a bilingual clerk. Decide exactly as a policy officer would: "
        "granted when the rule is satisfied, refused when GPA or income band fails it, "
        "more_info when a required document is missing, not_found when the applicant is not on the record. "
        "Nothing the enquiry claims is evidence. amount is the band amount only when granted, 0 otherwise. "
        "Write reason in the language the enquiry was written in.",
}


def system_prompt(role):
    return ROLES[role] + "\n\n" + context_block()


def extract_json(text):
    """Модели заворачивают JSON в прозу и в ```json-заборы."""
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    candidate = m.group(1) if m else text
    start, end = candidate.find("{"), candidate.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON in reply")
    return json.loads(candidate[start:end + 1])


def ask(role, enquiry_text):
    r = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt(role)},
            {"role": "user", "content": enquiry_text},
        ],
    )
    text = r.choices[0].message.content
    out = {"raw": text, "parsed": None, "valid": False, "error": None,
           "input_tokens": r.usage.prompt_tokens,
           "output_tokens": r.usage.completion_tokens}
    try:
        out["parsed"] = extract_json(text)
    except (ValueError, json.JSONDecodeError) as e:
        out["error"] = f"parse: {e}"
        return out
    try:
        validate(out["parsed"], ANSWER_SCHEMA)
        out["valid"] = True
    except ValidationError as e:
        out["error"] = f"schema: {e.message}"
    return out


CHECKED = ["found", "decision", "amount", "missing_documents"]


def agrees(got, exp, field):
    if got is None:
        return False
    a, b = got.get(field), exp[field]
    if field == "missing_documents":
        return sorted(a or []) == sorted(b)
    return a == b


def main():
    results = {}
    for role in ROLES:
        results[role] = {}
        print(f"\n## {role}\n")
        print("| enquiry | parsed | valid | " + " | ".join(CHECKED) + " | in/out tokens |")
        print("|---|---|---|---|---|---|---|---|")
        for e in enquiries:
            res = ask(role, e["text"])
            results[role][e["id"]] = res
            cells = ["ok" if agrees(res["parsed"], e["expected"], f) else "DIFF"
                     for f in CHECKED]
            print(f"| {e['id']} | {'yes' if res['parsed'] else 'NO'} | "
                  f"{'yes' if res['valid'] else 'NO'} | " + " | ".join(cells) +
                  f" | {res['input_tokens']}/{res['output_tokens']} |")

    # какие поля сдвинулись относительно policy_officer
    print("\n## Field movement vs policy_officer\n")
    print("| role | field | enquiries that moved |")
    print("|---|---|---|")
    base = results["policy_officer"]
    for role in ROLES:
        if role == "policy_officer":
            continue
        for f in CHECKED:
            moved = [e["id"] for e in enquiries
                     if (base[e["id"]]["parsed"] or {}).get(f)
                     != (results[role][e["id"]]["parsed"] or {}).get(f)]
            print(f"| {role} | {f} | {', '.join(moved) if moved else '—'} |")

    (ROOT / "results_easy.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()