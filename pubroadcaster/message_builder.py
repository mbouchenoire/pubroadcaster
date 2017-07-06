class MessageBuilder(object):
    def __init__(self):
        pass

    def get_game_stats(self, old_profile, new_profile, region, season, mode):
        kills = new_profile.get_increment_from(old_profile, region, season, mode, u'Kills')
        assists = new_profile.get_increment_from(old_profile, region, season, mode, u'Assists')
        dbnos = new_profile.get_increment_from(old_profile, region, season, mode, u'DBNOs')
        damage_dealt = new_profile.get_increment_from(old_profile, region, season, mode, u'DamageDealt')
        walk_distance = new_profile.get_increment_from(old_profile, region, season, mode, u'WalkDistance')
        ride_distance = new_profile.get_increment_from(old_profile, region, season, mode, u'RideDistance')
        revives = new_profile.get_increment_from(old_profile, region, season, mode, u'Revives')
        time_survived = new_profile.get_increment_from(old_profile, region, season, mode, u'TimeSurvived')
        suicides = new_profile.get_increment_from(old_profile, region, season, mode, u'Suicides')
        team_kills = new_profile.get_increment_from(old_profile, region, season, mode, u'TeamKills')
        longest_kill_increment = new_profile.get_increment_from(old_profile, region, season, mode, u'LongestKill')
        longest_kill = new_profile.get_field_numerical_value(region, season, mode, u'LongestKill')

        message = ""

        message += "* {}: {}".format("Kills", kills)
        
        if mode != "solo":
            message += "\n* {}: {}".format("Assists", assists)
            message += "\n* {}: {}".format("Knock Outs", dbnos)

        message += "\n* {}: {}".format("Damage Dealt", int(damage_dealt))
        
        if mode != "solo":
            message += "\n* {}: {}".format("Revives", revives)
            message += "\n* {}: {}min".format("Time Survived", int(time_survived // 60))

        walk_distance = walk_distance if walk_distance > 0 else 1
        ride_percentage = (ride_distance / walk_distance) * 100

        if longest_kill_increment > 0:
            message += "\n> beat his longest kill record with a {} meters shot!".format(longest_kill)

        if ride_percentage > 80:
            message += "\n> traveled {}% of his distance by vehicule!".format(ride_percentage)

        if ride_distance == 0:
            message += "\n> did not use a single vehicule!"

        if suicides > 0:
            message += "\n> his life ended with a suicide..."

        if team_kills > 0:
            message += "\n> killed one of his mates..."

        return message

    def get_global_stats(self, profile, region, season, mode):
        rounds_played = profile.get_field_numerical_value(region, season, mode, u'RoundsPlayed')

        rating = profile.get_field_display_value(region, season, mode, u'Rating')
        rating_percentile = profile.get_field_percentile(region, season, mode, u'Rating')

        win_ratio = profile.get_field_display_value(region, season, mode, u'WinRatio')
        win_ratio_percentile = profile.get_field_percentile(region, season, mode, u'WinRatio')

        top_ten_ratio = profile.get_field_display_value(region, season, mode, u'Top10Ratio')
        top_ten_ratio_percentile = profile.get_field_percentile(region, season, mode, u'Top10Ratio')

        kd = profile.get_field_display_value(region, season, mode, u'KillDeathRatio')
        kd_percentile = profile.get_field_percentile(region, season, mode, u'KillDeathRatio')

        kills_pg = profile.get_field_display_value(region, season, mode, u'KillsPg')
        kills_pg_percentile = profile.get_field_percentile(region, season, mode, u'KillsPg')

        assists_pg = profile.get_field_numerical_value(region, season, mode, u'Assists') // rounds_played
        dbnos_pg = profile.get_field_numerical_value(region, season, mode, u'DBNOs') / rounds_played

        damage_pg = profile.get_field_numerical_value(region, season, mode, u'DamagePg')
        damage_pg_percentile = profile.get_field_percentile(region, season, mode, u'DamagePg')

        revives_pg = profile.get_field_display_value(region, season, mode, u'RevivesPg')
        revives_pg_percentile = profile.get_field_percentile(region, season, mode, u'RevivesPg')

        time_survived_pg = profile.get_field_display_value(region, season, mode, u'TimeSurvivedPg')
        time_survived_pg_percentile = profile.get_field_percentile(region, season, mode, u'TimeSurvivedPg')

        message = ""

        template = "* {}: {} (top {}%)"
        template_without_perc = "* {}: {}"

        message += template.format("Rating", rating, rating_percentile)
        message += "\n" + template.format("Win Rate", win_ratio, win_ratio_percentile)
        message += "\n" + template.format("Top 10 Rate", top_ten_ratio,  top_ten_ratio_percentile)
        message += "\n" + template.format("K/D", kd, kd_percentile)
        message += "\n" + template.format("Kills Pg", kills_pg, kills_pg_percentile)
        message += "\n" + template_without_perc.format("Assists Pg", round(assists_pg, 1))
        message += "\n" + template_without_perc.format("Knock Outs Pg", round(dbnos_pg, 1))
        message += "\n" + template.format("Damage Pg", int(damage_pg), damage_pg_percentile)
        message += "\n" + template.format("Revives Pg", revives_pg, revives_pg_percentile)
        message += "\n" + template.format("Time Survived Pg", time_survived_pg, time_survived_pg_percentile)

        return message

    def build_win(self, profile_name, old_profile, new_profile, region, season, mode):
        message = "```Markdown"
        
        message += "\n# WINNER: {}!".format(profile_name)
        message += "\n> {}@{}".format(mode, region)
        message += "\n"
        message += self.get_game_stats(old_profile, new_profile, region, season, mode)
        
        message += "\n\n> stats {}@{}".format(mode, region)
        message += "\n"
        message += self.get_global_stats(new_profile, region, season, mode)

        message += "```"

        return message

    def build_topten(self, profile_name, old_profile, new_profile, region, season, mode):
        message = "```Markdown"
        
        message += "\n# TOP TEN: {}".format(profile_name)
        message += "\n> {}@{}".format(mode, region)
        message += "\n"
        message += self.get_game_stats(old_profile, new_profile, region, season, mode)

        message += "```"

        return message

    