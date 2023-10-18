import asyncio
from aiogram import Bot, Dispatcher
from functional import funcPlayer, funcSeller, funcTechnic, funcRegistration, funcAdmin
from database.db import Database

db = Database()
async def main() -> None:

    bot = Bot("6334146587:AAGcnymR4XTLizknwhCm3Z4_xbc3UtNcfKQ", parse_mode="HTML")
    dp = Dispatcher()

    dp.include_router(funcRegistration.routerRegistartion)
    dp.include_router(funcPlayer.routerPlayer)
    dp.include_router(funcSeller.routerSeller)
    dp.include_router(funcTechnic.routerTechnic)
    dp.include_router(funcAdmin.adminRouter)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
