#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telegram
import config
import logging
import os
import json
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, \
                         MessageHandler, Filters, CallbackContext

updater = Updater(token=config.TOKEN, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

groups = {all: []}


def load_db():
    try:
        logging.info("Trying to load groups DB.")
        global groups
        with open('groups.json', 'r', encoding='utf-8') as json_data_file:
            groups = json.load(json_data_file)
            
        logging.info("Groups DB successfully loaded!")
        
    except FileNotFoundError:
        logging.info(
            "There is no groups DB file in folder, so I created new.")
        save_db()
        
    except UnicodeDecodeError or JSONDecodeError:
        logging.info(
            "Seems like groups DB file is broken, so I backed up old one and created new.")
        os.rename('groups.json', 'groups-broken.json')
        save_db()


def save_db():
    with open('groups.json', 'w', encoding='utf-8') as json_data_file:
        json.dump(groups, json_data_file, indent=4, ensure_ascii=False)
    logging.info("Groups list successfully saved")

  
load_db()


def is_user_exists(user_id, context):
    try:
        context.bot.get_chat(user_id)
        return True
        
    except telegram.error.BadRequest as excp:
        return False


def can_delete_messages(update, context):
    if context.bot.get_chat_member(update.effective_chat.id,
                                   config.BOT_ID).can_delete_messages is True:
        context.bot.delete_message(chat_id=update.message.chat.id,
                                   message_id=update.message.message_id)


def start(update, context):
    chat_id = str(update.effective_chat.id)
    if not groups:
        if chat_id not in groups:
            groups[chat_id] = {all: []}
    context.bot.send_message(chat_id=chat_id,
                             text="Этот бот позволяет тегать всех участников чата. Чтобы это сделать, отправьте команду /tag all.")
    
    
def tag(update, context):
    result = update.message.text_markdown.split()
    chat_id = str(update.effective_chat.id)
    
    if chat_id in groups:
        if len(result) == 1:
            if 'all' in groups[chat_id]:
                if not groups[chat_id]['all']:
                    context.bot.send_message(chat_id=chat_id,
                                             text="В данный момент, группа пуста. Присоединитесь или добавьте в неё пользователей.",
                                             parse_mode=ParseMode.MARKDOWN)
                    
                else:
                    text = ''
                    size = len(groups[chat_id]['all'])
                    i = 0
                    print(context.bot.get_chat_member(chat_id, config.BOT_ID))
                    if context.bot.get_chat_member(chat_id, config.BOT_ID).can_delete_messages is True:
                        context.bot.delete_message(chat_id=chat_id,
                                                    message_id=update.message.message_id)
                    text = '*Вас тегнул пользователь ' + update.message.from_user.first_name + '.*\n'
                    while i < size:
                        if is_user_exists(groups[chat_id]['all'][i], context) == 0:
                            groups[chat_id]['all'].pop(i)
                            size -= 1
                            continue
                        user = context.bot.get_chat(groups[chat_id]['all'][i])
                        
                        if user.username is not None:
                            text += '@' + user.username + ' '
                        elif user.last_name is not None:
                            text += '[' + user.first_name + ' ' + user.last_name + '](tg://user?id=' + str(user.id) + ') '
                        else:
                            text += '[' + user.first_name + '](tg://user?id=' + str(user.id) + ') '
                        i += 1
                    context.bot.send_message(chat_id=chat_id,
                                             text=text,
                                             parse_mode=ParseMode.MARKDOWN)
                    
            else:
                context.bot.send_message(chat_id=chat_id,
                                         text='Группы "all" ещё нет, но вы можете создать её. Эта группа будет тегаться по команде "/tag" без аргументов.',
                                         parse_mode=ParseMode.MARKDOWN)
                
        elif result[1] in groups[chat_id]:
            if not groups[chat_id][result[1]]:
                context.bot.send_message(chat_id=chat_id,
                                         text="В данный момент, группа пуста. Присоединитесь или добавьте в неё пользователей.",
                                         parse_mode=ParseMode.MARKDOWN)
            else:
                text = ''
                size = len(groups[chat_id][result[1]])
                i = 0
                if context.bot.get_chat_member(chat_id, config.BOT_ID).can_delete_messages is True:
                        context.bot.delete_message(chat_id=chat_id,
                                                   message_id=update.message.message_id)
                text = '*Вас тегнул пользователь ' + update.message.from_user.first_name + '.*\n'

                while i < size:
                    print(groups[chat_id][result[1]][i])
                    if is_user_exists(groups[chat_id][result[1]][i], context) == 0:
                        groups[chat_id][result[1]].pop(i)
                        size -= 1
                        print("succ")
                        continue
                    user = context.bot.get_chat(groups[chat_id][result[1]][i])
                    print(user.username)
                    if user.username is not None:
                        text += '@' + user.username + ' '
                    elif user.last_name is not None:
                        text += '[' + user.first_name + ' ' + user.last_name + '](tg://user?id=' + str(user.id) + ')'
                    else:
                        text += '[' + user.first_name + '](tg://user?id=' + str(user.id) + ')'
                    i += 1
                context.bot.send_message(chat_id=chat_id,
                                         text=text,
                                         parse_mode=ParseMode.MARKDOWN)
                        
        else:
            context.bot.send_message(chat_id=chat_id,
                                     text="Такой группы нет.")
    else:
        context.bot.send_message(chat_id=chat_id,
                                 text="В этом чате нет групп. Создайте новую с помощью: /add_group *название_группы*")
        
 
def add_group(update, context):
    global groups
    user = update.message.from_user.id
    chat_id = str(update.effective_chat.id)
    status = context.bot.get_chat_member(chat_id, user).status
    
    if status == "creator" or status == "administrator":
        command = update.message.text_markdown
        result = update.message.text_markdown.split()
        if len(result) != 1:
            group_name = result[1]
            if group_name in groups[chat_id]:
                update.message.reply_text('Эта группа уже есть.')
                tag_list = {group_name: []}
            
            elif chat_id not in groups:
                groups[chat_id] = tag_list
                update.message.reply_text('Готово! Группа под названием "' + group_name + '" создана.')

            else:
                groups[chat_id][group_name] = []
                update.message.reply_text('Готово! Группа под названием "' + group_name + '" создана.')
                
            save_db()
            
            print(groups)
        else:
            context.bot.send_message(chat_id=chat_id,
                                        text='Некорректный ввод. Использование команды: /add_group *название_группы*')
    else:
        update.message.reply_text("Данная команда доступна только администраторам чата")


def join(update, context):
    global groups
    user = str(update.message.from_user.id)
    result = update.message.text_markdown.split()
    chat_id = str(update.effective_chat.id)
    
    if chat_id not in groups:
            groups[chat_id] = {all: []}
    
    if len(result) == 1:
        if 'all' in groups[chat_id]:
            if user not in groups[chat_id]['all']:
                groups[chat_id]['all'].append(user)
                context.bot.send_message(chat_id=chat_id,
                                         text='Вы успешно присоединились к группе "all"',
                                         parse_mode=ParseMode.MARKDOWN)
            else:
                context.bot.send_message(chat_id=chat_id,
                                         text='Вы уже есть в группе.',
                                         parse_mode=ParseMode.MARKDOWN)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Группы "all" ещё нет, но вы можете создать её. Эта группа будет тегаться по команде "/tag" без аргументов.',
                                     parse_mode=ParseMode.MARKDOWN)
    elif result[1] in groups[chat_id]:
        if len(result) > 2:
            try:
                context.bot.get_chat(result[2])
                if result[2] not in groups[chat_id][result[1]]:
                    groups[chat_id][result[1]].append(result[2])
                    context.bot.send_message(chat_id=chat_id,
                                             text='Вы успешно добавили пользователя к группе "' + result[1] + '"!',
                                             parse_mode=ParseMode.MARKDOWN)
                else:
                    context.bot.send_message(chat_id=chat_id,
                                             text='Этот пользователь уже есть в группе.',
                                             parse_mode=ParseMode.MARKDOWN)
            except telegram.error.BadRequest as excp:
                context.bot.send_message(chat_id=chat_id,
                                         text='Пользователя с таким ID не существует.',
                                         parse_mode=ParseMode.MARKDOWN)
        else:
            if user not in groups[chat_id][result[1]]:
                groups[chat_id][result[1]].append(user)
                context.bot.send_message(chat_id=chat_id,
                                         text='Вы успешно присоединились к группе "' + result[1] + '"!',
                                         parse_mode=ParseMode.MARKDOWN)
            else:
                context.bot.send_message(chat_id=chat_id,
                                         text='Вы уже есть в группе.',
                                         parse_mode=ParseMode.MARKDOWN)
                
    else:
        context.bot.send_message(chat_id=chat_id,
                                 text="Некорректный ввод: такой группы нет.")
    save_db()
    
    
