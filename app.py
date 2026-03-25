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
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');

    :root {
      --navy: #1B365D;
      --gold: #F2C94C;
      --gold-deep: #D4A72D;
      --white: #FFFFFF;
      --card: #EEF1F4;
      --panel: #FFFFFF;
      --page-top: #969CA3;
      --page-bottom: #888F97;
      --text: #1F2937;
      --muted: #5F6B7A;
      --border: #BCC6D2;
      --shadow: 0 14px 34px rgba(27, 54, 93, 0.16);
      --radius: 18px;
    }

    * { box-sizing: border-box; }

    html, body {
      margin: 0;
      padding: 0;
      font-family: 'Roboto', Arial, sans-serif;
      background: linear-gradient(180deg, var(--page-top) 0%, var(--page-bottom) 100%);
      color: var(--text);
    }

    body { min-height: 100vh; }

    .app-shell {
      width: 100%;
      min-height: 100vh;
      padding: 24px 16px 40px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .app-card {
      width: 100%;
      max-width: 860px;
      background: var(--card);
      border-radius: 24px;
      box-shadow: var(--shadow);
      overflow: hidden;
      border: 1px solid rgba(27, 54, 93, 0.16);
    }

    .top-bar {
      height: 8px;
      background: linear-gradient(90deg, var(--navy), var(--gold));
    }

    .content { padding: 28px 22px 26px; }

    .brand {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      font-size: 0.92rem;
      font-weight: 700;
      color: var(--navy);
      letter-spacing: 0.02em;
      margin-bottom: 18px;
      text-transform: uppercase;
    }

    .brand-badge {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: var(--gold);
      box-shadow: 0 0 0 4px rgba(242, 201, 76, 0.18);
    }

    h1, h2, h3 {
      margin: 0 0 12px;
      line-height: 1.15;
      color: var(--navy);
      font-family: 'Roboto', Arial, sans-serif;
    }

    h1 { font-size: clamp(2rem, 4vw, 2.8rem); font-weight: 900; }
    h2 { font-size: clamp(1.5rem, 3vw, 2.1rem); font-weight: 800; }
    h3 { font-size: 1.15rem; font-weight: 700; }

    p {
      margin: 0 0 14px;
      line-height: 1.6;
    }

    .lede {
      font-size: 1.08rem;
      color: var(--text);
      max-width: 700px;
    }

    .subtle { color: var(--muted); }

    .intro-panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px;
      margin: 20px 0 24px;
      box-shadow: 0 3px 10px rgba(27, 54, 93, 0.05);
    }

    .btn-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 16px;
    }

    button {
      appearance: none;
      border: none;
      border-radius: 14px;
      font: inherit;
      cursor: pointer;
      transition: transform 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease, border-color 0.15s ease;
      font-family: 'Roboto', Arial, sans-serif;
    }

    button:focus-visible,
    .answer-btn:focus-visible {
      outline: 3px solid rgba(242, 201, 76, 0.45);
      outline-offset: 2px;
    }

    .primary-btn {
      background: var(--navy);
      color: #FFFFFF;
      padding: 18px 28px;
      box-shadow: 0 8px 20px rgba(27, 54, 93, 0.18);
      font-size: 1.08rem;
      font-weight: 700;
      border-radius: 16px;
    }

    .primary-btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 10px 22px rgba(27, 54, 93, 0.2);
    }

    .secondary-btn {
      background: rgba(255,255,255,0.18);
      color: var(--navy);
      border: 1px solid rgba(27, 54, 93, 0.22);
      padding: 14px 20px;
      font-weight: 500;
      font-size: 1rem;
    }

    .secondary-btn:hover { background: rgba(255,255,255,0.28); }

    .progress-wrap { margin-bottom: 20px; }

    .progress-meta {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      margin-bottom: 10px;
      font-size: 0.96rem;
      color: var(--muted);
      font-weight: 700;
    }

    .progress-track {
      width: 100%;
      height: 12px;
      background: #D2D9E1;
      border-radius: 999px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, var(--gold), #F6D978);
      border-radius: 999px;
      transition: width 0.25s ease;
    }

    .question-card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px;
      box-shadow: 0 3px 10px rgba(27, 54, 93, 0.05);
    }

    .question-text {
      font-size: clamp(1.25rem, 2.7vw, 1.65rem);
      font-weight: 700;
      color: var(--navy);
      margin-bottom: 18px;
      line-height: 1.35;
    }

    .answers {
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
    }

    .answer-btn {
      width: 100%;
      text-align: left;
      padding: 16px 18px;
      background: var(--white);
      border: 1px solid var(--border);
      color: var(--text);
      border-radius: 14px;
      font-size: 1rem;
      font-weight: 700;
      box-shadow: 0 4px 10px rgba(17, 24, 39, 0.03);
      font-family: 'Roboto', Arial, sans-serif;
    }

    .answer-btn:hover {
      transform: translateY(-1px);
      border-color: rgba(27, 54, 93, 0.3);
    }

    .answer-btn.selected {
      background: rgba(242, 201, 76, 0.22);
      border-color: var(--gold-deep);
      color: var(--navy);
    }

    .question-actions {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      margin-top: 18px;
    }

    .small-note {
      font-size: 0.9rem;
      color: var(--muted);
    }

    .result-score {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      font-size: 0.98rem;
      font-weight: 700;
      color: var(--navy);
      background: rgba(27, 54, 93, 0.06);
      border: 1px solid rgba(27, 54, 93, 0.10);
      border-radius: 999px;
      padding: 8px 14px;
      margin-bottom: 14px;
    }

    .score-number {
      font-size: clamp(2.7rem, 8vw, 4.4rem);
      line-height: 1;
      font-weight: 900;
      color: var(--navy);
      margin: 8px 0 8px;
    }

    .score-bar-wrap { margin: 16px 0 20px; }

    .score-bar-track {
      width: 100%;
      height: 22px;
      border-radius: 999px;
      background: linear-gradient(90deg,#DC2626 0%,#F97316 28%,#F2C94C 58%,#22C55E 100%);
      position: relative;
      box-shadow: inset 0 0 0 1px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.04);
      overflow: visible;
    }

    .score-divider {
      position: absolute;
      top: 2px;
      bottom: 2px;
      width: 2px;
      background: rgba(255,255,255,0.5);
      border-radius: 999px;
      z-index: 1;
    }

    .score-divider.d1 { left: 25%; }
    .score-divider.d2 { left: 50%; }
    .score-divider.d3 { left: 75%; }

    .score-marker {
      position: absolute;
      top: 50%;
      transform: translate(-50%, -50%);
      min-width: 56px;
      height: 56px;
      border-radius: 999px;
      background: #FFF8DF;
      border: 3px solid #525E6F;
      color: var(--navy);
      font-weight: 900;
      font-size: 1rem;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 8px 20px rgba(27, 54, 93, 0.18), 0 0 0 3px rgba(255,255,255,0.55);
      z-index: 3;
      padding: 0 10px;
    }

    .score-bar-legend {
      margin-top: 10px;
      display: flex;
      justify-content: space-between;
      gap: 10px;
      font-size: 0.82rem;
      color: var(--muted);
      font-weight: 700;
    }

    .band-title {
      display: inline-block;
      background: #F8EBBA;
      color: var(--navy);
      font-weight: 800;
      padding: 10px 14px;
      border-radius: 999px;
      margin: 6px 0 18px;
      border: 1px solid #D9C06D;
      box-shadow: 0 3px 10px rgba(0,0,0,0.05);
    }

    .starting-point {
      margin: 4px 0 18px;
      font-weight: 700;
      color: var(--navy);
    }

    .result-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 16px;
      margin: 22px 0;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 18px;
      box-shadow: 0 3px 10px rgba(27, 54, 93, 0.05);
    }

    .panel ul {
      margin: 10px 0 0;
      padding-left: 20px;
    }

    .panel li {
      margin: 8px 0;
      line-height: 1.5;
    }

    .cta-card {
      margin-top: 22px;
      background: linear-gradient(135deg, rgba(27, 54, 93, 1) 0%, rgba(38, 69, 113, 1) 100%);
      color: var(--white);
      border-radius: 22px;
      padding: 22px;
      box-shadow: 0 16px 30px rgba(27, 54, 93, 0.22);
    }

    .cta-card h3 {
      color: var(--white);
      font-size: 1.65rem;
      margin-bottom: 12px;
      font-weight: 800;
    }

    .next-step-highlight {
      color: var(--gold);
      font-weight: 900;
    }

    .cta-tool-name {
      font-weight: 900;
      color: #FFFFFF;
    }

    .cta-card p {
      color: var(--white);
      margin-bottom: 12px;
    }

    .cta-copy {
      font-size: 1.08rem;
      line-height: 1.45;
      color: #FFFFFF;
      font-weight: 500;
    }

    .cta-highlight {
      color: #FFD86A !important;
      font-size: 1.08rem;
      line-height: 1.45;
      font-weight: 700;
      margin-top: 6px;
      margin-bottom: 0;
    }

    .cta-tool-inline {
      color: var(--gold);
      font-weight: 900;
    }

    .cta-card .primary-btn {
      background: var(--gold);
      color: var(--navy);
      box-shadow: none;
      font-weight: 700;
    }

    .cta-card .primary-btn:hover { box-shadow: none; }

    .cta-card .secondary-btn {
      background: rgba(255, 255, 255, 0.14);
      color: var(--white);
      border-color: rgba(255, 255, 255, 0.26);
      font-weight: 500;
      padding: 14px 24px;
    }

    .fade-enter { animation: fadeIn 0.24s ease; }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .footer-note {
      font-size: 0.85rem;
      color: var(--muted);
      margin-top: 18px;
    }

    @media (min-width: 700px) {
      .content { padding: 34px 34px 30px; }
      .answers { grid-template-columns: 1fr 1fr; }
      .result-grid { grid-template-columns: 1fr 1fr; }
    }

    @media (max-width: 480px) {
      .content { padding: 22px 16px 22px; }
      .question-card, .panel, .intro-panel, .cta-card { padding: 16px; }
      .primary-btn, .secondary-btn, .answer-btn { width: 100%; }
      .question-actions, .btn-row {
        flex-direction: column;
        align-items: stretch;
      }
      .score-marker {
        min-width: 48px;
        height: 48px;
        font-size: 0.95rem;
      }
      .score-bar-legend { font-size: 0.72rem; }
    }
  </style>
