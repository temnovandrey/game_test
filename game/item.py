"""
Класс собираемого предмета (монеты).
Золотые круги, которые нужно собирать для набора очков.
"""
import pygame
import random


class Item:
    """Собираемый предмет — золотой круг."""

    def __init__(self, x: int, y: int):
        """
        Инициализация предмета.

        Args:
            x: Позиция по горизонтали
            y: Позиция по вертикали
        """
        self.x = x
        self.y = y
        self.radius = 12
        self.color = (255, 215, 0)  # Золотой
        self.collected = False
        self.bob_timer = random.uniform(0, 6.28)  # Для анимации "парения"

    def draw(self, surface: pygame.Surface):
        """
        Отрисовывает предмет с анимацией парения.

        Args:
            surface: Поверхность для отрисовки
        """
        if self.collected:
            return

        self.bob_timer += 0.05
        bob_offset = math.sin(self.bob_timer) * 2

        # Свечение
        pygame.draw.circle(surface, (255, 255, 150),
                           (int(self.x), int(self.y + bob_offset)),
                           self.radius + 3)
        # Основной круг
        pygame.draw.circle(surface, self.color,
                           (int(self.x), int(self.y + bob_offset)),
                           self.radius)
        # Блик
        pygame.draw.circle(surface, (255, 255, 200),
                           (int(self.x) - 3, int(self.y + bob_offset) - 3),
                           4)

    def get_rect(self) -> pygame.Rect:
        """Возвращает pygame.Rect для проверки столкновений."""
        if self.collected:
            return pygame.Rect(-100, -100, 0, 0)  # Невидимый
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def collect(self):
        """Отмечает предмет как собранный."""
        self.collected = True

    def is_collected(self) -> bool:
        """Проверяет, собран ли предмет."""
        return self.collected

    def reset(self, x: int, y: int):
        """Восстанавливает предмет в новой позиции."""
        self.x = x
        self.y = y
        self.collected = False
        self.bob_timer = random.uniform(0, 6.28)


# Импортируем math для анимации
import math
