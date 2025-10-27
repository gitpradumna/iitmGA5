from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Enable CORS for all origins and GET method
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/api/outline", response_class=PlainTextResponse)
def get_country_outline(country: str = Query(..., description="Name of the country")):
    country = country.strip()
    if not country:
        raise HTTPException(status_code=400, detail="Country name cannot be empty")

    # Format Wikipedia URL
    country_title = country.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{country_title}"

    # Fetch Wikipedia page with User-Agent
    headers = {"User-Agent": "Mozilla/5.0 (compatible; OutlineBot/1.0)"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Wikipedia page not found")

    # Parse HTML and extract headings
    soup = BeautifulSoup(response.text, "html.parser")
    content = soup.find("div", {"id": "bodyContent"})
    if not content:
        raise HTTPException(status_code=500, detail="Failed to parse Wikipedia content")

    headings = content.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    if not headings:
        raise HTTPException(status_code=404, detail="No headings found on the page")

    # # Generate Markdown outline (shift all levels up by 1)
    # markdown_lines = [f"## {country}", "### Contents"]
    markdown_lines = [f"## Contents", f"### {country}"]
    skip_titles = {"contents", "see also", "references", "external links"}

    for tag in headings:
        title = tag.get_text(strip=True)
        if not title or title.lower() in skip_titles:
            continue
        level = int(tag.name[1]) + 1  # Shift heading level up by 1
        markdown_lines.append(f"{'#' * level} {title}")

    return "\n\n".join(markdown_lines)



