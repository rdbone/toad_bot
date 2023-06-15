from random import randint, choice
import re

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc, service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2
from emoji import emojize
import ephem
from telegram import ReplyKeyboardMarkup, KeyboardButton

import settings

# Функция генерирует смайлик
def get_smile(user_data):
    if 'emoji' not in user_data:
        smile = choice(settings.USER_EMOJI)
        return emojize(smile, language='alias')
    return user_data['emoji']

# Проверяет, что объект есть в списке объектов пакета ephem
def check_planet(planet):
    for item in ephem._libastro.builtin_planets():
        if planet in str(item):
            return True
    return False   

#Игра в случайные числа
def play_random_numbers(user_number):
    bot_number = randint(user_number - 10, user_number +10)
    if user_number > bot_number:
        message = f'Твое число {user_number}, мое - {bot_number}, ты выиграл!'
    elif user_number == bot_number:
        message = f'Твое число {user_number}, мое - {bot_number}, ничья!'
    else:
        message = f'Твое число {user_number}, мое - {bot_number}, я выиграл!'
    return message

#Функция для проверки города в игре в города
def check_city(user_city, user_data):
    #базовые проверки введенного города на первый символ и что не введены символы кроме букв и двух тире/дефисов
    result = re.fullmatch("[ёа-я]*\s?[-‐‑-ꟷー一]?[ёа-я]*\s?[-‐‑-ꟷー一]?[ёа-я]*", user_city)
    if not result:
        return f'Введи город на русском'
    if user_city[0] in ['ы', 'ъ', 'ь']:
        return f'Город не может начинаться с такой буквы'
    #проверяем, играл ли пользователь уже в эту игру, если нет, то записываем для него список городов
    if 'initial_cities' not in user_data:
        if user_city in [x.lower() for x in settings.INITIAL_CITIES]:
            user_data['initial_cities'] = [x.lower() for x in settings.INITIAL_CITIES]
            user_data['passed_cities'] = []
            user_data['current_user_letter'] = user_city[0]
        else:
            return f'Не знаю такого города'
    #тут основная логика
    if  user_city[0] != user_data['current_user_letter']:
        return f'Твой город должен начинаться с буквы {user_data["current_user_letter"].capitalize()}'
    if user_city in user_data['initial_cities']:
        user_data['passed_cities'].append(user_city)
        user_data['initial_cities'].remove(user_city)
        i = 1
        while user_city[-i] in ['ы', 'ъ', 'ь']:
            i += 1
        letter = user_city[-i]
        r = re.compile(f"{letter}[ёа-я]*[-‐‑-ꟷー一]?[ёа-я]*[-‐‑-ꟷー一]?[ёа-я]*")
        try:
            suitable_cities = list(filter(r.match, user_data['initial_cities']))
            bot_city = choice(suitable_cities)
            user_data['passed_cities'].append(bot_city)
            user_data['initial_cities'].remove(bot_city)
            ind = 1
            while bot_city[-ind] in ['ы', 'ъ', 'ь']: 
                ind += 1
            user_data['current_user_letter'] = bot_city[-ind]
            return f'{bot_city.capitalize()}. Твой ход'
        except IndexError:
            return f'Не знаю больше городов на букву {letter.capitalize()}. Ты выиграл'
    elif user_city in user_data['passed_cities']:
        return f'Город {user_city.capitalize()} уже был'
    else:
        return f'Не знаю такого города'
    
#Функция замены запятой на точку и приведения типов в калькуляторе
def change_delimeter_and_type(numbers):
    numbers = [item.replace(',', '.') for item in numbers]
    for i, item in enumerate(numbers):
        if '.' in item:
            item = float(item)
            numbers[i] = item
        else:
            item = int(item)
            numbers[i] = item
    return numbers

#Функция вычислений калькулятора
def calculation(user_string, numbers):
    if '+' in user_string:
        return f'Результат сложения: {numbers[0] + numbers[1]}'
    elif '-' in user_string:
        return f'Результат вычитания: {numbers[0] - numbers[1]}'
    elif '*' in user_string:
        return f'Результат умножения: {numbers[0] * numbers[1]}'
    elif '/' in user_string:
        try:
            division_result = numbers[0]/numbers[1]
            return f'Результат деления: {division_result}'
        except ZeroDivisionError:
            return 'На ноль делить нельзя'
        
