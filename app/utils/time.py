from datetime import datetime
import pytz

jst = pytz.timezone("Asia/Tokyo")

def jst_now():
    return datetime.now(pytz.timezone("Asia/Tokyo"))