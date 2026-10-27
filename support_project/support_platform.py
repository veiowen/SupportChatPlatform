"""Учебная платформа обращений в поддержку. Только стандартная библиотека Python."""

import json
import random
from datetime import datetime, timedelta


class Person:
    def __init__(self, person_id, full_name, city, birth_date, position, experience):
        self.id = person_id
        self.full_name = full_name
        self.city = city
        self.birth_date = birth_date
        self.position = position
        self.experience = experience

    def update_profile(self, **changes):
        allowed = {"full_name", "city", "birth_date", "position", "experience"}
        for field, value in changes.items():
            if field not in allowed:
                raise ValueError("Неизвестное поле профиля: " + field)
            setattr(self, field, value)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "city": self.city,
            "birth_date": self.birth_date,
            "position": self.position,
            "experience": self.experience,
        }


class Operator(Person):
    def __init__(self, person_id, full_name, city, birth_date, position, experience):
        super().__init__(person_id, full_name, city, birth_date, position, experience)
        self.is_busy = False
        self.active_chat_id = None

    def to_dict(self):
        data = super().to_dict()
        data["is_busy"] = self.is_busy
        data["active_chat_id"] = self.active_chat_id
        return data


class User(Person):
    pass


class Message:
    def __init__(self, sender_type, sender_id, text, sent_at=None):
        self.sender_type = sender_type
        self.sender_id = sender_id
        self.text = text
        self.sent_at = sent_at or datetime.now().isoformat(timespec="seconds")

    def to_dict(self):
        return {
            "sender_type": self.sender_type,
            "sender_id": self.sender_id,
            "text": self.text,
            "sent_at": self.sent_at,
        }


class Chat:
    def __init__(self, chat_id, user_id, operator_id=None):
        self.id = chat_id
        self.user_id = user_id
        self.operator_id = operator_id
        self.status = "open" if operator_id is not None else "waiting"
        self.created_at = datetime.now().isoformat(timespec="seconds")
        self.closed_at = None
        self.messages = []
        self.csat = None

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "operator_id": self.operator_id,
            "status": self.status,
            "created_at": self.created_at,
            "closed_at": self.closed_at,
            "csat": self.csat,
            "messages": [message.to_dict() for message in self.messages],
        }


