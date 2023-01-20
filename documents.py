from config import *
from datetime import date
from matplotlib.ticker import PercentFormatter
from mysql import connector
from mysql.connector.cursor import MySQLCursor
from typing import Callable, Any
import matplotlib.pyplot as plt
import pandas as pd
import textwrap


class OlimpDatabase:
    """
    Класс содержит методы по подсоединению и работе с базой данных Olimp.
    """

    def __init__(self):
        self._conn = connector.connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DATABASE
                )
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self) -> connector.MySQLConnection:
        """
        Возвращает объект подсоединения к MySQL.
        :return: MySQLConnection
        """
        return self._conn

    @property
    def cursor(self) -> MySQLCursor:
        """
        Возвращает курсор.
        :return: MySQLCursor
        """
        return self._cursor

    def commit(self) -> None:
        """
        Производит commit.
        :return: None
        """
        self.connection.commit()

    def execute(self, sql: str, params: tuple | None = None) -> None:
        """
        Выполняет SQL-запрос.
        :param sql: str
        :param params: tuple | None = None
        :return: None
        """
        self.cursor.execute(sql, params or ())

    def fetchall(self) -> list:
        """
        Возвращает список полученных после запроса значений
        :return: list
        """
        return self.cursor.fetchall()

    def fetchone(self) -> Any | None:
        """
        Возвращает одно значение из запрошенных.
        :return: Any | None
        """
        return self.cursor.fetchone()

    def query(self, sql: str, params: tuple | None = None) -> list:
        """
        Выполняет запрос и возвращает список полученных значений.
        :param sql: str
        :param params: tuple | None = None
        :return: list
        """
        self.execute(sql, params or ())
        return self.fetchall()

    def close(self, commit: bool = True) -> None:
        """
        Производит commit перед прерыванием соединения с базой данных Olimp.
        :param commit: bool = True
        :return: None
        """
        if commit:
            self.commit()
        self.connection.close()


