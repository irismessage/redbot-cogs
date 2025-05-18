from discord import Message
from redbot.core import commands


class GetCog(commands.Cog):
    gif_url = "https://giphy.com/gifs/2lQCCSp19EDAy5d7c7"
    qualifiers = {
        5: "QUINTS",
        6: "SEX",
        7: "SEPTS",
    }
    content_truncate = 5

    @staticmethod
    def consecutive_digits(number: int) -> int:
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

    async def quints(self, message: Message, message_id: int):
        consecutive = self.consecutive_digits(message_id)

        qual = self.qualifiers.get(consecutive)
        if qual is None:
            return

        content = message.content[: self.content_truncate]

        await message.channel.send(
            f'{message.author.name} sent "{content}..." with Message ID: {message_id} (***{qual}***)'
        )

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        await self.quints(message, message.id)

    @commands.is_owner()
    @commands.command(hidden=True)
    async def test_quints(self, ctx: commands.Context, message_id: int):
        await self.quints(ctx.message, message_id)
