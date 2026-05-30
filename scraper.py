import requests
from bs4 import BeautifulSoup
from datetime import datetime

# DNB News Market URL
url = "https://www.dnb.no/dnbnyheter/no/bors-og-marked"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    
    seen_links = set()
    markdown_output = f"## 📈 DNB Market Insights — {datetime.now().strftime('%d.%m.%Y')}\n\n"
    
    count = 0
    for link in links:
        href = link['href']
        # Isolate articles specifically inside the stock market segment
        if '/bors-og-marked/' in href and href not in seen_links:
            title = link.get_text(strip=True)
            
            # Filter out empty layouts, cookie links, or short buttons
            if len(title) > 20 and not title.startswith("Vis og DNB"): 
                seen_links.add(href)
                full_url = href if href.startswith('http') else f"https://www.dnb.no{href}"
                markdown_output += f"* **{title}**\n  👉 [Les artikkelen here]({full_url})\n\n"
                count += 1
        if count >= 5: # Limit to the 5 top latest entries
            break
            
    # Write to a file that our automated workflow can read
    with open("alert_body.md", "w", encoding="utf-8") as f:
        f.write(markdown_output)
else:
    with open("alert_body.md", "w", encoding="utf-8") as f:
        f.write("⚠️ Failed to scrape DNB Nyheter today. Website layout might have changed.")
