from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class Post(BaseModel):
    id: str
    Reddit_URL: Optional[str] = Field(None, alias="Reddit_URL")
    Thread_Title: Optional[str] = Field(None, alias="Thread_Title")
    Subreddit: Optional[str]
    Content: Optional[str]
    Category: str = "post"
    Author: Optional[str]
    Date_Posted: Optional[str] = Field(None, alias="Date_Posted")
    Number_of_comments: Optional[int] = Field(0, alias="Number_of_comments")
    Upvotes: int = 0
    Keywords: Optional[List[str]] = None
    Sentiment: Optional[str] = None
    Tag: Optional[str] = None
    Date_added: str = Field(
        default_factory=lambda: datetime.utcnow().strftime("%d/%m/%Y"),
        alias="Date added",
    )
    Who_added: str = Field(default="automated_script", alias="Who added")

    @classmethod
    def from_reddit(
        cls,
        reddit_obj,
        subreddit,
        id_number: int,
        parent_post: Optional["Post"] = None,  # param commun, ignoré pour Post
    ) -> "Post":
        """
        Create a Post instance from a Reddit object.
        Args:
            reddit_obj: The Reddit post object.
            subreddit: The subreddit object.
            id_number (int): The ID number for the post.
            parent_post (Optional[Post]): Ignored for Post, used for Comment.
        Returns:
            Post: An instance of the Post class.
        """
        post_datetime = datetime.utcfromtimestamp(getattr(reddit_obj, "created_utc", 0))
        clean_content = (getattr(reddit_obj, "selftext", "") or "").replace("\n", " ").strip()
        title = getattr(reddit_obj, "title", "")

        return cls(
            id=f"RD-01-{id_number:02d}",
            **{
                "Reddit_URL": (
                    f"https://www.reddit.com{getattr(reddit_obj, 'permalink', '')}"
                    if hasattr(reddit_obj, "permalink")
                    else None
                ),
                "Thread_Title": title,
                "Subreddit": f"r/{getattr(subreddit, "display_name", "")}",
                "Content": clean_content or None,
                "Category": "post",
                "Author": f"u/{getattr(reddit_obj, 'author', None)}"
                if getattr(reddit_obj, "author", None)
                else None,
                "Number_of_comments": getattr(reddit_obj, "num_comments"),
                "Date_Posted": post_datetime.strftime("%d/%m/%Y"),
                "Upvotes": getattr(reddit_obj, "score", 0),
                "Tag": getattr(reddit_obj, "link_flair_text", None),
            },
        )

class Comment(Post):
    Category: str = "comment"
    Number_of_comments: Optional[int] = None
    Post: Post

    @classmethod
    def from_reddit(
        cls,
        reddit_obj,
        subreddit,
        id_number: int,
        parent_post: Optional[Post] = None,
    ) -> "Comment":

        comment_datetime = datetime.utcfromtimestamp(getattr(reddit_obj, "created_utc", 0))
        clean_text = (getattr(reddit_obj, "body", "") or "").replace("\n", " ").strip()

        # Get parent post details if available
        thread_title = getattr(parent_post, "Thread_Title", None) if parent_post else None
        parent_tag = getattr(parent_post, "Tag", None) if parent_post else None
        parent_subreddit = f"r/{getattr(subreddit, 'display_name', None)}"

        return cls(
            id=f"{parent_post.id}-{id_number:02d}" if parent_post else f"RD-{id_number:02d}",
            **{
                "Reddit_URL": (
                    f"https://www.reddit.com{getattr(reddit_obj, 'permalink', '')}"
                    if hasattr(reddit_obj, "permalink")
                    else None
                ),
                "Thread_Title": thread_title,
                "Subreddit": parent_subreddit,
                "Content": clean_text or None,
                "Category": "comment",
                "Author": f"u/{getattr(reddit_obj, 'author', None)}" if getattr(reddit_obj, "author", None) else "",
                "Date_Posted": comment_datetime.strftime("%d/%m/%Y") if getattr(reddit_obj, "created_utc", None) else None,
                "Upvotes": getattr(reddit_obj, "score", 0),
                "Tag": parent_tag,
                "Keywords": None,
                "Sentiment": None,
            },
            Post=parent_post,
        )