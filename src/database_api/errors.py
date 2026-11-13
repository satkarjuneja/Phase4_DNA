"""Application errors and translation of MySQL errors into readable messages.

Every error raised by the data layer ends up as one of the AppError
subclasses below. app.py turns them into JSON responses of the form
{"detail": "<message>"} with the matching HTTP status code.
"""

import re
from datetime import date

import pymysql


class AppError(Exception):
    status_code = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    """Input breaks a business rule (bad format, out of range, ...)."""

    status_code = 400


class NotFoundError(AppError):
    """The requested or referenced record does not exist."""

    status_code = 404


class ConflictError(AppError):
    """The change clashes with existing data (duplicate key, row in use)."""

    status_code = 409


class DatabaseUnavailableError(AppError):
    status_code = 503


def check(condition, message: str):
    """Raise ValidationError(message) when condition is false.

    Used instead of `assert`, which is stripped when Python runs with -O
    and gives no message to the client.
    """
    if not condition:
        raise ValidationError(message)


def as_date(value, field: str = "date") -> date:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field} must be a date in YYYY-MM-DD format, got {value!r}")


def like_pattern(term: str | None):
    """LIKE pattern for a search word, or None when there is no word.

    The user's own % and _ are escaped so they are matched literally.
    """
    if term is None or not term.strip():
        return None
    escaped = term.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


# ---------------------------------------------------------------------------
# Translating MySQL errors
# ---------------------------------------------------------------------------

# CHECK constraints from schema.sql
_CHECK_MESSAGES = {
    "ck_country_code": "Country code must be exactly three capital letters (e.g. AUT)",
    "ck_tour_year": "Tour year must be a four-digit year",
    "ck_champ_year": "Championship year must be a four-digit year",
    "ck_stat_rank": "Statistics rank must be greater than 0",
    "ck_stat_score": "Statistics score cannot be negative",
    "ck_rank_pos": "Ranking position must be greater than 0",
    "ck_rank_score": "Ranking score cannot be negative",
    "ck_rank_last": "Last score cannot be negative",
    "ck_rank_tour": "Tour points cannot be negative",
    "ck_athlete_id": "Athlete ID must look like POL1985M001 (country code, birth year, M/F, 3 digits)",
    "ck_athlete_email": "Email address is not valid",
    "ck_athlete_phone": "Phone number must start with + followed by 7 to 15 digits",
    "ck_athlete_dob": "Date of birth must be after 1900-01-01",
    "ck_venue_stairs": "Number of stairs must be greater than 0",
    "ck_race_edition": "Edition number must be greater than 0",
    "ck_race_factor": "Factor must be one of 40, 60, 80, 120, 160, 200, 240, 280",
    "ck_race_lastfac": "Last factor must be one of 40, 60, 80, 120, 160, 200, 240, 280",
    "ck_race_position": "Tour position must be greater than 0",
    "ck_result_place": "Place must be greater than 0",
    "ck_result_points": "Points cannot be negative",
}

# UNIQUE / PRIMARY keys: MySQL reports them as '<Table>.<key>'
_DUPLICATE_MESSAGES = {
    "Country.PRIMARY": "A country with this name already exists",
    "Country.uq_country_code": "Another country already uses this country code",
    "Tour.PRIMARY": "A tour for this year already exists",
    "Championship.PRIMARY": "This championship already exists for that year",
    "Athletes.PRIMARY": "An athlete with this Athlete ID already exists",
    "Athletes.uq_athlete_member": "This member is already registered as an athlete",
    "Athletes.uq_athlete_email": "Another athlete already uses this email address",
    "Athletes.uq_athlete_phone": "Another athlete already uses this phone number",
    "Team.PRIMARY": "This member is already a team member",
    "Team_Social_Media.PRIMARY": "This social media handle is already listed for the team member",
    "Venue.PRIMARY": "A venue with this name already exists in that country",
    "News.PRIMARY": "This author already posted news with the same date and title",
    "Race.uq_race_previous": "That previous edition is already linked to another race",
    "Race.uq_race_tour_position": "Another race already holds this position in the tour",
    "Race_Distances_Offered.PRIMARY": "This distance is already listed for the race",
    "Participates_In.PRIMARY": "The athlete is already registered for this race",
    "Ranked_In.PRIMARY": "The athlete is already linked to this ranking",
    "Race_Result.PRIMARY": "The athlete already has a result for this race",
    "Race_Result.uq_result_place": "Another athlete already holds this place in this race and category",
    "Appeared_In.PRIMARY": "This appearance is already recorded",
}

