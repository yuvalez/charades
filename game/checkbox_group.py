from check_box import CheckBox


class CheckboxGroup:

    def __init__(self, categories, start_pos, check_box_size):
        self.group = []
        for idx, category in enumerate(categories):
            x, y = start_pos
            self.group.append(CheckBox(x, y + idx*check_box_size*1.5, check_box_size, None, category, True))

    def draw(self, screen):
        for button in self.group:
            button.draw(screen)

    def handle_event(self, event):
        for button in self.group:
            button.handle_event(event)

    def get_selected(self):
        return list(map(lambda b: b.get_text(), filter(lambda a: a.is_checked(), self.group)))
