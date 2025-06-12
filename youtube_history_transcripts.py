import datetime
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

# Scopes for YouTube Data API read access
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# This script fetches your watch history from yesterday
# and saves transcripts of each video in a text file

def get_authenticated_service(client_secrets_file: str):
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
    credentials = flow.run_console()
    return build("youtube", "v3", credentials=credentials)

def get_watch_history_items(youtube):
    # The watch history playlist ID is "HL"
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId="HL",
        maxResults=50,
    )
    while request is not None:
        response = request.execute()
        for item in response.get("items", []):
            yield item
        request = youtube.playlistItems().list_next(request, response)

def filter_items_from_yesterday(items):
    yesterday = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)
    for item in items:
        snippet = item.get("snippet", {})
        published_at = snippet.get("publishedAt")
        if not published_at:
            continue
        date = datetime.datetime.fromisoformat(published_at.replace("Z", "+00:00")).date()
        if date == yesterday:
            yield snippet.get("resourceId", {}).get("videoId")

def save_transcripts(video_ids, output_path: Path):
    with output_path.open("w", encoding="utf-8") as f:
        for vid in video_ids:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(vid)
                f.write(f"--- Transcript for {vid} ---\n")
                for line in transcript:
                    f.write(line.get("text", "") + "\n")
                f.write("\n")
            except Exception as e:
                f.write(f"Could not fetch transcript for {vid}: {e}\n\n")

def main():
    # Path to OAuth client secrets JSON downloaded from Google Cloud Console
    client_secrets_file = "client_secret.json"
    youtube = get_authenticated_service(client_secrets_file)
    items = get_watch_history_items(youtube)
    video_ids = list(filter_items_from_yesterday(items))
    output_path = Path("transcripts_yesterday.txt")
    save_transcripts(video_ids, output_path)
    print(f"Saved {len(video_ids)} transcripts to {output_path}")

if __name__ == "__main__":
    main()
