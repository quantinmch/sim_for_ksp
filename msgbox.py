from collections import deque
import time
import pi3d

log = deque([])
cmd = deque([])


class TextData(object):
    data = ""
    fps = 0

text_data = TextData()

class Msgbox():
    def __init__(self, display):
        self.prev_queue_size = 0

        self.text = pi3d.PointText(display.pointFont, display.CAMERA2D, max_chars=400, point_size=64)
        newtxt = pi3d.TextBlock(-600, 300, 100, 0.0, 100, data_obj=text_data, attr="data",
                text_format="{:s}", size=0.4, spacing="C", space=0.4, justify = 0,
                colour=(0.5, 0.5 , 1.0, 1.0))
        self.text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(-600, 330, 100, 0.0, 100, data_obj=text_data, attr="fps",
                text_format="{:d} fps", size=0.4, spacing="C", space=0.4, justify = 0,
                colour=(1, 0.5 , 0.5, 1.0))
        self.text.add_text_block(newtxt)

        self.t_end = 0

        self.disconnectedText = pi3d.FixedString('fonts/B612-Bold.ttf', "DISCONNECTED", font_size=35, background_color='red',
                                camera=display.CAMERA2D, justify='C', shader=display.flatsh, f_type='SMOOTH')
        self.disconnectedText.sprite.position(0, 300, 2)


    def display_text(self):
        if len(log) != self.prev_queue_size and log:
            text_data.data = "LOG : " + log.popleft()  # Remove the item from the front of the queue
            self.t_end = time.time() + 2
            
        if time.time() > self.t_end:
            text_data.data = ""

        self.text.regen()
        self.text.draw()
        self.prev_queue_size = len(log)

    def display_disconnected(self):
        self.disconnectedText.draw()
        
    def display_fps(self, fps):
        text_data.fps = fps