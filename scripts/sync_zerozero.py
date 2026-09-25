#!/usr/bin/env python3
"""Best-effort Zerozero sync for ADC Figueiras.

The script only uses normal HTTP requests and HTML parsing. It does not attempt
captcha solving, authentication bypasses, or other access-control workarounds.
If the source blocks automated access, the workflow exits without replacing the
last known-good data file.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "sync-config.json"
OUT_PATH = ROOT / "data" / "competition.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36",
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("\xa0", " ")).strip()


def to_int(value: str):
    value = clean(value)
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return None


def fetch(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=25)
    response.raise_for_status()
    if len(response.text) < 500:
        raise RuntimeError("Resposta demasiado curta para conter os dados esperados.")
    return response.text


def find_numeric_run(values: list[str], needed: int = 8):
    nums = [to_int(v) for v in values]
    for start in range(len(nums)):
        run = []
        i = start
        while i < len(nums) and nums[i] is not None:
            run.append(nums[i])
            i += 1
        if len(run) >= needed:
            return start, run
    return None, []


def parse_standings(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    candidates = []
    for table in soup.find_all("table"):
        text = clean(table.get_text(" ", strip=True)).upper()
        score = sum(token in text for token in (" GM ", " GS ", " DG ", " J ", " V ", " E ", " D "))
        if score >= 5:
            candidates.append(table)

    best = []
    for table in candidates:
        rows = []
        for tr in table.find_all("tr"):
            cells = [clean(td.get_text(" ", strip=True)) for td in tr.find_all(["td", "th"])]
            if not cells or any(x.upper() == "EQUIPA" for x in cells):
                continue
            start, nums = find_numeric_run(cells, 8)
            if start is None:
                continue
            # Stats are expected as P, J, V, E, D, GM, GS, DG.
            stats = nums[:8]
            team = ""
            for v in reversed(cells[:start]):
                if v and to_int(v) is None and v.lower() not in {"a", "equipa"}:
                    team = v
                    break
            if not team:
                continue
            rows.append({
                "position": len(rows) + 1,
                "team": team,
                "pts": stats[0], "j": stats[1], "v": stats[2], "e": stats[3],
                "d": stats[4], "gf": stats[5], "ga": stats[6], "dg": stats[7],
            })
        if len(rows) > len(best):
            best = rows

    # Sanity checks: this competition currently has 13 teams; allow future format changes.
    if len(best) < 5:
        raise RuntimeError("Não foi possível identificar a tabela classificativa no HTML.")
    return best


def infer_year(date_text: str, season: str) -> str | None:
    m = re.fullmatch(r"(\d{1,2})[-/](\d{1,2})(?:[-/](\d{2,4}))?", date_text)
    if not m:
        return None
    day, month, year = int(m.group(1)), int(m.group(2)), m.group(3)
    if year:
        y = int(year)
        if y < 100:
            y += 2000
    else:
        years = re.findall(r"\d{2,4}", season)
        first = int(years[0]); second = int(years[1]) if len(years) > 1 else first + 1
        if first < 100: first += 2000
        if second < 100: second += 2000
        y = first if month >= 7 else second
    try:
        return f"{y:04d}-{month:02d}-{day:02d}"
    except ValueError:
        return None


def unique_texts(items: Iterable[str]) -> list[str]:
    out = []
    for item in items:
        item = clean(item)
        if item and item not in out:
            out.append(item)
    return out


def parse_team_games(html: str, club_name: str, season: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    games = []
    for tr in soup.find_all("tr"):
        row_text = clean(tr.get_text(" ", strip=True))
        if club_name.lower() not in row_text.lower():
            continue
        date_match = re.search(r"\b(\d{4}-\d{2}-\d{2}|\d{1,2}[-/]\d{1,2}(?:[-/]\d{2,4})?)\b", row_text)
        if not date_match:
            continue
        raw_date = date_match.group(1)
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date):
            date_iso = raw_date
        else:
            date_iso = infer_year(raw_date, season)
        if not date_iso:
            continue
        time_match = re.search(r"\b([01]?\d|2[0-3]):[0-5]\d\b", row_text)
        time = time_match.group(0) if time_match else ""

        # Team names are usually anchor labels. Remove navigation helpers and duplicates.
        anchors = unique_texts(a.get_text(" ", strip=True) for a in tr.find_all("a"))
        anchors = [a for a in anchors if a.lower() not in {"h2h", "dist", "tdis"}]
        team_anchors = [a for a in anchors if not any(k in a.lower() for k in ("af porto", "futsal", "taça", "supertaça", "liga "))]
        club_index = next((i for i, a in enumerate(team_anchors) if club_name.lower() in a.lower()), None)
        opponent = ""
        home = away = ""
        if club_index is not None:
            others = [a for a in team_anchors if club_name.lower() not in a.lower() and len(a) > 2]
            if others:
                opponent = min(others, key=lambda a: abs(team_anchors.index(a)-club_index))
            home_away = re.search(r"\((C|F)\)", row_text, re.I)
            if home_away:
                if home_away.group(1).upper() == "C": home, away = club_name, opponent
                else: home, away = opponent, club_name
            elif opponent:
                opp_index = team_anchors.index(opponent)
                if club_index < opp_index: home, away = club_name, opponent
                else: home, away = opponent, club_name
        if not opponent or not home or not away:
            continue

        score_text = row_text.replace(raw_date, " ")
        if time:
            score_text = score_text.replace(time, " ")
        score_match = re.search(r"(?<!\d)(\d{1,2})\s*[-–]\s*(\d{1,2})(?!\d)", score_text)
        home_score = away_score = None
        if score_match:
            home_score, away_score = int(score_match.group(1)), int(score_match.group(2))

        round_match = re.search(r"\bJ(?:ornada)?\s*(\d+)\b", row_text, re.I)
        round_label = f"J{round_match.group(1)}" if round_match else ""
        key = f"zz|{date_iso}|{home}|{away}"
        games.append({
            "external_id": key,
            "round": round_label,
            "date": date_iso,
            "time": time,
            "home": home,
            "away": away,
            "home_score": home_score,
            "away_score": away_score,
        })

    # Remove duplicates while keeping chronological order.
    dedup = {}
    for g in games:
        dedup[g["external_id"]] = g
    return sorted(dedup.values(), key=lambda g: (g["date"], g["time"]))


def main() -> int:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    old = {}
    if OUT_PATH.exists():
        try: old = json.loads(OUT_PATH.read_text(encoding="utf-8"))
        except Exception: old = {}

    try:
        competition_html = fetch(config["competition_url"])
        standings = parse_standings(competition_html)
    except Exception as exc:
        print(f"ERROR standings: {exc}", file=sys.stderr)
        return 2

    games = old.get("games", [])
    try:
        team_html = fetch(config["team_url"])
        parsed_games = parse_team_games(team_html, config["club_name"], config["season"])
        if parsed_games:
            games = parsed_games
        else:
            print("WARNING: calendário não identificado; mantém-se o último calendário conhecido.", file=sys.stderr)
    except Exception as exc:
        print(f"WARNING games: {exc}; mantém-se o último calendário conhecido.", file=sys.stderr)

    payload = {
        "competition": config["competition"],
        "season": config["season"],
        "source_url": config["competition_url"],
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "standings": standings,
        "games": games,
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {len(standings)} equipas, {len(games)} jogos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
