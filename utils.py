import os
import re
from collections import Counter
from datetime import datetime
import nltk
from dotenv import load_dotenv
from nltk.corpus import stopwords
from praw.models import Subreddit
from model import Post, Comment

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def get_words_lists_old() -> tuple[list[str], list[str]]:
    positive_words = []
    negative_words = []
    with open("../words_lists/positive_words.txt", "r") as pos_file:
        positive_words = [
            line.strip()
            for line in pos_file
            if line.strip() and not line.startswith(";")
        ]
    with open("../words_lists/negative_words.txt", "r") as neg_file:
        negative_words = [
            line.strip()
            for line in neg_file
            if line.strip() and not line.startswith(";")
        ]
    return positive_words, negative_words


def analyze_post_interactions(subreddit: Subreddit, type: str, limit: int) -> None:
    """Analyze interactions on the most popular posts in a subreddit.
    Args:
        subreddit (Subreddit): The subreddit to analyze.
        type (str): Type of posts to analyze ("hot", "top", or "new").
        limit (int): Number of top posts to analyze.
    """
    # Select posts based on the specified type
    if type == "hot":
        print(
            f"\n=== Analysing top {limit} hot posts in r/{subreddit.display_name} ===\n"
        )
        reddit_iterator = subreddit.hot(limit=limit)
    elif type == "top":
        print(
            f"\n=== Analysing {limit} toppest posts in r/{subreddit.display_name} ===\n"
        )
        reddit_iterator = subreddit.top(limit=limit)
    else:
        print(
            f"\n=== Analysing {limit} newest posts in r/{subreddit.display_name} ===\n"
        )
        reddit_iterator = subreddit.new(limit=limit)

    # Load positive and negative words
    positive_words, negative_words = get_words_list()

    # Getting common English stopwords
    nltk.download("stopwords")
    common_stopwords = set(stopwords.words("english"))

    posts_stats = []

    # Analyze each post
    for post in reddit_iterator:
        # Fetch all comments
        post.comments.replace_more(limit=0)
        comments = post.comments.list()
        if post.treatment_tags:
            print(f"Skipping post '{post.title}' (advertisement detected).")
            continue

        # Basic statistics on comments
        nb_comments = len(comments)
        avg_score = (
            sum(comment.score for comment in comments) / nb_comments
            if nb_comments > 0
            else 0
        )
        avg_length = (
            sum(len(comment.body) for comment in comments) / nb_comments
            if nb_comments > 0
            else 0
        )

        # Sentiment analysis on comments
        pos_count = sum(
            any(w in comment.body.lower() for w in positive_words)
            for comment in comments
        )
        neg_count = sum(
            any(w in comment.body.lower() for w in negative_words)
            for comment in comments
        )

        # Most frequent words excluding short/common words on comments
        words = [
            w.lower()
            for comment in comments
            for w in comment.body.split()
            if len(w) > 3 and w.isalpha() and w.lower() not in common_stopwords
        ]
        common_words = Counter(words).most_common(5)

        posts_stats.append(
            {
                "title": post.title[:60],  # tronqué pour lisibilité
                "score": post.score,
                "positive": pos_count,
                "negative": neg_count,
            }
        )

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
    # return plot_sentiment_bars(posts_stats)


def contains_keyword(text: str, keywords: list[str]) -> bool:
    """
    Checks if any of the keywords are present in the given text (whole words only).
    Args:
        text (str): The text to search within.
        keywords (list[str]): List of keywords to search for.
    Returns:
        bool: True if any keyword is found, False otherwise.
    """
    if not text or not keywords:
        return False
    for kw in keywords:
        pattern = rf"\b{re.escape(kw)}\b"
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    return False


def extract_post_data(
    subreddit: Subreddit,
    limit: int,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    key_words: list[str] | None = None,
) -> list[Post]:
    """
    Extracts posts and comments containing given keywords or within a date range.
    Args:
        subreddit (Subreddit): The subreddit to extract data from.
        limit (int): Maximum number of posts and comments to extract.
        start_date (datetime | None): Start date for filtering posts/comments.
        end_date (datetime | None): End date for filtering posts/comments.
        key_words (list[str] | None): List of keywords to filter posts/comments.
    Returns:
        list[Post]: List of Post and Comment objects matching the criteria.
    """
    all_data = []
    posts = subreddit.top(limit=None)
    post_count = 0
    scrapped = 0

    for raw_post in posts:
        scrapped += 1
        if post_count >= limit:
            break

        # Filter post by date
        post_datetime = datetime.utcfromtimestamp(raw_post.created_utc)
        if start_date and post_datetime < start_date:
            continue
        if end_date and post_datetime > end_date:
            continue

        # Build post data
        post = Post.from_reddit(reddit_obj=raw_post, subreddit=subreddit, id_number=post_count + 1)

        # Check post keywords
        post_has_keyword = (
            (contains_keyword(post.Content, key_words) if key_words else True) or
            (contains_keyword(post.Thread_Title, key_words) if key_words else True)
    )

        # Load comments
        raw_post.comments.replace_more(limit=0)
        comments = raw_post.comments.list()
        comment_count = 0
        relevant_comments = []

        for raw_comment in comments:
            scrapped += 1
            if comment_count >= limit:
                break

            # Filter comment by date
            comment_datetime = datetime.utcfromtimestamp(raw_comment.created_utc)
            if start_date and comment_datetime < start_date:
                continue
            if end_date and comment_datetime > end_date:
                continue

            # Build comment data
            comment = Comment.from_reddit(reddit_obj=raw_comment,
                                               subreddit= subreddit,
                                               id_number=comment_count + 1,
                                               parent_post=post)

            # Check comment for keywords
            comment_has_keyword = (
                (contains_keyword(comment.Content, key_words) if key_words else True) or
                (contains_keyword(comment.Thread_Title, key_words) if key_words else True)
            )

            if not comment_has_keyword:
                continue

            relevant_comments.append(comment)
            comment_count += 1

        # Add post and its relevant comments if criteria met
        if post_has_keyword or relevant_comments:
            all_data.append(post)
            all_data.extend(relevant_comments)
            post_count += 1
            print(f"Added post {post.id} ({len(relevant_comments)} comments)")

    print(f"Total relevant items: {len(all_data)} / Scrapped: {scrapped}")
    return all_data

def get_words_list() -> list[str]:
    """
    Get a list of common English stopwords with some additions.
    """

    nltk.download("stopwords")
    common_stopwords = stopwords.words("english")
    common_stopwords += ["still","even","would","also","could","might","must","need","thing","really","something","anything","everything"]

    return common_stopwords


