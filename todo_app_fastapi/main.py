from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from todo_app_fastapi import setting
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends

class Todo(SQLModel, table=True):
    id : Optional[int] = Field(default = None, primary_key=True)
    content: str = Field(index=True)

# only needed for psycopg 3 - replace postgresql
# with postgresql+psycopg in settings.DATABASE_URL
connection_string = str(setting.Database_URL).replace(
    "postgresql", "postgresql+psycopg"
)

# recycle connections after 5 minutes
# to correspond with the compute scale down

engine = create_engine(
    connection_string, connect_args={'sslmode':'require'}, pool_recycle=300
)

def create_tables_and_db():
    SQLModel.metadata.create_all(engine)

# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
@asynccontextmanager
async def lifespan(app : FastAPI):
    print("creating Tables...")
    create_tables_and_db
    yield

app = FastAPI(lifespan=lifespan, title="Todo App with Database",
    version="0.0.1",
    servers=[{
        "url": "https://0.0.0.0:8000",
        "description":"Development Server"
    }])

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/")
def home():
    return {"First API" : "With Database"}

@app.post("/todo/")
def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@app.get("/todo/")
def read_todo(session: Annotated[Session, Depends(get_session)]):
    todo = session.exec(select(todo)).all()
    return todo