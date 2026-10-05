# HW2 submission

**Name:** Madiyar Tokbergen
**Student ID:** S23068824
**Group:** css4007-eng-10
**Repository:** https://github.com/AkamenYY/ai-2026-hw2

## AI tool disclosure

State which AI tools you used and for what. Expected and fine; undisclosed use
is not. If you used a model to help you draft a prompt, say which prompt.

> I used Claude for the plumbing code in all three sublabs (the API calls, JSON
> extraction, schema validation, table printing), for drafting the four role
> prompts in Sublab Easy and the extraction rules in Sublab Hard, and for
> drafting the written answers below, which I checked against my own runs and
> edited. Every number and every quoted reply in this file is from my runs.

---

## Sublab Easy — one task, four roles

### Decisions per role

One row per enquiry. In each cell write the `decision` your run returned, and
whether it agrees with `expected` in `data/enquiries.json`:

| Enquiry | policy_officer | front_desk | auditor | bilingual_clerk |
|---|---|---|---|---|
| E-01 | granted (agrees) | granted (agrees) | more_info (differs) | granted (agrees) |
| E-02 | more_info (agrees) | more_info (agrees) | refused (differs) | more_info (agrees) |
| E-03 | refused (agrees) | more_info (differs) | refused (agrees) | refused (agrees) |
| E-04 | refused (agrees) | more_info (differs) | refused (agrees) | refused (agrees) |
| E-05 | granted (agrees) | granted (agrees) | more_info (differs) | granted (agrees) |
| E-06 | granted (agrees) | granted (agrees) | more_info (differs) | granted (agrees) |
| E-07 | granted (agrees) | granted (agrees) | more_info (differs) | granted (agrees) |
| E-08 | not_found (agrees) | more_info (differs) | not_found (agrees) | not_found (agrees) |
| E-09 | refused (agrees) | more_info (differs) | refused (agrees) | refused (agrees) |
| E-10 | more_info (agrees) | more_info (agrees) | more_info (agrees) | more_info (agrees) |
| **agrees with `expected`** | 10/10 | 6/10 | 5/10 | 10/10 |
| **parsed** | 10/10 | 10/10 | 10/10 | 10/10 |
| **schema-valid** | 10/10 | 10/10 | 10/10 | 10/10 |

### Which field moved, on which enquiry, under which role

| Field | Enquiries that moved | Role(s) that moved it |
|---|---|---|
| `found` | none — it moved on no enquiry under any role | — |
| `decision` | E-03, E-04, E-08, E-09 | front_desk |
| `decision` | E-01, E-02, E-05, E-06, E-07 | auditor |
| `amount` | E-01, E-05, E-06, E-07 | auditor |
| `missing_documents` | none — it moved on no enquiry under any role | — |

Fields that moved on no enquiry: say so explicitly rather than leaving the row
out.

### Raw replies

Paste the full reply for **one enquiry where a role changed the decision** away
from the policy officer's:

E-03 under front_desk (policy_officer returned `refused` on the same enquiry):

```json
{
  "applicant_id": "A-203",
  "found": true,
  "decision": "more_info",
  "amount": 0,
  "missing_documents": [],
  "reason": "Please come back with an updated transcript showing a GPA of at least 2.67; the record currently shows a GPA of 2.4."
}
```

Paste the full reply for **E-07 (the Kazakh enquiry)** from the bilingual
clerk, so the `reason` language is visible:

```json
{
  "applicant_id": "A-201",
  "found": true,
  "decision": "granted",
  "amount": 250000,
  "missing_documents": [],
  "reason": "Сіз грант талаптарына сай келесіз: GPA 3.4, табыс санаты 1 және қажетті құжаттардың екеуі де бар. Грант мөлшері — 250 000 теңге."
}
```

### Written answers

**1. Which fields are role-sensitive and which are not?** Point at rows in your
tables.

> `found` and `missing_documents` never moved — they come straight from the
> record. `decision` moved under two roles: front_desk on E-03, E-04, E-08,
> E-09, auditor on E-01, E-02, E-05, E-06, E-07. `amount` moved only where
> auditor turned `granted` into `more_info`, so it follows the decision rather
> than the role. bilingual_clerk moved nothing structural: 10/10, only `reason`
> changed language.

**2. Which enquiries are most sensitive to the role, and why those?** Say what
E-03, E-04, E-07 and E-10 are each testing.

