from math import ceil
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


""" Класс для выбора лучшего менеджера """
class Manager:
        def __init__(self, name, money):
            self.name = name
            self.money = money


""" Получение данных месяца из полной таблицы """
def iterate_over_dataframe(data, line1, line2):
    df = pd.DataFrame(data, columns=["client_id", "sum", "status", "sale", "new/current", "document", "receiving_date"])
    
    data_to_send = df.iloc[line1 + 1:line2]
    month_name = df.iloc[line1]

    return [month_name, data_to_send]


""" Получение данных из таблицы по месяцам """
def get_table_data_by_month(specific_month=None):

    data = pd.read_excel(r"data.xlsx")

    df1 = pd.DataFrame(data, columns=["client_id", "status"])

    idx, idy = np.where(pd.isnull(df1))
    month_rows = np.column_stack([df1.index[idx], df1.columns[idy]])

    previous_line = None
    months_dict = {}

    for line in month_rows:
        if previous_line is not None:
            data_received = iterate_over_dataframe(data, previous_line, line[0])
            months_dict.setdefault(data_received[0].iloc[2], data_received[1])
            
        previous_line = line[0]           

    data_received = iterate_over_dataframe(data, previous_line, -1)
    months_dict.setdefault(data_received[0].iloc[2], data_received[1])
    
    if specific_month is not None:
        month_to_send = months_dict.get(specific_month)
        return month_to_send
    else:
        return months_dict


""" Получение дохода за месяц """
def get_income_by_month(data):
    not_overdue = data.loc[data['status'] != "ПРОСРОЧЕНО"]
    result = ceil(not_overdue['sum'].sum()*100) / 100

    return result


""" Получение данных по продажам конкретного менеджера """
def get_data_by_manager(data, manager):
    not_overdue = data.loc[data['status'] == "ОПЛАЧЕНО"]
    sales_of_current_manager = not_overdue.loc[not_overdue['sale'] == manager]
    result = ceil(sales_of_current_manager['sum'].sum()*100) / 100

    return result


""" Выбор среди менеджеров лучшего (или лучших) """
def determine_best_manager(data):

    manager_names_list = data.sale.unique()
    manager_list = []

    for manager in manager_names_list:
        manager_list.append(Manager(manager, get_data_by_manager(data=data, manager=manager)))

    current_highest_sales = None

    for manager in manager_list:            
        if current_highest_sales is None:
            current_highest_sales = manager
        else:
            if isinstance(current_highest_sales, list):
                if current_highest_sales[0].money < manager.money:
                    current_highest_sales = manager
                elif current_highest_sales[0].money == manager.money:
                    current_highest_sales = [current_highest_sales, manager]
                else:
                    pass
            else:
                if current_highest_sales.money < manager.money:
                    current_highest_sales = manager
                elif current_highest_sales.money == manager.money:
                    current_highest_sales = [current_highest_sales, manager]
                else:
                    pass
    
    if isinstance(current_highest_sales, list):
        return current_highest_sales[0].name
    else:
        return current_highest_sales.name


""" Подсчёт количества сделок за период """
def count_deal_type_amount(data, deal):
    deals_of_this_type = data.loc[data["new/current"] == deal]
    result = deals_of_this_type[deals_of_this_type.columns[0]].count()

    return result


""" Подсчёт бонуса сотрудника за период """
def bonus_counter(data, name):
    data_received = data.loc[data["sale"] == name]

    new_deals = data_received.loc[data_received["new/current"] == "новая"]
    current_deals = data_received.loc[data_received["new/current"] == "текущая"]

    new_deal_sales = new_deals.loc[new_deals["status"] == "ОПЛАЧЕНО"]
    new_deal_sum = np.around(((new_deal_sales['sum'].sum()) / 100 * 7), decimals=2)

    current_deal_big_filter = current_deals.loc[current_deals["sum"] > 10000]
    current_deal_big_sum = np.around(((current_deal_big_filter['sum'].sum()) / 100 * 5), decimals=2)

    current_deal_small_filter = current_deals.loc[current_deals["sum"] <= 10000]
    current_deal_small_sum = np.around(((current_deal_small_filter['sum'].sum()) / 100 * 3), decimals=2)

    result = round((new_deal_sum.item() + current_deal_big_sum.item() + current_deal_small_sum.item()), 2)

    return result


""" Основная функция, принимает номера вопросов и слово Задача """
def get_required_data(task_name):
    if task_name == 1:
        """ Вопрос 1 """

        data_received = get_table_data_by_month(specific_month="Июль 2021")
        result = get_income_by_month(data_received)

        print(f"Вопрос 1: {result}")
    
    elif task_name == 2:
        """ Вопрос 2 """

        data_received = get_table_data_by_month()
        income_graph_data = []
        income_graph_names = []

        for month in data_received:
            income = get_income_by_month(data_received.get(month))

            income_graph_data.append(income)
            income_graph_names.append(month)

        plt.figure(figsize=(10,5))
        plt.plot(income_graph_names, income_graph_data)
        plt.savefig('graph.png')

        print("Вопрос 2: сохранён в файле graph.png")
    
    elif task_name == 3:
        """ Вопрос 3 """

        data_received = get_table_data_by_month(specific_month="Сентябрь 2021")
        result = determine_best_manager(data_received)

        print(f"Вопрос 3: {result}")
    
    elif task_name == 4:
        """ Вопрос 4 """

        data_received = get_table_data_by_month(specific_month="Октябрь 2021")

        new_count = count_deal_type_amount(data_received, "новая")
        current_count = count_deal_type_amount(data_received, "текущая")
        
        if new_count > current_count:
            result = "новая"
        elif new_count < current_count:
            result = "текущая"
        else:
            result = "преобладающего типа нет"
        
        print(f"Вопрос 4: {result}")
    
    elif task_name == 5:
        """ Вопрос 5 """

        data_received = get_table_data_by_month(specific_month="Июнь 2021")
        rows_with_original = data_received.loc[data_received['document'] == "оригинал"]
        result = rows_with_original[rows_with_original.columns[0]].count()

        print(f"Вопрос 5: {result}")    
    
    elif task_name == "Задание":
        """ Задание """

        data = pd.read_excel(r"data.xlsx")
        df = pd.DataFrame(data, columns=["client_id", "sum", "status", "sale", "new/current", "document", "receiving_date"])
        df = df[df["client_id"].notna()]

        manager_list = df.sale.unique()
        final_date = "01.07.2021"

        not_nan_data = df[df["receiving_date"].notna()]
        data_not_sale_filter = not_nan_data.loc[not_nan_data["receiving_date"] != "-"]
        data_filtered_dy_date = data_not_sale_filter.loc[data_not_sale_filter["receiving_date"] < datetime.strptime(final_date, '%d.%m.%Y')]
        data_filtered_dy_overdue = data_filtered_dy_date.loc[data_filtered_dy_date["status"] != "ПРОСРОЧЕНО"]
        data_filtered_dy_document = data_filtered_dy_overdue.loc[data_filtered_dy_overdue["document"] == "оригинал"]
        
        print("Задание:")

        for manager in manager_list:
            if manager == "-":
                pass
            else:
                pass
                bonus_amount = bonus_counter(data_filtered_dy_document, manager)
                print(f"{manager}. Баланс на {final_date}: {bonus_amount}")


if __name__ == "__main__":
    """ Отсюда берётся список заданий для исполнения. 1-5 вопрос и одно задание """
    tasks_list = [1, 2, 3, 4, 5, "Задание"]

    for task in tasks_list:
        get_required_data(task)
