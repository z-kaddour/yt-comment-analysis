# YouTube Comments Analysis Tool

A Python-based tool that automatically retrieves, translates, and analyzes YouTube comments to extract insights about user sentiment and common themes. The tool processes comments to identify key topics, regional interests, and overall sentiment patterns.

## Features

- **Comment Retrieval**: Automatically fetches comments from YouTube videos
- **Sentiment Analysis**: Categorizes comments into positive, neutral, negative, or questions
- **Theme Detection**: Identifies common themes and topics in comments
- **Regional Analysis**: Tracks mentions of different countries and regions
- **Multilingual Support**: Handles both English and Arabic comments
- **Detailed Statistics**: Provides comprehensive analysis including:
  - Sentiment distribution
  - Most discussed themes
  - Country-specific insights
  - Most liked comments

## Prerequisites

1. Python 3.8 or higher
2. A Google Cloud Project with YouTube Data API v3 enabled
3. An OpenAI API key for sentiment analysis and translation

## Setup

1. Clone the repository:
```bash
git clone https://github.com/z-kaddour/yt-comment-analysis.git
cd yt-comment-analysis
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your API keys:
```env
YOUTUBE_API_KEY=your_youtube_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

1. Add YouTube URLs to analyze in `youtube_urls.txt`, one URL per line:

2. Run the comment fetcher:
```bash
python 1_fetch_comments.py --video_id YOUR_VIDEO_ID
```

3. Process and translate comments:
```bash
python 2_process_comments.py
```

4. Generate analysis:
```bash
python 3_comments_analysis.py
```

The analysis results will be saved in `output_dir/analysis_results/` with timestamps.

## Output Structure

The tool generates three types of analysis:
1. **Sentiment Analysis**: Overall distribution of comment sentiments
2. **Theme Analysis**: 
   - Service-related themes (identification, fees, withdrawals, etc.)
   - Country-specific mentions and trends
3. **Top Comments**: Most liked comments with full details

## Project Structure

```
├── 1_fetch_comments.py    # YouTube comment retrieval
├── 2_process_comments.py  # Comment processing and translation
├── 3_comments_analysis.py # Analysis and insights generation
├── requirements.txt       # Project dependencies
├── .env                  # API keys and configuration
└── output_dir/           # Generated analysis and results
```
