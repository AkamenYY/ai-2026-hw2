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

rubric = json.loads((DATA / "candidate_rubric.json").read_text(encoding="utf-8"))
STORIES = sorted((DATA / "candidates").glob("story-*.md"))

CV_SCHEMA = {
    "type": "object",
    "properties": {
        "candidate_id": {"type": "string"},
        "full_name": {"type": ["string", "null"]},
        "degree": {"type": ["string", "null"]},
        "graduation_year": {"type": ["integer", "null"]},
        "gpa_4_scale": {"type": ["number", "null"]},
        "gpa_original_scale": {"type": ["string", "null"]},
        "languages": {"type": "array", "items": {"type": "string"}},
        "published_peer_reviewed": {"type": "integer"},
        "not_published": {"type": "array", "items": {"type": "string"}},
        "experience_months": {"type": ["integer", "null"]},
        "ambiguities": {"type": "array", "items": {"type": "string"}},
        "evidence": {"type": "object"},
    },
    "required": ["candidate_id", "full_name", "degree", "graduation_year",
                 "gpa_4_scale", "gpa_original_scale", "languages",
                 "published_peer_reviewed", "not_published",
                 "experience_months", "ambiguities", "evidence"],
}

SHAPE = json.dumps({
    "candidate_id": "story-01", "full_name": "...", "degree": "...",
    "graduation_year": 2025, "gpa_4_scale": 3.8, "gpa_original_scale": "4.0",
    "languages": ["..."], "published_peer_reviewed": 2,
    "not_published": ["title — under review"], "experience_months": 8,
    "ambiguities": [], "evidence": {"gpa_4_scale": "quote from the story"},
}, ensure_ascii=False, indent=2)

# Правила подсчёта берутся из рубрики, чтобы они гарантированно были в промпте.
EXTRACT_PROMPT = (
    "You build a structured record from an applicant's written story. "
    "The story may be in English or Kazakh; the record is always in English.\n\n"
    "RULES — follow them exactly:\n"
    "1. A fact the story does not state is null. Never estimate it. No GPA "
    "means gpa_4_scale is null — do not infer one from the degree, the "
    "university, the distinction, or the tone of the story.\n"
    "2. A GPA on another scale is converted to a 4.0 scale, and the original "
    "scale is recorded in gpa_original_scale.\n"
    "3. A paper counts in published_peer_reviewed only when the story says it "
    "is published or accepted. 'Submitted', 'under review', 'in preparation', "
    "'planned' and 'in press' are NOT published: list them in not_published "
    "and do not count them. A poster or a talk is not a peer-reviewed paper.\n"
    "4. If the story contradicts itself about a field, do not resolve it and "
    "do not average it: the field is null and the contradiction goes in "
    "ambiguities. This applies to every field, not only the GPA.\n"
    "5. experience_months counts months, not jobs. Overlapping periods count "
    "once. A period with no dates is not countable — record it in ambiguities "
    "and count only the months you can count.\n"
    "6. evidence holds a short quote from the story for each field you filled. "
    "If you cannot quote it, the field is null.\n\n"
    "COUNTING RULES FROM THE RUBRIC:\n" +
    json.dumps(rubric["counting_rules"], ensure_ascii=False, indent=2) +
    "\n\nReturn one JSON object in this shape and nothing else:\n" + SHAPE
)

SCORE_PROMPT = (
    "Score this candidate against the rubric below. Return only three integer "
    "scores from 0 to 5, one per criterion, in this JSON shape:\n"
    '{"academic": 0, "research": 0, "experience": 0}\n'
    "Do not compute a total, do not weight anything, do not name a winner — "
    "the program does that.\n\n"
    "RUBRIC:\n" + json.dumps(rubric, ensure_ascii=False, indent=2)
)


def extract_json(text):
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    c = m.group(1) if m else text
    a, b = c.find("{"), c.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("no JSON in reply")
    return json.loads(c[a:b + 1])


