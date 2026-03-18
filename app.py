import os
import re
from flask import Flask, request, render_template_string

app = Flask(__name__)

FREE_CHECK_LIMIT = 2
usage_log = {}

# -------------------------
# SIGNAL DETECTION
# -------------------------

PROFANITY = [
    "asshole", "ass", "shit", "fuck", "bitch", "damn"
]

NEGATIVE_TONE = [
    "hate", "stupid", "idiot", "loser", "trash"
]

SEXUAL_TERMS = [
    "sex", "nude", "hookup", "onlyfans"
]

def analyze_text(text):
    text_lower = text.lower()

    signals = []
    score = 70

    # Profanity
    if any(word in text_lower for word in PROFANITY):
        signals.append("Name-calling or potentially abusive language")
        score -= 20

    # Negative tone
    if any(word in text_lower for word in NEGATIVE_TONE):
        signals.append("Negative or disrespectful tone")
        score -= 15

    # Sexual content
    if any(word in text_lower for word in SEXUAL_TERMS):
        signals.append("Potentially inappropriate or sexual content")
        score -= 20

    score = max(0, min(score, 100))

    return score, signals

# -------------------------
# HTML TEMPLATE
# -------------------------

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Digital Reputation Assessment</title>
<style>
body { font-family: Arial; background:#0f2a44; color:white; padding:20px;}
.container { background:white; color:black; padding:20px; border-radius:10px;}
textarea { width:100%; height:120px;}
button { padding:10px 20px; margin-top:10px;}
.result { margin-top:20px;}
.badge { font-weight:bold; color:#f0b429;}
</style>
</head>

<body>

<h1>{{ header }}</h1>

{% if graduate %}
<p><b>Graduate Access:</b> You now have full access to test your digital reputation anytime.</p>
{% else %}
<p>Test how your posts, comments, or messages may be interpreted.</p>
{% endif %}

<div class="container">

<form method="POST">
<textarea name="user_input" placeholder="Enter text...">{{ user_input }}</textarea>

<br>

<input type="file" name="file">

<br>

<button type="submit">Test My Reputation Signal</button>
</form>

{% if result %}
<div class="result">

<h2>Digital Reputation Signal: {{ score }}/100</h2>

<p><b>Signals Detected:</b></p>

<ul>
{% for s in signals %}
<li>{{ s }}</li>
{% endfor %}
</ul>

{% if not signals %}
<p>No major red flags detected.</p>
{% endif %}

</div>
{% endif %}

</div>

{% if not graduate %}
<p><i>Complete Protect Your Brand to unlock full access.</i></p>
{% endif %}

</body>
</html>
"""

# -------------------------
# FREE CHECKER
# -------------------------

@app.route("/checker", methods=["GET", "POST"])
def checker():

    user_ip = request.remote_addr
    usage_log[user_ip] = usage_log.get(user_ip, 0)

    if usage_log[user_ip] >= FREE_CHECK_LIMIT:
        return "<h2>Limit reached. Complete Protect Your Brand for full access.</h2>"

    result = False
    score = 0
    signals = []
    user_input = ""

    if request.method == "POST":

        user_input = request.form.get("user_input", "")
        file = request.files.get("file")

        if user_input:
            score, signals = analyze_text(user_input)
            result = True

        elif file:
            score = 70
            signals = ["Image review is limited. Consider tone, context, and perception."]
            result = True

        usage_log[user_ip] += 1

        # CLEAR INPUT AFTER SUBMIT
        user_input = ""

    return render_template_string(
        TEMPLATE,
        header="Digital Reputation Assessment",
        graduate=False,
        result=result,
        score=score,
        signals=signals,
        user_input=user_input
    )

# -------------------------
# GRADUATE ACCESS
# -------------------------

@app.route("/checker-unlimited", methods=["GET", "POST"])
def checker_unlimited():

    result = False
    score = 0
    signals = []
    user_input = ""

    if request.method == "POST":

        user_input = request.form.get("user_input", "")
        file = request.files.get("file")

        if user_input:
            score, signals = analyze_text(user_input)
            result = True

        elif file:
            score = 70
            signals = ["Image review is limited. Consider tone, context, and perception."]
            result = True

        # CLEAR INPUT AFTER SUBMIT
        user_input = ""

    return render_template_string(
        TEMPLATE,
        header="Graduate Access: Digital Reputation Assessment",
        graduate=True,
        result=result,
        score=score,
        signals=signals,
        user_input=user_input
    )

# -------------------------

if __name__ == "__main__":
    app.run()
