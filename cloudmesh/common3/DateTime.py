import datetime as TIME
import humanize
from dateutil import parser

class DateTime(object):

    timezone = TIME.timezone

    @staticmethod
    def now():
        return TIME.datetime.now()

    def natural(self, time):
        return parser.parse(time)

    def datetime(self, time):
        if type (time) == TIME:
            return time
        else:
            return humanize(time)
        pass

    def humanize(self, time):
        pass

    def string(self, time):
        if type(time) == str:
            d = time
        else:
            d = TIME.datetime.date(time)
        d = DateTime.humanize(time)
        return d
