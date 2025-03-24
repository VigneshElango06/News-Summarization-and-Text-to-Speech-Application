import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from transformers import pipeline
import pyttsx3
import io
import tempfile
import soundfile as sf
import numpy as np

def extract_news_articles(company_name):
    search_query = f"{company_name} news"
    search_url = f"https://www.google.com/search?q={search_query}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []

    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.startswith('/url?q=') and not href.startswith('/url?q=https://www.google.com/search'):
            real_link = href.split('/url?q=')[1].split('&')[0]
            if not real_link.endswith('.js'): #basic non js filter
                links.append(real_link)

    articles = []
    for link in links[:10]: #limit to 10 articles
        try:
            article_response = requests.get(link, headers=headers)
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            title = article_soup.find('title').text if article_soup.find('title') else 'No Title'
            paragraphs = article_soup.find_all('p')
            summary = ' '.join([p.text for p in paragraphs[:5]]) #basic summary generation
            articles.append({'title': title, 'summary': summary, 'link': link})
        except:
            pass

    return articles

def analyze_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return 'Positive'
    elif analysis.sentiment.polarity < 0:
        return 'Negative'
    else:
        return 'Neutral'

def extract_topics(text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    topics_generator = pipeline("text-classification", model="facebook/bart-large-mnli", multi_label=True)
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    topics = topics_generator(summary[0]['summary_text'], candidate_labels=["business", "finance", "technology", "politics", "sports", "entertainment"])
    return [label for label, score in zip(topics['labels'], topics['scores']) if score > 0.5]

def analyze_company_news(company_name):
    articles = extract_news_articles(company_name)
    if not articles:
        return None
    results = {"articles": []}
    for article in articles:
        sentiment = analyze_sentiment(article["summary"])
        topics = extract_topics(article["summary"])
        results["articles"].append({
            "title": article["title"],
            "summary": article["summary"],
            "sentiment": sentiment,
            "topics": topics,
        })

    comparative_analysis = {}
    positive_count = sum(1 for article in results["articles"] if article["sentiment"] == "Positive")
    negative_count = sum(1 for article in results["articles"] if article["sentiment"] == "Negative")
    neutral_count = sum(1 for article in results["articles"] if article["sentiment"] == "Neutral")

    comparative_analysis["positive_articles"] = positive_count
    comparative_analysis["negative_articles"] = negative_count
    comparative_analysis["neutral_articles"] = neutral_count
    results["comparative_analysis"] = comparative_analysis
    return results

def text_to_hindi_speech(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('voice', 'hindi')  # Set the voice to Hindi
        engine.setProperty('rate', 150)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio:
            engine.save_to_file(text, temp_audio.name)
            engine.runAndWait()
            engine.stop()

            with open(temp_audio.name, 'rb') as audio_file:
                audio_bytes = audio_file.read()
            return audio_bytes
    except Exception as e:
        print(f"TTS Error: {e}")
        return None