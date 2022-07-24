class bot:
    token = "" # 봇 토큰을 입력합니다.
    prefix = [] # 일부 명령어 사용을 위한 접두사를 입력합니다.

class setting:
    owner_ids = [] # 봇 관리자의 아이디를 입력합니다.
    intents = ["members"] # presences (PRESENCE INTENT), members (SERVER MEMBERS INTENT), message_content (MESSAGE CONTENT INTENT)를 입력할 수 있습니다.