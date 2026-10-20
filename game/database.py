"""
Модуль управления базой данных SQLite3.
Хранит таблицу лидеров с именами игроков и их очками.
"""
import sqlite3
from typing import List, Tuple


class DatabaseManager:
    """Класс для взаимодействия с базой данных SQLite3."""

    def __init__(self, db_path: str = "leaderboard.db"):
        """
        Инициализация подключения к базе данных.
        Автоматически создаёт таблицу leaderboard при первом вызове.

        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
        self.conn = None
        self.init_db()

    def init_db(self):
        """Создаёт подключение и таблицу leaderboard, если она не существует."""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                game_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def insert_score(self, player_name: str, score: int):
        """
        Сохраняет результат игрока в таблицу лидеров.

        Args:
            player_name: Никнейм игрока
            score: Набранные очки
        """
        if not self.conn:
            self.init_db()
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO leaderboard (player_name, score) VALUES (?, ?)",
                (player_name, score)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

    def get_top_5(self) -> List[Tuple]:
        """
        Возвращает топ-5 игроков, отсортированных по убыванию очков.

        Returns:
            Список кортежей (player_name, score, game_date)
        """
        if not self.conn:
            self.init_db()
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT player_name, score, game_date 
                FROM leaderboard 
                ORDER BY score DESC 
                LIMIT 5
            """)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")
            return []

    def close(self):
        """Закрывает подключение к базе данных."""
        if self.conn:
            self.conn.close()