class DocumentHandler:
    """
    Класс, содержащий данные и методы по составлению документов для выполняемых программой задач.
    """

    staff_list_docs = [

            "Перечень документов, разработанных по отделам",
            "Справка о рабочем времени",
            "Справка о заработной плате",
            "Нормы времени составления документов"

    ]

    missing_unit_docs = [
            "Штатное расписание",
            "Справка о специалистах"
    ]

    pareto_docs = [
            "Приказ об увольнении",
            "Справка о причинах увольнения",
            "Анкета",

    ]

    @property
    def doc_func_dict(self) -> dict[str, Callable]:
        """
        Возвращает словарь, где ключами являются наименования документов, а значениями - методы по получению
        данных из базы.
        :return: dict[str, Callable]
        """
        func_list = [self.docs_in_struct_subdiv, self.work_time_info, self.salary_info,
                     self.time_norms_to_create_docs, self.staff_list, self.exist_spec,
                     self.order_of_dismissal, self.dismissal_info, self.questionnaire_form
                     ]
        doc_func_dict = dict(zip(self.staff_list_docs+self.missing_unit_docs+self.pareto_docs, func_list))
        doc_func_dict.update({"Форма справки о недостающих кадрах": self.missing_unit_info,
                              "Диаграмма Парето": self.pareto_data})
        return doc_func_dict

    @classmethod
    def docs_in_struct_subdiv(cls) -> tuple[tuple[str, ...], list[tuple[str, str, str, int, int]]]:
        """
        Возвращает данные для составления документа "Перечень документов, разработанных по отделам".
        :return: tuple[tuple[str, str, str, str, str], list[tuple[str, str, str, int, int]]]
        """
        headers = ("Наименование Отдела", "Должность", "Наименование документа", "Периодичность", "Количество")
        with OlimpDatabase() as db:
            result = db.query("""SELECT struct_subdivision, function_name, doc_name, period, number
                            FROM Func 
                            JOIN Document ON Func.id=Document.function_id
                            ORDER BY struct_subdivision, function_name;""")
            return headers, result

    @classmethod
    def time_norms_to_create_docs(cls) -> tuple[tuple[str, ...], list[tuple[str, str, str, str, float]]]:
        """
        Возвращает данные для составления документа "Нормы времени составления документов".
        :return: tuple[tuple[str, str, str, str, str], list[tuple[str, str, str, str, float]]]
        """
        headers = ("Наименование документа", "Отдел", "Исполнитель", "Единица измерения", "Норма врем, ч")
        with OlimpDatabase() as db:
            result = db.query("""
                            SELECT doc_name, struct_subdivision, function_name, "1 документ" as units, time
                            FROM Func 
                            JOIN Document ON Func.id=Document.function_id
                            ORDER BY doc_name;
                            """)
            return headers, result

    @classmethod
    def salary_info(cls) -> tuple[tuple[str, str], list[tuple[str, float]]]:
        """
        Возвращает данные для составления документа "Справка о заработной плате".
        :return: tuple[tuple[str, str], list[tuple[str, float]]]
        """
        headers = ("Должность", "Сумма, руб")
        with OlimpDatabase() as db:
            result = db.query("""
                            SELECT function_name, salary
                            FROM Func ;
                            """)
            return headers, result

    @classmethod
    def work_time_info(cls, year: str = str(date.today().year+1)) -> tuple[tuple[str, ...], list[tuple[int, int, int, int]]]:
        """
        Возвращает данные для составления документа "Справка о рабочем времени". Даёт возможность фильтровать по году.
        :param year: str
        :return: tuple[tuple[str, str, str, str], list[tuple[int, int, int, int]]]
        """
        headers = ("Год", "Количество рабочих часов в году", "Количество рабочих часов в сутки",
                   "Количество рабочих дней в году")
        with OlimpDatabase() as db:
            result = db.query("""
                            SELECT current_year, hour_year, hour_day, day_year
                            FROM work_time_info
                            WHERE current_year=%s;
                            """, (year,))
            return headers, result

    @classmethod
    def staff_list(cls, year: str = str(date.today().year+1)) -> tuple[tuple[str, ...], list[tuple[str, str, int, float]]]:
        """
        Возвращает данные для составления документа "Штатное расписание". Даёт возможность фильтровать по году.
        :param year: str
        :return: tuple[tuple[str, str, str, str], list[tuple[str, str, int, float]]]
        """
        headers = ("Структурное подразделение", "Должность", "Количество штатных единиц", "Тарифная ставка, руб")
        with OlimpDatabase() as db:
            db.execute(""" 
                            CREATE OR REPLACE VIEW Stuff_list AS
                            SELECT f.struct_subdivision, f.function_name, floor(ceil(sum(d.number * d.period * d.time) 
                            / wti.hour_year)) as number_of_spec, f.salary
                            FROM Func as f
                            JOIN Document as d ON f.id=d.function_id
                            JOIN Work_time_info as wti ON wti.current_year=%s
                            GROUP BY f.function_name
                            ORDER BY f.function_name;
                            """, (year,))
            result = db.query("""SELECT struct_subdivision, function_name, cast(number_of_spec AS SIGNED) as number_of_spec, 
                            salary FROM Stuff_list;""")
            return headers, result

    @classmethod
    def exist_spec(cls) -> tuple[tuple[str, ...], list[tuple[str, str, int]]]:
        """
        Возвращает данные для составления документа "Справка о специалистах".
        :return: tuple[tuple[str, str, str], list[tuple[str, str, int]]]
        """
        headers = ("Структурное подразделение", "Должность", "Количество")
        with OlimpDatabase() as db:
            db.execute("""CREATE OR REPLACE VIEW Exist_spec AS
                            SELECT f.struct_subdivision, f.function_name, count(sp.id) as number_of_exist_spec
                            FROM Func as f 
                            JOIN Specialist as sp ON f.id=sp.function_id
                            WHERE sp.end_date IS NULL
                            GROUP BY f.function_name;""")
            result = db.query("""SELECT * FROM Exist_spec;""")
            return headers, result

    @classmethod
    def missing_unit_info(cls) -> tuple[tuple[str, ...], list[tuple[str, str, int, int, int]]]:
        """
        Возвращает данные для составления документа "Форма справки о недостающих кадрах".
        :return: tuple[tuple[str, str, str, str, str], list[tuple[str, str, int, int, int]]]
        """
        headers = ("Структурное подразделение",	"Должность", "Плановое количество", "Фактическое количество",
                   "Отклонение")
        with OlimpDatabase() as db:
            db.execute("""CREATE OR REPLACE VIEW Missing_unit_info AS
                            SELECT sl.struct_subdivision, sl.function_name, sl.number_of_spec, es.number_of_exist_spec, 
                            (sl.number_of_spec - es.number_of_exist_spec) AS deviation
                            FROM Stuff_list as sl
                            JOIN Exist_spec as es ON sl.function_name=es.function_name""")
            result = db.query("""SELECT struct_subdivision, function_name, cast(number_of_spec as signed), 
                            number_of_exist_spec, cast(deviation as signed) FROM Missing_unit_info""")
            return headers, result

    @classmethod
    def order_of_dismissal(cls) -> tuple[tuple[str, ...], list[tuple[int, date, str, str]]]:
        """
        Возвращает данные для составления документа "Приказ об увольнении".
        :return: tuple[tuple[str, str, str, str], list[tuple[int, date, str, str]]]
        """
        headers = ("Номер приказа", "Дата", "ФИО", "Причина")
        with OlimpDatabase() as db:
            result = db.query("""
                            SELECT ood.order_id, ood.order_date, sp.spec_name, di.short_reason as reason
                            FROM Order_of_dismissal as ood
                            JOIN Specialist as sp ON sp.id=ood.spec_id
                            JOIN Dismissal_info as di ON ood.reas_id=di.id
                            ORDER BY ood.order_date; 
                            """)
            return headers, result

    @classmethod
    def dismissal_info(cls) -> tuple[tuple[str, ...], list[tuple[int, str, str]]]:
        """
        Возвращает данные для составления документ "Справка о причинах увольнения".
        :return: tuple[tuple[str, str, str], list[tuple[int, str, str]]]
        """
        headers = ("Код причины", "Причина", "Расшифровка")
        with OlimpDatabase() as db:
            result = db.query("""
                            SELECT reason_id, short_reason, full_reason
                            FROM Dismissal_info; 
                            """)
            return headers, result

    @classmethod
    def questionnaire_form(cls, year: str = "2000") -> tuple[tuple[str, ...], list[tuple[str, ...]]]:
        """
        Возвращает данные для составления документа "Анкета".
        :param year: str
        :return: tuple[tuple[str, str, str, str], list[tuple[str, str, str, str]]]
        """
        headers = ("Структурное подразделение", "Должность", "ФИО",	"Причина")
        with OlimpDatabase() as db:
            result = db.query("""
                            SELECT f.struct_subdivision, f.function_name, sp.spec_name, ood.true_reason
                            FROM Func as f
                            JOIN Specialist as sp ON f.id=sp.function_id
                            JOIN Order_of_dismissal as ood ON sp.id=ood.spec_id
                            JOIN Dismissal_info as di ON ood.reas_id=di.id
                            WHERE ood.true_reason!='' AND YEAR(ood.order_date)>=%s;
                            """, (year,))
            return headers, result

    @classmethod
    def pareto_data(cls, year: str = "2015") -> tuple[tuple[str, ...], list[tuple[str, int]]]:
        """
        Возвращает данные для составления диаграммы Парето. Есть возможность фильтровать по году.
        :param year: str
        :return: tuple[tuple[str, ...], list[str]]
        """
        headers = ("Наименование причины", "Количество, шт.")
        with OlimpDatabase() as db:
            result = db.query("""
                            SELECT q.reason, COUNT(q.reason) as reason_count FROM 
                            (SELECT IF(di.reason_id=3, ood.true_reason, di.full_reason) as reason
                            FROM Func as f
                            JOIN Specialist as sp ON f.id=sp.function_id
                            JOIN Order_of_dismissal as ood ON sp.id=ood.spec_id
                            JOIN Dismissal_info as di ON ood.reas_id=di.id
                            WHERE YEAR(sp.end_date)>=%s) as q
                            GROUP BY q.reason
                            ORDER BY reason_count DESC; 
                            """, (year,))
            return headers, result

    @classmethod
    def create_pareto_diagram(cls, year: str = "2015") -> None:
        """
        Создаёт графическое изображение диаграммы Парето с помощью Matplotlib. Есть возможность фильтровать по году.
        :param year: str
        :return: None
        """
        _, pareto_data = cls.pareto_data(year)
        pd_data = pd.DataFrame(pareto_data)
        pd_data.set_axis(["index", "count"], axis='columns', inplace=True)
        pd_data["perc"] = round(pd_data["count"]/pd_data["count"].sum()*100, 2)
        pd_data["cumperc"] = round(pd_data["count"].cumsum()/pd_data["count"].sum()*100, 2)

        color1 = "steelblue"
        color2 = "red"
        line_size = 4

        fig, ax = plt.subplots()
        ax.bar(pd_data["index"], pd_data["perc"], color=color1)
        ax.set_ylim(bottom=0, top=100)
        ax.yaxis.set_major_formatter(PercentFormatter())
        ax2 = ax.twinx()
        ax2.plot(pd_data["index"], pd_data["cumperc"], color=color2, marker="D", ms=line_size)
        ax2.set_ylim(bottom=0)
        ax2.yaxis.set_major_formatter(PercentFormatter())
        ax.tick_params(axis="y", color=color1)
        ax2.tick_params(axis="y", color=color2)
        ax.tick_params(axis="x", labelsize=6)
        labels = []
        for label in ax.get_xticklabels():
            text = label.get_text()
            labels.append(textwrap.fill(text, width=10,
                                        break_long_words=False))
        ax.set_xticklabels(labels, rotation=45)
        plt.title("Диаграмма Парето")
        fig.set_tight_layout(True)
        plt.show()
        return


