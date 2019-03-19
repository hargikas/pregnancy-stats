import calendar
import datetime
import math
import shutil
import time

import zodiac_sign
from progress.bar import ShadyBar


def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(math.floor(n/10) % 10 != 1)*(n % 10 < 4)*n % 10::4])


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def add_years(sourcedate, years):
    new_year = sourcedate.year + years
    try:
        return sourcedate.replace(year=new_year)
    except ValueError:
        # Leap day
        if (sourcedate.month == 2 and sourcedate.day == 29 and calendar.isleap(sourcedate.year) and not calendar.isleap(new_year)):
            return sourcedate.replace(year=new_year, day=28)
        raise


def fuzzy_delivery_date(last_period):
    min_weeks = 37
    max_weeks = 42

    min_delivery = last_period + datetime.timedelta(weeks=min_weeks)
    max_delivery = last_period + datetime.timedelta(weeks=max_weeks)

    return [min_delivery, max_delivery]


def naegele_due_date(last_period):
    # Naegele’s rule (for 28 days period)
    # https://www.healthline.com/health/pregnancy/what-is-gestation#calculate-a-due-date
    # https://www.healthline.com/health/pregnancy/your-due-date#1
    due_date = last_period + datetime.timedelta(days=7)
    due_date = add_months(due_date, -3)
    due_date = add_years(due_date, 1)
    return due_date


def find_start_of_gestation(a_date, age):
    return a_date - age


if __name__ == '__main__':
    screen_line = (shutil.get_terminal_size()[0]-1)*"-"

    # Σταθερές που γνωρίζουμε για την εγκυμοσύνη
    last_period = datetime.date(year=2019, month=1, day=19)
    conception_min = datetime.date(year=2019, month=1, day=26)
    conception_max = datetime.date(year=2019, month=2, day=5)

    # 3/4/2019 Επίσκεψη γιατρού me πρώτη εκτίμηση και εκτύπωση σε χαρτί
    # Εκτίμηση γιατρού
    estimations = [
        (datetime.date(year=2019, month=3, day=4),
         datetime.timedelta(weeks=5, days=6)),
        (datetime.date(year=2019, month=3, day=16),
         datetime.timedelta(weeks=8, days=0)),
    ]

    possible_start_gestation = [find_start_of_gestation(
        a_date, age) for a_date, age in estimations]

    print("Doctor’s estimates for the start of the pregnacy (gestation):")
    for i, doctors_conception in enumerate(possible_start_gestation):
        print("\t%s estimate:" % (ordinal(i+1)), doctors_conception)
    print(screen_line)

    gestational_age = datetime.date.today() - last_period
    doctors_age = datetime.date.today() - possible_start_gestation[-1]
    fetal_age_min = datetime.date.today() - conception_max
    fetal_age_max = datetime.date.today() - conception_min
    fetal_age_aprox = gestational_age - datetime.timedelta(weeks=2)
    fetal_age_doctors = doctors_age - datetime.timedelta(weeks=2)

    print("Gestational Age:")
    print("\tGestational age (calculated from last period) (Weeks, Days):",
          divmod(gestational_age.days, 7))
    print("\tDoctor’s last estimate of gestational age (Weeks, Days):",
          divmod(doctors_age.days, 7))
    print("Fetal Age:")
    print("\tMax fetal age (Weeks, Days):", divmod(fetal_age_max.days, 7))
    print("\tMin fetal age (Weeks, Days):", divmod(fetal_age_min.days, 7))
    print("\tApproximation of fetal age based on period (Week, Days):",
          divmod(fetal_age_aprox.days, 7))
    print("\tApproximation of fetal age based on doctor’s last estimate (Week, Days):",
          divmod(fetal_age_doctors.days, 7))
    print(screen_line)

    delivery_dates = ["%s %s [%s]" % (dt.strftime("%A"), dt.isoformat(
    ), zodiac_sign.get_zodiac_sign(dt)) for dt in fuzzy_delivery_date(last_period)]
    naegele_date = naegele_due_date(last_period)
    # My prognosis
    harrys_date = naegele_due_date(possible_start_gestation[-1])
    print("Possible Delivery Dates:", ' - '.join(delivery_dates))
    print("Due Date (Naegele’s rule):", "%s %s [%s]" % (naegele_date.strftime(
        "%A"), naegele_date.isoformat(), zodiac_sign.get_zodiac_sign(naegele_date)))
    print("Harry’s prediction of due date:", "%s %s [%s]" % (harrys_date.strftime(
        "%A"), harrys_date.isoformat(), zodiac_sign.get_zodiac_sign(harrys_date)))
    print(screen_line)

    # Animation of Progress Bar
    total_days = (harrys_date - last_period).days
    completed_days = (datetime.date.today() - last_period).days
    with ShadyBar('Pregnacy', max=total_days, suffix='%(percent)d%%') as bar:
        for i in range(completed_days):
            time.sleep(0.025)
            bar.next()
