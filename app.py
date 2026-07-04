"""
app.py
------
The Streamlit screen for the limits-practice app. All the math lives in limits.py.

Run locally with:   streamlit run app.py

How the file is laid out:
    1. Setup            – imports and page config
    2. Content          – the feedback message pools
    3. Helpers          – small functions for state, feedback, and spacing
    4. Styling          – the CSS that gives the page its look
    5. Session state    – set up / read the current problem
    6. The page         – everything drawn on screen, top to bottom
"""

# ===========================================================================
# 1. Setup
# ===========================================================================
import random
import streamlit as st
from limits import (
    generate_problem, build_explanation_steps, build_hint,
    check_answer, equation_latex,
)

st.set_page_config(page_title="Limit Practice", page_icon="♾️", layout="centered")

TOTAL_PROBLEMS = 5   # one full round = the 5 clean-answer problems


# ===========================================================================
# 2. Content — feedback messages
# On submit we choose ONE pool based on the outcome, then pick a random message from it.
# ===========================================================================
FEEDBACK = {
    "firstTryCorrect": [   # right, with no wrong attempts on this problem
        "Nice — first try! 🎯 You spotted that 0/0 trap right away. Check the solution at the bottom to compare with the standard write-up.",
        "Clean work! 💪 You nailed the canceling step, which means you really get how these problems are built. Peek at the solution below to see if there's an even shorter way.",
        "You nailed it! ✨ The 0/0 didn't fool you — you went straight to canceling. Scroll to the solution at the bottom to lock it in.",
        "Solid! 🎯 This kind of problem trips most people up on the very first step, but you slid right past it. Take a quick look at the solution below to make it stick.",
        "Great instincts 👀 Spot the common factor, cancel it, plug in — not a single misstep. The solution's at the bottom; give it a read to review.",
    ],
    "recoveredCorrect": [   # right, but only after getting it wrong at least once
        "There it is! 💪 Once you found the factor you could cancel, it all clicked, right? That \"stuck → adjust → solved\" loop is real learning. Compare with the solution at the bottom.",
        "Finally got it — and you didn't give up, which matters most 🔥 The 0/0 → factor → cancel routine will feel familiar next time. The solution at the bottom helps lock in the steps.",
        "Cracked it! 👏 The tough ones teach you the most — you won't forget this one. Scroll to the solution at the bottom and walk through the full thinking once more.",
        "Nice comeback ✨ Getting it wrong and then fixing it yourself is worth more than getting it right the first time. The solution's at the bottom — use it to reinforce.",
        "Got it! 🌱 That \"find the problem → switch approach → solve it\" path you just took is exactly where real skill grows. Check the solution below for the clean write-up.",
        "Done! 🎯 Getting stuck isn't the problem — finding the canceling trick is the win. Look at the solution at the bottom to confirm your steps match.",
    ],
    "incorrect": [   # any wrong answer (one flat pool, not tied to attempt count)
        "Getting it wrong is totally normal 🙂 With these limit problems, don't rush to compute — plug in the value x is approaching and watch what the top and bottom become. That usually tells you the next move. Stuck? The solution's at the bottom.",
        "Don't lose heart 🙂 The key signal is 0/0: if both top and bottom turn into 0 after you plug in, it's not \"no answer\" — it's a hint that they share a common factor you can cancel first, then plug in. Full steps are in the solution below.",
        "Try once more 👀 When you see 0/0, don't stop — it means the top and bottom hide the same factor. Find it, cancel it, and the problem opens up. Need a nudge? Scroll to the solution at the bottom.",
        "Don't panic, you're close. The general routine here is two steps: ① factor whatever can be factored; ② cancel the common factor — the expression suddenly gets simple, then you plug in. Still stuck? The solution's at the bottom.",
        "Don't grind it out the hard way 🙂 The main line is: factor → cancel the common factor on top and bottom → plug in the value. One step at a time, don't do it all in one go. The solution at the bottom lays out every step — read it, then redo it yourself.",
        "You're working hard 👏 Just remember one thing: 0/0 is a \"cancel me\" signal, not a dead end. Try factoring, canceling, then plugging in. If you're still lost, the solution's at the bottom anytime — understand the thinking, then write it out once on your own to really own it.",
        "Stuck? That's normal — this is the trickiest step in these problems. First check whether plugging in gives you 0/0; if it does, find the common factor and cancel it. The solution at the bottom has the full walk-through to make it clearer.",
        "Direction matters 🧭 Don't let the bottom of the fraction scare you — can you split it into two things multiplied together? Once it's split, part of it often cancels with the top. Stuck? Check the solution at the bottom.",
        "Take your time 🙂 Simplify the fraction under the root first: find the common factor on top and bottom, cancel it, then plug in the value — it usually pops right out. The solution at the bottom matches each of your steps.",
    ],
}

