"""
limits.py
---------
All the math for the limits-practice app: problem generation, answer
checking, and the hint / solution content. No Streamlit here on purpose,
so the math can be tested on its own by running `python limits.py`.

The problem
    lim (x -> -1)  sqrt( (x + 1) / (x^2 + c*x + b) )

The design in one line: every problem is built from ONE random number, k,
and everything else is derived from it, so the problem is always
self-consistent:
    a = k - 1,   b = k,   c = k + 1,   answer = 1 / sqrt(a)

The full derivation — how the brief's two conditions (a genuine 0/0, and a
tidy real answer) force exactly these relations — is worked through in
README.md, section "How a problem is generated".
"""

import random
from fractions import Fraction
from math import isqrt

# The 5 "clean" k values the app uses: a = k - 1 is a perfect square for each
# (1, 4, 9, 16, 25), so the answer 1/sqrt(a) is a tidy fraction (see README).
CLEAN_K_VALUES = [2, 5, 10, 17, 26]

# ---------------------------------------------------------------------------
# 1. Make a problem
# ---------------------------------------------------------------------------
def generate_problem(used_ks=None):
    """
    Pick a k, then derive the whole problem from it (a, b, c, and the answer).

    used_ks: k values already shown, so we prefer unseen ones.
    """
    used_ks = set(used_ks or [])
    remaining = ([k for k in CLEAN_K_VALUES if k not in used_ks]
                 or CLEAN_K_VALUES)   # reuse once all k used; only the self-test hits this
    k = random.choice(remaining)
    a, b, c = k - 1, k, k + 1

    return {
        "k": k, "a": a, "b": b, "c": c,
        "answer_exact": Fraction(1, isqrt(a)),   # a is a perfect square by construction
    }


# ---------------------------------------------------------------------------
# 2. Show the problem (LaTeX for the question)
# ---------------------------------------------------------------------------
def equation_latex(problem):
    """Build the LaTeX string for the limit the student has to evaluate."""
    b, c = problem["b"], problem["c"]
    return (r"\lim_{x \to -1} \sqrt{\dfrac{x + 1}{x^2 + "
            + f"{c}" + r"x + " + f"{b}" + r"}}")


# ---------------------------------------------------------------------------
# 3. Check the student's typed answer
# ---------------------------------------------------------------------------
def check_answer(student_text, problem):
    """
    True if the typed answer matches. Accepts a fraction (1/10) or decimal (0.1).
    """
    student_text = (student_text or "").strip()
    if not student_text:
        return False
    try:
        return Fraction(student_text) == problem["answer_exact"]    # exact match, no float bugs
    except (ValueError, ZeroDivisionError):      # unreadable input counts as wrong, not a crash
        return False


# ---------------------------------------------------------------------------
# 4. Hint (the method only — never the answer)
# ---------------------------------------------------------------------------
def build_hint(problem):
    """Return the hint as a list of steps, one string each (no answer values)."""
    return [
        "Plugging x = −1 in directly gives 0/0, which is indeterminate — so direct substitution won't work here.",
        "That 0/0 means the denominator is also zero at x = −1. Any value that makes a polynomial zero corresponds to a factor, so (x + 1) is a factor of the denominator — try factoring it out, and see what happens next.",
    ]


# ---------------------------------------------------------------------------
# 5. Full solution (LaTeX steps, with this problem's real numbers)
# ---------------------------------------------------------------------------
def build_explanation_steps(problem):
    """Return a list of {title, why, latex} steps for the full-solution tab."""
    k, a, b, c = problem["k"], problem["a"], problem["b"], problem["c"]
    final_latex = rf"\dfrac{{1}}{{{isqrt(a)}}}"   # a is a perfect square, so this is a plain fraction

    return [
        {
            "title": "Step 1 — Factor the denominator",
            "latex": rf"x^2 + {c}x + {b} = (x+1)(x+{k})",
            "why": "Direct substitution gave 0/0, so the denominator must be zero at x = −1; that means (x + 1) is one of its factors.",
        },
        {
            "title": "Step 2 — Cancel the common factor (x + 1)",
            "latex": (
                rf"\sqrt{{\dfrac{{x+1}}{{(x+1)(x+{k})}}}}"
                rf"\;=\; \sqrt{{\dfrac{{1}}{{x+{k}}}}}"
            ),
            "why": "The same (x + 1) sits on top and bottom, so it cancels — this is what removes the 0/0.",
        },
        {
            "title": "Step 3 — Substitute x = −1",
            "latex": (
                rf"\sqrt{{\dfrac{{1}}{{-1+{k}}}}}"
                rf"\;=\; \sqrt{{\dfrac{{1}}{{{a}}}}}"
            ),
            "why": "After cancelling, the denominator is no longer zero at x = −1, so substitution is now safe.",
        },
        {
            "title": "Step 4 — Simplify the square root",
            "latex": (
                rf"\sqrt{{\dfrac{{1}}{{{a}}}}}"
                rf"\;=\; \dfrac{{1}}{{\sqrt{{{a}}}}}"
                rf"\;=\; {final_latex}"
            ),
            "why": "The whole expression was under a root, so take the root of the result.",
        },
    ]


# ---------------------------------------------------------------------------
# Self-test: run `python limits.py` to check the math without the UI.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    used = []
    for _ in range(6):
        p = generate_problem(used_ks=used)
        used.append(p["k"])
        assert p["c"] == p["k"] + 1 and p["b"] == p["k"], "coefficient relation broken!"
        print("k =", p["k"], "| answer =", p["answer_exact"])
    print("All self-tests passed. Distinct k values used:", used)
