import random
from dataclasses import dataclass
from time import monotonic
import pygame
import sys

image_path = '/data/data/com.kostyhub.createword/files/app/'

@dataclass
class Mode:
    name: str
    words: set[str]

@dataclass
class Player:
    money = 0
    experience = 0

modes = [
    Mode('easy', words={'e012', 'e01234', 'e0156'}),
    Mode('medium', words={'m00000000', 'm000111', 'm010101010101'}),
    Mode('hard', words={'h0ghgh12', 'h7dfgsdgfs', 'h345hfhdfh'}),
]

screen: pygame.Surface
screen_scale = 700
screen_width = screen_scale / 2.16
screen_height = screen_scale

scenes = {'menu': None, 'game': None, 'leaderboard': None}
scene = None

# events = []

class Styles:
    def __init__(self):
        # h - href
        # bg - background
        # col - color
        # ft - font
        # cr - corner radius
        # act - active
        # de - not

        self.h1_ft = pygame.font.SysFont('cambria', 40)
        self.h2_ft = pygame.font.SysFont('consolas', 35)
        self.h3_ft = pygame.font.SysFont('consolas', 20)
        self.bg_col = '#59D5E0'
        self.h_col = '#030637'
        self.h_act_col = '#720455'
        self.h_de_act_col = '#910A67'

        self.settings_bg_col = '#F5DD61'
        self.settings_bg_cr = 20
        self.settings_close_col = '#F4538A'

        self.game_letter_ft = pygame.font.SysFont('cambria', 30)
        self.game_letter_col = '#F5DD61'
st: Styles

sounds = True
selected_mode_index = 0

# complete_levels_count = 0

def exit_app():
    pygame.quit()
    sys.exit()

def set_scene(name):
    global scene

    scene = scenes[name]
    scene.on_start()

def btn(screen: pygame.Surface, text: str, center: tuple[float, float], on_click=None, active=True) -> pygame.Rect:
    text = st.h3_ft.render(text, True, st.h_col if active else st.h_de_act_col)
    text_rect = text.get_rect(center=center)
    screen.blit(text, text_rect)
    rect = text_rect
    rect.w += 20
    rect.h += 20
    rect.x -= 10
    rect.y -= 10
    pygame.draw.rect(screen, st.h_col, rect, 2, 10)
    if active and on_click is not None:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(event.pos):
                on_click()
    return rect

class Window:
    def __init__(self, screen: pygame.Surface, title: str or None = None, content=None, width=250, height=155,
                 pos: (int, int) or None = None, show=True):
        self.screen = screen
        self.title = title
        self.content = content
        self.width = width
        self.height = height
        self.pos = (screen.get_width() - width) / 2, 230 if pos is None else pos
        self.show = show

    def render(self):
        if not self.show: return

        pygame.draw.rect(
            self.screen,
            st.settings_bg_col,
            pygame.Rect(self.pos, (self.width, self.height)),
            0,
            st.settings_bg_cr,
        )

        close_btn_rect = pygame.Rect(self.pos[0] + self.width - 20, self.pos[1] - 20, 40, 40)
        close_btn = pygame.transform.scale(pygame.image.load(image_path + 'assets\\close.png'), close_btn_rect.size)
        self.screen.blit(close_btn, close_btn_rect)

        if self.title is not None:
            title = st.h2_ft.render(self.title, True, st.h_col)
            title_rect = title.get_rect(center=(self.pos[0] + self.width / 2, self.pos[1] + 35))
            self.screen.blit(title, title_rect)

        if self.content is not None: self.content(self)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and close_btn_rect.collidepoint(event.pos):
                self.show = False

