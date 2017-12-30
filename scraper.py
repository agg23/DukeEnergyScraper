from enum import Enum

import requests

# Mode 1: averageEnergyByDayOfWeek
# Mode 2: dailyEnergy
# Mode 3: hourlyEnergyUse

class Scraper(object):
	class Mode(Enum):
		averageEnergy = 1
		dailyEnergy = 2
		hourlyEnergy = 3

	headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}

	createCookieData = {
		"rememberMe": False
	}

	def __init__(self, username, password):
		self.session = requests.Session()
		self.loggedIn = False
		self.username = username
		self.password = password
		super()

	def daily(self, forDate):
		pass

	def request(self, data, mode, forDate, previouslyTried = False):
		chartName = ""

		if mode == Scraper.Mode.averageEnergy:
			chartName = "averageEnergyByDayOfWeek"
		elif mode == Scraper.Mode.dailyEnergy:
			chartName = "dailyEnergy"
		elif mode == Scraper.Mode.hourlyEnergy:
			chartName = "hourlyEnergyUse"

		data["chartName"] = chartName
		data["Mode"] = mode.value

		print(data)

		if not self.loggedIn:
			self.login()
			previouslyTried = True

		try:
			response = self.session.post("https://ols-b.duke-energy.com/037/rms.usag.dailyusage/DailyEnergyUsage", data=data, headers=self.headers, timeout=10)

			responseJson = response.json()

			print("Loaded data")
			return responseJson
		except:
			print("Failed to load json")
			self.loggedIn = False
			self.login()
			# Try request again if hasn't been previously tried
			if not previouslyTried:
				self.request(mode, forDate, previouslyTried = True)

	def login(self):
		print("Logging in")
		
		createCookie = self.session.post("https://www.duke-energy.com/api/Login/CreateCookie", data=self.createCookieData, headers=self.headers, timeout=10)

		if createCookie.status_code != 200:
			return

		loginData = {
			"userId": self.username,
			"userPassword": self.password,
			"returnURL": "https://www.duke-energy.com/sign-in",
			"deviceprofile": "desktop"
		}

		login2Data = {
			"userId": self.username,
			"userPassword": self.password,
			"returnURL": "https://www.duke-energy.com/sign-in",
			"Mode": 1,
			"deviceprofile": "desktop",
			"Promo": "",
			"SourceAcctID1": "",
			"SourceAcctID2": "",
			"SourceSystemCode": ""
		}

		login = self.session.post("https://ols.duke-energy.com/037/EnterpriseSingleSignOn/SharedLoginServlet", data=loginData, headers=self.headers, timeout=10)

		if login.status_code != 200:
			return

		login2 = self.session.post("https://ols.duke-energy.com/037/EnterpriseSingleSignOn/ExternalCustomerLogonServlet", data=login2Data, headers=self.headers, timeout=10)

		if login2.status_code != 200:
			return

		self.loggedIn = True
