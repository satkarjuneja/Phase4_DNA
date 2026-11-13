# Tower Running – Project Phase 4 (Team 42)

A populated MySQL database and a web application for our Mini World, **Tower Running**,
modelled on [towerrunning.com](https://www.towerrunning.com/) (Towerrunning World Association:
stair races, the Towerrunning Tour, the TWA world ranking, news and team).

## 1. Paradigm and stack

| Part | Choice |
|---|---|
| Paradigm / DBMS | Relational – **MySQL 8.0+** (InnoDB, utf8mb4). `schema.sql` uses `REGEXP_LIKE`, CHECK constraints, generated columns and window functions, so MySQL 8.0.16 or newer is required. |
| Query language | Raw SQL strings with `%s` parameters. No ORM or query builder. |
| Python driver | **PyMySQL 1.2.4** |
| Backend | **Python 3.13**, **FastAPI 0.162.5** (served by uvicorn) |
| Frontend | Server-rendered **Jinja2** templates, plain CSS, and a small plain-JavaScript file. No frontend framework and no build step. |

The browser only talks to the Python backend. Pages are rendered by the backend; forms and
buttons call the backend's JSON API under `/api/...`; only the backend talks to MySQL.

## 2. Design Changes

Our Mini World was modelled by **Team 38 in Phase 2** (EER) and **Team 29 in Phase 3**
(relational schema, normalised to 3NF). We used the Phase 3 schema as the baseline and changed
the following. The tags `[REV-n]` also appear as comments in `src/schema.sql`.

| # | Change to the Phase 3 design | Reason |
|---|---|---|
| REV-1 | `Country` gets a new attribute `Country_Code CHAR(3)`, UNIQUE. | The Athlete ID starts with a three-letter country code (Phase 1 rule); with only `Country_Name` that rule could not be checked. |
| REV-2 | Table `Postal_Code_Directory` removed; `City` is stored in `Athletes` and `Venue` again. | Postal codes are not unique across countries, so `Postal_Code → City` does not hold worldwide; the table also forced a postal code for venues that publish none. |
| REV-3 | `Athletes` primary key is `Athlete_ID` (Phase 3: `Member_ID`). `Member_ID` stays as a UNIQUE NOT NULL foreign key. | Phase 1 defines `Athlete_ID` as the identifier of an athlete, and the Phase 3 tables `Participates_In`, `Ranked_In` and `Race_Result` already reference it. |
| REV-4 | `Race.Info_Part_1` and `Info_Part_2` merged into one nullable `Additional_Info`. | The two parts were placeholders invented in Phase 2; the website has a single "Additional Info" field. |
| REV-5 | `TWA_Ranking` gets a surrogate key `Ranking_ID` (Phase 3 key: `Country`). `Lat` renamed `Last_Score`, `Tour` renamed `Tour_Points`. `Ranked_In` references `Ranking_ID`. | With `Country` as key only one ranking row per country could exist, so male and female rankings, or two athletes of one country, could not be stored. `Lat` was a typo for "Last" in Phase 1. |
| REV-5b | `TWA_Ranking.Dev` and `Total` are generated columns (`Score − Last_Score`, `Races + Tour_Points`). | Phase 1 defines both as computed values; generating them removes the update anomaly noted in Phase 2. `Total` was dropped in Phase 3 and is restored. |
| REV-6 | CHECK constraints and triggers added: Athlete ID format and agreement with country code, birth year and gender; date of birth in the past; factor in the allowed set; disjoint `Athletes`/`Team` specialisation; previous edition must be earlier and have a smaller edition number; tour year and position set together; championship name and year set together; no result for a race in the future; a result implies a `Participates_In` row; `Country_Code` cannot change. | Restores the integrity rules of Phase 1 (Tables 3 and 4) that a plain relational mapping cannot express. |
| REV-7 | `FLOAT` replaced by `DECIMAL` for scores and points. | Points are exact values such as 133.33; floating point gives rounding differences in sums and comparisons. |
| REV-8 | `Athletes.Email_Address` and `Phone_Number` are NOT NULL as well as UNIQUE. | Both are alternate keys in Phase 2/3, and registration on the site requires them. |
| – | `Statistics.Rank` renamed `Stat_Rank`; `TWA_Ranking.D+-` named `D_Plus_Minus`. | `RANK` is a reserved word in MySQL 8; `D+-` is not a valid column name. |
| – | `Race.Previous_Race_ID` is UNIQUE; `(Tour_Year, Position)` is UNIQUE; `Race_Result (Race_ID, Category, Place)` is UNIQUE. | PREVIOUS_EDITION is 1:1 in the EER; a tour position and a place in a category can each be taken once. |
| – | Referential actions chosen per relationship (see `schema.sql`): deleting a race or an athlete cascades to results, registrations and ranking links; deleting a country, venue, tour or championship that is still in use is refused (RESTRICT); deleting the previous edition of a race sets the link to NULL. | Phase 3 did not specify ON DELETE / ON UPDATE behaviour. |

