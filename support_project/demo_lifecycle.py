from support_platform import SupportPlatform, Operator, User

platform = SupportPlatform()
platform.add_operator(Operator(1, "Аменбеков Жанас", "Алматы", "1990-01-01", "Оператор поддержки", 3))
platform.add_user(User(1, "Иванов Иван", "Астана", "2000-05-15", "Менеджер", 1))

chat = platform.create_chat(1, "Не могу войти в аккаунт")
print("Новый чат:", chat.id, chat.status, "оператор:", chat.operator_id)
platform.send_operator_message(chat.id, chat.operator_id, "Попробуйте восстановить пароль")
platform.close_chat(chat.id, chat.operator_id)
platform.rate_chat(chat.id, 1, 5)
platform.users[1].update_profile(city="Алматы", experience=2)
print("Чат закрыт, CSAT:", chat.csat)
print("Обновлённый город пользователя:", platform.users[1].city)
platform.export_all_chats("lifecycle_chat.json")
