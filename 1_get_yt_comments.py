import os
import json
import csv
from typing import List, Dict
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

def load_api_key() -> str:
    """Load YouTube API key from environment variables."""
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        raise ValueError("YouTube API key not found in environment variables")
    return api_key

def create_youtube_client(api_key: str):
    """Create YouTube API client."""
    return build('youtube', 'v3', developerKey=api_key)

def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    import re
    
    # Patterns for YouTube URLs
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # Standard and mobile URLs
        r'youtu.be\/([0-9A-Za-z_-]{11})',    # Short URLs
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError(f"Could not extract video ID from URL: {url}")

def get_video_comments(video_id: str, max_results: int = 200) -> List[Dict]:
    """
    Retrieve comments from a YouTube video.
    
    Args:
        video_id (str): The ID of the YouTube video
        max_results (int): Maximum number of comments to retrieve (default: 200)
    
    Returns:
        List[Dict]: List of comments with author and text information
    """
    try:
        # Initialize the YouTube client
        youtube = create_youtube_client(load_api_key())
        
        comments = []
        next_page_token = None
        
        while len(comments) < max_results:
            # Make API request to get comments
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(100, max_results - len(comments)),
                pageToken=next_page_token,
                textFormat='plainText'
            )
            
            response = request.execute()
            
            # Process each comment
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'video_id': video_id,
                    'author': comment['authorDisplayName'],
                    'text': comment['textDisplay'],
                    'likes': comment['likeCount'],
                    'published_at': comment['publishedAt']
                })
            
            # Check if there are more comments to fetch
            next_page_token = response.get('nextPageToken')
            if not next_page_token or len(comments) >= max_results:
                break
        
        return comments[:max_results]
    
    except HttpError as e:
        print(f"An HTTP error occurred for video {video_id}: {e.resp.status} {e.content}")
        return []
    except Exception as e:
        print(f"An error occurred for video {video_id}: {str(e)}")
        return []

def save_comments_to_json(comments: List[Dict], output_file: str):
    """Save comments to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

def save_comments_to_csv(comments: List[Dict], output_file: str):
    """Save comments to a CSV file."""
    if not comments:
        print("No comments to save to CSV")
        return
    
    fieldnames = comments[0].keys()
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(comments)

def main():
    """Main function to process YouTube URLs and save comments."""
    # Set console to UTF-8 mode
    import sys
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

    try:
        # Create output directory if it doesn't exist
        output_dir = "output_dir/raw_comments"
        os.makedirs(output_dir, exist_ok=True)

        # Read URLs from file
        with open('youtube_urls.txt', 'r') as f:
            urls = [line.strip() for line in f if line.strip()]

        # Process each URL
        all_comments = []
        for url in urls:
            try:
                video_id = extract_video_id(url)
                print(f"\nProcessing video: {url}")
                print(f"Video ID: {video_id}")
                
                comments = get_video_comments(video_id)
                print(f"Retrieved {len(comments)} comments")
                all_comments.extend(comments)
            
            except ValueError as e:
                print(f"Error processing URL {url}: {str(e)}")
                continue

        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save all comments to JSON and CSV
        if all_comments:
            json_file = os.path.join(output_dir, f"youtube_comments_{timestamp}.json")
            csv_file = os.path.join(output_dir, f"youtube_comments_{timestamp}.csv")
            
            save_comments_to_json(all_comments, json_file)
            save_comments_to_csv(all_comments, csv_file)
            
            print(f"\nSaved {len(all_comments)} comments to:")
            print(f"JSON: {json_file}")
            print(f"CSV: {csv_file}")
        else:
            print("\nNo comments were retrieved.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 