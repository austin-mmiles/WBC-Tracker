#!/usr/bin/env python3
"""
WBC Fantasy Stats Fetcher
Run this script to pull live WBC stats and generate your dashboard.

SETUP (one time):
  pip install requests

RUN:
  python3 fetch_wbc_stats.py

It will create/overwrite wbc_dashboard.html with fresh stats.
Run it whenever you want to update the scores.
"""

import requests
import json
import math
import sys
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
WBC_START = "2026-03-05"
WBC_END   = "2026-03-17"
SEASON    = 2026
BASE      = "https://statsapi.mlb.com/api/v1"
HEADERS   = {"User-Agent": "WBCFantasy/1.0"}
TIMEOUT   = 15

# Pitcher role assumptions: innings per game appearance
PITCHER_IP_STARTER  = 3.0
PITCHER_IP_RELIEVER = 1.0

# ─── ROSTERS ──────────────────────────────────────────────────────────────────
ROSTERS = {
    "Austin": {"color": "#4da6ff", "players": [
        {"name": "Alejandro Kirk",       "pos": "C",    "nation": "Mexico"},
        {"name": "Bobby Witt Jr.",        "pos": "INF",  "nation": "USA"},
        {"name": "Ketel Marte",           "pos": "INF",  "nation": "DR"},
        {"name": "Xander Bogaerts",       "pos": "INF",  "nation": "Netherlands"},
        {"name": "Josh Naylor",           "pos": "INF",  "nation": "Canada"},
        {"name": "Nolan Arenado",         "pos": "INF",  "nation": "PR"},
        {"name": "Hyeseong Kim",          "pos": "INF",  "nation": "Korea"},
        {"name": "Juan Soto",             "pos": "OF",   "nation": "DR"},
        {"name": "Fernando Tatis Jr.",    "pos": "OF",   "nation": "DR"},
        {"name": "Ronald Acuna Jr.",      "pos": "OF",   "nation": "Venezuela"},
        {"name": "Jackson Chourio",       "pos": "OF",   "nation": "Venezuela"},
        {"name": "Shohei Ohtani",         "pos": "UTIL", "nation": "Japan"},
        {"name": "Kyle Schwarber",        "pos": "UTIL", "nation": "USA"},
        {"name": "Rowdy Tellez",          "pos": "UTIL", "nation": "Mexico"},
        {"name": "Hiromi Itoh",           "pos": "P",    "nation": "Japan"},
        {"name": "Yoshinobu Yamamoto",    "pos": "P",    "nation": "Japan"},
        {"name": "Mason Miller",          "pos": "P",    "nation": "USA"},
        {"name": "Ranger Suarez",         "pos": "P",    "nation": "Venezuela"},
        {"name": "Edwin Diaz",            "pos": "P",    "nation": "PR"},
        {"name": "Seth Lugo",             "pos": "P",    "nation": "PR"},
    ]},
    "AJ": {"color": "#f5c542", "players": [
        {"name": "William Contreras",     "pos": "C",    "nation": "Venezuela"},
        {"name": "Vladimir Guerrero Jr.", "pos": "INF",  "nation": "DR"},
        {"name": "Josh Naylor",           "pos": "INF",  "nation": "Canada"},
        {"name": "Otto Lopez",            "pos": "INF",  "nation": "Canada"},
        {"name": "Nolan Arenado",         "pos": "INF",  "nation": "PR"},
        {"name": "Eugenio Suarez",        "pos": "INF",  "nation": "Venezuela"},
        {"name": "Hyeseong Kim",          "pos": "INF",  "nation": "Korea"},
        {"name": "Fernando Tatis Jr.",    "pos": "OF",   "nation": "DR"},
        {"name": "Seiya Suzuki",          "pos": "OF",   "nation": "Japan"},
        {"name": "Heliot Ramos",          "pos": "OF",   "nation": "PR"},
        {"name": "Aaron Judge",           "pos": "OF",   "nation": "USA"},
        {"name": "Shohei Ohtani",         "pos": "UTIL", "nation": "Japan"},
        {"name": "Ronald Acuna Jr.",      "pos": "UTIL", "nation": "Venezuela"},
        {"name": "Jarren Duran",          "pos": "UTIL", "nation": "Mexico"},
        {"name": "Cristopher Sanchez",    "pos": "P",    "nation": "DR"},
        {"name": "Yoshinobu Yamamoto",    "pos": "P",    "nation": "Japan"},
        {"name": "James Paxton",          "pos": "P",    "nation": "Canada"},
        {"name": "Edwin Diaz",            "pos": "P",    "nation": "PR"},
        {"name": "Paul Skenes",           "pos": "P",    "nation": "USA"},
        {"name": "Mason Miller",          "pos": "P",    "nation": "USA"},
    ]},
    "Nathan": {"color": "#f05252", "players": [
        {"name": "Cal Raleigh",           "pos": "C",    "nation": "USA"},
        {"name": "Vladimir Guerrero Jr.", "pos": "INF",  "nation": "DR"},
        {"name": "Josh Naylor",           "pos": "INF",  "nation": "Canada"},
        {"name": "Nolan Arenado",         "pos": "INF",  "nation": "PR"},
        {"name": "Ketel Marte",           "pos": "INF",  "nation": "DR"},
        {"name": "Jonathan Aranda",       "pos": "INF",  "nation": "Mexico"},
        {"name": "Xander Bogaerts",       "pos": "INF",  "nation": "Netherlands"},
        {"name": "Aaron Judge",           "pos": "OF",   "nation": "USA"},
        {"name": "Juan Soto",             "pos": "OF",   "nation": "DR"},
        {"name": "Ronald Acuna Jr.",      "pos": "OF",   "nation": "Venezuela"},
        {"name": "Randy Arozarena",       "pos": "OF",   "nation": "Mexico"},
        {"name": "Shohei Ohtani",         "pos": "UTIL", "nation": "Japan"},
        {"name": "Bo Naylor",             "pos": "UTIL", "nation": "Canada"},
        {"name": "Luis Arraez",           "pos": "UTIL", "nation": "Venezuela"},
        {"name": "Paul Skenes",           "pos": "P",    "nation": "USA"},
        {"name": "Yoshinobu Yamamoto",    "pos": "P",    "nation": "Japan"},
        {"name": "Yusei Kikuchi",         "pos": "P",    "nation": "Japan"},
        {"name": "Kenley Jansen",         "pos": "P",    "nation": "Netherlands"},
        {"name": "Jameson Taillon",       "pos": "P",    "nation": "Canada"},
        {"name": "Aaron Nola",            "pos": "P",    "nation": "Italy"},
    ]},
    "Marcus": {"color": "#a855f7", "players": [
        {"name": "Alejandro Kirk",        "pos": "C",    "nation": "Mexico"},
        {"name": "Bryce Harper",          "pos": "INF",  "nation": "USA"},
        {"name": "Ketel Marte",           "pos": "INF",  "nation": "DR"},
        {"name": "Vinnie Pasquantino",    "pos": "INF",  "nation": "Italy"},
        {"name": "Jazz Chisholm Jr.",     "pos": "INF",  "nation": "GB"},
        {"name": "Munetaka Murakami",     "pos": "INF",  "nation": "Japan"},
        {"name": "Josh Naylor",           "pos": "INF",  "nation": "Canada"},
        {"name": "Fernando Tatis Jr.",    "pos": "OF",   "nation": "DR"},
        {"name": "Juan Soto",             "pos": "OF",   "nation": "DR"},
        {"name": "Ronald Acuna Jr.",      "pos": "OF",   "nation": "Venezuela"},
        {"name": "Jarren Duran",          "pos": "OF",   "nation": "Mexico"},
        {"name": "Shohei Ohtani",         "pos": "UTIL", "nation": "Japan"},
        {"name": "Aaron Judge",           "pos": "UTIL", "nation": "USA"},
        {"name": "Randy Arozarena",       "pos": "UTIL", "nation": "Mexico"},
        {"name": "Paul Skenes",           "pos": "P",    "nation": "USA"},
        {"name": "Edwin Diaz",            "pos": "P",    "nation": "PR"},
        {"name": "Aaron Nola",            "pos": "P",    "nation": "Italy"},
        {"name": "Ranger Suarez",         "pos": "P",    "nation": "Venezuela"},
        {"name": "Seth Lugo",             "pos": "P",    "nation": "PR"},
        {"name": "Yoshinobu Yamamoto",    "pos": "P",    "nation": "Japan"},
    ]},
    "Evan": {"color": "#3ecf8e", "players": [
        {"name": "Cal Raleigh",           "pos": "C",    "nation": "USA"},
        {"name": "Vladimir Guerrero Jr.", "pos": "INF",  "nation": "DR"},
        {"name": "Ketel Marte",           "pos": "INF",  "nation": "DR"},
        {"name": "Gleyber Torres",        "pos": "INF",  "nation": "Venezuela"},
        {"name": "Nolan Arenado",         "pos": "INF",  "nation": "PR"},
        {"name": "Alex Bregman",          "pos": "INF",  "nation": "USA"},
        {"name": "Jazz Chisholm Jr.",     "pos": "INF",  "nation": "GB"},
        {"name": "Randy Arozarena",       "pos": "OF",   "nation": "Mexico"},
        {"name": "Jarren Duran",          "pos": "OF",   "nation": "Mexico"},
        {"name": "Juan Soto",             "pos": "OF",   "nation": "DR"},
        {"name": "Jackson Chourio",       "pos": "OF",   "nation": "Venezuela"},
        {"name": "Shohei Ohtani",         "pos": "UTIL", "nation": "Japan"},
        {"name": "Tyler O'Neill",          "pos": "UTIL", "nation": "Canada"},
        {"name": "Xander Bogaerts",       "pos": "UTIL", "nation": "Netherlands"},
        {"name": "Hiromi Itoh",           "pos": "P",    "nation": "Japan"},
        {"name": "Seth Lugo",             "pos": "P",    "nation": "PR"},
        {"name": "Yoshinobu Yamamoto",    "pos": "P",    "nation": "Japan"},
        {"name": "Andres Munoz",          "pos": "P",    "nation": "Mexico"},
        {"name": "Edwin Diaz",            "pos": "P",    "nation": "PR"},
        {"name": "Paul Skenes",           "pos": "P",    "nation": "USA"},
    ]},
    "Quinn": {"color": "#ff6eb4", "players": [
        {"name": "Alejandro Kirk",        "pos": "C",    "nation": "Mexico"},
        {"name": "Vladimir Guerrero Jr.", "pos": "INF",  "nation": "DR"},
        {"name": "Bryce Harper",          "pos": "INF",  "nation": "USA"},
        {"name": "Bobby Witt Jr.",        "pos": "INF",  "nation": "USA"},
        {"name": "Michael Arroyo",        "pos": "INF",  "nation": "Colombia"},
        {"name": "Shugo Maki",            "pos": "INF",  "nation": "Japan"},
        {"name": "Maikel Garcia",         "pos": "INF",  "nation": "Venezuela"},
        {"name": "Aaron Judge",           "pos": "OF",   "nation": "USA"},
        {"name": "Juan Soto",             "pos": "OF",   "nation": "DR"},
        {"name": "Ronald Acuna Jr.",      "pos": "OF",   "nation": "Venezuela"},
        {"name": "Julio Rodriguez",       "pos": "OF",   "nation": "DR"},
        {"name": "Shohei Ohtani",         "pos": "UTIL", "nation": "Japan"},
        {"name": "Denzel Clarke",         "pos": "UTIL", "nation": "Canada"},
        {"name": "Heliot Ramos",          "pos": "UTIL", "nation": "PR"},
        {"name": "Edwin Diaz",            "pos": "P",    "nation": "PR"},
        {"name": "Taisei Ota",            "pos": "P",    "nation": "Japan"},
        {"name": "Seth Lugo",             "pos": "P",    "nation": "PR"},
        {"name": "Andres Munoz",          "pos": "P",    "nation": "Mexico"},
        {"name": "Victor Vodnik",         "pos": "P",    "nation": "Mexico"},
        {"name": "Eduard Bazardo",        "pos": "P",    "nation": "Venezuela"},
    ]},
}

