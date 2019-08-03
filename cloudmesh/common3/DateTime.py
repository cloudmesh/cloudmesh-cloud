import datetime as TIME
from datetime import timezone
import humanize as HUMANIZE
from dateutil import parser
import time

class DateTime(object):

    timezone = TIME.timezone


    @staticmethod
    def now():
        return TIME.datetime.now()

    @staticmethod
    def natural(time):
        return parser.parse(time)

    @staticmethod
    def datetime(time):
        if type (time) == TIME:
            return time
        else:
            return DateTime.humanize(time)
        pass

    @staticmethod
    def humanize(time):
        return HUMANIZE.naturaltime(time)

    @staticmethod
    def string(time):
        if type(time) == str:
            d = time
        else:
            d = TIME.datetime.date(time)
        d = DateTime.humanize(time)
        return d

    @staticmethod
    def delta(n):
        return TIME.timedelta(seconds=n)

    @staticmethod
    def local(time):
        return time

    @staticmethod
    def utc(time):
        return time.replace(tzinfo=timezone.utc).astimezone(tz=None)


if __name__ == "__main__":

    start = DateTime.now()
    stop = DateTime.now() + DateTime.delta(1)

    print ("START", start)
    print ("STOP", stop)
    print("HUMANIZE STOP", DateTime.humanize(stop - start))
    print ("LOCAL", DateTime.local(start))
    print("UTC", DateTime.utc(start))
