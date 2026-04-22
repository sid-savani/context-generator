import requests
from bs4 import BeautifulSoup

def fetch_website_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print("Error fetching website:", e)
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # TITLE
    title = soup.title.string.strip() if soup.title else "No title"

    # HEADINGS (structure of page)
    headings = []
    for tag in ["h1", "h2", "h3"]:
        for h in soup.find_all(tag):
            text = h.get_text(strip=True)
            if text:
                headings.append(text)

    # PARAGRAPHS (descriptions)
    paragraphs = []
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if text:
            paragraphs.append(text)

    # BUTTONS
    buttons = []
    for btn in soup.find_all("button"):
        text = btn.get_text(strip=True)
        if text:
            buttons.append(text)

    # LINKS (navigation items)
    links = []
    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        if text and len(text) < 40:  # avoid long junk text
            links.append(text)

    # CLEAN OUTPUT (limit size)
    data = {
        "title": title,
        "headings": headings[:15],
        "paragraphs": paragraphs[:15],
        "buttons": buttons[:10],
        "links": links[:15]
    }

    return data


# 🔥 TEST WITH APPLE WEBSITE
url = "https://www.apple.com"

data = fetch_website_data(url)

print("\n===== EXTRACTED DATA =====\n")

if data:
    for key, values in data.items():
        print(f"{key.upper()}:")
        if isinstance(values, list):
            for v in values:
                print("-", v)
        else:
            print("-", values)
        print()