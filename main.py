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

if __name__ == "__main__":
    thread_name = "griefbots"
    subreddit = get_thread(thread_name)

    # 5 most recent posts
    for post in subreddit.new(limit=5):
        print("Titre :", post.title)
        print("Auteur :", post.author)
        print("URL :", post.url)
        print("Texte :", post.selftext[:300], "…")
        print("-" * 80)

    # 5 hotter posts
    for post in subreddit.hot(limit=5):
        print("Titre :", post.title)
        print("Auteur :", post.author)
        print("URL :", post.url)
        print("Texte :", post.selftext[:300], "…")
        print("-" * 80)