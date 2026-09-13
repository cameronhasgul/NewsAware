import os
import requests

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import HTTPException
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Field,  create_engine, Session, select

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# defining our article schema
class Article(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    category: str
    content: str
    url: str

# engine creation
sqlite_file_name = "newsaware.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

# create tables automatically when startup
SQLModel.metadata.create_all(engine)

# Initialize the FastAPI application instance
app = FastAPI(title="NewsAware API")

def get_session():
    with Session(engine) as session:
        yield session

@app.post("/articles")
def create_article(article: Article):
    with Session(engine) as session:
        session.add(article)
        session.commit()
        session.refresh(article)
        return article

# fetch articles by category

@app.get("/articles")
def fetch_articles(category: str):
    with Session(engine) as session:
        # select all columns from article table where category matches string in url
        statement = select(Article).where(Article.category == category)
        results = session.exec(statement).all()
        return results

@app.post("/fetch-news")
def fetch_news(category: str):
    # check if news api key is present
    if not NEWS_API_KEY:
        return HTTPException(status_code=500, detail="NEWS_API_KEY missing from .env file")

    # sends request to newsapi's top headlines for requested category
    url = f"https://newsapi.org/v2/top-headlines?category={category}&language=en&apiKey={NEWS_API_KEY}"
    response = requests.get(url)

    # error code if we cant fetch from our api
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch from NewsAPI")

    # store as json 
    data = response.json()
    # extract the articles from our json data
    raw_articles = data.get("articles", [])

    saved_articles = []
    with Session(engine) as session:
        for item in raw_articles:
            if not item.get("title") or item.get("title") == "[Removed]":
                continue

            new_article = Article(
                title=item.get("title"),
                category=category.capitalize(),
                content=item.get("description") or "No description available",
                url=item.get("url") or ""
            )
            session.add(new_article)
            saved_articles.append(new_article)
        session.commit()

    return {
        "status": "success",
        "message": f"Successfully fetched and saved {len(saved_articles)} articles!",
        "category": category
    }

# define a root GET endpoint
@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "NewsAware Backend",
        "message": "Welcome to the NewsAware API!"
    }