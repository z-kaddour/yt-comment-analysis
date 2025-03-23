import json
import os
import glob
import pandas as pd
from datetime import datetime
import re

# Define themes and their keywords
THEMES = {
    "Customer Identification": [
        "passport", "id", "identification", "باسبور", "جواز", "هوية", "توثيق"
    ],
    "fees": [
        "fee", "fees", "commission", "cost", "pricing", "رسوم", "عموله", "عمولة", "تكلفة", "مصاريف"
    ],
    "withdrawal": [
        "withdraw", "withdrawal", "اسحب", "سحب"
    ],
    "account_activation": [
        "activate", "activation",  "تفعيل", "تنشيط"
    ],
    "integration_apps": [
        "integration", "integrate", "api", "link", "connect", "الربط", "بوابة دفع", "ربط", "توافق", "stripe", "paypal", "shopify"
    ],
    "customer_service": [
        "support", "customer service", "help", "contact", "دعم", "خدمة العملاء", "تواصل", "مساعدة", "التواصل", "الدعم"
    ],
    "country_sudan": ["sudan", "السودان"],
    "country_yemen": ["yemen", "اليمن"],
    "country_turkey": ["turkey", "تركيا"],
    "country_saudi_arabia": ["saudi", "saudi arabia", "السعودية"],
    "country_iraq": ["iraq", "العراق"],
    "country_algeria": ["algeria", "الجزائر"],
    "country_egypt": ["egypt", "مصر"],
    "country_lebanon": ["lebanon", "لبنان"],
    "country_syria": ["syria", "سوريا"],
    "country_morocco": ["morocco", "المغرب"],
    "country_tunisia": ["tunisia", "تونس"],
    "country_palestine": ["palestine", "فلسطين", "gaza", "غزة"],
    "country_oman": ["oman", "عمان"],
    "country_jordan": ["jordan", "الأردن"],
    "country_kuwait": ["kuwait", "الكويت"],
    "country_bahrain": ["bahrain", "البحرين"],
    "country_qatar": ["qatar", "قطر"],
    "country_uae": ["uae", "الإمارة العربية المتحدة"],
    "country_bangladesh": ["bangladesh", "بنغلاديش"],
    "country_india": ["india", "الهند"],
    "country_pakistan": ["pakistan", "باكستان"],
    "country_nepal": ["nepal", "نيبال"],
    "country_afghanistan": ["afghanistan", "أفغانستان"],
    "country_iran": ["iran", "إيران"],
}

