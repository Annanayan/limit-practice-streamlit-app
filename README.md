# Limit Practice — Streamlit App

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58-FF4B4B?logo=streamlit&logoColor=white)

An interactive tool for practicing limits of the form

```math
\lim_{x \to -1} \sqrt{\dfrac{x+1}{x^2 + cx + b}}
```

The app generates a random problem, checks the student's answer, and offers
escalating help (feedback → hint → full solution). After all five problems
are solved, it ends with a celebration and a recap of the technique.

- **Live app:** https://limit-practice-app-5.streamlit.app/
- **Source code:** https://github.com/Annanayan/limit-practice-streamlit-app

## Quick start

Requires Python 3.9+ and `pip`. No secrets, API keys, or environment
variables are needed.

```bash
git clone https://github.com/Annanayan/limit-practice-streamlit-app.git
cd limit-practice-streamlit-app
pip install -r requirements.txt
streamlit run app.py        # opens at http://localhost:8501
```

To verify the math module without opening the UI:

```bash
python limits.py            # runs a built-in self-test
```

### Project structure

| File               | Role                                                                    |
|--------------------|-------------------------------------------------------------------------|
| `app.py`           | Streamlit UI — layout, interaction flow, styling                        |
| `limits.py`        | Math engine — problem generation, answer checking, hints and solutions (pure Python, self-testing) |
| `requirements.txt` | Dependencies                                                            |

## How a problem is generated

The generator is derived directly from the brief's two conditions.

**1. The limit must be a genuine 0/0.**
At $x = -1$ the numerator $(x + 1)$ is 0. For the denominator to be 0 as
well, substituting $x = -1$ into $x^2 + cx + b$ gives $1 - c + b = 0$, so
$c = b + 1$.

**2. The answer must be real and tidy.**
Since $(x + 1)$ has to cancel, the denominator must factor as
$(x + 1)(x + k)$. Cancelling leaves $\frac{1}{x + k}$, which at $x = -1$
equals $\frac{1}{k - 1}$ — call it $\frac{1}{a}$. For the radicand to be
real and defined, $a$ must be a positive integer, so $k \geq 2$.

**3. One random integer fixes the whole problem.**
Expanding $(x + 1)(x + k) = x^2 + (k + 1)x + k$ and matching coefficients
gives $b = k$ and $c = k + 1$. Everything is derived from a single random
$k$, so both conditions hold by construction:

| Symbol | Formula      | Meaning                             | Values used             |
|--------|--------------|-------------------------------------|-------------------------|
| `k`    | random       | the "other root" of the denominator | 2, 5, 10, 17, 26        |
| `b`    | `k`          | constant term                       | 2, 5, 10, 17, 26        |
| `c`    | `k + 1`      | middle coefficient                  | 3, 6, 11, 18, 27        |
| `a`    | `k − 1`      | simplified denominator at x = −1    | 1, 4, 9, 16, 25         |
| answer | `1 / sqrt(a)`| the value the student must find     | 1, 1/2, 1/3, 1/4, 1/5   |

The answer $\frac{1}{\sqrt{a}}$ is rational only when $a$ is a perfect
square, so the app draws `k` from the five values where $a$ = 1, 4, 9, 16,
25 — giving exactly five clean problems per session.

## Design

### Principles

The scope is deliberately narrow — one problem type, one screen — so the
design work concentrates on information architecture, interaction flow, and
instructional quality rather than feature count:

- **Minimize extraneous cognitive load.** Everything needed for the task
  (progress, problem, answer, feedback, help) sits on a single page with no
  navigation or scrolling, keeping attention on the mathematics.
- **Restrained visual design with semantic color.** Blue for actions and
  position, green/red reserved for correct/incorrect, grey for secondary
  information. Color encodes state, not decoration.
- **The interface encodes the flow.** Elements appear in the order they are
  used, and button states leave exactly one available next action at each
  step, so the flow needs no written instructions.
- **Feedback follows learning principles.** Feedback is immediate; help is
  scaffolded, deepening only as far as the learner needs.

### Math engine (`limits.py`)

- **`k` is the single source of randomness.** Deriving `b`, `c`, and the
  answer from one number means no rejection loop and no way to generate an
  inconsistent problem.
- **Clean answers by design.** Restricting `k` to perfect-square values of
  `a` makes every answer a tidy fraction, matching the brief's `1/2` example
  and avoiding ambiguous square-root entry. The limit *skill* practiced is
  identical, so this is a UX choice, not a simplification.