def leave(update, context):
    global groups
    user = str(update.message.from_user.id)
    chat_id = str(update.effective_chat.id)
    result = update.message.text_markdown.split()
    
    if len(result) == 1:
        if 'all' in groups[chat_id]:
            if user in groups[chat_id]['all']:
                groups[chat_id]['all'].remove(user)
                context.bot.send_message(chat_id=chat_id,
                                         text='Вы успешно вышли из группы "all"',
                                         parse_mode=ParseMode.MARKDOWN)
            else:
                context.bot.send_message(chat_id=chat_id,
                                         text='Вас и не было в группе.',
                                         parse_mode=ParseMode.MARKDOWN)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Группы "all" ещё нет, но вы можете создать её. Эта группа будет тегаться по команде "/tag" без аргументов.',
                                     parse_mode=ParseMode.MARKDOWN)
    elif result[1] in groups[chat_id]:
        if len(result) > 2:
            try:
                context.bot.get_chat(result[2])
                if result[2] in groups[chat_id][result[1]]:
                    groups[chat_id][str(result[1])].remove(str(result[2]))
                    context.bot.send_message(chat_id=chat_id,
                                             text='Вы успешно удалили пользователя из группы "' + result[1] + '"!',
                                             parse_mode=ParseMode.MARKDOWN)
                else:
                    context.bot.send_message(chat_id=chat_id,
                                             text='Этого пользователя нет в группе.',
                                             parse_mode=ParseMode.MARKDOWN)
            except telegram.error.BadRequest as excp:
                context.bot.send_message(chat_id=chat_id,
                                         text='Пользователя с таким ID не существует.',
                                         parse_mode=ParseMode.MARKDOWN)
        else:
            if user in groups[chat.id][str(result[1])]:
                groups[chat_id][str(result[1])].remove(user)
                context.bot.send_message(chat_id=chat_id,
                                         text='Вы успешно вышли из группы "' + result[1] + '"!',
                                         parse_mode=ParseMode.MARKDOWN)
            else:
                context.bot.send_message(chat_id=chat_id,
                                         text='Вас и так нет в группе.',
                                         parse_mode=ParseMode.MARKDOWN)
    else:
        context.bot.send_message(chat_id=chat_id,
                                 text="Некорректный ввод: такой группы нет.")
    save_db()                 
    

