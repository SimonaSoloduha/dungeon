# -*- coding: utf-8 -*-

# Подземелье было выкопано ящеро-подобными монстрами рядом с аномальной рекой, постоянно выходящей из берегов.
# Из-за этого подземелье регулярно затапливается, монстры выживают, но не герои, рискнувшие спуститься к ним в поисках
# приключений.
# Почуяв безнаказанность, ящеры начали совершать набеги на ближайшие деревни. На защиту всех деревень не хватило
# солдат и вас, как известного в этих краях героя, наняли для их спасения.
#
# Карта подземелья представляет собой json-файл под названием rpg.json. Каждая локация в лабиринте описывается объектом,
# в котором находится единственный ключ с названием, соответствующем формату "Location_<N>_tm<T>",
# где N - это номер локации (целое число), а T (вещественное число) - это время,
# которое необходимо для перехода в эту локацию. Например, если игрок заходит в локацию "Location_8_tm30000",
# то он тратит на это 30000 секунд.
# По данному ключу находится список, который содержит в себе строки с описанием монстров а также другие локации.
# Описание монстра представляет собой строку в формате "Mob_exp<K>_tm<M>", где K (целое число) - это количество опыта,
# которое получает игрок, уничтожив данного монстра, а M (вещественное число) - это время,
# которое потратит игрок для уничтожения данного монстра.
# Например, уничтожив монстра "Boss_exp10_tm20", игрок потратит 20 секунд и получит 10 единиц опыта.
# Гарантируется, что в начале пути будет две локации и один монстр
# (то есть в коренном json-объекте содержится список, содержащий два json-объекта, одного монстра и ничего больше).
#
# На прохождение игры игроку дается 123456.0987654321 секунд.
# Цель игры: за отведенное время найти выход ("Hatch")
#
# По мере прохождения вглубь подземелья, оно начинает затапливаться, поэтому
# в каждую локацию можно попасть только один раз,
# и выйти из нее нельзя (то есть двигаться можно только вперед).
#
# Чтобы открыть люк ("Hatch") и выбраться через него на поверхность, нужно иметь не менее 280 очков опыта.
# Если до открытия люка время заканчивается - герой задыхается и умирает, воскрешаясь перед входом в подземелье,
# готовый к следующей попытке (игра начинается заново).
#
# Гарантируется, что искомый путь только один, и будьте аккуратны в рассчетах!
# При неправильном использовании библиотеки decimal человек, играющий с вашим скриптом рискует никогда не найти путь.
#
# Также, при каждом ходе игрока ваш скрипт должен запоминать следущую информацию:
# - текущую локацию
# - текущее количество опыта
# - текущие дату и время (для этого используйте библиотеку datetime)
# После успешного или неуспешного завершения игры вам необходимо записать
# всю собранную информацию в csv файл dungeon.csv.
# Названия столбцов для csv файла: current_location, current_experience, current_date
#
#
# Пример взаимодействия с игроком:
#
# Вы находитесь в Location_0_tm0
# У вас 0 опыта и осталось 123456.0987654321 секунд до наводнения
# Прошло времени: 00:00
#
# Внутри вы видите:
# — Вход в локацию: Location_1_tm1040
# — Вход в локацию: Location_2_tm123456
# Выберите действие:
# 1.Атаковать монстра
# 2.Перейти в другую локацию
# 3.Сдаться и выйти из игры
#
# Вы выбрали переход в локацию Location_2_tm1234567890
#
# Вы находитесь в Location_2_tm1234567890
# У вас 0 опыта и осталось 0.0987654321 секунд до наводнения
# Прошло времени: 20:00
#
# Внутри вы видите:
# — Монстра Mob_exp10_tm10
# — Вход в локацию: Location_3_tm55500
# — Вход в локацию: Location_4_tm66600
# Выберите действие:
# 1.Атаковать монстра
# 2.Перейти в другую локацию
# 3.Сдаться и выйти из игры
#
# Вы выбрали сражаться с монстром
#
# Вы находитесь в Location_2_tm0
# У вас 10 опыта и осталось -9.9012345679 секунд до наводнения
#
# Вы не успели открыть люк!!! НАВОДНЕНИЕ!!! Алярм!
#
# У вас темнеет в глазах... прощай, принцесса...
# Но что это?! Вы воскресли у входа в пещеру... Не зря матушка дала вам оберег :)
# Ну, на этот-то раз у вас все получится! Трепещите, монстры!
# Вы осторожно входите в пещеру... (текст умирания/воскрешения можно придумать свой ;)
#
# Вы находитесь в Location_0_tm0
# У вас 0 опыта и осталось 123456.0987654321 секунд до наводнения
# Прошло уже 0:00:00
# Внутри вы видите:
#  ...
#  ...
#
# и так далее...
import csv
import json
import re
from decimal import Decimal, getcontext
from pprint import pprint

from termcolor import cprint


