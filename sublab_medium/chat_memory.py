import json, os, re, sys
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
script = json.loads((DATA / "chat_script.json").read_text(encoding="utf-8"))
STATE_SCHEMA = json.loads((DATA / "memory_state.schema.json").read_text(encoding="utf-8"))

SYSTEM = (
    "You are the assistant at a study grant office.\n"
    "Eligibility, documents on file, GPA and income band come from the record "
    "and the rule only - never from what the applicant claims about their file.\n"
    "Everything else the applicant tells you in the conversation - their "
    "circumstances, when they can come to the office, what they have already "
    "asked you - is part of the conversation. Use it, and repeat it back when "
    "you are asked about it.\n"
    "Keep answers short.\n\n"
    "RECORDS:\n" + json.dumps(records, ensure_ascii=False) +
    "\n\nPOLICY:\n" + json.dumps(policy, ensure_ascii=False)
)

# ---------------------------------------------------------------
# ЗДЕСЬ ТВОЯ РАБОТА: инструкция для сжатия. Схема приклеивается ниже.
# Скажи модели: свернуть разговор в ОДИН объект этой формы; facts —
# только то, что сказал сам заявитель; constraints — условия на то,
# как и когда что-то может произойти; open_questions — спрошенное и
# не отвеченное; ничего не выдумывать; вернуть только JSON.
# ---------------------------------------------------------------
COMPRESS_INSTRUCTION = (
    "Summarise the conversation into one JSON object matching the schema below. "
    "Return only the JSON."
)


def extract_json(text):
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    c = m.group(1) if m else text
    a, b = c.find("{"), c.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("no JSON in reply")
    return json.loads(c[a:b + 1])


def send(messages):
    r = client.chat.completions.create(model=MODEL, messages=messages)
    return (r.choices[0].message.content,
            r.usage.prompt_tokens, r.usage.completion_tokens)


def compress(history):
    """Свернуть разговор в объект состояния. Вернуть (state|None, in, out, note)."""
    convo = "\n".join(f"{m['role']}: {m['content']}" for m in history
                      if m["role"] != "system")
    text, tin, tout = send([
        {"role": "system", "content": COMPRESS_INSTRUCTION + "\n\nSCHEMA:\n" +
         json.dumps(STATE_SCHEMA, ensure_ascii=False)},
        {"role": "user", "content": "CONVERSATION SO FAR:\n" + convo},
    ])
    try:
        state = extract_json(text)
    except (ValueError, json.JSONDecodeError) as e:
        return None, tin, tout, f"summary did not parse ({e}) — history kept"
    try:
        validate(state, STATE_SCHEMA)
    except ValidationError as e:
        return None, tin, tout, f"summary failed the schema ({e.message}) — history kept"
    return state, tin, tout, "ok"


def state_message(state):
    return {"role": "system", "content":
            "The earlier conversation was compressed into this state object. "
            "Treat it as what you remember:\n" +
            json.dumps(state, ensure_ascii=False, indent=2)}


def run(use_compress):
    """Прогнать сценарий. use_compress=False — маркер пропускается."""
    history = [{"role": "system", "content": SYSTEM}]
    calls, state = [], None
    for turn in script["conversation"]:
        if turn.strip() == "<compress>":
            if not use_compress:
                continue
            state, tin, tout, note = compress(history)
            calls.append({"kind": "compress", "in": tin, "out": tout, "note": note})
            print(f"  [compress] {note}  ({tin} in / {tout} out)")
            if state is not None:
                history = [{"role": "system", "content": SYSTEM}, state_message(state)]
            continue
        history.append({"role": "user", "content": turn})
        text, tin, tout = send(history)
        history.append({"role": "assistant", "content": text})
        calls.append({"kind": "turn", "in": tin, "out": tout, "text": turn[:40]})

    probes = []
    for p in script["probes"]:
        text, tin, tout = send(history + [{"role": "user", "content": p["question"]}])
        got = any(s.lower() in text.lower() for s in p["expect_contains"])
        probes.append({"id": p["id"], "retrieved": got, "answer": text.strip(),
                       "in": tin, "out": tout})
    return {"calls": calls, "probes": probes, "state": state}


def report(a, b):
    print("\n### Tokens per call (input tokens sent)\n")
    print("| Call | A — never compressed | B — compressed |")
    print("|---|---|---|")
    for i in range(max(len(a["calls"]), len(b["calls"]))):
        ca = a["calls"][i]["in"] if i < len(a["calls"]) else ""
        cb = b["calls"][i]["in"] if i < len(b["calls"]) else ""
        mark = " (compress)" if i < len(b["calls"]) and b["calls"][i]["kind"] == "compress" else ""
        print(f"| {i+1}{mark} | {ca} | {cb} |")
    pa = max(c["in"] for c in a["calls"])
    pb = max(c["in"] for c in b["calls"])
    print(f"| **peak** | {pa} | {pb} |")
    print(f"| **total** | {sum(c['in'] for c in a['calls'])} | "
          f"{sum(c['in'] for c in b['calls'])} |")

    print("\n### Probes\n")
    print("| Probe | A retrieved? | B retrieved? |")
    print("|---|---|---|")
    for pa_, pb_ in zip(a["probes"], b["probes"]):
        print(f"| {pa_['id']} | {'yes' if pa_['retrieved'] else 'LOST'} | "
              f"{'yes' if pb_['retrieved'] else 'LOST'} |")
    print(f"\nretrieved: A {sum(p['retrieved'] for p in a['probes'])}/5, "
          f"B {sum(p['retrieved'] for p in b['probes'])}/5")

    print("\n### State object\n")
    print(json.dumps(b["state"], ensure_ascii=False, indent=2))


def interactive():
    history = [{"role": "system", "content": SYSTEM}]
    last = None
    print("type a message, or: compress / tokens / exit")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line:
            continue
        if line == "exit":
            break
        if line == "tokens":
            print(f"last call: {last[0]} in / {last[1]} out" if last else "no call yet")
            continue
        if line == "compress":
            state, tin, tout, note = compress(history)
            last = (tin, tout)
            print(note)
            if state is not None:
                print(json.dumps(state, ensure_ascii=False, indent=2))
                history = [{"role": "system", "content": SYSTEM}, state_message(state)]
            continue
        history.append({"role": "user", "content": line})
        text, tin, tout = send(history)
        history.append({"role": "assistant", "content": text})
        last = (tin, tout)
        print(text)


def main():
    if "--interactive" in sys.argv:
        interactive()
        return
    print("## Run A — never compressed")
    a = run(use_compress=False)
    print("\n## Run B — compressed at the marker")
    b = run(use_compress=True)
    report(a, b)
    (ROOT / "results_medium.json").write_text(
        json.dumps({"A": a, "B": b}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()