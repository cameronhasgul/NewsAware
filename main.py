from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Field,  create_engine, Session, select

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

# Define a root GET endpoint
@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "NewsAware Backend",
        "message": "Welcome to the NewsAware API!"
    }