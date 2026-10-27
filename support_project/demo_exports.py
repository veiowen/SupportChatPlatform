from support_platform import generate_demo_platform

platform = generate_demo_platform(chat_count=120)
platform.export_all_chats()
platform.export_operator_chats(operator_id=1)
platform.export_user_chats(user_id=1)
platform.export_operators()
platform.export_users()
