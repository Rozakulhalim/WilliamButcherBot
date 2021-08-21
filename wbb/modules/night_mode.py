# Copyright (C) 2020-2021 by DevsExpo@Github, < https://github.com/DevsExpo >.
#
# This file is part of < https://github.com/DevsExpo/FridayUserBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/DevsExpo/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram import filters

from wbb import app
from wbb.core.decorators.errors import capture_err
from wbb.core.decorators.permissions import adminsOnly
from wbb.utils.dbfunctions import is_night_chat_in_db, get_all_night_chats, rm_night_chat, add_night_chat
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
import requests
import json

__MODULE__ = "Night Mode"
__HELP__ = """ Here For Help Night Mode
/nightmode on|enable|yes To Enable Night Mode
/nightmode off|disable|no To Disable Night Mode"""

@app.on_message(
    filters.command("on_grp") & ~filters.edited & ~filters.private
)    
async def scgrp(client, message):
    pablo = await edit_or_reply(message, "`Memproses...`")
    lol = await is_night_chat_in_db(message.chat.id)
    if lol:
        await pablo.edit("Obrolan Ini Telah Mengaktifkan Mode Malam.")
        return
    await add_night_chat(message.chat.id)
    await pablo.edit(f"**Ditambahkan Obrolan {message.chat.title} dengan Id {message.chat.id} ke Database. Grup ini akan ditutup pada jam 22PM(WIB) dan akan dibuka pukul 6AM(WIB)**")


@app.on_message(
    filters.command("on_grp") & ~filters.edited & ~filters.private
)    
async def scgrp(client, message):
    pablo = await edit_or_reply(message, "`Searching For Anime.....`")
    lol = await is_night_chat_in_db(message.chat.id)
    if not lol:
        await pablo.edit("Obrolan Ini Belum Mengaktifkan Mode Malam.")
        return
    await rm_night_chat(message.chat.id)
    await pablo.edit(f"**Menghapus obrolan {message.chat.title} dengan Id {message.chat.id} dari Database. Grup ini tidak akan ditutup pada 22PM(WIB) dan akan dibuka pada 6AM(WIB)**")


async def job_close():
    lol = await get_all_night_chats()
    if len(lol) == 0:
        return
    for warner in lol:
        try:
            await app.send_message(
              int(warner.get("chat_id")), "**🌃 Mode Malam Aktif**\n\n`Sekarang jam 22:00, Grup ditutup dan akan dibuka esok hari secara otomatis. Selamat beristirahat semuanya!!` \n**Powered By Pyrogram**"
            )
            await app.set_chat_permissions(
                        warner.get("chat_id"),
                        ChatPermissions(
                            can_send_messages=False,
                            can_invite_users=True,
                         )
            )
            async for member in app.iter_chat_members(warner.get("chat_id")):
             if member.user.is_deleted:
                try:
                    await app.kick_chat_member(warner.get("chat_id"), member.user.id)
                except:
                    pass
        except Exception as e:
            logging.info(str(e))
            ido = warner.get("chat_id")
            try:
                await app.send_message(Config.LOG_GRP, f"[NIGHT MODE]\n\nFailed To Close The Group {ido}.\nError : {e}")
            except:
                pass


scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")
scheduler.add_job(job_close, trigger="cron", hour=22, minute=0)
scheduler.start()

async def job_open():
    req = requests.get('http://fadhil-s.herokuapp.com/api/random_quotes.php?apikey=dwh20ud9u0q2ijsd092099139jp')
    json = req.json()
    quote = json["data"]["quotes"]
    author = json["data"]["by"]
    lol = await get_all_night_chats()
    if len(lol) == 0:
        return
    for warner in lol:
        try:
            await app.send_message(
              int(warner.get("chat_id")), "`Sekarang sudah jam 6 pagi. Selamat pagi, grup kini telah dibuka semoga hari-harimu menyenangkan.`\n\n**Quotes Today:**\n"+quote+"\n~ "+author+"\n**Powered By Pyrogram**"
            )
            await app.set_chat_permissions(
                        warner.get("chat_id"),
                        ChatPermissions(
                            can_send_messages=True,
                            can_send_media_messages=True,
                            can_send_stickers=False,
                            can_send_animations=True,
                            can_invite_users=True,
                            can_add_web_page_previews=True,
                            can_use_inline_bots=True
                         )
            )
            
        except Exception as e:
            logging.info(str(e))
            ido = warner.get("chat_id")
            try:
                await app.send_message(Config.LOG_GRP, f"[NIGHT MODE]\n\nFailed To Open The Group {ido}.\nError : {e}")
            except:
                pass
            

scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")
scheduler.add_job(job_open, trigger="cron", hour=6, minute=0)
scheduler.start()