# Short heading shown above each feedback message (the colored status word).
TITLES = {
    "firstTryCorrect":  "Correct",
    "recoveredCorrect": "Correct",
    "incorrect":        "Not quite yet",
}


# ===========================================================================
# 3. Helpers — small functions for state, feedback, and spacing
# ===========================================================================
def pick_feedback(pool):
    """Pick a random message from a pool, avoiding the one shown last from that pool."""
    options = FEEDBACK[pool]
    avoid = st.session_state.last_shown.get(pool)
    fresh = [m for m in options if m != avoid] or options
    choice = random.choice(fresh)
    st.session_state.last_shown[pool] = choice   # remember it so we don't repeat next time
    return choice

def new_problem():
    """Generate a fresh problem and reset all the per-problem state flags."""
    used = st.session_state.get("used_ks", [])
    p = generate_problem(used_ks=used)
    st.session_state.problem = p
    st.session_state.used_ks = used + [p["k"]]
    st.session_state.submitted = False
    st.session_state.was_correct = False
    st.session_state.failed_once = False   # has this problem been answered wrong yet?
    st.session_state.feedback_kind = None
    st.session_state.feedback_text = ""
    st.session_state.box_id = st.session_state.get("box_id", 0) + 1   # bump the key so the answer box clears for the next problem

def reset_session():
    """Wipe everything and start a brand-new session from question 1."""
    st.session_state.clear()

def vspace(rem):
    """Insert a fixed vertical gap (Streamlit has no built-in spacer)."""
    st.markdown(f"<div style='height:{rem}rem'></div>", unsafe_allow_html=True)