class DataHandler:
    """
    Класс содержит данные и методы по работе с редактируемыми данными.
    """

    names = ("Структурные подразделения", "Документы", "Сотрудники", "Приказ об увольнении",
            "Расшифровка причин увольнения", "Данные о рабочем времени")

    @property
    def data_list(self) -> dict[str, type]:
        """
        Возвращает словарь, где ключами являются наименования таблиц с редактируемыми данными, а значениями -
        классы, содержащие данные и методы по работе с этими таблицами.
        :return: dict[str, type]
        """
        objects = (Subdivision, Documents, Units, DismissalOrder, DismissalInfo, TimeInfo)
        data = dict(zip(self.names, objects))
        return data


class Subdivision:
    """
    Класс, содержащий данные и методы по работе с таблицей "Структурные подразделения".
    """

    headers = ("Код должности", "Наименование должности", "Отдел", "Заработная плата, руб")

    @classmethod
    def show(cls) -> tuple[tuple[str, ...], list[tuple[int, str, str, float, int, float]]]:
        """
        Возвращает данные для заполнения таблицы "Структурные подразделения".
        :return: tuple[tuple[str, str, str, str, str, str], list[tuple[int, str, str, float, int, float]]]]
        """
        with OlimpDatabase() as db:
            result = db.query("""
            SELECT function_id, function_name, struct_subdivision, salary FROM Func;
            """)
            return cls.headers, result

    @classmethod
    def add_data(cls, f_id: str, f_name: str, st_sub: str, sal: str) -> None:
        """
        Добавляет переданные из диалогового окна значения в таблицу Func базы данных.
        :param f_id: str
        :param f_name: str
        :param st_sub: str
        :param sal: str
        :return: None
        """
        with OlimpDatabase() as db:
            db.execute("""
            INSERT INTO Func(function_id, function_name, struct_subdivision, salary)
            VALUES(%s, %s, %s, %s);
            """, (f_id, f_name, st_sub, sal))

    @classmethod
    def edit_data(cls, f_id: str, f_name: str, st_sub: str, sal: str, old_f_id: str) -> None:
        """
        Обновляет выделенную строку в таблице Func базы данных с помощью переданных из диалогового окна значений.
        :param f_id: str
        :param f_name: str
        :param st_sub: str
        :param sal: str
        :param old_f_id: str
        :return: None
        """
        with OlimpDatabase() as db:
            db.execute("""
            UPDATE Func
            SET function_id=%s, function_name=%s, struct_subdivision=%s, salary=%s
            WHERE function_id=%s
            """, (f_id, f_name, st_sub, sal, old_f_id))

    @classmethod
    def del_data(cls, f_id: str) -> None:
        """
        Удаляет выделенную строку из таблицы Func базы данных.
        :param f_id: str
        :return: None
        """
        with OlimpDatabase() as db:
            db.execute("""
            DELETE FROM Func WHERE function_id=%s;
            """, (f_id,))


