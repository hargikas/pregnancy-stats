import argparse
import datetime
import html
import json
import locale
import math
import random
import shutil
import smtplib
import sys
import tempfile
import textwrap
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pyaztro
import zodiac_sign
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

import chinese_zodiac
from progress.bar import ShadyBar


def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(math.floor(n/10) % 10 != 1)*(n % 10 < 4)*n % 10::4])


def fuzzy_delivery_date(last_period):
    min_weeks = 37
    max_weeks = 42

    min_delivery = last_period + relativedelta(weeks=+min_weeks)
    max_delivery = last_period + relativedelta(weeks=+max_weeks)

    return [min_delivery, max_delivery]


def naegele_due_date(last_period):
    # Naegele’s rule (for 28 days period)
    # https://www.healthline.com/health/pregnancy/what-is-gestation#calculate-a-due-date
    # https://www.healthline.com/health/pregnancy/your-due-date#1
    due_date = last_period + relativedelta(weeks=+1, months=-3, years=+1)
    return due_date


def find_start_of_gestation(a_date, age):
    return a_date - age


def main(input_data, out_file):
    screen_line = (shutil.get_terminal_size()[0]-1)*"-"

    # Σταθερές που γνωρίζουμε για την εγκυμοσύνη
    last_period = parse(input_data["start_of_last_period"]).date()
    conception_min = parse(input_data["min_possible_conception"]).date()
    conception_max = parse(input_data["max_possible_conception"]).date()

    # Εκτιμήσεις γιατρού
    estimations = [(parse(est["date"]).date(), relativedelta(
        weeks=est["weeks"], days=est["days"]))
        for est in input_data["doctors_age_estimations"]]

    possible_start_gestation = [find_start_of_gestation(
        a_date, age) for a_date, age in estimations]

    if possible_start_gestation:
        print(
            "Doctor’s estimates for the start of the pregnacy (gestation):", file=out_file)
        for i, doctors_conception in enumerate(possible_start_gestation):
            print("\t%s estimate:" % (ordinal(i+1)),
                  doctors_conception, file=out_file)
        print(screen_line, file=out_file)
        doctors_age = datetime.date.today() - possible_start_gestation[-1]
        fetal_age_doctors = doctors_age + relativedelta(weeks=-2)

    gestational_age = datetime.date.today() - last_period
    fetal_age_min = datetime.date.today() - conception_max
    fetal_age_max = datetime.date.today() - conception_min
    fetal_age_aprox = gestational_age + relativedelta(weeks=-2)

    print("Gestational Age:", file=out_file)
    print("\tGestational age (calculated from last period) (Weeks, Days):",
          divmod(gestational_age.days, 7), file=out_file)
    if doctors_age and doctors_age != gestational_age:
        print("\tDoctor’s last estimate of gestational age (Weeks, Days):",
              divmod(doctors_age.days, 7), file=out_file)
    print("Fetal Age:", file=out_file)
    print("\tMax fetal age (Weeks, Days):", divmod(
        fetal_age_max.days, 7), file=out_file)
    print("\tMin fetal age (Weeks, Days):", divmod(
        fetal_age_min.days, 7), file=out_file)
    print("\tApproximation of fetal age based on last period (Week, Days):",
          divmod(fetal_age_aprox.days, 7), file=out_file)
    if fetal_age_doctors and fetal_age_doctors != fetal_age_aprox:
        print("\tApproximation of fetal age based on doctor’s last estimate (Week, Days):",
              divmod(fetal_age_doctors.days, 7), file=out_file)
    print(screen_line, file=out_file)

    loc = locale.getlocale()
    locale.setlocale(locale.LC_ALL, 'C')
    delivery_dates = ["%s %s [%s]" % (dt.strftime("%A"), dt.isoformat(
    ), zodiac_sign.get_zodiac_sign(dt)) for dt in fuzzy_delivery_date(last_period)]
    naegele_date = naegele_due_date(last_period)
    possible_zodiac = zodiac_sign.get_zodiac_sign(naegele_date)

    print("Possible Delivery Dates:", ' - '.join(delivery_dates), file=out_file)
    print("Due Date (Naegele’s rule):", "%s %s [%s]" % (naegele_date.strftime(
        "%A"), naegele_date.isoformat(), possible_zodiac), file=out_file)
    # My prognosis
    if possible_start_gestation and possible_start_gestation[-1] != last_period:
        harrys_date = naegele_due_date(possible_start_gestation[-1])
        possible_zodiac = zodiac_sign.get_zodiac_sign(harrys_date)
        print("Harry’s prediction of due date:", "%s %s [%s]" % (harrys_date.strftime(
            "%A"), harrys_date.isoformat(), possible_zodiac), file=out_file)
    print(screen_line, file=out_file)
    locale.setlocale(locale.LC_ALL, loc)

    try:
        total_days = (harrys_date - last_period).days
    except UnboundLocalError:
        total_days = (naegele_date - last_period).days

    completed_days = (datetime.date.today() - last_period).days
    if out_file is sys.stdout:
        # Animation of Progress Bar
        with ShadyBar('Pregnacy', max=total_days, suffix='%(percent)d%%') as bar:
            for i in range(completed_days):
                time.sleep(0.025)
                bar.next()
    else:
        print("Pregnacy is about %.1f%% complete" %
              (completed_days*100/total_days), file=out_file)
    print(screen_line, file=out_file)

    print("", file=out_file)
    print("Silly & Fun Stuff".center(len(screen_line), '*'), file=out_file)
    print("", file=out_file)
    chinese_zodiacs = set([chinese_zodiac.calculate_dt(dt)
                           for dt in fuzzy_delivery_date(last_period)])
    chinese_desc = "Chinese zodiac: %s" % (" or ".join(chinese_zodiacs))
    print(textwrap.fill(chinese_desc, width=len(screen_line)), file=out_file)
    print("", file=out_file)
    horoscope = pyaztro.Aztro(sign=possible_zodiac.lower())
    horoscope_desc = "Horoscope for %s: %s" % (
        horoscope.sign.capitalize(), horoscope.description)
    print(textwrap.fill(horoscope_desc, width=len(screen_line)), file=out_file)
    print("", file=out_file)
    print("Color:", horoscope.color, file=out_file)
    print("Mood:", horoscope.mood, file=out_file)
    print("Compatibility:", horoscope.compatibility, file=out_file)
    print("Lucky Number:", horoscope.lucky_number, file=out_file)
    print("Lucky Time:", horoscope.lucky_time, file=out_file)


def send_email(email_info, email_msg):
    commaspace = ', '
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Pregnancy Statistics for: %s' % (
        datetime.date.today().strftime("%x"))
    msg['From'] = email_info["email_from"]
    msg['To'] = commaspace.join(email_info["email_rcpt_to"])

    # Record the MIME types of both parts - text/plain and text/html.
    html_text = '<html><head></head><body><pre width="79">%s</pre></body></html>' % (
        html.escape(email_msg))
    part1 = MIMEText(email_msg, 'plain')
    part2 = MIMEText(html_text, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

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
