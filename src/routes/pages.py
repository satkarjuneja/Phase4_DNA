"""Server-rendered pages, modelled on towerrunning.com.

Every page reads through the same database_api functions as the JSON API.
Create/update/delete actions on the pages call the JSON API (static/app.js).
"""

from datetime import date
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from database_api import (
    athletes,
    championship,
    country,
    news,
    race,
    statistics,
    team,
    tour,
    twa_ranking,
    venue,
)
from database_api.errors import AppError, ValidationError

router = APIRouter(include_in_schema=False)

templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")
templates.env.filters["dmy"] = lambda d: d.strftime("%d.%m.%Y") if d else ""
templates.env.filters["longdate"] = lambda d: d.strftime("%B %-d, %Y") if d else ""
templates.env.filters["mon"] = lambda d: d.strftime("%b %Y") if d else ""
templates.env.filters["day"] = lambda d: d.strftime("%d") if d else ""
templates.env.filters["pts"] = lambda x: "" if x is None else f"{float(x):.2f}"
templates.env.filters["mmss"] = lambda t: (t[3:] if t and t.startswith("00:") else t) or ""

NEWS_PER_PAGE = 5
FACTORS = (40, 60, 80, 120, 160, 200, 240, 280)


def render(request: Request, name: str, status_code: int = 200, **context):
    """Render a template; adds the tours needed by the menu on every page."""
    try:
        context["nav_tours"] = tour.list_tours()
    except AppError:
        context["nav_tours"] = []  # database down: still show the error page
    context.setdefault("today", date.today())
    return templates.TemplateResponse(request, name, context, status_code=status_code)


def _text(value: str | None):
    """Empty form fields arrive as '' -- treat them as 'no filter'."""
    return value.strip() if value and value.strip() else None


def _int(value: str | None, field: str):
    value = _text(value)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        raise ValidationError(f"{field} must be a whole number")


def _race_form_lookups():
    return {
        "venues": venue.list_venues(),
        "tours": tour.list_tours(),
        "championships": championship.list_championships(),
        "factors": FACTORS,
    }


# --------------------------------------------------------------------- Home
@router.get("/")
def home(request: Request):
    return render(
        request,
        "home.html",
        title="Home",
        posts=news.list_news(limit=NEWS_PER_PAGE),
        upcoming=race.list_races(status="upcoming", limit=4),
        top_men=twa_ranking.get_ranking_table("Male", limit=3),
        top_women=twa_ranking.get_ranking_table("Female", limit=3),
    )


# -------------------------------------------------------------------- Races
@router.get("/races")
def races(
    request: Request,
    month: str | None = None,
    status: str | None = None,
    country_name: str | None = None,
    factor: str | None = None,
):
    month, status, country_name = _text(month), _text(status), _text(country_name)
    factor_value = _int(factor, "Factor")
    # Like the site: with no filter chosen, show the upcoming races
    if not (month or status or country_name or factor_value):
        status = "upcoming"
    rows = race.list_races(
        status=None if status == "all" else status,
        country=country_name,
        factor=factor_value,
        month=month,
    )
    return render(
        request,
        "races.html",
        title="Races",
        races=rows,
        months=race.list_race_months(),
        countries=country.list_countries(),
        f={"month": month, "status": status, "country_name": country_name, "factor": factor_value},
        **_race_form_lookups(),
    )


@router.get("/races/{race_id}")
def race_page(request: Request, race_id: int, category: str | None = None):
    data = race.get_race_results(race_id, _text(category))
    return render(
        request,
        "race.html",
        title=data["Race_Name"],
        race=data,
        editions=race.get_race_editions(race_id),
        category=_text(category),
        all_athletes=athletes.search_athletes(),
        **_race_form_lookups(),
    )


# ------------------------------------------------------------------ Ranking
@router.get("/ranking")
def ranking(request: Request, tab: str = "Male", country_name: str | None = None):
    country_name = _text(country_name)
    if tab == "Nations":
        rows, nations = [], statistics.get_country_standings()
    else:
        rows, nations = twa_ranking.get_ranking_table(tab, country_name), []
    return render(
        request,
        "ranking.html",
        title="Ranking",
        tab=tab,
        rows=rows,
        nations=nations,
        country_name=country_name,
        countries=country.list_countries(),
    )


# ------------------------------------------------------------------ Members
@router.get("/members")
def members(
    request: Request,
    search: str | None = None,
    country_name: str | None = None,
    gender: str | None = None,
):
    search, country_name, gender = _text(search), _text(country_name), _text(gender)
    return render(
        request,
        "members.html",
        title="Members",
        athletes=athletes.search_athletes(search, country_name, gender),
        countries=country.list_countries(),
        f={"search": search, "country_name": country_name, "gender": gender},
    )


@router.get("/members/{athlete_id}")
def member_page(request: Request, athlete_id: str):
    profile = athletes.get_athlete_profile(athlete_id)
    return render(
        request,
        "member.html",
        title=f"{profile['First_Name']} {profile['Last_Name']}",
        a=profile,
    )


# --------------------------------------------------------------------- News
@router.get("/news")
def news_list(
    request: Request,
    category: str | None = None,
    search: str | None = None,
    page: int = 1,
):
    category, search = _text(category), _text(search)
    page = max(page, 1)
    total = news.count_news(category, search)
    return render(
        request,
        "news.html",
        title="News",
        posts=news.list_news(category, search, NEWS_PER_PAGE, (page - 1) * NEWS_PER_PAGE),
        categories=news.list_categories(),
        authors=team.list_team(),
        category=category,
        search=search,
        page=page,
        pages=max(1, -(-total // NEWS_PER_PAGE)),
        total=total,
    )


@router.get("/news/{member_id}/{news_date}/{title:path}")
def news_post(request: Request, member_id: int, news_date: date, title: str):
    post = news.get_news_post(member_id, news_date, title)
    return render(request, "news_post.html", title=post["Title"], post=post)


# --------------------------------------------------------------- Statistics
@router.get("/statistics")
def statistics_page(request: Request, level: str | None = None):
    level = _text(level)
    return render(
        request,
        "statistics.html",
        title="Statistics",
        championships=championship.list_championships(level),
        nations=statistics.get_country_standings(),
        level=level,
    )


# --------------------------------------------------------------------- Team
@router.get("/team")
def team_page(request: Request):
    return render(request, "team.html", title="Team", team=team.list_team())


# --------------------------------------------------------------------- Tour
@router.get("/tour/{year}")
def tour_page(request: Request, year: int):
    info = tour.get_tour(year)
    return render(
        request,
        "tour.html",
        title=info["Tour_Name"],
        tour=info,
        races=race.list_races(tour_year=year),
    )


# -------------------------------------------------------------------- Venue
@router.get("/venues/{country_name}/{name:path}")
def venue_page(request: Request, country_name: str, name: str):
    info = venue.get_venue(country_name, name)
    return render(
        request,
        "venue.html",
        title=info["Name"],
        venue=info,
        races=race.list_races(country=country_name, venue=name),
    )


# ------------------------------------------------------------------- Search
@router.get("/search")
def search_page(request: Request, q: str | None = None):
    q = _text(q)
    return render(
        request,
        "search.html",
        title="Search",
        q=q,
        races=race.list_races(search=q) if q else [],
        posts=news.list_news(search=q, limit=20) if q else [],
        athletes=athletes.search_athletes(q) if q else [],
    )
