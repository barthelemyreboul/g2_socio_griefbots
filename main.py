from collections import Counter
from praw import *
from praw.models import Subreddit
from dotenv import load_dotenv
import os
from nltk.corpus import stopwords
import nltk
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def get_words_lists() -> tuple[list[str], list[str]]:
    positive_words = []
    negative_words = []
    with open("words_lists/positive_words.txt", "r") as pos_file:
        positive_words = [line.strip() for line in pos_file if line.strip() and not line.startswith(";")]
    with open("words_lists/negative_words.txt", "r") as neg_file:
        negative_words = [line.strip() for line in neg_file if line.strip() and not line.startswith(";")]
    return positive_words, negative_words

def get_thread(thread_name: str) -> Subreddit:
    # Create the Reddit instance
    reddit = Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent="python:projectdecember.script:v1.0 (by u/sk00bew)"
    )

    # Retrieve the subreddit
    subreddit = reddit.subreddit(thread_name)
    return subreddit

def analyze_post_interactions(subreddit: Subreddit, type: str, limit: int = 5) -> None:
    """Analyze interactions on the most popular posts in a subreddit.
    Args:
        subreddit (Subreddit): The subreddit to analyze.
        type (str): Type of posts to analyze ("hot", "top", or "new").
        limit (int): Number of top posts to analyze.
    """
    # Select posts based on the specified type
    if type =="hot":
        print(f"\n=== Analysing top {limit} hot posts in r/{subreddit.display_name} ===\n")
        reddit_iterator = subreddit.hot(limit=limit)
    elif type =="top":
        print(f"\n=== Analysing {limit} toppest posts in r/{subreddit.display_name} ===\n")
        reddit_iterator = subreddit.top(limit=limit)
    else:
        print(f"\n=== Analysing {limit} newest posts in r/{subreddit.display_name} ===\n")
        reddit_iterator = subreddit.new(limit=limit)

    # Load positive and negative words
    positive_words, negative_words = get_words_lists()

    # Getting common English stopwords
    nltk.download("stopwords")
    common_stopwords = set(stopwords.words("english"))

    # Analyze each post
    for post in reddit_iterator:

        # Fetch all comments
        post.comments.replace_more(limit=0)
        comments = post.comments.list()

        # Basic statistics on comments
        nb_comments = len(comments)
        avg_score = sum(comment.score for comment in comments) / nb_comments if nb_comments > 0 else 0
        avg_length = sum(len(comment.body) for comment in comments) / nb_comments if nb_comments > 0 else 0

        # Sentiment analysis on comments
        pos_count = sum(any(w in comment.body.lower() for w in positive_words) for comment in comments)
        neg_count = sum(any(w in comment.body.lower() for w in negative_words) for comment in comments)

        # Most frequent words excluding short/common words on comments
        words = [
            w.lower()
            for comment in comments for w in comment.body.split()
            if len(w) > 3 and w.isalpha() and w.lower() not in common_stopwords
        ]
        common_words = Counter(words).most_common(5)

        # Print analysis results
        print(f"Title: {post.title}")
        print(f"Author: {post.author}")
        print(f"Score (likes): {post.score}")
        print(f"Number of comments: {nb_comments}")
        print(f"Average comment score: {avg_score:.2f}")
        print(f"Average comment length: {avg_length:.1f} characters")
        print(f"Estimated sentiment: +{pos_count} / -{neg_count}")
        print(f"Most frequent words: {common_words}")
        print("-" * 100)


if __name__ == "__main__":
    thread_name = "GriefSupport" # or "ProjectDecember1982"
    subreddit = get_thread(thread_name)

    #get_newer_posts(subreddit= subreddit, limit=5)
    analyze_post_interactions(subreddit= subreddit,type="top", limit=5)