# ─── SCORING ──────────────────────────────────────────────────────────────────
SCORING = {
    "hitting":  {"tb":1,"rbi":1,"r":1,"sb":1,"bb":1,"hbp":1,"so":-1,"cs":-1},
    "pitching": {"ip":3,"w":2,"l":-2,"qs":3,"k":1,"bbA":-1,"er":-2,"hb":-1,"hA":-1,"hld":2,"sv":4},
}

# Nation label → API team name aliases (for flag/elimination lookup)
NATION_ALIASES = {
    "USA":         ["united states", "usa"],
    "Japan":       ["japan"],
    "DR":          ["dominican republic", "dominican"],
    "Mexico":      ["mexico"],
    "Venezuela":   ["venezuela"],
    "PR":          ["puerto rico"],
    "Korea":       ["korea", "south korea"],
    "Canada":      ["canada"],
    "Netherlands": ["netherlands"],
    "Italy":       ["italy"],
    "Cuba":        ["cuba"],
    "Panama":      ["panama"],
    "GB":          ["great britain", "gb"],
    "Colombia":    ["colombia"],
    "Australia":   ["australia"],
    "Taiwan":      ["taiwan", "chinese taipei"],
}

def team_name_to_nation(team_name):
    if not team_name:
        return None
    tl = team_name.lower()
    for nation, aliases in NATION_ALIASES.items():
        if any(alias in tl for alias in aliases):
            return nation
    return None

# ─── OWNERSHIP ────────────────────────────────────────────────────────────────
def compute_ownership(norm_fn):
    """Returns {normalized_player_name: (count, num_teams, [owner_names])} across all rosters."""
    from collections import defaultdict
    num_teams = len(ROSTERS)
    owner_map = defaultdict(list)
    for owner, data in ROSTERS.items():
        for p in data["players"]:
            owner_map[norm_fn(p["name"])].append(owner)
    return {name: (len(owners), num_teams, owners) for name, owners in owner_map.items()}

