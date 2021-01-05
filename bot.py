#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telegram
import config
import logging
import os
import json
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext



updater = Updater(token=config.TOKEN, use_context=True)
dispatcher = updater.dispatcher


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def load_groups():
    try:
        logging.info("Trying to load groups")
        global groups
        with open('groups.json', 'r', encoding='utf-8') as json_data_file:
            groups_temp = json.load(json_data_file)
            groups = groups_temp
        logging.info("Buttons successfully loaded")
        
    except FileNotFoundError:
        logging.info(
            "There is no buttons list file in folder, so I created new")
        save_groups()
        
    except UnicodeDecodeError:
        logging.info(
            "Seems like this file is broken, so I created new")
        os.rename('groups.json','groups-broken.json')
        save_groups()

def save_groups():
    with open('groups.json', 'w', encoding='utf-8') as json_data_file:
        json.dump(groups, json_data_file, indent=4, ensure_ascii=False)
    logging.info("Banned users list successfully saved")
    
    
load_groups()
    
def chk_usr(context, user_id):
    try:
        context.bot.get_chat(user_id)
        return 1
    except telegram.error.BadRequest as excp:
        return 0

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Этот бот позволяет тегать всех участников чата. Чтобы это сделать, отправьте команду /tag_all.")
    
def tag(update, context):
    result = update.message.text_markdown.split()
    if str(update.effective_chat.id) in groups:
        if len(result) == 1:
            if 'all' in groups[str(update.effective_chat.id)]:
                if not groups[str(update.effective_chat.id)]['all']:
                    context.bot.send_message(chat_id=update.effective_chat.id, 
                                            text="В данный момент, группа пуста. Присоединитесь или добавьте в неё пользователей.",
                                            parse_mode=ParseMode.MARKDOWN)
                else:
                    text = ''
                    size = len(groups[str(update.effective_chat.id)]['all'])
                    i = 0
                    while i < size:
                        if chk_usr(context, groups[str(update.effective_chat.id)]['all'][i]) == 0:
                            groups[str(update.effective_chat.id)]['all'].pop(i)
                            size -= 1
                            continue
                        user = context.bot.get_chat(groups[str(update.effective_chat.id)]['all'][i])
                        if user.username is not None:
                            text += '@' + user.username + ' '
                        elif user.last_name is not None:
                            text += '[' + user.first_name + ' ' + user.last_name + '](tg://user?id=' + str(user.id) + ') '
                        else: 
                            text += '[' + user.first_name + '](tg://user?id=' + str(user.id) + ') '
                        i += 1
                    context.bot.send_message(chat_id=update.effective_chat.id, 
                                                text=text,
                                                parse_mode=ParseMode.MARKDOWN)
                    
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, 
                                        text='Группы "all" ещё нет, но вы можете создать её. Эта группа будет тегаться по команде "/tag" без аргументов.',
                                        parse_mode=ParseMode.MARKDOWN)
                
        elif result[1] in groups[str(update.effective_chat.id)]:
            if not groups[str(update.effective_chat.id)][str(result[1])]:
                context.bot.send_message(chat_id=update.effective_chat.id, 
                                            text="В данный момент, группа пуста. Присоединитесь или добавьте в неё пользователей.",
                                            parse_mode=ParseMode.MARKDOWN)
            else:
                text = ''
                size = len(groups[str(update.effective_chat.id)][result[1]])
                i = 0
                while i < size:
                    if chk_usr(context, groups[str(update.effective_chat.id)][result[1]][i]) == 0:
                            groups[str(update.effective_chat.id)][result[1]].pop(i)
                            size -= 1
                            continue
                    user = context.bot.get_chat(groups[str(update.effective_chat.id)]['all'][i])
                    if user.username is not None:
                        text += '@' + user.username + ' '
                    elif user.last_name is not None:
                        text += '[' + user.first_name + ' ' + user.last_name + '](tg://user?id=' + str(user.id) + ')'
                    else: 
                        text += '[' + user.first_name + '](tg://user?id=' + str(user.id) + ')'
                    i += 1
                context.bot.send_message(chat_id=update.effective_chat.id, 
                                            text=text,
                                            parse_mode=ParseMode.MARKDOWN)
                        
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, 
                                    text="Такой группы нет.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                    text="В этом чате нет групп. Создайте новую с помощью: /add_group *название_группы*")
        

    
def add_group(update, context):
    global groups
    user = update.message.from_user.id
    status = context.bot.get_chat_member(update.effective_chat.id, user).status
    if status == "creator" or status == "administrator":
        command = update.message.text_markdown
        result = update.message.text_markdown.split()
        if len(result) != 1:
            group_name = result[1]
            command = command.replace(result[0] + ' ' + result[1], '')
            tag_list = {group_name: []}
            
            if str(update.effective_chat.id) not in groups:
                groups[str(update.effective_chat.id)] = tag_list

            else:
                groups[str(update.effective_chat.id)][group_name] = []
                
            save_groups()
            update.message.reply_text('Готово! Группа под названием "' + group_name + '" создана.')
            print(groups)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, 
                                        text='Некорректный ввод. Использование команды: /add_group *название_группы*')
    else:
        update.message.reply_text("Данная команда доступна только администраторам чата")
        