Unchanged from Phase 3: all other relations, including the decomposition of the ternary
APPEARED_IN into `Race_Result` and `Appeared_In`.

## 3. Setup and run

Requirements: MySQL 8.0+, Python 3.13 (3.10 or newer should work), pip.

```bash
cd src

# 1. Create and fill the database (drops and recreates the database tower_running)
mysql -u <user> -p < schema.sql
mysql -u <user> -p < populate.sql

# 2. Install the Python dependencies
pip install -r requirements.txt

# 3. Tell the application how to reach MySQL (defaults shown)
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=<your password>
export MYSQL_DATABASE=tower_running

# 4. Start the application
uvicorn app:app --port 8000
```

Open **http://localhost:8000**. There is no frontend install or build step.

To see the add / edit / delete controls, tick **Admin mode** in the top-right corner of any
page (there is no login; the switch only keeps the public pages looking like the original site).

Data: `populate.sql` holds data taken from towerrunning.com in November 2026 (races, venues,
results, team, news, championships, tours). Its header lists the few values the site does not
publish (athlete birth dates, e-mails, phone numbers), which are clearly synthetic.

## 4. Schema Mapping

Not applicable: the implementation is relational (MySQL), like the Phase 3 schema.

## 5. Features

Every feature runs raw, parameterised SQL in the Python backend (`src/database_api/`).
The list is in the order of the video demonstration.

### Queries (read)

1. **News feed** – Home page (`/`) and News page (`/news`). Lists news posts, newest first, with
   author name and role (News ⋈ Team ⋈ Members). On `/news`, click a category in the sidebar
   (`?category=Announcement`), type a word in "Search news" (`?search=Faber`), or use the page
   numbers (`?page=2`). Click a title to open the post.
2. **Race calendar** – Races page (`/races`). Shows upcoming races by default, each with venue,
   city, country, stairs, factor and male/female winner. Click a month under "Events by month"
   (`?month=2025-10`) or use the filter bar: Upcoming/Past/All, month, country, factor.
3. **Race page with results** – click any race (`/races/14`). Shows the race details, venue,
   distances, the results table with athlete names and countries (Race_Result ⋈ Athletes ⋈
   Members ⋈ Country) and the registered athletes, including those without a result. Click a
   category tab (`?category=Women Open`) to show one category.
4. **All editions of a race** – "All editions" box on a race page. Follows the recursive
   previous-edition relationship backwards and forwards (recursive CTE) and lists every edition
   with its winners. "Previous edition" in the details links to the earlier race.
5. **TWA ranking** – Ranking page (`/ranking`). Tabs Males / Females show the ranking table with
   athlete names (TWA_Ranking ⋈ Ranked_In ⋈ Athletes ⋈ Members); the country dropdown limits it
   to one country (`?tab=Male&country_name=China`). The home page shows the top 3 of each.
