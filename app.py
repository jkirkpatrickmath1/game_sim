from flask import Flask, render_template, request, session, redirect
from schedular import generate_matches
import math

app = Flask(__name__)
import os
app.secret_key = os.environ.get("SECRET_KEY", "dev")

def make_team(name):
    return {
        "name": name,
        "rp": 0,
        "auto": 0,
        "match": 0,
        "matches_played": 0
    }

def make_match(num, red, blue):
    return {
        "num": num,
        "red": red,
        "blue": blue
    }

def get_team(name):
    for team in session["teams"]:
        if team["name"] == name:
            return team
    return None

@app.route("/", methods=["GET"])
def start():
    return render_template("start.html")

@app.route("/schedule", methods=["POST"])
def schedule():
    raw_names = request.form["names"]
    names = [n.strip() for n in raw_names.split("\n") if n.strip()]

    teams = [make_team(name) for name in names]
    matches = generate_matches(names)

    session["teams"] = teams
    session["matches"] = matches
    session["current_match"] = 0

    return render_template("schedule.html", matches=matches)

@app.route("/match", methods=["GET", "POST"])
def match():
    if "matches" not in session:
        return "No active tournament"

    matches = session["matches"]
    teams = session["teams"]
    current = session["current_match"]

    if current >= len(matches):
        return redirect("/rankings")

    match_obj = matches[current]

    if request.method == "POST":
        red_rp = int(request.form.get("red_rp", 0))
        red_match = int(request.form.get("red_match", 0))
        red_auto = int(request.form.get("red_auto", 0))

        blue_rp = int(request.form.get("blue_rp", 0))
        blue_match = int(request.form.get("blue_match", 0))
        blue_auto = int(request.form.get("blue_auto", 0))

        # RP bonus
        if red_match > blue_match:
            red_rp += 3
        elif blue_match > red_match:
            blue_rp += 3
        else:
            red_rp += 1
            blue_rp += 1

        for name in match_obj["red"]:
            team = get_team(name)
            team["rp"] += red_rp
            team["auto"] += red_auto
            team["match"] += red_match
            team["matches_played"] += 1

        for name in match_obj["blue"]:
            team = get_team(name)
            team["rp"] += blue_rp
            team["auto"] += blue_auto
            team["match"] += blue_match
            team["matches_played"] += 1

        session["current_match"] += 1
        session.modified = True

        return redirect("/rankings")

    # ADDED: compute next two matches for ticker
    next_matches = []
    for i in range(1, 3):
        if current + i < len(matches):
            next_matches.append(matches[current + i])

    return render_template(
        "match.html",
        match=match_obj,
        next_matches=next_matches  # ADDED
    )

@app.route("/rankings")
def rankings():
    if "teams" not in session:
        return "No active tournament"

    teams = session["teams"]
    matches = session["matches"]
    current = session["current_match"]

    def avg(team, key):
        if team["matches_played"] == 0:
            return 0
        return team[key] / team["matches_played"]

    sorted_teams = sorted(
        teams,
        key=lambda t: (-avg(t, "rp"), -avg(t, "match"), -avg(t, "auto"))
    )

    for team in teams:
        mp = team["matches_played"]
        team["avg_rp"] = team["rp"] / mp if mp > 0 else 0
        team["avg_auto"] = team["auto"] / mp if mp > 0 else 0
        team["avg_match"] = team["match"] / mp if mp > 0 else 0

    if current >= len(matches):
        match = None
    else:
        match = matches[current]  # FIXED: removed trailing comma

    next_matches = []
    for i in range(1, 3):
        if current + i < len(matches):
            next_matches.append(matches[current + i])

    return render_template(
        "rankings.html",
        teams=sorted_teams,
        matches=matches,
        match=match,
        current_match=current,
        total_matches=len(matches),
        next_matches=next_matches 
    )

if __name__ == "__main__":
    app.run()