def remove_group(update, context):
    global groups
    user = update.message.from_user.id
    status = context.bot.get_chat_member(update.effective_chat.id, user).status
    chat_id = str(update.effective_chat.id)
    
    if status == "creator" or status == "administrator":
        result = update.message.text_markdown.split()

        if len(result) == 1:
            context.bot.send_message(chat_id=chat_id,
                                     text="Неверный аргумент.")
        
        elif chat_id not in groups or result[1] not in groups[chat_id]:
            context.bot.send_message(chat_id=chat_id,
                                     text="Такой группы нет.")
        
        else:
            groups[chat_id].pop(result[1], None)
            save_db()
            update.message.reply_text('Готово! Группа под названием "' + result[1] + '" удалена.')

    else:
        update.message.reply_text("Данная команда доступна только администраторам чата")


def show_groups(update, context):
    global groups
    chat_id = str(update.effective_chat.id)
    
    if chat_id not in groups:
        groups[chat_id] = {}
        context.bot.send_message(chat_id=chat_id,
                                 text="В этом чате нет групп. Создать можно с помощью: /add_group *названиие_группы*")
            
    elif not groups[chat_id]:
        context.bot.send_message(chat_id=chat_id,
                                 text="В этом чате нет групп. Создать можно с помощью: /add_group *названиие_группы*")
    else:
        text = '<b>Доступные группы:</b>\n'
        for i in groups[chat_id]:
            text += i + ': '
            size = len(groups[chat_id][i])
            n = 0
            if size == 0:
                text += 'пусто'
            else:
                while n < size:
                    if is_user_exists(groups[chat_id][i][n], context) == 0:
                            groups[chat_id][i].pop(n)
                            size -= 1
                            continue
                    user = context.bot.get_chat(groups[chat_id][i][n])
                    if user.last_name is not None:
                        text += user.first_name + ' ' + user.last_name
                    else:
                        text += user.first_name
                    if n + 1 < size:
                        text += ', '
                    n += 1
            text += '\n'
            
        context.bot.send_message(chat_id=chat_id,
                                 text=text, parse_mode=ParseMode.HTML)
      
          
def tag_all(update, context):
    if update.message.text.startswith('@all'):
#        class NewFromUser:
#            first_name = update.message.from_user.first_name
#            last_name = update.message.from_user.last_name
#            
#        class NewMessage:
#            text_markdown = '/tag all'
#            message_id = update.message.message_id
#            from_user = NewFromUser()
#            
#        class NewUpdate:
#            effective_chat = update.effective_chat
#            message = NewMessage()
#            
#        new_update = NewUpdate()
#        tag(new_update, context)
        tag(update, context)
    

def main():
    updater = Updater(config.TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("tag", tag))
    dispatcher.add_handler(CommandHandler("add_group", add_group))
    dispatcher.add_handler(CommandHandler("remove_group", remove_group))
    dispatcher.add_handler(CommandHandler("join", join))
    dispatcher.add_handler(CommandHandler("show_groups", show_groups))
    dispatcher.add_handler(CommandHandler("leave", leave))
    dispatcher.add_handler(MessageHandler(Filters.text, tag_all))
    
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