# ===========================================================================
# 4. Styling — the page's look (colors, buttons, tabs, celebration effects)
#
# Streamlit has no styling API, so we inject CSS that targets the HTML it
# renders (its own class names like .stApp, and attributes like
# kind="primary"). `!important` appears on most lines because it's the only
# way to override Streamlit's built-in styles. Palette used throughout:
# blue #0071e3 (action/brand), 
# near-black #1d1d1f (text), 
# grey #6e6e73(secondary text), 
# light grey #e5e5ea (borders / empty states).
# ===========================================================================
st.markdown("""
<style>
/* Contents of this stylesheet
   4.1  Base ................ page background + column padding
   4.2  Title ............... the h1 heading
   4.3  Primary button ...... Submit / Next / Practice again
   4.4  Text input .......... the answer box
   4.5  Help tabs ........... Hint / Full solution (st.radio styled as tabs)
   4.6  Caption ............. small grey helper text
   4.7  Card pop-in ......... finish screen: summary card entrance
   4.8  Confetti ............ finish screen: falling pieces
   4.9  Balloons ............ finish screen: rising balloons          */

/* ── 4.1 Base ────────────────────────────────────────────────────────────
   Page background + breathing room above and below the content column. */
.stApp { background-color: #f5f5f7; }
.main .block-container {
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

/* ── 4.2 Title ───────────────────────────────────────────────────────────
   Shrink Streamlit's default h1 and tighten the letter spacing. */
h1 {
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;    /* slightly tighter = large-text look */
    color: #1d1d1f !important;
}

/* ── 4.3 Primary button (Submit / Next / Practice again) ────────────────
   Every st.button(type="primary") renders as button[kind="primary"].
   Solid brand blue, rounded corners, no default shadow. */
button[kind="primary"] {
    background-color: #0071e3 !important;
    border-color:     #0071e3 !important;
    color:            #ffffff !important;
    border-radius:    8px !important;
    font-weight:      600 !important;
    font-size:        0.92rem !important;
    padding:          0.5rem 1.4rem !important;
    box-shadow:       none !important;                     /* remove Streamlit's focus glow */
    transition:       background-color 0.12s !important;   /* smooth color change on hover */
}
button[kind="primary"]:hover:not([disabled]) {
    background-color: #005ecb !important;   /* darker blue on hover (enabled only) */
    border-color:     #005ecb !important;
}
button[kind="primary"][disabled] {
    background-color: #c7c7cc !important;   /* solid grey instead of Streamlit's */
    border-color:     #c7c7cc !important;   /* faded-out disabled look, so the */
    color:            #f5f5f7 !important;   /* label stays readable */
    opacity:          1 !important;
}

/* ── 4.4 Text input (the answer box) ─────────────────────────────────────
   Rounded white box with a grey border that turns blue when focused. */
.stTextInput > div > div > input {
    border-radius: 8px !important;
    border:        1.5px solid #d2d2d7 !important;
    font-size:     1rem !important;
    padding:       0.55rem 0.85rem !important;
    background:    #ffffff !important;
    color:         #1d1d1f !important;
    transition:    border-color 0.12s, box-shadow 0.12s !important;   /* smooth focus animation */
}
.stTextInput > div > div > input:focus {
    border-color: #0071e3 !important;
    box-shadow:   0 0 0 3px #0071e32e !important;   /* soft blue halo around the box (brand blue at 18% alpha) */
    outline:      none !important;                                /* replace the browser's default outline */
}
.stTextInput > label {
    font-size:   0.875rem !important;   /* the "Your answer" label above the box */
    font-weight: 700 !important;
    color:       #3a3a3c !important;
}
.stTextInput > div > div > input:disabled {
    background: #f0f0f5 !important;   /* greyed out once the answer is correct */
    color:      #8e8e93 !important;
}

/* ── 4.5 Help tabs (Hint / Full solution) ───────────────────────────────
   Looks like a tab bar, but is actually st.radio — st.tabs can't start
   closed (its first tab always opens) or change its default selection.
   Before a submit only 💡 Hint is rendered, unselected; after the submit
   📖 Full solution joins it, pre-selected. The CSS hides the radio
   circles and restyles the options as tab labels sitting on a thin
   baseline, with the active one in blue over a blue underline. */
div[role="radiogroup"] {
    flex-direction: row !important;
    gap:            1.6rem !important;                /* space between the two labels */
    border-bottom:  1px solid #e5e5ea !important;     /* thin line the "tabs" sit on */
}
div[role="radiogroup"] label[data-baseweb="radio"] {
    margin-right:  0 !important;                      /* the gap above replaces Streamlit's own margins */
    padding:       0.5rem 0 !important;
    margin-bottom: -1px !important;                   /* underline overlaps the baseline, like a real tab */
    border-bottom: 2px solid transparent !important;  /* reserve the underline slot so labels don't jump */
    cursor:        pointer !important;
}
div[role="radiogroup"] label[data-baseweb="radio"] > div:first-of-type {
    display: none !important;                         /* hide the radio circle — label text only */
}
div[role="radiogroup"] label[data-baseweb="radio"] p {
    color:       #6e6e73 !important;                  /* inactive "tab" = grey */
    font-size:   0.92rem !important;
    font-weight: 500 !important;
}
div[role="radiogroup"] label[data-baseweb="radio"]:hover p { color: #1d1d1f !important; }
div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
    border-bottom-color: #0071e3 !important;          /* blue underline under the active "tab" */
}
div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) p { color: #0071e3 !important; }   /* active "tab" = blue text */

/* ── 4.6 Caption — small grey helper text ──────────────────────────────── */
.stCaption p {
    color:     #6e6e73 !important;
    font-size: 0.8rem !important;
}

/* ── 4.7 Finish screen: the summary card pops in ─────────────────────────
   @keyframes defines an animation timeline; .celebrate-card plays it once.
   The card starts small and low, overshoots to 101.5%, then settles —
   the overshoot is what makes it feel like a "pop" rather than a fade. */
@keyframes popIn {
    0%   { opacity: 0; transform: scale(0.9) translateY(12px); }
    60%  { opacity: 1; transform: scale(1.015) translateY(0); }
    100% { opacity: 1; transform: scale(1) translateY(0); }
}
.celebrate-card { animation: popIn 0.6s cubic-bezier(0.21, 1.02, 0.4, 1) both; }

/* ── 4.8 Finish screen: confetti falling down ────────────────────────────
   Each piece starts above the viewport (-12vh), falls past the bottom
   (105vh) while spinning two full turns. The wrapper covers the whole
   screen but lets clicks pass through (pointer-events: none) and draws
   on top of everything (z-index: 9999). */
@keyframes confettiFall {
    0%   { transform: translateY(-12vh) rotate(0deg);   opacity: 1; }
    100% { transform: translateY(105vh) rotate(720deg); opacity: 0.9; }
}
.confetti-wrap {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none; overflow: hidden; z-index: 9999;
}
.confetti-wrap i {
    position: absolute; top: -12vh; width: 3.5px; height: 6px; border-radius: 1px;   /* one tiny rectangle = one confetto */
    animation-name: confettiFall; animation-timing-function: ease-in;                /* ease-in = accelerates like gravity */
    animation-iteration-count: 1;
}

/* ── 4.9 Finish screen: a few balloons drifting up ──────────────────────
   Balloons rise from the bottom edge to above the viewport (-125vh) and
   fade. fill-mode: forwards holds the final (off-screen) state — without
   it they'd snap back and sit on the page after rising. */
@keyframes balloonRise {
    0%   { transform: translateY(0);      opacity: 0.95; }
    100% { transform: translateY(-125vh); opacity: 0; }
}
.balloon-wrap {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none; overflow: hidden; z-index: 9998;   /* just under the confetti layer */
}
.balloon-wrap b {
    position: absolute; width: 28px; height: 35px;
    border-radius: 50% 50% 50% 50% / 46% 46% 54% 54%;        /* uneven ellipse = balloon silhouette */
    box-shadow: inset -3px -4px 6px #00000024;               /* inner shadow bottom-right = 3D shading (black at 14% alpha) */
    animation-name: balloonRise; animation-timing-function: ease-in;
    animation-iteration-count: 1; animation-fill-mode: forwards;
}
.balloon-wrap b::after {
    content: ''; position: absolute; top: 100%; left: 50%;   /* the short string hanging below */
    width: 1px; height: 10px; background: #0000001f;         /* black at 12% alpha */
}
</style>
""", unsafe_allow_html=True)


