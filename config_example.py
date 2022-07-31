class Bot:
    token = ""  # 봇 토큰을 입력합니다.
    prefix = []  # 일부 명령어 사용을 위한 접두사를 입력합니다.


class Setting:
    owner_ids = []  # 봇 관리자의 아이디를 입력합니다.
    intents = ["members"]
    # presences (PRESENCE INTENT), members (SERVER MEMBERS INTENT)
    # message_content (MESSAGE CONTENT INTENT)를 입력할 수 있습니다.

    KxD_API_Key = ""
    # KxD 해커톤에서 제공한 API 키를 입력합니다.
    # 위 필드는 해커톤이 종료된 이후, 삭제될 예정입니다.

    class database:
        uri = "mongodb://localhost:27017"  # MongoDB 데이터베이스에 접속할 수 있는 URI를 입력합니다.
        name = "kbyeworld"  # MongoDB 데이터베이스 이름을 입력합니다.
