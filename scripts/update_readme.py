#!/usr/bin/env python3
"""
scripts/update_readme.py
Updates the daily art movement and recently pushed repositories in README.md.
Uses standard library only (urllib, json, datetime, re, os, sys, argparse).
Idempotent and safe: never logs or leaks tokens.
"""

import argparse
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request


def load_movements(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_todays_movement(movements):
    # Deterministic choice based on UTC day-of-year
    day_of_year = datetime.datetime.now(datetime.timezone.utc).timetuple().tm_yday
    index = (day_of_year - 1) % len(movements)
    return movements[index]


def format_movement_markdown(movement):
    return (
        f"**{movement['name']}** · *{movement['period']}*\n\n"
        f"{movement['description']}\n\n"
        f"*Key figure:* {movement['artist']}"
    )


def fetch_recent_repos(username, token=None, timeout=10):
    url = f"https://api.github.com/users/{username}/repos?sort=pushed&direction=desc&per_page=30"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Profile-Updater",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                filtered = []
                for repo in data:
                    if not isinstance(repo, dict):
                        continue
                    if repo.get("fork"):
                        continue
                    if repo.get("private"):
                        continue
                    filtered.append(repo)
                    if len(filtered) == 5:
                        break
                return filtered
            else:
                return None
    except Exception as e:
        # Graceful fallback: never expose or log the token
        sys.stderr.write(f"Warning: Could not fetch repositories from GitHub API ({e.__class__.__name__}).\n")
        return None


def format_repos_markdown(repos):
    if not repos:
        return "*Repositories will be listed here.*"

    lines = []
    for r in repos:
        name = r.get("name", "repository")
        url = r.get("html_url", "")
        desc = r.get("description") or ""
        desc = desc.strip()
        if desc:
            lines.append(f"- [{name}]({url}) — {desc}")
        else:
            lines.append(f"- [{name}]({url})")
    return "\n".join(lines)


def update_section(content, start_marker, end_marker, replacement):
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker),
        re.DOTALL,
    )
    match = pattern.search(content)
    if not match:
        raise ValueError(f"Marker range {start_marker} ... {end_marker} not found in content.")

    new_section = f"{start_marker}\n{replacement.strip()}\n{end_marker}"
    return pattern.sub(lambda _: new_section, content)


def extract_section(content, start_marker, end_marker):
    pattern = re.compile(
        re.escape(start_marker) + r"\n(.*?)\n" + re.escape(end_marker),
        re.DOTALL,
    )
    match = pattern.search(content)
    return match.group(1).strip() if match else None


def main():
    parser = argparse.ArgumentParser(description="Update daily movement and recent repos in README.md")
    parser.add_argument("--user", help="GitHub username (defaults to GITHUB_REPOSITORY_OWNER or melikee46)")
    args = parser.parse_args()

    username = args.user or os.environ.get("GITHUB_REPOSITORY_OWNER") or "melikee46"
    token = os.environ.get("GITHUB_TOKEN")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    movements_path = os.path.join(repo_root, "data", "movements.json")
    readme_path = os.path.join(repo_root, "README.md")

    if not os.path.exists(movements_path):
        sys.stderr.write(f"Error: {movements_path} not found.\n")
        sys.exit(1)

    if not os.path.exists(readme_path):
        sys.stderr.write(f"Error: {readme_path} not found.\n")
        sys.exit(1)

    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()

    # 1. Update Movement
    movements = load_movements(movements_path)
    todays_movement = get_todays_movement(movements)
    movement_md = format_movement_markdown(todays_movement)
    readme_content = update_section(
        readme_content,
        "<!--MOVEMENT:START-->",
        "<!--MOVEMENT:END-->",
        movement_md,
    )

    # 2. Update Repositories
    repos = fetch_recent_repos(username, token=token)
    if repos is not None:
        repos_md = format_repos_markdown(repos)
        readme_content = update_section(
            readme_content,
            "<!--REPOS:START-->",
            "<!--REPOS:END-->",
            repos_md,
        )
    else:
        # Graceful fallback: preserve existing content between markers if present
        existing_repos = extract_section(readme_content, "<!--REPOS:START-->", "<!--REPOS:END-->")
        if not existing_repos:
            repos_md = format_repos_markdown([])
            readme_content = update_section(
                readme_content,
                "<!--REPOS:START-->",
                "<!--REPOS:END-->",
                repos_md,
            )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"Updated README.md: movement set to '{todays_movement['name']}'.")


if __name__ == "__main__":
    main()
