# -*- coding: utf-8 -*-

strings = {
    'ru': {
        'name': 'Русский',
        'welcome': '<b>Привет, это TrashPingBot!</b>\nС помощью данного бота вы сможете мгновенно упоминать участников'
                   ' чата. Для детальной информации нажмите '
                   'на /help',
        'help': '<b>Инструкция по использованию:</b>\n'
                'Прежде чем тегать всех пользователей, необходимо создать группу пользователей, либо присоединиться в '
                'уже имеющуюся. При добавлении бота в чат автоматически создаётся группа "all", в которую будут '
                'добавляться все участники чата. Чтобы присоединиться к ней, нажмите на команду <i>/join</i>. \n\n'
                'Чтобы создать свою группу, необходимо использовать другую команду:'
                ' <i>/tag *название_группы*</i>. Для входа в данную группу понадобится уже другая команда: <i>/join '
                '*название_группы*</i>.',
        'select_language': 'Выберите язык бота:',
        'cancel': 'Отмена',
        'done': 'Готово!',
        'empty_group': 'На данный момент группа "{group}" пуста. Вы можете присоединиться к ней с помощью команды /join',
        'tag': '<b>Вас тегнул пользователь {name}</b>',
        'private_chat': 'Эта функция не работает в приватном чате.',
        'already_in': 'Вы уже участник этой группы.',
        'group_not_exists': 'Этой группы не существует.',
        'join_success': 'Вы успешно вошли в группу {group}!',
        'remove_success': 'Вы успешно вышли из группы {group}!',
        'remove_group_success': 'Вы успешно удалили группу {group}!',
        'not_in': 'Вы не являетесь участником этой группы.',
        'wrong_arg': 'Неверный аргумент. Использование: /add_group *название_группы*',
        'wrong_arg_users': 'Неверный аргумент. Использование: /group_info *название_группы*',
        'wrong_arg_remove': 'Неверный аргумент. Использование: /remove_group *название_группы*',
        'all_protected': 'Вы не можете удалить группу "all".',
        'available_groups': '<b>Доступные группы:</b>',
        'group_members': '<b>Участники группы {group}:</b>',
        'whitelist_': '<b>Участники в белом списке:</b>',
        'blacklist_': '<b>Участники в чёрном списке:</b>',
        'wrong_arg_settings': 'Неверный аргумент. Использование: /settings *название_группы*',
        'inv_tag': 'Невидимый тег: {status}',
        'admin_only': 'Только для админов: {status}',
        'group_settings': '<b>Настройки группы "{group}":</b>',
        'only_admins': 'Только админы могут тегнуть эту группу.',
        'for_admins': 'Эти настройки доступны только для админов.',
        'create_success': 'Группа "{group}" успешно создана!',
        'group_already_exists': 'Такая группа уже есть.',
        'enable_whitelist': 'Белый список: {status}',
        'un_whitelisted': 'Пользователь успешно удалён из белого списка группы "{group}".',
        'un_blacklisted': 'Пользователь успешно разблокирован в группе "{group}".',
        'whitelisted': 'Вы успешно добавили пользователя в группу "{group}"!',
        'blacklisted': 'Вы успешно заблокировали пользователя в группе "{group}".',
        'whitelist': 'Эту группу могут тегать только участники в белом списке.',
        'blacklist': 'Вы были заблокированы админом.',
        'long_name': 'Имя группы слишком длинное (макс. 32 символа).',
        'locked': 'Редактирование групп неадминам успешно запрещено.',
        'unlocked': 'Редактирование групп неадминам успешно разрешено!',
        'locked_msg': 'В этой группе запрещено создавать или редактировать группы неадминам.',
        'empty': 'Эта группа пуста. Присоединитесь с помощью /join *имя_группы*.'

    },
    'en': {
        'name': 'English',
        'welcome': "<b>Hi, it's TrashPingBot!</b>\nWith this bot you can instantly mention members in"
                   'chat. For more information click /help',
        'help': '<b>How to use:</b>\n'
                'Before tagging people, you need to create a group, or join existing one. '
                'Bot will automatically create group "all" on join, in which chat members will join. '
                'To join, press <i>/join</i>. \n\n'
                'You will need another command to create your own group:'
                ' <i>/tag *group_name*</i>. To join it, just type: <i>/join '
                '*group_name*</i>.',
        'fallback': 'An issue occurred with localization. Please contact @artanzo for further investigation.',
        'select_language': 'Select bot language:',
        'cancel': 'Cancel',
        'done': 'Done!',
        'empty_group': 'Seems like group "{group}" is empty. You can join it using command /join',
        'tag': '<b>You were tagged by {name}</b>',
        'already_in': 'You already a group member.',
        'group_not_exists': 'This group does not exist.',
        'join_success': 'Successfully joined group {group}!',
        'remove_success': 'Successfully left group {group}!',
        'remove_group_success': 'Successfully deleted group {group}!',
        'not_in': 'You are not member of this group.',
        'wrong_arg': 'Wrong argument. Usage: /add_group *group_name*',
        'wrong_arg_group': 'Wrong argument. Usage: /remove_group *group_name*',
        'wrong_arg_users': 'Wrong argument. Usage: /group_info *group_name*',
        'all_protected': 'Sorry, you can not delete group "all".',
        'available_groups': '<b>Available groups:</b>',
        'group_members': '<b>{group} members:</b>',
        'whitelist_': '<b>Whitelisted people:</b>',
        'blacklist_': '<b>Blacklisted people:</b>',
        'wrong_arg_settings': 'Wrong argument. Usage: /settings *group_name*',
        'inv_tag': 'Invisible tag: {status}',
        'admin_only': 'Admin only: {status}',
        'enabled': ' ✅',
        'disabled': ' ❌',
        'group_settings': '<b>"{group}" settings:</b>',
        'only_admins': 'Only admins can tag this group.',
        'for_admins': 'This settings are only accessible for admins.',
        'create_success': 'Created group "{group}" successfully!',
        'group_already_exists': 'This group already exists.',
        'enable_whitelist': 'Whitelist: {status}',
        'un_whitelisted': 'Removed from "{group}" whitelist successfully.',
        'un_blacklisted': 'Removed from "{group}" blacklist successfully.',
        'whitelisted': 'Added to "{group}" whitelist successfully!',
        'blacklisted': 'Added to "{group}" blacklist successfully!',
        'whitelist': 'This group can be tagged only by people in whitelist.',
        'blacklist': 'You were banned by admin.',
        'long_name': 'Group name is too long (max is 32 symbols).',
        'ce': 'Admin only',
        'locked': 'Locked groups editing for non-admins successfully.',
        'unlocked': 'Allowed groups editing for non-admins successfully!',
        'locked_msg': 'Editing groups is allowed only for admins.',
        'empty': 'This group is empty. Join using /join *group_name*.'
    }

}


def get_string(key, lang):
    if lang in strings:
        loc = strings.get(lang)
    else:
        loc = strings.get('en')

    if key in loc:
        return loc[key]

    else:
        loc = strings.get('en')
        if key in loc:
            return loc[key]
        else:
            return loc['fallback']