# ─── ELIMINATION ──────────────────────────────────────────────────────────────
# Manually update this set as teams are knocked out of the tournament.
# Nation names must match the keys used in NATION_ALIASES above.
ELIMINATED_NATIONS = {
    "Mexico",
    "Netherlands",
    "Cuba",
    "Panama",
    "GB",
    "Colombia",
    "Australia",
    "Taiwan",
    "Brazil",
    "Czechia",
    "Israel",
    "Nicaragua",
    "Korea",
    "Canada",
    "Japan",
    "PR",
    "DR",
    "Venezuela",
}

def fetch_nation_odds():
    """Returns elimination status based on ELIMINATED_NATIONS set above."""
    result = {}
    for nation in NATION_ALIASES:
        eliminated = nation in ELIMINATED_NATIONS
        result[nation] = {"eliminated": eliminated, "expected_games": 0.0 if eliminated else 3.0}
        if eliminated:
            print(f"  ❌ {nation} — eliminated")
    return result


def compute_proj_pts(player, pts_so_far, games_played_by_nation, nation_odds):
    """
    Project remaining fantasy points for a player.
    - Hitters: pts_per_game × expected_remaining_games
    - Pitchers: use IP-based rate × PITCHER_IP_STARTER or PITCHER_IP_RELIEVER
    Returns (proj_pts, eliminated) tuple.
    """
    nation = player["nation"]
    odds = nation_odds.get(nation, {"eliminated": False, "expected_games": 3.0})

    if odds["eliminated"]:
        return 0.0, True

    expected_games = odds["expected_games"]
    games_played = games_played_by_nation.get(nation, 1)
    if games_played == 0:
        games_played = 1

    is_pitcher = player["pos"] == "P"

    if is_pitcher:
        # Determine if starter or reliever from IP rate
        ip_per_game = PITCHER_IP_STARTER if pts_so_far > 0 and pts_so_far / games_played > 5 else PITCHER_IP_RELIEVER
        # Projected IP remaining
        proj_ip = ip_per_game * expected_games
        # Use pitching scoring: ip*3 is the baseline, scale from current pts rate
        pts_per_ip = (pts_so_far / (games_played * ip_per_game)) if games_played > 0 and pts_so_far != 0 else SCORING["pitching"]["ip"]
        proj = pts_per_ip * proj_ip
    else:
        pts_per_game = pts_so_far / games_played if pts_so_far != 0 else 0
        proj = pts_per_game * expected_games

    return round(proj, 1), False


def normalize(name):
    import unicodedata, re
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    name = name.lower()
    name = re.sub(r"[^a-z ]", "", name)
    name = re.sub(r"\b(jr|sr|ii|iii)\b", "", name)
    return re.sub(r"\s+", " ", name).strip()

def parse_ip(ip_raw):
    parts = str(ip_raw or "0").split(".")
    return int(parts[0]) + int(parts[1] if len(parts) > 1 else 0) / 3

def calc_hitting(s):
    if not s: return 0
    sc = SCORING["hitting"]
    tb = (s.get("hits",0) - s.get("doubles",0) - s.get("triples",0) - s.get("homeRuns",0)
          + 2*s.get("doubles",0) + 3*s.get("triples",0) + 4*s.get("homeRuns",0))
    return (tb*sc["tb"] + s.get("rbi",0)*sc["rbi"] + s.get("runs",0)*sc["r"]
            + s.get("stolenBases",0)*sc["sb"] + s.get("baseOnBalls",0)*sc["bb"]
            + s.get("hitByPitch",0)*sc["hbp"] + s.get("strikeOuts",0)*sc["so"]
            + s.get("caughtStealing",0)*sc["cs"])

def calc_pitching(s):
    if not s: return 0
    sc = SCORING["pitching"]
    ip = s.get("_ipDecimal", parse_ip(s.get("inningsPitched","0")))
    er = s.get("earnedRuns",0)
    qs = 1 if ip >= 6 and er <= 3 else 0
    return (ip*sc["ip"] + s.get("wins",0)*sc["w"] + s.get("losses",0)*sc["l"]
            + qs*sc["qs"] + s.get("strikeOuts",0)*sc["k"]
            + s.get("baseOnBalls",0)*sc["bbA"] + er*sc["er"]
            + s.get("hitByPitch",0)*sc["hb"] + s.get("hits",0)*sc["hA"]
            + s.get("holds",0)*sc["hld"] + s.get("saves",0)*sc["sv"])

def merge(cache, name, pid, group, stat):
    key = normalize(name)
    if key not in cache:
        cache[key] = {"fullName": name, "id": pid, "hitting": None, "pitching": None}
    entry = cache[key]
    fields_h = ["hits","doubles","triples","homeRuns","rbi","runs","stolenBases",
                "baseOnBalls","hitByPitch","strikeOuts","caughtStealing","atBats"]
    fields_p = ["wins","losses","earnedRuns","hits","baseOnBalls","strikeOuts",
                "hitByPitch","holds","saves"]
    if group == "hitting":
        if not entry["hitting"]: entry["hitting"] = {}
        h = entry["hitting"]
        for f in fields_h: h[f] = h.get(f,0) + stat.get(f,0)
    elif group == "pitching":
        if not entry["pitching"]: entry["pitching"] = {}
        p = entry["pitching"]
        new_ip = parse_ip(stat.get("inningsPitched","0"))
        p["_ipDecimal"] = p.get("_ipDecimal",0) + new_ip
        full = int(p["_ipDecimal"])
        thirds = round((p["_ipDecimal"] - full) * 3)
        p["inningsPitched"] = f"{full}.{thirds}"
        for f in fields_p: p[f] = p.get(f,0) + stat.get(f,0)

# ─── FETCH ────────────────────────────────────────────────────────────────────
def get(url):
    print(f"  GET {url}")
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    if r.status_code == 404:
        print(f"  ⚠️  404 Not Found")
        return {}
    r.raise_for_status()
    return r.json()

