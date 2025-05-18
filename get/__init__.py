from redbot.core.bot import Red

from .get import GetCog


async def setup(bot: Red):
    await bot.add_cog(GetCog())