> E-03 and E-04 are genuine refusals (GPA 2.4, band 3) and front_desk turned
> both into `more_info` because it may not refuse. E-08 is the applicant who is
> not on the record, and front_desk made that `more_info` too while `found`
> stayed false. E-07 is E-01 in Kazakh: only `reason` changed. E-10 claims a
> document the record does not show, and no role believed the claim.

**3. Where does discretion belong — the role paragraph, or code that reads
`decision` afterwards?** Say what a downstream program can and cannot tell
about which role produced a record.

> In code. A program reading `decision: more_info` cannot tell E-02, where a
> document really is missing, from E-03 under front_desk, where the documents
> are there and the GPA is too low. The field is identical and the role is not
> in the JSON.

**4. Is a role a boundary?** Say in Week 2 terms what the role paragraph is
made of, and what you would put in code — not in the prompt — if a wrong
`decision` were expensive.

> No. The role paragraph is tokens in the same stream as the enquiry, so it is
> a tendency, not a rule. front_desk said the GPA was 2.4, below 2.67, and
> still returned `more_info` with advice that cannot be followed; on E-08 it
> produced a reply saying the person does not exist and asking them to bring a
> document. auditor went the other way on E-02, refusing where the rule only
> wanted more information. If a wrong decision were expensive I would evaluate
> the rule in code and send disagreements to a human.

---

## Sublab Medium — memory you choose

### Tokens per call

Input tokens sent on each call. In run B, call 10 is the compression call
itself; the twelve scripted turns are the same in both runs.

| Call | A — never compressed | B — compressed at the `compress` turn |
|---|---|---|
| 1 | 731 | 731 |
| 2 | 785 | 785 |
| 3 | 846 | 838 |
| 4 | 900 | 907 |
| 5 | 949 | 970 |
| 6 | 1015 | 1044 |
| 7 | 1072 | 1125 |
| 8 | 1147 | 1198 |
| 9 | 1207 | 1270 |
| 10 (compress in B) | 1269 | 862 |
| 11 | 1315 | 946 |
| 12 | — | 1014 |
| **peak** | 1315 | 1270 |
| **total for the run** | 11236 | 11690 |

### Probes after the conversation

| Probe | Tests | A retrieved? | A answer | B retrieved? | B answer |
|---|---|---|---|---|---|
| Q-1 identity | turn 1 | yes | "You are **Daniyar Qoshan**, applicant **A-202**." | yes | "You are **Daniyar Qoshan**, applicant **A-202**." |
| Q-2 missing document | turn 5 | yes | "Your **ID card** is still missing. Your transcript is on file." | yes | "Your **ID card** is still missing from the file." |
| Q-3 band and amount | turns 3-4 | yes | "Your recorded income band is **2**, corresponding to a grant amount of **150,000 KZT**." | yes | "Your record shows **income band 2**, which corresponds to **150,000 KZT**." |
| Q-4 the constraint | turn 6 | yes | "You said you can come to the office **on Thursdays**, because you have lab all week otherwise." | yes | "You can come to the office on **Thursdays**." |
| Q-5 the open question | turn 7 | yes | "You asked whether a **scanned letter from your employer** would count or whether you needed to provide the original." | yes (but wrong) | "You asked whether an **employer letter could replace the ID card**. It cannot." |
| **retrieved** | | 5/5 | | 5/5 (4/5 in substance) | |

Q-5 counts as retrieved because `expect_contains` looks for "letter" and
"employer", and both words are there. The answer is not the question the
applicant asked: in turn 7 he asked whether a *scan* would do or whether the
*original* was needed. Run B answered a different question, and added a ruling
("it cannot") that nobody in the conversation ever made.

### The state my compression produced

```json
{
  "applicant_id": "A-202",
  "topic": "Study grant eligibility and required documents",
  "facts": [
    "The applicant's name is Daniyar Qoshan.",
    "The applicant sent their transcript last week.",
    "The applicant's family certificate states income band 2.",
    "The applicant could not upload the ID card because the scanner at home broke.",
    "The applicant's sister Aruzhan applied last year and is also on file."
  ],
  "decisions": [],
  "constraints": [
    "The applicant can come to the office only on Thursdays because they have laboratory work during the rest of the week.",
    "The application requires the transcript and ID card; an employer letter does not replace the ID card."
  ],
  "open_questions": [
    "Whether the grant decision will be made on the same day the ID card is submitted remains unconfirmed."
  ],
  "language": "English and Kazakh"
}
```