def send(system, user, json_mode=True):
    kw = {"model": MODEL,
          "messages": [{"role": "system", "content": system},
                       {"role": "user", "content": user}]}
    if json_mode:
        kw["response_format"] = {"type": "json_object"}
    try:
        r = client.chat.completions.create(**kw)
    except Exception:
        kw.pop("response_format", None)
        r = client.chat.completions.create(**kw)
    return (r.choices[0].message.content,
            r.usage.prompt_tokens, r.usage.completion_tokens)


def extract(path):
    story = path.read_text(encoding="utf-8")
    user = f"CANDIDATE ID: {path.stem}\n\nSTORY:\n{story}"
    out = {"id": path.stem, "parsed": False, "valid": False,
           "record": None, "error": None, "raw": ""}
    text, _, _ = send(EXTRACT_PROMPT, user)
    out["raw"] = text
    try:
        rec = extract_json(text)
    except (ValueError, json.JSONDecodeError) as e:
        out["error"] = f"parse: {e}"
        return out
    out["parsed"] = True
    out["record"] = rec
    try:
        validate(rec, CV_SCHEMA)
        out["valid"] = True
    except ValidationError as e:
        out["error"] = f"schema: {e.message}"
    return out


def score(path, record):
    user = (f"CANDIDATE: {path.stem}\n\nSTORY:\n{path.read_text(encoding='utf-8')}"
            f"\n\nEXTRACTED RECORD:\n{json.dumps(record, ensure_ascii=False, indent=2)}")
    text, _, _ = send(SCORE_PROMPT, user)
    return extract_json(text)


def weighted_total(s):
    """Считает код, не модель."""
    w = {c["id"]: c["weight"] for c in rubric["criteria"]}
    return round(sum(s[k] * w[k] for k in ("academic", "research", "experience")), 2)


def prose_winner():
    stories = "\n\n".join(
        f"=== {p.stem} ===\n{p.read_text(encoding='utf-8')}" for p in STORIES)
    text, _, _ = send(
        "You are on a scholarship committee. There is one funded place.",
        "Read the six applications below and say in prose which candidate "
        "should win, and why.\n\n" + stories, json_mode=False)
    return text.strip()


def nulls(rec):
    return [k for k, v in rec.items()
            if v is None or (isinstance(v, list) and not v and k != "not_published")]


def main():
    results = {}
    print("## Part 1 — extraction\n")
    print("| Story | Parsed? | Valid? | null fields | published | months | ambiguities |")
    print("|---|---|---|---|---|---|---|")
    for p in STORIES:
        r = extract(p)
        results[p.stem] = r
        rec = r["record"] or {}
        print(f"| {p.stem} | {'yes' if r['parsed'] else 'NO'} | "
              f"{'yes' if r['valid'] else 'NO'} | "
              f"{', '.join(k for k, v in rec.items() if v is None) or '—'} | "
              f"{rec.get('published_peer_reviewed', '?')} | "
              f"{rec.get('experience_months', '?')} | "
              f"{len(rec.get('ambiguities', []))} |")

    print("\n## Part 2 — scores and the winner\n")
    print("| Candidate | academic | research | experience | weighted total (code) |")
    print("|---|---|---|---|---|")
    totals = {}
    for p in STORIES:
        r = results[p.stem]
        if not r["record"]:
            print(f"| {p.stem} | — | — | — | not extracted |")
            continue
        s = score(p, r["record"])
        t = weighted_total(s)
        totals[p.stem] = t
        r["scores"] = s
        r["total"] = t
        print(f"| {p.stem} | {s['academic']} | {s['research']} | "
              f"{s['experience']} | {t} |")

    ranked = sorted(totals.items(), key=lambda kv: -kv[1])
    print(f"\n**Winner, computed by my code:** {ranked[0][0]} ({ranked[0][1]})")
    if len(ranked) > 1:
        gap = round(ranked[0][1] - ranked[1][1], 2)
        print(f"Runner-up: {ranked[1][0]} ({ranked[1][1]}) — gap {gap}")

    print("\n**The model's prose answer, asked separately:**\n")
    prose = prose_winner()
    print(prose)

    (ROOT / "results_hard.json").write_text(json.dumps(
        {"extractions": results, "totals": totals, "ranked": ranked,
         "prose": prose}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
