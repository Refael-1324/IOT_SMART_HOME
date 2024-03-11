from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.properties import StringProperty


class ColoredLabel(BoxLayout):
    text = StringProperty('')  # Define a text property to bind to the Label widget's text

    def __init__(self, text, bg_color, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        with self.canvas.before:
            Color(*bg_color)  # Set the background color
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        self.label = Label(text=text)  # Use the internal Label widget
        self.add_widget(self.label)

        self.text = text  # Set the text property, which is now bound to the Label's text
        self.bind(text=self._update_label_text)  # Update the Label widget when text property changes

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def _update_label_text(self, instance, value):
        self.label.text = self.text  # Update the internal Label's text
