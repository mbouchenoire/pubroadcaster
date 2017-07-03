import json

class Profile(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)

    def get_wins_count(self, region, season, mode):
        """Returns the number of wins for a given region and season"""
        for regional_stats in self.Stats:
            if regional_stats["Region"] == region and regional_stats["Season"] == season and regional_stats["Match"] == mode:
                for stat in regional_stats["Stats"]:
                    if stat["field"] == u'Wins':
                        return stat["ValueInt"]

    def get_topten_count(self, region, season, mode):
        """Returns the number of top 10 for a given region and season"""
        for regional_stats in self.Stats:
            if regional_stats["Region"] == region and regional_stats["Season"] == season and regional_stats["Match"] == mode:
                for stat in regional_stats["Stats"]:
                    if stat["field"] == u'Top10s':
                        return stat["ValueInt"]
