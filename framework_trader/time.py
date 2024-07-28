import pendulum


def now(tz: str | pendulum.Timezone = None) -> pendulum.DateTime:
    return pendulum.now(tz=tz)


def past(
    years: int | None = 0,
    months: int | None = 0,
    weeks: int | None = 0,
    days: int | None = 0,
    hours: int | None = 0,
    minutes: int | None = 0,
    seconds: float | None = 0,
    microseconds: int | None = 0,
    tz: pendulum.Timezone | None = None,
) -> pendulum.DateTime:
    return pendulum.now(tz=tz).subtract(
        years=years,
        months=months,
        weeks=weeks,
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        microseconds=microseconds,
    )


def future(
    years: int | None = 0,
    months: int | None = 0,
    weeks: int | None = 0,
    days: int | None = 0,
    hours: int | None = 0,
    minutes: int | None = 0,
    seconds: float | None = 0,
    microseconds: int | None = 0,
    tz: pendulum.Timezone | None = None,
) -> pendulum.DateTime:
    return pendulum.now(tz=tz).add(
        years=years,
        months=months,
        weeks=weeks,
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        microseconds=microseconds,
    )
