from collections import Counter
from datetime import datetime

import praw
from model import Post
from utils import CLIENT_ID, CLIENT_SECRET, extract_post_data, get_words_list


def frequent_words(list_posts: list[Post]) -> list[tuple[str, int]]:
    """
    Get the most common words from a list of posts/comments.
    Args:
        list_posts (list[Post]): List of Post objects containing content.
    Returns:
        list[tuple[str, int]]: List of tuples with the most common words and their counts.
    """

    # Getting common English stopwords
    common_stopwords = get_words_list()

    # Extract words from posts/comments
    words = [
        w.lower()
        for post in list_posts
        for w in (post.Content or "").split()
        if len(w) > 3 and w.isalpha() and w.lower() not in common_stopwords
    ]

    # Get the most common words
    common_words = Counter(words).most_common(2)

    return common_words

if __name__ == "__main__":
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent="u/sk00bew",
    )
    subreddit = reddit.subreddit("Futurology")
    begin = datetime(2020, 1, 1)
    end = None

    all_data = extract_post_data(
        subreddit,
        limit=3,
        start_date=begin,
        end_date=end,
        key_words=None,
    )
    common_words = frequent_words(all_data)
    print("Most common words:")
    for word, count in common_words:
        print(f"{word}: {count}")

