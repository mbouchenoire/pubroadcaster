import logging as log
import json
import http.client


class GameContext(object):
    def __init__(self, season: str, region: str, mode: str) -> None:
        self.season = season
        self.region = region
        self.mode = mode

    def __eq__(self, other) -> bool:
        return other.season == self.season and other.region == self.region and other.mode == self.mode

    def __hash__(self) -> int:
        return hash(self.season + self.region + self.mode)


class Profile(object):
    def __init__(self, j, profile_name) -> None:
        self.__dict__ = json.loads(j)
        self.name = profile_name

    def __get_field__(self, context: GameContext, field_name: str, field_value: str):
        if not hasattr(self, "Stats"):
            return None

        for regional_stats in self.Stats:
            if regional_stats["Region"] == context.region and regional_stats["Season"] == context.season and regional_stats["Match"] == context.mode:
                for stat in regional_stats["Stats"]:
                    if stat["field"] == field_name:
                        return stat[field_value]

    def __get_field_percentile__(self, context: GameContext, field_name: str) -> float:
        return self.__get_field__(context, field_name, "percentile")

    def __get_field_display_value__(self, context: GameContext, field_name: str) -> str:
        return self.__get_field__(context, field_name, "displayValue")

    def __get_field_numerical_value__(self, context: GameContext, field_name: str) -> float:
        int_value = self.__get_field__(context, field_name, "ValueInt")
        
        if int_value is not None:
            return int_value

        dec_value = self.__get_field__(context, field_name, "ValueDec")

        if dec_value is not None:
            return round(dec_value, 1)

        warn = "{} field has value 'None' for {}: {}@{}".format(field_name, self.name, context.mode, context.region)
        log.warning(warn)

        return None

    def __get_increment_from__(self, old_profile, context: GameContext, field_name: str) -> float:
        up_to_date_field_value = self.__get_field_numerical_value__(context, field_name)

        if up_to_date_field_value is None:
            return None

        old_field_value = old_profile.__get_field_numerical_value__(context, field_name)

        if old_field_value is None:
            return None

        return up_to_date_field_value - old_field_value

    def has_won(self, old_profile, context: GameContext) -> bool:
        incremented_wins = self.__get_increment_from__(old_profile, context, u'Wins')
        return incremented_wins == 1

    def has_topten(self, old_profile, context: GameContext) -> bool:
        incremented_toptens = self.__get_increment_from__(old_profile, context, u'Top10s')
        return incremented_toptens == 1

    def get_game_facts(self, old_profile, context: GameContext) -> 'GameFacts':
        walk_distance = self.__get_increment_from__(old_profile, context, u'WalkDistance')
        ride_distance = self.__get_increment_from__(old_profile, context, u'RideDistance')
        suicides = self.__get_increment_from__(old_profile, context, u'Suicides')
        team_kills = self.__get_increment_from__(old_profile, context, u'TeamKills')
        longest_kill_increment = self.__get_increment_from__(old_profile, context, u'LongestKill')
        longest_kill = self.__get_field_numerical_value__(context, u'LongestKill')
        walk_distance = walk_distance if walk_distance > 0 else 1
        ride_percentage = (ride_distance / (ride_distance + walk_distance)) * 100

        facts = []

        if longest_kill_increment > 0:
            facts.append("{} beat his longest kill record with a {}m shot!".format(self.name, longest_kill))

        if ride_percentage > 80:
            facts.append("{} traveled {}% by vehicule!".format(self.name, int(ride_percentage)))

        if ride_distance == 0:
            facts.append("{} did not use a single vehicule!".format(self.name))

        if suicides > 0:
            facts.append("{} ended his life with a suicide...".format(self.name))

        if team_kills > 0:
            facts.append("{} killed one of his mates...".format(self.name))

        return GameFacts(self, context, facts)

    def get_game_stats(self, old_profile, context: GameContext) -> 'GameStats':
        kills = self.__get_increment_from__(old_profile, context, u'Kills')
        assists = self.__get_increment_from__(old_profile, context, u'Assists')
        dbnos = self.__get_increment_from__(old_profile, context, u'DBNOs')
        damage_dealt = self.__get_increment_from__(old_profile, context, u'DamageDealt')
        revives = self.__get_increment_from__(old_profile, context, u'Revives')
        seconds_survived = self.__get_increment_from__(old_profile, context, u'TimeSurvived')
        minutes_survived = int(seconds_survived // 60)

        return GameStats(self, context, kills, assists, dbnos, damage_dealt, revives, minutes_survived)

    def get_global_stats(self, context: GameContext) -> 'GlobalStats':
        return GlobalStats(self, context)


class GameStats(object):
    def __init__(self, profile: Profile, context: GameContext, kills: int, assists: int, dbnos: int, damage_dealt: float, revives: int, minutes_survived: int):
        self.profile = profile
        self.context = context
        self.kills = kills
        self.assists = assists
        self.dbnos = dbnos
        self.damage_dealt = damage_dealt
        self.revives = revives
        self.minutes_survived = minutes_survived

    def headers(self) -> [str]:
        h = ["* Player", "Kil."]

        if self.context.mode != "solo":
            h.append("Fin.")
            h.append("Kno.")

        h.append("Dam.")

        if self.context.mode != "solo":
            h.append("Rev.")

        h.append("Sur.")

        return h

    def values(self) -> list:
        stats = ["* " + self.profile.name, self.kills]

        if self.context.mode != "solo":
            stats.append(self.assists)
            stats.append(self.dbnos)
        
        stats.append(self.damage_dealt)

        if self.context.mode != "solo":
            stats.append(self.revives)
            
        stats.append(str(self.minutes_survived) + "min")

        return stats

    def score(self):
        return self.damage_dealt


class GlobalStats(object):
    def __init__(self, profile: Profile, game_context: GameContext) -> None:
        self.profile = profile
        self.game_context = game_context

    def values(self) -> list:
        return [["* Stat", "Value", "Top"],
                self.get_field_tuple(u"Rating"),
                self.get_field_tuple(u"WinRatio"),
                self.get_field_tuple(u"Top10Ratio"),
                self.get_field_tuple(u"KillDeathRatio"),
                self.get_field_tuple(u"KillsPg"),
                self.get_field_tuple(u"DamagePg"),
                self.get_field_tuple(u"RevivesPg"),
                self.get_field_tuple(u"TimeSurvivedPg")]

    def get_field_tuple(self, field_name):
        label = self.profile.__get_field__(self.game_context, field_name, u'label')
        display_value = self.profile.__get_field_display_value__(self.game_context, field_name)

        percentile_dec = self.profile.__get_field_percentile__(self.game_context, field_name)
        percentile_str = str(percentile_dec)
        percentile_str = percentile_str if not percentile_str.endswith(".0") else percentile_str.replace(".0", "")
        percentile_displayed = percentile_str + "%"

        return ("* " + label), display_value, percentile_displayed 
        

class GameFacts(object):
    def __init__(self, profile: Profile, context: GameContext, facts: [str]):
        self.profile = profile
        self.context = context
        self.facts = facts


class PubgTracker(object):
    def __init__(self, api_key: str):
        self._host = "pubgtracker.com"
        self._endpoint = "/api/profile/pc/"
        self._headers = {"TRN-Api-Key": api_key}

    def retreive_profile(self, name: str) -> Profile:
        """Returns the PUBG player profile"""
        conn = http.client.HTTPSConnection(self._host)
        conn.request("GET", self._endpoint + name, headers=self._headers)
        response = conn.getresponse()

        data = response.read()

        conn.close()

        return Profile(data.decode("utf-8"), name)
