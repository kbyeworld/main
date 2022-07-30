import asyncio
import datetime

import discord
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands, pages

import config
from utils.database import UserDatabase
from utils.embed import Embed

class Mail_Form(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            discord.ui.InputText(
                label="제목",
                placeholder="메일 제목을 입력해주세요. (최대 50자까지 가능)",
                custom_id="title",
                max_length=50,
                required=True,
            ),
            discord.ui.InputText(
                label="내용",
                placeholder="보낼 메일의 내용을 입력해주세요. (최대 500자까지 가능)",
                style=discord.InputTextStyle.long,
                max_length=1000,
                custom_id="description",
                required=True,
            ),
            discord.ui.InputText(
                label="사진",
                placeholder="메일에 첨부될 사진의 URL을 입력해주세요.",
                style=discord.InputTextStyle.short,
                custom_id="image",
                required=False,
            ),
            title="메일 전송하기",
            *args,
            **kwargs,
        )

    async def callback(self, interaction: discord.Interaction):
        title, description, image = (
            self.children[0].value,
            self.children[1].value,
            self.children[2].value,
        )
        embed = Embed.default(title=title, description=description)
        if str(image) != "":
            embed.set_image(url=image)
        embed.set_footer(text="프리뷰입니다.")

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="네", emoji="✅", style=discord.ButtonStyle.green, custom_id=f"yes"
            )
        )
        view.add_item(
            discord.ui.Button(
                label="아니오", emoji="❎", style=discord.ButtonStyle.red, custom_id=f"no"
            )
        )
        msg = await interaction.response.send_message(content="이와 같이 전송하시겠습니까?", embed=embed, view=view, ephemeral=True)

        def check(inter):
            return inter.user.id == interaction.user.id

        try:
            interaction_check = await interaction.client.wait_for(
                "interaction", check=check, timeout=60.0
            )
        except asyncio.TimeoutError:
            embed = Embed.cancel(
                timestamp=datetime.datetime.now(),
                description="제한시간이 초과되어 취소되었어요.",
            )
            Embed.user_footer(embed, interaction.user)
            try:
                return await msg.edit_original_message(
                    content=None,
                    embed=embed,
                    view=None,
                )
            except:
                return

        if interaction_check.data["custom_id"] == "no":
            embed = Embed.cancel(
                timestamp=datetime.datetime.now(),
                description="사용자님의 요청으로 취소되었어요.",
            )
            Embed.user_footer(embed, interaction.user)
            return await msg.edit_original_message(content=None, embed=embed, view=None)

        allu = await UserDatabase.list({'deleted': False})
        json = {
            "title": title,
            "description": description,
            "image": image,
            "date": datetime.datetime.now(),
            "sender": interaction.user.id,
            "read": False,
        }

        success = 0
        for i in allu:
            result = await UserDatabase.mail.add(i["_id"], json)
            if result["error"] == False:
                success += 1

        embed = Embed.default(
            timestamp=datetime.datetime.now(),
            title="✅ 메일이 전송되었습니다.",
            description=f"``{len(allu)}``명의 유저 중 ``{success}``명의 유저에게 발송을 완료했어요.",
        )
        Embed.user_footer(embed, interaction.user)
        await msg.edit_original_message(content=None, embed=embed, view=None)

