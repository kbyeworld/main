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

    async def list(filiter: dict = {}):
        """
        filiter (dict) - 선택, 리스트 조회 필터를 입력합니다.
        """
        return [data async for data in client.users.find(filiter)]

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
                        "description": f"기본 지원금으로 5천만원이 추가되었습니다!\n\n:question: __더 궁금하신 사항이 있으신가요?__\n[깃허브에서 이슈로 남겨주세요!](https://github.com/kbyeworld/main)",
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
        return {'success': True, 'result': '가입을 완료했습니다! ``/메일 확인 필터:읽지 않음``으로 메일을 확인해보세요!'}

    async def delete(user_id: int):
        """
        user_id (int) - 필수, 디스코드 유저 ID 입력
        """
        if (await UserDatabase.find(user_id=user_id) is None):
            return {'success': False, 'result': '존재하지 않는 사용자입니다.'}
        await client.users.update_one({"user_id": user_id, "deleted": False}, {'$set': {"deleted": True, "deleted_at": datetime.datetime.now()}})
        return {'success': True, 'result': '탈퇴를 완료했습니다. 30일 후 재가입이 가능합니다.'}
