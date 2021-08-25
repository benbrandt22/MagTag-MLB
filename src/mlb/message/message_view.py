import time
from adafruit_display_text import label
import fonts.fonts as FONTS
import board
import displayio

class MessageView:

    def __init__(self, message:str) -> None:
        self._message = message

    def render(self):
        print(f'Displaying message: {self._message}')

        display = board.DISPLAY
        
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

        # Message label
        message_label = label.Label(FONTS.OpenSans_12, text=self._message, color=0x000000)
        message_label.anchor_point = (0.5, 0.5)
        message_label.anchored_position = (display.width // 2, display.height // 2)
        main_group.append(message_label)

        # show the main group and refresh.
        display.show(main_group)
        display.refresh()