</head>
<body>
  <div class="app-shell">
    <main class="app-card" role="main" aria-live="polite">
      <div class="top-bar"></div>
      <div class="content">
        <div id="app"></div>
      </div>
    </main>
  </div>

  <script>
    const CTA_URL = {{ checker_url|tojson }};

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
        interpretation: "Your answers suggest that your online habits are mostly aligned with maturity, judgment, and future opportunity.",
        meaning: "A strong score doesn’t mean everything online is helping you. The strongest digital reputations are built on awareness, consistency, and regular review."
      },
      {
        min: 70, max: 84,
        title: "Mostly Safe, Some Risk",
        interpretation: "Your answers show some healthy digital habits, but there are still areas that could create concern.",
        meaning: "You may not be in major trouble — but you may be more exposed than you think."
      },
      {
        min: 50, max: 69,
        title: "Reputation Vulnerable",
        interpretation: "Your answers suggest that your digital presence may contain patterns that could hurt how others view your maturity, judgment, and readiness.",
        meaning: "This is the range where people often think they’re fine, but still have visible habits or content that create concern."
      },
      {
        min: 0, max: 49,
        title: "High Digital Risk",
        interpretation: "Your answers suggest that your current digital habits may be creating avoidable risk.",
        meaning: "This does not define you — but it does signal that your digital reputation may need attention now, not later."
      }
    ];

    const RISK_FLAGS = {
      1: "Limited pause before posting",
      2: "Posting or reacting emotionally",
      3: "Profile may not match future goals",
      4: "Language that may weaken professionalism",
      5: "Older content may be going unreviewed",
      6: "Online presence may not reflect maturity or judgment",
      7: "Shared content may be viewed as offensive or inappropriate",
      8: "Online habits may be working against long-term goals",
      9: "Public review by others may feel uncomfortable",
      10: "Digital reputation may not be built with intention"
    };

    const STRENGTH_FLAGS = {
      1: "Awareness before posting",
      3: "Profile shows some alignment with future goals",
      5: "Willingness to review and manage online presence",
      6: "Signs of maturity and self-control online",
      8: "Online activity appears connected to goals",
      9: "Comfort with outside review of profile",
      10: "Intentional effort to build a positive reputation"
    };

    const REINFORCEMENT_FLAGS = [
      "You appear to pause and think before posting",
      "Your profile seems aligned with your future goals",
      "You show signs of maturity and self-control online",
      "You appear intentional about managing your digital reputation"
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

    function getAllScores() {
      return QUESTIONS.map((question, index) => {
        const answer = state.answers[index];
        return answer ? getScoreFor(question, answer) : 0;
      });
    }

    function getTotalScore() {
      return getAllScores().reduce((sum, value) => sum + value, 0);
    }

    function getBand(score) {
      return SCORE_BANDS.find(band => score >= band.min && score <= band.max);
    }

    function getRiskAndStrengths() {
      const scores = getAllScores();

      const lowItems = QUESTIONS.map((question, index) => {
        const score = scores[index];
        return { id: question.id, score, isLow: score <= 3, label: RISK_FLAGS[question.id] };
      });

      let risks = lowItems
        .filter(item => item.isLow)
        .sort((a, b) => a.score - b.score)
        .map(item => item.label);

      if (risks.length < 2) {
        const supplemental = lowItems
          .filter(item => !risks.includes(item.label))
          .sort((a, b) => a.score - b.score)
          .map(item => item.label);

        for (const label of supplemental) {
          if (!risks.includes(label)) risks.push(label);
          if (risks.length >= 2) break;
        }
      }

      risks = risks.slice(0, 4);

      const highItems = QUESTIONS
        .filter(q => q.type === "positive")
        .map(question => {
          const score = scores[question.id - 1];
          return { id: question.id, score, isHigh: score >= 7, label: STRENGTH_FLAGS[question.id] };
        });

      let strengths = highItems
        .filter(item => item.isHigh)
        .sort((a, b) => b.score - a.score)
        .map(item => item.label);

      if (strengths.length < 2) {
        const supplemental = highItems
          .filter(item => !strengths.includes(item.label))
          .sort((a, b) => b.score - a.score)
          .map(item => item.label);

        for (const label of supplemental) {
          if (!strengths.includes(label)) strengths.push(label);
          if (strengths.length >= 2) break;
        }
      }

      strengths = strengths.slice(0, 3);

      return { risks, strengths };
    }

    function getScoreMarkerPosition(score) {
      return Math.max(3, Math.min(97, score));
    }

    function renderIntro() {
      app.innerHTML = `
        <section class="fade-enter">
          <div class="brand">
            <span class="brand-badge" aria-hidden="true"></span>
            Leadhawk Learning
          </div>
          <h1>What’s Your Digital Score?</h1>
          <p class="lede">Take this quick assessment to see how your online habits may be helping — or hurting — your future.</p>

          <div class="intro-panel">
            <p>In less than 90 sec, you’ll get a score, a quick read on your current digital reputation habits, and a clear next step.</p>
            <p class="subtle">This quick self-check is designed to raise awareness. It’s a starting point for better digital decisions.</p>
          </div>

          <div class="btn-row">
            <button class="primary-btn" id="startBtn">Start My Score</button>
          </div>
        </section>
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
      const progressPercent = ((state.currentIndex) / QUESTIONS.length) * 100;

      app.innerHTML = `
        <section class="fade-enter">
          <div class="brand">
            <span class="brand-badge" aria-hidden="true"></span>
            Leadhawk Learning
          </div>

          <div class="progress-wrap">
            <div class="progress-meta">
              <span>Question ${state.currentIndex + 1} of ${QUESTIONS.length}</span>
              <span>${Math.round(progressPercent)}% complete</span>
            </div>
            <div class="progress-track" aria-hidden="true">
              <div class="progress-fill" style="width:${progressPercent}%"></div>
            </div>
          </div>

          <div class="question-card">
            <div class="question-text">${escapeHtml(question.text)}</div>

            <div class="answers" role="group" aria-label="Answer choices">
              ${ANSWERS.map(answer => `
                <button class="answer-btn ${selectedAnswer === answer ? "selected" : ""}" data-answer="${escapeHtml(answer)}" type="button">
                  ${escapeHtml(answer)}
                </button>
              `).join("")}
            </div>

            <div class="question-actions">
              <button class="secondary-btn" id="backBtn" type="button" ${state.currentIndex === 0 ? "disabled" : ""}>Back</button>
              <div class="small-note">Choose the answer that feels most true right now.</div>
            </div>
          </div>
        </section>
      `;

      document.querySelectorAll(".answer-btn").forEach(button => {
        button.addEventListener("click", () => {
          const value = button.getAttribute("data-answer");
          state.answers[state.currentIndex] = value;
          document.querySelectorAll(".answer-btn").forEach(btn => {
            btn.classList.toggle("selected", btn.getAttribute("data-answer") === value);
          });

          window.setTimeout(() => {
            if (state.currentIndex < QUESTIONS.length - 1) {
              state.currentIndex += 1;
              render();
            } else {
              state.view = "result";
              render();
            }
          }, 180);
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
      const { risks, strengths } = getRiskAndStrengths();
      const markerPosition = getScoreMarkerPosition(totalScore);
      const isStrongScore = totalScore >= 85;

      const leftPanelTitle = isStrongScore ? "What’s working in your digital habits" : "What may be affecting your score";
      const leftPanelItems = isStrongScore ? REINFORCEMENT_FLAGS : risks;

      app.innerHTML = `
        <section class="fade-enter">
          <div class="brand">
            <span class="brand-badge" aria-hidden="true"></span>
            Leadhawk Learning
          </div>

          <div class="result-score">Your Digital Score</div>
          <div class="score-number">${totalScore}</div>

          <div class="score-bar-wrap">
            <div class="score-bar-track" aria-hidden="true">
              <span class="score-divider d1"></span>
              <span class="score-divider d2"></span>
              <span class="score-divider d3"></span>
              <div class="score-marker" style="left:${markerPosition}%;">${totalScore}</div>
            </div>
            <div class="score-bar-legend">
              <span>High Risk</span>
              <span>Vulnerable</span>
              <span>Mostly Safe</span>
              <span>Strong</span>
            </div>
          </div>

          <div class="band-title">${escapeHtml(band.title)}</div>
          <p class="starting-point">This score is not your final answer. It is your starting point.</p>

          <p class="lede">${escapeHtml(band.interpretation)}</p>

          <div class="panel" style="margin-top:18px;">
            <h3>What this means</h3>
            <p>${escapeHtml(band.meaning)}</p>
          </div>

          <div class="result-grid">
            <div class="panel">
              <h3>${escapeHtml(leftPanelTitle)}</h3>
              <ul>${leftPanelItems.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
            </div>

            <div class="panel">
              <h3>Strengths detected</h3>
              <ul>${strengths.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
            </div>
          </div>

          <div class="cta-card">
            <h3><span class="next-step-highlight">Next Step:</span> <span class="cta-tool-name">Use the Digital Reputation Assessment</span></h3>
            <p class="cta-copy">Your score identified the gap. Now use the <span class="cta-tool-inline">Digital Reputation Assessment</span> to see the signal your real posts, comments, captions, messages, screenshots, or photos may be sending.</p>
            <p class="cta-highlight">Next, click <span class="cta-tool-inline">Digital Reputation Assessment</span> to discover how your digital behavior may be interpreted by others.</p>

            <div class="btn-row">
              <button class="primary-btn" id="ctaBtn" type="button">Digital Reputation Assessment</button>
              <button class="secondary-btn" id="retakeBtn" type="button">Retake My Score</button>
            </div>
          </div>

          <p class="footer-note">This score is a quick self-assessment designed to raise awareness. It is not a full evaluation of all online activity or platform settings.</p>
        </section>
      `;

      document.getElementById("ctaBtn").addEventListener("click", () => {
        window.location.href = CTA_URL + "?score=" + totalScore;
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
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>{{ page_title }}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="Rep Check">
  <meta name="theme-color" content="#23364f">
  <link rel="apple-touch-icon" href="/logo">
  <link rel="manifest" href="/manifest.json">

  <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');

    body {
      font-family: 'Roboto', Arial, sans-serif;
      background: linear-gradient(180deg, #23364F 0%, #1A2433 100%);
      max-width: 1080px;
      margin: 0 auto;
      padding: 36px 20px 50px 20px;
      color: #E5E7EB;
    }

    .site-header { margin-bottom: 28px; }

    .header-wrap {
      display: flex;
      align-items: flex-start;
      gap: 18px;
    }

    .logo-container img {
      width: 68px;
      height: 68px;
      border-radius: 10px;
      background: white;
      padding: 4px;
      box-shadow: 0 4px 12px rgba(0,0,0,.28);
      object-fit: contain;
    }

    .title-container h1 {
      margin: 0;
      font-size: 2.15rem;
      line-height: 1.15;
      color: white;
      font-weight: 900;
    }

    .tagline {
      margin-top: 6px;
      font-size: 1rem;
      line-height: 1.4;
      color: #DBE4EF;
    }

    .highlight {
      color: #F4A100;
      font-weight: 700;
    }

    .audience-tags {
      margin-top: 12px;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .audience-tags span {
      padding: 6px 12px;
      font-size: 12px;
      border-radius: 999px;
      background: rgba(255,255,255,0.12);
      color: #D8E2EC;
      border: 1px solid rgba(255,255,255,.18);
      font-weight: 700;
    }

    .promo {
      margin-top: 26px;
      margin-bottom: 24px;
      line-height: 1.65;
    }

    .promo strong {
      color: white;
      font-size: 1.45rem;
      font-weight: 900;
      display: block;
      margin-bottom: 8px;
    }

    .promo-line-2 { margin-top: 0; }

    .pyb-link {
      color: #F4A100;
      font-weight: 700;
      text-decoration: none;
    }

    .pyb-link:hover { text-decoration: underline; }

    .promo-emphasis {
      color: #F4A100;
      font-weight: 800;
    }

    .score-carry-card {
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.14);
      border-radius: 14px;
      padding: 16px 18px;
      margin-bottom: 18px;
    }

    .score-carry-main {
      color: #F2C94C;
      font-size: 24px;
      font-weight: 900;
      margin-bottom: 4px;
    }

    .score-carry-sub {
      font-size: 15px;
      line-height: 1.5;
      color: #FFFFFF;
      font-weight: 400;
      margin: 0;
    }

    .graduate-card {
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.14);
      border-radius: 14px;
      padding: 16px 18px;
      margin-bottom: 18px;
    }

    .graduate-main {
      color: #F2C94C;
      font-size: 24px;
      font-weight: 900;
      margin-bottom: 4px;
    }

    .graduate-sub {
      font-size: 15px;
      line-height: 1.5;
      color: #FFFFFF;
      font-weight: 400;
      margin: 0;
    }

    .card {
      background: #F8FAFC;
      color: #111827;
      border-radius: 14px;
      padding: 22px;
      margin-top: 20px;
      box-shadow: 0 10px 26px rgba(0,0,0,.22);
    }

    .post-step-banner {
      display: inline-block;
      background: #D1D5DB;
      color: #1B365D;
      border: 1px solid #C4C9D1;
      border-radius: 999px;
      padding: 8px 14px;
      margin-bottom: 14px;
      font-size: 15px;
      font-weight: 700;
      letter-spacing: 0.2px;
    }

    .post-step-note {
      margin-bottom: 14px;
      font-size: 0.98rem;
      color: #374151;
      line-height: 1.5;
    }

    .check-type-title {
      font-weight: 700;
      margin-bottom: 10px;
      color: #1B365D;
    }

    .check-type-group {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 16px;
    }

    .check-type-btn {
      border: 1px solid #CBD5E1;
      background: white;
      color: #1B365D;
      border-radius: 999px;
      padding: 9px 14px;
      font-weight: 700;
      cursor: pointer;
      font-size: 14px;
    }

    .check-type-btn.active {
      background: #1B365D;
      color: white;
      border-color: #1B365D;
    }

    label {
      display: block;
      font-weight: 700;
      margin-bottom: 12px;
      color: #111827;
      font-size: 1.05rem;
    }

    .field-explainer {
      color: #374151;
      font-size: 0.98rem;
      line-height: 1.5;
      margin-bottom: 10px;
    }

    textarea {
      width: 100%;
      min-height: 140px;
      padding: 14px;
      border-radius: 8px;
      border: 1px solid #CBD5E1;
      font-size: 15px;
      resize: vertical;
      box-sizing: border-box;
      font-family: 'Roboto', Arial, sans-serif;
    }

    .upload-wrap { margin-top: 16px; }

    .upload-label {
      display: block;
      font-weight: 700;
      margin-bottom: 8px;
      color: #1B365D;
      font-size: 0.98rem;
    }

    .upload-help {
      font-size: 13px;
      color: #6B7280;
      margin-top: 6px;
    }

    .input-guidance {
      margin-top: 8px;
      margin-bottom: 0;
      color: #6B7280;
      font-size: 13px;
      line-height: 1.45;
    }

    input[type="file"] {
      display: block;
      width: 100%;
      padding: 10px;
      background: white;
      border: 1px solid #CBD5E1;
      border-radius: 10px;
      box-sizing: border-box;
      font-family: 'Roboto', Arial, sans-serif;
    }

    button.main-btn {
      background: #1B365D;
      color: white;
      border: none;
      border-radius: 8px;
      padding: 13px 20px;
      margin-top: 16px;
      font-weight: 700;
      cursor: pointer;
      font-size: 17px;
      font-family: 'Roboto', Arial, sans-serif;
    }

    button.main-btn:hover { background: #274D85; }

    button.alt-btn {
      background: #F2C94C;
      color: #1B365D;
      border: none;
      border-radius: 8px;
      padding: 12px 18px;
      margin-top: 14px;
      font-weight: 700;
      cursor: pointer;
      font-size: 18px;
      font-family: 'Roboto', Arial, sans-serif;
    }

    button.alt-btn:hover { background: #E6BC3F; }

    .behavior {
      margin-top: 10px;
      font-weight: 700;
      color: #DBEAFE;
    }

    .free-check-badge {
      display: inline-block;
      margin-bottom: 12px;
      padding: 8px 12px;
      border-radius: 999px;
      background: #F2C94C;
      color: #1B365D;
      border: 1px solid #D4A72D;
      font-weight: 700;
      font-size: 14px;
      letter-spacing: 0.2px;
    }

    .signal-title {
      font-size: 28px;
      font-weight: 900;
      margin-bottom: 6px;
      color: #1B365D;
    }

    .score-number {
      font-size: 34px;
      font-weight: 900;
      color: #1B365D;
    }

    .signal-loop {
      margin-top: 6px;
      margin-bottom: 12px;
      font-size: 0.98rem;
      color: #374151;
      font-weight: 700;
    }

    .category-line {
      margin-top: 6px;
      margin-bottom: 10px;
      font-size: 1rem;
      color: #374151;
    }

    .summary {
      font-size: 1.05rem;
      font-weight: 700;
      margin-bottom: 14px;
      color: #374151;
    }

    .disclaimer {
      font-size: 14px;
      color: #374151;
      margin-bottom: 16px;
    }

    .strength-meter-wrap {
      margin: 18px 0 10px 0;
    }

    .strength-meter {
      position: relative;
      height: 34px;
      border-radius: 999px;
      background: linear-gradient(90deg, #DC2626 0%, #F97316 33%, #EAB308 66%, #22C55E 100%);
      box-shadow: inset 0 0 0 1px rgba(0,0,0,.08);
      overflow: visible;
    }

    .score-badge {
      position: absolute;
      top: 50%;
      transform: translate(-50%, -50%);
      background: #FFFFFF;
      color: #111827;
      border: 2px solid #1B365D;
      border-radius: 999px;
      min-width: 58px;
      height: 58px;
      padding: 0 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      font-size: 22px;
      box-shadow: 0 4px 10px rgba(0,0,0,.18);
      z-index: 2;
    }

    .meter-legend {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: #4B5563;
      margin-top: 8px;
      font-weight: 700;
    }

    .typical-range {
      font-size: 13px;
      color: #4B5563;
      margin-top: 10px;
      margin-bottom: 18px;
    }

    h3 {
      color: #1B365D;
      margin-top: 18px;
      margin-bottom: 10px;
      font-weight: 700;
    }

    ul { padding-left: 20px; }
    li { line-height: 1.5; }

    .trend-wrap {
      margin-top: 18px;
      padding: 14px;
      background: #F5F8FC;
      border: 1px solid #DAE4EF;
      border-radius: 10px;
    }

    .trend-score {
      font-size: 20px;
      font-weight: 900;
      color: #1B365D;
      margin-bottom: 6px;
    }

    .trend-copy {
      color: #374151;
      line-height: 1.5;
      margin: 0;
    }

    .insight-intro {
      margin-top: 18px;
      margin-bottom: 10px;
      color: #374151;
      font-size: 14px;
      font-weight: 700;
    }

    .insight-tab-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 0;
      margin-bottom: 12px;
    }

    .insight-tab {
      background: #E9F1FB;
      color: #1B365D;
      border: 1px solid #CAD8EA;
      border-radius: 999px;
      padding: 10px 14px;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
    }

    .insight-tab.active {
      background: #1B365D;
      color: white;
      border-color: #1B365D;
    }

    .insight-content-panel {
      margin-top: 8px;
      padding: 14px;
      background: #F7FAFC;
      border: 1px solid #DAE3EE;
      border-radius: 10px;
      display: none;
    }

    .insight-content-panel.show {
      display: block;
    }

    .audience-wrap {
      margin-top: 18px;
      padding: 14px;
      background: #F4F7FB;
      border: 1px solid #D9E2EE;
      border-radius: 10px;
    }

    .audience-help {
      margin-bottom: 10px;
      color: #4B5563;
      font-size: 14px;
    }

    .audience-tabs {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }

    .audience-tab {
      background: white;
      border: 1px solid #CBD5E1;
      color: #1B365D;
      border-radius: 999px;
      padding: 8px 12px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
    }

    .audience-tab.active {
      background: #1B365D;
      color: white;
      border-color: #1B365D;
    }

    .audience-panel {
      background: white;
      border: 1px solid #DBE4EE;
      border-radius: 10px;
      padding: 12px 14px;
      color: #1F2937;
      line-height: 1.6;
      min-height: 88px;
    }

    .audience-panel .lead {
      font-weight: 800;
    }

    .audience-panel .interpretation {
      font-style: italic;
    }

    .share-box {
      margin-top: 18px;
      padding: 12px;
      background: #EEF2FF;
      border-radius: 8px;
      font-size: 14px;
      line-height: 1.45;
    }

    .checks-remaining-box {
      margin-top: 18px;
      display: inline-block;
      background: #F2C94C;
      color: #1B365D;
      padding: 9px 14px;
      border-radius: 8px;
      font-size: 18px;
      font-weight: 700;
      box-shadow: 0 3px 10px rgba(0,0,0,.10);
      border: 1px solid #D4A72D;
    }

    .checks-wrap { margin-top: 16px; }

    .improve-note {
      margin-top: 12px;
      padding: 10px 12px;
      background: #EEF6FF;
      border-left: 4px solid #1B365D;
      border-radius: 6px;
      color: #1F2937;
      font-size: 14px;
    }

    .next-step-card {
      margin-top: 22px;
      background: linear-gradient(135deg, rgba(27,54,93,1) 0%, rgba(38,69,113,1) 100%);
      color: #FFFFFF;
      border-radius: 22px;
      padding: 22px;
      box-shadow: 0 16px 30px rgba(27, 54, 93, 0.22);
      text-align: left;
    }

    .next-step-card h3 {
      color: #FFFFFF;
      font-size: 1.65rem;
      margin-bottom: 12px;
      font-weight: 800;
    }

    .next-step-highlight {
      color: #F2C94C;
      font-weight: 900;
    }

    .next-step-title {
      color: #FFFFFF;
      font-weight: 900;
    }

    .next-step-copy {
      font-size: 1.08rem;
      line-height: 1.45;
      color: #FFFFFF;
      font-weight: 500;
      margin-bottom: 10px;
    }

    .next-step-statement {
      color: #FFFFFF;
      font-size: 1rem;
      line-height: 1.45;
      font-weight: 500;
      margin-bottom: 14px;
    }

    .next-step-inline {
      color: #F2C94C;
      font-weight: 900;
    }

    .next-step-actionline {
      color: #FFD86A;
      font-size: 1rem;
      line-height: 1.45;
      font-weight: 700;
      margin-bottom: 18px;
    }

    .cta {
      display: inline-block;
      background: #F2C94C;
      color: #1B365D;
      padding: 14px 22px;
      border-radius: 10px;
      font-size: 20px;
      font-weight: 800;
      text-decoration: none;
      margin-top: 0;
      box-shadow: 0 6px 14px rgba(0,0,0,.14);
    }

    .cta:hover { background: #E6BC3F; }

    .error {
      color: #991B1B;
      font-weight: 700;
    }

    .small {
      color: #6B7280;
      font-size: 14px;
    }

    .footer {
      margin-top: 26px;
      font-size: 13px;
      text-align: center;
      color: #CBD5E1;
    }

    @media (max-width: 768px) {
      body { padding: 24px 14px 40px 14px; }
      .header-wrap {
        flex-direction: column;
        align-items: center;
        text-align: center;
        gap: 14px;
      }
      .logo-container img {
        width: 78px;
        height: 78px;
      }
      .title-container h1 { font-size: 2rem; }
      .tagline {
        max-width: 330px;
        margin-left: auto;
        margin-right: auto;
      }
      .audience-tags { justify-content: center; }
      .promo strong { font-size: 1.3rem; }
      .card { padding: 18px; }
      .free-check-badge { font-size: 13px; }
      .checks-remaining-box { font-size: 16px; }
      .cta { font-size: 18px; }
      .score-carry-main, .graduate-main { font-size: 21px; }
      .next-step-card h3 { font-size: 1.45rem; }
    }
  </style>
</head>
<body>

  <div class="site-header">
    <div class="header-wrap">
      <div class="logo-container">
        <img src="{{ logo_url }}" alt="Leadhawk Logo">
      </div>

      <div class="title-container">
        <h1>{{ header_title }}</h1>

        <p class="tagline">
          {% if graduate %}
            <span class="highlight">Graduate Access activated.</span><br>
            Use this tool anytime to test how your digital behavior may be interpreted before you post.
          {% else %}
            <span class="highlight">Before you post it, check it.</span><br>
            See how different people in your world might interpret your digital behavior.
          {% endif %}
        </p>

        <div class="audience-tags">
          <span>Parents</span>
          <span>Teachers</span>
          <span>Professors</span>
          <span>Coaches</span>
          <span>Admissions</span>
          <span>Recruiters</span>
          <span>Employers</span>
        </div>
      </div>
    </div>

    <div class="promo">
      <strong>Test Your Digital Reputation</strong>
      <div class="promo-line-2">
        {% if graduate %}
          You completed Protect Your Brand. You now have continuing access to test posts, captions, messages, comments, or images before you share them.
        {% else %}
          Run two reputation tests to see how your posts, captions, messages, comments, or images may be interpreted — then unlock
          <span class="promo-emphasis">Graduate Access</span> by completing the
          <a class="pyb-link" href="{{ pyb_url }}" target="_blank">Protect Your Brand Challenge</a>.
        {% endif %}
      </div>
    </div>
  </div>

  {% if carry_score is not none and not graduate %}
  <div class="score-carry-card">
    <div class="score-carry-main">Your Digital Score was {{ carry_score }}</div>
    <p class="score-carry-sub">{{ carry_message }}</p>
  </div>
  {% endif %}

  {% if graduate %}
  <div class="graduate-card">
    <div class="graduate-main">Graduate Access: Digital Reputation Assessment</div>
    <p class="graduate-sub">This tool is now part of your decision-making process. Use it anytime before you post.</p>
  </div>
  {% endif %}

  <div class="card">
    <div class="post-step-banner" id="postStepBanner">Post 1 of 2</div>
    <div class="post-step-note" id="postStepNote">Start by entering your first post, comment, caption, message, screenshot, or photo below.</div>

    <form id="scanForm" enctype="multipart/form-data">
      <div class="check-type-title">What would you like to check?</div>
      <div class="check-type-group">
        <button type="button" class="check-type-btn active" data-type="Caption">Caption</button>
        <button type="button" class="check-type-btn" data-type="Comment">Comment</button>
        <button type="button" class="check-type-btn" data-type="DM">DM</button>
        <button type="button" class="check-type-btn" data-type="Post">Post</button>
      </div>

      <input type="hidden" name="check_type" id="check_type" value="Caption">

      <label for="text_input">Paste a recent or past caption, comment, DM, message, or post to see how it may impact your reputation:</label>
      <div class="field-explainer">You can test something recent, something older, or even draft wording before you post.</div>
      <textarea name="text" id="text_input" placeholder="Example: Weekend at the lake with my crew."></textarea>

      <div class="upload-wrap">
        <div class="upload-label">Or upload a screenshot/photo:</div>
        <input type="file" name="image" id="image_input" accept=".png,.jpg,.jpeg,.webp">
        <div class="upload-help">Useful for screenshots of comments, DMs, posts, or conversations.</div>
        <div class="input-guidance">Use either pasted text or an image. If the screenshot contains written text, paste the visible words for the most accurate review.</div>
      </div>

      <button class="main-btn" type="submit" id="analyzeBtn">Test My Reputation Signal</button>
    </form>
  </div>

  <div class="behavior">
    Think before you post. Every message sends a signal about judgment, maturity, and respect.
  </div>

  <div class="card" id="results">
    <p class="small">Your analysis will appear here.</p>
  </div>

  <div class="footer">
    Educational guidance only. This tool helps users think more carefully about how digital behavior may be interpreted.
  </div>

  <script>
    const IS_GRADUATE = {{ graduate|tojson }};
    const PYB_URL = {{ pyb_url|tojson }};

    const placeholders = {
      "Caption": "Example: Weekend at the lake with my crew.",
      "Comment": "Example: You look awesome in this pic!",
      "DM": "Example: Stop texting me, you're being annoying.",
      "Post": "Example: Can't believe how wild last night was lol"
    };

    let currentCheckNumber = 1;
    let firstResultData = null;
    let secondResultData = null;

    function updatePostStepUI() {
      const banner = document.getElementById("postStepBanner");
      const note = document.getElementById("postStepNote");
      const results = document.getElementById("results");

      if (currentCheckNumber <= 1) {
        banner.textContent = "Post 1 of 2";
        note.textContent = "Start by entering your first post, comment, caption, message, screenshot, or photo below.";
      } else {
        banner.textContent = "Post 2 of 2";
        note.textContent = "Now enter a second post so you can compare how the signal changes.";
        results.innerHTML = "<p class='small'>Enter your second post to compare how the signal changes.</p>";
      }
    }

    function clearForNextPost() {
      document.getElementById("text_input").value = "";
      document.getElementById("image_input").value = "";
      document.getElementById("text_input").placeholder = placeholders[document.getElementById("check_type").value] || placeholders["Post"];
      currentCheckNumber = 2;
      updatePostStepUI();
      document.getElementById("text_input").focus();
      window.scrollTo({ top: 0, behavior: "smooth" });
    }

    document.querySelectorAll(".check-type-btn").forEach(btn => {
      btn.addEventListener("click", function() {
        document.querySelectorAll(".check-type-btn").forEach(b => b.classList.remove("active"));
        this.classList.add("active");
        document.getElementById("check_type").value = this.dataset.type;
        document.getElementById("text_input").placeholder = placeholders[this.dataset.type] || placeholders["Post"];
      });
    });

    document.getElementById("image_input").addEventListener("change", function() {
      if (this.files && this.files.length > 0) {
        document.getElementById("text_input").value = "";
      }
    });

    document.getElementById("text_input").addEventListener("input", function() {
      if (this.value.trim().length > 0) {
        const imageInput = document.getElementById("image_input");
        if (imageInput.value) {
          imageInput.value = "";
        }
      }
    });

    function clamp(n, min, max) {
      return Math.max(min, Math.min(max, n));
    }

    function getCheckBadge(checksUsed) {
      if (IS_GRADUATE) {
        if (checksUsed === 1) return '<div class="free-check-badge">Graduate Check 1</div>';
        if (checksUsed === 2) return '<div class="free-check-badge">Graduate Check 2</div>';
        return '<div class="free-check-badge">Graduate Access</div>';
      }
      if (checksUsed === 1) return '<div class="free-check-badge">1st Reputation Signal Test</div>';
      if (checksUsed === 2) return '<div class="free-check-badge">2nd and Final Reputation Signal Test</div>';
      return '';
    }

    function renderUpgradeBlock(pyUrl) {
      return `
        <div class="next-step-card">
          <h3><span class="next-step-highlight">Next Step:</span> <span class="next-step-title">Strengthen Your Digital Reputation</span></h3>
          <p class="next-step-copy">
            You’ve used your two Reputation Signal Tests. Continue with the
            <span class="next-step-inline">Protect Your Brand Challenge</span>
            to strengthen your digital behavior and unlock Graduate Access.
          </p>
          <p class="next-step-statement">
            Your score identified the gap. Your signal tests exposed how your words may be interpreted.
          </p>
          <p class="next-step-actionline">Click below to continue with the Protect Your Brand Challenge.</p>
          <a class="cta" href="${pyUrl}" target="_blank">Strengthen My Reputation Signals</a>
        </div>
      `;
    }

    function audienceTabsHtml(interpretations) {
      return `
        <div class="audience-wrap">
          <h3>How different audiences may evaluate this message</h3>
          <div class="audience-help">Click each audience to see how they might evaluate this message.</div>
          <div class="audience-tabs">
            <button type="button" class="audience-tab active" data-audience="parents">Parents</button>
            <button type="button" class="audience-tab" data-audience="coaches">Coaches</button>
            <button type="button" class="audience-tab" data-audience="admissions">Admissions</button>
            <button type="button" class="audience-tab" data-audience="employers">Employers</button>
          </div>
          <div class="audience-panel" id="audiencePanel"></div>
        </div>
      `;
    }

    function formatAudienceInterpretation(text) {
      const parts = text.split("::");
      if (parts.length === 2) {
        return `<span class="lead">${parts[0]}:</span> <span class="interpretation">${parts[1].trim()}</span>`;
      }
      return text;
    }

    function activateAudienceTab(audienceKey, interpretations) {
      document.querySelectorAll(".audience-tab").forEach(tab => {
        tab.classList.toggle("active", tab.dataset.audience === audienceKey);
      });
      const panel = document.getElementById("audiencePanel");
      if (panel) {
        panel.innerHTML = formatAudienceInterpretation(interpretations[audienceKey] || "");
      }
    }

    function buildTrendBlock(firstScore, secondScore) {
      const delta = secondScore - firstScore;
      let trendLabel = "No Change";
      let trendCopy = "Your second post sent about the same reputation signal as your first post. Small wording choices still matter.";

      if (delta > 0) {
        trendLabel = `↑ Stronger Signal (+${delta})`;
        trendCopy = "Your second post created a stronger reputation signal than your first one. That shows how quickly better language choices can improve digital perception.";
      } else if (delta < 0) {
        trendLabel = `↓ Weaker Signal (${delta})`;
        trendCopy = "Your second post created a weaker reputation signal than your first one. This shows how tone or wording can quickly shift how others may interpret your message.";
      }

      return `
        <div class="trend-wrap">
          <h3>Signal Trend</h3>
          <div class="trend-score">Post 1: ${firstScore} | Post 2: ${secondScore} | ${trendLabel}</div>
          <p class="trend-copy">${trendCopy}</p>
        </div>
      `;
    }

    function combinedSignalsHtml(firstData, secondData) {
      const allNeg = [...(firstData.top_risks || []), ...(secondData.top_risks || [])]
        .filter(x => x && !x.startsWith("No major") && !x.startsWith("No red"))
        .filter((v, i, a) => a.indexOf(v) === i)
        .slice(0, 5);

      const allPos = [...(firstData.positive_signals || []), ...(secondData.positive_signals || [])]
        .filter(x => x && !x.startsWith("No strong"))
        .filter((v, i, a) => a.indexOf(v) === i)
        .slice(0, 5);

      const negList = allNeg.length
        ? allNeg.map(i => `<li>${i}</li>`).join("")
        : "<li>No major repeat red-flag signals were clearly detected across both posts.</li>";

      const posList = allPos.length
        ? allPos.map(i => `<li>${i}</li>`).join("")
        : "<li>No strong positive pattern was clearly established across both posts.</li>";

      let overview = "Across both posts, your language pattern suggests there are signals worth paying attention to. The goal is to reduce risky wording while strengthening respect, maturity, and clarity.";

      if (allNeg.length === 0 && allPos.length > 0) {
        overview = "Across both posts, your language suggests a healthier signal pattern. Keep building consistency in respect, appreciation, and intentional communication.";
      } else if (allNeg.length > 0 && allPos.length > 0) {
        overview = "Across both posts, you show both strengths and mixed signals. Reducing risky wording while increasing maturity and purpose would strengthen your digital reputation.";
      }

      return `
        <div>
          <h3>Combined Signals Across Both Posts</h3>
          <p>${overview}</p>
          <h3>Repeated or Shared Risk Signals</h3>
          <ul>${negList}</ul>
          <h3>Positive Signals Across Both Posts</h3>
          <ul>${posList}</ul>
        </div>
      `;
    }

    function strongBehaviorGuideHtml() {
      return `
        <div>
          <h3>What Strong Digital Behavior Looks Like</h3>
          <ul>
            <li>Pauses before posting when emotional.</li>
            <li>Uses language that sounds respectful, not reactive.</li>
            <li>Shows maturity, gratitude, or responsibility in wording.</li>
            <li>Connects online behavior to goals, leadership, or future opportunities.</li>
            <li>Reviews posts and profile content regularly.</li>
            <li>Chooses messages that strengthen trust with parents, coaches, schools, and employers.</li>
          </ul>
          <p>A high digital reputation score is usually built through self-control, respect, awareness, and consistency over time.</p>
        </div>
      `;
    }

    function buildInsightSection(firstData, secondData) {
      return `
        <div class="insight-intro">Choose one section to explore deeper insight:</div>
        <div class="insight-tab-row">
          <button type="button" class="insight-tab" id="combinedSignalsTab">View My Combined Signals</button>
          <button type="button" class="insight-tab" id="strongBehaviorTab">Signals of a Strong Digital Reputation</button>
        </div>

        <div class="insight-content-panel" id="combinedSignalsPanel">
          ${combinedSignalsHtml(firstData, secondData)}
        </div>

        <div class="insight-content-panel" id="strongBehaviorPanel">
          ${strongBehaviorGuideHtml()}
        </div>
      `;
    }

    function setupInsightTabs() {
      const combinedTab = document.getElementById("combinedSignalsTab");
      const strongTab = document.getElementById("strongBehaviorTab");
      const combinedPanel = document.getElementById("combinedSignalsPanel");
      const strongPanel = document.getElementById("strongBehaviorPanel");

      if (!combinedTab || !strongTab || !combinedPanel || !strongPanel) return;

      combinedTab.addEventListener("click", () => {
        combinedTab.classList.add("active");
        strongTab.classList.remove("active");
        combinedPanel.classList.add("show");
        strongPanel.classList.remove("show");
      });

      strongTab.addEventListener("click", () => {
        strongTab.classList.add("active");
        combinedTab.classList.remove("active");
        strongPanel.classList.add("show");
        combinedPanel.classList.remove("show");
      });
    }

    document.getElementById("scanForm").addEventListener("submit", async function(e) {
      e.preventDefault();

      const results = document.getElementById("results");
      results.innerHTML = "<p>Running analysis...</p>";

      const formData = new FormData(this);

      try {
        const response = await fetch(window.location.pathname === "/checker-unlimited" ? "/scan-unlimited" : "/scan", {
          method: "POST",
          body: formData
        });

        const data = await response.json();

        if (!response.ok) {
          if (data.limit_reached && !IS_GRADUATE) {
            results.innerHTML = renderUpgradeBlock(data.pyb_url);
            return;
          }

          results.innerHTML = `<p class="error">Error:</p><p>${data.message || "Something went wrong."}</p>`;
          return;
        }

        if (currentCheckNumber === 1) firstResultData = data;
        else secondResultData = data;

        const scorePosition = clamp(data.strength_score, 3, 97);
        const improveNote = data.improve_note
          ? `<div class="improve-note"><strong>What could make this even stronger?</strong><br>${data.improve_note}</div>`
          : "";

        const remainingHtml = (!IS_GRADUATE && data.checks_remaining > 0)
          ? `<div class="checks-wrap"><div class="checks-remaining-box">Reputation Tests Remaining: ${data.checks_remaining}</div></div>`
          : "";

        const nextPostButton = (currentCheckNumber === 1)
          ? `<button class="alt-btn" id="checkAnotherBtn" type="button">Check Post 2</button>`
          : "";

        const signalLoopText = (currentCheckNumber === 1)
          ? `<div class="signal-loop">Test another post to see how the signal changes.</div>`
          : "";

        const audienceHtml = audienceTabsHtml(data.audience_interpretations || {});

        let trendHtml = "";
        let insightSectionHtml = "";
        let upgradeHtml = "";

        if (currentCheckNumber === 2 && firstResultData && secondResultData) {
          trendHtml = buildTrendBlock(firstResultData.strength_score, secondResultData.strength_score);
          insightSectionHtml = buildInsightSection(firstResultData, secondResultData);

          if (!IS_GRADUATE && data.checks_remaining === 0) {
            upgradeHtml = renderUpgradeBlock(data.pyb_url);
          }
        }

        const badgeHtml = getCheckBadge(data.checks_used || 1);

        results.innerHTML = `
          ${badgeHtml}

          <div class="signal-title">Digital Reputation Signal: <span class="score-number">${data.strength_score}</span>/100</div>
          ${signalLoopText}
          <div class="category-line"><strong>Category:</strong> ${data.category}</div>
          <div class="summary">${data.result_summary}</div>

          <div class="disclaimer">
            This result reflects how your message may be interpreted, not necessarily what you intended.
          </div>

          <div class="strength-meter-wrap">
            <div class="strength-meter">
              <div class="score-badge" style="left:${scorePosition}%;">${data.strength_score}</div>
            </div>
            <div class="meter-legend">
              <span>Needs Attention</span>
              <span>Mixed Signal</span>
              <span>Strong Signal</span>
            </div>
          </div>

          <div class="typical-range">
            Most people who test this tool score between <strong>40–68</strong> depending on tone, language, and context.
          </div>

          ${trendHtml}
          ${improveNote}

          <h3>Signals Detected</h3>
          <ul>${data.top_risks.map(i => "<li>" + i + "</li>").join("")}</ul>

          <h3>Positive Signals Detected</h3>
          <ul>${data.positive_signals.map(i => "<li>" + i + "</li>").join("")}</ul>

          <h3>First Impression</h3>
          <p>A person in authority reviewing this content might think:</p>
          <ul>${data.why_it_matters.map(i => "<li>" + i + "</li>").join("")}</ul>

          <h3>Safer Alternatives</h3>
          <ul>${data.safer_alternatives.map(i => "<li>" + i + "</li>").join("")}</ul>

          <h3>Next Best Move</h3>
          <p>${data.next_best_move}</p>

          ${audienceHtml}
          ${insightSectionHtml}

          <h3>Reflection Question</h3>
          <p><strong>If a person in authority saw this message today, would it strengthen or weaken the reputation you want to build?</strong></p>

          ${nextPostButton}

          <div class="share-box">
            <strong>Challenge a Friend</strong><br><br>
            "I just ran my post through the Leadhawk Digital Reputation Assessment.<br>
            Strength Score: ${data.strength_score}/100.<br>
            Before you post it, check it.<br>
            Try it: ${location.href}"
          </div>

          ${remainingHtml}
          ${upgradeHtml}
        `;

        const nextBtn = document.getElementById("checkAnotherBtn");
        if (nextBtn) nextBtn.addEventListener("click", clearForNextPost);

        document.querySelectorAll(".audience-tab").forEach(tab => {
          tab.addEventListener("click", () => {
            activateAudienceTab(tab.dataset.audience, data.audience_interpretations || {});
          });
        });

        activateAudienceTab("parents", data.audience_interpretations || {});
        setupInsightTabs();
      } catch (err) {
        results.innerHTML = "<p class='error'>Error:</p><p>The check did not finish. Please try again.</p>";
      }
    });

    updatePostStepUI();
  </script>
</body>
</html>
"""

NEGATIVE_SIGNAL_PATTERNS = {
    "public_threat": [
        r"\bbomb the school\b", r"\bshoot up the school\b", r"\bshoot up this school\b",
        r"\bkill everyone\b", r"\bburn the school down\b", r"\battack the school\b",
        r"\bblow up the school\b", r"\bbomb this place\b", r"\bburn this place down\b",
        r"\bshoot up this place\b"
    ],
    "violence": [
        r"\bkill\b", r"\battack\b", r"\bstab\b", r"\bshoot\b", r"\bpunch\b", r"\bslap\b",
        r"\bsmack\b", r"\bhurt\b", r"\bfight\b", r"\bassault\b",
        r"\bjump him\b", r"\bjump her\b", r"\bkick his ass\b", r"\bkick her ass\b",
        r"\bbeat his ass\b", r"\bbeat her ass\b", r"\bpunch him\b", r"\bpunch her\b",
        r"\bslap him\b", r"\bslap her\b"
    ],
    "hate_language": [
        r"\bnigger\b", r"\bnigga\b", r"\bkike\b", r"\bspic\b", r"\bfaggot\b",
        r"\bching chong\b", r"\bpaki\b", r"\bwetback\b"
    ],
    "sexual_content": [
        r"\bhad sex\b", r"\bhave sex\b", r"\bhaving sex\b", r"\bsex with\b",
        r"\bhooked up\b", r"\bhookup\b", r"\bsend nudes\b", r"\bnude\b", r"\bnudes\b",
        r"\bdick pic\b", r"\bblowjob\b", r"\bpussy\b", r"\bpenis\b", r"\bvagina\b",
        r"\bnice tits\b", r"\bnice ass\b", r"\bfuck goats\b", r"\bgoat fucker\b",
        r"\bgoat fuckers\b", r"\bfucking goats\b"
    ],
    "abusive_language": [
        r"\basshole\b", r"\bassholes\b", r"\barsehole\b", r"\barseholes\b",
        r"\bdumbass\b", r"\bdumbasses\b", r"\bjackass\b", r"\bjackasses\b",
        r"\bsmartass\b", r"\bsmartasses\b", r"\bidiot\b", r"\bidiots\b",
        r"\bmoron\b", r"\bmorons\b", r"\bloser\b", r"\blosers\b",
        r"\btrash\b", r"\bpathetic\b", r"\bslut\b", r"\bwhore\b", r"\bhoe\b",
        r"\bcunt\b", r"\btwat\b", r"\bjerk\b", r"\bstupid\b", r"\bugly\b",
        r"\bqueer\b", r"\basses\b"
    ],
    "profanity": [
        r"\bfuck\b", r"\bfucks\b", r"\bfucking\b", r"\bfucker\b", r"\bfuckers\b",
        r"\bmotherfucker\b", r"\bmother fucker\b", r"\bshit\b", r"\bshits\b",
        r"\bshitty\b", r"\bbullshit\b", r"\bdamn\b", r"\bhell\b", r"\bass\b",
        r"\bbadass\b", r"\bbad ass\b", r"\bweakass\b", r"\bweak ass\b",
        r"\bsuckass\b", r"\bsuck ass\b", r"\bpiss off\b"
    ],
    "reckless_behavior": [
        r"\bdrunk\b", r"\bwasted\b", r"\bstoned\b", r"\bblackout\b", r"\bfight tonight\b"
    ],
    "emotional_reactivity": [
        r"\bi hate\b", r"\bhate you\b", r"\bcant stand\b", r"\bcan't stand\b",
        r"\bso mad\b", r"\bpissed off\b", r"\bdone with you\b", r"\bsick of you\b",
        r"\bscrew you\b", r"\bim done\b", r"\bi'm done\b", r"\bwhatever\b",
        r"\bdont care anymore\b", r"\bdon't care anymore\b"
    ],
    "sarcasm_contempt": [
        r"\bmust be nice\b",
        r"\bgood for you\b",
        r"\bgood for you i guess\b",
        r"\bthat explains a lot\b",
        r"\bwhat a joke\b",
        r"\binteresting that\b",
        r"\bno one asked\b",
        r"\bthanks for asking\b",
        r"\bbless your heart\b",
        r"\byeah right\b",
        r"\bsure you did\b"
    ],
    "dismissive_tone": [
        r"\bwhatever\b",
        r"\bget over it\b",
        r"\bwho cares\b",
        r"\bcry about it\b",
        r"\bnot my problem\b",
        r"\bdo better\b",
        r"\bfigure it out\b",
        r"\bthat sounds like a you problem\b",
        r"\bokay then\b",
        r"\bcool story\b"
    ],
    "passive_aggression": [
        r"\bi guess\b",
        r"\bif you say so\b",
        r"\bthat.?s cute\b",
        r"\bhow surprising\b",
        r"\bi.?m sure\b",
        r"\bthanks for that\b",
        r"\bnoted\b"
    ],
}

POSITIVE_SIGNAL_PATTERNS = {
     "gratitude": [
        r"\bgrateful\b", r"\bthankful\b", r"\bblessed\b", r"\bthank you\b",
        r"\bthanks for\b", r"\bappreciate\b", r"\bso thankful\b"
    ],
    "respect": [
        r"\brespect\b", r"\bproud of\b", r"\bappreciate you\b", r"\bthankful for\b",
        r"\bglad i got to\b", r"\bhonored\b"
    ],
    "maturity": [
        r"\blearned a lot\b", r"\blesson learned\b", r"\bgrowing\b", r"\bworking on myself\b",
        r"\bself control\b", r"\btrying to improve\b", r"\bbetter than i was\b",
        r"\btaking responsibility\b", r"\bownership\b"
    ],
    "leadership": [
        r"\bteammates\b", r"\bteam\b", r"\blead\b", r"\bleadership\b", r"\bsupporting others\b",
        r"\bshowing up\b", r"\bcommitted\b", r"\bfocused\b", r"\baccountable\b"
    ],
    "professionalism": [
        r"\bopportunity\b", r"\bcareer\b", r"\bwork ethic\b", r"\bprofessional\b",
        r"\bgoals\b", r"\bfuture\b", r"\bprepared\b"
    ],
    "encouragement": [
        r"\bproud of you\b", r"\byou got this\b", r"\bkeep going\b", r"\bwell done\b",
        r"\bgreat job\b", r"\bhappy for you\b", r"\bhang in there\b", r"\bstay strong\b"
    ],
    "positive_connection": [
        r"\bgreat time\b", r"\bgood people\b", r"\bgreat people\b", r"\bgreat atmosphere\b",
        r"\bfun night\b", r"\blove my family\b", r"\blove my wife\b", r"\blove my husband\b",
        r"\blove my parents\b", r"\bhad a great time\b", r"\breally enjoyed\b",
        r"\benjoyed the game\b", r"\benjoyed the night\b", r"\bhad fun\b"
    ],
    "empathy": [
        r"\bi can.?t imagine\b", r"\bthat must be hard\b", r"\bthat sounds hard\b",
        r"\bi.?m sorry\b", r"\bsorry you.?re dealing with that\b", r"\bsorry to hear that\b",
        r"\bthinking of you\b", r"\bhere for you\b", r"\byou.?re not alone\b",
        r"\bif you need anything\b", r"\bdon.?t hesitate to reach out\b", r"\breach out\b",
        r"\bhow are you holding up\b", r"\btake care of yourself\b"
    ],
    "supportive_tone": [
        r"\blet me know how i can help\b", r"\bi.?m here if you need me\b",
        r"\bhere if you need anything\b", r"\bglad to help\b", r"\bi.?ve got you\b",
        r"\bwe.?re here for you\b", r"\byou can count on me\b"
    ],
    "emotional_intelligence": [
        r"\bi understand\b", r"\bi hear you\b", r"\bthat makes sense\b",
        r"\bi appreciate your honesty\b", r"\bthanks for sharing\b",
        r"\bI understand how\b", r"\blet.?s talk\b"
    ]
}

NEGATIVE_WEIGHTS = {
    "public_threat": 40,
    "violence": 30,
    "hate_language": 32,
    "sexual_content": 20,
    "abusive_language": 20,
    "profanity": 16,
    "reckless_behavior": 12,
    "emotional_reactivity": 10,
    "sarcasm_contempt": 14,
    "dismissive_tone": 12,
    "passive_aggression": 10,
}

POSITIVE_WEIGHTS = {
    "gratitude": 10,
    "respect": 10,
    "maturity": 10,
    "leadership": 10,
    "professionalism": 9,
    "encouragement": 8,
    "positive_connection": 8,
    "empathy": 12,
    "supportive_tone": 10,
    "emotional_intelligence": 10
}

NEGATIVE_LABELS = {
    "public_threat": "Public threat or mass-harm language",
    "violence": "Threatening or violent language",
    "hate_language": "Hateful or discriminatory language",
    "sexual_content": "Sexualized, explicit, or graphic sexual content",
    "abusive_language": "Name-calling or potentially abusive language",
    "profanity": "Profane or inappropriate language",
    "reckless_behavior": "Reckless or irresponsible behavior signals",
    "emotional_reactivity": "Emotionally reactive tone",
    "sarcasm_contempt": "Sarcastic, contemptuous, or mocking tone",
    "dismissive_tone": "Dismissive or uncaring tone",
    "passive_aggression": "Passive-aggressive wording",
}

POSITIVE_LABELS = {
    "gratitude": "Gratitude or appreciation",
    "respect": "Respectful or affirming tone",
    "maturity": "Maturity or ownership",
    "leadership": "Leadership or team-oriented language",
    "professionalism": "Goal-oriented or professional language",
    "encouragement": "Encouragement or support",
    "positive_connection": "Healthy social connection",
    "empathy": "Empathy or compassionate language",
    "supportive_tone": "Supportive or helpful tone",
    "emotional_intelligence": "Emotional intelligence or thoughtful communication"
}

SPORT_CONTEXT_TERMS = [
    "court", "field", "game", "team", "season", "match", "won", "score",
    "basketball", "football", "baseball", "soccer", "tennis", "state"
]

SEVERE_NEGATIVE_SIGNALS = {"public_threat", "violence", "hate_language"}
MODERATE_NEGATIVE_SIGNALS = {"sexual_content", "abusive_language", "profanity", "reckless_behavior", "emotional_reactivity", "sarcasm_contempt", "dismissive_tone", "passive_aggression"}

def normalize_text(text):
    text = (text or "").lower()
    text = re.sub(r"[-_]", " ", text)
    text = re.sub(r"[^\w\s']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def has_sports_context(text):
    return any(term in text for term in SPORT_CONTEXT_TERMS)

def _matches_any_pattern(text, patterns):
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    return False

def detect_signal_matches(text):
    lowered = normalize_text(text)
    negative_hits = []
    positive_hits = []

    for signal, patterns in NEGATIVE_SIGNAL_PATTERNS.items():
        if signal == "violence" and has_sports_context(lowered):
            sport_safe_patterns = [
                r"\bbeat\b", r"\bbeat them\b", r"\bbeat those\b", r"\bkick ass\b", r"\bkickass\b"
            ]
            if any(re.search(p, lowered, flags=re.IGNORECASE) for p in sport_safe_patterns):
                violence_patterns = [
                    p for p in patterns
                    if p not in [r"\bkick his ass\b", r"\bkick her ass\b", r"\bbeat his ass\b", r"\bbeat her ass\b"]
                ]
                if _matches_any_pattern(lowered, violence_patterns):
                    negative_hits.append(signal)
                continue

        if _matches_any_pattern(lowered, patterns):
            negative_hits.append(signal)

    for signal, patterns in POSITIVE_SIGNAL_PATTERNS.items():
        if _matches_any_pattern(lowered, patterns):
            positive_hits.append(signal)

    return negative_hits, positive_hits

def score_text(negative_hits, positive_hits):
    score = 70

    for sig in negative_hits:
        score -= NEGATIVE_WEIGHTS.get(sig, 0)

    for sig in positive_hits:
        score += POSITIVE_WEIGHTS.get(sig, 0)

    if "abusive_language" in negative_hits and "profanity" in negative_hits:
        score -= 4

    if "sarcasm_contempt" in negative_hits and "dismissive_tone" in negative_hits:
        score -= 3

    if "sarcasm_contempt" in negative_hits and "passive_aggression" in negative_hits:
        score -= 2
    
    if any(sig in negative_hits for sig in SEVERE_NEGATIVE_SIGNALS):
        score -= 6

    if "empathy" in positive_hits and "supportive_tone" in positive_hits:
        score += 3

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

def build_summary(score, negative_hits, positive_hits, has_image=False, limited_image_review=False):
    if limited_image_review:
        return "Limited review only. This screenshot may contain text the tool cannot fully interpret from an image alone. Paste the visible text for the most trustworthy result."
    if has_image and not negative_hits:
        return "No obvious visual red flags were identified in this image, but text inside screenshots may still need pasted-text review for a full result."
    if any(sig in negative_hits for sig in SEVERE_NEGATIVE_SIGNALS):
        return "This message creates serious concern about safety, judgment, or trust."
    if "abusive_language" in negative_hits or "profanity" in negative_hits:
        return "This message may be read as disrespectful, immature, or reactive depending on who sees it."
    if "sarcasm_contempt" in negative_hits or "dismissive_tone" in negative_hits or "passive_aggression" in negative_hits:
        return "This message may sound cold, dismissive, or subtly disrespectful depending on who reads it."
    if "empathy" in positive_hits or "supportive_tone" in positive_hits or "emotional_intelligence" in positive_hits:
        return "This message reflects supportive, thoughtful, and emotionally aware communication."
    if score >= 85:
        return "This message appears to send a strong and healthy reputation signal."
    if score >= 65:
        return "This message appears relatively safe, but tone and context still matter."
    if score >= 40:
        return "This message may be sending mixed signals about maturity, judgment, or professionalism."
    if score >= 20:
        return "This message raises meaningful concerns about reputation, judgment, or self-control."
    return "This message creates serious concern about safety, maturity, or trust."

def build_why_it_matters(score, negative_hits, positive_hits, limited_image_review=False):
    if limited_image_review:
        return [
            "A screenshot can contain text, tone, and context that the tool cannot fully read from an image alone.",
            "If the image contains comments, captions, or messages, those words may carry very different signals than the image itself.",
            "For the most accurate result, paste the visible text into the text box."
        ]

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
    if "sarcasm_contempt" in negative_hits:
        reasons.append("Sarcasm or contempt can make a message sound immature, mocking, or disrespectful.")
    if "dismissive_tone" in negative_hits:
        reasons.append("Dismissive language may suggest low empathy, poor people skills, or weak emotional maturity.")
    if "passive_aggression" in negative_hits:
        reasons.append("Passive-aggressive wording can create tension and weaken trust.")
    
    if not negative_hits:
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
        if "empathy" in positive_hits:
            reasons.append("Empathy often signals emotional maturity, awareness, and care for others.")
        if "supportive_tone" in positive_hits:
            reasons.append("Supportive language can strengthen trust and show healthy relationship skills.")
        if "emotional_intelligence" in positive_hits:
            reasons.append("Thoughtful communication often reflects maturity, composure, and sound judgment.")

    if not reasons:
        reasons = [
            "Different audiences may interpret the same message in different ways.",
            "Tone, wording, and context all shape digital reputation.",
            "Even a short message can communicate maturity or immaturity."
        ]

    return reasons[:4]

def build_safer_alternatives(negative_hits, positive_hits, limited_image_review=False):
    if limited_image_review:
        return [
            "Paste the visible text from the screenshot into the text box for a stronger review.",
            "Use image upload as support, not as the only source, when the image contains written comments or captions."
        ]

    alts = []

    if "public_threat" in negative_hits or "violence" in negative_hits:
        alts.append("Remove any threatening or violent language completely.")
        alts.append("Pause before posting and choose calm, non-threatening words.")
    if "hate_language" in negative_hits:
        alts.append("Remove hateful or discriminatory language immediately.")
    if "abusive_language" in negative_hits:
        alts.append("Replace insults or name-calling with respectful wording.")
    if "profanity" in negative_hits:
        alts.append("Remove profanity if you want the message to sound more mature and professional.")
    if "sexual_content" in negative_hits:
        alts.append("Remove graphic or sexualized language if you want the message to reflect stronger judgment.")
    if "reckless_behavior" in negative_hits:
        alts.append("Avoid language that glorifies risky behavior.")
    if "emotional_reactivity" in negative_hits:
        alts.append("Wait before posting and rewrite the message once emotions settle.")
    if "sarcasm_contempt" in negative_hits:
        alts.append("Remove sarcastic or mocking wording if you want the message to sound more mature.")
    if "dismissive_tone" in negative_hits:
        alts.append("Rewrite the message with more empathy or respect for the other person.")
    if "passive_aggression" in negative_hits:
        alts.append("Say what you mean directly and respectfully instead of sounding indirect or resentful.")
    
    if not negative_hits and positive_hits:
        alts.append("Keep using clear, respectful language that reflects maturity.")
        alts.append("Lean into gratitude, respect, and purpose when you post.")
    elif not alts:
        alts.append("Add context if needed and keep the message respectful.")
        alts.append("Choose language that reflects the reputation you want to build.")

    return alts[:4]

def build_next_best_move(score, negative_hits, positive_hits, limited_image_review=False):
    if limited_image_review:
        return "Paste the visible text from this screenshot before relying on this result. That will give you a more trustworthy assessment."
    if "public_threat" in negative_hits or "violence" in negative_hits or "hate_language" in negative_hits:
        return "Do not post this as written. Remove the harmful language completely and rewrite from a calm, responsible place."
    if "abusive_language" in negative_hits or "profanity" in negative_hits:
        return "Rewrite this with more maturity and respect before posting. Removing the harsh language would strengthen the signal immediately."
    if "sexual_content" in negative_hits:
        return "Rewrite this to remove the sexual or graphic language if you want the post to reflect stronger judgment and maturity."
    if score < 40:
        return "Step back, remove the strongest risk signals, and rewrite with more self-control."
    if score < 65:
        return "Tighten the wording so the message sounds more mature, respectful, and intentional."
    return "This is fairly safe, but you can strengthen it further with clearer maturity and purpose."

def build_improve_note(score, negative_hits, positive_hits, limited_image_review=False):
    if limited_image_review:
        return "For screenshots of comments, captions, or posts, the pasted text is what makes this tool most accurate."
    if score >= 85:
        return "Messages like this get even stronger when they show gratitude, purpose, or encouragement."
    if "sexual_content" in negative_hits:
        return "Removing the sexual or graphic language would immediately strengthen the signal."
    if "emotional_reactivity" in negative_hits:
        return "A calmer tone would improve the signal quickly."
    if "profanity" in negative_hits or "abusive_language" in negative_hits:
        return "Removing the harsh language would immediately strengthen how this may be interpreted."
    if "violence" in negative_hits or "public_threat" in negative_hits:
        return "Any threatening wording heavily damages how this may be interpreted."
    if score < 65:
        return "A little more respect, self-control, or clarity could make a noticeable difference."
    return ""

def audience_line(label, interpretation):
    return f"{label}::{interpretation}"

def build_audience_interpretations(score, negative_hits, positive_hits, limited_image_review=False):
    if limited_image_review:
        return {
            "parents": audience_line("Parents reviewing this may think", "A screenshot alone may not give enough clarity. The text in the image could change the interpretation significantly."),
            "coaches": audience_line("Coaches reviewing this may think", "Without the written text pasted in, this is only a partial review and may miss important context."),
            "admissions": audience_line("Admissions reviewing this may think", "A screenshot can carry risk through words the tool may not fully interpret unless the text is pasted."),
            "employers": audience_line("Employers reviewing this may think", "This is only a limited review. The written content inside the screenshot matters most.")
        }

    severe = any(sig in negative_hits for sig in SEVERE_NEGATIVE_SIGNALS)
    moderate = any(sig in negative_hits for sig in MODERATE_NEGATIVE_SIGNALS)

    if severe:
        return {
            "parents": audience_line("Parents reviewing this may think", "This raises serious concern about judgment, safety, and self-control."),
            "coaches": audience_line("Coaches reviewing this may think", "This signals poor discipline, weak composure, and a major trust concern."),
            "admissions": audience_line("Admissions reviewing this may think", "This raises major concerns about maturity, judgment, and readiness."),
            "employers": audience_line("Employers reviewing this may think", "This would be viewed as a serious professionalism and trust problem.")
        }

    if "abusive_language" in negative_hits or "profanity" in negative_hits:
        return {
            "parents": audience_line("Parents reviewing this may think", "This message may raise concerns about maturity, respect, and emotional control."),
            "coaches": audience_line("Coaches reviewing this may think", "This sounds reactive and disrespectful rather than composed or team-first."),
            "admissions": audience_line("Admissions reviewing this may think", "This may weaken your image by sounding immature or lacking self-control."),
            "employers": audience_line("Employers reviewing this may think", "This does not reflect the professionalism or judgment most employers want to see.")
        }

    if "sexual_content" in negative_hits:
        return {
            "parents": audience_line("Parents reviewing this may think", "This may raise concerns about judgment, maturity, and boundaries."),
            "coaches": audience_line("Coaches reviewing this may think", "This may feel immature or distracting to your reputation."),
            "admissions": audience_line("Admissions reviewing this may think", "This may weaken perceptions of maturity and decision-making."),
            "employers": audience_line("Employers reviewing this may think", "This could feel inappropriate or unprofessional depending on the context.")
        }

    if "empathy" in positive_hits or "supportive_tone" in positive_hits or "emotional_intelligence" in positive_hits:
        return {
            "parents": audience_line("Parents reviewing this may think", "This reflects empathy, maturity, and healthy concern for another person."),
            "coaches": audience_line("Coaches reviewing this may think", "This sounds supportive, composed, and emotionally aware."),
            "admissions": audience_line("Admissions reviewing this may think", "This reflects emotional maturity, empathy, and thoughtful communication."),
            "employers": audience_line("Employers reviewing this may think", "This suggests professionalism, empathy, and strong people skills.")
        }

    if "emotional_reactivity" in negative_hits or "reckless_behavior" in negative_hits or moderate:
        return {
            "parents": audience_line("Parents reviewing this may think", "This may suggest reactive judgment or weaker self-control."),
            "coaches": audience_line("Coaches reviewing this may think", "This may signal inconsistency, impulsiveness, or weak discipline."),
            "admissions": audience_line("Admissions reviewing this may think", "This creates mixed signals about maturity and judgment."),
            "employers": audience_line("Employers reviewing this may think", "This may raise concerns about professionalism and reliability.")
        }

    parents = []
    coaches = []
    admissions = []
    employers = []

    if "gratitude" in positive_hits:
        parents.append("This shows appreciation and perspective.")
        coaches.append("This reflects coachability and maturity.")
        admissions.append("This shows reflection and emotional maturity.")
        employers.append("Gratitude is a positive professionalism signal.")

    if "respect" in positive_hits:
        parents.append("This sounds respectful and grounded.")
        coaches.append("This reflects self-control and respect for others.")
        admissions.append("This shows maturity and healthy communication.")
        employers.append("Respectful language supports professionalism.")

    if "leadership" in positive_hits:
        parents.append("This shows growth in how you relate to others.")
        coaches.append("This sounds team-first and leadership-oriented.")
        admissions.append("This reflects contribution and maturity.")
        employers.append("This suggests accountability and teamwork.")

    if "professionalism" in positive_hits or "maturity" in positive_hits:
        parents.append("This reflects stronger judgment and responsibility.")
        coaches.append("This shows discipline and maturity.")
        admissions.append("This strengthens readiness and judgment.")
        employers.append("This feels more professional and future-minded.")

    if "positive_connection" in positive_hits:
        parents.append("This looks healthy and socially appropriate.")
        coaches.append("This feels like normal positive social behavior.")
        admissions.append("This is low-risk and socially appropriate.")
        employers.append("This appears low-risk if the tone stays respectful.")

    def fallback_or_join(items, fallback):
        return " ".join(items[:2]) if items else fallback

    return {
        "parents": audience_line("Parents reviewing this may think", fallback_or_join(parents, "This message appears relatively safe if the tone and context stay respectful.")),
        "coaches": audience_line("Coaches reviewing this may think", fallback_or_join(coaches, "This message appears reasonably controlled and low-risk.")),
        "admissions": audience_line("Admissions reviewing this may think", fallback_or_join(admissions, "This appears relatively safe, though context still matters.")),
        "employers": audience_line("Employers reviewing this may think", fallback_or_join(employers, "This appears relatively low-risk if it fits the broader context of your profile."))
    }

def analyze_text(text, has_image=False):
    lowered = normalize_text(text)

    if has_image and not lowered:
        score = 50
        return {
            "strength_score": score,
            "category": "Limited Review",
            "result_summary": build_summary(score, [], [], has_image=True, limited_image_review=True),
            "top_risks": [
                "Screenshot uploaded without pasted text.",
                "The tool cannot fully analyze written text inside images yet.",
                "This result should not be treated as a full reputation review."
            ],
            "positive_signals": ["Limited image review only"],
            "why_it_matters": build_why_it_matters(score, [], [], limited_image_review=True),
            "safer_alternatives": build_safer_alternatives([], [], limited_image_review=True),
            "next_best_move": build_next_best_move(score, [], [], limited_image_review=True),
            "improve_note": build_improve_note(score, [], [], limited_image_review=True),
            "audience_interpretations": build_audience_interpretations(score, [], [], limited_image_review=True)
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
        "next_best_move": build_next_best_move(score, negative_hits, positive_hits),
        "improve_note": build_improve_note(score, negative_hits, positive_hits),
        "audience_interpretations": build_audience_interpretations(score, negative_hits, positive_hits)
    }

def build_carry_message(score):
    if score is None:
        return None
    if score >= 85:
        return "That suggests strong awareness. Now test how individual posts actually signal that reputation."
    if score >= 50:
        return "That suggests some habits may be creating mixed signals. Now test how specific posts may be interpreted."
    return "That suggests your digital reputation may be vulnerable. Now test real posts to see which signals need to change."

def render_checker_page(graduate=False, carry_score=None):
    return render_template_string(
        CHECKER_HTML,
        page_title="Graduate Access: Digital Reputation Assessment" if graduate else "Leadhawk Digital Reputation Assessment",
        header_title="Graduate Access: Digital Reputation Assessment" if graduate else "Leadhawk Digital Reputation Assessment",
        logo_url=url_for("logo"),
        pyb_url=PYB_CHECKOUT_URL,
        carry_score=carry_score,
        carry_message=build_carry_message(carry_score),
        graduate=graduate
    )

def scan_impl(unlimited=False):
    text = request.form.get("text", "").strip()
    image = request.files.get("image")
    has_image = image is not None and image.filename != ""

    if not text and not has_image:
        return jsonify({"message": "Please paste some text or upload a screenshot first."}), 400

    if text and has_image:
        return jsonify({
            "message": "Please use either pasted text or an image for one check, not both. If your screenshot contains words, paste the visible text for the most accurate result."
        }), 400

    user_ip = request.remote_addr or "unknown"

    if not unlimited:
        if user_ip not in usage_log:
            usage_log[user_ip] = 0

        if usage_log[user_ip] >= FREE_CHECK_LIMIT:
            return jsonify({
                "limit_reached": True,
                "message": "You’ve used your 2 free Reputation Signal Tests.",
                "submessage": "Complete the Protect Your Brand Challenge to unlock Graduate Access.",
                "pyb_url": PYB_CHECKOUT_URL
            }), 403

    try:
        result = analyze_text(text, has_image)
    except Exception as e:
        return jsonify({"message": f"Analysis error: {str(e)}"}), 500

    if unlimited:
        result["checks_used"] = 999
        result["checks_remaining"] = 999
    else:
        usage_log[user_ip] += 1
        result["checks_used"] = usage_log[user_ip]
        result["checks_remaining"] = max(0, FREE_CHECK_LIMIT - usage_log[user_ip])

    result["pyb_url"] = PYB_CHECKOUT_URL
    return jsonify(result)

@app.route("/")
def home():
    return redirect(url_for("survey"))

@app.route("/survey")
def survey():
    return render_template_string(SURVEY_HTML, checker_url=url_for("checker"))

@app.route("/checker")
def checker():
    return redirect("https://www.leadhawklearning.com/results")

@app.route("/redirect-test")
def redirect_test():
    return redirect("https://www.leadhawklearning.com/results")

@app.route("/checker-unlimited")
def checker_unlimited():
    return render_checker_page(graduate=True, carry_score=None)

@app.route("/scan", methods=["POST"])
def scan():
    return scan_impl(unlimited=False)

@app.route("/scan-unlimited", methods=["POST"])
def scan_unlimited():
    return scan_impl(unlimited=True)

@app.route("/logo")
def logo():
    return send_from_directory(".", LOGO_FILENAME)

@app.route("/manifest.json")
def manifest():
    return jsonify({
        "name": "Leadhawk Digital Reputation Tools",
        "short_name": "Leadhawk",
        "start_url": "/survey",
        "display": "standalone",
        "background_color": "#23364f",
        "theme_color": "#23364f",
        "icons": [
            {"src": "/logo", "sizes": "192x192", "type": "image/png"},
            {"src": "/logo", "sizes": "512x512", "type": "image/png"}
        ]
    })

@app.route("/reset")
def reset_checks():
    usage_log.clear()
    return "Checks reset."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)