class Dungeon:

    def __init__(self, json_file='rpg.json', remaining_time='123456.0987654321', exit_from_dungeon='Hatch'):
        self.json_file = json_file
        self.next_location = 'Location_0_tm0'
        self.experience = 0
        self.time = remaining_time
        self.remaining_time = 0
        self.field_names = ['current_location', 'current_experience', 'current_date']
        self.write_date = []
        self.monsters = []
        self.monster = None
        self.locations = []
        self.current_location = ''
        self.exp_pattern = r'_exp\d+'
        self.time_pattern = r'_tm\d+'
        self.path_to_location = None
        self.current_json_file = None
        self.reply = None
        self.exit_from_dungeon = exit_from_dungeon
        self.game_over_reply = True
        self.reed_file()

    def reed_file(self):
        self.remaining_time = Decimal(self.time)
        self.next_location = 'Location_0_tm0'
        with open(self.json_file, 'r') as rpg_file:
            self.current_location = self.next_location
            self.current_json_file = json.load(rpg_file)
        self.path_to_location = self.current_json_file[self.current_location]
        self.run()

    def check_live(self):
        if self.remaining_time < 0:
            cprint(f'ваше время истекло {self.remaining_time}', 'red')
            self.game_over()

    def print_current_info1(self):
        current_dict = {
            'current_location': self.next_location,
            'current_experience': self.experience,
            'current_date': self.remaining_time,
        }
        cprint(f'Вы находитесь в {current_dict["current_location"]}\nУ вас {current_dict["current_experience"]}'
               f' опыта и осталось {current_dict["current_date"]} '
               f'секунд до наводнения, Прошло времени: 00:00', 'magenta')
        self.write_date.append(current_dict)

    def print_current_info2(self):
        cprint(f'\nВнутри вы видите:\n', 'red')
        self.locations = []
        self.monsters = []
        for elem in self.path_to_location:
            if isinstance(elem, dict):
                for key, value in elem.items():
                    if self.exit_from_dungeon in key:
                        pprint(f'ЗДЕСЬ ЕСТЬ ВЫХОД!! Вам необходимо 280 очков опыта, у вас есть {self.experience}')
                        cprint(f'-- Вход в локацию: {key}', 'green')
                        self.locations.append(key)
                    else:
                        cprint(f'-- Вход в локацию: {key}', 'green')
                        self.locations.append(key)
            elif isinstance(elem, str):
                cprint(f'-- Монстра: {elem}', 'blue')
                self.monsters.append(elem)
        if len(self.monsters) == 0 and len(self.locations) == 0:
            self.game_over()

    def user_input(self):
        doing_dict = {
            1: {'name': 'Атаковать монстра', 'func': self.attack_the_monster, 'len': len(self.monsters)},
            2: {'name': 'Перейти в другую локацию', 'func': self.choose_location, 'len': len(self.locations)},
            3: {'name': 'Сдаться и выйти из игры', 'func': self.game_over, 'len': 1}
        }
        cprint('\nВыберите действие:\n', 'red')
        for key, value in doing_dict.items():
            if value['len'] > 0:
                cprint(f'{key} -- {value["name"]}', 'grey')
        self.check_user_reply()
        for key, value in doing_dict.items():
            if key == self.reply:
                value['func']()

    def attack_the_monster(self):
        try:
            cprint('Введите номер монстра, с которым хотите сразиться', 'blue')
            for i, monster in enumerate(self.monsters):
                print(f'{i + 1} -- с монстром {self.monsters[i]}')
            self.check_user_reply()
            self.monster = self.monsters[self.reply - 1]
            delta_exp = re.search(self.exp_pattern, self.monster)
            delta_time = re.search(self.time_pattern, self.monster)
            self.experience += int(delta_exp.group()[4:])
            self.remaining_time -= int(delta_time.group()[3:])
            self.path_to_location.remove(self.monster)
        except IndexError:
            cprint('Здесь нет монстров', 'blue')

    def choose_location(self):
        try:
            print('Введите номер локации, в которую хотите перейти')
            for i, location in enumerate(self.locations):
                print(f'{i + 1} -- в локацию {self.locations[i]}')
            self.check_user_reply()
            self.next_location = self.locations[self.reply - 1]
            if self.exit_from_dungeon in self.next_location:
                if self.experience >= 280:
                    cprint('!!!You are winner!!!', 'red')
                    self.game_over()
                else:
                    cprint('Недостаточно очков для входа', 'red')
                    self.game_over()
            delta_time = re.search(self.time_pattern, self.next_location)
            self.remaining_time -= int(delta_time.group()[3:])
            for elem in self.path_to_location:
                if isinstance(elem, dict):
                    for key, value in elem.items():
                        if key == self.next_location:
                            self.path_to_location = value
        except IndexError:
            cprint('Нет входа в другую локацию', 'blue')

    def check_user_reply(self):
        self.reply = input()
        try:
            if self.reply.isdigit():
                self.reply = int(self.reply)
        except ValueError as exc:
            print(f'Введите ответ в виде цифры\n Error: {exc}')

    def write_file(self):
        with open('dungeon.csv', 'w') as out_detail_file:
            writer = csv.DictWriter(out_detail_file, fieldnames=self.field_names)
            writer.writeheader()
            writer.writerows(self.write_date)

    def game_over(self):
        self.write_file()
        cprint('GAME OVER\nWant to start over?\n Yes - enter 1\n', 'red')
        self.check_user_reply()
        while True:
            if self.reply != 1:
                self.game_over_reply = False
                break
            else:
                self.reed_file()

    def run(self):
        while self.game_over_reply:
            self.check_live()
            self.print_current_info1()
            self.print_current_info2()
            self.user_input()


if __name__ == "__main__":
    Dungeon()
