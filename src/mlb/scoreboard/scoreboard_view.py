from mlb.models.game_detail import GameDetail
import time
import math
import board
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.circle import Circle
from adafruit_bitmap_font import bitmap_font
from time_utils import utc_to_local, month_name, hour_12, ampm, relative_day, day_of_week, local_now

class ScoreboardView:

    #Display 296 x 128

    def __init__(self, model: GameDetail):
        self.model = model
        self.helveticaBold16 = bitmap_font.load_font("/fonts/Helvetica-Bold-16.bdf")


    def render(self):
        display = board.DISPLAY
        
        
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

        header = self._header_group()
        header.x = 0
        header.y = 0
        main_group.append(header)

        highlightAway = (self.model.status == 'Live' and self.model.inningHalf == "Top")
        highlightHome = (self.model.status == 'Live' and self.model.inningHalf == "Bottom")

        away_score_group = self._team_score_group(self.model.away.teamName, self.model.away.runs, highlightAway )
        away_score_group.x = 5
        away_score_group.y = 25
        main_group.append(away_score_group)

        home_score_group = self._team_score_group(self.model.home.teamName, self.model.home.runs, highlightHome )
        home_score_group.x = 100
        home_score_group.y = 25
        main_group.append(home_score_group)

        innings = self._innings_group()
        innings.x = 5
        innings.y = 70
        main_group.append(innings)

        runs_hits_errors = self._runs_hits_errors_group()
        runs_hits_errors.x = 235
        runs_hits_errors.y = innings.y
        main_group.append(runs_hits_errors)

        if self.model.status == 'Live':
            current_inning = self._current_inning_group()
            current_inning.x = 205
            current_inning.y = 27
            main_group.append(current_inning)

            balls_strikes_label = label.Label(terminalio.FONT, text=f'{self.model.balls}-{self.model.strikes}', color=0x000000)
            balls_strikes_label.anchor_point = (0, 0)
            balls_strikes_label.anchored_position = (205, 45)
            main_group.append(balls_strikes_label)

            diamond = self._baseball_diamond_group(self.model.postOnFirst, self.model.postOnSecond, self.model.postOnThird, self.model.outs)
            diamond.x = 240
            diamond.y = 23
            main_group.append(diamond)
        
        display.show(main_group)
        display.refresh()

    def _header_group(self):
        header_height = 18
        header_bg = 0x555555
        header_group = displayio.Group()

        top_bar = Rect(0, 0, 296, header_height, fill=header_bg)
        header_group.append(top_bar)

        # Default to showing the game start time
        header_time = utc_to_local(self.model.dateTimeUtc)
        if(self.model.status == "Live"):
            header_time = local_now()

        day_text = ( relative_day(header_time) or day_of_week(header_time) )
        header_text = f'{day_text}, {month_name(header_time)} {header_time.day} / {hour_12(header_time)}:{header_time.minute:02d} {ampm(header_time)}'

        time_label = label.Label(terminalio.FONT, text=header_text, color=0xFFFFFF, background_color=header_bg)
        time_label.anchor_point = (0, 0.5)
        time_label.anchored_position = (3, int(header_height/2))
        header_group.append(time_label)

        if self.model.status == 'Live' or self.model.status == 'Final':
            status_label = label.Label(terminalio.FONT, text=self.model.status, color=0xFFFFFF, background_color=header_bg)
            status_label.anchor_point = (1, 0.5)
            status_label.anchored_position = (293, int(header_height/2))
            header_group.append(status_label)

        return header_group

    def _team_score_group(self, teamName, runs, highlight = False):
        group_width = 90
        teamScore_group = displayio.Group()

        team_label = label.Label(terminalio.FONT, text=teamName, color=0x000000,
            padding_right=8, padding_left=8,
            padding_top=1, padding_bottom=19,
            background_color=0xAAAAAA if highlight else 0xFFFFFF )
        team_label.anchor_point = (0.5, 0)
        team_label.anchored_position = ((group_width/2), 0)
        teamScore_group.append(team_label)

        score_label = label.Label(self.helveticaBold16, text=str(runs), color=0x000000)
        score_label.anchor_point = (0.5, 0)
        score_label.anchored_position = ((group_width/2), 16)
        teamScore_group.append(score_label)

        return teamScore_group

    def _innings_group(self):
        innings_group = displayio.Group()

        team_abbrev_width = 21
        inning_box_width = 20
        inning_box_height = 18
        box_stroke = 1
        border_color = 0x000000

        away_label = label.Label(terminalio.FONT, text=self.model.away.teamAbbreviation, color=0x000000)
        away_label.anchor_point = (0, 0.5)
        away_label.anchored_position = (0, (inning_box_height * 1.5))
        innings_group.append(away_label)

        home_label = label.Label(terminalio.FONT, text=self.model.home.teamAbbreviation, color=0x000000)
        home_label.anchor_point = (0, 0.5)
        home_label.anchored_position = (0, ((inning_box_height * 2.5)-box_stroke) )
        innings_group.append(home_label)

        total_inning_boxes = max(len(self.model.innings), self.model.scheduledInnings)

        if total_inning_boxes > 11:
            inning_box_width = 16

        for i in range(total_inning_boxes):
            x = (team_abbrev_width + (i * (inning_box_width - box_stroke)))
            text_x = (x + (inning_box_width/2))

            inning_num = (i+1)
            
            inning_data = None
            for inn in self.model.innings:
                if inn.num == inning_num:
                    inning_data = inn

            inning_num_label = label.Label(terminalio.FONT, text=f"{inning_num}", color=0x000000)
            inning_num_label.anchor_point = (0.5, 0.5)
            inning_num_label.anchored_position = (text_x, (inning_box_height * 0.5))
            innings_group.append(inning_num_label)

            away_box = Rect(x, inning_box_height, inning_box_width, inning_box_height, fill=0xFFFFFF, outline=border_color, stroke=box_stroke)
            innings_group.append(away_box)
            home_box = Rect(x, ((2*inning_box_height) - box_stroke), inning_box_width, inning_box_height, fill=0xFFFFFF, outline=border_color, stroke=box_stroke)
            innings_group.append(home_box)

            if inning_data is not None:
                inning_away_label = label.Label(terminalio.FONT, text=f'{inning_data.awayRuns}', color=0x000000)
                inning_away_label.anchor_point = (0.5, 0.5)
                inning_away_label.anchored_position = (text_x, (inning_box_height * 1.5))
                innings_group.append(inning_away_label)

                inning_home_label = label.Label(terminalio.FONT, text=f'{inning_data.homeRuns}', color=0x000000)
                inning_home_label.anchor_point = (0.5, 0.5)
                inning_home_label.anchored_position = (text_x, ((inning_box_height * 2.5) - box_stroke) )
                innings_group.append(inning_home_label)

        return innings_group


    def _current_inning_group(self):
        current_inning_group = displayio.Group()

        if self.model.inningHalf == 'Top':
            top = Triangle(0,7 , 8,7 , 4,3, fill=0x000000)
            current_inning_group.append(top)

        if self.model.inningHalf == 'Bottom':
            bottom = Triangle(0,9 , 8,9 , 4,13, fill=0x000000)
            current_inning_group.append(bottom)

        num_label = label.Label(self.helveticaBold16, text=str(self.model.currentInning or '?'), color=0x000000)
        num_label.anchor_point = (0, 0.5)
        num_label.anchored_position = (11, 8)
        current_inning_group.append(num_label)

        return current_inning_group

    def _baseball_diamond_group(self, on_first: bool, on_second: bool, on_third: bool, outs: int):
        diamond = displayio.Group()
        base_size = 19
        base_spacing = 3
        out_circle_diameter = 6

        first = self._single_base_group(on_first, base_size)
        first.x = int(base_size - 1 + (2*base_spacing))
        first.y = int(math.floor(base_size/2) + base_spacing)

        second = self._single_base_group(on_second, base_size)
        second.x = int(math.floor(base_size/2) + base_spacing)
        second.y = 0

        third = self._single_base_group(on_third, base_size)
        third.x = 0
        third.y = int(math.floor(base_size/2) + base_spacing)

        diamond.append(first)
        diamond.append(second)
        diamond.append(third)

        circle_y = (third.y + base_size + 2)
        circle_x = ((second.x + (base_size/2)) - (out_circle_diameter + 2))
        for i in range(3):
            out_fill_color = 0x555555 if (outs or 0) > i else 0xFFFFFF
            x = circle_x + (i * (out_circle_diameter + 2))
            out_circle = Circle(int(x), int(circle_y), int(out_circle_diameter/2), fill=out_fill_color, outline=0x000000, stroke=1)
            diamond.append(out_circle)

        return diamond

    def _single_base_group(self, on_base: bool, size: int = 9):
        base_group = displayio.Group()

        mid = math.floor(size/2) # "middle" coordinate value

        border_color = 0x000000

        outer_top = Triangle(0,mid , size-1,mid , mid,0, fill=border_color)
        outer_btm = Triangle(0,mid , size-1,mid , mid,size-1, fill=border_color)
        base_group.append(outer_top)
        base_group.append(outer_btm)

        inner_fill = 0x555555 if on_base else 0xFFFFFF
        
        inner_top = Triangle(1,mid , size-2,mid , mid,1, fill=inner_fill)
        inner_btm = Triangle(1,mid , size-2,mid , mid,size-2, fill=inner_fill)
        base_group.append(inner_top)
        base_group.append(inner_btm)
        
        return base_group

    def _runs_hits_errors_group(self):
        rhe_group = displayio.Group()

        box_width = 20
        box_height = 18
        box_stroke = 1
        border_color = 0x000000

        for i in range(3):
            x = (i * (box_width - box_stroke))
            text_x = (x + (box_width/2))

            header_text = (['R','H','E'][i])
            attr = (['runs','hits','errors'][i])
            
            header_label = label.Label(terminalio.FONT, text=header_text, color=0x000000)
            header_label.anchor_point = (0.5, 0.5)
            header_label.anchored_position = (text_x, (box_height * 0.5))
            rhe_group.append(header_label)

            away_box = Rect(x, box_height, box_width, box_height, fill=0xFFFFFF, outline=border_color, stroke=box_stroke)
            rhe_group.append(away_box)
            home_box = Rect(x, ((2*box_height) - box_stroke), box_width, box_height, fill=0xFFFFFF, outline=border_color, stroke=box_stroke)
            rhe_group.append(home_box)

            inning_away_label = label.Label(terminalio.FONT, text=str(getattr(self.model.away, attr)), color=0x000000)
            inning_away_label.anchor_point = (0.5, 0.5)
            inning_away_label.anchored_position = (text_x, (box_height * 1.5))
            rhe_group.append(inning_away_label)

            inning_home_label = label.Label(terminalio.FONT, text=str(getattr(self.model.home, attr)), color=0x000000)
            inning_home_label.anchor_point = (0.5, 0.5)
            inning_home_label.anchored_position = (text_x, ((box_height * 2.5) - box_stroke) )
            rhe_group.append(inning_home_label)

        return rhe_group