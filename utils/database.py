import motor.motor_asyncio
import asyncio
import datetime
import config

client = motor.motor_asyncio.AsyncIOMotorClient(config.Setting.database.uri)[
    config.Setting.database.name
]
client.get_io_loop = asyncio.get_running_loop

class UserDatabase:
    async def find(user_id: int, deleted: bool = False, **kwargs):
        """
        user_id (int) - 필수, 디스코드 유저 ID 입력
        """
        return await client.users.find_one({"user_id": user_id, 'deleted': deleted})

    async def list(filter: dict = {}):
        """
        filter (dict) - 선택, 리스트 조회 필터를 입력합니다.
        """
        return [data async for data in client.users.find(filter)]

    async def add(user_id: int):
        """
        user_id (int) - 필수, 디스코드 유저 ID 입력
        """
        if (await UserDatabase.find(user_id=user_id)):
            return {'success': False, 'result': '이미 존재하는 사용자입니다.'}
        if (await UserDatabase.list({'user_id':user_id, 'deleted':True})):
            for info in (await UserDatabase.list({'user_id':user_id, 'deleted':True})):
                time = (info['deleted_at'] + datetime.timedelta(days=30)) - datetime.datetime.now()
                if time.total_seconds() >= 0:
                    timestr = []
                    return {'success': False, 'result': f'재가입 기간을 지나지 않았습니다. {str(time)}'}
        await client.users.insert_one(
            {
                "user_id": user_id,
                "money": "50000000",
                "mail": [
                    {
                        "title": f"K-BYEWORLD 서비스 가입을 축하드립니다! :tada:",
                        "description": f"기본 지원금으로 5천만원이 추가되었습니다!\n\n:question: __더 궁금하신 사항이 있으신가요?__\n> [깃허브에서 이슈로 남겨주세요!](https://github.com/kbyeworld/main)",
                        "image": None,
                        "date": datetime.datetime.now(),
                        "sender": 1000553177051037697,
                        "read": False,
                    },
                ],
                "mail_last_notify": None,
                "deleted": False,
            },
        )
        return {'success': True, 'result': '가입을 완료했습니다! ``/메일 확인 필터:읽지 않은 메일``으로 메일을 확인해보세요!'}

    async def delete(user_id: int):
        """
        user_id (int) - 필수, 디스코드 유저 ID 입력
        """
        if (await UserDatabase.find(user_id=user_id) is None):
            return {'success': False, 'result': '존재하지 않는 사용자입니다.'}
        await client.users.update_one({"user_id": user_id, "deleted": False}, {'$set': {"deleted": True, "deleted_at": datetime.datetime.now()}})
        return {'success': True, 'result': '탈퇴를 완료했습니다. 30일 후 재가입이 가능합니다.'}

    class mail:
        async def add(user_id: int, mail: dict):
            """
            user_id (int) - 필수, 디스코드 유저 ID 입력
            mail (dict) - 필수, DICT 형식으로 입력
            """
            user = await UserDatabase.find(user_id)
            if user != None:
                user["mail"].insert(0, mail)
                await client.users.update_one(
                    {"user_id": user_id, "deleted": False}, {"$set": {"mail": user["mail"]}}
                )
                return {"error": False}
            return {"error": True}

        async def last_notify(user_id: int, time: datetime.datetime):
            """
            user_id (int) - 필수, 디스코드 유저 ID 입력
            time (datetime.datetime) - 필수, datetime.datetime 형식으로 입력
            """
            if (await UserDatabase.find(user_id)) != None:
                await client.users.update_one(
                    {"user_id": user_id, "deleted": False}, {"$set": {"mail_last_notify": time}}
                )
                return {"error": False}
            return {"error": True}

        async def list(user_id: int, read: bool = None):
            """
            user_id (int) - 필수, 조회할 유저 id 입력
            read (bool) - 선택, 읽은 이메일 (True) / 안 읽은 이메일 (False) / 모두 (None)
            """
            if (await UserDatabase.find(user_id)) != None:
                mail_list = []
                if read == None:
                    for i in (await UserDatabase.find(user_id))["mail"]:
                        mail_list.append(i)
                    return {"error": False, "mail_list": mail_list}
                for i in (await UserDatabase.find(user_id))["mail"]:
                    if read == i["read"]:
                        mail_list.append(i)
                return {"error": False, "mail_list": mail_list}
            else:
                return {"error": True}

        async def set(user_id: int, data: dict):
            """
            user_id (int) - 필수, 조회할 유저 id 입력
            data (dict) - 필수, 설정할 데이터 입력
            """
            if (await UserDatabase.find(user_id)) != None:
                await client.users.update_one({"user_id": user_id, "deleted": False}, {"$set": {"mail": data}})
                return {"error": False}
            else:
                return {"error": True}