# Foreign keys: (message when the parent row is missing,
#                message when a parent row is still referenced)
_FK_MESSAGES = {
    "fk_stat_country": ("Country does not exist", "Country still has statistics"),
    "fk_ranking_country": ("Country does not exist", "Country still has TWA ranking entries"),
    "fk_athlete_member": ("Member does not exist", "Member is still an athlete"),
    "fk_athlete_country": ("Country does not exist", "Country still has athletes"),
    "fk_team_member": ("Member does not exist", "Member is still a team member"),
    "fk_team_country": ("Country does not exist", "Country is still represented by team members"),
    "fk_tsm_team": ("Team member does not exist", "Team member still has social media handles"),
    "fk_venue_country": ("Country does not exist", "Country still has venues"),
    "fk_news_team": ("Author is not a team member", "Team member still has news posts"),
    "fk_race_previous": ("Previous edition race does not exist", "Race is the previous edition of another race"),
    "fk_race_venue": ("Venue does not exist in that country", "Venue still hosts races"),
    "fk_race_tour": ("Tour year does not exist", "Tour still has races"),
    "fk_race_champ": ("Championship does not exist", "Championship still has races"),
    "fk_rdo_race": ("Race does not exist", "Race still has distances"),
    "fk_pi_athlete": ("Athlete does not exist", "Athlete is still registered for races"),
    "fk_pi_race": ("Race does not exist", "Race still has participants"),
    "fk_ri_athlete": ("Athlete does not exist", "Athlete is still ranked"),
    "fk_ri_ranking": ("TWA ranking entry does not exist", "Ranking entry still has athletes"),
    "fk_rr_athlete": ("Athlete does not exist", "Athlete still has race results"),
    "fk_rr_race": ("Race does not exist", "Race still has results"),
    "fk_ai_result": ("Athlete has no result for this race", "Race result is still used by statistics"),
    "fk_ai_stat": ("Statistics entry does not exist", "Statistics entry still has appearances"),
}

# MySQL error codes
ER_DUP_ENTRY = 1062
ER_BAD_NULL = 1048
ER_ROW_IS_REFERENCED = 1451
ER_NO_REFERENCED_ROW = 1452
ER_DATA_TOO_LONG = 1406
ER_TRUNCATED_WRONG_VALUE = 1292
ER_WARN_DATA_OUT_OF_RANGE = 1264
ER_WRONG_VALUE_FOR_FIELD = 1366
ER_DATA_TRUNCATED = 1265
ER_SIGNAL_EXCEPTION = 1644  # SIGNAL SQLSTATE '45000' from our triggers
ER_CHECK_CONSTRAINT_VIOLATED = 3819  # MySQL 8
ER_CONSTRAINT_FAILED = 4025  # MariaDB equivalent of 3819


def _constraint_name(message: str):
    m = re.search(r"CONSTRAINT `([^`]+)`", message)
    return m.group(1) if m else None


def _duplicate_message(message: str) -> str:
    # MySQL 8 names the key 'Table.key'; MariaDB gives only 'key'
    m = re.search(r"for key '([^']+)'", message)
    key = m.group(1) if m else ""
    if key in _DUPLICATE_MESSAGES:
        return _DUPLICATE_MESSAGES[key]
    if key != "PRIMARY":
        for full_key, text in _DUPLICATE_MESSAGES.items():
            if full_key.endswith("." + key):
                return text
    return "This record already exists"


def translate_mysql_error(exc: pymysql.err.MySQLError) -> AppError:
    """Map a PyMySQL exception to an AppError with a readable message."""
    code = exc.args[0] if exc.args else None
    message = exc.args[1] if len(exc.args) > 1 else str(exc)

    if code == ER_SIGNAL_EXCEPTION:
        # Message text comes straight from the trigger (schema.sql)
        return ValidationError(message)

    if code in (ER_CHECK_CONSTRAINT_VIOLATED, ER_CONSTRAINT_FAILED):
        # MySQL: "Check constraint 'ck_x' is violated."
        # MariaDB: "CONSTRAINT `ck_x` failed for `db`.`table`"
        m = re.search(r"Check constraint '([^']+)'", message)
        name = m.group(1) if m else _constraint_name(message)
        return ValidationError(_CHECK_MESSAGES.get(name, f"Invalid value ({name or message})"))

    if code == ER_DUP_ENTRY:
        return ConflictError(_duplicate_message(message))

    if code == ER_NO_REFERENCED_ROW:
        missing, _ = _FK_MESSAGES.get(_constraint_name(message), ("Referenced record does not exist", None))
        return NotFoundError(missing)

    if code == ER_ROW_IS_REFERENCED:
        _, in_use = _FK_MESSAGES.get(_constraint_name(message), (None, "Record is still referenced by other data"))
        return ConflictError(f"Cannot delete or change this record: {in_use.lower()}")

    if code == ER_BAD_NULL:
        m = re.search(r"Column '([^']+)'", message)
        return ValidationError(f"{m.group(1) if m else 'A required field'} is required")

    if code == ER_DATA_TOO_LONG:
        m = re.search(r"column '([^']+)'", message)
        return ValidationError(f"Value for {m.group(1) if m else 'a field'} is too long")

    if code in (ER_TRUNCATED_WRONG_VALUE, ER_WRONG_VALUE_FOR_FIELD, ER_DATA_TRUNCATED, ER_WARN_DATA_OUT_OF_RANGE):
        return ValidationError(f"Invalid value: {message}")

    if isinstance(exc, pymysql.err.OperationalError) and code in (2002, 2003, 2006, 2013, 1045, 1049):
        return DatabaseUnavailableError(f"Database is unavailable: {message}")

    err = AppError(f"Database error: {message}")
    err.status_code = 500
    return err