6. **Nations table** – Ranking page, tab Nations (`/ranking?tab=Nations`), also on Statistics.
   Per country: athletes, results, gold/silver/bronze places and total points, ranked with
   `RANK()`. Countries whose athletes have no results appear with 0 points.
7. **Athlete search** – Members page (`/members`). Search by name or Athlete ID, filter by
   country and gender. Each row shows age (computed from date of birth), races, wins, podiums
   and points; athletes without results are included.
8. **Athlete profile** – click an athlete anywhere (`/members/JPN1989M001`). Personal data with
   derived age, all race results, and races the athlete is registered for without a result.
9. **Championships by year** – Statistics page (`/statistics`). Championships with the race each
   was held at; championships whose race is not in the database are still listed. Tabs filter
   by level (`?level=World`).
10. **Team** – Team page (`/team`). Presidium and national association representatives with
    country, description, social media links and number of news posts.
11. **Tour** – menu Tour → a year (`/tour/2026`). The races of that tour in order, with winners.
    A tour without races (2021) shows an empty list.
12. **Venue** – click a venue name on a race (`/venues/Austria/DC Tower`). Venue details and the
    races held there.
13. **Site search** – search box in the header (`/search?q=taipei`). Finds races (by race, venue
    or city name), athletes and news containing the word.

### Updates (write) – tick "Admin mode" first

14. **Register an athlete (create)** – Members page, form "Register" at the bottom. Inserts the
    `Members` row and the `Athletes` row in one transaction. Errors are shown in a banner, e.g.
    an Athlete ID that does not match country, birth year and gender, or a duplicate e-mail.
15. **Edit an athlete (update)** – athlete page → "Edit profile". Updates name (`Members`) and
    contact details and address (`Athletes`).
16. **Add a race (create)** – Races page → "Add a race". Inserts into `Race`; rejected with a
    message if the venue does not exist, the tour position is taken, or the factor is invalid.
17. **Edit a race (update)** – race page → "Edit race".
18. **Register an athlete for a race (create) / remove (delete)** – race page → "Register an
    athlete for this race"; "remove" next to a registered athlete. Table `Participates_In`.
19. **Add a result (create)** – race page → "Add a result". Inserts into `Race_Result`; refused
    for a race in the future or a place already taken in that category.
20. **Edit a result (update) / delete a result (delete)** – "Edit" and "Delete" in the Admin
    column of the results table.
21. **Edit a ranking entry (update)** – Ranking page → "Edit" in a row. `Dev` and `Total` are
    recomputed by the database.
22. **Write a news post (create)** – News page → "Write a news post".
23. **Edit a news post (update) / delete it (delete)** – open the post → "Edit post" / "Delete post".
24. **Delete a race (delete)** – race page → "Delete race". Its results, registrations and
    distances are deleted with it (ON DELETE CASCADE).
25. **Delete an athlete (delete)** – athlete page → "Delete athlete". Removes the member, the
    athlete and, by cascade, the athlete's results, registrations and ranking links.

### Errors

Constraint violations, missing records and invalid input are shown as a red banner on the page
(for form actions) or as an error page (for URLs). Examples: opening `/races/999` ("Race 999
not found"); adding a result with a place that is already taken; deleting a country that still
has athletes through the API (`DELETE /api/country/Austria` → 409 "country still has athletes").

## 6. Source layout

```
src/
  schema.sql, populate.sql   database scripts
  app.py                     FastAPI entry point, error handling
  database_api/              all SQL (one module per table) + db.py (connection), errors.py
  routes/                    JSON API routes (/api/...) and pages.py (HTML pages)
  base_models/               request bodies of the JSON API
  templates/, static/        Jinja2 templates, style.css, app.js
  requirements.txt
```

The JSON API also offers create/read/update/delete for every table; interactive documentation
is at `http://localhost:8000/docs`.
