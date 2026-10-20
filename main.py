"""
Collection Game — Игра на PyGame с SQLite3.

Управление: стрелки или WASD
Цель: собрать все 10 монет, избегая красных врагов.
У вас 2 минуты и 100 очков здоровья.

Запуск: python main.py
"""
import pygame
import sys
from enum import Enum
from datetime import datetime

from game.database import DatabaseManager
from game.game import Game


class GameState(Enum):
    """Состояния игры."""
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    LEADERBOARD = 3


class Button:
    """Кнопка для меню."""

    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = (80, 80, 80)
        self.hover_color = (120, 120, 120)
        self.text_color = (255, 255, 255)

    def draw(self, surface: pygame.Surface, mouse_pos: tuple):
        """Отрисовывает кнопку."""
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (150, 150, 150), self.rect, 2, border_radius=8)

        text_surface = pygame.font.SysFont("arial", 20, bold=True).render(
            self.text, True, self.text_color
        )
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def clicked(self, mouse_pos: tuple) -> bool:
        """Проверяет, была ли нажата кнопка."""
        return self.rect.collidepoint(mouse_pos)


class TextInput:
    """Поле ввода текста (никнейм)."""

    def __init__(self, x: int, y: int, width: int, max_length: int = 20):
        self.rect = pygame.Rect(x, y, width, 40)
        self.text = ""
        self.max_length = max_length
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event: pygame.event.Event):
        """Обрабатывает события клавиатуры."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return "enter"
            elif len(self.text) < self.max_length:
                if event.unicode and event.unicode.isalnum():
                    self.text += event.unicode

        return None

    def draw(self, surface: pygame.Surface):
        """Отрисовывает поле ввода."""
        # Рамка
        border_color = (100, 150, 255) if self.active else (100, 100, 100)
        pygame.draw.rect(surface, border_color, self.rect, border_radius=6)
        pygame.draw.rect(surface, (60, 60, 60), self.rect, 2, border_radius=6)

        # Текст
        font = pygame.font.SysFont("arial", 20)
        text_surface = font.render(self.text, True, (255, 255, 255))

        # Курсор
        cursor_x = self.rect.x + 8 + text_surface.get_width() + 2
        self.cursor_timer += 1
        if self.active and (self.cursor_timer // 20) % 2 == 0:
            pygame.draw.line(surface, (255, 255, 255),
                             (cursor_x, self.rect.y + 5),
                             (cursor_x, self.rect.y + 35))

        surface.blit(text_surface, (self.rect.x + 8, self.rect.y + 10))

    def is_empty(self) -> bool:
        """Проверяет, пустое ли поле."""
        return len(self.text.strip()) == 0


def draw_menu(screen: pygame.Surface, name_input: TextInput,
              buttons: list[Button], mouse_pos: tuple):
    """Отрисовывает главное меню."""
    screen.fill((25, 25, 35))

    # Заголовок
    title_font = pygame.font.SysFont("arial", 48, bold=True)
    title = title_font.render("COLLECTION GAME", True, (255, 255, 255))
    title_rect = title.get_rect(center=(screen.get_width() // 2, 60))
    screen.blit(title, title_rect)

    # Подзаголовок
    subtitle = pygame.font.SysFont("arial", 18).render(
        "Собирайте монеты, избегайте врагов!", True, (180, 180, 180)
    )
    subtitle_rect = subtitle.get_rect(center=(screen.get_width() // 2, 105))
    screen.blit(subtitle, subtitle_rect)

    # Поле ввода имени
    name_label = pygame.font.SysFont("arial", 22).render("Введите ваше имя:", True, (200, 200, 200))
    screen.blit(name_label, (name_input.rect.x, name_input.rect.y - 30))
    name_input.draw(screen)

    # Кнопки
    for btn in buttons:
        btn.draw(screen, mouse_pos)

    # Инструкция
    instructions_y = 380
    instructions = [
        "📋 ИНСТРУКЦИЯ:",
        "",
        "• Управление: стрелки или WASD",
        "• Соберите все 10 золотых монет для победы",
        "• Избегайте красных врагов — они наносят урон!",
        "• У вас 100 здоровья и 2 минуты",
        "• После удара вы briefly неуязвимы (мигание)",
        "",
        "Нажмите ENTER для начала игры",
    ]

    for i, line in enumerate(instructions):
        if line.startswith("📋"):
            color = (100, 200, 255)
            size = 20
        elif line.startswith("•"):
            color = (180, 180, 180)
            size = 18
        elif line.startswith("Нажмите"):
            color = (100, 255, 100)
            size = 18
        else:
            color = (150, 150, 150)
            size = 18

        font = pygame.font.SysFont("arial", size)
        text = font.render(line, True, color)
        screen.blit(text, (50, instructions_y + i * 24))


def draw_game_over(screen: pygame.Surface, game: Game, player_name: str,
                   buttons: list[Button], mouse_pos: tuple):
    """Отрисовывает экран окончания игры."""
    screen.fill((25, 25, 35))

    if game.won:
        title = pygame.font.SysFont("arial", 56, bold=True).render(
            "ПОБЕДА!", True, (0, 255, 100)
        )
    else:
        title = pygame.font.SysFont("arial", 48, bold=True).render(
            "ИГРА ОКОНЧЕНА", True, (255, 50, 50)
        )

    title_rect = title.get_rect(center=(screen.get_width() // 2, 80))
    screen.blit(title, title_rect)

    # Информация об игроке
    info_y = 160
    info_lines = [
        (f"Игрок: {player_name}", (200, 200, 200), 24),
        (f"Набранные очки: {game.player.score}", (255, 215, 0), 28),
        (f"Монет собрано: {game.collected_count}/{game.total_items}", (200, 200, 200), 22),
        (f"Осталось здоровья: {game.player.health}/{game.player.max_health}", (200, 200, 200), 22),
    ]

    for text, color, size in info_lines:
        font = pygame.font.SysFont("arial", size, bold=(size >= 28))
        surface = font.render(text, True, color)
        surface_rect = surface.get_rect(center=(screen.get_width() // 2, info_y))
        screen.blit(surface, surface_rect)
        info_y += 40

    # Кнопки
    for btn in buttons:
        btn.draw(screen, mouse_pos)

    hint = pygame.font.SysFont("arial", 16).render(
        "ENTER — начать заново | LEADERBOARD — таблица лидеров | MENU — в меню",
        True, (120, 120, 120)
    )
    screen.blit(hint, (screen.get_width() // 2, 540))


def draw_leaderboard(screen: pygame.Surface, db: DatabaseManager,
                     button: Button, mouse_pos: tuple):
    """Отрисовывает таблицу лидеров."""
    screen.fill((25, 25, 35))

    # Заголовок
    title = pygame.font.SysFont("arial", 40, bold=True).render(
        "ТОП-5 ИГРОКОВ", True, (255, 215, 0)
    )
    title_rect = title.get_rect(center=(screen.get_width() // 2, 50))
    screen.blit(title, title_rect)

    # Получаем данные
    top_players = db.get_top_5()

    if not top_players:
        no_data = pygame.font.SysFont("arial", 22).render(
            "Пока нет записей. Сыграйте первую игру!", True, (150, 150, 150)
        )
        no_rect = no_data.get_rect(center=(screen.get_width() // 2, 150))
        screen.blit(no_data, no_rect)
    else:
        # Таблица
        table_x = screen.get_width() // 2 - 250
        table_y = 100
        col_widths = [50, 200, 100, 150]  # #, Name, Score, Date

        # Заголовки столбцов
        headers = ["#", "Имя", "Очки", "Дата"]
        header_font = pygame.font.SysFont("arial", 18, bold=True)
        x = table_x
        for i, header in enumerate(headers):
            surface = header_font.render(header, True, (100, 200, 255))
            screen.blit(surface, (x, table_y))
            x += col_widths[i]

        # Разделитель
        pygame.draw.line(screen, (100, 100, 100),
                         (table_x, table_y + 25),
                         (table_x + sum(col_widths), table_y + 25), 2)

        # Строки
        row_font = pygame.font.SysFont("arial", 18)
        for idx, (name, score, date) in enumerate(top_players, 1):
            x = table_x
            row_y = table_y + 40 + (idx - 1) * 35

            # Номер
            rank_color = (255, 215, 0) if idx <= 3 else (180, 180, 180)
            surface = row_font.render(str(idx), True, rank_color)
            screen.blit(surface, (x, row_y))
            x += col_widths[0]

            # Имя
            surface = row_font.render(name[:18], True, (220, 220, 220))
            screen.blit(surface, (x, row_y))
            x += col_widths[1]

            # Очки
            surface = row_font.render(str(score), True, (255, 215, 0))
            screen.blit(surface, (x, row_y))
            x += col_widths[2]

            # Дата
            date_str = str(date)[:10] if date else "—"
            surface = row_font.render(date_str, True, (150, 150, 150))
            screen.blit(surface, (x, row_y))

    # Кнопка "Назад"
    button.draw(screen, mouse_pos)


def main():
    """Точка входа в игру."""
    pygame.init()
    pygame.mixer.init()

    # Экран
    WIDTH, HEIGHT = 900, 650
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Collection Game")
    clock = pygame.time.Clock()

    # База данных
    db = DatabaseManager()

    # Игровой объект
    game = Game(screen)

    # Состояние
    state = GameState.MENU
    player_name = ""
    name_input_active = False

    # Элементы меню
    name_input = TextInput(WIDTH // 2 - 120, 140, 240)
    menu_buttons = [
        Button(WIDTH // 2 - 150, 330, 140, 45, "НАЧАТЬ ИГРУ"),
        Button(WIDTH // 2 + 10, 330, 140, 45, "ЛИДЕРЫ"),
    ]
    gameover_buttons = [
        Button(WIDTH // 2 - 200, 460, 140, 45, "ЗАНОВО"),
        Button(WIDTH // 2 - 30, 460, 140, 45, "ЛИДЕРЫ"),
        Button(WIDTH // 2 + 140, 460, 140, 45, "МЕНЮ"),
    ]
    leaderboard_button = Button(WIDTH // 2 - 70, 540, 140, 45, "НАЗАД")

    # Таймер обратного отсчёта
    timer = pygame.time.get_ticks()
    countdown_active = False
    countdown_seconds = 3
    countdown_text = ""

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # --- MENU ---
            if state == GameState.MENU:
                # Автофокус на поле ввода при входе в меню
                if not name_input.active:
                    name_input.active = True

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Проверка кнопок
                    if menu_buttons[0].clicked(mouse_pos):
                        # Начало игры
                        if not name_input.is_empty():
                            player_name = name_input.text.strip()
                            countdown_active = True
                            countdown_seconds = 3
                            countdown_text = str(countdown_seconds)
                            state = GameState.PLAYING
                            timer = pygame.time.get_ticks()
                            if game.sound_menu:
                                game.sound_menu.play()
                    elif menu_buttons[1].clicked(mouse_pos):
                        state = GameState.LEADERBOARD
                        if game.sound_menu:
                            game.sound_menu.play()

                elif event.type == pygame.KEYDOWN:
                    result = name_input.handle_event(event)
                    if result == "enter" and not name_input.is_empty():
                        player_name = name_input.text.strip()
                        countdown_active = True
                        countdown_seconds = 3
                        countdown_text = str(countdown_seconds)
                        state = GameState.PLAYING
                        timer = pygame.time.get_ticks()
                        if game.sound_menu:
                            game.sound_menu.play()

            # --- PLAYING ---
            elif state == GameState.PLAYING:
                action = game.handle_events()
                if action == "restart":
                    game.init_game()
                    if game.sound_menu:
                        game.sound_menu.play()
                elif action == "quit":
                    state = GameState.MENU
                    name_input.text = player_name
                    name_input.active = True
                    if game.sound_menu:
                        game.sound_menu.play()

            # --- GAME_OVER ---
            elif state == GameState.GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if gameover_buttons[0].clicked(mouse_pos):
                        # Перезапуск
                        game.init_game()
                        state = GameState.PLAYING
                        if game.sound_menu:
                            game.sound_menu.play()
                    elif gameover_buttons[1].clicked(mouse_pos):
                        state = GameState.LEADERBOARD
                        if game.sound_menu:
                            game.sound_menu.play()
                    elif gameover_buttons[2].clicked(mouse_pos):
                        # Сохраняем результат в БД
                        db.insert_score(player_name, game.player.score)
                        game.game_over = False
                        game.game_started = False
                        state = GameState.MENU
                        name_input.active = True
                        if game.sound_menu:
                            game.sound_menu.play()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game.init_game()
                        state = GameState.PLAYING
                        if game.sound_menu:
                            game.sound_menu.play()
                    elif event.key == pygame.K_ESCAPE:
                        db.insert_score(player_name, game.player.score)
                        game.game_over = False
                        game.game_started = False
                        state = GameState.MENU
                        name_input.text = player_name
                        name_input.active = True
                        if game.sound_menu:
                            game.sound_menu.play()

            # --- LEADERBOARD ---
            elif state == GameState.LEADERBOARD:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if leaderboard_button.clicked(mouse_pos):
                        state = GameState.MENU
                        if game.sound_menu:
                            game.sound_menu.play()

        # --- Обновление ---
        if state == GameState.PLAYING:
            game.update()

            # Проверка окончания игры
            if game.game_over and state == GameState.PLAYING:
                state = GameState.GAME_OVER

            # Обратный отсчёт перед игрой
            if countdown_active:
                elapsed = (pygame.time.get_ticks() - timer) // 1000
                if elapsed >= countdown_seconds:
                    countdown_seconds -= 1
                    timer = pygame.time.get_ticks()
                    if countdown_seconds > 0:
                        countdown_text = str(countdown_seconds)
                    else:
                        countdown_active = False
                        countdown_text = "ВНИМАНИЕ!"
                        game.game_started = True

        # --- Отрисовка ---
        if state == GameState.MENU:
            draw_menu(screen, name_input, menu_buttons, mouse_pos)

        elif state == GameState.PLAYING:
            # Обратный отсчёт
            if countdown_active:
                screen.fill((30, 30, 30))
                font = pygame.font.SysFont("arial", 120, bold=True)
                if countdown_seconds > 0:
                    countdown_text = str(countdown_seconds)
                text = font.render(countdown_text, True, (255, 255, 255))
                text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(text, text_rect)

                hint = pygame.font.SysFont("arial", 20).render(
                    "Приготовьтесь!", True, (180, 180, 180)
                )
                hint_rect = hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
                screen.blit(hint, hint_rect)
            else:
                game.draw()

        elif state == GameState.GAME_OVER:
            # Сохраняем результат
            db.insert_score(player_name, game.player.score)
            draw_game_over(screen, game, player_name, gameover_buttons, mouse_pos)

        elif state == GameState.LEADERBOARD:
            draw_leaderboard(screen, db, leaderboard_button, mouse_pos)

        pygame.display.flip()
        clock.tick(60)

    # Закрытие
    db.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
