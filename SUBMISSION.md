# HW2 submission

**Name:** Madiyar Tokbergen
**Student ID:** S23068824
**Group:** css4007-eng-10
**Repository:** https://github.com/AkamenYY/ai-2026-hw2

## AI tool disclosure

State which AI tools you used and for what. Expected and fine; undisclosed use
is not. If you used a model to help you draft a prompt, say which prompt.

> I used Claude for the plumbing code in all three sublabs (the API calls,
> JSON extraction, schema validation, table printing), for drafting the four
> role prompts in Sublab Easy and the extraction rules in Sublab Hard, and for
> drafting the written answers below, which I checked against my own runs and
> edited. Every number and every quoted reply in this file comes from my runs.

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
> depends on that difference. To pay for it I would drop `topic` and
> `language`.

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

**Winner, computed by my code:** story-01, Aziza Bekova, 4.4.
Runner-up story-04 at 3.9, a gap of 0.5.

**The model's prose answer, asked separately ("who should win?"):**

> Aziza Bekova should receive the funded scholarship.
>
> She presents the strongest overall combination of academic achievement,
> research preparation, and a credible plan for using the funded year. Her
> 3.8/4.0 GPA is excellent, and she has two completed peer-reviewed
> publications rather than counting work that is merely under review or still
> in preparation. Her proposed project — developing her retrieval research into
> a thesis — is a clear continuation of work she has already done, and she has
> discussed it with potential supervisors. Her eight months of data-team
> experience also provides useful practical evidence of technical maturity,
> even though it was not research employment.
>
> Aisha Nurlankyzy is a close contender, with a slightly higher GPA and
> relevant data-quality experience, but she has only one published paper and no
> submitted second paper. Lyazzat has strong preparation and substantial
> internships, but only one completed publication and a less directly
> comparable grading scale. Dias has the most employment experience, but his
> research record and academic evidence are thinner. Tamerlan's application
> shows promise, but two of his four listed publications are not yet submitted,
> and he has not completed his degree. Nurzhan's inconsistent degree and GPA
> information makes his application difficult to assess reliably.
>
> Aziza therefore offers the clearest evidence that she is already capable of
> producing research and the most convincing, well-defined plan for turning the
> scholarship into a substantial thesis.

### Part 3 — written answers

**1. Which rule did you have to add, and what broke without it?** Name the
story that forced it.

> The rubric writes the contradiction rule about a value. story-06 contradicts
> itself twice: GPA 3.2 then 3.5, and "I graduated in 2024" against "currently
> a final-year student graduating in 2026". The second is not a number, so I
> had to say in the prompt that the rule applies to every field. With that,
> `graduation_year` came back null and both contradictions were recorded. I
> also required a quote in `evidence` for every filled field.

**2. Where did the model guess, and where did your code have to decide?** One
example of each, from your run.

> The model guessed on story-03: the story gives 4.6/5.0 and refuses to convert
> it, and the model returned 3.68. The arithmetic happens to be right, but
> nothing in my pipeline checks it. My code decided the ranking — it applied
> the rubric weights and sorted. The model was told not to total anything or
> name a winner.

**3. Did your prose ranking and your computed ranking agree?** Say which one
you trust and why — and if they agreed, what you would need to see before
trusting the prose one alone.

> They agreed — both put Aziza Bekova first. I trust the computed one, because
> I can show where each number came from. The prose answer praises her
> "credible plan", which is not a rubric criterion, and weights nothing. Before
> trusting prose alone I would want it to survive repeated runs and a reshuffle
> of the six stories.

**4. The rubric has no anchor for a contradicted field.** The stories say 3.2
and then 3.5; the rubric defines a 0 and a 5 and nothing in between for this
case. Say what you did and what the rule should be.

> I set the field to null and recorded the contradiction. But the scores show
> the real problem: the rubric says a story with no GPA scores 0 on academic,
> and the model gave story-06 a 2 and story-02 — also null — a 3. A null is
> being read as "weak" rather than "absent", and differently each time. The
> rule should treat a contradicted field as unverified and flag it for a human,
> and it should be enforced in code: if `gpa_4_scale` is null, force academic
> to 0 instead of hoping the model remembers.

**5. How close were your top two candidates?** If they were within 0.05, say
what you would tell the committee and what you would change in the extraction
to make that call defensible.

> Not close: 4.4 against 3.9, a gap of 0.5, and it comes from research, where
> story-01 is the only candidate with two published papers. If they had been
> within 0.05 I would tell the committee the scores cannot separate them. To
> make such a call defensible I would score from the extracted record rather
> than the story, derive academic and research from the counts in code, and run
> the scoring several times to show the spread.

---

## Reflection (optional, one short paragraph)

Having now written a role prompt, compressed a conversation, and ranked six
extractions — what will you do differently the next time you build something
that has to get reliable structured output out of a model?

>
