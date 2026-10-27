from support_platform import generate_demo_platform

platform = generate_demo_platform(chat_count=120)
print("Всего чатов:", len(platform.chats))
for status in ("open", "waiting", "closed"):
    print(status + ":", sum(chat.status == status for chat in platform.chats.values()))
print("Чатов с CSAT:", sum(chat.csat is not None for chat in platform.chats.values()))
platform.export_all_chats()