def fetch_stats():
    cache = {}
    game_pks = []

    # ── Step 1: Discover valid sportIds from the API itself ──────────────────
    print("🔍 Step 1: Discovering valid sports from MLB API...")
    sports_url = f"{BASE}/sports"
    try:
        sports_data = get(sports_url)
        sports = sports_data.get("sports", [])
        print(f"  Found {len(sports)} sports:")
        wbc_sport_ids = []
        for s in sports:
            sid = s.get("id")
            name = s.get("name","")
            code = s.get("code","")
            print(f"    id={sid} code={code} name={name}")
            if any(kw in name.lower() for kw in ["world baseball", "wbc", "international", "classic"]):
                wbc_sport_ids.append(sid)
                print(f"      ↑ WBC candidate!")
        if not wbc_sport_ids:
            # Try all sport IDs 1-60 via schedule
            wbc_sport_ids = [23, 51, 22, 17, 16, 13, 6, 5, 4, 3, 2, 1]
    except Exception as e:
        print(f"  ❌ Could not fetch sports list: {e}")
        wbc_sport_ids = [23, 51, 22, 1]

    # ── Step 2: Find WBC games ───────────────────────────────────────────────
    print(f"\n🔍 Step 2: Searching for WBC games ({WBC_START} to {WBC_END})...")
    all_game_types = "B,S,E,A,D,F,G,I,L,P,R,S,W,C,N,Z"
    for sport_id in wbc_sport_ids:
        try:
            url = (f"{BASE}/schedule?sportId={sport_id}&season={SEASON}"
                   f"&startDate={WBC_START}&endDate={WBC_END}"
                   f"&gameType={all_game_types}")
            data = get(url)
            dates = data.get("dates", [])
            games = [g for d in dates for g in d.get("games", [])]
            if not games:
                print(f"  sportId={sport_id}: 0 games")
                continue
            # Show all games found
            print(f"  sportId={sport_id}: {len(games)} games found:")
            for g in games:
                status = g.get("status",{}).get("abstractGameState","?")
                date = g.get("officialDate","?")
                away = g.get("teams",{}).get("away",{}).get("team",{}).get("name","?")
                home = g.get("teams",{}).get("home",{}).get("team",{}).get("name","?")
                pk = g.get("gamePk")
                gtype = g.get("gameType","?")
                print(f"    pk={pk} type={gtype} {date}: {away} @ {home} [{status}]")
            finished = [g["gamePk"] for g in games
                        if g.get("status",{}).get("abstractGameState") in ("Final","Live")]
            if finished:
                print(f"  ✅ Using sportId={sport_id}: {len(finished)} completed games")
                game_pks = finished
                # Track games played per team name from schedule
                team_game_counts = {}
                for g in games:
                    if g.get("status",{}).get("abstractGameState") in ("Final","Live"):
                        for side in ["away","home"]:
                            tname = g.get("teams",{}).get(side,{}).get("team",{}).get("name","")
                            if tname:
                                team_game_counts[tname.lower()] = team_game_counts.get(tname.lower(),0) + 1
                break
        except Exception as e:
            print(f"  ❌ sportId={sport_id}: {e}")

    # ── Step 3: Fetch box scores ─────────────────────────────────────────────
    if not game_pks:
        print("\n⚠️  No completed games found via schedule. Check output above for clues.")
        print("   The WBC may not have started yet, or uses a different API structure.")
        return cache, 0, {}

    # Map team game counts to nation labels via NATION_ALIASES
    games_played_by_nation = {}
    for nation, aliases in NATION_ALIASES.items():
        for tname, count in team_game_counts.items():
            if any(alias in tname for alias in aliases):
                games_played_by_nation[nation] = max(games_played_by_nation.get(nation, 0), count)
    print(f"  📊 Games played by nation: {games_played_by_nation}")

    print(f"\n📊 Step 3: Fetching box scores for {len(game_pks)} completed games...")
    for i, pk in enumerate(game_pks):
        try:
            box_url = f"{BASE}/game/{pk}/boxscore"
            box = get(box_url)
            if not box:
                continue
            players_found = 0
            for side in ["away", "home"]:
                team = box.get("teams", {}).get(side, {})
                team_name = team.get("team", {}).get("name", "").lower()
                for pid_str, player in team.get("players", {}).items():
                    name = player.get("person", {}).get("fullName")
                    pid  = player.get("person", {}).get("id")
                    if not name: continue
                    bat = player.get("stats", {}).get("batting", {})
                    pit = player.get("stats", {}).get("pitching", {})
                    if bat and bat.get("atBats",0) + bat.get("baseOnBalls",0) + bat.get("hitByPitch",0) > 0:
                        merge(cache, name, pid, "hitting", bat)
                        players_found += 1
                    if pit and parse_ip(pit.get("inningsPitched","0")) > 0:
                        merge(cache, name, pid, "pitching", pit)
                        players_found += 1
                    # Store team name on cache entry for flag lookup
                    key = normalize(name)
                    if key in cache and team_name and "team_name" not in cache[key]:
                        cache[key]["team_name"] = team_name
            print(f"  Game {i+1}/{len(game_pks)} pk={pk}: {players_found} player-stats merged")
        except Exception as e:
            print(f"  ❌ Game pk={pk}: {e}")

    print(f"\n✅ Total unique players with stats: {len(cache)}")
    return cache, len(game_pks), games_played_by_nation

# ─── SCORE ────────────────────────────────────────────────────────────────────
def score_roster(owner, cache, ownership=None, nation_odds=None, games_played_by_nation=None):
    players = ROSTERS[owner]["players"]
    results = []
    total = 0
    for p in players:
        key = normalize(p["name"])
        entry = cache.get(key)
        is_p = p["pos"] == "P"
        h_pts = calc_hitting(entry["hitting"]) if entry and entry["hitting"] and not is_p else 0
        p_pts = calc_pitching(entry["pitching"]) if entry and entry["pitching"] else 0
        pts = h_pts + p_pts
        total += pts

        # Projection
        if nation_odds and games_played_by_nation is not None:
            proj, eliminated = compute_proj_pts(p, pts, games_played_by_nation, nation_odds)
        else:
            proj, eliminated = None, False

        h = entry["hitting"] if entry else None
        pit = entry["pitching"] if entry else None
        if h:
            singles = h.get('hits',0) - h.get('doubles',0) - h.get('triples',0) - h.get('homeRuns',0)
            tb = singles + 2*h.get('doubles',0) + 3*h.get('triples',0) + 4*h.get('homeRuns',0)
            stat_items = [
                (tb,                         "TB",  1),
                (h.get('rbi',0),             "RBI", 1),
                (h.get('runs',0),            "R",   1),
                (h.get('stolenBases',0),     "SB",  1),
                (h.get('baseOnBalls',0),     "BB",  1),
                (h.get('hitByPitch',0),      "HBP", 1),
                (h.get('strikeOuts',0),      "SO",  -1),
                (h.get('caughtStealing',0),  "CS",  -1),
            ]
        elif pit:
            stat_items = [
                (pit.get('inningsPitched','0'), "IP",  3),
                (pit.get('wins',0),             "W",   2),
                (pit.get('losses',0),           "L",   -2),
                (pit.get('strikeOuts',0),       "K",   1),
                (pit.get('earnedRuns',0),       "ER",  -2),
                (pit.get('hits',0),             "HA",  -1),
                (pit.get('baseOnBalls',0),      "BBA", -1),
                (pit.get('hitByPitch',0),       "HB",  -1),
                (pit.get('saves',0),            "SV",  4),
                (pit.get('holds',0),            "HLD", 2),
            ]
        else:
            stat_items = []

        results.append({
            "name": p["name"], "pos": p["pos"], "nation": p["nation"],
            "pts": round(pts), "h_pts": round(h_pts), "p_pts": round(p_pts),
            "stat_items": stat_items, "found": entry is not None,
            "ownership": ownership.get(normalize(p["name"]), (0, len(ROSTERS), [])) if ownership else (0, len(ROSTERS), []),
            "proj_pts": proj,
            "eliminated": eliminated,
        })
    return round(total), results

# ─── BUILD HTML ───────────────────────────────────────────────────────────────
FLAGS = {
    "Mexico":"🇲🇽","USA":"🇺🇸","DR":"🇩🇴","Netherlands":"🇳🇱","Canada":"🇨🇦",
    "PR":"🇵🇷","Korea":"🇰🇷","Japan":"🇯🇵","Venezuela":"🇻🇪","Italy":"🇮🇹",
    "GB":"🇬🇧","Colombia":"🇨🇴","Cuba":"🇨🇺","Panama":"🇵🇦","Australia":"🇦🇺","Taiwan":"🇹🇼"
}