class Menu:
    @staticmethod
    def settings_window_content(window: Window):
        global sounds

        sound_button_rect = pygame.Rect(window.pos[0] + (window.width - 70) / 2 - 45, window.pos[1] + 35 + 30, 70, 70)
        sound_button = pygame.transform.scale(
            pygame.image.load(image_path + 'assets\\sound-on.png' if sounds else image_path + 'assets\\sound-off.png'),
            sound_button_rect.size,
        )
        window.screen.blit(sound_button, sound_button_rect)

        exit_button_rect = pygame.Rect(window.pos[0] + (window.width - 70) / 2 + 45, window.pos[1] + 35 + 30, 70, 70)
        exit_button = pygame.transform.scale(
            pygame.image.load(image_path + 'assets\\exit2.png'),
            exit_button_rect.size,
        )
        window.screen.blit(exit_button, exit_button_rect)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if sound_button_rect.collidepoint(event.pos): sounds = not sounds
                if exit_button_rect.collidepoint(event.pos): window.show = False

    @staticmethod
    def set_complexity_window_content(window: Window):
        global selected_mode_index

        for i, e in enumerate(['Легко', 'Нормально', 'Сложно']):
            selected = i == selected_mode_index
            text = st.h3_ft.render(f'> {e}  ' if selected else e, True, st.h_act_col if selected else st.h_col)
            text_rect = text.get_rect(center=(window.pos[0] + window.width / 2, window.pos[1] + 35 + 35 + i * 25))
            window.screen.blit(text, text_rect)

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and text_rect.collidepoint(event.pos):
                    selected_mode_index = i
                    # set_scene('game')

            btn(screen, '       Старт       ', center=(window.pos[0] + window.width / 2, window.pos[1] + 160),
                on_click=lambda: set_scene('game'))

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.settings_window = Window(screen, 'Настройки', self.settings_window_content, show=False)
        self.set_complexity_window = Window(screen, 'Сложность', self.set_complexity_window_content, show=False,
                                            height=190)

    def on_start(self):
        self.settings_window.show = False
        self.set_complexity_window.show = False

    def render(self):
        # update = False
        # for event in events:
        #     if event.type in (pygame.WINDOWSHOWN, pygame.MOUSEBUTTONDOWN): update = True
        # if not update: return

        screen.fill(st.bg_col)

        game_name = st.h1_ft.render('Составь слово!', True, st.h_col)
        game_name_rect = game_name.get_rect(center=(screen.get_width() / 2, 100))
        screen.blit(game_name, game_name_rect)

        play_text = st.h2_ft.render('Старт', True, st.h_col)
        play_text_rect = play_text.get_rect(center=(screen.get_width() / 2, 250))
        screen.blit(play_text, play_text_rect)

        settings_text = st.h2_ft.render('Настройки', True, st.h_col)
        settings_text_rect = settings_text.get_rect(center=(screen.get_width() / 2, 250 + 60))
        screen.blit(settings_text, settings_text_rect)

        exit_text = st.h2_ft.render('Выход', True, st.h_col)
        exit_text_rect = exit_text.get_rect(center=(screen.get_width() / 2, 250 + 60 * 2))
        screen.blit(exit_text, exit_text_rect)

        if not (self.set_complexity_window.show or self.settings_window.show):
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_text_rect.collidepoint(event.pos): self.set_complexity_window.show = True
                    if settings_text_rect.collidepoint(event.pos): self.settings_window.show = True
                    if exit_text_rect.collidepoint(event.pos): exit_app()
        else:
            self.settings_window.render()
            self.set_complexity_window.render()

