# players = {id: "color", ...}

async def pan(province, players):
    pan_data = []
    for data in province["province"]:
        players_emoji_list = [players[str(user)]["color"] for user in data['users']]
        if len(players_emoji_list) == 0:
            players_emoji_list.append("⬜️")
        if data["name"] == "시작":
            pan_data.append(
                f"[{', '.join(players_emoji_list)}] {data['name']}"
            )
        elif data["name"] == "이벤트 카드":
            pan_data.append(f"[{', '.join(players_emoji_list)}] 💳 {data['name']}")
        elif data["name"] == "여행":
            pan_data.append(f"[{', '.join(players_emoji_list)}] 🧳 {data['name']}")
        elif data["name"] == "감옥":
            pan_data.append(f"[{', '.join(players_emoji_list)}] 🔒 {data['name']}")
        else:
            pan_data.append(f"[{', '.join(players_emoji_list)}] 🏙️ {data['name']} ({f'''<@{data['owner']}>''' if data['owner'] != 0 else '소유주 없음'}, {data['money']})")

    return pan_data