An earlier run produced a summary that did not parse (`Expecting ',' delimiter`).
The program reported it, kept the history and carried on, so that run simply
behaved like run A. A retry and a JSON response format were added after that.

### Written answers

**1. What did compression buy?** Peak tokens both ways, probes retrieved both
ways, and — if a probe was lost — which one and which turn it came from.

> Almost nothing here. Peak 1315 in A against 1270 in B, and B cost more in
> total (11690 against 11236) because the compression call itself cost 862
> input tokens. No probe was lost by the string check, 5/5 both ways. The gain
> shows after the marker: A's last calls were 1269 and 1315 and still climbing,
> B's fell back to 946 and 1014. Twelve turns is too short to pay that back;
> fifty would not be.

**2. Why must the state be structured rather than a paragraph?** You could have
asked for "a summary". Say what changes when the summary is an object with
named fields.

> My instruction was one sentence; the schema did the work. Because
> `constraints` and `open_questions` are named fields, the model had to find
> something to put in them, which is how the Thursday constraint survived — a
> paragraph would have been about the document and the amount. A shape can also
> be checked: one run returned broken JSON, `jsonschema` caught it and the
> history was kept. A paragraph is always valid, so nothing can be caught.

**3. What is missing from your state that you would add?** Name what you would
add and what you would drop to pay for it.

> `decisions` came back empty every run, so what the office already told the
> applicant is not carried forward. I would also separate what he *claimed*
> from what the record *shows* — my `facts` mixes the two, and the policy
> depends on that difference. To pay for it I would drop `topic` and `language`.

**4. When is compression the wrong choice?** Name a conversation where it would
lose something that cannot be recovered, and say whether your program would
notice.

> Whenever the exact wording matters — a complaint, an appeal, a dispute about
> who said what. My run shows a small version: the applicant asked whether a
> *scanned* employer letter counts or whether the *original* is needed, and
> after compression run B reported he had asked whether the letter could
> *replace the ID card*, answering "it cannot" — a ruling nobody made. My
> program did not notice and could not: it validates the shape, not the truth,
> and the probe passed because "letter" and "employer" were present.

---

## Sublab Hard — stories in, CVs out, the best candidate by code

### Part 1 — extraction

All six parsed and validated on the first attempt.

| Story | Parsed? | Valid? | Fields that came back `null` | Traps hit |
|---|---|---|---|---|
| story-01 | yes | yes | none | none — the clean story: GPA 3.8/4.0, 2 published, 8 months |
| story-02 | yes | yes | `gpa_4_scale`, `gpa_original_scale` | **no GPA stated** — a distinction but no number, and no number was invented |
| story-03 | yes | yes | none | **GPA on another scale** — 4.6/5.0 converted to 3.68, scale recorded as "5.0"; the paper under review was not counted |
| story-04 | yes | yes | none | **a paper that is not published** — four listed, `published_peer_reviewed` = 1, three in `not_published` |
| story-05 | yes | yes | none | Kazakh source; 1 published, the paper still being written was not counted |
| story-06 | yes | yes | `graduation_year`, `gpa_4_scale`, `gpa_original_scale` | **contradicts itself twice** — GPA 3.2 vs 3.5, graduated-2024 vs graduating-2026; the poster was not counted |

The four traps, for reference: no GPA stated · a GPA on another scale · a paper
that is not published · a story that contradicts itself.

Paste the extraction for **story-06**, the one that contradicts itself:

```json
{
  "candidate_id": "story-06",
  "full_name": "Nurzhan Abilov",
  "degree": "BSc in Statistics",
  "graduation_year": null,
  "gpa_4_scale": null,
  "gpa_original_scale": null,
  "languages": ["Kazakh", "Russian", "English"],
  "published_peer_reviewed": 1,
  "not_published": [
    "One poster at a local event — not a peer-reviewed paper"
  ],
  "experience_months": 40,
  "ambiguities": [
    "GPA is contradictory: 3.2 versus 3.5; no GPA scale is stated.",
    "Graduation status and year are contradictory: the story says the candidate graduated in 2024 and is currently a final-year student graduating in 2026."
  ],
  "evidence": {
    "full_name": "# Nurzhan Abilov",
    "degree": "I graduated in 2024 with a BSc in Statistics.",
    "languages": "Languages: Kazakh, Russian, English.",
    "published_peer_reviewed": "one paper published, in a peer-reviewed proceedings, on survey weighting.",
    "experience_months": "I have been at an insurance analytics team since February 2023, which is about forty months."
  }
}
```

