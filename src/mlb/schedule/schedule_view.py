from mlb.models.game_detail import GameDetail
import time
import board
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_bitmap_font import bitmap_font
from mlb.schedule.schedule_view_model import ScheduleViewModel
from time_utils import day_of_week, month_name_short, relative_day, utc_to_local, month_name, hour_12, ampm

class ScheduleView:

    #Display 296 x 128

    def __init__(self, model: ScheduleViewModel):
        self.model = model
        self.helveticaBold16 = bitmap_font.load_font("/fonts/Helvetica-Bold-16.bdf")

    def render(self):
        display = board.DISPLAY
        print(f'Display: {display.width} x {display.height}')

        # wait until we can draw
        time.sleep(display.time_to_refresh)

        # main group to hold everything
        main_group = displayio.Group()

        # white background. Scaled to save RAM
        bg_bitmap = displayio.Bitmap(display.width // 8, display.height // 8, 1)
        bg_palette = displayio.Palette(1)
        bg_palette[0] = 0xFFFFFF
        bg_sprite = displayio.TileGrid(bg_bitmap, x=0, y=0, pixel_shader=bg_palette)
        bg_group = displayio.Group(scale=8)
        bg_group.append(bg_sprite)
        main_group.append(bg_group)

        game1_group = self._single_game_group(self.model.game1)
        game1_group.x = 0
        game1_group.y = 0

        game2_group = self._single_game_group(self.model.game2)
        game2_group.x = 99
        game2_group.y = 0

        game3_group = self._single_game_group(self.model.game3)
        game3_group.x = 198
        game3_group.y = 0

        main_group.append(game1_group)
        main_group.append(game2_group)
        main_group.append(game3_group)

        # show the main group and refresh.
        display.show(main_group)
        display.refresh()


    def _single_game_group(self, game: GameDetail):

        game_group = displayio.Group()

        if game is None:
            return game_group

        roundrect = RoundRect(5, 5, 88, 118, 10, fill=0xFFFFFF, outline=0x555555, stroke=3)
        game_group.append(roundrect)

        gametime_local = utc_to_local(game.dateTimeUtc)
        day_text = ( relative_day(gametime_local) or day_of_week(gametime_local) )
        date_text = f'{month_name(gametime_local)} {gametime_local.day}'
        time_text = f'{hour_12(gametime_local)}:{gametime_local.minute:02d} {ampm(gametime_local)}'
        
        day_label = label.Label(terminalio.FONT, text=day_text, color=0x000000)
        day_label.anchor_point = (0.5, 0)
        day_label.anchored_position = (49, 6)
        game_group.append(day_label)

        date_label = label.Label(terminalio.FONT, text=date_text, color=0x000000)
        date_label.anchor_point = (0.5, 0)
        date_label.anchored_position = (49, 18)
        game_group.append(date_label)

        time_label = label.Label(terminalio.FONT, text=time_text, color=0x000000)
        time_label.anchor_point = (0.5, 0)
        time_label.anchored_position = (49, 30)
        game_group.append(time_label)

        #Teams
        if game.status == 'Preview': #(no score to show)
            away_team = label.Label(self.helveticaBold16, text=f"{game.away.teamAbbreviation}", color=0x000000)
            away_team.anchor_point = (0.5, 0)
            away_team.anchored_position = (49, 62)
            game_group.append(away_team)

            at_label = label.Label(terminalio.FONT, text='@', color=0x000000)
            at_label.anchor_point = (0.5, 0)
            at_label.anchored_position = (49, 77)
            game_group.append(at_label)

            home_team = label.Label(self.helveticaBold16, text=f"{game.home.teamAbbreviation}", color=0x000000)
            home_team.anchor_point = (0.5, 0)
            home_team.anchored_position = (49, 95)
            game_group.append(home_team)

        else:
            teams = label.Label(self.helveticaBold16, text=f"{game.away.teamAbbreviation}\n{game.home.teamAbbreviation}", color=0x000000)
            teams.anchor_point = (0, 0)
            teams.anchored_position = (15, 58)
            game_group.append(teams)
            scores = label.Label(self.helveticaBold16, text=f"{game.away.runs}\n{game.home.runs}", color=0x000000)
            scores.anchor_point = (1, 0)
            scores.anchored_position = (84, 58)
            game_group.append(scores)

        if game.status == 'Live':
            inning = label.Label(terminalio.FONT, text=f"{game.inningHalf} {game.currentInningOrdinal}", color=0x000000)
            inning.anchor_point = (0.5, 0)
            inning.anchored_position = (49, 105)
            game_group.append(inning)

        if game.status == 'Final':
            status_label = label.Label(terminalio.FONT, text=f"{game.status}", color=0x000000)
            status_label.anchor_point = (0.5, 0)
            status_label.anchored_position = (49, 105)
            game_group.append(status_label)

        return game_group