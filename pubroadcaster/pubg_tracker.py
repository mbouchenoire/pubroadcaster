import http.client
from profile import Profile

class PubgTracker(object):
    def __init__(self, api_key):
        self.host = "pubgtracker.com"
        self.endpoint = "/api/profile/pc/"
        self.headers = {"TRN-Api-Key": api_key}

    def get_profile(self, name):
        """Returns the PUBG player profile"""
        conn = http.client.HTTPSConnection(self.host)
        conn.request("GET", self.endpoint + name, headers=self.headers)
        response = conn.getresponse()

        data = response.read()

        conn.close()

        return Profile(data.decode("utf-8"))
