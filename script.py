import requests
import pandas as pd
from enum import Enum
import pytz
from datetime import datetime
from os import environ


ENDPOINT = "https://apc-cap.ic.gc.ca/pls/apc_anon/query_avail_cs$callsign.actionquery"
EMAIL_HOST = "smtp.mailgun.org"
EMAIL_PORT = 465
EMAIL_HOST_USER = environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = environ["EMAIL_HOST_PASSWORD"]
EMAIL_USE_TLS = True
EMAIL_USE_SSL = True
TIMEZONE = pytz.timezone("America/Toronto")

EMAIL_RECIPTIENT = "ve3hmm@gilani.me"

import smtplib

from email.mime.text import MIMEText


class NumberOfLetters(Enum):
    TWO = "2"
    THREE = "3"


class CallSignsNotifier:
    def _send_email(
        self,
        callsigns: list,
        number_of_letters: NumberOfLetters,
        time: datetime,
        recipient: str,
    ) -> None:
        delimited_signs = "\n".join([f"* {callsign}" for callsign in callsigns])
        formatted_time = time.strftime("%A %B %d, %Y at %I:%M%p")

        body = (
            f"Hi Amin, as you requested, there may be {number_of_letters}-letter callsign available. "
            f"Your options on {formatted_time} are:\n{delimited_signs}"
        )

        s = smtplib.SMTP("smtp.mailgun.org", 587)
        s.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        short_date = time.strftime("%d/%m/%y")
        subject = f"{number_of_letters}-letter callsigns available on {short_date}!"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_HOST_USER
        msg["To"] = receipient

        s.sendmail(msg["From"], msg["To"], msg.as_string())

        s.quit()

    def _get_iesd_results_page(self, number_of_letters: NumberOfLetters) -> str:
        data = {
            "P_PREFIX_U": "VE3",
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

    def __init__(self, number_of_letters: NumberOfLetters, recipient: str) -> None:
        results_page = self._get_iesd_results_page(number_of_letters)
        callsigns = None
        try:
            callsigns = self._results_page_to_callsigns(results_page)

            self._send_email(
                callsigns,
                number_of_letters=number_of_letters,
                time=datetime.now(TIMEZONE),
                recipient=recipient,
            )
        except ValueError as e:
            if "No tables found" in f"{e}":
                print("No callsigns available")
            else:
                raise e


if __name__ == "__main__":

    CallSignsNotifier(NumberOfLetters.THREE.value, recipient=EMAIL_RECIPTIENT)