class Documents:
    """
    Класс, содержащий данные и методы по работе с таблицей "Документы".
    """

    headers = ("Код документа", "Наименование документа", "Должность", "Время, ч", "Количество, шт.",
               "Периодичность шт./год")

    @classmethod
    def show(cls) -> tuple[tuple[str, ...], list[tuple[int, str, str, float, int]]]:
        """
        Возвращает данные для заполнения таблицы "Документы".
        :return: tuple[tuple[str, str, str, str, str], list[tuple[int, str, str, float, int]]]
        """
        with OlimpDatabase() as db:
            result = db.query("""
                SELECT d.doc_id, d.doc_name, f.function_name, d.time, d.number, d.period 
                FROM Func as f
                JOIN Document as d ON f.id=d.function_id
                ORDER BY f.function_name;
                """)
            return cls.headers, result

    @classmethod
    def add_data(cls, doc_id: str, doc_name: str, func_name: str, num: str, period: str, time: str) -> None:
        """
        Добавляет переданные из диалогового окна значения в таблицу Document базы данных.
        :param doc_id: str
        :param doc_name: str
        :param func_name: str
        :param num: str
        :param period: str
        :param time: str
        :return: None
        """
        with OlimpDatabase() as db:
            db.execute("""
                INSERT INTO Document(doc_id, doc_name, number, period, time, function_id)
                SELECT %s as doc_id, %s as doc_name, %s as number, %s as period, %s as time, f.id as function_id
                FROM Func as f LEFT JOIN Document as d ON d.function_id=f.id
                WHERE f.function_name=%s
                GROUP BY f.id;
            """, (doc_id, doc_name, num, period, time, func_name))

    @classmethod
    def edit_data(cls, doc_id: str, doc_name: str, func_name: str, num: str, period: str, time: str, old_doc_id: str) -> None:
        """
        Обновляет выделенную строку в таблице Document базы данных с помощью переданных из диалогового окна значений.
        :param doc_id: str
        :param doc_name: str
        :param func_name: str
        :param num: str
        :param period: str
        :param time: str
        :param old_doc_id: str
        :return: None
        """
        with OlimpDatabase() as db:
            print(func_name)
            f_id = db.query("""
                SELECT id FROM Func WHERE function_name=%s;        
            """, (func_name,))[0][0]
            print(f_id)
            db.execute("""
                UPDATE Document 
                SET doc_id=%s, doc_name=%s, number=%s, period=%s, time=%s, function_id=%s
                WHERE doc_id=%s
            """, (doc_id, doc_name, num, period, time, f_id, old_doc_id))

    @classmethod
    def del_data(cls, doc_id: str) -> None:
        """
        Удаляет выделенную строку из таблицы Document базы данных.
        :param doc_id: str
        :return: None
        """
        with OlimpDatabase() as db:
            db.execute("""
                DELETE FROM Document WHERE doc_id=%s;
            """, (doc_id,))


