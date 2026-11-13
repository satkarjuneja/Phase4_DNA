import re
from datetime import date

from .db import get_db
from .errors import NotFoundError, as_date, check, like_pattern

_FACTORS = (40, 60, 80, 120, 160, 200, 240, 280)
_FACTOR_TEXT = ", ".join(map(str, _FACTORS))


def _validate_race(
    db,
    race_id,
    previous_race_id,
    edition_number,
    race_date,
    factor,
    last_factor,
    tour_year,
    position,
    championship_name,
    championship_year,
):
    check(edition_number > 0, "Edition number must be greater than 0")
    check(factor in _FACTORS, f"Factor must be one of {_FACTOR_TEXT}")
    check(last_factor is None or last_factor in _FACTORS, f"Last factor must be one of {_FACTOR_TEXT}")
    check(position is None or position > 0, "Tour position must be greater than 0")
    check((tour_year is None) == (position is None), "Tour year and position must both be set or both be empty")
    check(
        (championship_name is None) == (championship_year is None),
        "Championship name and year must both be set or both be empty",
    )

    race_day = as_date(race_date, "Race date")
    if previous_race_id is not None:
        check(previous_race_id != race_id, "A race cannot be its own previous edition")
        row = db.execute(
            "SELECT Edition_Number, Race_Date FROM Race WHERE Race_ID = %s",
            (previous_race_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError(f"Previous edition race {previous_race_id} not found")
        check(
            row["Edition_Number"] < edition_number,
            f"Edition number must be greater than the previous edition's ({row['Edition_Number']})",
        )
        check(
            as_date(row["Race_Date"]) < race_day,
            f"Race date must be after the previous edition's date ({row['Race_Date']})",
        )


def add_race(
    race_name: str,
    race_date: str,
    edition_number: int,
    factor: int,
    venue_country: str,
    venue_name: str,
    race_link: str | None = None,
    last_factor: int | None = None,
    result_link: str | None = None,
    result_link_old: str | None = None,
    category: str | None = None,
    additional_info: str | None = None,
    previous_race_id: int | None = None,
    tour_year: int | None = None,
    position: int | None = None,
    championship_name: str | None = None,
    championship_year: int | None = None,
):
    check(race_name.strip(), "Race name is required")
    with get_db() as db:
        _validate_race(
            db, None, previous_race_id, edition_number, race_date, factor, last_factor,
            tour_year, position, championship_name, championship_year,
        )
        cur = db.execute(
            """
            INSERT INTO Race
                (Race_Name, Race_Date, Edition_Number, Race_Link, Factor,
                 Last_Factor, Result_Link, Result_Link_Old, Category,
                 Additional_Info, Previous_Race_ID, Venue_Country, Venue_Name,
                 Tour_Year, Position, Championship_Name, Championship_Year)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                race_name, race_date, edition_number, race_link, factor, last_factor,
                result_link, result_link_old, category, additional_info, previous_race_id,
                venue_country, venue_name, tour_year, position, championship_name,
                championship_year,
            ),
        )
        return cur.lastrowid


def delete_race(race_id: int):
    with get_db() as db:
        db.modify("DELETE FROM Race WHERE Race_ID = %s", (race_id,), f"Race {race_id} not found")


def update_race(
    race_id: int,
    race_name: str,
    race_date: str,
    edition_number: int,
    factor: int,
    venue_country: str,
    venue_name: str,
    race_link: str | None = None,
    last_factor: int | None = None,
    result_link: str | None = None,
    result_link_old: str | None = None,
    category: str | None = None,
    additional_info: str | None = None,
    previous_race_id: int | None = None,
    tour_year: int | None = None,
    position: int | None = None,
    championship_name: str | None = None,
    championship_year: int | None = None,
):
    check(race_name.strip(), "Race name is required")
    with get_db() as db:
        _validate_race(
            db, race_id, previous_race_id, edition_number, race_date, factor, last_factor,
            tour_year, position, championship_name, championship_year,
        )
        db.modify(
            """
            UPDATE Race
               SET Race_Name = %s, Race_Date = %s, Edition_Number = %s,
                   Race_Link = %s, Factor = %s, Last_Factor = %s, Result_Link = %s,
                   Result_Link_Old = %s, Category = %s, Additional_Info = %s,
                   Previous_Race_ID = %s, Venue_Country = %s, Venue_Name = %s,
                   Tour_Year = %s, Position = %s, Championship_Name = %s,
                   Championship_Year = %s
             WHERE Race_ID = %s
            """,
            (
                race_name, race_date, edition_number, race_link, factor, last_factor,
                result_link, result_link_old, category, additional_info, previous_race_id,
                venue_country, venue_name, tour_year, position, championship_name,
                championship_year, race_id,
            ),
            f"Race {race_id} not found",
        )


def get_race(race_id: int):
    with get_db() as db:
        return db.fetch_one(
            "SELECT * FROM Race WHERE Race_ID = %s", (race_id,), f"Race {race_id} not found"
        )


# ---------------------------------------------------------------------------
# Functional requirement: race calendar (the site's "Races" page). Like the
# site it can be browsed by month; it can also be filtered by upcoming/past,
# year, country, venue, factor, tour and a word in the race or venue name.
# Each row carries the male and female winner, as on the site. LEFT JOIN and
# the sub-selects keep races that have no championship and no results yet.
# ---------------------------------------------------------------------------
_STATUSES = ("upcoming", "past")
_MONTH = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")

_WINNER = """
       (SELECT CONCAT(wm.First_Name, ' ', wm.Last_Name, ' (', wc.Country_Code, ')')
          FROM Race_Result wr
          JOIN Athletes wa ON wa.Athlete_ID   = wr.Athlete_ID
          JOIN Members  wm ON wm.Member_ID    = wa.Member_ID
          JOIN Country  wc ON wc.Country_Name = wa.Country_Name
         WHERE wr.Race_ID = r.Race_ID AND wa.Gender = '{gender}'
         ORDER BY wr.Finish_Time
         LIMIT 1)"""


def _month_range(month: str | None):
    """'2025-10' -> (date(2025,10,1), date(2025,11,1)); None -> (None, None)."""
    if month is None:
        return None, None
    m = _MONTH.match(month)
    check(m, "Month must look like YYYY-MM")
    year, mon = int(m.group(1)), int(m.group(2))
    start = date(year, mon, 1)
    end = date(year + 1, 1, 1) if mon == 12 else date(year, mon + 1, 1)
    return start, end


def list_races(
    status: str | None = None,
    year: int | None = None,
    country: str | None = None,
    factor: int | None = None,
    month: str | None = None,
    search: str | None = None,
    tour_year: int | None = None,
    venue: str | None = None,
    limit: int = 500,
):
    check(status is None or status in _STATUSES, "Status must be 'upcoming' or 'past'")
    check(factor is None or factor in _FACTORS, f"Factor must be one of {_FACTOR_TEXT}")
    check(1 <= limit <= 500, "Limit must be between 1 and 500")
    start, end = _month_range(month)
    pattern = like_pattern(search)
    # Upcoming races and tour schedules are listed soonest first, everything
    # else newest first. Only these two fixed words are ever put in the SQL.
    order = "ASC" if status == "upcoming" or tour_year is not None else "DESC"
    with get_db() as db:
        return db.fetch_all(
            f"""
            SELECT r.Race_ID, r.Race_Name, r.Race_Date, r.Edition_Number,
                   r.Factor, r.Last_Factor, r.Category,
                   v.Name AS Venue_Name, v.City, r.Venue_Country, c.Country_Code,
                   v.Number_of_Stairs,
                   r.Tour_Year, r.Position,
                   ch.Name AS Championship_Name, ch.`Level` AS Championship_Level,
                   (r.Race_Date >= CURDATE()) AS Upcoming,
                   (SELECT COUNT(*) FROM Race_Result rr WHERE rr.Race_ID = r.Race_ID) AS Finishers,
                   {_WINNER.format(gender="Male")} AS Winner_Male,
                   {_WINNER.format(gender="Female")} AS Winner_Female
              FROM Race r
              JOIN Venue   v  ON v.Country_Name = r.Venue_Country AND v.Name = r.Venue_Name
              JOIN Country c  ON c.Country_Name = r.Venue_Country
              LEFT JOIN Championship ch
                     ON ch.Name = r.Championship_Name AND ch.`Year` = r.Championship_Year
             WHERE (%s IS NULL
                    OR (%s = 'upcoming' AND r.Race_Date >= CURDATE())
                    OR (%s = 'past'     AND r.Race_Date <  CURDATE()))
               AND (%s IS NULL OR YEAR(r.Race_Date) = %s)
               AND (%s IS NULL OR r.Venue_Country = %s)
               AND (%s IS NULL OR r.Factor = %s)
               AND (%s IS NULL OR (r.Race_Date >= %s AND r.Race_Date < %s))
               AND (%s IS NULL OR r.Race_Name LIKE %s OR v.Name LIKE %s OR v.City LIKE %s)
               AND (%s IS NULL OR r.Tour_Year = %s)
               AND (%s IS NULL OR r.Venue_Name = %s)
             ORDER BY r.Race_Date {order}, r.Race_ID
             LIMIT %s
            """,
            (
                status, status, status, year, year, country, country, factor, factor,
                start, start, end, pattern, pattern, pattern, pattern,
                tour_year, tour_year, venue, venue, limit,
            ),
        )


# Months that have races, newest first -- the site's "Events by month" links.
def list_race_months():
    with get_db() as db:
        return db.fetch_all(
            """
            SELECT YEAR(Race_Date) AS `Year`, MONTH(Race_Date) AS `Month`,
                   MONTHNAME(MIN(Race_Date)) AS Month_Name, COUNT(*) AS Races
              FROM Race
             GROUP BY YEAR(Race_Date), MONTH(Race_Date)
             ORDER BY `Year` DESC, `Month` DESC
            """
        )


# ---------------------------------------------------------------------------
# Functional requirement: race page -- details, venue, distances, results
# table (by category and place, with names and nationalities) and every
# registered athlete, including those without a result.
# ---------------------------------------------------------------------------
def get_race_results(race_id: int, category: str | None = None):
    with get_db() as db:
        race = db.fetch_one(
            """
            SELECT r.*, v.City, v.Number_of_Stairs, v.Special_Info AS Venue_Info,
                   c.Country_Code, t.Tour_Name,
                   p.Race_Name AS Previous_Race_Name, p.Race_Date AS Previous_Race_Date
              FROM Race r
              JOIN Venue   v ON v.Country_Name = r.Venue_Country AND v.Name = r.Venue_Name
              JOIN Country c ON c.Country_Name = r.Venue_Country
              LEFT JOIN Tour t ON t.`Year`   = r.Tour_Year
              LEFT JOIN Race p ON p.Race_ID  = r.Previous_Race_ID
             WHERE r.Race_ID = %s
            """,
            (race_id,),
            f"Race {race_id} not found",
        )
        race["distances"] = [
            row["Distance"]
            for row in db.fetch_all(
                "SELECT Distance FROM Race_Distances_Offered WHERE Race_ID = %s ORDER BY Distance",
                (race_id,),
            )
        ]
        race["results"] = db.fetch_all(
            """
            SELECT rr.Category, rr.Place,
                   a.Athlete_ID, CONCAT(m.First_Name, ' ', m.Last_Name) AS Athlete_Name,
                   a.Gender, c.Country_Code, a.Country_Name,
                   CAST(rr.Finish_Time AS CHAR) AS Finish_Time,
                   rr.Points
              FROM Race_Result rr
              JOIN Athletes a ON a.Athlete_ID   = rr.Athlete_ID
              JOIN Members  m ON m.Member_ID    = a.Member_ID
              JOIN Country  c ON c.Country_Name = a.Country_Name
             WHERE rr.Race_ID = %s
               AND (%s IS NULL OR rr.Category = %s)
             ORDER BY rr.Category, rr.Place
            """,
            (race_id, category, category),
        )
        # Winner per gender (fastest time) and the category list are taken
        # from all results, so they do not change with the category filter.
        winners = db.fetch_all(
            """
            SELECT a.Gender, a.Athlete_ID,
                   CONCAT(m.First_Name, ' ', m.Last_Name) AS Athlete_Name,
                   c.Country_Code, CAST(rr.Finish_Time AS CHAR) AS Finish_Time
              FROM Race_Result rr
              JOIN Athletes a ON a.Athlete_ID   = rr.Athlete_ID
              JOIN Members  m ON m.Member_ID    = a.Member_ID
              JOIN Country  c ON c.Country_Name = a.Country_Name
             WHERE rr.Race_ID = %s
               AND rr.Finish_Time = (SELECT MIN(x.Finish_Time)
                                       FROM Race_Result x
                                       JOIN Athletes xa ON xa.Athlete_ID = x.Athlete_ID
                                      WHERE x.Race_ID = rr.Race_ID AND xa.Gender = a.Gender)
            """,
            (race_id,),
        )
        race["winners"] = {row["Gender"]: row for row in winners}
        race["categories"] = [
            row["Category"]
            for row in db.fetch_all(
                "SELECT DISTINCT Category FROM Race_Result WHERE Race_ID = %s ORDER BY Category",
                (race_id,),
            )
        ]
        race["participants"] = db.fetch_all(
            """
            SELECT a.Athlete_ID, CONCAT(m.First_Name, ' ', m.Last_Name) AS Athlete_Name,
                   a.Gender, c.Country_Code,
                   (rr.Athlete_ID IS NOT NULL) AS Has_Result
              FROM Participates_In pi
              JOIN Athletes a ON a.Athlete_ID   = pi.Athlete_ID
              JOIN Members  m ON m.Member_ID    = a.Member_ID
              JOIN Country  c ON c.Country_Name = a.Country_Name
              LEFT JOIN Race_Result rr
                     ON rr.Athlete_ID = pi.Athlete_ID AND rr.Race_ID = pi.Race_ID
             WHERE pi.Race_ID = %s
             ORDER BY m.Last_Name, m.First_Name
            """,
            (race_id,),
        )
        return race


# ---------------------------------------------------------------------------
# Functional requirement: all editions of a race. Walks the recursive
# PREVIOUS_EDITION relationship backwards and forwards from any edition and
# lists the winner(s) of each.
# ---------------------------------------------------------------------------
def get_race_editions(race_id: int):
    with get_db() as db:
        db.fetch_one("SELECT 1 FROM Race WHERE Race_ID = %s", (race_id,), f"Race {race_id} not found")
        return db.fetch_all(
            """
            WITH RECURSIVE
              earlier AS (
                SELECT Race_ID, Previous_Race_ID FROM Race WHERE Race_ID = %s
                UNION ALL
                SELECT r.Race_ID, r.Previous_Race_ID
                  FROM Race r JOIN earlier e ON r.Race_ID = e.Previous_Race_ID
              ),
              later AS (
                SELECT Race_ID FROM Race WHERE Race_ID = %s
                UNION ALL
                SELECT r.Race_ID
                  FROM Race r JOIN later l ON r.Previous_Race_ID = l.Race_ID
              )
            SELECT r.Race_ID, r.Race_Name, r.Race_Date, r.Edition_Number, r.Factor,
                   r.Previous_Race_ID,
                   GROUP_CONCAT(
                     CONCAT(m.First_Name, ' ', m.Last_Name, ' (', c.Country_Code, ', ',
                            CAST(rr.Finish_Time AS CHAR), ')')
                     ORDER BY rr.Category SEPARATOR '; '
                   ) AS Winners
              FROM Race r
              LEFT JOIN Race_Result rr ON rr.Race_ID = r.Race_ID AND rr.Place = 1
              LEFT JOIN Athletes a ON a.Athlete_ID   = rr.Athlete_ID
              LEFT JOIN Members  m ON m.Member_ID    = a.Member_ID
              LEFT JOIN Country  c ON c.Country_Name = a.Country_Name
             WHERE r.Race_ID IN (SELECT Race_ID FROM earlier
                                 UNION
                                 SELECT Race_ID FROM later)
             GROUP BY r.Race_ID, r.Race_Name, r.Race_Date, r.Edition_Number, r.Factor,
                      r.Previous_Race_ID
             ORDER BY r.Edition_Number
            """,
            (race_id, race_id),
        )
