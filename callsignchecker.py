from datetime import datetime
from enum import Enum
from os import environ

import pandas as pd
import pytz
import requests

ENDPOINT = "https://apc-cap.ic.gc.ca/pls/apc_anon/query_avail_cs$callsign.actionquery"
EMAIL_HOST = "smtp.mailgun.org"
EMAIL_PORT = 465
EMAIL_HOST_USER = environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = environ["EMAIL_HOST_PASSWORD"]
EMAIL_USE_TLS = True
EMAIL_USE_SSL = True
TIMEZONE = pytz.timezone("America/Toronto")

EMAIL_RECIPTIENTS = (
    ["Amin", "ve3hmm@gilani.me"],
    ["Chris", "ve3rwj@winsystem.org"],
)

import smtplib
from email.mime.text import MIMEText


class NumberOfLetters(Enum):
    TWO = "2"
    THREE = "3"


class Prefix(Enum):
    VE3 = "VE3"
    VA3 = "VA3"


class CallSignsNotifier:
    def _send_email(
        self,
        callsigns: list,
        number_of_letters: NumberOfLetters,
        time: datetime,
        recipient: str,
        recipient_first_name: str,
    ) -> None:
        delimited_signs = "\n".join([f"* {callsign}" for callsign in callsigns])
        formatted_time = time.strftime("%A %B %d, %Y at %I:%M%p")

        body = (
            f"Hi {recipient_first_name}, as you requested, there may be {number_of_letters}-letter callsign available. "
            f"Your options on {formatted_time} are:\n{delimited_signs}"
        )

        s = smtplib.SMTP("smtp.mailgun.org", 587)
        s.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        short_date = time.strftime("%d/%m/%y")
        subject = f"{number_of_letters}-letter callsigns available on {short_date}!"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_HOST_USER
        msg["To"] = recipient

        s.sendmail(msg["From"], msg["To"], msg.as_string())

        s.quit()

    def _get_iesd_results_page(
        self, prefix: Prefix, number_of_letters: NumberOfLetters
    ) -> str:
        data = {
            "P_PREFIX_U": prefix,
            "P_SUFFIX_CHAR_1_U": "%",
            "P_SUFFIX_CHAR_2_U": "%",
            "P_SUFFIX_CHAR_3_U": "%",
            "P_SUFFIX_TYPE_U": number_of_letters,
            "Z_ACTION": "QUERY",
            "Z_CHK": "0",
        }

        response = requests.post(ENDPOINT, data=data)
        return response.text

    def _results_page_to_callsigns(self, results_page: str) -> list:
        tables = pd.read_html(results_page)
        call_signs_table = tables[0]
        callsigns = [
            callsign
            for callsign_wrapped in call_signs_table.values.tolist()
            for callsign in callsign_wrapped
        ]
        return callsigns

    def __init__(
        self,
        prefix: Prefix,
        number_of_letters: NumberOfLetters,
        recipient: str,
        recipient_first_name: str,
    ) -> None:
        results_page = self._get_iesd_results_page(
            prefix=prefix,
            number_of_letters=number_of_letters,
        )
        callsigns = None
        try:
            callsigns = self._results_page_to_callsigns(results_page)

            self._send_email(
                callsigns,
                number_of_letters=number_of_letters,
                time=datetime.now(TIMEZONE),
                recipient=recipient,
                recipient_first_name=recipient_first_name,
            )
        except ValueError as e:
            if "No tables found" in f"{e}":
                print("No callsigns available")
            else:
                raise e


def main():
    for recipient_first_name, recipient_mail in EMAIL_RECIPTIENTS:
        CallSignsNotifier(
            prefix=Prefix.VE3.value,
            number_of_letters=NumberOfLetters.TWO.value,
            recipient=recipient_mail,
            recipient_first_name=recipient_first_name,
        )
        CallSignsNotifier(
            prefix=Prefix.VA3.value,
            number_of_letters=NumberOfLetters.TWO.value,
            recipient=recipient_mail,
            recipient_first_name=recipient_first_name,
        )


if __name__ == "__main__":
    main()
