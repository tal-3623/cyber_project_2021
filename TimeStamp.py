from datetime import datetime


class TimeStamp:

    def __init__(self, date_as_str: str = None):
        if date_as_str is None:
            self.date_as_str = datetime.now()
        else:
            self.date_as_str = date_as_str
        a, b = str(self.date_as_str).split(' ')
        self.year, self.month, self.day = a.split('-')
        self.hour, self.minute, self.sec = b.split(':')

    def __str__(self):
        return self.date_as_str
