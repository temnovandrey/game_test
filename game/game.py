"""
Класс игровой логики.
Управляет игровым циклом, столкновениями, спавном объектов, звуками и HUD.
"""
import pygame
import random
from game.player import Player
from game.enemy import Enemy
from game.item import Item


class Game:
    """Основной класс игры — управляет всеми объектами и логикой."""

    def __init__(self, screen: pygame.Surface):
        """
        Инициализация игры.

        Args:
            screen: Поверхность экрана (pygame.display.set_mode())
        """
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.width, self.height = screen.get_size()

        # Игровые объекты
        self.player = Player(100, 100)
        self.enemies: list[Enemy] = []
        self.items: list[Item] = []

        # Параметры игры
        self.total_items = 10
        self.collected_count = 0
        self.time_limit = 120  # секунд
        self.time_remaining = self.time_limit
        self.game_started = False
        self.game_over = False
        self.won = False

        # Шрифты
        self.font_large = pygame.font.SysFont("arial", 36, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 24)
        self.font_small = pygame.font.SysFont("arial", 18)

        # Звуки
        self.sound_coin = None
        self.sound_hit = None
        self.sound_win = None
        self.sound_lose = None
        self.sound_menu = None
        self.load_sounds()

    def load_sounds(self):
        """Загружает звуковые эффекты и фоновую музыку."""
        try:
            self.sound_coin = pygame.mixer.Sound("assets/sounds/coin.wav")
            self.sound_hit = pygame.mixer.Sound("assets/sounds/hit.wav")
            self.sound_win = pygame.mixer.Sound("assets/sounds/win.wav")
            self.sound_lose = pygame.mixer.Sound("assets/sounds/lose.wav")
            self.sound_menu = pygame.mixer.Sound("assets/sounds/menu_select.wav")
            pygame.mixer.music.load("assets/music/background.wav")
            pygame.mixer.music.set_volume(0.2)
        except pygame.error:
            # Если звуки не загрузились — игра работает без звука
            print("Внимание: звуковые файлы не найдены. Запустите generate_sounds.py")

    def init_game(self):
        """Инициализирует/перезапускает игру."""
        self.player.reset()
        self.collected_count = 0
        self.time_remaining = self.time_limit
        self.game_over = False
        self.won = False
        self.game_started = True
        self.spawn_enemies(5)
        self.spawn_items(10)

    def spawn_enemies(self, count: int = 5):
        """Создаёт врагов в случайных позициях (не рядом с игроком)."""
        self.enemies = []
        for _ in range(count):
            x = random.randint(0, self.width - 35)
            y = random.randint(0, self.height - 35)
            # Не спавним рядом с стартовой позицией игрока
            while abs(x - 100) < 150 and abs(y - 100) < 150:
                x = random.randint(0, self.width - 35)
                y = random.randint(0, self.height - 35)
            self.enemies.append(Enemy(x, y))

    def spawn_items(self, count: int = 10):
        """Создаёт собираемые предметы в случайных позициях."""
        self.items = []
        for _ in range(count):
            x = random.randint(20, self.width - 40)
            y = random.randint(60, self.height - 40)
            self.items.append(Item(x, y))

    def check_collisions(self):
        """Проверяет столкновения игрока с предметами и врагами."""
        player_rect = self.player.get_rect()

        # Игрок vs Предметы
        for item in self.items:
            if not item.is_collected() and player_rect.colliderect(item.get_rect()):
                item.collect()
                self.collected_count += 1
                self.player.add_score(10)
                if self.sound_coin:
                    self.sound_coin.play()

        # Игрок vs Враги
        for enemy in self.enemies:
            if player_rect.colliderect(enemy.get_rect()):
                self.player.take_damage(20)
                if self.sound_hit:
                    self.sound_hit.play()
                # Перемещаем врага на случайную сторону экрана
                edge = random.choice(["top", "bottom", "left", "right"])
                if edge == "top":
                    enemy.x = random.randint(0, self.width - 35)
                    enemy.y = 0
                elif edge == "bottom":
                    enemy.x = random.randint(0, self.width - 35)
                    enemy.y = self.height - 35
                elif edge == "left":
                    enemy.x = 0
                    enemy.y = random.randint(0, self.height - 35)
                else:
                    enemy.x = self.width - 35
                    enemy.y = random.randint(0, self.height - 35)

    def update(self):
        """Обновляет состояние всех игровых объектов."""
        if not self.game_started or self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.move(keys, self.width, self.height)

        for enemy in self.enemies:
            enemy.move(self.width, self.height)

        self.check_collisions()

        # Проверка условий победы/поражения
        if self.collected_count >= self.total_items:
            self.game_over = True
            self.won = True
            if self.sound_win:
                self.sound_win.play()

        if not self.player.is_alive():
            self.game_over = True
            self.won = False
            if self.sound_lose:
                self.sound_lose.play()

    def draw(self):
        """Отрисовывает все игровые объекты и HUD."""
        # Фон
        self.screen.fill((30, 30, 30))

        # Собираемые предметы
        for item in self.items:
            item.draw(self.screen)

        # Враги
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Игрок
        self.player.draw(self.screen)

        # HUD
        self._draw_hud()

        # Сообщение о победе/поражении
        if self.game_over:
            self._draw_game_over()

    def _draw_hud(self):
        """Отрисовывает интерфейс сверху экрана."""
        hud_height = 40
        hud_rect = pygame.Rect(0, 0, self.width, hud_height)
        pygame.draw.rect(self.screen, (50, 50, 50), hud_rect)
        pygame.draw.line(self.screen, (100, 100, 100), (0, hud_height), (self.width, hud_height), 2)

        # Очки
        score_text = self.font_small.render(f"Очки: {self.player.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        # Здоровье (полоска)
        health_ratio = self.player.health / self.player.max_health
        health_bar_x = 120
        health_bar_w = 100
        health_color = (0, 200, 0) if health_ratio > 0.5 else (255, 150, 0) if health_ratio > 0.25 else (255, 50, 50)
        pygame.draw.rect(self.screen, (100, 100, 100),
                         (health_bar_x, 8, health_bar_w, 20))
        pygame.draw.rect(self.screen, health_color,
                         (health_bar_x, 8, int(health_bar_w * health_ratio), 20))
        health_text = self.font_small.render("Здоровье", True, (255, 255, 255))
        self.screen.blit(health_text, (health_bar_x, 30))

        # Таймер
        timer_text = self.font_small.render(f"Время: {self.time_remaining}с", True, (255, 255, 255))
        self.screen.blit(timer_text, (250, 10))

        # Предметы
        items_text = self.font_small.render(f"Монеты: {self.collected_count}/{self.total_items}", True, (255, 215, 0))
        self.screen.blit(items_text, (400, 10))

    def _draw_game_over(self):
        """Отрисовывает экран окончания игры."""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        if self.won:
            title = self.font_large.render("ПОБЕДА!", True, (0, 255, 0))
        else:
            title = self.font_large.render("ИГРА ОКОНЧЕНА", True, (255, 50, 50))

        title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 80))
        self.screen.blit(title, title_rect)

        # Финальный счёт
        score_text = self.font_medium.render(f"Набранные очки: {self.player.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.width // 2, self.height // 2 - 30))
        self.screen.blit(score_text, score_rect)

        coins_text = self.font_medium.render(f"Собрано монет: {self.collected_count}/{self.total_items}", True, (255, 215, 0))
        coins_rect = coins_text.get_rect(center=(self.width // 2, self.height // 2 + 10))
        self.screen.blit(coins_text, coins_rect)

        # Подсказка
        hint = self.font_small.render("Нажмите ENTER для перезапуска или ESC для выхода в меню", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(self.width // 2, self.height // 2 + 60))
        self.screen.blit(hint, hint_rect)

    def handle_events(self):
        """
        Обрабатывает события PyGame во время игры.

        Returns:
            str: 'restart' — перезапуск, 'quit' — выход
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.game_over:
                    return "restart"
                if event.key == pygame.K_ESCAPE:
                    return "quit"

        return None

    def is_won(self) -> bool:
        """Возвращает True, если игрок собрал все монеты."""
        return self.collected_count >= self.total_items

    def is_lost(self) -> bool:
        """Возвращает True, если игрок проиграл."""
        return not self.player.is_alive()
