import json

class Profile(object):
    INCREMENTAL_FIELD_NAMES = [ u'Kills', u'Assists', u'DBNOs', u'DamageDealt', u'TeamKills', u'Suicides', u'VehiculeDestroys', u'RoadKills',
                                u'WalkDistance', u'RideDistance', u'Revives',  ]

    
    RARE_FIELD_NAMES = [ u'Suicides', u'TeamKills', u'VehiculeDestroys', u'RoadKills' ] 

    def __init__(self, j):
        self.__dict__ = json.loads(j)

    def get_field(self, region, season, mode, field_name, field_value):
        for regional_stats in self.Stats:
            if regional_stats["Region"] == region and regional_stats["Season"] == season and regional_stats["Match"] == mode:
                for stat in regional_stats["Stats"]:
                    if stat["field"] == field_name:
                        return stat[field_value]

    def get_field_percentile(self, region, season, mode, field_name):
        return int(self.get_field(region, season, mode, field_name, 'percentile'))

    def get_field_value(self, region, season, mode, field_name):
        return self.get_field(region, season, mode, field_name, 'value')

    def get_field_display_value(self, region, season, mode, field_name):
        return self.get_field(region, season, mode, field_name, 'displayValue')

    def get_field_numerical_value(self, region, season, mode, field_name):
        int_value = self.get_field(region, season, mode, field_name, 'ValueInt')
        
        if int_value is not None:
            return int_value

        return round(self.get_field(region, season, mode, field_name, 'ValueDec'), 1)

    def get_increment_from(self, old_profile, region, season, mode, field_name):
        up_to_date_field_value = self.get_field_numerical_value(region, season, mode, field_name)
        old_field_value = old_profile.get_field_numerical_value(region, season, mode, field_name)
        return up_to_date_field_value - old_field_value

    def has_incremented_from(self, old_profile, region, season, mode, field_name):
        return self.get_increment_from(old_profile, region, season, mode, field_name) > 0
