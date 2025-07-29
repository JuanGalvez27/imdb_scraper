import csv
import hashlib
import os

from imdb_scraper.models import Actor, Base, Movie, movie_actor_association
from imdb_scraper.settings import SCRAPY_OUTPUT_FILE
from scrapy import Spider
from scrapy.exceptions import DropItem, NotConfigured
from scrapy.exporters import CsvItemExporter
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker


class ImdbScraperPipeline:
    def process_item(self, item, spider):
        return item


class PostgresPipeline:
    def __init__(self, db_url):
        self.db_url = db_url

    @classmethod
    def from_crawler(cls, crawler):
        db_url = crawler.settings.get("DATABASE_URL")
        if not db_url:
            raise NotConfigured("DATABASE_URL setting is missing")
        return cls(db_url)

    def open_spider(self, spider: Spider):
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def close_spider(self, spider: Spider):
        self.engine.dispose()

    def process_item(self, item, spider: Spider):
        session = self.Session()
        try:
            movie = session.query(Movie).filter_by(title=item["title"]).first()
            if not movie:
                movie = Movie(
                    title=item["title"],
                    year=item.get("release_year"),
                    rating=item.get("rating"),
                    duration=item.get("duration_minutes"),
                    metascore=item.get("metascore"),
                )
                session.add(movie)
                session.flush()

            actor_instances = []
            for actor_name in item.get("main_actors", []):
                actor = session.query(Actor).filter_by(name=actor_name).first()
                if not actor:
                    actor = Actor(name=actor_name)
                    session.add(actor)
                    session.flush()
                actor_instances.append(actor)

            for actor in actor_instances:
                if actor not in movie.actors:
                    movie.actors.append(actor)

            session.commit()
            return item

        except IntegrityError:
            session.rollback()
            spider.logger.warning(f"IntegrityError with movie: {item['title']}")
        except Exception as e:
            session.rollback()
            spider.logger.error(f"Error processing item: {item['title']} - {str(e)}")
        finally:
            session.close()


class UniqueCsvPipeline:
    def __init__(self):
        self.seen_hashes = set()
        self.filename = SCRAPY_OUTPUT_FILE
        self.file = None
        self.exporter = None

    def open_spider(self, spider):
        if os.path.exists(self.filename):
            with open(self.filename, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = self._item_hash(row)
                    self.seen_hashes.add(key)

        self.file = open(self.filename, mode="ab")
        self.exporter = CsvItemExporter(self.file)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        key = self._item_hash(item)
        if key in self.seen_hashes:
            raise DropItem(f"Duplicate item: {item['title']}")
        self.seen_hashes.add(key)
        self.exporter.export_item(item)
        return item

    def _item_hash(self, item):
        unique_str = f"{item['title'].strip().lower()}|{item.get('release_year', '')}"
        return hashlib.sha256(unique_str.encode()).hexdigest()
