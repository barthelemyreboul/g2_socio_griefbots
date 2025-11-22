from collections import Counter
from datetime import datetime
import praw
import re
from gensim.utils import simple_preprocess
from gensim import corpora
from gensim.models.ldamodel import LdaModel
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
stop_words = set(stopwords.words("english") + ["even","thing","want","still","would", "every","get","got","make","much","know"])
lemmatizer = WordNetLemmatizer()

from model import Post
from utils import CLIENT_ID, CLIENT_SECRET, extract_post_data, get_words_list
from config import key_words_1, key_words_2

def frequent_words(list_posts: list[Post], toppest: int) -> list[tuple[str, int]]:
    """
    Get the most common words from a list of posts/comments.
    Args:
        list_posts (list[Post]): List of Post objects containing content.
        toppest (int): Number of top common words to return.
    Returns:
        list[tuple[str, int]]: List of tuples with the most common words and their counts.
    """

    # Getting common English stopwords
    common_stopwords = get_words_list()

    # Extract words from posts/comments
    words = [
        w.lower()
        for post in list_posts
        for w in ((post.Content+post.Thread_Title) or "").split()
        if len(w) > 3 and w.isalpha() and w.lower() not in common_stopwords
    ]

    # Get the most common words
    common_words = Counter(words).most_common(toppest)

    return common_words


def clean_text(text: str):

    if not text or not isinstance(text, str):
        return []

    # Deleting urls, special characters & mentions
    text = re.sub(r"http\S+|www\S+|@\w+", " ", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    tokens = simple_preprocess(text, deacc=True, min_len=3)

    tokens = [lemmatizer.lemmatize(tok) for tok in tokens if tok not in stop_words]
    return tokens

def train_lda(posts: list[Post], num_topics=10):

    # Clean text
    documents = [clean_text(post.Content) for post in posts]

    # Words dictionnary
    dictionary = corpora.Dictionary(documents) # indexing words
    dictionary.filter_extremes(no_below=5, no_above=0.5) # only keeps words present in >=5 doc and <50% docs

    # Making bags of words, each word (identified by its index) is associated with a number of occurence
    corpus = [dictionary.doc2bow(doc) for doc in documents]

    lda = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        random_state=42,
        chunksize=len(corpus)//10, # Chunksize = 10% of the corpus
        passes=15, # Number of iteration
        alpha="auto",
        eta="auto"
    )

    return lda, corpus, dictionary

# ----------------------------------------------------
# Affichage des topics
# ----------------------------------------------------

def display_topics(lda_model, num_words=10):
    for idx, topic in lda_model.print_topics(num_topics=-1, num_words=num_words):
        print(f"Topic {idx}: {topic}")


if __name__ == "__main__":
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent="u/sk00bew",
    )
    list_subs_1 = ["GriefSupport","Futurology"]
    list_subs_2 = ["Chatbots", "artificial", "ArtificialInteligence"]
    list_subs_3 = ["ProjectDecember1982"]

    subreddit = reddit.subreddit("GriefSupport")
    begin = datetime(2020, 1, 1)
    end = None
    all_data = extract_post_data(
        subreddit=subreddit,
        limit=100,
        start_date=begin,
        end_date=end,
        key_words=None,
    )
    #all_data_1 = [
    #    post
    #    for sub in list_subs_1
    #    for post in extract_post_data(
    #        subreddit=reddit.subreddit(sub),
    #        limit=100,
    #        start_date=begin,
    #        end_date=end,
    #        key_words=key_words_1,
    #    )
    #]
    #all_data_2 = [
    #    post
    #    for sub in list_subs_2
    #    for post in extract_post_data(
    #        subreddit=reddit.subreddit(sub),
    #        limit=100,
    #        start_date=begin,
    #        end_date=end,
    #        key_words=key_words_2,
    #    )
    #]

    # common_words = frequent_words(list_posts=all_data, toppest=20)

    lda, corpus, dictionary = train_lda(all_data, num_topics=5)
    display_topics(lda)


