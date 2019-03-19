import argparse
import calendar
import datetime
import json
import math
import shutil
import smtplib
import sys
import tempfile
import time
from email.mime.text import MIMEText
import locale

import zodiac_sign
from dateutil.parser import parse

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
        if (sourcedate.month == 2 and
                sourcedate.day == 29 and
                calendar.isleap(sourcedate.year) and
                not calendar.isleap(new_year)):
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


def main(input_data, out_file):
    screen_line = (shutil.get_terminal_size()[0]-1)*"-"

    # Σταθερές που γνωρίζουμε για την εγκυμοσύνη
    last_period = parse(input_data["start_of_last_period"]).date()
    conception_min = parse(input_data["min_possible_conception"]).date()
    conception_max = parse(input_data["max_possible_conception"]).date()

    # 3/4/2019 Επίσκεψη γιατρού me πρώτη εκτίμηση και εκτύπωση σε χαρτί
    # Εκτίμηση γιατρού

    estimations = [(parse(est["date"]).date(), datetime.timedelta(
        weeks=est["weeks"], days=est["days"]))
        for est in input_data["doctors_age_estimations"]]

    possible_start_gestation = [find_start_of_gestation(
        a_date, age) for a_date, age in estimations]

    print("Doctor’s estimates for the start of the pregnacy (gestation):", file=out_file)
    for i, doctors_conception in enumerate(possible_start_gestation):
        print("\t%s estimate:" % (ordinal(i+1)),
              doctors_conception, file=out_file)
    print(screen_line, file=out_file)

    gestational_age = datetime.date.today() - last_period
    doctors_age = datetime.date.today() - possible_start_gestation[-1]
    fetal_age_min = datetime.date.today() - conception_max
    fetal_age_max = datetime.date.today() - conception_min
    fetal_age_aprox = gestational_age - datetime.timedelta(weeks=2)
    fetal_age_doctors = doctors_age - datetime.timedelta(weeks=2)

    print("Gestational Age:", file=out_file)
    print("\tGestational age (calculated from last period) (Weeks, Days):",
          divmod(gestational_age.days, 7), file=out_file)
    print("\tDoctor’s last estimate of gestational age (Weeks, Days):",
          divmod(doctors_age.days, 7), file=out_file)
    print("Fetal Age:", file=out_file)
    print("\tMax fetal age (Weeks, Days):", divmod(
        fetal_age_max.days, 7), file=out_file)
    print("\tMin fetal age (Weeks, Days):", divmod(
        fetal_age_min.days, 7), file=out_file)
    print("\tApproximation of fetal age based on period (Week, Days):",
          divmod(fetal_age_aprox.days, 7), file=out_file)
    print("\tApproximation of fetal age based on doctor’s last estimate (Week, Days):",
          divmod(fetal_age_doctors.days, 7), file=out_file)
    print(screen_line, file=out_file)

    loc = locale.getlocale()
    locale.setlocale(locale.LC_ALL, 'en_US')
    delivery_dates = ["%s %s [%s]" % (dt.strftime("%A"), dt.isoformat(
    ), zodiac_sign.get_zodiac_sign(dt)) for dt in fuzzy_delivery_date(last_period)]
    naegele_date = naegele_due_date(last_period)
    # My prognosis
    harrys_date = naegele_due_date(possible_start_gestation[-1])
    print("Possible Delivery Dates:", ' - '.join(delivery_dates), file=out_file)
    print("Due Date (Naegele’s rule):", "%s %s [%s]" % (naegele_date.strftime(
        "%A"), naegele_date.isoformat(), zodiac_sign.get_zodiac_sign(naegele_date)), file=out_file)
    print("Harry’s prediction of due date:", "%s %s [%s]" % (harrys_date.strftime(
        "%A"), harrys_date.isoformat(), zodiac_sign.get_zodiac_sign(harrys_date)), file=out_file)
    print(screen_line, file=out_file)
    locale.setlocale(locale.LC_ALL, loc)

    total_days = (harrys_date - last_period).days
    completed_days = (datetime.date.today() - last_period).days
    if out_file is sys.stdout:
        # Animation of Progress Bar
        with ShadyBar('Pregnacy', max=total_days, suffix='%(percent)d%%') as bar:
            for i in range(completed_days):
                time.sleep(0.025)
                bar.next()
    else:
        print("Pregnacy is about %.1f%% complete" % (completed_days*100/total_days), file=out_file)


def send_email(email_info, email_msg):
    commaspace = ', '
    msg = MIMEText(email_msg)
    msg['Subject'] = 'Pregnancy Statistics for: %s' % (
        datetime.date.today().strftime("%x"))
    msg['From'] = email_info["email_from"]
    msg['To'] = commaspace.join(email_info["email_rcpt_to"])

    with smtplib.SMTP(email_info["email_smtp_host"], email_info["email_smtp_port"]) as s:
        if email_info["email_smtp_tls"]:
            s.starttls()

        s.login(email_info["email_from"], email_info["email_password"])
        text = msg.as_string()
        s.sendmail(email_info["email_from"], email_info["email_rcpt_to"], text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Simple Calculations for Pregnancy')
    parser.add_argument(
        "pregnancy_info", help="a json file containing pregnancy information", nargs='+')
    parser.add_argument(
        "-e", "--email", help="send email of the output", action="store_true")
    args = parser.parse_args()
    for info in args.pregnancy_info:
        with open(info, 'r') as fr_obj:
            data = json.load(fr_obj)
            if args.email and data['email_rcpt_to']:
                with tempfile.TemporaryFile(mode='w+', encoding="utf-8") as f_tmp:
                    main(data, f_tmp)
                    f_tmp.seek(0)
                    output = f_tmp.read()
                    send_email(data, output)
            else:
                main(data, sys.stdout)
