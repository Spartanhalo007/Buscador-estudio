import os
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Read the API key from the environment (.env file)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def search_books(query, max_results=5):
    """
    Call Google Books API to search books by topic.
    Returns a list of dictionaries with simplified book data.
    """
    if not query or not GOOGLE_API_KEY:
        return []

    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "maxResults": max_results,
        "key": GOOGLE_API_KEY,
        "country": "CO"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        print("DEBUG Books status:", response.status_code)
        response.raise_for_status()
        data = response.json()

        items = data.get("items", [])
        books = []

        for item in items:
            info = item.get("volumeInfo", {})
            books.append(
                {
                    "title": info.get("title", "Untitled"),
                    "authors": ", ".join(info.get("authors", [])),
                    "description": (info.get("description", "")[:250] + "...")
                    if info.get("description")
                    else "",
                    "link": info.get("infoLink", "#"),
                    "thumbnail": info.get("imageLinks", {}).get("thumbnail"),
                }
            )

        return books
    except Exception:
        return []


def search_videos(query, max_results=5):
    """
    Call YouTube Data API v3 to search videos by topic.
    Returns a list of dictionaries with simplified video data.
    """
    if not query or not GOOGLE_API_KEY:
        return []

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "type": "video",
        "q": query,
        "maxResults": max_results,
        "key": GOOGLE_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        print("DEBUG YouTube status:", response.status_code)
        response.raise_for_status()
        data = response.json()

        items = data.get("items", [])
        videos = []

        for item in items:
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")

            if not video_id:
                continue

            videos.append(
                {
                    "title": snippet.get("title", "Untitled"),
                    "channel": snippet.get("channelTitle", ""),
                    "description": (snippet.get("description", "")[:200] + "...")
                    if snippet.get("description")
                    else "",
                    "video_url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": snippet.get("thumbnails", {})
                    .get("medium", {})
                    .get("url"),
                }
            )

        return videos
    except Exception:
        return []


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main route for the study resources search page.

    GET: show the form.
    POST: process the topic and show books + videos + map.
    """
    query = ""
    books = []
    videos = []
    error = None

    if request.method == "POST":
        query = request.form.get("query", "").strip()

        if not query:
            error = "Please enter a topic to search."
        else:
            books = search_books(query)
            videos = search_videos(query)

            if not books and not videos:
                error = "No results found or there was a problem with the APIs."

    return render_template(
        "index.html",
        query=query,
        books=books,
        videos=videos,
        error=error,
        google_maps_api_key=GOOGLE_API_KEY,
    )


if __name__ == "__main__":
    app.run(debug=True)