from db_handlers.db_connection import DatabaseCursor
from typing import Set, Dict
from learn_bot.config import GEO_DB


def create_countries_tb() -> None:
    with DatabaseCursor(GEO_DB) as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS countries (
        country_title TEXT PRIMARY KEY,
        country_eng_title TEXT,
        capital TEXT,
        country_flag TEXT,
        country_article_link TEXT,
        position_on_map_image TEXT,
        country_flag_bytes BLOB,
        position_on_map_image_bytes BLOB
        )""")


def add_country(country_tuple_to_insert) -> None:
    with DatabaseCursor(GEO_DB) as cursor:
        cursor.execute(
            """INSERT OR IGNORE INTO countries(
            country_title,
            country_eng_title,
            capital,
            country_flag,
            country_article_link,
            position_on_map_image)
            VALUES (?,?,?,?,?,?)""",
            country_tuple_to_insert
        )


def select_db_country_titles() -> Set:
    with DatabaseCursor(GEO_DB) as cursor:
        country_titles = cursor.execute(
            """SELECT
            country_title
            FROM countries
            WHERE
            country_flag is not NULL
            AND
            position_on_map_image is not NULL
            ;"""
        )

        country_titles = {t["country_title"] for t in country_titles}
    return country_titles


def absent_images() -> Dict:
    """
    Getting the total list of files that needed to be downloaded into a db
    and then converted to a readable format
    to machine
    """
    with DatabaseCursor(GEO_DB) as cursor:
        absent_flags = cursor.execute(
            """SELECT country_flag FROM countries \
            WHERE country_flag_bytes IS NULL LIMIT 3;"""
        ).fetchall()
        absent_positions = cursor.execute("""\
            SELECT position_on_map_image FROM countries\
            WHERE position_on_map_image_bytes IS NULL LIMIT 3;""").fetchall()
        absent_flags = [f["country_flag"] for f in absent_flags]
        absent_positions = [
            p["position_on_map_image"] for p in absent_positions
        ]

    return {"flag": absent_flags, "position": absent_positions}


def country_title_get_db_row(country_title: str) -> Dict:
    with DatabaseCursor(GEO_DB) as cursor:
        country_row = cursor.execute(
            """SELECT * FROM countries
            WHERE
            country_title LIKE ?\
            OR country_eng_title LIKE ?;""",
            (
                f"%{country_title}%",
                f"%{country_title}%"
            )
        )

        return dict(country_row.fetchone())


def write_image_to_db(
    country_title: str,
    db_col_name: str,
    image_bytes: bytes
) -> None:
    with DatabaseCursor(GEO_DB) as cursor:
        cursor.execute(f"""
        UPDATE countries
        SET {db_col_name} = ?
        WHERE country_title = ?
        """, (image_bytes, country_title))
        print(f"{country_title}::{db_col_name},\
             len(image_bytes): {len(image_bytes)},\
             type(image_bytes): {type(image_bytes)}")


if __name__ == "__main__":
    country = country_title_get_db_row("Россия")
    print("hello world")