def join(update, context):
    global groups
    user = update.message.from_user.id
    result = update.message.text_markdown.split()
    
    if str(update.effective_chat.id) not in groups:
            groups[str(update.effective_chat.id)] = {}
    
    if len(result) == 1:
        if 'all' in groups[str(update.effective_chat.id)]:
            if str(user) not in groups[str(update.effective_chat.id)]['all']:
                groups[str(update.effective_chat.id)]['all'].append(str(user))
                context.bot.send_message(chat_id=update.effective_chat.id, 
                                        text='Вы успешно присоединились к группе "all"',
                                        parse_mode=ParseMode.MARKDOWN)
            else: 
                context.bot.send_message(chat_id=update.effective_chat.id, 
                                        text='Вы уже есть в группе.',
                                        parse_mode=ParseMode.MARKDOWN)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, 
                                     text='Группы "all" ещё нет, но вы можете создать её. Эта группа будет тегаться по команде "/tag" без аргументов.',
                                     parse_mode=ParseMode.MARKDOWN)
    elif result[1] in groups[str(update.effective_chat.id)]:
        if len(result) > 2:
            try:
                context.bot.get_chat(result[1])
                if result[2] not in groups[str(update.effective_chat.id)][str(result[1])]:
                    groups[str(update.effective_chat.id)][result[1]].append(str(result[2]))
                    context.bot.send_message(chat_id=update.effective_chat.id, 
                                            text='Вы успешно добавили пользователя к группе "' + result[1] + '"!',
                                            parse_mode=ParseMode.MARKDOWN)
                else: 
                    context.bot.send_message(chat_id=update.effective_chat.id, 
                                            text='Этот пользователь уже есть в группе.',
                                            parse_mode=ParseMode.MARKDOWN)
            except telegram.error.BadRequest as excp:
                context.bot.send_message(chat_id=update.effective_chat.id, 
                                            text='Пользователя с таким ID не существует.',
                                            parse_mode=ParseMode.MARKDOWN)
        else:
            groups[str(update.effective_chat.id)][result[1]].append(str(user))
            context.bot.send_message(chat_id=update.effective_chat.id, 
                                    text='Вы успешно присоединились к группе "' + result[1] + '"!',
                                    parse_mode=ParseMode.MARKDOWN)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text="Некорректный ввод: такой группы нет.")
    save_groups()
    

def remove_group(update, context):
    global groups
    user = update.message.from_user.id
    status = context.bot.get_chat_member(update.effective_chat.id, user).status
    if status == "creator" or status == "administrator":
        result = update.message.text_markdown.split()

        if len(result) == 1:
            context.bot.send_message(chat_id=update.effective_chat.id, 
                                     text="Неверный аргумент.")
        
        elif str(update.effective_chat.id) not in groups or result[1] not in groups[str(update.effective_chat.id)]:
            context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text="Такой группы нет.")
        
        else:
            groups[str(update.effective_chat.id)].pop(result[1], None)
            save_groups()
            update.message.reply_text('Готово! Группа под названием "' + result[1] + '" удалена.')

    else:
        update.message.reply_text("Данная команда доступна только администраторам чата")

def show_groups(update, context, arg):
    global groups
    if str(update.effective_chat.id) not in groups:
        groups[str(update.effective_chat.id)] = {}
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text="В этом чате нет групп. Создать можно с помощью: /add_group *названиие_группы*")
            
    elif not groups[str(update.effective_chat.id)]:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text="В этом чате нет групп. Создать можно с помощью: /add_group *названиие_группы*")
    else:
        text = '*Доступные группы:\n*'
        for i in groups[str(update.effective_chat.id)]:
            text += i + ': '
            for j in range(len(groups[str(update.effective_chat.id)])):
                size = len(groups[str(update.effective_chat.id)][i])
                n = 0
                while n < size:
                    if chk_usr(context, groups[str(update.effective_chat.id)][i][n]) == 0:
                            groups[str(update.effective_chat.id)][i].pop(n)
                            size -= 1
                            continue
                    user = context.bot.get_chat(groups[str(update.effective_chat.id)][i][n])
                    if user.username is not None:
                        text += '@' + user.username + ' '
                    elif user.last_name is not None:
                        text += '[' + user.first_name + ' ' + user.last_name + '](tg://user?id=' + str(user.id) + ')'
                    else: 
                        text += '[' + user.first_name + '](tg://user?id=' + str(user.id) + ')'
                    if n < size:
                        text += ', '
                    n += 1
                text += '\n'
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text=text, parse_mode=ParseMode.MARKDOWN)
                
                


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(config.TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("tag", tag))
    dispatcher.add_handler(CommandHandler("add_group", add_group))
    dispatcher.add_handler(CommandHandler("remove_group", remove_group))
    dispatcher.add_handler(CommandHandler("tag", tag))
    dispatcher.add_handler(CommandHandler("join", join))
    dispatcher.add_handler(CommandHandler("show_groups", show_groups))
    #dispatcher.add_handler(CommandHandler("help", help_command))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()