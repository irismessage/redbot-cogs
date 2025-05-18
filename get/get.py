from typing import Optional

from discord import (
    Member,
    Message,
    StageChannel,
    TextChannel,
    Thread,
    User,
    VoiceChannel,
)
from discord.abc import Messageable
from redbot.core import bank, commands


class GetCog(commands.Cog):
    gif_url = "https://giphy.com/gifs/2lQCCSp19EDAy5d7c7"
    qualifiers = {
        # 2: "DUBS",
        # 3: "TRIS",
        # 4: "QUADS",
        5: "QUINTS",
        6: "SEX",
        7: "SEPTS",
        8: "OCTS",
    }
    over = "WHAT THE FUCK?"
    content_truncate = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.max_qualifier = max(self.qualifiers.keys())

    @staticmethod
    def count_consecutive_digits(number: int) -> int:
        """
        >>> GetCog.consecutive_digits(55555)
        5
        >>> GetCog.consecutive_digits(155555)
        5
        >>> GetCog.consecutive_digits(1)
        1
        """
        digit = number % 10
        consecutive = 1
        while number > 9:
            number //= 10
            if number % 10 != digit:
                break
            consecutive += 1

        return consecutive

    def get_qualifier(self, consecutive_digits: int) -> Optional[str]:
        if consecutive_digits > self.max_qualifier:
            return self.over
        else:
            return self.qualifiers.get(consecutive_digits)

    @staticmethod
    async def bank_reward(member: User | Member, consecutive_digits: int):
        if not isinstance(member, Member):
            return

        reward_value = 10**consecutive_digits
        balance = await bank.get_balance(member)
        new_balance = balance + reward_value
        try:
            await bank.set_balance(member, new_balance)
        except bank.errors.BalanceTooHigh:
            pass

    async def quints(
        self,
        message: Message,
        message_id: Optional[int] = None,
        destination: Optional[Messageable] = None,
    ):
        if message_id is None:
            message_id = message.id
        if destination is None:
            destination = message.channel

        consecutive_digits = self.count_consecutive_digits(message_id)

        qual = self.get_qualifier(consecutive_digits)
        if qual is None:
            return

        await self.bank_reward(message.author, consecutive_digits)

        # note: newlines included
        content = message.content[: self.content_truncate]
        await destination.send(
            f'{message.author.name} sent "{content}..." with Message ID: {message_id} (***{qual}***)'
        )

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        await self.quints(message)

    @commands.is_owner()
    @commands.command(hidden=True)
    async def test_quints(self, ctx: commands.Context, message_id: int):
        await self.quints(ctx.message, message_id)

    @commands.is_owner()
    @commands.command(hidden=True)
    async def backfill_quints(self, ctx: commands.Context):
        guild = ctx.guild
        if guild is None:
            await ctx.send("not in a guild")
            return

        await ctx.send("Loading all history")
        channels = [*guild.channels, *guild.threads]

        for c in channels:
            if not isinstance(c, (TextChannel, VoiceChannel, StageChannel, Thread)):
                # no history
                await ctx.send(f"Ignoring {c.mention}")
                continue

            status_message = await ctx.send(f"Loading history in {c.mention}")
            count = 0

            async def update_status():
                await status_message.edit(content=f"Read {count} in {c.mention}")

            async for message in c.history(limit=None):
                await self.quints(message, message.id, ctx.channel)

                count += 1
                if count % 1000 == 0:
                    await update_status()

            await update_status()
            await ctx.send(f"Loaded history in {c.mention}")

        await ctx.send("Loaded all history")