# ===========================================================================
# 5. Session state — set up on first load, then read for this run
# ===========================================================================
if "problem" not in st.session_state:   # first visit only: start counters, make problem 1
    st.session_state.used_ks = []
    st.session_state.questions_completed = 0
    st.session_state.session_done = False
    st.session_state.last_shown = {}   # last message shown per pool (for no-repeat)
    new_problem()

problem   = st.session_state.problem
q_num     = len(st.session_state.used_ks)         # which question we're on (1-indexed)
completed = st.session_state.questions_completed  # how many are fully solved


# ===========================================================================
# 6. The page — rendered strictly top to bottom in screen order
#
#    Contents of this section
#    6.1  Header ........... the page title
#    6.2  Progress bar ..... 5 segments: solved / current / not yet
#    6.3  Finish screen .... celebration + recap; sits here (not last) because
#                            it ends with st.stop() — an early exit, so the
#                            problem UI below needs no session_done guards
#    6.4  Problem .......... general form, then this question's numbers
#    6.5  Answer box ....... the student's input
#    6.6  Feedback banner .. green/red verdict after a submission
#    6.7  Action buttons ... Submit / Next (or "See your summary" on the last)
#    6.8  Submit handler ... checks the answer, picks the feedback
#    6.9  Help tabs ........ Hint / Full solution
#    6.10 Next handler ..... advance, or show the finish screen
# ===========================================================================

