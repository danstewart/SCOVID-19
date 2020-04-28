import datetime
import pytz

class DT(object):

	# Constructors
	def __init__(self, dt=datetime.datetime.now(), format="%Y-%m-%d"):
		if (isinstance(dt, datetime.datetime)):
			self.dt = dt
		else:
			self.dt = datetime.datetime.strptime(dt, format)

		tz = pytz.timezone('Europe/London')
		self.dt = pytz.utc.localize(self.dt).astimezone(tz)

	@classmethod
	def from_date(self, date):
		self = DT(date)
		return self

	@classmethod
	def from_datetime(self, date):
		self = DT(date, '%Y-%m-%d %H:%M:%s')
		return self


	# Formatters
	def make_nice(self, format='%B {day} %Y'):
		self.nice = self.dt.strftime(format)
		if ('{day}' in format):
			self.nice = self.nice.replace('{day}', self.suffix())

		return self


	# Other
	def suffix(self):
		day = self.dt.day
		suffix = 'th' if 11 <= day <=13 else { 1:'st', 2:'nd', 3:'rd' }.get(day % 10, 'th')
		return str(day) + suffix
