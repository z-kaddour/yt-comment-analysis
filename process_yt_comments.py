import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI  # Import the OpenAI class

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  # Initialize the client

def translate_and_clean_comment(comment: str) -> str:
    """Translate non-English comments to English and clean the text."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that translates text to English (if not already in English) and cleans it by removing noise, formatting issues, and redundant information. Keep the core message intact."},
                {"role": "user", "content": f"Clean and translate if necessary: {comment}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error processing comment: {e}")
        return comment

def classify_sentiment(comment: str) -> str:
    """Classify the sentiment and type of the comment."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Classify the following comment into one of these categories: 'negative affirmation', 'positive affirmation', 'neutral affirmation', 'question'. Return ONLY the category name."},
                {"role": "user", "content": comment}
            ]
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"Error classifying sentiment: {e}")
        return "neutral affirmation"

def process_comments(input_file: str, max_comments: int = 1000) -> None:
    """Process comments from JSON file."""
    # Read comments
    with open(input_file, 'r', encoding='utf-8') as f:
        comments_data = json.load(f)
    
    # Create DataFrame
    df = pd.DataFrame(comments_data)[:max_comments]
    
    print("Translating and cleaning comments...")
    df['cleaned_text'] = df['text'].apply(translate_and_clean_comment)
    
    print("Classifying sentiments...")
    df['sentiment'] = df['cleaned_text'].apply(classify_sentiment)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "output_dir/processed_comments"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save processed data
    output_data = {
        'comments': df.to_dict('records')
    }
    
    output_file = os.path.join(output_dir, f"analysis_results_{timestamp}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    # Print 
        sentiment_counts = df['sentiment'].value_counts()
    print("\nAnalysis Summary:")
    print(f"Total comments processed: {len(df)}")
    print("\nSentiment Distribution:")
    for sentiment, count in sentiment_counts.items():
        print(f"{sentiment}: {count}")

    print(f"\nResults saved to {output_file}")

def main():
    """Main function to run the analysis."""
    try:
        # Find most recent comments file
        comments_dir = "output_dir/raw_comments"
        json_files = [f for f in os.listdir(comments_dir) if f.endswith('.json')]
        if not json_files:
            raise ValueError("No comment files found in comments_output directory")
        
        latest_file = max(json_files, key=lambda x: os.path.getctime(os.path.join(comments_dir, x)))
        input_file = os.path.join(comments_dir, latest_file)
        
        print(f"Processing comments from: {input_file}")
        process_comments(input_file)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 