# 6.1 Header
st.title("Limit Practice")

# 6.2 Progress bar — 5 segments, one per problem: solved / current / not yet
current_solved = st.session_state.was_correct
done_count  = (q_num - 1) + (1 if current_solved else 0)   # segments fully solved
current_idx = -1 if current_solved else q_num - 1          # the in-progress segment (none if solved)

segments = ""
for i in range(TOTAL_PROBLEMS):
    if i < done_count:
        color = "#0071e3"   # solved
    elif i == current_idx:
        color = "#79b2f2"   # current problem, still in progress
    else:
        color = "#e5e5ea"   # not reached yet
    segments += (
        f'<div style="flex:1;height:8px;border-radius:4px;background:{color};'
        f'transition:background 0.45s ease;"></div>'
    )

label = ("All 5 complete" if st.session_state.session_done
         else f"Question {q_num} of {TOTAL_PROBLEMS}")
st.markdown(
    f'<p style="font-size:0.8rem;color:#6e6e73;font-weight:500;margin:0 0 5px;">'
    f'{label}</p>'
    f'<div style="display:flex;gap:5px;margin-bottom:1.1rem;">{segments}</div>',   # 4 gaps = the breakpoints between the 5 problems
    unsafe_allow_html=True,
)

# 6.3 Finish screen — celebration + recap once all 5 are done, then stop
if st.session_state.session_done:
    # Confetti and balloons: small HTML elements with random positions,
    # colours, and timings so each one looks different.
    colors = ["#0071e3", "#34c759", "#ff9500", "#ff2d55", "#af52de", "#5ac8fa", "#ffcc00"]
    pieces = "".join(
        f'<i style="left:{random.randint(2, 98)}%;background:{random.choice(colors)};'
        f'animation-duration:{random.uniform(2.4, 4.2):.2f}s;'
        f'animation-delay:{random.uniform(0, 1.2):.2f}s;'
        f'transform:rotate({random.randint(0, 360)}deg);"></i>'
        for _ in range(40)
    )
    balloons = "".join(
        f'<b style="left:{random.randint(5, 95)}%;bottom:{random.randint(-6, 2)}vh;'
        f'background:radial-gradient(circle at 32% 28%, #ffffff99, {c} 62%);'   # white at 60% alpha for the balloon's highlight spot
        f'animation-duration:{random.uniform(3.0, 4.5):.2f}s;'
        f'animation-delay:{random.uniform(0, 0.1):.2f}s;"></b>'
        for c in (random.choice(colors) for _ in range(9))
    )
    st.markdown(f'<div class="confetti-wrap">{pieces}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="balloon-wrap">{balloons}</div>', unsafe_allow_html=True)

    # Headline card.
    st.markdown("""
    <div class="celebrate-card" style="text-align:center;padding:2.8rem 2rem 2.4rem;
                background:linear-gradient(160deg,#fbfbfd 0%,#eef1f6 100%);
                border:1px solid #e5e5ea;border-radius:20px;margin:0.5rem 0 1.6rem;">
      <div style="font-size:0.78rem;font-weight:600;letter-spacing:0.08em;
                  text-transform:uppercase;color:#0071e3;margin-bottom:0.6rem;">
          Session complete</div>
      <div style="font-size:1.6rem;font-weight:700;letter-spacing:-0.02em;
                  color:#1d1d1f;margin-bottom:0.5rem;">
          You solved all 5 limits</div>
      <p style="color:#6e6e73;font-size:0.95rem;line-height:1.6;
                max-width:380px;margin:0 auto;">
          You worked through every problem in the set. Here's a recap of the
          technique you just practised.</p>
    </div>
    """, unsafe_allow_html=True)

    # Recap of the method.
    st.markdown(
        '<p style="font-weight:600;font-size:1.05rem;color:#1d1d1f;'
        'margin:0.4rem 0 0.6rem;">The technique, in five steps</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="color:#3a3a3c;font-size:0.93rem;line-height:1.9;'
        'padding-left:0.2rem;">'
        '<strong>1.</strong>&nbsp; Substituting <em>x = −1</em> directly gives 0 / 0 — '
        'an indeterminate form, so the limit needs more work.<br>'
        '<strong>2.</strong>&nbsp; Factor the denominator. The 0/0 tells us the '
        'denominator is also zero at <em>x = −1</em>, so <em>(x + 1)</em> must be a '
        'shared factor.<br>'
        '<strong>3.</strong>&nbsp; Cancel the shared <em>(x + 1)</em> from top and bottom.<br>'
        '<strong>4.</strong>&nbsp; Substitute <em>x = −1</em> into what remains.<br>'
        '<strong>5.</strong>&nbsp; Apply the square root to reach the answer.'
        '</div>',
        unsafe_allow_html=True,
    )
    vspace(0.7)
    st.latex(
        r"\sqrt{\dfrac{x+1}{x^2+cx+b}}"
        r"\;=\;\sqrt{\dfrac{x+1}{(x+1)(x+k)}}"
        r"\;=\;\sqrt{\dfrac{1}{x+k}}"
        r"\;\xrightarrow{\;x\,\to\,-1\;}\;"
        r"\sqrt{\dfrac{1}{k-1}}"
    )

    # Start-over button.
    vspace(1.4)
    _, col_btn, _ = st.columns([1, 1, 1])
    with col_btn:
        if st.button("Practice again", type="primary", use_container_width=True):
            reset_session()
            st.rerun()
    st.stop()   # nothing below the finish screen should render


