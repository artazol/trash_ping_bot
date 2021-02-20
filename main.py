#!venv/bin/python
# -*- coding: utf-8 -*-

import logging
import config
import localization
import db
from html import escape
from aiogram import Bot, Dispatcher, executor, types, exceptions

bot = Bot(config.TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

groups = db.load_db()


# Utils
async def create_db_entry(chat_id):
    if await is_private(chat_id):
        if str(chat_id) not in groups:
            groups[chat_id] = {'lang': 'ru'}
            db.save_db(groups)
    else:
        if str(chat_id) not in groups:
            groups[chat_id] = {
                'groups': {
                    'all': {
                        'users': [],
                        'admin_only': False,
                        'invisible_tag': False,
                        'enable_whitelist': False,
                        'whitelist': []
                    }
                },
                'lang': 'ru',
                'create_admin': False,
                'blacklist': []
            }
            db.save_db(groups)


async def is_private(chat_id):
    user = await bot.get_chat(chat_id)
    if user.type == 'private':
        return True
    else:
        return False


async def is_admin(chat_id, user_id):
    member = await bot.get_chat_member(chat_id, user_id)
    return member.is_chat_admin()


async def is_whitelisted(chat_id, dest, user_id):
    if await is_admin(chat_id, user_id):
        return True

    if groups[chat_id]['groups'][dest]['enable_whitelist']:
        if str(user_id) in groups[chat_id]['groups'][dest]['whitelist']:
            return True
        else:
            return False
    else:
        return True


async def is_blacklisted(chat_id, user_id):
    if await is_admin(chat_id, user_id):
        return True

    if str(user_id) in groups[chat_id]['blacklist']:
        return False
    else:
        return True


async def is_locked(chat_id, user_id):
    if await is_admin(chat_id, user_id):
        return False

    if groups[chat_id]['create_admin']:
        return True
    else:
        return False


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await create_db_entry(message.chat.id)
    await bot.send_message(message.chat.id, localization.get_string('welcome', groups[str(message.chat.id)]['lang']),
                           parse_mode='HTML')


async def settings_compose(message, dest):
    chat_id = str(message.chat.id)
    lng = groups[chat_id]['lang']

    buttons = types.InlineKeyboardMarkup(row_width=1)
    if groups[chat_id]['groups'][dest]['invisible_tag']:
        status1 = localization.get_string('enabled', lng)
    else:
        status1 = localization.get_string('disabled', lng)

    if groups[chat_id]['groups'][dest]['admin_only']:
        status2 = localization.get_string('enabled', lng)
    else:
        status2 = localization.get_string('disabled', lng)

    if groups[chat_id]['groups'][dest]['enable_whitelist']:
        status3 = localization.get_string('enabled', lng)
    else:
        status3 = localization.get_string('disabled', lng)

    btn1_text = localization.get_string('inv_tag', lng).format(status=status1)
    btn2_text = localization.get_string('admin_only', lng).format(status=status2)
    btn3_text = localization.get_string('enable_whitelist', lng).format(status=status3)

    btn1 = types.InlineKeyboardButton(btn1_text, callback_data='inv_tag' + dest)
    btn2 = types.InlineKeyboardButton(btn2_text, callback_data='admin_only' + dest)
    btn3 = types.InlineKeyboardButton(btn3_text, callback_data='ew' + dest)

    buttons.add(btn1, btn2, btn3)
    buttons.add(types.InlineKeyboardButton(localization.get_string('cancel', lng), callback_data='cancel'))

    return buttons


async def message_compose(message, group):
    chat_id = str(message.chat.id)
    await create_db_entry(chat_id)
    lng = groups[chat_id]['lang']

    tagger = await bot.get_chat(message.from_user.id)
    name = escape(tagger.first_name)
    if tagger.last_name:
        name += ' ' + escape(tagger.last_name)

    text = localization.get_string('tag', lng).format(name=name)

    if len(groups[chat_id]['groups'][group]['users']) > 0:
        if groups[chat_id]['groups'][group]['invisible_tag']:
            for i in groups[chat_id]['groups'][group]['users']:
                text += '<a href="tg://user?id=' + str(i) + '"> 󠁿󠁿</a>'

        else:
            text += '\n'
            for i, user_id in enumerate(groups[chat_id]['groups'][group]['users']):
                user = await bot.get_chat(user_id)
                if user.username:
                    text += '@' + user.username
                else:
                    text += '<a href="tg://user?id=' + user_id + '">' + escape(user.first_name) + '</a>'

                if i != len(groups[chat_id]['groups'][group]['users']) - 1:
                    text += ', '
    else:
        text = localization.get_string('empty', lng).format(name=name)

    return text


@dp.message_handler(commands="tag")
async def tag(message: types.Message):
    chat_id = str(message.chat.id)
    await create_db_entry(chat_id)
    lng = groups[chat_id]['lang']

    if await is_private(chat_id):
        await bot.send_message(chat_id,
                               localization.get_string('private_chat', lng),
                               parse_mode='HTML')
        return

    command = message.text.split()
    if len(command) <= 1:
        dest = 'all'
    else:
        dest = command[1]

    if not await is_whitelisted(chat_id, dest, message.from_user.id) or \
            not await is_blacklisted(chat_id, message.from_user.id):
        await bot.send_message(chat_id, localization.get_string('whitelist', lng), parse_mode='HTML')
        return

    if not await is_admin(chat_id, message.from_user.id) and \
            groups[chat_id]['groups'][dest]['admin_only']:
        await bot.send_message(message.chat.id, localization.get_string('only_admins', lng), parse_mode='HTML')
        return

    if dest not in groups[chat_id]['groups']:
        await bot.send_message(message.chat.id, localization.get_string('group_not_exists', lng).format(group=dest),
                               parse_mode='HTML')
    else:
        await bot.send_message(chat_id, await message_compose(message, dest), parse_mode='HTML')


@dp.message_handler(commands="join")
async def join(message: types.Message):
    chat_id = str(message.chat.id)
    await create_db_entry(chat_id)
    lng = groups[chat_id]['lang']

    if await is_private(chat_id):
        await bot.send_message(chat_id, localization.get_string('private_chat', lng), parse_mode='HTML')
        return

    command = message.text.split()
    if len(command) <= 1:
        dest = 'all'
    else:
        dest = command[1]

    if not await is_blacklisted(chat_id, message.from_user.id):
        await bot.send_message(chat_id, localization.get_string('blacklist', lng), parse_mode='HTML')
        return

    if dest in groups[chat_id]['groups']:
        if str(message.from_user.id) in groups[chat_id]['groups'][dest]['users']:
            await bot.send_message(chat_id, localization.get_string('already_in', lng), parse_mode='HTML')
        else:
            groups[chat_id]['groups'][dest]['users'].append(str(message.from_user.id))
            db.save_db(groups)
            await bot.send_message(chat_id, localization.get_string('join_success', lng).format(group=dest),
                                   parse_mode='HTML')
    else:
        await bot.send_message(chat_id, localization.get_string('group_not_exists', lng), parse_mode='HTML')


@dp.message_handler(commands="leave")
async def leave(message: types.Message):
    chat_id = str(message.chat.id)
    await create_db_entry(chat_id)
    lng = groups[chat_id]['lang']

    if await is_private(chat_id):
        await bot.send_message(chat_id, localization.get_string('private_chat', lng), parse_mode='HTML')
        return

    command = message.text.split()
    if len(command) <= 1:
        dest = 'all'
    else:
        dest = command[1]

    if dest in groups[chat_id]['groups']:
        if str(message.from_user.id) not in groups[chat_id]['groups'][dest]['users']:
            await bot.send_message(chat_id, localization.get_string('not_in', lng), parse_mode='HTML')
        else:
            groups[chat_id]['groups'][dest]['users'].remove(str(message.from_user.id))
            db.save_db(groups)
            await bot.send_message(chat_id, localization.get_string('remove_success', lng).format(group=dest),
                                   parse_mode='HTML')
    else:
        await bot.send_message(chat_id, localization.get_string('group_not_exists', lng), parse_mode='HTML')


@dp.message_handler(commands="w")
async def whitelist(message: types.Message):
    chat_id = str(message.chat.id)
    await create_db_entry(chat_id)
    lng = groups[chat_id]['lang']

    if await is_private(chat_id):
        await bot.send_message(chat_id, localization.get_string('private_chat', lng), parse_mode='HTML')
        return

    command = message.text.split()
    if len(command) <= 1:
        dest = 'all'
    else:
        dest = command[1]

    if not await is_admin(chat_id, message.from_user.id):
        await bot.send_message(chat_id=chat_id, text=localization.get_string('for_admins', lng), reply_markup=None)
        return

    if dest in groups[chat_id]['groups']:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            if str(user_id) in groups[chat_id]['groups'][dest]['whitelist']:
                groups[chat_id]['groups'][dest]['whitelist'].remove(str(user_id))
                db.save_db(groups)
                await bot.send_message(chat_id, localization.get_string('un_whitelisted', lng).format(group=dest),
                                       parse_mode='HTML')
            else:
                groups[chat_id]['groups'][dest]['whitelist'].append(str(user_id))
                db.save_db(groups)
                await bot.send_message(chat_id, localization.get_string('whitelisted', lng).format(group=dest),
                                       parse_mode='HTML')
        else:
            text = localization.get_string('whitelist_', lng) + '\n'
            for i, item in enumerate(groups[chat_id]['groups'][dest]['whitelist']):
                user = await bot.get_chat(item)
                text += escape(user.first_name)
                if user.last_name:
                    text += ' ' + escape(user.last_name)

                if i != len(groups[chat_id]['groups'][dest]['users']) - 2:
                    text += ', '

            await bot.send_message(chat_id, text, parse_mode='HTML')

    else:
        await bot.send_message(chat_id, localization.get_string('group_not_exists', lng), parse_mode='HTML')


@dp.message_handler(commands="b")
async def blacklist(message: types.Message):
    chat_id = str(message.chat.id)
    await create_db_entry(chat_id)
    lng = groups[chat_id]['lang']

    if await is_private(chat_id):
        await bot.send_message(chat_id, localization.get_string('private_chat', lng), parse_mode='HTML')
        return

    command = message.text.split()
    if len(command) <= 1:
        dest = 'all'
    else:
        dest = command[1]

    if not await is_admin(chat_id, message.from_user.id):
        await bot.send_message(chat_id=chat_id, text=localization.get_string('for_admins', lng), reply_markup=None)
        return

    if dest in groups[chat_id]['groups']:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            if str(user_id) in groups[chat_id]['blacklist']:
                groups[chat_id]['blacklist'].remove(str(user_id))
                db.save_db(groups)
                await bot.send_message(chat_id, localization.get_string('un_blacklisted', lng).format(group=dest),
                                       parse_mode='HTML')
            else:
                groups[chat_id]['blacklist'].append(str(user_id))
                db.save_db(groups)
                await bot.send_message(chat_id, localization.get_string('blacklisted', lng).format(group=dest),
                                       parse_mode='HTML')
        else:
            text = localization.get_string('blacklist_', lng) + '\n'
            for i, item in enumerate(groups[chat_id]['blacklist']):
                user = await bot.get_chat(item)
                text += escape(user.first_name)
                if user.last_name:
                    text += ' ' + escape(user.last_name)

                if i != len(groups[chat_id]['blacklist']) - 1:
                    text += ', '

            await bot.send_message(chat_id, text, parse_mode='HTML')

    else:
        await bot.send_message(chat_id, localization.get_string('group_not_exists', lng), parse_mode='HTML')


@dp.message_handler(commands="add_group")
async def add_group(message: types.Message):
    chat_id = str(message.chat.id)
    await create_db_entry(chat_id)
    lng = groups[chat_id]['lang']

    if await is_private(chat_id):
        await bot.send_message(chat_id, localization.get_string('private_chat', lng), parse_mode='HTML')
        return

    if not await is_blacklisted(chat_id, message.from_user.id):
        await bot.send_message(chat_id, localization.get_string('blacklist', lng), parse_mode='HTML')
        return

    if await is_locked(chat_id, message.from_user.id):
        await bot.send_message(chat_id, localization.get_string('locked_msg', lng), parse_mode='HTML')
        return

    command = message.text.split()
    if len(command) <= 1:
        await bot.send_message(chat_id, localization.get_string('wrong_arg', lng), parse_mode='HTML')
        return
    else:
        dest = command[1]

    if len(dest) > 32:
        await bot.send_message(chat_id, localization.get_string('long_name', lng), parse_mode='HTML')
        return

    dest = escape(dest)

    if dest not in groups[chat_id]['groups']:
        groups[chat_id]['groups'][dest] = {
            'users': [],
            'admin_only': False,
            'invisible_tag': False,
            'enable_whitelist': False,
            'whitelist': []
        }
        db.save_db(groups)
        await bot.send_message(chat_id, localization.get_string('create_success', lng).format(group=dest),
                               parse_mode='HTML')
    else:
        await bot.send_message(chat_id, localization.get_string('group_already_exists', lng), parse_mode='HTML')


@dp.message_handler(commands="remove_group")
async def remove_group(message: types.Message):
    chat_id = str(message.chat.id)
    await create_db_entry(chat_id)
    lng = groups[chat_id]['lang']

    if await is_private(chat_id):
        await bot.send_message(chat_id, localization.get_string('private_chat', lng), parse_mode='HTML')
        return

    if not await is_blacklisted(chat_id, message.from_user.id):
        await bot.send_message(chat_id, localization.get_string('blacklist', lng), parse_mode='HTML')
        return

    if await is_locked(chat_id, message.from_user.id):
        await bot.send_message(chat_id, localization.get_string('locked_msg', lng), parse_mode='HTML')
        return

    command = message.text.split()

    if len(command) <= 1:
        await bot.send_message(chat_id, localization.get_string('wrong_arg_remove', lng), parse_mode='HTML')
        return
    else:
        dest = command[1]

    dest = escape(dest)

    if dest == 'all':
        await bot.send_message(chat_id, localization.get_string('all_protected', lng), parse_mode='HTML')
        return

    dest = escape(dest)

    if dest in groups[chat_id]['groups']:
        if groups[chat_id]['groups'][dest]['admin_only']:
            await bot.send_message(chat_id, localization.get_string('locked_msg', lng), parse_mode='HTML')
            return

        groups[chat_id]['groups'].pop(dest)
        db.save_db(groups)
        await bot.send_message(chat_id, localization.get_string('remove_group_success', lng).format(group=dest),
                               parse_mode='HTML')
    else:
        await bot.send_message(chat_id, localization.get_string('group_not_exists', lng), parse_mode='HTML')


@dp.message_handler(commands="show_groups")
async def show_groups(message: types.Message):
    chat_id = str(message.chat.id)
    await create_db_entry(chat_id)
    lng = groups[chat_id]['lang']

    if await is_private(chat_id):
        await bot.send_message(chat_id, localization.get_string('private_chat', lng), parse_mode='HTML')
        return

    text = localization.get_string('available_groups', lng) + '\n'

    for i, item in enumerate(groups[chat_id]['groups']):
        text += item
        if i != len(groups[chat_id]['groups']) - 1:
            text += ', '

    await bot.send_message(chat_id, text, parse_mode='HTML')


@dp.message_handler(commands="group_info")
async def group_info(message: types.Message):
    chat_id = str(message.chat.id)
    await create_db_entry(chat_id)
    lng = groups[chat_id]['lang']

    if await is_private(chat_id):
        await bot.send_message(chat_id, localization.get_string('private_chat', lng), parse_mode='HTML')
        return

    command = message.text.split()
    if len(command) <= 1:
        dest = 'all'
    else:
        dest = command[1]

    if dest in groups[chat_id]['groups']:
        text = localization.get_string('group_members', groups[chat_id]['lang']).format(group=dest) + '\n'

        for i, item in enumerate(groups[chat_id]['groups'][dest]['users']):
            try:
                user = await bot.get_chat(item)
            except exceptions.ChatNotFound:
                print(item)
                continue

            text += escape(user.first_name)
            if user.last_name:
                text += ' ' + escape(user.last_name)

            if i != len(groups[chat_id]['groups'][dest]['users']) - 1:
                text += ', '

        await bot.send_message(chat_id, text, parse_mode='HTML')

    else:
        await bot.send_message(chat_id, localization.get_string('group_not_exists', lng), parse_mode='HTML')


@dp.message_handler(commands="help")
async def bot_help(message: types.Message):
    await create_db_entry(message.chat.id)
    await bot.send_message(message.chat.id, localization.get_string('help', groups[message.chat.id]['lang']),
                           parse_mode='HTML')


@dp.message_handler(commands="lang")
async def lang(message: types.Message):
    chat_id = str(message.chat.id)
    await create_db_entry(chat_id)
    lng = groups[chat_id]['lang']

    buttons = types.InlineKeyboardMarkup(row_width=1)
    for i in localization.strings:
        buttons.add(types.InlineKeyboardButton(localization.strings[i]['name'], callback_data='lang_' + i))
    buttons.add(types.InlineKeyboardButton(localization.strings[groups[chat_id]['lang']]['cancel'],
                                           callback_data='cancel'))
    await bot.send_message(chat_id, localization.get_string('select_language', lng), parse_mode='HTML',
                           reply_markup=buttons)


@dp.message_handler(commands="settings")
async def settings(message: types.Message):
    chat_id = str(message.chat.id)
    await create_db_entry(chat_id)
    lng = groups[chat_id]['lang']

    if await is_private(chat_id):
        await bot.send_message(chat_id, localization.get_string('private_chat', lng), parse_mode='HTML')
        return

    if not await is_blacklisted(chat_id, message.from_user.id):
        await bot.send_message(chat_id, localization.get_string('blacklist', lng), parse_mode='HTML')
        return

    command = message.text.split()
    if len(command) <= 1:
        dest = 'all'
    else:
        dest = command[1]

    if not await is_admin(chat_id, message.from_user.id) and groups[chat_id]['groups'][dest]['admin_only']:
        await bot.send_message(chat_id=chat_id, text=localization.get_string('for_admins', lng))
        return

    if dest not in groups[chat_id]['groups']:
        await bot.send_message(chat_id, localization.get_string('group_not_exists', lng), parse_mode='HTML')
        return

    await bot.send_message(chat_id, localization.get_string('group_settings', lng).format(group=dest),
                           parse_mode='HTML', reply_markup=await settings_compose(message, dest))


@dp.message_handler(commands="lock")
async def lock(message: types.Message):
    chat_id = str(message.chat.id)
    await create_db_entry(chat_id)
    lng = groups[chat_id]['lang']

    if await is_private(chat_id):
        await bot.send_message(chat_id, localization.get_string('private_chat', lng), parse_mode='HTML')
        return

    if not await is_admin(chat_id, message.from_user.id):
        await bot.send_message(chat_id=chat_id, text=localization.get_string('for_admins', lng))
        return

    groups[chat_id]['create_admin'] = not groups[chat_id]['create_admin']
    db.save_db(groups)

    if groups[chat_id]['create_admin']:
        text = localization.get_string('locked', lng)
    else:
        text = localization.get_string('unlocked', lng)

    await bot.send_message(chat_id, text, parse_mode='HTML')


@dp.callback_query_handler()
async def callback_handler(call: types.CallbackQuery):
    if call.data.startswith("lang_"):
        groups[str(call.message.chat.id)]['lang'] = call.data.replace('lang_', '')
        db.save_db(groups)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=localization.strings[call.data.replace('lang_', '')]['done'],
                                    reply_markup=None)

    if call.data == "cancel":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=localization.strings[groups[str(call.message.chat.id)]['lang']]['done'],
                                    reply_markup=None)

    if call.data.startswith("inv_tag"):
        dest = call.data.replace('inv_tag', '')
        chat_id = str(call.message.chat.id)
        lng = groups[chat_id]['lang']

        if not await is_admin(call.message.chat.id, call.from_user.id) and \
                groups[chat_id]['groups'][dest]['admin_only']:
            await bot.answer_callback_query(call.id, text=localization.get_string('for_admins', lng), show_alert=True)
            return

        groups[chat_id]['groups'][dest]['invisible_tag'] = not groups[chat_id]['groups'][dest]['invisible_tag']
        db.save_db(groups)

        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id,
                                            reply_markup=await settings_compose(call.message, dest))

    if call.data.startswith("admin_only"):
        dest = call.data.replace('admin_only', '')
        chat_id = str(call.message.chat.id)
        lng = groups[chat_id]['lang']

        if not await is_admin(call.message.chat.id, call.from_user.id):
            await bot.answer_callback_query(call.id, text=localization.get_string('for_admins', lng), show_alert=True)
            return

        groups[chat_id]['groups'][dest]['admin_only'] = not groups[chat_id]['groups'][dest]['admin_only']
        db.save_db(groups)

        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id,
                                            reply_markup=await settings_compose(call.message, dest))

    if call.data.startswith("ew"):
        dest = call.data.replace('ew', '')
        chat_id = str(call.message.chat.id)
        lng = groups[chat_id]['lang']

        if not await is_admin(call.message.chat.id, call.from_user.id):
            await bot.answer_callback_query(call.id, text=localization.get_string('for_admins', lng), show_alert=True)
            return

        groups[chat_id]['groups'][dest]['enable_whitelist'] = not groups[chat_id]['groups'][dest]['enable_whitelist']
        db.save_db(groups)

        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id,
                                            reply_markup=await settings_compose(call.message, dest))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
