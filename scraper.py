# scraper.py
from playwright.sync_api import sync_playwright, TimeoutError
import os, json
from datetime import datetime

output_file = "output.json"

def scrape_entertainment(page):
    """Scrape top 5 entertainment news articles"""
    page.goto("https://ekantipur.com/entertainment")
    page.wait_for_load_state("networkidle")

    titles = page.query_selector_all("h2")[:5]  # top 5 headlines
    images = page.query_selector_all("img")[:5]  # top 5 images (rough match)

    news_list = []
    for i in range(len(titles)):
        title_el = titles[i]
        img_el = images[i] if i < len(images) else None

        title = title_el.text_content().strip() if title_el else None
        image_url = img_el.get_attribute("src") if img_el else None

        news_list.append({
            "title": title,
            "image_url": image_url,
            "category": "मनोरञ्जन",
            "author": None,
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return news_list

def scrape_cartoon(page):
    """Scrape cartoon of the day"""
    page.goto("https://ekantipur.com/")
    page.wait_for_load_state("networkidle")

    cartoon_el = page.query_selector("div.cartoon img")
    if cartoon_el:
        return {
            "title": "Cartoon of the Day",
            "image_url": cartoon_el.get_attribute("src"),
            "author": None,
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    return {"title": None, "image_url": None, "author": None, "scraped_at": None}

def main():
    # Step 1: Read existing data
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    else:
        existing_data = {"entertainment_news": [], "cartoon_of_the_day": {}}

    # Step 2: Scrape new data
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        new_entertainment = scrape_entertainment(page)
        new_cartoon = scrape_cartoon(page)

        browser.close()

    # Step 3: Append new entertainment data
    existing_data["entertainment_news"].extend(new_entertainment)

    # Remove duplicate headlines in entertainment
    unique_articles = {article["title"]: article for article in existing_data["entertainment_news"]}
    existing_data["entertainment_news"] = list(unique_articles.values())

    # Step 4: Replace cartoon (latest only)
    existing_data["cartoon_of_the_day"] = new_cartoon

    # Step 5: Save updated data
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    print("✅ Scraping complete. Data saved to output.json")

if __name__ == "__main__":
    main()