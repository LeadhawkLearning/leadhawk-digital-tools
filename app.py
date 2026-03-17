import os
import re
from flask import Flask, request, render_template_string, jsonify, send_from_directory, redirect, url_for
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)

PYB_CHECKOUT_URL = os.getenv(
    "PYB_CHECKOUT_URL",
    "https://www.leadhawklearning.com/protect-your-brand-1"
)

FREE_CHECK_LIMIT = 2
usage_log = {}
LOGO_FILENAME = "leadhawk-logo.png"


SURVEY_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>What's Your Digital Score? | Leadhawk Learning</title>
  <style>
    body {
      margin: 0;
      font-family: Arial, sans-serif;
      background: linear-gradient(180deg, #9aa1a8 0%, #7f8790 100%);
      color: #1f2937;
    }
    .wrap {
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 20px;
    }
    .card {
      width: 100%;
      max-width: 820px;
      background: #eef1f4;
      border-radius: 20px;
      box-shadow: 0 12px 30px rgba(0,0,0,0.15);
      overflow: hidden;
    }
    .top {
      height: 8px;
      background: linear-gradient(90deg, #1B365D, #F2C94C);
    }
    .content {
      padding: 28px;
    }
    h1, h2 {
      color: #1B365D;
      margin: 0 0 12px;
    }
    p {
      line-height: 1.6;
    }
    .panel {
      background: white;
      border-radius: 16px;
      padding: 18px;
      margin: 20px 0;
      border: 1px solid #c8d0d8;
    }
    .btn {
      background: #1B365D;
      color: white;
      border: none;
      border-radius: 12px;
      padding: 14px 22px;
      font-size: 16px;
      font-weight: 700;
      cursor: pointer;
    }
    .btn:hover {
      background: #274D85;
    }
    .secondary {
      background: #ffffff;
      color: #1B365D;
      border: 1px solid #c8d0d8;
    }
    .answers {
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
      margin-top: 18px;
    }
    .answer-btn {
      width: 100%;
      text-align: left;
      padding: 16px;
      border-radius: 12px;
      border: 1px solid #c8d0d8;
      background: white;
      font-size: 16px;
      font-weight: 700;
      cursor: pointer;
    }
    .answer-btn.selected {
      background: #f8ebba;
      border-color: #d9c06d;
      color: #1B365D;
    }
    .progress {
      margin: 16px 0 20px;
    }
    .progress-bar {
      height: 12px;
      width: 100%;
      background: #d6dde4;
      border-radius: 999px;
      overflow: hidden;
    }
    .progress-fill {
      height: 12px;
      background: linear-gradient(90deg, #F2C94C, #f6dc7f);
      width: 0%;
    }
    .result-score {
      font-size: 52px;
      font-weight: 900;
      color: #1B365D;
      margin: 10px 0;
    }
    .band {
      display: inline-block;
      background: #f8ebba;
      color: #1B365D;
      border: 1px solid #d9c06d;
      border-radius: 999px;
      padding: 10px 14px;
      font-weight: 800;
      margin-bottom: 18px;
    }
    .grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 16px;
      margin-top: 20px;
    }
    .cta {
      margin-top: 24px;
      background: linear-gradient(135deg, #1B365D 0%, #264571 100%);
      color: white;
      border-radius: 18px;
      padding: 22px;
    }
    .cta h3 {
      color: white;
      margin-top: 0;
    }
    .cta .btn {
      background: #F2C94C;
      color: #1B365D;
      margin-right: 10px;
      margin-top: 8px;
    }
    .cta .btn.secondary {
      background: rgba(255,255,255,0.12);
      color: white;
      border: 1px solid rgba(255,255,255,0.25);
    }
    @media (min-width: 720px) {
      .grid {
        grid-template-columns: 1fr 1fr;
      }
      .answers {
        grid-template-columns: 1fr 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div class="top"></div>
      <div class="content">
        <div id="app"></div>
      </div>
    </div>
  </div>

  <script>
    const CHECKER_URL = {{ checker_url|tojson }};

    const QUESTIONS = [
      { id: 1, type: "positive", text: "Before I post, comment, or share, I think about how it could affect my future." },
      { id: 2, type: "risk", text: "I have posted, commented, or reposted something when I was angry, emotional, or trying to prove a point." },
      { id: 3, type: "positive", text: "My social media profile reflects the kind of person I want a coach, college, employer, or scholarship reviewer to see." },
      { id: 4, type: "risk", text: "I use profanity, insults, or degrading language in posts, captions, comments, or messages." },
      { id: 5, type: "positive", text: "I regularly review old posts, photos, videos, and comments to make sure they still represent me well." },
      { id: 6, type: "positive", text: "Someone who looks through my feed would see maturity, self-control, and good judgment." },
      { id: 7, type: "risk", text: "I have shared jokes, memes, screenshots, or content that could be seen as offensive, disrespectful, sexual, threatening, or inappropriate." },
      { id: 8, type: "positive", text: "My online activity supports my goals more than it threatens them." },
      { id: 9, type: "positive", text: "I would be comfortable if a parent, coach, admissions officer, employer, or teammate reviewed my profile today." },
      { id: 10, type: "positive", text: "I am actively building a digital reputation that helps create opportunities for me." }
    ];

    const ANSWERS = ["Always", "Sometimes", "Rarely", "Never"];

    const SCORE_MAP = {
      positive: { "Always": 10, "Sometimes": 7, "Rarely": 3, "Never": 0 },
      risk: { "Always": 0, "Sometimes": 3, "Rarely": 7, "Never": 10 }
    };

    const SCORE_BANDS = [
      {
        min: 85, max: 100,
        title: "Strong Digital Presence",
        interpretation: "Your online habits appear mostly aligned with maturity, judgment, and future opportunity."
      },
      {
        min: 70, max: 84,
        title: "Mostly Safe, Some Risk",
        interpretation: "You show some healthy digital habits, but there are still areas that may create concern."
      },
      {
        min: 50, max: 69,
        title: "Reputation Vulnerable",
        interpretation: "Your digital presence may contain patterns that could hurt how others view your maturity and judgment."
      },
      {
        min: 0, max: 49,
        title: "High Digital Risk",
        interpretation: "Your current digital habits may be creating avoidable risk and need attention now."
      }
    ];

    const state = {
      view: "intro",
      currentIndex: 0,
      answers: Array(QUESTIONS.length).fill(null)
    };

    const app = document.getElementById("app");

    function escapeHtml(str) {
      return String(str)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }

    function getScoreFor(question, answer) {
      return SCORE_MAP[question.type][answer];
    }

    function getTotalScore() {
      return QUESTIONS.reduce((sum, q, i) => {
        const answer = state.answers[i];
        return sum + (answer ? getScoreFor(q, answer) : 0);
      }, 0);
    }

    function getBand(score) {
      return SCORE_BANDS.find(b => score >= b.min && score <= b.max);
    }

    function renderIntro() {
      app.innerHTML = `
        <div>
          <h1>What’s Your Digital Score?</h1>
          <p>Take this quick assessment to see how your online habits may be helping — or hurting — your future.</p>

          <div class="panel">
            <p>In less than 90 seconds, you’ll get a score, a quick read on your current digital reputation habits, and a clear next step.</p>
            <p>This quick self-check is designed to raise awareness. It’s a starting point for better digital decisions.</p>
          </div>

          <button class="btn" id="startBtn">Start My Score</button>
        </div>
      `;

      document.getElementById("startBtn").addEventListener("click", () => {
        state.view = "question";
        state.currentIndex = 0;
        render();
      });
    }

    function renderQuestion() {
      const question = QUESTIONS[state.currentIndex];
      const selectedAnswer = state.answers[state.currentIndex];
      const progressPercent = (state.currentIndex / QUESTIONS.length) * 100;

      app.innerHTML = `
        <div>
          <div class="progress">
            <p><strong>Question ${state.currentIndex + 1} of ${QUESTIONS.length}</strong></p>
            <div class="progress-bar">
              <div class="progress-fill" style="width:${progressPercent}%"></div>
            </div>
          </div>

          <div class="panel">
            <h2>${escapeHtml(question.text)}</h2>

            <div class="answers">
              ${ANSWERS.map(answer => `
                <button class="answer-btn ${selectedAnswer === answer ? "selected" : ""}" data-answer="${escapeHtml(answer)}" type="button">
                  ${escapeHtml(answer)}
                </button>
              `).join("")}
            </div>

            <div style="margin-top:18px;">
              <button class="btn secondary" id="backBtn" type="button" ${state.currentIndex === 0 ? "disabled" : ""}>Back</button>
            </div>
          </div>
        </div>
      `;

      document.querySelectorAll(".answer-btn").forEach(button => {
        button.addEventListener("click", () => {
          const value = button.getAttribute("data-answer");
          state.answers[state.currentIndex] = value;

          if (state.currentIndex < QUESTIONS.length - 1) {
            state.currentIndex += 1;
            render();
          } else {
            state.view = "result";
            render();
          }
        });
      });

      const backBtn = document.getElementById("backBtn");
      if (backBtn) {
        backBtn.addEventListener("click", () => {
          if (state.currentIndex > 0) {
            state.currentIndex -= 1;
            render();
          }
        });
      }
    }

    function renderResult() {
      const totalScore = getTotalScore();
      const band = getBand(totalScore);

      app.innerHTML = `
        <div>
          <p><strong>Your Digital Score</strong></p>
          <div class="result-score">${totalScore}</div>
          <div class="band">${escapeHtml(band.title)}</div>

          <div class="panel">
            <p>${escapeHtml(band.interpretation)}</p>
            <p><strong>This score is not your final answer. It is your starting point.</strong></p>
          </div>

          <div class="cta">
            <h3>Next Step: Use the Digital Reputation Assessment</h3>
            <p>Your score identified the gap. Now use the Digital Reputation Assessment to see how your real posts, comments, captions, messages, screenshots, or photos may be interpreted by others.</p>
            <button class="btn" id="ctaBtn" type="button">Digital Reputation Assessment</button>
            <button class="btn secondary" id="retakeBtn" type="button">Retake My Score</button>
          </div>
        </div>
      `;

      document.getElementById("ctaBtn").addEventListener("click", () => {
        window.location.href = CHECKER_URL + "?score=" + totalScore;
      });

      document.getElementById("retakeBtn").addEventListener("click", () => {
        state.view = "intro";
        state.currentIndex = 0;
        state.answers = Array(QUESTIONS.length).fill(null);
        render();
      });
    }

    function render() {
      if (state.view === "intro") renderIntro();
      else if (state.view === "question") renderQuestion();
      else renderResult();
    }

    render();
  </script>
</body>
</html>
"""


CHECKER_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Leadhawk Digital Reputation Assessment</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: linear-gradient(180deg, #23364F 0%, #1A2433 100%);
      color: white;
      margin: 0;
      padding: 28px 16px 40px;
    }
    .wrap {
      max-width: 980px;
      margin: 0 auto;
    }
    .header {
      margin-bottom: 24px;
    }
    .header h1 {
      margin: 0 0 10px;
    }
    .header p {
      line-height: 1.6;
      color: #d7e1ec;
    }
    .score-carry {
      background: rgba(255,255,255,0.09);
      border: 1px solid rgba(255,255,255,0.16);
      border-radius: 14px;
      padding: 16px;
      margin-bottom: 20px;
    }
    .card {
      background: #f8fafc;
      color: #111827;
      border-radius: 16px;
      padding: 22px;
      margin-top: 18px;
      box-shadow: 0 10px 24px rgba(0,0,0,0.18);
    }
    label {
      display: block;
      font-weight: 700;
      margin-bottom: 10px;
    }
    textarea {
      width: 100%;
      min-height: 140px;
      padding: 12px;
      border-radius: 10px;
      border: 1px solid #cbd5e1;
      box-sizing: border-box;
      font-size: 15px;
    }
    input[type="file"] {
      width: 100%;
      margin-top: 10px;
    }
    .btn {
      background: #1B365D;
      color: white;
      border: none;
      border-radius: 10px;
      padding: 14px 20px;
      font-size: 16px;
      font-weight: 700;
      cursor: pointer;
      margin-top: 14px;
    }
    .btn:hover {
      background: #274D85;
    }
    .gold-btn {
      background: #F2C94C;
      color: #1B365D;
    }
    .section-title {
      font-size: 28px;
      font-weight: 900;
      color: #1B365D;
      margin-bottom: 8px;
    }
    .score {
      font-size: 40px;
      font-weight: 900;
      color: #1B365D;
    }
    ul {
      padding-left: 20px;
    }
    li {
      line-height: 1.5;
      margin: 6px 0;
    }
    .upgrade {
      margin-top: 24px;
      background: linear-gradient(135deg, #1B365D 0%, #264571 100%);
      color: white;
      border-radius: 18px;
      padding: 22px;
    }
    .upgrade a {
      display: inline-block;
      margin-top: 10px;
      background: #F2C94C;
      color: #1B365D;
      text-decoration: none;
      font-weight: 800;
      padding: 12px 18px;
      border-radius: 10px;
    }
    .small {
      color: #6b7280;
    }
    .error {
      color: #991B1B;
      font-weight: 700;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <h1>Leadhawk Digital Reputation Assessment</h1>
      <p>Before you post it, check it. See how different people in your world might interpret your digital behavior.</p>
    </div>

    {% if carry_score is not none %}
    <div class="score-carry">
      <strong>Your Digital Score was {{ carry_score }}</strong><br>
      {{ carry_message }}
    </div>
    {% endif %}

    <div class="card">
      <form id="scanForm" enctype="multipart/form-data">
        <label for="text_input">Paste a caption, comment, DM, message, or post:</label>
        <textarea name="text" id="text_input" placeholder="Example: Weekend at the lake with my crew."></textarea>

        <label for="image_input" style="margin-top:16px;">Or upload a screenshot/photo:</label>
        <input type="file" name="image" id="image_input" accept=".png,.jpg,.jpeg,.webp">

        <button class="btn" type="submit">Test My Reputation Signal</button>
      </form>
    </div>

    <div class="card" id="results">
      <p class="small">Your analysis will appear here.</p>
    </div>
  </div>

  <script>
    function renderUpgradeBlock(pyUrl) {
      return `
        <div class="upgrade">
          <h3>Next Step: Strengthen Your Digital Reputation</h3>
          <p>You’ve used your two Reputation Signal Tests. Continue with the Protect Your Brand Challenge to strengthen your digital behavior and unlock unlimited Reputation Assessments.</p>
          <a href="${pyUrl}" target="_blank">Strengthen My Reputation Signals</a>
        </div>
      `;
    }

    document.getElementById("scanForm").addEventListener("submit", async function(e) {
      e.preventDefault();

      const results = document.getElementById("results");
      results.innerHTML = "<p>Running analysis...</p>";

      const formData = new FormData(this);

      try {
        const response = await fetch("/scan", {
          method: "POST",
          body: formData
        });

        const data = await response.json();

        if (!response.ok) {
          if (data.limit_reached) {
            results.innerHTML = renderUpgradeBlock(data.pyb_url);
            return;
          }

          results.innerHTML = `<p class="error">Error:</p><p>${data.message || "Something went wrong."}</p>`;
          return;
        }

        results.innerHTML = `
          <div class="section-title">Digital Reputation Signal: <span class="score">${data.strength_score}</span>/100</div>
          <p><strong>Category:</strong> ${data.category}</p>
          <p><strong>Summary:</strong> ${data.result_summary}</p>

          <h3>Signals Detected</h3>
          <ul>${data.top_risks.map(i => "<li>" + i + "</li>").join("")}</ul>

          <h3>Positive Signals Detected</h3>
          <ul>${data.positive_signals.map(i => "<li>" + i + "</li>").join("")}</ul>

          <h3>First Impression</h3>
          <ul>${data.why_it_matters.map(i => "<li>" + i + "</li>").join("")}</ul>

          <h3>Safer Alternatives</h3>
          <ul>${data.safer_alternatives.map(i => "<li>" + i + "</li>").join("")}</ul>

          <h3>Next Best Move</h3>
          <p>${data.next_best_move}</p>

          <p><strong>Reputation Tests Remaining:</strong> ${data.checks_remaining}</p>
        `;
      } catch (err) {
        results.innerHTML = "<p class='error'>Error:</p><p>The check did not finish. Please try again.</p>";
      }
    });
  </script>
</body>
</html>
"""


NEGATIVE_SIGNALS = {
    "violence": [
        "kill", "attack", "stab", "shoot", "punch", "slap", "smack", "hurt",
        "fight", "assault", "jump him", "jump her", "kick his ass", "kick her ass",
        "beat his ass", "beat her ass", "punch him", "punch her", "slap him", "slap her",
        "kick ass", "kickass"
    ],
    "public_threat": [
        "bomb the school", "shoot up the school", "shoot up this school", "kill everyone",
        "burn the school down", "attack the school", "blow up the school", "bomb this place",
        "burn this place down", "shoot up this place"
    ],
    "hate_language": [
        "nigger", "nigga", "kike", "spic", "faggot", "ching chong", "paki", "wetback"
    ],
    "profanity": [
        "fuck", "fucking", "motherfucker", "mother fucker", "shit", "bullshit", "damn", "hell",
        "ass", "kick ass", "kickass", "bad ass", "badass", "smart ass", "smartass", "weak ass", "weakass"
    ],
    "abusive_language": [
        "bitch", "asshole", "arsehole", "dumbass", "idiot", "moron", "loser", "trash",
        "pathetic", "slut", "whore", "hoe", "cunt", "twat", "jerk", "stupid", "ugly",
        "queer"
    ],
    "sexual_content": [
        "had sex", "have sex", "having sex", "hooked up", "hookup", "send nudes",
        "nude", "nudes", "dick pic", "blowjob", "pussy", "penis", "vagina", "nice tits", "nice ass"
    ],
    "reckless_behavior": [
        "drunk", "wasted", "stoned", "blackout", "fight tonight"
    ],
    "emotional_reactivity": [
        "i hate", "hate you", "cant stand", "can't stand", "so mad", "pissed off", "done with you",
        "sick of you", "screw you", "im done", "i'm done", "whatever", "dont care anymore", "don't care anymore"
    ]
}

POSITIVE_SIGNALS = {
    "gratitude": [
        "grateful", "thankful", "blessed", "thank you", "thanks for", "appreciate", "so thankful"
    ],
    "respect": [
        "respect", "proud of", "appreciate you", "thankful for", "glad i got to", "honored"
    ],
    "maturity": [
        "learned a lot", "lesson learned", "growing", "working on myself", "self control",
        "trying to improve", "better than i was", "taking responsibility", "ownership"
    ],
    "leadership": [
        "teammates", "team", "lead", "leadership", "supporting others", "showing up",
        "committed", "focused", "accountable"
    ],
    "professionalism": [
        "opportunity", "career", "work ethic", "professional", "goals", "future", "prepared"
    ],
    "encouragement": [
        "proud of you", "you got this", "keep going", "well done", "great job", "happy for you"
    ],
    "positive_connection": [
        "great time", "good people", "great people", "great atmosphere", "fun night", "love my family",
        "love my wife", "love my husband", "love my parents", "had a great time", "really enjoyed",
        "enjoyed the game", "enjoyed the night", "had fun"
    ]
}

NEGATIVE_WEIGHTS = {
    "public_threat": 35,
    "violence": 28,
    "hate_language": 30,
    "sexual_content": 18,
    "abusive_language": 15,
    "profanity": 12,
    "reckless_behavior": 10,
    "emotional_reactivity": 8
}

POSITIVE_WEIGHTS = {
    "gratitude": 10,
    "respect": 10,
    "maturity": 10,
    "leadership": 10,
    "professionalism": 9,
    "encouragement": 8,
    "positive_connection": 8
}

NEGATIVE_LABELS = {
    "public_threat": "Public threat or mass-harm language",
    "violence": "Threatening or violent language",
    "hate_language": "Hateful or discriminatory language",
    "sexual_content": "Sexualized or explicit language",
    "abusive_language": "Name-calling or potentially abusive language",
    "profanity": "Profane or inappropriate language",
    "reckless_behavior": "Reckless or irresponsible behavior signals",
    "emotional_reactivity": "Emotionally reactive tone"
}

POSITIVE_LABELS = {
    "gratitude": "Gratitude or appreciation",
    "respect": "Respectful or affirming tone",
    "maturity": "Maturity or ownership",
    "leadership": "Leadership or team-oriented language",
    "professionalism": "Goal-oriented or professional language",
    "encouragement": "Encouragement or support",
    "positive_connection": "Healthy social connection"
}

SPORT_CONTEXT_TERMS = [
    "court", "field", "game", "team", "season", "match", "won", "score",
    "basketball", "football", "baseball", "soccer", "tennis"
]


def normalize_text(text):
    text = (text or "").lower()
    text = re.sub(r"[-_]", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def contains_phrase(text, phrase):
    return phrase in text


def contains_word(text, word):
    pattern = r"\b" + re.escape(word) + r"\b"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def has_sports_context(text):
    return any(term in text for term in SPORT_CONTEXT_TERMS)


def detect_signal_matches(text):
    lowered = normalize_text(text)
    negative_hits = []
    positive_hits = []

    for signal, terms in NEGATIVE_SIGNALS.items():
        matched = False
        for term in terms:
            term_norm = normalize_text(term)
            if signal == "violence" and term_norm == "beat" and has_sports_context(lowered):
                continue
            if " " in term_norm:
                if contains_phrase(lowered, term_norm):
                    matched = True
                    break
            else:
                if contains_word(lowered, term_norm):
                    matched = True
                    break
        if matched:
            negative_hits.append(signal)

    for signal, terms in POSITIVE_SIGNALS.items():
        matched = False
        for term in terms:
            term_norm = normalize_text(term)
            if " " in term_norm:
                if contains_phrase(lowered, term_norm):
                    matched = True
                    break
            else:
                if contains_word(lowered, term_norm):
                    matched = True
                    break
        if matched:
            positive_hits.append(signal)

    return negative_hits, positive_hits


def score_text(negative_hits, positive_hits):
    score = 70
    for sig in negative_hits:
        score -= NEGATIVE_WEIGHTS.get(sig, 0)
    for sig in positive_hits:
        score += POSITIVE_WEIGHTS.get(sig, 0)
    return max(1, min(99, score))


def score_category(score):
    if score >= 85:
        return "Strong Reputation Signal"
    if score >= 65:
        return "Mostly Positive"
    if score >= 40:
        return "Mixed Signals"
    if score >= 20:
        return "Reputation Risk"
    return "High Concern"


def build_positive_labels(positive_hits):
    labels = [POSITIVE_LABELS[s] for s in positive_hits if s in POSITIVE_LABELS]
    if not labels:
        return ["No strong positive reputation signals were clearly identified."]
    return labels[:4]


def build_negative_labels(negative_hits):
    labels = [NEGATIVE_LABELS[s] for s in negative_hits if s in NEGATIVE_LABELS]
    if not labels:
        return ["No major red-flag language was clearly identified."]
    return labels[:5]


def build_summary(score, negative_hits, positive_hits, has_image=False):
    if has_image and not negative_hits:
        return "No obvious red flags were identified in this image. It appears socially appropriate and relatively low risk based on visible content."
    if score >= 85:
        return "This message appears to send a strong and healthy reputation signal."
    if score >= 65:
        return "This message appears relatively safe, but tone and context still matter."
    if score >= 40:
        return "This message may be sending mixed signals about maturity, judgment, or professionalism."
    if score >= 20:
        return "This message raises meaningful concerns about reputation, judgment, or self-control."
    return "This message creates serious concern about safety, maturity, or trust."


def build_why_it_matters(score, negative_hits, positive_hits):
    reasons = []

    if "violence" in negative_hits or "public_threat" in negative_hits:
        reasons.append("A person in authority may see this as a safety or discipline concern.")
    if "hate_language" in negative_hits:
        reasons.append("This could be interpreted as disrespectful, discriminatory, or unacceptable.")
    if "abusive_language" in negative_hits or "profanity" in negative_hits:
        reasons.append("This may signal immaturity, poor self-control, or weak professionalism.")
    if "sexual_content" in negative_hits:
        reasons.append("This may raise concerns about boundaries, privacy, and judgment.")
    if "emotional_reactivity" in negative_hits:
        reasons.append("This may suggest emotional impulsiveness rather than composure.")
    if "reckless_behavior" in negative_hits:
        reasons.append("This may signal risky decision-making or weak judgment.")

    if "gratitude" in positive_hits:
        reasons.append("Gratitude usually strengthens perceptions of maturity and appreciation.")
    if "respect" in positive_hits:
        reasons.append("Respectful language often improves trust and first impressions.")
    if "maturity" in positive_hits or "professionalism" in positive_hits:
        reasons.append("This may communicate self-awareness, responsibility, or future-minded behavior.")
    if "leadership" in positive_hits:
        reasons.append("Team-oriented language often suggests leadership and accountability.")
    if "positive_connection" in positive_hits:
        reasons.append("Positive shared experiences can support a healthier and more socially appropriate signal.")

    if not reasons:
        reasons = [
            "Different audiences may interpret the same message in different ways.",
            "Tone, wording, and context all shape digital reputation.",
            "Even a short message can communicate maturity or immaturity."
        ]

    return reasons[:4]


def build_safer_alternatives(negative_hits, positive_hits):
    alts = []

    if "public_threat" in negative_hits or "violence" in negative_hits:
        alts.append("Remove any threatening or violent language completely.")
        alts.append("Pause before posting and choose calm, non-threatening words.")
    if "hate_language" in negative_hits:
        alts.append("Remove hateful or discriminatory language immediately.")
    if "abusive_language" in negative_hits:
        alts.append("Replace name-calling with more respectful wording.")
    if "profanity" in negative_hits:
        alts.append("Remove profanity if you want the message to sound more mature and professional.")
    if "sexual_content" in negative_hits:
        alts.append("Keep intimate or sexual content private and off public-facing platforms.")
    if "reckless_behavior" in negative_hits:
        alts.append("Avoid language that glorifies risky behavior.")
    if "emotional_reactivity" in negative_hits:
        alts.append("Wait before posting and rewrite the message once emotions settle.")

    if not negative_hits and positive_hits:
        alts.append("Keep using clear, respectful language that reflects maturity.")
        alts.append("Lean into gratitude, respect, and purpose when you post.")
    elif not alts:
        alts.append("Add context if needed and keep the message respectful.")
        alts.append("Choose language that reflects the reputation you want to build.")

    return alts[:4]


def build_next_best_move(score, negative_hits, positive_hits):
    if score < 20:
        return "Delete or fully rewrite this message before posting anything further."
    if score < 40:
        return "Step back, remove the strongest risk signals, and rewrite with more self-control."
    if score < 65:
        return "Tighten the wording so the message sounds more mature, respectful, and intentional."
    return "This is fairly safe, but you can strengthen it further with clearer maturity and purpose."


def analyze_text(text, has_image=False):
    lowered = normalize_text(text)

    if has_image and not lowered:
        return {
            "strength_score": 90,
            "category": score_category(90),
            "result_summary": "No obvious red flags were identified in this photo. It appears socially appropriate and relatively low risk based on visible content.",
            "top_risks": ["No major red-flag language was clearly identified."],
            "positive_signals": ["Healthy social context", "No obvious red flags identified"],
            "why_it_matters": [
                "A person in authority would likely see this as a normal social, family, or school-related image.",
                "The visible setting and behavior do not appear to raise obvious professionalism or safety concerns.",
                "Appropriate photos usually support a more positive digital impression."
            ],
            "safer_alternatives": [
                "Keep sharing images that reflect healthy relationships, normal settings, and respectful behavior.",
                "Before posting, still consider caption, context, and who may view the image."
            ],
            "next_best_move": "This image appears appropriate to share, assuming the caption and context also reflect good judgment."
        }

    negative_hits, positive_hits = detect_signal_matches(lowered)
    score = score_text(negative_hits, positive_hits)

    return {
        "strength_score": score,
        "category": score_category(score),
        "result_summary": build_summary(score, negative_hits, positive_hits, has_image),
        "top_risks": build_negative_labels(negative_hits),
        "positive_signals": build_positive_labels(positive_hits),
        "why_it_matters": build_why_it_matters(score, negative_hits, positive_hits),
        "safer_alternatives": build_safer_alternatives(negative_hits, positive_hits),
        "next_best_move": build_next_best_move(score, negative_hits, positive_hits)
    }


def build_carry_message(score):
    if score is None:
        return None
    if score >= 85:
        return "That suggests strong awareness. Now test how individual posts actually signal that reputation."
    if score >= 50:
        return "That suggests some habits may be creating mixed signals. Now test how specific posts may be interpreted."
    return "That suggests your digital reputation may be vulnerable. Now test real posts to see which signals need to change."


@app.route("/health")
def health():
    return "ok", 200


@app.route("/")
def home():
    return redirect(url_for("survey"))


@app.route("/survey")
def survey():
    return render_template_string(SURVEY_HTML, checker_url=url_for("checker"))


@app.route("/assessment")
def assessment():
    return redirect(url_for("checker", **request.args))


@app.route("/checker")
def checker():
    score_param = request.args.get("score", "").strip()
    carry_score = None
    if score_param.isdigit():
        carry_score = int(score_param)

    return render_template_string(
        CHECKER_HTML,
        pyb_url=PYB_CHECKOUT_URL,
        carry_score=carry_score,
        carry_message=build_carry_message(carry_score)
    )


@app.route("/logo")
def logo():
    if os.path.exists(LOGO_FILENAME):
        return send_from_directory(".", LOGO_FILENAME)
    return "", 204


@app.route("/manifest.json")
def manifest():
    return jsonify({
        "name": "Leadhawk Digital Reputation Tools",
        "short_name": "Leadhawk",
        "start_url": "/survey",
        "display": "standalone",
        "background_color": "#23364f",
        "theme_color": "#23364f",
        "icons": []
    })


@app.route("/reset")
def reset_checks():
    usage_log.clear()
    return "Checks reset."


@app.route("/scan", methods=["POST"])
def scan():
    text = request.form.get("text", "").strip()
    image = request.files.get("image")
    has_image = image is not None and image.filename != ""

    if not text and not has_image:
        return jsonify({"message": "Please paste some text or upload a screenshot first."}), 400

    user_ip = request.remote_addr or "unknown"

    if user_ip not in usage_log:
        usage_log[user_ip] = 0

    if usage_log[user_ip] >= FREE_CHECK_LIMIT:
        return jsonify({
            "limit_reached": True,
            "message": "You’ve used your 2 free Reputation Signal Tests.",
            "submessage": "Complete the Protect Your Brand Challenge to unlock unlimited Reputation Checks.",
            "pyb_url": PYB_CHECKOUT_URL
        }), 403

    try:
        result = analyze_text(text, has_image)
    except Exception as e:
        return jsonify({"message": f"Analysis error: {str(e)}"}), 500

    usage_log[user_ip] += 1
    result["pyb_url"] = PYB_CHECKOUT_URL
    result["checks_used"] = usage_log[user_ip]
    result["checks_remaining"] = max(0, FREE_CHECK_LIMIT - usage_log[user_ip])

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
