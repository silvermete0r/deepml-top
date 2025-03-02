import time
import csv
import requests
from bs4 import BeautifulSoup

# GitHub File Paths
README_FILE = "README.md"
LEADERBOARD_FILE = "leaderboard.csv"

# Shields.io Badge Template
BADGE_TEMPLATE = "![{user}](https://img.shields.io/badge/{rank}-{user}-orange?style=flat&logo=fire)"

# Function to scrape leaderboard
def fetch_leaderboard():
    url = 'https://www.deep-ml.com/leaderboard'
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to fetch leaderboard")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    leaderboard_container = soup.find('div', class_='space-y-3')

    if not leaderboard_container:
        print("Leaderboard not found!")
        return None

    leaderboard_items = leaderboard_container.find_all(
        'div', class_='animate-in fade-in slide-in-from-bottom-3 duration-500 ease-out')

    leaderboard = []
    
    for item in leaderboard_items:
        rank_span = item.find('span', class_='text-2xl font-bold transition-transform duration-200 inline-block group-active:scale-95')
        username_span = item.find('span', class_='font-semibold')
        score_span = item.find('span', class_='font-mono font-semibold')

        if rank_span and username_span and score_span:
            rank = rank_span.text.strip()
            username = username_span.text.strip()
            score = score_span.text.strip()
            leaderboard.append((rank, username, score))

    return leaderboard

# Function to update README
def update_readme(leaderboard):
    with open(README_FILE, "r", encoding="utf-8") as f:
        readme_lines = f.readlines()

    # Find start and end markers for leaderboard
    start_marker = "<!-- LEADERBOARD_START -->\n"
    end_marker = "<!-- LEADERBOARD_END -->\n"

    try:
        start_idx = readme_lines.index(start_marker) + 1
        end_idx = readme_lines.index(end_marker)
    except ValueError:
        print("Leaderboard markers not found in README.md")
        return

    # Generate new leaderboard table
    leaderboard_md = "| Rank | Username | Score |\n|------|---------|-------|\n"
    badges_md = []

    for rank, username, score in leaderboard:
        leaderboard_md += f"| {rank} | {username} | {score} |\n"
        if int(rank) <= 3:  # Add badges for top 3 users
            badges_md.append(BADGE_TEMPLATE.format(rank=rank, user=username))

    # Update README content
    updated_readme = readme_lines[:start_idx] + [leaderboard_md] + readme_lines[end_idx:]

    # Add badges at the bottom
    updated_readme.append("\n## 🏆 Top Performers\n")
    updated_readme.extend([badge + "\n" for badge in badges_md])

    # Write back to README.md
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.writelines(updated_readme)

# Function to update leaderboard.csv
def save_csv(leaderboard):
    with open(LEADERBOARD_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Rank", "Username", "Score"])
        writer.writerows(leaderboard)

# Run script
if __name__ == "__main__":
    leaderboard_data = fetch_leaderboard()

    if leaderboard_data:
        save_csv(leaderboard_data)
        update_readme(leaderboard_data)
        print("Leaderboard updated successfully!")
    else:
        print("No data to update.")
