"""
Класс врага.
Красные квадраты, которые двигаются по экрану и наносят урон при столкновении.
"""
import pygame
import random


class Enemy:
    """Враг — красный квадрат с непредсказуемым движением."""

    def __init__(self, x: int, y: int, speed: int = 2):
        """
        Инициализация врага.

        Args:
            x: Начальная позиция по горизонтали
            y: Начальная позиция по вертикали
            speed: Скорость движения
        """
        self.x = x
        self.y = y
        self.width = 35
        self.height = 35
        self.speed = speed
        # Случайное начальное направление
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        if dx == 0 and dy == 0:
            dx = 1
        self.direction = (dx, dy)
        self.color = (255, 50, 50)  # Красный
        self.change_timer = 0
        self.change_interval = random.randint(60, 120)  # Смена направления каждые 1-2 сек

    def move(self, screen_width: int, screen_height: int):
        """
        Двигает врага. Отскакивает от стен, случайно меняет направление.

        Args:
            screen_width: Ширина игрового экрана
            screen_height: Высота игрового экрана
        """
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed

        # Отскок от стен
        if self.x <= 0:
            self.x = 0
            self.direction = (1, self.direction[1])
        elif self.x + self.width >= screen_width:
            self.x = screen_width - self.width
            self.direction = (-1, self.direction[1])

        if self.y <= 0:
            self.y = 0
            self.direction = (self.direction[0], 1)
        elif self.y + self.height >= screen_height:
            self.y = screen_height - self.height
            self.direction = (self.direction[0], -1)

        # Случайная смена направления
        self.change_timer += 1
        if self.change_timer >= self.change_interval:
            self.change_timer = 0
            self.change_interval = random.randint(60, 120)
            self.direction = (
                random.choice([-1, 0, 1]),
                random.choice([-1, 0, 1])
            )
            # Убедимся, что направление не нулевое
            if self.direction == (0, 0):
                self.direction = (1, 0)

    def draw(self, surface: pygame.Surface):
        """Отрисовывает врага."""
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        # Глаза (для визуального различия)
        eye_size = 5
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 10), int(self.y + 10)), eye_size)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 25), int(self.y + 10)), eye_size)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 11), int(self.y + 11)), 2)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 26), int(self.y + 11)), 2)

    def get_rect(self) -> pygame.Rect:
        """Возвращает pygame.Rect для проверки столкновений."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def reset(self, x: int, y: int):
        """Перемещает врага в новую позицию."""
        self.x = x
        self.y = y
        self.direction = (random.choice([-1, 1]), random.choice([-1, 1]))