def build_html(cache, games_processed, games_played_by_nation=None):
    from datetime import timezone, timedelta
    pst = timezone(timedelta(hours=-7))
    updated = datetime.now(pst).strftime("%B %d, %Y at %I:%M %p PDT")

    # Fetch odds/projections
    print("\n📡 Fetching WBC advancement odds...")
    nation_odds = fetch_nation_odds()
    games_played_by_nation = games_played_by_nation or {}

    # Build ranked teams
    ownership = compute_ownership(normalize)
    teams = []
    for owner, data in ROSTERS.items():
        score, players = score_roster(owner, cache, ownership, nation_odds, games_played_by_nation)
        teams.append({"owner": owner, "color": data["color"], "score": score, "players": players})
    teams.sort(key=lambda t: t["score"], reverse=True)

    # Build leaderboard cards HTML
    cards_html = ""
    for i, team in enumerate(teams):
        rank = i + 1
        rank_class = f"rank-{rank}" if rank <= 3 else "rank-other"
        color = team["color"]
        found_count = sum(1 for p in team["players"] if p["found"])
        hit_pts = sum(p["h_pts"] for p in team["players"])
        pit_pts = sum(p["p_pts"] for p in team["players"])
        active_count = sum(1 for p in team["players"] if not p["eliminated"])
        elim_count   = sum(1 for p in team["players"] if p["eliminated"])

        # Roster rows
        rows = ""
        for p in sorted(team["players"], key=lambda x: (-x["pts"], x["eliminated"])):
            flag = FLAGS.get(p["nation"], "🏳️")
            pts_class = "pts-pos" if p["pts"] > 0 else ("pts-neg" if p["pts"] < 0 else "pts-zero")
            pts_str = (f"+{int(p['pts'])}" if p["pts"] > 0 else str(int(p["pts"]))) if p["found"] else "—"
            elim_class = " player-elim" if p["eliminated"] else ""
            elim_badge = ' <span class="elim-badge">ELIM</span>' if p["eliminated"] else ""
            # Build stat pill badges — always show all, color-coded by whether they help or hurt
            if p["stat_items"]:
                pills = ""
                for val, label, direction in p["stat_items"]:
                    if direction > 0:
                        pill_cls = "sp-pos" if float(str(val).replace("0.","").replace(".0","") or 0) else "sp-zero"
                    else:
                        pill_cls = "sp-neg" if float(str(val).replace("0.","").replace(".0","") or 0) else "sp-zero"
                    pills += f'<span class="spill {pill_cls}">{val}&nbsp;<span class="slabel">{label}</span></span>'
                stat_html = f'<div class="spills">{pills}</div>'
            else:
                stat_html = '<span class="no-stats">no stats yet</span>'
            own_count, own_total, own_teams = p["ownership"]
            own_class = "own-pct high" if own_count == own_total else "own-pct"
            own_tooltip = ", ".join(own_teams) if own_teams else "None"

            rows += f"""
            <tr class="player-row{elim_class}">
              <td><span class="pos-badge">{p["pos"]}</span>{flag} {p["name"]}{elim_badge}</td>
              <td class="num"><span class="own-cell {own_class}" data-owners="{own_tooltip}">{own_count}/{own_total}<span class="own-tooltip">{own_tooltip}</span></span></td>
              <td>{stat_html}</td>
              <td class="num {pts_class}">{pts_str}</td>
            </tr>"""

        cards_html += f"""
        <div class="team-card {rank_class}" style="--team-color:{color}" data-owner="{team['owner']}">
          <div class="rank-num">{rank}</div>
          <div class="team-info">
            <div class="team-name" style="color:{color}">{team['owner']}</div>
            <div class="team-meta">{len(team['players'])} PLAYERS · {found_count} WITH STATS</div>
          </div>
          <div class="score-block">
            <div class="score-pts">{int(team['score'])}</div>
            <div class="score-label">PTS</div>
          </div>
          <div class="stat-pills">
            <div class="stat-pill pos">HIT <span>+{int(hit_pts)}</span></div>
            <div class="stat-pill pos">PITCH <span>+{int(pit_pts)}</span></div>
            <div class="stat-pill">FOUND <span>{found_count}/{len(team['players'])}</span></div>
            <div class="stat-pill active-pill">ACTIVE <span>{active_count}</span></div>
            {f'<div class="stat-pill elim-pill">ELIM <span>{elim_count}</span></div>' if elim_count > 0 else ''}
            <div style="flex:1"></div>
            <div class="stat-pill toggle-btn" onclick="toggleRoster(this)" style="border-color:{color};color:{color}">▼ ROSTER</div>
          </div>
          <div class="roster-detail">
            <table class="roster-table">
              <thead><tr>
                <th>Player</th><th class="num">Owned</th><th>Stats</th><th class="num">Pts</th>
              </tr></thead>
              <tbody>{rows}</tbody>
            </table>
          </div>
        </div>"""

    # Scoring rows for display
    scoring_html_hit = ""
    for label, pts in [("Total Bases (TB)",1),("RBI",1),("Runs Scored (R)",1),("Stolen Bases (SB)",1),
                        ("Walks (BB)",1),("Hit By Pitch (HBP)",1),("Strikeouts (SO)",-1),("Caught Stealing (CS)",-1)]:
        cls = "pos" if pts > 0 else "neg"
        sign = "+" if pts > 0 else ""
        scoring_html_hit += f'<div class="scoring-row"><span>{label}</span><span class="scoring-pts {cls}">{sign}{pts}</span></div>'

    scoring_html_pit = ""
    for label, pts in [("Innings Pitched (IP)",3),("Win (W)",2),("Loss (L)",-2),("Quality Start (QS)",3),
                        ("Strikeouts (K)",1),("Walks Allowed (BB)",-1),("Earned Runs (ER)",-2),
                        ("Hit Batsmen (HB)",-1),("Hits Allowed (H)",-1),("Holds (HLD)",2),("Saves (SV)",4)]:
        cls = "pos" if pts > 0 else "neg"
        sign = "+" if pts > 0 else ""
        scoring_html_pit += f'<div class="scoring-row"><span>{label}</span><span class="scoring-pts {cls}">{sign}{pts}</span></div>'

    # ── Build Top Players table ──────────────────────────────────────────────
    # Build a lookup of rostered players so we know pos for cache entries
    rostered_pos = {}
    for data in ROSTERS.values():
        for p in data["players"]:
            key = normalize(p["name"])
            if key not in rostered_pos:
                rostered_pos[key] = p["pos"]

    # Start from the full stats cache so unowned players are included
    all_players_map = {}
    for key, entry in cache.items():
        has_hit = entry.get("hitting") is not None
        has_pit = entry.get("pitching") is not None
        pos = rostered_pos.get(key, "P" if has_pit and not has_hit else "UTIL")
        is_p = pos == "P"

        h_pts = calc_hitting(entry["hitting"]) if has_hit and not is_p else 0
        p_pts = calc_pitching(entry["pitching"]) if has_pit else 0
        pts = h_pts + p_pts

        h = entry.get("hitting")
        pit = entry.get("pitching")
        if h and not is_p:
            singles = h.get('hits',0) - h.get('doubles',0) - h.get('triples',0) - h.get('homeRuns',0)
            tb = singles + 2*h.get('doubles',0) + 3*h.get('triples',0) + 4*h.get('homeRuns',0)
            stat_items = [
                (tb, "TB", 1), (h.get('rbi',0), "RBI", 1), (h.get('runs',0), "R", 1),
                (h.get('stolenBases',0), "SB", 1), (h.get('baseOnBalls',0), "BB", 1),
                (h.get('hitByPitch',0), "HBP", 1), (h.get('strikeOuts',0), "SO", -1),
                (h.get('caughtStealing',0), "CS", -1),
            ]
        elif pit:
            stat_items = [
                (pit.get('inningsPitched','0'), "IP", 3), (pit.get('wins',0), "W", 2),
                (pit.get('losses',0), "L", -2), (pit.get('strikeOuts',0), "K", 1),
                (pit.get('earnedRuns',0), "ER", -2), (pit.get('hits',0), "HA", -1),
                (pit.get('baseOnBalls',0), "BBA", -1), (pit.get('hitByPitch',0), "HB", -1),
                (pit.get('saves',0), "SV", 4), (pit.get('holds',0), "HLD", 2),
            ]
        else:
            stat_items = []

        own_data = ownership.get(key, (0, len(ROSTERS), []))
        # Resolve nation: prefer roster data, fall back to API team name
        nation = team_name_to_nation(entry.get("team_name", "")) or "—"
        is_elim = nation_odds.get(nation, {}).get("eliminated", False)
        all_players_map[key] = {
            "name": entry["fullName"], "pos": pos, "nation": nation,
            "pts": round(pts), "stat_items": stat_items,
            "found": True, "ownership": own_data, "eliminated": is_elim,
        }

    # Override nation with roster data where available (more precise labeling)
    for data in ROSTERS.values():
        for p in data["players"]:
            key = normalize(p["name"])
            if key in all_players_map:
                all_players_map[key]["nation"] = p["nation"]
                all_players_map[key]["eliminated"] = nation_odds.get(p["nation"], {}).get("eliminated", False)

    top_players = sorted(all_players_map.values(), key=lambda x: -x["pts"])

    top_rows = ""
    for rank, p in enumerate(top_players, 1):
        flag = FLAGS.get(p["nation"], "🏳️")
        pts_class = "pts-pos" if p["pts"] > 0 else ("pts-neg" if p["pts"] < 0 else "pts-zero")
        pts_str = f"+{int(p['pts'])}" if p["pts"] > 0 else str(int(p["pts"]))
        rank_cls = f"tp-rank-{rank}" if rank <= 3 else ""
        elim_class = " player-elim" if p.get("eliminated") else ""
        elim_badge = ' <span class="elim-badge">ELIM</span>' if p.get("eliminated") else ""

        if p["stat_items"]:
            pills = ""
            for val, label, direction in p["stat_items"]:
                if direction > 0:
                    pill_cls = "sp-pos" if float(str(val).replace("0.","").replace(".0","") or 0) else "sp-zero"
                else:
                    pill_cls = "sp-neg" if float(str(val).replace("0.","").replace(".0","") or 0) else "sp-zero"
                pills += f'<span class="spill {pill_cls}">{val}&nbsp;<span class="slabel">{label}</span></span>'
            stat_html = f'<div class="spills">{pills}</div>'
        else:
            stat_html = '<span class="no-stats">no stats yet</span>'

        own_count, own_total, own_teams = p["ownership"]
        own_class = "own-pct high" if own_count == own_total else "own-pct"
        own_tooltip = ", ".join(own_teams) if own_teams else "None"

        top_rows += f"""
        <tr class="{rank_cls}{elim_class}">
          <td class="num tp-rank">{rank}</td>
          <td><span class="pos-badge">{p["pos"]}</span>{flag} {p["name"]}{elim_badge}</td>
          <td class="num"><span class="own-cell {own_class}" data-owners="{own_tooltip}">{own_count}/{own_total}<span class="own-tooltip">{own_tooltip}</span></span></td>
          <td>{stat_html}</td>
          <td class="num {pts_class}">{pts_str}</td>
        </tr>"""

    top_players_html = f"""
    <table class="roster-table top-players-table">
      <thead><tr>
        <th class="num">#</th><th>Player</th><th class="num">Owned</th><th>Stats</th><th class="num">Pts</th>
      </tr></thead>
      <tbody>{top_rows}</tbody>
    </table>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="900">
<title>WBC Fantasy 2026 · Live Leaderboard</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg:#0a0c0f; --surface:#111418; --surface2:#181d23; --border:#252c35;
    --accent:#e8c84a; --accent2:#3ecf8e; --red:#f05252;
    --text:#e8edf2; --muted:#6b7585;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:var(--bg); color:var(--text); font-family:'DM Sans',sans-serif; min-height:100vh; overflow-x:hidden; }}
  body::before {{ content:''; position:fixed; inset:0; background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E"); pointer-events:none; z-index:999; opacity:0.35; }}
  header {{ padding:2rem 2rem 1rem; border-bottom:1px solid var(--border); display:flex; align-items:flex-end; justify-content:space-between; flex-wrap:wrap; gap:1rem; }}
  .logo-main {{ font-family:'Bebas Neue',sans-serif; font-size:3rem; letter-spacing:.04em; color:var(--accent); line-height:1; }}
  .logo-sub {{ font-family:'DM Mono',monospace; font-size:.7rem; color:var(--muted); letter-spacing:.15em; text-transform:uppercase; }}
  .updated {{ font-family:'DM Mono',monospace; font-size:.7rem; color:var(--muted); text-align:right; }}
  .updated strong {{ color:var(--accent2); display:block; font-size:.65rem; }}
  .tabs {{ display:flex; border-bottom:1px solid var(--border); padding:0 2rem; }}
  .tab {{ font-family:'DM Mono',monospace; font-size:.72rem; letter-spacing:.1em; text-transform:uppercase; padding:1rem 1.5rem; cursor:pointer; color:var(--muted); border:none; border-bottom:2px solid transparent; background:none; transition:all .2s; }}
  .tab:hover {{ color:var(--text); }}
  .tab.active {{ color:var(--accent); border-bottom-color:var(--accent); }}
  .tab-content {{ display:none; padding:2rem; }}
  .tab-content.active {{ display:block; }}
  .leaderboard {{ display:flex; flex-direction:column; gap:.75rem; }}
  .team-card {{ background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:1.2rem 1.5rem; display:grid; grid-template-columns:3rem 1fr auto; align-items:center; gap:1rem; cursor:pointer; transition:border-color .2s,background .2s; animation:fadeSlide .4s ease both; }}
  .team-card:hover {{ background:var(--surface2); }}
  .rank-1 {{ border-color:rgba(232,200,74,.4); }}
  .rank-2 {{ border-color:rgba(155,170,184,.3); }}
  .rank-3 {{ border-color:rgba(201,123,75,.3); }}
  @keyframes fadeSlide {{ from {{opacity:0;transform:translateY(12px)}} to {{opacity:1;transform:translateY(0)}} }}
  .rank-num {{ font-family:'Bebas Neue',sans-serif; font-size:2rem; color:var(--muted); text-align:center; }}
  .rank-1 .rank-num {{ color:#e8c84a; }}
  .rank-2 .rank-num {{ color:#9baab8; }}
  .rank-3 .rank-num {{ color:#c97b4b; }}
  .team-info {{ display:flex; flex-direction:column; gap:.2rem; }}
  .team-name {{ font-family:'Bebas Neue',sans-serif; font-size:1.5rem; letter-spacing:.05em; line-height:1; }}
  .team-meta {{ font-family:'DM Mono',monospace; font-size:.65rem; color:var(--muted); letter-spacing:.08em; }}
  .score-block {{ text-align:right; }}
  .score-pts {{ font-family:'Bebas Neue',sans-serif; font-size:2.2rem; line-height:1; color:var(--accent); }}
  .score-label {{ font-family:'DM Mono',monospace; font-size:.6rem; color:var(--muted); letter-spacing:.12em; }}
  .stat-pills {{ grid-column:1/-1; display:flex; gap:.5rem; flex-wrap:wrap; padding-top:.5rem; border-top:1px solid var(--border); margin-top:.3rem; }}
  .stat-pill {{ font-family:'DM Mono',monospace; font-size:.62rem; color:var(--muted); background:var(--surface2); border:1px solid var(--border); border-radius:4px; padding:.2rem .5rem; }}
  .stat-pill span {{ color:var(--text); }}
  .stat-pill.pos span {{ color:var(--accent2); }}
  .toggle-btn {{ cursor:pointer; }}
  .roster-detail {{ display:none; grid-column:1/-1; margin-top:.5rem; }}
  .roster-detail.open {{ display:block; }}
  .roster-table {{ width:100%; border-collapse:collapse; font-size:.78rem; }}
  .roster-table th {{ font-family:'DM Mono',monospace; font-size:.6rem; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); padding:.5rem .6rem; border-bottom:1px solid var(--border); text-align:left; }}
  .roster-table th.num {{ text-align:right; }}
  .roster-table td {{ padding:.45rem .6rem; border-bottom:1px solid rgba(37,44,53,.5); }}
  .roster-table td.num {{ text-align:right; font-family:'DM Mono',monospace; font-size:.72rem; }}
  .spills {{ display:flex; flex-wrap:wrap; gap:.25rem; }}
  .spill {{ font-family:'DM Mono',monospace; font-size:.62rem; padding:.15rem .4rem; border-radius:3px; border:1px solid var(--border); white-space:nowrap; }}
  .slabel {{ opacity:.6; font-size:.58rem; }}
  .sp-pos {{ color:var(--accent2); border-color:rgba(62,207,142,.25); background:rgba(62,207,142,.07); }}
  .sp-neg {{ color:var(--red); border-color:rgba(240,82,82,.25); background:rgba(240,82,82,.07); }}
  .sp-zero {{ color:var(--muted); border-color:var(--border); background:transparent; }}
  .no-stats {{ font-family:'DM Mono',monospace; font-size:.65rem; color:var(--muted); font-style:italic; }}
  .roster-table tr:last-child td {{ border-bottom:none; }}
  .pos-badge {{ font-family:'DM Mono',monospace; font-size:.58rem; background:var(--surface2); border:1px solid var(--border); border-radius:3px; padding:.1rem .35rem; color:var(--muted); margin-right:.4rem; }}
  .pts-pos {{ color:var(--accent2); }}
  .pts-neg {{ color:var(--red); }}
  .pts-zero {{ color:var(--muted); }}
  .player-elim {{ opacity:.5; }}
  .player-elim td {{ text-decoration:line-through; text-decoration-color:rgba(240,82,82,.4); }}
  .player-elim .pos-badge, .player-elim .spill {{ opacity:.6; }}
  .elim-badge {{ font-family:'DM Mono',monospace; font-size:.52rem; font-weight:600; letter-spacing:.06em; color:#f05252; background:rgba(240,82,82,.12); border:1px solid rgba(240,82,82,.3); border-radius:3px; padding:.1rem .3rem; margin-left:.35rem; vertical-align:middle; text-decoration:none; display:inline-block; }}
  .elim-pill {{ border-color:rgba(240,82,82,.3) !important; }}
  .elim-pill span {{ color:var(--red) !important; }}
  .active-pill span {{ color:var(--accent2) !important; }}
  .own-pct {{ color:var(--muted); font-family:'DM Mono',monospace; font-size:.68rem; }}
  .own-pct.high {{ color:var(--accent); font-weight:500; }}
  .own-cell {{ position:relative; cursor:pointer; font-family:'DM Mono',monospace; font-size:.68rem; display:inline-block; }}
  .own-tooltip {{ display:none; position:absolute; right:0; top:100%; margin-top:4px; background:#1e242c; border:1px solid var(--border); border-radius:6px; padding:.4rem .65rem; font-family:'DM Mono',monospace; font-size:.65rem; color:var(--text); white-space:nowrap; z-index:100; box-shadow:0 4px 16px rgba(0,0,0,.5); pointer-events:none; }}
  .own-tooltip::before {{ content:'Owned by'; display:block; font-size:.55rem; color:var(--muted); letter-spacing:.08em; text-transform:uppercase; margin-bottom:.3rem; }}
  .own-cell:hover .own-tooltip {{ display:block; }}
  .proj-pos {{ color:var(--accent2); font-family:'DM Mono',monospace; font-size:.68rem; }}
  .proj-neg {{ color:var(--red); font-family:'DM Mono',monospace; font-size:.68rem; }}
  .proj-na  {{ color:var(--muted); font-family:'DM Mono',monospace; font-size:.68rem; }}
  .proj-elim {{ font-family:'DM Mono',monospace; font-size:.58rem; font-weight:600; letter-spacing:.06em; color:#ff6b6b; background:rgba(240,82,82,.12); border:1px solid rgba(240,82,82,.3); border-radius:3px; padding:.1rem .35rem; }}
  .top-players-table {{ width:100%; border-collapse:collapse; font-size:.78rem; }}
  .top-players-table th {{ font-family:'DM Mono',monospace; font-size:.6rem; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); padding:.5rem .6rem; border-bottom:1px solid var(--border); text-align:left; position:sticky; top:0; background:var(--bg); z-index:10; }}
  .top-players-table th.num {{ text-align:right; }}
  .top-players-table td {{ padding:.5rem .6rem; border-bottom:1px solid rgba(37,44,53,.5); }}
  .top-players-table td.num {{ text-align:right; font-family:'DM Mono',monospace; font-size:.72rem; }}
  .top-players-table tr:last-child td {{ border-bottom:none; }}
  .tp-rank {{ font-family:'Bebas Neue',sans-serif; font-size:1.1rem; color:var(--muted); width:2rem; }}
  .tp-rank-1 .tp-rank {{ color:#e8c84a; }}
  .tp-rank-2 .tp-rank {{ color:#9baab8; }}
  .tp-rank-3 .tp-rank {{ color:#c97b4b; }}
  .tp-rank-1 td {{ background:rgba(232,200,74,.03); }}
  .tp-rank-2 td {{ background:rgba(155,170,184,.02); }}
  .tp-rank-3 td {{ background:rgba(201,123,75,.02); }}
  .info-note {{ background:rgba(232,200,74,.07); border:1px solid rgba(232,200,74,.2); border-radius:6px; padding:.8rem 1rem; font-family:'DM Mono',monospace; font-size:.68rem; color:rgba(232,200,74,.7); margin-bottom:1.5rem; }}
  .scoring-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; }}
  .scoring-section {{ background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:1.5rem; }}
  .scoring-section h3 {{ font-family:'Bebas Neue',sans-serif; font-size:1.3rem; letter-spacing:.05em; color:var(--accent); margin-bottom:1rem; }}
  .scoring-row {{ display:flex; justify-content:space-between; padding:.5rem 0; border-bottom:1px solid rgba(37,44,53,.5); font-size:.82rem; }}
  .scoring-row:last-child {{ border-bottom:none; }}
  .scoring-pts {{ font-family:'DM Mono',monospace; font-weight:500; }}
  .scoring-pts.pos {{ color:var(--accent2); }}
  .scoring-pts.neg {{ color:var(--red); }}
  .how-step {{ display:flex; gap:1rem; margin-bottom:1.5rem; align-items:flex-start; }}
  .step-num {{ font-family:'Bebas Neue',sans-serif; font-size:2rem; color:var(--accent); line-height:1; flex-shrink:0; width:2rem; }}
  .step-body h4 {{ font-size:.9rem; margin-bottom:.3rem; }}
  .step-body p {{ font-size:.8rem; color:var(--muted); line-height:1.6; }}
  .step-body code {{ background:var(--surface2); border:1px solid var(--border); padding:.15rem .4rem; border-radius:3px; font-family:'DM Mono',monospace; font-size:.7rem; color:var(--accent2); }}
  @media (max-width:600px) {{
    .team-card {{ grid-template-columns:2.5rem 1fr auto; padding:1rem; }}
    .logo-main {{ font-size:2rem; }}
    .tabs {{ padding:0 1rem; }}
    .tab {{ padding:.8rem .8rem; font-size:.65rem; }}
    .tab-content {{ padding:1rem; }}
    .scoring-grid {{ grid-template-columns:1fr; }}
  }}
</style>
</head>
<body>
<header>
  <div>
    <div class="logo-main">⚾ WBC FANTASY</div>
    <div class="logo-sub">2026 Live Leaderboard</div>
  </div>
  <div class="updated">
    <strong>STATIC SNAPSHOT</strong>
    {updated}<br>
    {games_processed} games processed · {len(cache)} players found
  </div>
</header>

<div class="tabs">
  <button class="tab active" onclick="switchTab('leaderboard',this)">Leaderboard</button>
  <button class="tab" onclick="switchTab('touplayers',this)">Top Players</button>
  <button class="tab" onclick="switchTab('scoring',this)">Scoring</button>
  <button class="tab" onclick="switchTab('howto',this)">Setup Guide</button>
</div>

<div id="leaderboard" class="tab-content active">
  <div class="info-note">
    ⚡ Snapshot generated {updated} from {games_processed} completed WBC games.
    Re-run <code>python3 fetch_wbc_stats.py</code> to refresh scores.
  </div>
  <div class="leaderboard">
    {cards_html}
  </div>
</div>

<div id="touplayers" class="tab-content">
  <div class="info-note">
    🏆 All rostered players ranked by fantasy points scored. Hover/tap Owned to see which teams drafted each player.
  </div>
  {top_players_html}
</div>

<div id="scoring" class="tab-content">
  <div class="scoring-grid">
    <div class="scoring-section"><h3>⚾ Hitting</h3>{scoring_html_hit}</div>
    <div class="scoring-section"><h3>🥎 Pitching</h3>{scoring_html_pit}</div>
  </div>
</div>

<div id="howto" class="tab-content">
  <div style="max-width:680px">
    <div class="how-step"><div class="step-num">1</div><div class="step-body">
      <h4>Install Python (if you don't have it)</h4>
      <p>Download from <code>python.org</code> — it's free. Then install requests once: <code>pip install requests</code></p>
    </div></div>
    <div class="how-step"><div class="step-num">2</div><div class="step-body">
      <h4>Run the fetcher script</h4>
      <p>In your terminal/command prompt, navigate to the folder with <code>fetch_wbc_stats.py</code> and run: <code>python3 fetch_wbc_stats.py</code> — it will create a fresh <code>wbc_dashboard.html</code> with current scores.</p>
    </div></div>
    <div class="how-step"><div class="step-num">3</div><div class="step-body">
      <h4>Share the HTML file</h4>
      <p>Send the generated <code>wbc_dashboard.html</code> via iMessage, email, or AirDrop to your group. Anyone can open it in a browser — no internet required to view it.</p>
    </div></div>
    <div class="how-step"><div class="step-num">4</div><div class="step-body">
      <h4>Automate it (optional)</h4>
      <p>On Mac/Linux, add a cron job to run every 30 minutes during games: open Terminal, type <code>crontab -e</code>, and add: <code>*/30 * * * * python3 /path/to/fetch_wbc_stats.py</code>. On Windows, use Task Scheduler.</p>
    </div></div>
    <div class="how-step"><div class="step-num">5</div><div class="step-body">
      <h4>Host it live (optional)</h4>
      <p>For a shared live URL, upload <code>wbc_dashboard.html</code> to GitHub Pages (free). Run the script locally, push the file to your repo, and GitHub Pages serves it. The URL stays the same each time you push an update.</p>
    </div></div>
  </div>
</div>

<script>
function switchTab(id, btn) {{
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
}}
function toggleRoster(btn) {{
  const card = btn.closest('.team-card');
  const detail = card.querySelector('.roster-detail');
  detail.classList.toggle('open');
  btn.textContent = detail.classList.contains('open') ? '▲ ROSTER' : '▼ ROSTER';
}}

document.addEventListener('click', function(e) {{
  const cell = e.target.closest('.own-cell');
  if (cell) {{
    e.stopPropagation();
    const tooltip = cell.querySelector('.own-tooltip');
    const isOpen = tooltip.style.display === 'block';
    document.querySelectorAll('.own-tooltip').forEach(t => t.style.display = 'none');
    tooltip.style.display = isOpen ? 'none' : 'block';
  }} else {{
    document.querySelectorAll('.own-tooltip').forEach(t => t.style.display = 'none');
  }}
}});
</script>
</body>
</html>"""

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  WBC Fantasy Stats Fetcher")
    print("=" * 50)

    try:
        cache, games_processed, games_played_by_nation = fetch_stats()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

    print("\n🏆 Scores preview:")
    teams = []
    for owner in ROSTERS:
        score, _ = score_roster(owner, cache)
        teams.append((owner, score))
    for owner, score in sorted(teams, key=lambda x: -x[1]):
        print(f"  {owner:12} {score:6} pts")

    html = build_html(cache, games_processed, games_played_by_nation)
    outfile = "wbc_dashboard.html"
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ Dashboard saved to: {outfile}")
    print("   Open it in your browser or share it with your group!")
    print("=" * 50)
