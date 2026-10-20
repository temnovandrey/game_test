"""
Класс главного персонажа игры.
Управляет движением, здоровьем, счётом и отрисовкой игрока.
"""
import pygame


class Player:
    """Главный персонаж — синий квадрат, управляемый стрелками/WASD."""

    def __init__(self, x: int = 100, y: int = 100):
        """
        Инициализация игрока.

        Args:
            x: Начальная позиция по горизонтали
            y: Начальная позиция по вертикали
        """
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.score = 0
        self.color = (0, 150, 255)  # Синий
        self.invincible_timer = 0  # Таймер неуязвимости после получения урона

    def move(self, keys: dict, screen_width: int, screen_height: int):
        """
        Перемещает игрока на основе нажатых клавиш.
        Поддерживает стрелки и WASD.

        Args:
            keys: Состояние клавиш (pygame.key.get_pressed())
            screen_width: Ширина игрового экрана
            screen_height: Высота игрового экрана
        """
        # Стрелки
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed

        # Ограничение в пределах экрана
        self.x = max(0, min(self.x, screen_width - self.width))
        self.y = max(0, min(self.y, screen_height - self.height))

    def take_damage(self, amount: int = 20):
        """
        Получает урон. Если игрок неуязвим — урон не применяется.

        Args:
            amount: Количество получаемого урона
        """
        if self.invincible_timer > 0:
            return
        self.health = max(0, self.health - amount)
        self.invincible_timer = 18  # 0.3 секунды при 60 FPS

    def add_score(self, amount: int = 10):
        """
        Добавляет очки.

        Args:
            amount: Количество добавляемых очков
        """
        self.score += amount

    def get_rect(self) -> pygame.Rect:
        """Возвращает pygame.Rect для проверки столкновений."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def is_alive(self) -> bool:
        """Проверяет, жив ли игрок."""
        return self.health > 0

    def draw(self, surface: pygame.Surface):
        """
        Отрисовывает игрока и полоску здоровья.

        Args:
            surface: Поверхность для отрисовки
        """
        # Мигание белым при неуязвимости
        color = self.color
        if self.invincible_timer > 0:
            if (self.invincible_timer // 3) % 2 == 0:
                color = (255, 255, 255)
            self.invincible_timer -= 1

        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))

        # Полоска здоровья над персонажем
        bar_width = self.width
        bar_height = 6
        health_ratio = self.health / self.max_health
        # Фон полоски
        pygame.draw.rect(surface, (100, 100, 100),
                         (self.x, self.y - 10, bar_width, bar_height))
        # Заполнение
        fill_color = (0, 255, 0) if health_ratio > 0.5 else (255, 200, 0) if health_ratio > 0.25 else (255, 50, 50)
        pygame.draw.rect(surface, fill_color,
                         (self.x, self.y - 10, int(bar_width * health_ratio), bar_height))

    def reset(self):
        """Сбрасывает игрока к начальному состоянию."""
        self.x = self.start_x
        self.y = self.start_y
        self.health = self.max_health
        self.score = 0
        self.invincible_timer = 0