- **No repeated problems.** Used `k` values are tracked and excluded, so one
  session walks through all five problems exactly once.
- **Forgiving answer checking.** Accepts a fraction (`1/10`) or a decimal
  (`0.1`) via exact `Fraction` arithmetic — no float-comparison bugs — and
  unreadable input counts as wrong rather than crashing.
- **Pure and testable.** No Streamlit dependency; `python limits.py`
  self-tests the coefficient relations and the no-repeat behaviour.

### Interface (`app.py`)

- **Screen order matches task order.** Progress → problem → answer →
  feedback → actions → help, rendered strictly top to bottom; the code is
  laid out in the same order, so the file reads like the screen.
- **A progress bar that locates you.** Five discrete segments in three
  states: solved (blue), current (light blue), not reached (grey). It fills
  left-to-right, the same direction as the "Next →" button.
- **Gated progression, but never stuck.** "Next" stays disabled until the
  problem is answered correctly, yet the full worked solution opens after
  the *first* submission, right or wrong — the one pedagogically meaningful
  barrier (an attempt is required) is kept; everything else is low-friction.
- **Feedback by outcome.** One short message per outcome — first-try
  correct, correct after a miss, and incorrect — pointing to the help below.
- **Escalating help at three depths.** The hint gives only the entry-point
  insight (0/0 means a shared factor) and stops; the solution shows all four
  steps, each with a one-clause "why"; the end-of-session recap compresses
  the method into five lines. All three tell the same causal story at
  increasing depth.
- **State details that keep the flow honest.** The answer box clears between
  problems, locks once correct, and carries input-format guidance as
  placeholder text. On the final problem, Submit/Next is replaced by a single
  "See your summary" button, signalling a terminal step.
- **A considered look.** One small commented stylesheet gives the app a
  consistent palette and typography; the completion celebration is
  hand-rolled CSS animation tuned for count, size, and timing.

### Code quality

Readable code is treated as part of the deliverable:

- Each file opens with a map of its sections, ordered by the real flow of
  the program.
- One brief annotation per section; trailing comments only on genuinely
  non-obvious lines.
- Hardcoded choices document their "why" — e.g. `CLEAN_K_VALUES` states the
  perfect-square rule and points here for the full derivation.
- Logic and presentation are fully separated, and the logic module verifies
  itself.

## How this was built

1. **Understand the problem type** — the knowledge point assessed (0/0
   indeterminate limits resolved by factoring) and the structure of this
   problem shape.
2. **Derive the constraints** — the derivation in "How a problem is
   generated" above.
3. **Build the math module** (`limits.py`) — pure, self-testing Python,
   structured as generate / check / hint / explain.
4. **Build the UI** (`app.py`) — all styling isolated in one commented
   stylesheet, layout rendered in screen order.
5. **Heuristic evaluation** in repeated passes — clear information
   architecture, uninterrupted flow, one page without scrolling, appropriate
   depth at each help layer.
6. **User testing (contextual inquiry, n = 1).** One learner was observed
   working through a full session — at this formative stage a single
   participant is enough to surface the largest interaction and
   information-architecture problems, which is what this round was for.
   Confirmed as working: feedback wording, the Submit/Next row, the recap.
   Two findings drove changes: the tester could not tell their position or
   the session length (→ the segmented progress bar), and did not discover
   the solution tab (→ tab icons and the auto-opening solution). The tester
   also suggested an AI tutor (see below).
7. **Second round of user testing (n = 1).** After the round-one changes, a
   second learner — a Master's student in Education — worked through a full
   session. The round-one changes were strongly endorsed, with the
   interaction flow read as clear and the full solution as comprehensive.
   Four suggestions drove a further pass toward a clearer, lower
   cognitive-load interaction.
8. **Iterate and deploy** — code-quality passes over both files, then
   deployment as a web app.

## Future plans

- **An AI tutor for personalized questions**, as suggested by test user —
  supplementing the current design: answer checking and the worked solution
  stay deterministic, while the tutor handles free-form questions.
- **An irrational-answer difficulty mode** (answers like 1/√5). This needs
  its own answer-entry design (e.g. radical/symbolic input rather than
  decimals only) and matching checking rules, so it is left as future design
  work rather than a hidden switch.