class Units:
    """
    Класс, содержащий данные и методы по работе с таблицей "Сотрудники".
    """

    headers = ("Код специалиста", "ФИО", "Дата рождения", "Должность", "Дата вступления в должность", "Дата увольнения")

    @classmethod
    def show(cls) -> tuple[tuple[str, ...], list[tuple[int, str, date, str, date, date]]]:
        """
        Возвращает данные для заполнения таблицы "Сотрудники".
        :return: tuple[tuple[str, str, str, str, str, str], list[tuple[int, str, date, str, date, date]]]
        """
        with OlimpDatabase() as db:
            result = db.query("""
                SELECT sp.spec_id, sp.spec_name, sp.birthday, f.function_name, sp.start_date, sp.end_date
                FROM Func as f
                JOIN Specialist as sp ON f.id=sp.function_id
                ORDER BY sp.start_date;
                """)
            return cls.headers, result

    @classmethod
    def add_data(cls, spec_id: str, spec_name: str, birthday: str, function_name: str, start_date: str) -> None:
        """
        Добавляет переданные из диалогового окна значения в таблицу Specialist базы данных.
        :param spec_id: str
        :param spec_name: str
        :param birthday: str
        :param function_name: str
        :param start_date: str
        :return: None
        """
        with OlimpDatabase() as db:
            f_id = db.query("""SELECT id FROM Func WHERE function_name=%s;""", (function_name,))[0][0]
            db.execute("""
            INSERT INTO Specialist(spec_id, spec_name, birthday, start_date, function_id)
            VALUES(%s, %s, %s, %s, %s)
            """, (spec_id, spec_name, birthday, start_date, f_id))

    @classmethod
    def edit_data(cls, spec_id: str, spec_name: str, birthday: str, function_name: str, start_date: str, end_date: str, old_spec_id: str) -> None:
        """
        Обновляет выделенную строку в таблице Specialist базы данных с помощью переданных из диалогового окна значений.
        :param spec_id: str
        :param spec_name: str
        :param birthday: str
        :param function_name: str
        :param start_date: str
        :param end_date: str
        :param old_spec_id: str
        :return: None
        """
        if end_date == '':
            end_date = None
        with OlimpDatabase() as db:
            f_id = db.query("""SELECT id FROM Func WHERE function_name=%s;""", (function_name,))[0][0]
            db.execute("""
            UPDATE Specialist
            SET spec_id=%s, spec_name=%s, birthday=%s, start_date=%s, end_date=%s, function_id=%s
            WHERE spec_id=%s
            """, (spec_id, spec_name, birthday, start_date, end_date, f_id, old_spec_id))

    @classmethod
    def del_data(cls, spec_id: str) -> None:
        """
        Удаляет выделенную строку из таблицы Specialist базы данных.
        :param spec_id: str
        :return: None
        """
        with OlimpDatabase() as db:
            db.execute("""
            DELETE FROM Specialist
            WHERE spec_id=%s;
            """, (spec_id,))


