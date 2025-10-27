from collections import Counter
from praw import *
from praw.models import Subreddit
from dotenv import load_dotenv
load_dotenv()
import os
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

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
    if type =="hot":
        print(f"\n=== Analysing top {limit} hot posts in r/{subreddit.display_name} ===\n")
        iterator = subreddit.hot(limit=limit)
    elif type =="top":
        print(f"\n=== Analysing {limit} toppest posts in r/{subreddit.display_name} ===\n")
        iterator = subreddit.top(limit=limit)
    else:
        print(f"\n=== Analysing {limit} newest posts in r/{subreddit.display_name} ===\n")
        iterator = subreddit.new(limit=limit)

    for post in iterator:
        post.comments.replace_more(limit=0)
        comments = post.comments.list()

        nb_comments = len(comments)
        avg_score = sum(comment.score for comment in comments) / nb_comments if nb_comments > 0 else 0
        avg_length = sum(len(comment.body) for comment in comments) / nb_comments if nb_comments > 0 else 0

        # Basic word sentiment analysis
        positive_words = ["great", "amazing", "love", "excellent", "good"]
        negative_words = ["bad", "hate", "terrible", "awful", "worse"]

        pos_count = sum(any(w in comment.body.lower() for w in positive_words) for comment in comments)
        neg_count = sum(any(w in comment.body.lower() for w in negative_words) for comment in comments)

        # Most frequent words excluding short/common words
        words = [
            w.lower()
            for comment in comments for w in comment.body.split()
            if len(w) > 3 and w.isalpha()
        ]
        common_words = Counter(words).most_common(5)

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
    thread_name = "GriefSupport"
    subreddit = get_thread(thread_name)

    #get_newer_posts(subreddit= subreddit, limit=5)
    analyze_post_interactions(subreddit= subreddit,type="top", limit=5)