class mail(commands.Cog, name="메일"):
    def __init__(self, bot):
        self.bot = bot

    async def account_check(self):
        result = await UserDatabase.find(self.author.id)
        if result == None:
            embed = Embed.perm_warn(
                timestamp=datetime.datetime.now(),
                description=f"{self.author.mention}님은 ``{self.bot.user.name} 서비스``에 가입하지 않으셨어요.\n``/가입`` 명령어로 서비스에 가입하실 수 있어요.",
            )
            Embed.user_footer(embed, self.author)
            await self.respond(embed=embed, ephemeral=True)
            return False
        return True

    mail = SlashCommandGroup("메일", "시스템 메일 관련 명령어에요.")

    @mail.command(
        name="전송",
        description="[🔒 개발자 전용] 시스템 메일을 전송합니다.",
        default_permission=False,
    )
    @commands.is_owner()
    async def alert_send(self, ctx):
        await ctx.send_modal(modal=Mail_Form())

    @mail.command(
        name="확인",
        description="시스템 메일을 확인합니다.",
        checks=[account_check],
    )
    async def alert_check(
        self,
        ctx,
        filiter: Option(
            str,
            "읽을 메일을 분류해서 보여드려요.",
            choices=["전체", "읽지 않은 메일", "읽은 메일"],
            name="필터",
            required=False,
        ) = "전체",
    ):
        await ctx.defer(ephemeral=True)
        read = None
        if filiter == "전체":
            read = None
        elif filiter == "읽지 않은 메일":
            read = False
        elif filiter == "읽은 메일":
            read = True

        user = await UserDatabase.mail.list(ctx.author.id, read=read)

        if len(user["mail_list"]) == 0:
            embed = Embed.default(
                timestamp=datetime.datetime.now(), title="받은 메일이 없어요 :("
            )
            Embed.user_footer(embed, ctx.author)
            return await ctx.respond(
                embed=embed,
            )

        mail_embed = []
        mail_data = []
        if filiter == "전체":
            for i in user["mail_list"]:
                if i["read"] is False:
                    json = {
                        "title": i["title"],
                        "description": i["description"],
                        "image": i["image"],
                        "date": i["date"],
                        "sender": i["sender"],
                        "read": True,
                    }
                    mail_data.append(json)
                else:
                    json = i
                    mail_data.append(json)
                t = str(i["date"])
                send_date = datetime.datetime(
                    int(t.split("-")[0]),
                    int(t.split("-")[1]),
                    int((t.split("-")[2]).split(" ")[0]),
                    int((t.split(" ")[1]).split(":")[0]),
                    int(t.split(":")[1]),
                    int((t.split(":")[2]).split(".")[0]),
                    int(t.split(".")[1]),
                )
                embed = Embed.default(
                    timestamp=send_date,
                    title=i["title"],
                    description=i["description"],
                )
                if i["image"]:
                    embed.set_image(url=i["image"])
                try:
                    embed.set_footer(
                        text=f"보낸 사람 : {self.bot.get_user(int(i['sender']))}",
                        icon_url=self.bot.get_user(int(i["sender"])).display_avatar,
                    )
                except:
                    embed.set_footer(
                        text=f"보낸 사람 : 정보를 찾을 수 없음",
                        icon_url="https://cdn.discordapp.com/embed/avatars/0.png",
                    )
                mail_embed.append(embed)
            await UserDatabase.mail.set(ctx.author.id, mail_data)

        if filiter == "읽지 않은 메일":
            for i in user["mail_list"]:
                if i["read"] is False:
                    json = {
                        "title": i["title"],
                        "description": i["description"],
                        "image": i["image"],
                        "date": i["date"],
                        "sender": i["sender"],
                        "read": True,
                    }
                    mail_data.append(json)
                    t = str(i["date"])
                    send_date = datetime.datetime(
                        int(t.split("-")[0]),
                        int(t.split("-")[1]),
                        int((t.split("-")[2]).split(" ")[0]),
                        int((t.split(" ")[1]).split(":")[0]),
                        int(t.split(":")[1]),
                        int((t.split(":")[2]).split(".")[0]),
                        int(t.split(".")[1]),
                    )
                    embed = Embed.default(
                        timestamp=send_date,
                        title=i["title"],
                        description=i["description"],
                    )
                    if i["image"]:
                        embed.set_image(url=i["image"])
                    try:
                        embed.set_footer(
                            text=f"보낸 사람 : {self.bot.get_user(int(i['sender']))}",
                            icon_url=self.bot.get_user(int(i["sender"])).display_avatar,
                        )
                    except:
                        embed.set_footer(
                            text=f"보낸 사람 : 정보를 찾을 수 없음",
                            icon_url="https://cdn.discordapp.com/embed/avatars/0.png",
                        )
                    mail_embed.append(embed)
                else:
                    json = i
                    mail_data.append(json)
            await UserDatabase.mail.set(ctx.author.id, mail_data)

        if filiter == "읽은 메일":
            for i in user["mail_list"]:
                if i["read"]:
                    json = {
                        "title": i["title"],
                        "description": i["description"],
                        "image": i["image"],
                        "date": i["date"],
                        "sender": i["sender"],
                        "read": True,
                    }
                    mail_data.append(json)
                    t = str(i["date"])
                    send_date = datetime.datetime(
                        int(t.split("-")[0]),
                        int(t.split("-")[1]),
                        int((t.split("-")[2]).split(" ")[0]),
                        int((t.split(" ")[1]).split(":")[0]),
                        int(t.split(":")[1]),
                        int((t.split(":")[2]).split(".")[0]),
                        int(t.split(".")[1]),
                    )
                    embed = Embed.default(
                        timestamp=send_date,
                        title=i["title"],
                        description=i["description"],
                    )
                    if i["image"]:
                        embed.set_image(url=i["image"])
                    try:
                        embed.set_footer(
                            text=f"보낸 사람 : {self.bot.get_user(int(i['sender']))}",
                            icon_url=self.bot.get_user(int(i["sender"])).display_avatar,
                        )
                    except:
                        embed.set_footer(
                            text=f"보낸 사람 : 정보를 찾을 수 없음",
                            icon_url="https://cdn.discordapp.com/embed/avatars/0.png",
                        )
                    mail_embed.append(embed)

        if len(mail_embed) == 0:
            embed = Embed.default(
                timestamp=datetime.datetime.now(), title="받은 메일이 없어요 :("
            )
            Embed.user_footer(embed, ctx.author)
            return await ctx.respond(
                embed=embed,
                ephemeral=True,
            )

        else:
            paginator = pages.Paginator(pages=mail_embed, use_default_buttons=False)
            paginator.add_button(
                pages.PaginatorButton(
                    "first", emoji="⏪", style=discord.ButtonStyle.blurple
                )
            )
            paginator.add_button(
                pages.PaginatorButton(
                    "prev", emoji="◀️", style=discord.ButtonStyle.green
                )
            )
            paginator.add_button(
                pages.PaginatorButton(
                    "page_indicator", style=discord.ButtonStyle.gray, disabled=True
                )
            )
            paginator.add_button(
                pages.PaginatorButton(
                    "next", emoji="▶️", style=discord.ButtonStyle.green
                )
            )
            paginator.add_button(
                pages.PaginatorButton(
                    "last", emoji="⏩", style=discord.ButtonStyle.blurple
                )
            )
            await paginator.respond(ctx.interaction, ephemeral=True)


def setup(bot):
    bot.add_cog(mail(bot))