class DismissalOrder:
    """
    Класс, содержащий данные и методы по работе с таблицей "Приказ об увольнении".
    """

    headers = ("Номер приказа", "Дата приказа", "ФИО специалиста", "Причина увольнения",
               "Настоящая причина увольнения")

    @classmethod
    def show(cls) -> tuple[tuple[str, ...], list[int, date, str, str, str]]:
        """
        Возвращает данные для заполнения таблицы "Приказ об увольнении".
        :return: tuple[tuple[str, str, str, str, str], list[int, date, str, str, str]]
        """
        with OlimpDatabase() as db:
            result = db.query("""
                SELECT ood.order_id, ood.order_date, sp.spec_name, di.short_reason, ood.true_reason 
                FROM Order_of_dismissal as ood
                JOIN Specialist as sp ON ood.spec_id=sp.id
                JOIN Dismissal_info as di ON ood.reas_id=di.id
                ORDER BY ood.order_date;
                """)
            return cls.headers, result

    @classmethod
    def add_data(cls, order_id: str, order_date: str, spec_name: str, short_reason: str, true_reason: str) -> None:
        """
        Добавляет переданные из диалогового окна значения в таблицу Order_of_dismissal базы данных.
        :param order_id: str
        :param order_date: str
        :param spec_name: str
        :param short_reason: str
        :param true_reason: str
        :return: None
        """
        with OlimpDatabase() as db:
            r_id = db.query("""
            SELECT id FROM Dismissal_info WHERE short_reason=%s;
            """, (short_reason,))[0][0]
            sp_id = db.query("""
            SELECT id FROM Specialist WHERE spec_name=%s;
            """, (spec_name,))[0][0]
            db.execute("""
            INSERT INTO Order_of_dismissal(order_id, order_date, true_reason, reas_id, spec_id)
            VALUES(%s, %s, %s, %s, %s)
            """, (order_id, order_date, true_reason, r_id, sp_id))

    @classmethod
    def edit_data(cls, order_id: str, order_date: str, spec_name: str, short_reason: str, true_reason: str, old_order_id: str) -> None:
        """
        Обновляет выделенную строку в таблице Order_of_dismissal базы данных с помощью переданных из диалогового окна значений.
        :param order_id: str
        :param order_date: str
        :param spec_name: str
        :param short_reason: str
        :param true_reason: str
        :param old_order_id: str
        :return: None
        """
        with OlimpDatabase() as db:
            r_id = db.query("""
                        SELECT id FROM Dismissal_info WHERE short_reason=%s;
                        """, (short_reason,))[0][0]
            sp_id = db.query("""
                        SELECT id FROM Specialist WHERE spec_name=%s;
                        """, (spec_name,))[0][0]
            db.execute("""
            UPDATE Order_of_dismissal
            SET order_id=%s, order_date=%s, true_reason=%s, reas_id=%s, spec_id=%s
            WHERE order_id=%s;
            """, (order_id, order_date, true_reason, r_id, sp_id, old_order_id))

    @classmethod
    def del_data(cls, order_id: str) -> None:
        """
        Удаляет выделенную строку из таблицы Order_of_dismissal базы данных.
        :param order_id: str
        :return: None
        """
        with OlimpDatabase() as db:
            db.execute("""
            DELETE FROM Order_of_dismissal
            WHERE order_id=%s
            """, (order_id,))


