import discord


class Embed(discord.Embed):
    def default(title: str = None, description: str = None, **kwargs):
        embed = discord.Embed(**kwargs, colour=discord.Colour.blurple())
        if not title is None:
            embed.title = title
        if not description is None:
            embed.description = description
        return embed

    def warn(description: str, **kwargs):
        embed = discord.Embed(
            **kwargs,
            colour=discord.Colour.gold(),
            title="⚠ 경고",
            description=description,
        )
        return embed

    def perm_warn(description: str, **kwargs):
        embed = discord.Embed(
            **kwargs,
            colour=discord.Colour.gold(),
            title="⚠ 권한 부족",
            description=description,
        )
        return embed

    def cancel(description: str, **kwargs):
        embed = discord.Embed(
            **kwargs, color=0x5865F2, title="❌ 취소됨", description=description
        )
        return embed

    def error(description: str, **kwargs):
        embed = discord.Embed(
            **kwargs, color=0xFF0000, title="⚠ 오류 발생", description=description
        )
        return embed

    def user_footer(embed, user):
        return embed.set_footer(
            text=str(user.global_name),
            icon_url=user.display_avatar,
        )

    def blacklist_embed(result: dict):
        embed = Embed.perm_warn(
            description=f"<@{result['user_id']}>님은 시스템에서 차단조치되었어요.\n사유가 올바르지 않거나, 이의를 제기하고 싶으시다면 [삼해트의 공방](https://discord.gg/TD9BvMxhP6)의 문의 채널에서 문의 부탁드립니다!",
        )
        embed.add_field(name="차단 사유", value=f"```{result['reason']}```", inline=False)
        if result["ended_at"]:
            embed.add_field(
                name="차단 해제 시각",
                value=f"<t:{str((result['ended_at']).timestamp()).split('.')[0]}> (<t:{str((result['ended_at']).timestamp()).split('.')[0]}:R>)",
                inline=False,
            )
        return embed
