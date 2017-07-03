import json

class Profile(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)

    def __get_integer_field(self, region, season, mode, field_name):
        for regional_stats in self.Stats:
            if regional_stats["Region"] == region and regional_stats["Season"] == season and regional_stats["Match"] == mode:
                for stat in regional_stats["Stats"]:
                    if stat["field"] == field_name:
                        return stat["ValueInt"]

    def get_wins_count(self, region, season, mode):
        return self.__get_integer_field(region, season, mode, u"Wins")

    def get_topten_count(self, region, season, mode):
        return self.__get_integer_field(region, season, mode, u"Top10s")
    
    def get_kills_count(self, region, season, mode):
        return self.__get_integer_field(region, season, mode, u"Kills")
