from twilio.rest import Client
from flight_data import FlightData
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

TXT_MSG_AUTH_TOKEN = os.environ["AUTH_TOKEN"]
ACCOUNT_SID = "AC43688d5710b72e119a022032080f8c41"
CLIENT = Client(ACCOUNT_SID, TXT_MSG_AUTH_TOKEN)
MY_EMAIL = "testerofpythontbt@gmail.com"
PASSWORD = "g_hzPU.fzDaY8m5"


class NotificationManager:
    @staticmethod
    def send_msg(flight_itinerary: FlightData, user: dict):
        body = f"Hello {user['First']} {user['Last']},\n" \
               f"Low price alert! Only ${flight_itinerary.total_price} to fly from "\
               f"{flight_itinerary.origin_city}-{flight_itinerary.origin_code} to "\
               f"{flight_itinerary.destination_city}-{flight_itinerary.destination_code},"\
               f" from {flight_itinerary.leave_date} to {flight_itinerary.return_date}." \

        # message = CLIENT.messages.create(
        #         body=body+" Check your email.",
        #         from_="+12393301206",
        #         to="+19198855568",
        #     )

        html = f"""
            <html>
            <head></head>
              <body>
                <p>{body}</p>"""

        for link in flight_itinerary.links:
            html += f"<p><a href={link}>Click here</a></p>\n"

        html += "</body></html>"

        # print(message.status)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Low price alert for flight to {flight_itinerary.destination_city}"
        msg['From'] = MY_EMAIL
        msg['To'] = user["email"]

        part1 = MIMEText(html, 'html')
        msg.attach(part1)

        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=PASSWORD)
            connection.sendmail(
                from_addr=MY_EMAIL,
                to_addrs=user["email"],
                msg=msg.as_string()
            )