class DismissalInfo:
    """
    Класс, содержащий данные и методы по работе с таблицей "Расшифровка причин увольнения".
    """

    headers = ("Код причины", "Причина", "Полная запись")

    @classmethod
    def show(cls) -> tuple[tuple[str, ...], list[tuple[int, str, str]]]:
        """
        Возвращает данные для заполнения таблицы "Расшифровка причин увольнения".
        :return: tuple[tuple[str, str, str], list[tuple[int, str, str]]]
        """
        with OlimpDatabase() as db:
            result = db.query("""
                SELECT reason_id, short_reason, full_reason FROM Dismissal_info;
                """)
            return cls.headers, result

    @classmethod
    def add_data(cls, reas_id: str, sh_reas: str, full_reas: str) -> None:
        """
        Добавляет переданные из диалогового окна значения в таблицу Dismissal_info базы данных.
        :param reas_id: str
        :param sh_reas: str
        :param full_reas: str
        :return: None
        """
        with OlimpDatabase() as db:
            db.execute("""
            INSERT INTO Dismissal_info(reason_id, short_reason, full_reason)
            VALUES(%s, %s, %s)
            """, (reas_id, sh_reas, full_reas))

    @classmethod
    def edit_data(cls, reas_id: str, sh_reas: str, full_reas: str, old_reas_id: str) -> None:
        """
        Обновляет выделенную строку в таблице Dismissal_info базы данных с помощью переданных из диалогового окна значений.
        :param reas_id: str
        :param sh_reas: str
        :param full_reas: str
        :param old_reas_id: str
        :return: None
        """
        with OlimpDatabase() as db:
            db.execute("""
            UPDATE Dismissal_info
            SET reason_id=%s, short_reason=%s, full_reason=%s
            WHERE reason_id=%s
            """, (reas_id, sh_reas, full_reas, old_reas_id))

    @classmethod
    def del_data(cls, reas_id: str) -> None:
        """
        Удаляет выделенную строку из таблицы Dismissal_info базы данных.
        :param reas_id: str
        :return: None
        """
        with OlimpDatabase() as db:
            db.execute("""
            DELETE FROM Dismissal_info
            WHERE reason_id=%s
            """, (reas_id,))


class TimeInfo:
    """
    Класс, содержащий данные и методы по работе с таблицей "Данные о рабочем времени".
    """

    headers = ("Год", "Количество рабочих часов в году", "Количество рабочих часов в сутки",
               "Количество рабочих дней в году")

    @classmethod
    def show(cls) -> tuple[tuple[str, ...], list[tuple[int, int, int, int]]]:
        """
        Возвращает данные для заполнения таблицы "Данные о рабочем времени".
        :return: tuple[tuple[str, str, str, str], list[tuple[int, int, int, int]]]
        """
        with OlimpDatabase() as db:
            result = db.query("""
                SELECT current_year, hour_year, hour_day, day_year FROM Work_time_info;
                """)
            return cls.headers, result

    @classmethod
    def add_data(cls, cur_year: str, hy: str, hd: str, dy: str) -> None:
        """
        Добавляет переданные из диалогового окна значения в таблицу Work_time_info базы данных.
        :param cur_year: str
        :param hy: str
        :param hd: str
        :param dy: str
        :return: None
        """
        with OlimpDatabase() as db:
            db.execute("""
                INSERT INTO Work_time_info(current_year, hour_year, hour_day, day_year)
                VALUES(%s, %s, %s, %s);
            """, (cur_year, hy, hd, dy))

    @classmethod
    def edit_data(cls, cur_year: str, hy: str, hd: str, dy: str, old_cur_year: str) -> None:
        """
        Обновляет выделенную строку в таблице Work_time_info базы данных с помощью переданных из диалогового окна значений.
        :param cur_year: str
        :param hy: str
        :param hd: str
        :param dy: str
        :param old_cur_year: str
        :return: None
        """
        with OlimpDatabase() as db:
            db.execute("""
                UPDATE Work_time_info
                SET current_year=%s, hour_year=%s, hour_day=%s, day_year=%s
                WHERE current_year=%s;
            """, (cur_year, hy, hd, dy, old_cur_year))

    @classmethod
    def del_data(cls, cur_year: str) -> None:
        """
        Удаляет выделенную строку из таблицы Work_time_info базы данных.
        :param cur_year: str
        :return: None
        """
        with OlimpDatabase() as db:
            db.execute("""
                DELETE FROM Work_time_info WHERE current_year=%s;
            """, (cur_year,))


if __name__ == "__main__":
    ...