def load_latest_processed_comments():
    """
    Finds and loads the most recent JSON file with processed comments.
    
    Returns:
        df: The loaded JSON data or None if no analysis files are found
    """
    try:
        # Assuming analysis files are stored in an 'processed_comments' directory
        # and follow a naming pattern that includes a timestamp
        processed_comments_dir = "output_dir/processed_comments"
        
        # Print if it doesn't exist
        if not os.path.exists(processed_comments_dir):
            print(f"Analysis directory '{processed_comments_dir}' not found.")
            return None
        
        # Find all JSON files in the analysis directory
        json_files = glob.glob(os.path.join(processed_comments_dir, "*.json"))
        
        if not json_files:
            print("No analysis JSON files found.")
            return None
        
        # Sort files by modification time (most recent last)
        latest_file = max(json_files, key=os.path.getmtime)
        
        print(f"Loading latest analysis file: {latest_file}")
        
        # Load and return the JSON data
        with open(latest_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        return pd.DataFrame(data['comments'])
    
    except Exception as e:
        print(f"Error loading analysis file: {str(e)}")
        return None

# Analysis functions

def analyse_most_liked_comments(df: pd.DataFrame, top_n=10):
    """Get the top N comments with the most likes from the dataframe."""
    if df is None or df.empty:
        return None
    
    # Sort by likes and get top N
    top_liked = df.nlargest(top_n, 'likes')
    
    # Create the header
    result_text = """
        ====================================
        === Top {top_n} Most Liked Comments ==="""
    
    # Add each comment's details
    i=0
    for idx, comment in top_liked.iterrows():
        i+=1
        result_text += f"""
        
        --- #{i} Most Liked Comment (ID:{idx + 1})---
        Author: {comment['author']}
        Likes: {comment['likes']}
        Published at: {comment['published_at']}

        Original text:
        {comment['text']}

        Cleaned/translated text:
        {comment['cleaned_text']}

        Sentiment: {comment['sentiment']}"""
    
    # Add footer
    result_text += "\n        ===================================="
    
    return result_text

def analyse_sentiment_distribution(df: pd.DataFrame):
    """Analyze and summarize the sentiment distribution across all comments."""
    if df is None or df.empty:
        return None
    
    # Calculate sentiment counts
    sentiment_counts = df['sentiment'].value_counts()
    
    # Calculate percentages
    total_comments = len(df)
    sentiment_percentages = (sentiment_counts / total_comments * 100).round(2)
    
    # Create summary text
    sentiment_text = f"""
        ====================================
        === Sentiment Analysis Summary ===
        Total Comments Analyzed: {total_comments}

        Sentiment Distribution:
        Question: {sentiment_counts.get('question', 0)} ({sentiment_percentages.get('question', 0)}%)
        Positive: {sentiment_counts.get('positive affirmation', 0)} ({sentiment_percentages.get('positive affirmation', 0)}%)
        Neutral: {sentiment_counts.get('neutral affirmation', 0)} ({sentiment_percentages.get('neutral affirmation', 0)}%)
        Negative: {sentiment_counts.get('negative affirmation', 0)} ({sentiment_percentages.get('negative affirmation', 0)}%)

        Additional Statistics:
        Average Likes per Comment: {df['likes'].mean():.5f}
        Most Common Sentiment: {sentiment_counts.index[0]}
        
        ===================================="""
    return sentiment_text

def analyse_themes(df: pd.DataFrame):
    """Analyze themes in comments based on keyword identification."""
    if df is None or df.empty:
        return None
    
    # Initialize counters for each theme
    theme_counts = {theme: 0 for theme in THEMES.keys()}
    theme_comments = {theme: [] for theme in THEMES.keys()}
    theme_sentiments = {theme: {'question': 0, 'positive affirmation': 0, 'neutral affirmation': 0, 'negative affirmation': 0} 
                       for theme in THEMES.keys()}
    
    # Function to check if text contains any keyword from a list
    def contains_keywords(text, keywords):
        # Convert text to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Add spaces around punctuation to ensure proper word boundary detection
        for punct in '.,!?;:()[]{}':
            text_lower = text_lower.replace(punct, f' {punct} ')
        
        # Split into words and remove empty strings
        words = [w for w in text_lower.split() if w]
        
        # Check each keyword
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in words:
                return True
        return False
    
    # Analyze each comment
    for idx, comment in df.iterrows():
        text = f"{comment['text']} {comment['cleaned_text']}"  # Check both original and cleaned text
        
        # Check each theme
        for theme, keywords in THEMES.items():
            if contains_keywords(text, keywords):
                theme_counts[theme] += 1
                theme_comments[theme].append({
                    'text': comment['text'],
                    'likes': comment['likes']
                })
                # Count sentiment for this theme
                theme_sentiments[theme][comment['sentiment']] += 1
    
    # Calculate percentages
    total_comments = len(df)
    theme_percentages = {theme: (count/total_comments*100) for theme, count in theme_counts.items()}
    
    # Group themes by category
    country_themes = [theme for theme in THEMES.keys() if theme.startswith('country_')]
    service_themes = [theme for theme in THEMES.keys() if not theme.startswith('country_')]
    
    # Create summary text
    themes_text = f"""
        ====================================
        === Themes Analysis Summary ===
        Total Comments Analyzed: {total_comments}

        --- Service-Related Themes ---"""
    
    # Add service themes with all their comments
    for theme in service_themes:
        count = theme_counts[theme]
        percentage = theme_percentages[theme]
        
        # Get keywords for this theme
        keywords_str = ", ".join(THEMES[theme])
        
        # Calculate sentiment percentages for this theme
        if count > 0:
            sentiment_dist = theme_sentiments[theme]
            sentiment_str = f"[Q:{sentiment_dist['question']}, +:{sentiment_dist['positive affirmation']}, "
            sentiment_str += f"=:{sentiment_dist['neutral affirmation']}, -:{sentiment_dist['negative affirmation']}]"
        else:
            sentiment_str = ""
        
        themes_text += f"\n        {theme.replace('_', ' ').title()}: {count} ({percentage:.2f}%) {sentiment_str}"
        themes_text += f"\n        Keywords: {keywords_str}"
        
        if count > 0:
            # Sort comments by likes
            sorted_comments = sorted(theme_comments[theme], key=lambda x: x['likes'], reverse=True)
            themes_text += "\n        Comments:"
            for comment in sorted_comments:
                # Remove newlines and truncate if too long
                clean_text = comment['text'].replace('\n', ' ')
                if len(clean_text) > 200:
                    clean_text = clean_text[:197] + "..."
                themes_text += f"\n        - {clean_text}"
            themes_text += "\n"
    
    # Add country themes as a single category
    country_specific_comments = []
    total_country_mentions = 0
    
    themes_text += "\n\n        --- Country-Specific Comments ---"
    
    # First list country statistics (only non-zero counts)
    non_zero_countries = [(theme, count) for theme, count in theme_counts.items() 
                         if theme.startswith('country_') and count > 0]
    
    # Sort countries by mention count
    non_zero_countries.sort(key=lambda x: x[1], reverse=True)
    
    for theme, count in non_zero_countries:
        percentage = theme_percentages[theme]
        country_name = theme.replace('country_', '').replace('_', ' ').title()
        
        # Add sentiment distribution for this country
        sentiment_dist = theme_sentiments[theme]
        sentiment_str = f"[Q:{sentiment_dist['question']}, +:{sentiment_dist['positive affirmation']}, "
        sentiment_str += f"=:{sentiment_dist['neutral affirmation']}, -:{sentiment_dist['negative affirmation']}]"
        
        themes_text += f"\n        {country_name}: {count} ({percentage:.2f}%) {sentiment_str}"
        total_country_mentions += count
        
        # Add comments to the combined list with country prefix
        for comment in theme_comments[theme]:
            country_specific_comments.append({
                'country': country_name,
                'text': comment['text'],
                'likes': comment['likes']
            })
    
    # Add overall country statistics
    if total_country_mentions > 0:
        country_percentage = (total_country_mentions/total_comments*100)
        themes_text += f"\n\n        Total Country-Related Comments: {total_country_mentions} ({country_percentage:.2f}%)"
        
        # Add all country-specific comments sorted by likes
        if country_specific_comments:
            sorted_country_comments = sorted(country_specific_comments, key=lambda x: x['likes'], reverse=True)
            themes_text += "\n        Comments by Country:"
            for comment in sorted_country_comments:
                # Remove newlines and truncate if too long
                clean_text = comment['text'].replace('\n', ' ')
                if len(clean_text) > 200:
                    clean_text = clean_text[:197] + "..."
                themes_text += f"\n        - [{comment['country']}] {clean_text}"
    
    themes_text += "\n        ===================================="
    
    return themes_text

if __name__ == "__main__":
    # Load the latest analysis data
    comments_df = load_latest_processed_comments()

    # Write results
    if comments_df is not None and not comments_df.empty:        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("output_dir/analysis_results", exist_ok=True)
        with open(f"output_dir/analysis_results/analysis_{timestamp}.txt", 'w', encoding='utf-8') as f:
            # Write sentiment analysis
            f.write(analyse_sentiment_distribution(comments_df))
            # Write themes analysis
            f.write(analyse_themes(comments_df))
            # Write top liked comments
            f.write(analyse_most_liked_comments(comments_df))
    else:
        print("No comments data available for analysis")

    # Print comments sorted by likes in descending order
    print("\nComments sorted by likes (descending):")
    print(comments_df.sort_values(by='likes', ascending=False)[['author', 'likes', 'cleaned_text']])
