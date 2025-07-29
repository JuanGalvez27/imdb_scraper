# IMDb Scraper

Amazing app to scrape IMDb top 250 films and get its title, release_year, rating, duration_minutes, metascore and main_actors, then store it in a CVS file and in a PostgreSQL database.

## Running the project 
- Clone the repo
- Create a .env file into /imdb_scraper, take this as an example:
>
```
POSTGRES_USER=scrapyuser
POSTGRES_PASSWORD=scrapypass
POSTGRES_DB=scrapydb
DATABASE_HOST=host.docker.internal
DATABASE_PORT=5432

SCRAPY_OUTPUT_FILE=output/movies.csv
SCRAPY_SPIDER_NAME=movies

ROBOTSTXT_OBEY=True
USER_AGENT="Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
```
- Run `docker compose up --build`
- Open a Terminal and run `docker exec -it imdb_scraper bash`
- Run `scrapy crawl movies` to run the scraper 
- Enjoy it!



1. Get the 5 films with the longest average length per decade.

```
SELECT
    (year / 10) * 10 AS decade,
    AVG(CAST(duration AS FLOAT)) AS avg_duration
FROM movies
WHERE duration IS NOT NULL
GROUP BY decade
ORDER BY avg_duration DESC
LIMIT 5;
```

2. Calculate the standard deviation of grades per year.

```
SELECT
    year,
    STDDEV(CAST(rating AS FLOAT)) AS std_rating
FROM movies
WHERE rating IS NOT NULL
GROUP BY year
ORDER BY year;
```

3. Detect movies with more than a 20% difference between IMDB rating and Metascore (normalized).

```
SELECT
    title,
    rating,
    metascore,
    ROUND((CAST(metascore AS FLOAT) / 10)::numeric, 2) AS metascore_normalized,
    ABS(rating - (CAST(metascore AS FLOAT) / 10)) AS diff
FROM movies
WHERE rating IS NOT NULL AND metascore IS NOT NULL
  AND ABS(rating - (CAST(metascore AS FLOAT) / 10)) > 2
```

4. Create a view that links movies and actors, and allows filtering by lead actor.

```
CREATE OR REPLACE VIEW movie_actor_view AS
SELECT
    m.id AS movie_id,
    m.title AS movie_title,
    a.id AS actor_id,
    a.name AS actor_name
FROM movies m
JOIN movie_actor_association maa ON m.id = maa.movie_id
JOIN actors a ON a.id = maa.actor_id;
```

Run the view
```
SELECT * FROM movie_actor_view;