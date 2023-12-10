import ntplib
from datetime import datetime

def get_online_time():
    try:
        ntp_client = ntplib.NTPClient()
        print("Getting time from NTP server...")
        response = ntp_client.request('pool.ntp.org', version=3)
        ntp_time = datetime.fromtimestamp(response.tx_time)
        return ntp_time
    except ntplib.NTPException as e:
        print(f"Failed to get time from NTP server: {e}")
        return datetime.now()