# 6.4 Problem — the general form, then this question's real numbers.
#     The intro paragraph + general formula only appear on question 1:
#     repeating them on every problem made testers stop to re-read them,
#     assuming the text had changed.
if q_num == 1:
    st.markdown(
        '<p style="color:#3a3a3c;font-size:0.93rem;margin-bottom:0.3rem;">'
        'Each question asks you to evaluate a limit that involves a square root and a '
        'rational expression. The point stays the same every time — <em>x</em> always '
        'approaches <strong>−1</strong> — while only the coefficients <strong>b</strong> '
        'and <strong>c</strong> change from one round to the next. '
        'Every problem has the same shape:</p>',
        unsafe_allow_html=True,
    )
    st.latex(r"\lim_{x \to -1} \sqrt{\dfrac{x + 1}{x^2 + c\,x + b}}")
    vspace(1.4)

st.markdown(
    '<p style="font-weight:600;font-size:1rem;color:#1d1d1f;margin-bottom:0.1rem;">'
    'Evaluate this limit:</p>',
    unsafe_allow_html=True,
)
st.latex(equation_latex(problem))

vspace(0.8)

# 6.5 Answer box
student_text = st.text_input(
    "Your answer",
    key=f"answer_box_{st.session_state.box_id}",   # key changes each problem so the field clears
    placeholder="fraction (e.g. 1/10) or decimal (e.g. 0.1)",
    disabled=st.session_state.was_correct,
)

