import time
import csv
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import urllib.parse

# GitHub File Paths
README_FILE = "README.MD"
LEADERBOARD_FILE = "leaderboard.csv"
BADGES_JSON = "badges.json"

# URL encode username for badge template
def encode_username(username):
    return urllib.parse.quote(username)

# Shields.io Badge Template
BADGE_TEMPLATE = '![DeepML {display_username}](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fsilvermete0r%2Fdeepml-top%2Fmain%2Fbadges.json&query=%24.{encoded_key}.rank&prefix=Rank%20&style=for-the-badge&label=%F0%9F%9A%80%20DeepML&color=blue&link=https%3A%2F%2Fwww.deep-ml.com%2Fleaderboard)'

# Initialize Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode
driver = webdriver.Chrome(options=options)

# Function to scrape leaderboard
def fetch_leaderboard():
    url = 'https://www.deep-ml.com/leaderboard'
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "space-y-3"))
        )
    except:
        print("Leaderboard did not load in time.")
        driver.quit()
        exit()

    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    driver.quit()

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
    try:
        with open(README_FILE, "r", encoding="utf-8") as f:
            readme_content = f.read()
    except FileNotFoundError:
        print(f"README file not found at {README_FILE}")
        return
    
    top_badges = []

    # Generate top badges
    for rank, username, score in leaderboard:
        if int(rank) <= 3:
            # Create a safe key for the JSON lookup
            encoded_key = encode_username(username)
            # Use the badge template with both original username for display and encoded username for query
            top_badges.append(BADGE_TEMPLATE.format(
                display_username=username,
                encoded_key=encoded_key
            ))
    
    # Add top 3 users as badges
    badges_section = "\n".join(top_badges)
    
    # Update badges section
    badge_start_marker = "<!-- BADGES_START -->"
    badge_end_marker = "<!-- BADGES_END -->"
    badge_pattern = f"{badge_start_marker}(.*?){badge_end_marker}"
    
    if badge_start_marker in readme_content and badge_end_marker in readme_content:
        readme_content = re.sub(
            badge_pattern,
            f"{badge_start_marker}\n{badges_section}\n{badge_end_marker}",
            readme_content, 
            flags=re.DOTALL
        )
    else:
        print("Badge markers not found in README.md")

    # Find start and end markers for leaderboard
    leaderboard_start_marker = "<!-- LEADERBOARD_START -->"
    leaderboard_end_marker = "<!-- LEADERBOARD_END -->"
    leaderboard_pattern = f"{leaderboard_start_marker}(.*?){leaderboard_end_marker}"
    
    # Generate new leaderboard table
    leaderboard_md = "\n| Rank | Username | Score |\n|------|---------|-------|\n"
    
    for rank, username, score in leaderboard:
        leaderboard_md += f"| {rank} | {username} | {score} |\n"
    
    # Update the leaderboard content
    if leaderboard_start_marker in readme_content and leaderboard_end_marker in readme_content:
        readme_content = re.sub(
            leaderboard_pattern,
            f"{leaderboard_start_marker}{leaderboard_md}{leaderboard_end_marker}",
            readme_content,
            flags=re.DOTALL
        )
    else:
        print("Leaderboard markers not found in README.md")

    # Write back to README.md
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(readme_content)

# Function to update badges.json
def save_json(leaderboard):
    badges = {}

    for rank, username, score in leaderboard:
        # Use URL-encoded username as the key to ensure it works with the badge query
        encoded_username = encode_username(username)
        badges[encoded_username] = {
            "label": f"No. {rank} | {username}",
            "rank": rank,
            "score": score,
            "username": username
        }

    with open(BADGES_JSON, "w", encoding="utf-8") as f:
        json.dump(badges, f, indent=4)

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
        save_json(leaderboard_data)
        update_readme(leaderboard_data)
        print("Leaderboard updated successfully!")
    else:
        print("No data to update.")