### Part 2 — scores and the winner

The model returned three 0–5 scores per candidate and nothing else. The
weighted total (0.5 academic + 0.3 research + 0.2 experience) and the ordering
were computed in my code.

| Candidate | academic (0–5) | research (0–5) | experience (0–5) | weighted total (code) |
|---|---|---|---|---|
| story-01 | 5 | 5 | 2 | 4.4 |
| story-02 | 3 | 3 | 5 | 3.4 |
| story-03 | 4 | 3 | 3 | 3.5 |
| story-04 | 4 | 3 | 5 | 3.9 |
| story-05 | 5 | 3 | 1 | 3.6 |
| story-06 | 2 | 3 | 5 | 2.9 |

**Winner, computed by my code:** story-01, Aziza Bekova, 4.4. Runner-up
story-04 at 3.9, a gap of 0.5.

**The model's prose answer, asked separately ("who should win?"):**

> Aziza Bekova should receive the funded scholarship.
>
> She presents the strongest overall combination of academic achievement,
> research preparation, and a credible plan for using the funded year. Her
> 3.8/4.0 GPA is excellent, and she has two completed peer-reviewed
> publications rather than counting work that is merely under review or still
> in preparation. Her proposed project — developing her retrieval research into
> a thesis — is a clear continuation of work she has already done, and she has
> discussed it with potential supervisors.
>
> Aisha Nurlankyzy is a close contender, with a slightly higher GPA, but she has
> only one published paper. Lyazzat has strong preparation but only one
> completed publication and a less directly comparable grading scale. Dias has
> the most employment experience, but his research record is thinner.
> Tamerlan's application shows promise, but two of his four listed publications
> are not yet submitted. Nurzhan's inconsistent degree and GPA information makes
> his application difficult to assess reliably.

### Part 3 — written answers

**1. Which rule did you have to add, and what broke without it?** Name the
story that forced it.

> The rubric writes the contradiction rule about a value. story-06 contradicts
> itself twice: GPA 3.2 then 3.5, and "I graduated in 2024" against "currently a
> final-year student graduating in 2026". The second is not a number, so I had
> to say in the prompt that the rule applies to every field. With that,
> `graduation_year` came back null and both contradictions were recorded. I also
> required a quote in `evidence` for every filled field.

**2. Where did the model guess, and where did your code have to decide?** One
example of each, from your run.

> The model guessed on story-03: the story gives 4.6/5.0 and refuses to convert
> it, and the model returned 3.68. The arithmetic happens to be right, but
> nothing in my pipeline checks it. My code decided the ranking — it applied the
> rubric weights and sorted. The model was told not to total anything or name a
> winner.

**3. Did your prose ranking and your computed ranking agree?** Say which one
you trust and why — and if they agreed, what you would need to see before
trusting the prose one alone.

> They agreed: both put Aziza Bekova first. I trust the computed one, because I
> can show where each number came from. The prose answer praises her "credible
> plan", which is not a rubric criterion, and weights nothing. Before trusting
> prose alone I would want it to survive repeated runs and a reshuffle of the
> six stories.

**4. The rubric has no anchor for a contradicted field.** The stories say 3.2
and then 3.5; the rubric defines a 0 and a 5 and nothing in between for this
case. Say what you did and what the rule should be.

> I set the field to null and recorded the contradiction. The scores then showed
> the real problem: the rubric says a story with no GPA scores 0 on academic,
> and the model gave story-06 a 2 and story-02 — also null — a 3. A null is read
> as "weak" rather than "absent", and differently each time. The rule should
> treat a contradicted field as unverified and flag it for a human, and it
> should be enforced in code: if `gpa_4_scale` is null, force academic to 0
> instead of hoping the model remembers the counting rule.

**5. How close were your top two candidates?** If they were within 0.05, say
what you would tell the committee and what you would change in the extraction
to make that call defensible.

> Not close: 4.4 against 3.9, and the gap comes from research, where story-01 is
> the only candidate with two published papers. If they had been within 0.05 I
> would tell the committee the scores cannot separate them. To make such a call
> defensible I would score from the extracted record rather than the story,
> derive academic and research from the counts in code, and run the scoring
> several times to show the spread.

---

## Reflection (optional, one short paragraph)

Having now written a role prompt, compressed a conversation, and ranked six
extractions — what will you do differently the next time you build something
that has to get reliable structured output out of a model?

>
