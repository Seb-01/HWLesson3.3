# Написать декоратор - логгер. Он записывает в файл дату
# и время вызова функции, имя функции, аргументы, с которыми вызвалась и возвращаемое значение

"""
Чтобы создать описание функции, внутри функции перед её телом нужно сделать многострочный комментарий
(делается он с помощью трёх знаков ''').
Этот комментарий будет рассматриваться, как аттрибут .__doc__ и будет появляться при вызове help()
"""
import datetime
from pprint import pprint
import csv
import os

#Это для регулярных выражений
from pprint import pprint
import csv
import re


# функция для приведения в порядок записной книжки
def contact_normalizer():
    # читаем адресную книгу в формате CSV в список contacts_list
    with open("phonebook_raw.csv", encoding='utf-8') as f:
        rows = csv.reader(f, delimiter=",")
        contacts_list = list(rows)

    #наводим порядок с ФИО. Задача 1
    phone_dict=[]
    for part in contacts_list:
        #словарь готовим
        phone_row=dict()
        #что лежит в lastname
        fio=part[0].split(' ')
        if len(fio) == 3:
            #фамилия имя отчество
            phone_row['lastname']=fio[0]
            phone_row['firstname'] = fio[1]
            phone_row['surname'] = fio[2]

        elif len(fio) == 2:
            #фамилия имя, , отчество
            phone_row['lastname']=fio[0]
            phone_row['firstname'] = fio[1]
            phone_row['surname'] = part[2]

        else:
            #Вариант 1: фамилия, имя, отчетство
            #Вариант 2: фамилия, имя отчетство,
            phone_row['lastname']=fio[0]

            io = part[1].split(' ')
            if len(io) == 2:
                #Вариант 2: фамилия, имя отчетство,
                phone_row['firstname'] = io[0]
                phone_row['surname'] = io[1]
            else:
                #Вариант 1: фамилия, имя, отчетство
                phone_row['firstname'] = part[1]
                phone_row['surname'] = part[2]

        #остальные поля
        phone_row['organization'] = part[3]
        phone_row['position'] = part[4]
        phone_row['phone'] = part[5]
        phone_row['email'] = part[6]

        phone_dict.append(phone_row)

    pprint(phone_dict)

    #Обогощаем записи и удаляем дубли. Задача 3:
    for num1, frecord in enumerate(phone_dict):
        for num2, srecord in enumerate(phone_dict):
            if (frecord['lastname']==srecord['lastname']) or (frecord['firstname']==srecord['firstname']):
                if num1 != num2:
                    #нашли дубль!
                    print(f"Нашли дубль {frecord['lastname']} и {srecord['lastname']}")
                    #работаем:
                    dict_merge_empty2(frecord,srecord)
                    #убираем дубль
                    phone_dict.remove(srecord)

    #приводим все телефоны в формат +7(999)999-99-99. Задача 2
    #мой шаблон: https://regex101.com/r/IfID3s/4
    # (\s*\+*[7,8]\s*)(\(*(\d{3})\)*)(\s*-*(\d{3})\s*-*)(\s*(\d{2})\s*-*)(\s*\d{2})(\s*)(\(*)((доб.)?)(\s*)((\d{4})*)(\)*)

    pattern = r"(\s*\+*[7,8]\s*)(\(*(\d{3})\)*)(\s*-*(\d{3})\s*-*)(\s*(\d{2})\s*-*)(\s*\d{2})(\s*)(\(*)((доб.)?)(\s*)((\d{4})*)(\)*)"
    regex = re.compile(pattern)

    #идем по всем записям, кроме первой = названия полей
    for i, part in enumerate(phone_dict):
        if i == 0:
            continue
        #телефон
        text=part['phone']
        # проверка на "доб."
        if text.find('доб.') != -1:
            text2 = regex.sub(r"+7(\3)\5-\7-\8 доб.\15", text)
        else:
            text2 = regex.sub(r"+7(\3)\5-\7-\8", text)

        print(text2)
        part['phone']=text2

    pprint(phone_dict)

    # записываем результат в файл в формате CSV
    """
    Избавляемся от лишних строк при выводе в файл:
    В Python 2 откройте outfile с режимом 'wb' вместо 'w'. csv.writer записывает \r\n в файл напрямую. 
    Если вы не откроете файл в режиме binary , он напишет \r\r\n, потому что в режиме Windows текст переводит каждый \n в \r\n.
    В Python 3 был изменен требуемый синтаксис, поэтому откройте outfile с дополнительным параметром newline=''.
    """
    with open("phonebook.csv", "w", encoding='utf-8', newline='') as f:
        #Второй параметр в DictWriter определяет последовательность ключей, которые определяют порядок,
        #в котором значения в словаре записываются в файл CSV
        datawriter = csv.DictWriter(f,phone_dict[0])
        datawriter.writerows(phone_dict)

#декоратор
def param_logger(log_folder):

    # счетчик вызова логгера
    count = 0

    def my_logger2(old_func):

        def wrapped_func(*args, **kwargs):

            # счетчик вызова логгера
            nonlocal count

            # словарь со статистикой
            header_stat = dict()
            header_stat['rec_num'] = 'Номер записи'
            header_stat['call_time'] = 'Дата/время вызова'
            header_stat['func_name'] = 'Имя функции'
            header_stat['return_value'] = 'Возвращаемое значение'
            header_stat['args'] = 'Позиционные аргументы'
            header_stat['kwargs'] = 'Именованные аргументы'

            func_stat = dict()
            func_stat['rec_num'] = count + 1
            func_stat['call_time']=str(datetime.datetime.now())
            func_stat['func_name']=old_func.__name__
            func_stat['return_value'] = old_func(*args, **kwargs)
            func_stat['args']=args
            func_stat['kwargs'] = kwargs

            pprint(func_stat)

            #создаем в текущем рабочем каталоге папку log_folder
            if not os.path.exists(os.getcwd() + '\\' + log_folder):
                #если не существует
                folder=os.mkdir(log_folder)
            #полный путь к файлу:
            log_path=os.getcwd() + '\\' + log_folder + '\\' + 'mylog.csv'

            with open(log_path, "a", encoding='utf-8', newline='') as f:
                # Второй параметр в DictWriter определяет последовательность ключей, которые определяют порядок,
                # в котором значения в словаре записываются в файл CSV
                #keys=list(func_stat.keys())
                #print(keys)

                logwriter = csv.DictWriter(f,header_stat)
                if count == 0:
                    logwriter.writerow(header_stat)
                logwriter.writerow(func_stat)

            count+=1

            return (func_stat['return_value'])
        return wrapped_func
    return my_logger2

#вызов декоратора
@param_logger('logs')
# "сливает" два словаря, обогощая поля друг друга
def dict_merge_empty2(dict1, dict2):
    #список ключей
    keys1=list(dict1.keys())
    #идем по всем ключам
    for key in keys1:
        if dict1[key] != '':
            continue
        else:
            if dict2[key] != '':
                #пустое поле заполняем информацией из второго словаря при ее наличии
                dict1[key]=dict2[key]
            else:
                continue

# главная функция
def main():
    contact_normalizer()

if __name__=="__main__":
    main()


