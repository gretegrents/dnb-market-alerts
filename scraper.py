import requests
from bs4 import BeautifulSoup
from datetime import datetime

url = "https://www.dnb.no/dnbnyheter/no/bors-og-marked"
# Upgraded headers to look like a standard desktop Google Chrome browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "no-NO,no;q=0.9,en-US;q=0.8,en;q=0.7"
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    status = response.status_code
except Exception as e:
    status = f"Forbindelsesfeil: {str(e)}"
    response = None

articles_html = ""

# Scenario 1: Successfully reached DNB
if response and response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    
    seen_links = set()
    count = 0
    
    for link in links:
        href = link['href']
        if '/bors-og-marked/' in href and href not in seen_links:
            title = link.get_text(strip=True)
            
            if len(title) > 20 and not title.startswith("Vis og DNB"): 
                seen_links.add(href)
                full_url = href if href.startswith('http') else f"https://www.dnb.no{href}"
                
                articles_html += f"""
                <div class="card">
                    <h3>{title}</h3>
                    <a href="{full_url}" target="_blank" class="btn">Les artikkelen →</a>
                </div>
                """
                count += 1
        if count >= 5:
            break
            
    if count == 0:
        articles_html = "<div class='card'><h3>Fant ingen artikler. DNB kan ha endret designet på nettsiden sin.</h3></div>"

# Scenario 2: Blocked or encountered an issue (Ensures index.html is still built)
else:
    articles_html = f"""
    <div class="card" style="border-left: 4px solid #ff4b4b;">
        <h3 style="color: #d93838;">⚠️ Kunne ikke hente markedsdata</h3>
        <p>Statuskode fra DNB: <strong>{status}</strong></p>
        <p>Dette skjer vanligvis fordi DNBs sikkerhetssystemer (brannmur) blokkerer forespørsler som kommer fra offentlige skyservere som GitHub Actions.</p>
    </div>
    """

# Complete HTML styling template
html_content = f"""
<!DOCTYPE html>
<html lang="no">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DNB Market Insights</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f4f7f6; color: #1c2826; margin: 0; padding: 40px 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        h1 {{ color: #002e3b; text-align: center; margin-bottom: 5px; font-size: 2rem; }}
        .date {{ text-align: center; color: #6b7c7c; margin-bottom: 30px; font-size: 0.9rem; }}
        .card {{ background: #ffffff; padding: 24px; margin-bottom: 16px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.03); border: 1px solid #e1e8e8; }}
        h3 {{ margin: 0 0 12px 0; color: #004d5a; font-size: 1.2rem; line-height: 1.4; }}
        .btn {{ display: inline-block; text-decoration: none; color: #00c0a8; font-weight: 600; font-size: 0.95rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 DNB Market Insights</h1>
        <div class="date">Sist oppdatert: {datetime.now().strftime('%d.%m.%Y %H:%M')} UTC</div>
        {articles_html}
    </div>
</body>
</html>
"""

# Save the file (guaranteed execution)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("index.html successfully written.")