# 6.6 Feedback banner — green if correct, red if not; same layout either way
if st.session_state.submitted and st.session_state.feedback_kind:
    kind = st.session_state.feedback_kind
    bg, bar, title_col, body_col = (
        ("#e7f7ec", "#34c759", "#1a7f37", "#1a6b30") if st.session_state.was_correct
        else ("#fff0ee", "#d93025", "#9c1b14", "#7d1a11")
    )
    st.markdown(
        f'<div style="background:{bg};border-left:4px solid {bar};border-radius:8px;'
        f'padding:0.85rem 1.1rem;margin:0.7rem 0 0.4rem;">'
        f'  <div style="font-weight:700;color:{title_col};margin-bottom:0.3rem;">{TITLES[kind]}</div>'
        f'  <div style="color:{body_col};font-size:0.93rem;line-height:1.6;">'
        f'{st.session_state.feedback_text}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# 6.7 Action buttons — Submit until correct, then Next; on the last problem
#     both are replaced by one full-width summary button
resolved = st.session_state.was_correct
is_last  = completed >= TOTAL_PROBLEMS   # final problem already solved

vspace(0.3)
if is_last:
    submit_clicked = False
    next_clicked = st.button(
        "🎉  See your summary  →", type="primary",
        use_container_width=True, key="to_summary",
    )
else:
    col_submit, col_next = st.columns(2)
    with col_submit:
        submit_clicked = st.button(
            "Submit", type="primary", use_container_width=True,
            disabled=resolved,
        )
    with col_next:
        next_clicked = st.button(
            "Next  →", type="primary", use_container_width=True,
            disabled=not resolved,
            help=None if resolved else "Answer correctly to continue",
        )

# 6.8 Submit handler — feedback text is chosen HERE (not when drawing it) so
#     it stays the same across reruns from tab clicks or hint reveals
if submit_clicked and not resolved and student_text.strip():
    st.session_state.submitted = True
    correct = check_answer(student_text, problem)
    st.session_state.was_correct = correct
    if correct:
        st.session_state.questions_completed += 1
        pool = "recoveredCorrect" if st.session_state.failed_once else "firstTryCorrect"   # praise depends on earlier misses
    else:
        st.session_state.failed_once = True
        pool = "incorrect"
    st.session_state.feedback_kind = pool
    st.session_state.feedback_text = pick_feedback(pool)
    st.rerun()

# 6.9 Help tabs — drawn with st.radio (styled as tabs in section 4.5).
#     Before a submission only 💡 Hint exists, unselected, so nothing shows
#     until the student clicks it. The first submit adds 📖 Full solution
#     next to it AND selects it, so the worked solution opens on its own.
#     The key encodes box_id + submitted: it changes exactly once per
#     problem (at the first submit), which is what lets the new default
#     take effect; afterwards the student can toggle freely.
vspace(0.9)
HINT_TAB, SOLUTION_TAB = "💡 Hint", "📖 Full solution"
if st.session_state.submitted:
    tab_options, default_idx = [HINT_TAB, SOLUTION_TAB], 1   # solution auto-opens
else:
    tab_options, default_idx = [HINT_TAB], None              # closed until clicked
help_choice = st.radio(
    "Help", tab_options,
    index=default_idx, horizontal=True, label_visibility="collapsed",
    key=f"help_tab_{st.session_state.box_id}_{int(st.session_state.submitted)}",
)

if help_choice == HINT_TAB:
    vspace(0.5)
    for i, step in enumerate(build_hint(problem), 1):
        st.write(f"**{i}.** {step}")

elif help_choice == SOLUTION_TAB:   # only exists once an answer was submitted
    vspace(0.5)
    # Each step renders as one unit — title + why + expression share a
    # dark tone and tight margins, with a single gap only between steps.
    for step in build_explanation_steps(problem):
        head = (
            '<p style="font-weight:600;font-size:1rem;color:#1d1d1f;'
            'margin:0 0 0.2rem;">' + step["title"] + '</p>'
        )
        if step.get("why"):
            head += (
                '<p style="font-weight:400;font-size:0.92rem;color:#3a3a3c;'
                'line-height:1.55;margin:0;"><span style="font-weight:600;">'
                'Why:</span> ' + step["why"] + '</p>'
            )
        st.markdown(head, unsafe_allow_html=True)
        st.latex(step["latex"])
        vspace(1.3)   # single clean gap between steps

# 6.10 Next handler — advance, or (after the last problem) show the finish
#      screen on the following click so the student can linger on the solution
if next_clicked and resolved:
    if is_last:
        st.session_state.session_done = True
    else:
        new_problem()
    st.rerun()
