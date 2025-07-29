from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

movie_actor_association = Table(
    "movie_actor_association",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True),
    Column("actor_id", Integer, ForeignKey("actors.id"), primary_key=True),
)


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), unique=True, nullable=False)
    year = Column(Integer)
    rating = Column(Float)
    duration = Column(Integer)
    metascore = Column(Float)

    actors = relationship(
        "Actor", secondary=movie_actor_association, back_populates="movies"
    )

    def __repr__(self):
        return f"<Movie(id={self.id}, title='{self.title}')>"


class Actor(Base):
    __tablename__ = "actors"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)

    movies = relationship(
        "Movie", secondary=movie_actor_association, back_populates="actors"
    )

    def __repr__(self):
        return f"<Actor(id={self.id}, name='{self.name}')>"