class Game:
    # region word
    level_completed = False

    word: str = '01234567'
    up_letters_indexes = []
    down_letters_indexes = [i for i in range(len(word))]

    clues_letters_indexes = [i for i in range(len(word))]
    active_clues_count = 0

    def complete_level(self):
        self.level_completed = True
        self.win_window.show = True

    def try_add_up_letter(self, letter_index: int) -> bool:
        if self.level_completed or letter_index in self.up_letters_indexes: return False
        self.up_letters_indexes.append(letter_index)

        if len(self.up_letters_indexes) == len(self.word):
            word = ''.join([self.word[e] for e in self.up_letters_indexes])
            if word == self.word: self.complete_level()

        return True
    def try_remove_up_letter(self, letter_index: int) -> bool:
        if self.level_completed or len(self.up_letters_indexes) <= letter_index: return False
        self.up_letters_indexes.pop(letter_index)
        return True
    def try_remove_end_up_letter(self) -> bool:
        if self.level_completed or len(self.up_letters_indexes) < 1: return False
        self.up_letters_indexes.pop()
        return True
    def try_clear_up_letters(self) -> bool:
        if self.level_completed: return False
        self.up_letters_indexes.clear()
        return True
    # endregion

    def question_window_content(self, window: Window):
        word = ['?'] * len(self.word)
        for i in range(self.active_clues_count):
            word[self.clues_letters_indexes[i]] = \
                self.word[self.clues_letters_indexes[i]]
        word = ''.join(word)

        word = st.h2_ft.render(word, True, st.h_col)
        word_rect = word.get_rect(center=(window.pos[0] + window.width / 2, window.pos[1] + 35 + 50))
        self.screen.blit(word, word_rect)

        can_by_letter = len(self.clues_letters_indexes) > self.active_clues_count

        def try_by_letter():
            if can_by_letter: self.active_clues_count += 1

        btn(window.screen, 'Купить букву (1$)', center=(window.pos[0] + window.width / 2, window.pos[1] + 35 + 100),
            on_click=try_by_letter, active=can_by_letter)

        # by_letter = st.h3_ft.render('Купить букву (1$)', True, st.h_act_col if can_by_letter else st.h_de_act_col)
        # by_letter_rect = by_letter.get_rect(center=(window.pos[0] + window.width / 2, window.pos[1] + 35 + 100))
        # self.screen.blit(by_letter, by_letter_rect)
        # if can_by_letter:
        #     for event in events:
        #         if event.type == pygame.MOUSEBUTTONDOWN and by_letter_rect.collidepoint(event.pos):
        #             self.active_clues_count += 1

    def win_window_content(self, window: Window):
        text = st.h3_ft.render('+2$, +10XP', True, st.h_col)
        text_rect = text.get_rect(center=(window.pos[0] + window.width / 2, 305))
        self.screen.blit(text, text_rect)

        btn(window.screen, 'Следующий уровень >', center=(window.pos[0] + window.width / 2, 355),
            on_click=lambda: set_scene('game'))

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.question_window = Window(screen, 'Подсказка', self.question_window_content, show=False, height=170)
        self.win_window = Window(screen, 'Ты победил!', self.win_window_content, show=False)

    def on_start(self):
        self.question_window.show = False
        self.win_window.show = False

        self.level_completed = False

        self.word = random.choice(list(modes[selected_mode_index].words)).upper()

        self.up_letters_indexes = []
        self.down_letters_indexes = [i for i in range(len(self.word))]
        random.shuffle(self.down_letters_indexes)
        self.clues_letters_indexes = [i for i in range(len(self.word))]
        random.shuffle(self.clues_letters_indexes)
        self.active_clues_count = 0

    def render(self):
        screen.fill(st.bg_col)

        game_name = st.h1_ft.render('Составь слово!', True, st.h_col)
        game_name_rect = game_name.get_rect(center=(screen.get_width() / 2, 50))
        screen.blit(game_name, game_name_rect)

        cell_size = (30, 30)
        cells_line_max_length = 8
        gap = (2, 5)
        center_x = (screen_width - min(len(self.word), cells_line_max_length) * (cell_size[0] + gap[0])) / 2

        def get_rect(index: int, padding_top=200) -> pygame.Rect:
            return pygame.Rect(
                center_x + index % cells_line_max_length * (cell_size[0] + gap[0]),
                padding_top + index // cells_line_max_length * (cell_size[1] + gap[1]),
                cell_size[0],
                cell_size[0]
            )

        def letter_cell(value: str or None, rect: pygame.Rect, on_click):
            pygame.draw.rect(self.screen, '#030637', rect, 0 if value else 2, 5)

            text = st.game_letter_ft.render(value, True, st.game_letter_col)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(event.pos):
                    on_click()

        for i in range(len(self.word)):
            letter = self.word[self.up_letters_indexes[i]] if len(self.up_letters_indexes) > i else None
            letter_cell(letter, get_rect(i, 200), lambda: self.try_remove_up_letter(i))

        for i in range(len(self.word)):
            letter_cell(None if self.down_letters_indexes[i] in self.up_letters_indexes else
                        self.word[self.down_letters_indexes[i]], rect := get_rect(i, 270),
                        lambda: self.try_add_up_letter(self.down_letters_indexes[i]))

        gap = 20
        size = 50
        count = 4
        x_positions = [(screen_width - count * size - (count - 1) * gap) / 2 + i * (size + gap) for i in range(count)]

        home_btn_rect = pygame.Rect(x_positions[0], screen_height - 70, size, size)
        home_btn = pygame.transform.scale(pygame.image.load(image_path + 'assets\\home.png'), home_btn_rect.size)
        self.screen.blit(home_btn, home_btn_rect)

        question_btn_rect = pygame.Rect(x_positions[1], screen_height - 70, size, size)
        question_btn = pygame.transform.scale(pygame.image.load(image_path + 'assets\\question.png'), question_btn_rect.size)
        self.screen.blit(question_btn, question_btn_rect)

        clear_btn_rect = pygame.Rect(x_positions[2], screen_height - 70, size, size)
        clear_btn = pygame.transform.scale(pygame.image.load(image_path + 'assets\\reset.png'), clear_btn_rect.size)
        self.screen.blit(clear_btn, clear_btn_rect)

        bcsp_btn_rect = pygame.Rect(x_positions[3], screen_height - 70, size, size)
        bcsp_btn = pygame.transform.scale(pygame.image.load(image_path + 'assets\\delete.png'), bcsp_btn_rect.size)
        self.screen.blit(bcsp_btn, bcsp_btn_rect)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if home_btn_rect.collidepoint(event.pos):
                    set_scene('menu')
                if not self.level_completed:
                    if question_btn_rect.collidepoint(event.pos):
                        self.question_window.show = True
                    if clear_btn_rect.collidepoint(event.pos):
                        self.try_clear_up_letters()
                    if bcsp_btn_rect.collidepoint(event.pos):
                        self.try_remove_end_up_letter()

        # text = st.h3_ft.render('Подсказка', True, st.h_col)
        # text_rect = text.get_rect(center=(screen_width / 2 - 100, 370))
        # self.screen.blit(text, text_rect)
        #
        # text = st.h3_ft.render('Сбросить', True, st.h_col)
        # text_rect = text.get_rect(center=(screen_width / 2, 370))
        # self.screen.blit(text, text_rect)
        #
        # text = st.h3_ft.render('Стереть', True, st.h_col)
        # text_rect = text.get_rect(center=(screen_width / 2 + 100, 370))
        # self.screen.blit(text, text_rect)

        self.question_window.render()
        self.win_window.render()

def main():
    global screen
    global st
    global events
    global scenes

    pygame.init()
    screen = pygame.display.set_mode((screen_scale / 2.16, screen_scale))
    st = Styles()

    scenes['menu'] = Menu(screen)
    scenes['game'] = Game(screen)

    set_scene('menu')

    while True:
        events = pygame.event.get()

        scene.render()

        for event in events:
            if event.type == pygame.QUIT: exit_app()
        pygame.display.flip()

if __name__ == '__main__': main()