class SupportPlatform:
    def __init__(self):
        self.operators = {}
        self.users = {}
        self.chats = {}
        self.next_chat_id = 1

    def add_operator(self, operator):
        if operator.id in self.operators:
            raise ValueError("Оператор с таким ID уже существует")
        self.operators[operator.id] = operator

    def add_user(self, user):
        if user.id in self.users:
            raise ValueError("Пользователь с таким ID уже существует")
        self.users[user.id] = user

    def _free_operators(self):
        return [op for op in self.operators.values() if not op.is_busy]

    def _assign(self, chat):
        free = self._free_operators()
        if not free:
            return False
        operator = random.choice(free)
        operator.is_busy = True
        operator.active_chat_id = chat.id
        chat.operator_id = operator.id
        chat.status = "open"
        return True

    def create_chat(self, user_id, first_message):
        if user_id not in self.users:
            raise ValueError("Пользователь не найден")
        chat = Chat(self.next_chat_id, user_id)
        self.next_chat_id += 1
        chat.messages.append(Message("user", user_id, first_message))
        self.chats[chat.id] = chat
        self._assign(chat)
        return chat

    def send_user_message(self, chat_id, text):
        chat = self.chats[chat_id]
        if chat.status == "closed":
            raise ValueError("Нельзя писать в закрытый чат")
        chat.messages.append(Message("user", chat.user_id, text))

    def send_operator_message(self, chat_id, operator_id, text):
        chat = self.chats[chat_id]
        if chat.status != "open" or chat.operator_id != operator_id:
            raise ValueError("Чат не открыт или назначен другому оператору")
        chat.messages.append(Message("operator", operator_id, text))

    def close_chat(self, chat_id, operator_id):
        chat = self.chats[chat_id]
        if chat.status != "open" or chat.operator_id != operator_id:
            raise ValueError("Закрыть чат может только назначенный оператор")
        chat.status = "closed"
        chat.closed_at = datetime.now().isoformat(timespec="seconds")
        operator = self.operators[operator_id]
        operator.is_busy = False
        operator.active_chat_id = None
        # Освободившийся оператор принимает первое ожидающее обращение.
        for waiting_chat in self.chats.values():
            if waiting_chat.status == "waiting":
                self._assign(waiting_chat)
                break

    def rate_chat(self, chat_id, user_id, csat):
        chat = self.chats[chat_id]
        if chat.user_id != user_id:
            raise ValueError("Оценку может поставить только автор обращения")
        if chat.status != "closed":
            raise ValueError("Оценивать можно только закрытые чаты")
        if type(csat) is not int or not 1 <= csat <= 5:
            raise ValueError("CSAT должен быть целым числом от 1 до 5")
        if chat.csat is not None:
            raise ValueError("Оценка уже выставлена")
        chat.csat = csat

    @staticmethod
    def _save_json(data, filename):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print("Сохранено:", filename, "| Записей:", len(data))

    def export_all_chats(self, filename="all_chats.json"):
        self._save_json([chat.to_dict() for chat in self.chats.values()], filename)

    def export_operator_chats(self, operator_id, filename=None):
        if operator_id not in self.operators:
            raise ValueError("Оператор не найден")
        filename = filename or f"operator_{operator_id}_chats.json"
        data = [chat.to_dict() for chat in self.chats.values() if chat.operator_id == operator_id]
        self._save_json(data, filename)

    def export_user_chats(self, user_id, filename=None):
        if user_id not in self.users:
            raise ValueError("Пользователь не найден")
        filename = filename or f"user_{user_id}_chats.json"
        data = [chat.to_dict() for chat in self.chats.values() if chat.user_id == user_id]
        self._save_json(data, filename)

    def export_operators(self, filename="operators.json"):
        self._save_json([op.to_dict() for op in self.operators.values()], filename)

    def export_users(self, filename="users.json"):
        self._save_json([user.to_dict() for user in self.users.values()], filename)


FIRST_NAMES = ["Жанас", "Айдана", "Иван", "Мария", "Алихан", "Дана", "Руслан", "Анна"]
LAST_NAMES = ["Аменбеков", "Иванов", "Ким", "Серикова", "Петров", "Омаров", "Смирнова", "Ахметова"]
CITIES = ["Алматы", "Астана", "Шымкент", "Караганда", "Актобе", "Павлодар"]
QUESTIONS = ["Не могу войти в аккаунт", "Как изменить пароль?", "Не проходит оплата", "Где мой заказ?", "Как вернуть деньги?"]
ANSWERS = ["Проверяем ваш запрос", "Попробуйте повторить действие", "Проблема решена", "Передали информацию в систему"]


def random_person_data(role):
    name = random.choice(LAST_NAMES) + " " + random.choice(FIRST_NAMES)
    year = random.randint(1975, 2005)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    position = "Оператор поддержки" if role == "operator" else random.choice(["Студент", "Менеджер", "Инженер", "Продавец"])
    return name, random.choice(CITIES), f"{year}-{month:02d}-{day:02d}", position, random.randint(0, 15)


def generate_demo_platform(operator_count=12, user_count=60, chat_count=120):
    """Генерирует обращения, часть оставляет открытыми/в очереди/без оценки."""
    platform = SupportPlatform()
    for i in range(1, operator_count + 1):
        platform.add_operator(Operator(i, *random_person_data("operator")))
    for i in range(1, user_count + 1):
        platform.add_user(User(i, *random_person_data("user")))

    for _ in range(chat_count):
        user_id = random.choice(list(platform.users))
        chat = platform.create_chat(user_id, random.choice(QUESTIONS))
        if chat.status == "open":
            if random.random() < 0.85:
                platform.send_operator_message(chat.id, chat.operator_id, random.choice(ANSWERS))
            if random.random() < 0.75:
                operator_id = chat.operator_id
                platform.close_chat(chat.id, operator_id)
                if random.random() < 0.80:
                    platform.rate_chat(chat.id, user_id, random.randint(1, 5))
        elif random.random() < 0.30:
            platform.send_user_message(chat.id, "Ожидаю ответа")
    return platform