#Функция определения выражения калькулятора
def convert_to_calc(user_string): 
    result = re.fullmatch("-?[0-9]+[.,]?[0-9]*[-+*/]-?[0-9]+[.,]?[0-9]*", user_string)
    if not result:
        return 'Введи корректное выражение после команды'
    signs = [x for x in user_string if x in '-+*/']
    number_of_signs = len(signs)
    if number_of_signs == 1: #2 positives
        number_list = re.split('[-+*/]',user_string)
        number_list = change_delimeter_and_type(number_list)
        return calculation(user_string, number_list)
    elif number_of_signs == 3:
        if len(set(signs)) == 1: #2 negatives, minus
            number_list = user_string.split('-')
            number_list = [x for x in number_list if x != '']
            number_list = change_delimeter_and_type(number_list)
            number_list = [-x for x in number_list]
            return calculation(user_string, number_list)
        else: #2 negatives, another action
            user_string = user_string.replace('-','')
            number_list = re.split('[+*/]',user_string)
            number_list = change_delimeter_and_type(number_list)
            number_list = [-x for x in number_list]
            return calculation(user_string, number_list)
    elif number_of_signs == 2: #1 negative
        result = re.fullmatch("-[0-9]+[.,]?[0-9]*[-+*/][0-9]+[.,]?[0-9]*", user_string)
        if not result:
            if len(set(signs)) == 1: #Second negative, minus
                number_list = user_string.split('-')
                number_list = [x for x in number_list if x != '']
                number_list = change_delimeter_and_type(number_list)
                number_list[1] = number_list[1] * (-1)
                return calculation(user_string, number_list)
            else: #Second negative, another action
                user_string = user_string.replace('-','')
                number_list = re.split('[+*/]',user_string)
                number_list = change_delimeter_and_type(number_list)
                number_list[1] = number_list[1] * (-1)
                return calculation(user_string, number_list)
        if len(set(signs)) == 1: #First negative, minus
            number_list = user_string.split('-')
            number_list = [x for x in number_list if x != '']
            number_list = change_delimeter_and_type(number_list)
            number_list[0] = number_list[0] * (-1)
            return calculation(user_string, number_list)
        else: #First negative, another action
            user_string = user_string.replace('-','')
            number_list = re.split('[+*/]',user_string)
            number_list = change_delimeter_and_type(number_list)
            number_list[0] = number_list[0] * (-1)
            return calculation(user_string, number_list)
        
#функция клавиатуры
def main_keyboard():
    return ReplyKeyboardMarkup([['Рандомный жабокрад', KeyboardButton('Мое гео', request_location=True), 'Заполнить анкету']])

#функция определения, что на картинке жаба
def has_object_on_image(file_name, object_names):
    channel = ClarifaiChannel.get_grpc_channel()
    app = service_pb2_grpc.V2Stub(channel)
    metadata = (('authorization', f'Key {settings.CLARIFAI_API_KEY}'),)

    with open(file_name, 'rb') as f:
        file_data = f.read()
        image = resources_pb2.Image(base64=file_data)

        request = service_pb2.PostModelOutputsRequest(
            model_id='aaa03c23b3724a16a56b629203edc62c',
            inputs=[
            resources_pb2.Input(data=resources_pb2.Data(image=image))
            ])
        response = app.PostModelOutputs(request, metadata=metadata)
        return check_response_for_object(response, object_names)

def check_response_for_object(response, object_names):
    if response.status.code == status_code_pb2.SUCCESS:
        for concept in response.outputs[0].data.concepts:
            if concept.name in object_names and concept.value >= 0.8:
                return True
    else:
        return f'Ошибка распознавания картинки {response.outputs[0].status.details}'
    return False

if __name__ == '__main__':
    print(has_object_on_image('images/toad_singapore_1.jpg', ['toad', 'frog']))
    print(has_object_on_image('images/toad_singapore_2.jpg', ['toad', 'frog']))
    print(has_object_on_image('images/toad_singapore_3.jpg', ['toad', 'frog']))
    print(has_object_on_image('images/toad_death_note.jpg', ['toad', 'frog']))
    print(has_object_on_image('images/toad_singapore_4.jpg', ['toad', 'frog']))
    print(has_object_on_image('images/toad_pokemon.jpg', ['toad', 'frog']))
    print(has_object_on_image('images/brunch_latte.jpg', ['toad', 'frog']))
    print(has_object_on_image('images/lizard_enemy.jpg', ['toad', 'frog']))