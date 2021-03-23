from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior

from utill.StableBoolean import StableBoolean


class ComplexButton(ButtonBehavior):
    def __init__(self, is_hover=True, **kwargs):
        super().__init__(**kwargs)

        self.r = 0

        if is_hover:
            self.is_mouse_over = StableBoolean(false_threshold=3)
            Window.bind(mouse_pos=self.mouse_over_ani)
            self.bind(on_press=self.on_press)

    def mouse_over_ani(self, src, mouse_pos):
        self.r = self.size[0] / 2

        x, y = self.pos
        x = x + self.r
        y = y + self.r

        m_x, m_y = mouse_pos

        y_ready = abs(m_y - y) <= self.r
        x_ready = abs(m_x - x) <= self.r

        self.is_mouse_over.update(x_ready and y_ready)

        if self.state == 'down':
            pass

        elif self.is_mouse_over.out_val and self.state == 'normal':
            self.opacity = 1

        else:
            self.opacity = 1

    def on_press(self, *args):
        self.opacity = 0.3
