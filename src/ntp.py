import ntplib
from datetime import datetime

def get_online_time():
    try:
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request('pool.ntp.org', version=3)
        return datetime.fromtimestamp(response.tx_time)
    except ntplib.NTPException as e:
        return datetime.now()
