from abc import ABC
from datetime import datetime
import traceback
from PyQt5 import QtWidgets as qtw, QtCore as qtc, QtGui as qtg
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog
from documents import DocumentHandler, DataHandler, Subdivision, Documents, Units, DismissalOrder, DismissalInfo, TimeInfo
import sys
import pandas as pd


class MainWindow(qtw.QMainWindow):
    """
    Класс описывает создание и функционирование основного интерфейса программы.
    """

    sort_year_signal = qtc.pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.sorted_year = None
        self.setMinimumSize(800, 600)

        # Создание меню.
        self.menu_bar = qtw.QMenuBar()
        self.file_menu = self.menu_bar.addMenu("Файл")
        self.open_action = self.file_menu.addAction("Открыть")
        self.save_as_pdf_action = self.file_menu.addAction("Сохранить как PDF")
        self.save_as_xlsx_action = self.file_menu.addAction("Сохранить как XLSX")
        self.file_menu.addSeparator()
        self.exit_action = self.file_menu.addAction("Закрыть")
        self.exit_action.setShortcut("Ctrl+Q")
        self.edit_menu = self.menu_bar.addMenu("Правка")
        self.add_row = self.edit_menu.addAction("Добавить строку")
        self.del_row = self.edit_menu.addAction("Удалить строку")
        self.view_menu = self.menu_bar.addMenu("Вид")
        self.documents_view = self.view_menu.addAction("Список документов")
        self.documents_view.setCheckable(True)
        self.documents_view.setChecked(True)
        self.help_menu = self.menu_bar.addMenu("Справка")
        self.help = self.help_menu.addAction("Помощь")

        # Присоединение сигналов для пунктов меню.
        self.exit_action.triggered.connect(self.close)
        self.documents_view.triggered.connect(self.show_document_list)
        self.save_as_pdf_action.triggered.connect(self.save_pdf)
        self.save_as_xlsx_action.triggered.connect(self.save_xlsx)
        self.add_row.triggered.connect(self.add_new_data)
        self.del_row.triggered.connect(self.del_cur_row)

        # Создание центральной части интерфейса.
        self.main_screen = qtw.QWidget()
        self.setCentralWidget(self.main_screen)
        self.layout = qtw.QVBoxLayout()
        self.main_screen.setLayout(self.layout)
        self.title_label = qtw.QLabel("Choose your destiny!")
        self.table = qtw.QTableWidget()
        self.create_pareto_diagram_button = qtw.QPushButton("Построить диаграмму")
        self.create_pareto_diagram_button.setFixedWidth(200)
        self.sort_year_widget = qtw.QWidget()
        self.sort_year_widget.setLayout(qtw.QHBoxLayout())
        self.sort_year_label = qtw.QLabel("Введите год для сортировки данных: ")
        self.sort_year_line = qtw.QLineEdit()
        self.sort_year_button = qtw.QPushButton("Сортировать")
        self.sort_year_widget.layout().addWidget(self.sort_year_label)
        self.sort_year_widget.layout().addWidget(self.sort_year_line)
        self.sort_year_widget.layout().addWidget(self.sort_year_button)
        self.sort_year_widget.setHidden(True)
        self.sort_year_button.setEnabled(False)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.sort_year_widget)
        self.layout.addWidget(self.create_pareto_diagram_button)
        self.layout.setAlignment(qtc.Qt.AlignCenter)
        self.create_pareto_diagram_button.setHidden(True)

        # Создание бокового окна, содержащего списки документов.
        self.docs_dock = MyDockWidget()
        self.dock_widget = qtw.QWidget()
        self.dock_layout = qtw.QVBoxLayout()
        self.data_widget = DataManagingWidget()
        self.docs_widget = DocumentWidget()
        self.dock_layout.addWidget(self.data_widget)
        self.dock_layout.addWidget(self.docs_widget)
        self.dock_widget.setLayout(self.dock_layout)
        self.docs_dock.setWidget(self.dock_widget)
        self.addDockWidget(qtc.Qt.LeftDockWidgetArea, self.docs_dock)

        self.data_manage_button_widget = qtw.QWidget()
        self.data_manage_button_widget.setLayout(qtw.QHBoxLayout())
        self.refresh_data_button = qtw.QPushButton("Обновить")
        self.refresh_data_button.clicked.connect(self.refresh_data_in_table)
        self.add_new_data_button = qtw.QPushButton("Добавить")
        self.add_new_data_button.clicked.connect(self.add_new_data)
        self.edit_row_button = qtw.QPushButton("Редактировать")
        self.edit_row_button.clicked.connect(self.edit_cur_row)
        self.del_row_button = qtw.QPushButton("Удалить")
        self.del_row_button.clicked.connect(self.del_cur_row)
        self.data_manage_button_widget.layout().addWidget(self.refresh_data_button)
        self.data_manage_button_widget.layout().addWidget(self.add_new_data_button)
        self.data_manage_button_widget.layout().addWidget(self.edit_row_button)
        self.data_manage_button_widget.layout().addWidget(self.del_row_button)
        self.layout.addWidget(self.data_manage_button_widget)
        self.data_manage_button_widget.setHidden(True)

        self.docs_dock.closed.connect(self.on_destroy)
        self.sort_year_line.textChanged.connect(self.activate_sort_button)
        self.sort_year_button.clicked.connect(self.emit_year)
        self.docs_widget.doc_signal.connect(self.take_doc_data)
        self.data_widget.data_signal.connect(self.take_data)
        self.create_pareto_diagram_button.clicked.connect(self.create_pareto_diagram)
        self.sort_year_signal.connect(self.take_data)
        self.show()

    def refresh_data_in_table(self):
        self.take_data(self.title_label.text())

    @property
    def label_to_object_dict(self) -> dict:
        """
        Создаётся словарь, где ключами являются наименования редактируемых документов, а значениями - классы,
        содержащие методы по взаимодействию с ними.
        :return: dict
        """
        labels = DataHandler.names
        objects = (SubdivisionDialogWidget, DocumentsDialogWidget, UnitsDialogWidget, DismissalOrderDialogWidget,
                   DismissalInfoDialogWidget, TimeInfoDialogWidget)
        return dict(zip(labels, objects))

    def add_new_data(self) -> None:
        """
        Берёт наименования столбцов из активного документа и выводит диалоговое окно для вставки новой строки.
        :return: None
        """
        headers = []
        model = self.table.model()
        for col in range(model.columnCount()):
            headers.append(model.headerData(col, qtc.Qt.Horizontal))
        self.dialog_widget = self.label_to_object_dict[self.title_label.text()](headers)
        # self.dialog_widget.closed.connect(self.refresh_data_in_table)


    def edit_cur_row(self) -> None:
        """
        Берёт номер выделенной строки документа, собирает наименования столбцов и выводит диалоговое окно
        для редактирования строки.
        :return: None
        """
        cur_row = self.table.currentRow()
        if cur_row == -1:
            qtw.QMessageBox.information(self, "Внимание!", "Выделите нужную строку в таблице!", qtw.QMessageBox.Ok)
            return
        model = self.table.model()
        headers = []
        for col in range(model.columnCount()):
            headers.append(model.headerData(col, qtc.Qt.Horizontal))

        row_data = [model.index(cur_row, i).data() for i in range(model.columnCount())]
        self.dialog_widget = self.label_to_object_dict[self.title_label.text()](headers=headers, row_data=row_data)
        self.take_data(self.title_label.text())

    def del_cur_row(self) -> None:
        """
        Берёт номер выделенной строки и вызывает метод по её удалению.
        :return: None
        """
        cur_row = self.table.currentRow()
        if cur_row == -1:
            self.help_message_pop()
            return
        else:
            msg = self.question_message_pop()
            if msg == qtw.QMessageBox.Cancel:
                return
        some_data = self.table.model().index(cur_row, 0).data()
        DataHandler().data_list[self.title_label.text()].del_data(some_data)
        self.take_data(self.title_label.text())

    @classmethod
    def question_message_pop(cls) -> int:
        """
        Создаёт всплывающее окно, удостоверяющееся в том, что пользователь действительно хочет удалить строку.
        :return: None
        """
        msg = qtw.QMessageBox()
        msg.setIcon(qtw.QMessageBox.Question)
        msg.setText("Вы точно хотите удалить выделенную строку?")
        # msg.setInformativeText("Для этого щёлкните по номеру строки слева от таблицы!")
        msg.setStandardButtons(qtw.QMessageBox.Ok | qtw.QMessageBox.Cancel)
        return msg.exec()

    @classmethod
    def help_message_pop(cls) -> None:
        """
        Создаёт всплывающее окно с подсказкой при попытке редактировать/удалить строку документа,
        предварительно не выделив её.
        :return: None
        """
        msg = qtw.QMessageBox()
        msg.setIcon(qtw.QMessageBox.Information)
        msg.setText("Выделите нужную строку в таблице!")
        msg.setInformativeText("Для этого щёлкните по номеру строки слева от таблицы!")
        msg.setStandardButtons(qtw.QMessageBox.Ok)
        x = msg.exec()

    def on_destroy(self) -> None:
        """
        Убирает отметку выделения пункта меню, демонстрирующего наличие/отсутствие бокового окна интерфейса.
        :return: None
        """
        self.documents_view.setChecked(False)

    def show_document_list(self) -> None:
        """
        Скрывает или демонстрирует боковое окно интерфейса и меня состояние выделение соответствующего пункта меню,
        демонстрирующего его наличие/отсутствие.
        :return: None
        """
        if self.docs_dock.isVisible():
            self.docs_dock.close()
            self.documents_view.setChecked(False)

        else:
            self.docs_dock.show()
            self.documents_view.setChecked(True)

    def emit_year(self) -> None:
        """
        Транслирует сигнал, содержащий информацию о названии активного документа и годе, ранее которого
        записи выводиться не будут по запросу пользователя.
        :return: None
        """
        self.sort_year_signal.emit(self.title_label.text(), self.sort_year_line.text())

    def activate_sort_button(self) -> None:
        """
        Активирует кнопку, нажатие которой приводит к фильтрации записей по выбранному году.
        :return: None
        """
        if self.sort_year_line.text():
            self.sort_year_button.setEnabled(True)
        else:
            self.sort_year_button.setEnabled(False)

    def fill_table(self, headers: tuple[str], doc_data: list[tuple], text: str) -> None:
        """
        Заполняет таблицу данными из базы, устанавливает наименование активного документа, скрывает или демонстрирует
        кнопки, соответствующие возможностям взаимодействия с активным документом.
        :param headers: tuple[str]
        :param doc_data: list[tuple]
        :param text: str
        :return: None
        """
        self.title_label.setText(text)
        self.table.clear()
        self.table.setRowCount(0)
        column_number = len(doc_data[0])
        self.table.setColumnCount(column_number)
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(qtw.QHeaderView.ResizeToContents)
        # self.table.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)
        self.table.resizeColumnsToContents()
        # self.table.resizeRowsToContents()
        for data_row in doc_data:
            row_num = self.table.rowCount()
            self.table.insertRow(row_num)
            for i, element in enumerate(data_row):
                if element is None:
                    element = ''
                self.table.setItem(row_num, i, qtw.QTableWidgetItem(str(element)))
        # index = self.table.model().index(self.table.rowCount()-1, 0)
        self.table.scrollToBottom()
        # self.table.scrollToItem(self.table.item(self.table.rowCount(), 0), qtw.QAbstractItemView.PositionAtCenter)
        if self.title_label.text() in ("Штатное расписание", "Анкета", "Диаграмма Парето"):
            self.sort_year_widget.setHidden(False)
            self.sort_year_line.clear()
        else:
            self.sort_year_widget.setHidden(True)
        if self.title_label.text() == "Диаграмма Парето":
            self.create_pareto_diagram_button.setHidden(False)
        else:
            self.create_pareto_diagram_button.setHidden(True)
        if self.title_label.text() in DataHandler.names:
            self.data_manage_button_widget.setHidden(False)
        else:
            self.data_manage_button_widget.setHidden(True)

    def take_data(self, text: str) -> None:
        """
        Получает данные из базы по выбранному названию и вызывает метод fill_table для заполнения таблицы
        в интерфейсе программы.
        :param text: str
        :return: None
        """
        try:
            data = DataHandler().data_list[text].show()
            headers = data[0]
            doc_data = data[1]
        except KeyError as e:
            print(f"Здесь ошибка", e)
        else:
            self.fill_table(headers, doc_data, text)

    def take_doc_data(self, text: str, year: str | None = None) -> None:
        """
        Получает данные документа из базы по выбранному названию и вызывает метод fill_table для заполнения таблицы
        в интерфейсе программы. При наличии введённого года фильтрует записи.
        :param text: str
        :param year: str | None = None
        :return: None
        """
        try:
            if year:
                data = DocumentHandler().doc_func_dict[text](year)
                self.sorted_year = year
            else:
                data = DocumentHandler().doc_func_dict[text]()
                self.sorted_year = None
            headers = data[0]
            doc_data = data[1]
        except KeyError as e:
            print(f"Здесь ошибка", e)
        else:
            self.fill_table(headers, doc_data, text)

    def create_pareto_diagram(self) -> None:
        """
        Отправляет запрос на создание диаграммы Парето.
        :return: None
        """
        if self.sorted_year:
            DocumentHandler.create_pareto_diagram(self.sorted_year)
        else:
            DocumentHandler.create_pareto_diagram()

    def save_pdf(self) -> None:
        """
        Настраивает printer, вызывает метод по созданию html-представления документа и сохраняет в формате pdf.
        :return: None
        """
        file_name, _ = qtw.QFileDialog.getSaveFileName(self, "Export PDF", None, 'PDF files (.pdf);;All Files()')
        if file_name:
            if not qtc.QFileInfo(file_name).suffix():
                file_name += ".pdf"
            printer = QPrinter(QPrinter.PrinterResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_name)
            doc = self.create_html_from_table()
            doc.setPageSize(qtc.QSizeF(printer.pageRect().size()))
            doc.print_(printer)

    def save_xlsx(self) -> None:
        """
        Сохраняет в формате xlsx, используя ExcelWriter. Вызывает метод create_dataframe_from_table для перевода
        табличных значений в DataFrame.
        :return: None
        """
        file_name, _ = qtw.QFileDialog.getSaveFileName(self, "Export XLSX", None, "Книга Excel (.xlsx);;All Files()")
        if file_name:
            if not qtc.QFileInfo(file_name).suffix():
                file_name += ".xlsx"
            writer = pd.ExcelWriter(file_name, engine="xlsxwriter")
            df = self.create_dataframe_from_table()
            df.to_excel(writer, startrow=2, sheet_name="Лист1", index=False)
            workbook = writer.book
            worksheet = writer.sheets["Лист1"]
            for i, col in enumerate(df.columns):
                col_len = df[col].astype(str).str.len().max()
                col_len = max(col_len, len(col)) + 2
                worksheet.set_column(i, i, col_len)
            writer.save()

    def create_dataframe_from_table(self) -> pd.DataFrame:
        """
        Создаёт pandas.DataFrame из данных активного документа.
        :return: pd.DataFrame
        """
        headers = []
        model = self.table.model()
        for col in range(model.columnCount()):
            headers.append(model.headerData(col, qtc.Qt.Horizontal))
        df = pd.DataFrame(columns=headers)
        for row in range(model.rowCount()):
            for col in range(model.columnCount()):
                df.at[row, headers[col]] = model.index(row, col).data()
        return df

    def create_html_from_table(self) -> qtg.QTextDocument:
        """
        Создаёт html-представление активного документа.
        :return: qtg.QTextDocument
        """
        doc = qtg.QTextDocument()
        model = self.table.model()
        html = """
        <html>
        <head>
        <style>
        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
        }
        </style>
        </head>
        """
        html += f"<h1>{self.title_label.text()}</h1>"
        html += "<table><thead>"
        html += "<tr>"
        for col in range(model.columnCount()):
            html += f"<th>{model.headerData(col, qtc.Qt.Horizontal)}</th>"
        html += "</tr></thead>"
        html += "<tbody>"
        for row in range(model.rowCount()):
            html += "<tr>"
            for col in range(model.columnCount()):
                html += f"<td>{model.index(row, col).data()}</td>"
            html += "</tr>"
        html += "</tbody></table>"
        doc.setHtml(html)
        return doc


class MyDockWidget(qtw.QDockWidget):
    """
    Класс, представляющий из себя потомка qtw.QDockWidget с перегруженным методом closeEvent для более удобного
    перехвата события.
    """

    closed = qtc.pyqtSignal()

    def __init__(self, *args):
        super().__init__(*args)

    def closeEvent(self, event: qtg.QCloseEvent) -> None:
        """
        Запускает closeEvent, транслируя сигнал closed.
        :param event: qtg.QCloseEvent
        :return: None
        """
        self.closed.emit()
        super().closeEvent(event)


class DataManagingWidget(qtw.QWidget):
    """
    Класс описывает поведение QListWidget для редактируемых данных в боковой панели интерфейса программы.
    """

    data_signal = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.layout = qtw.QVBoxLayout()
        self.data_label = qtw.QLabel("Управление данными")

        self.data_list = qtw.QListWidget()
        self.data_list.addItems(DataHandler.names)
        self.layout.addWidget(self.data_label)
        self.layout.addWidget(self.data_list)
        self.setLayout(self.layout)
        self.data_label.setFixedHeight(20)
        self.data_list.setFixedHeight(min(self.data_list.sizeHintForRow(0) * self.data_list.count(),
                                          self.data_list.sizeHintForRow(0) * 6) + 5)
        self.setFixedHeight(self.data_label.height() + self.data_list.height() + 20)
        self.data_list.doubleClicked.connect(self.on_submit)
        self.show()

    def on_submit(self, item: qtc.QModelIndex) -> None:
        """
        Транслирует сигнал при двойном нажатии на элемент и передаёт содержащийся в элементе текст.
        :param item: qtc.QModelIndex
        :return: None
        """
        text = item.data()
        self.data_signal.emit(text)


class DocumentWidget(qtw.QWidget):
    """
    Класс описывает поведение QTreeWidget для документов в боковой панели интерфейса программы.
    """

    doc_signal = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.layout = qtw.QVBoxLayout()
        self.doc_tree_widget = qtw.QTreeWidget()
        self.staff_list_parent = qtw.QTreeWidgetItem(self.doc_tree_widget, ["Составление штатного расписания"])
        self.staff_list_input = qtw.QTreeWidgetItem(self.staff_list_parent, ["Входные документы"])
        self.staff_list_output = qtw.QTreeWidgetItem(self.staff_list_parent, ["Выходные документы"])
        for i, doc in enumerate(DocumentHandler.staff_list_docs):
            setattr(self, f"staff_list_in_doc_{i}", qtw.QTreeWidgetItem(self.staff_list_input, [doc]))
        self.staff_list = qtw.QTreeWidgetItem(self.staff_list_output, ["Штатное расписание"])
        self.missing_unit_info_parent = qtw.QTreeWidgetItem(self.doc_tree_widget,
                                                            ["Определение годовой потребности в недостающем персонале"])
        self.missing_unit_info_input = qtw.QTreeWidgetItem(self.missing_unit_info_parent, ["Входные документы"])
        self.missing_unit_info_output = qtw.QTreeWidgetItem(self.missing_unit_info_parent, ["Выходные документы"])
        for i, doc in enumerate(DocumentHandler.missing_unit_docs):
            setattr(self, f"missing_unit_in_doc_{i}", qtw.QTreeWidgetItem(self.missing_unit_info_input, [doc]))
        self.missing_unit_info = qtw.QTreeWidgetItem(self.missing_unit_info_output,
                                                     ["Форма справки о недостающих кадрах"])
        self.pareto_parent = qtw.QTreeWidgetItem(self.doc_tree_widget, ["Учёт текучести кадров и анализ причин"])
        self.pareto_input = qtw.QTreeWidgetItem(self.pareto_parent, ["Входные документы"])
        self.pareto_output = qtw.QTreeWidgetItem(self.pareto_parent, ["Выходные документы"])
        for i, doc in enumerate(DocumentHandler.pareto_docs):
            setattr(self, f"pareto_in_doc_{i}", qtw.QTreeWidgetItem(self.pareto_input, [doc]))
        self.missing_unit_info = qtw.QTreeWidgetItem(self.pareto_output, ["Диаграмма Парето"])
        self.doc_tree_widget.expandAll()
        self.doc_tree_widget.adjustSize()
        self.doc_tree_widget.setHeaderLabel("Решение задач")
        self.layout.addWidget(self.doc_tree_widget)
        self.setLayout(self.layout)

        self.doc_tree_widget.doubleClicked.connect(self.on_submit)
        self.show()

    def on_submit(self, val: qtc.QModelIndex) -> None:
        """
        Транслирует сигнал при двойном нажатии на элемент и передаёт содержащийся в элементе текст.
        :param val: qtc.QModelIndex
        :return: None
        """
        text = val.data()
        self.doc_signal.emit(text)


class BaseDialogWidget(qtw.QWidget):
    """
    Базовый класс, осуществляющий построение диалогового окна для редактирования данных.
    Необходимо переопределить методы create_fields и on_submit для корретной работы.
    """
    closed = qtc.pyqtSignal()

    def __init__(self, headers: list[str], row_data: list[str] | None = None):
        super().__init__()
        self.row_data = row_data
        self.headers = headers
        self.layout = qtw.QFormLayout()
        self.create_fields()
        if row_data:
            self.fill_fields_with_data()
        self.button_widget = qtw.QWidget()
        self.button_widget.setLayout(qtw.QHBoxLayout())
        self.submit_button = qtw.QPushButton("Ок")
        self.cancel_button = qtw.QPushButton("Отмена")
        self.button_widget.layout().addWidget(self.cancel_button)
        self.button_widget.layout().addWidget(self.submit_button)
        self.cancel_button.clicked.connect(self.close)
        self.submit_button.clicked.connect(self.on_submit)
        self.layout.addRow("", self.button_widget)
        self.setLayout(self.layout)
        self.show()

    @staticmethod
    def str_to_table_date(string: str) -> datetime:
        """
        Переводит строку с датой формата базы данных в объект datetime.
        :param string: str
        :return: datetime
        """
        return datetime.strptime(string, "%Y-%m-%d")

    @staticmethod
    def date_to_database_format(date: str) -> str:
        """
        Переводит строку с табличным форматом данных в строку формата базы данных.
        :param date: str
        :return: str
        """
        return datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")

    @staticmethod
    def _get_list_from_bd(object_name: type, index: int, cond_index: int | None = None) -> list[str]:
        """
        Возвращает список по заданным параметрам из базы данных.
        :param object_name: type
        :param index: int
        :param cond_index: int | None = None
        :return: list[str]
        """
        data_set = set()
        data = object_name.show()[1]
        if cond_index is not None:
            for element in data:
                if (el := element[index]) not in data_set and element[cond_index] is None:
                    data_set.add(el)
        else:
            for element in data:
                if (el := element[index]) not in data_set:
                    data_set.add(el)
        return sorted(data_set)

    def get_struct_list(self) -> list[str]:
        """
        Возвращает список отделов в организации.
        :return: list[str]
        """
        return self._get_list_from_bd(Subdivision, 2)

    def get_func_list(self) -> list[str]:
        """
        Возвращает список специальностей в организации.
        :return: list[str]
        """
        return self._get_list_from_bd(Subdivision, 1)

    def get_reas_list(self) -> list[str]:
        """
        Возвращает список причин увольнения.
        :return: list[str]
        """
        return self._get_list_from_bd(DismissalInfo, 1)

    def get_active_spec_list(self) -> list[str]:
        """
        Возвращает список действующих сотрудников.
        :return: list[str]
        """
        return self._get_list_from_bd(Units, 1, 5)

    def fill_fields_with_data(self) -> None:
        """
        Заполняет поля диалогового окна редактируемыми данными.
        :return: None
        """
        raise NotImplementedError

    def create_fields(self) -> None:
        """
        Создаёт поля для диалогового окна.
        :return: None
        """
        raise NotImplementedError

    def on_submit(self) -> None:
        """
        Собирает данные из заполненных полей диалогового окна и вызывает специальные методы по редактированию данных.
        При удачном завершении запроса закрывает диалоговое окно.
        :return: None
        """
        raise NotImplementedError

    def closeEvent(self, event: qtg.QCloseEvent) -> None:
        """
        Запускает closeEvent, транслируя сигнал closed.
        :param event: qtg.QCloseEvent
        :return: None
        """
        self.closed.emit()
        super().closeEvent(event)


class SubdivisionDialogWidget(BaseDialogWidget):
    """
    Описывает поведение диалогового окна для таблицы "Структурные подразделения".
    """

    def __init__(self, headers: list[str], row_data: list[str] | None = None):
        super().__init__(headers, row_data)

    def create_fields(self) -> None:
        self.id_line_edit = qtw.QLineEdit()
        self.func_line_edit = qtw.QLineEdit()
        self.struct_line_edit = qtw.QComboBox()
        self.struct_line_edit.setEditable(True)
        items_list = self.get_struct_list()
        self.struct_line_edit.addItems(items_list)
        self.struct_line_edit.setFixedWidth(250)

        self.salary_line_edit = qtw.QLineEdit()
        self.layout.addRow(self.headers[0], self.id_line_edit)
        self.layout.addRow(self.headers[1], self.func_line_edit)
        self.layout.addRow(self.headers[2], self.struct_line_edit)
        self.layout.addRow(self.headers[3], self.salary_line_edit)

    def fill_fields_with_data(self) -> None:
        self.id_line_edit.setText(self.row_data[0])
        self.func_line_edit.setText(self.row_data[1])
        self.struct_line_edit.setCurrentIndex(self.struct_line_edit.findText(self.row_data[2]))
        self.salary_line_edit.setText(self.row_data[3])

    def on_submit(self):
        fid, func, struct, salary = self.id_line_edit.text(), self.func_line_edit.text(), \
                                    self.struct_line_edit.currentText(), self.salary_line_edit.text()
        try:
            if self.row_data:
                Subdivision.edit_data(fid, func, struct, salary, self.row_data[0])
            else:
                Subdivision.add_data(fid, func, struct, salary)
        except Exception as e:
            print(e)
        else:
            self.close()


class DocumentsDialogWidget(BaseDialogWidget):
    """
        Описывает поведение диалогового окна для таблицы "Документы".
    """

    def __init__(self, headers: list[str], row_data: list[str] | None = None):
        super().__init__(headers, row_data)

    def create_fields(self) -> None:
        self.id_line_edit = qtw.QLineEdit()
        self.name_line_edit = qtw.QLineEdit()
        self.func_line_edit = qtw.QComboBox()
        self.func_line_edit.setFixedWidth(250)
        self.func_line_edit.addItems(self.get_func_list())
        self.time_line_edit = qtw.QLineEdit()
        self.count_line_edit = qtw.QLineEdit()
        self.period_line_edit = qtw.QLineEdit()
        self.layout.addRow(self.headers[0], self.id_line_edit)
        self.layout.addRow(self.headers[1], self.name_line_edit)
        self.layout.addRow(self.headers[2], self.func_line_edit)
        self.layout.addRow(self.headers[3], self.time_line_edit)
        self.layout.addRow(self.headers[4], self.count_line_edit)
        self.layout.addRow(self.headers[5], self.period_line_edit)

    def fill_fields_with_data(self) -> None:
        self.id_line_edit.setText(self.row_data[0])
        self.name_line_edit.setText(self.row_data[1])
        self.func_line_edit.setCurrentIndex(self.func_line_edit.findText(self.row_data[2]))
        self.time_line_edit.setText(self.row_data[3])
        self.count_line_edit.setText(self.row_data[4])
        self.period_line_edit.setText(self.row_data[5])

    def on_submit(self) -> None:
        did, name, func, time, count, period = self.id_line_edit.text(), self.name_line_edit.text(), \
                                               self.func_line_edit.currentText(), self.time_line_edit.text(), \
                                               self.count_line_edit.text(), self.period_line_edit.text()
        try:
            if self.row_data:
                Documents.edit_data(did, name, func, time, count, period, self.row_data[0])
            else:
                Documents.add_data(did, name, func, time, count, period)
        except Exception as e:
            traceback.print_exc()
        else:
            self.close()


class UnitsDialogWidget(BaseDialogWidget):
    """
        Описывает поведение диалогового окна для таблицы "Сотрудники".
    """

    def __init__(self, headers: list[str], row_data: list[str] | None = None):
        super().__init__(headers, row_data)

    def create_fields(self) -> None:
        self.id_line_edit = qtw.QLineEdit()
        self.name_line_edit = qtw.QLineEdit()
        self.birthday_line_edit = qtw.QDateEdit(calendarPopup=True)
        self.birthday_line_edit.clear()
        self.func_line_edit = qtw.QComboBox()
        self.func_line_edit.setFixedWidth(250)
        self.func_line_edit.addItems(self.get_func_list())
        self.st_date_line_edit = qtw.QDateEdit(calendarPopup=True)
        self.st_date_line_edit.setDate(qtc.QDate.currentDate())
        self.open_e_date_section_label = qtw.QLabel("Увольнение сотрудника")
        self.open_e_date_section_checkbox = qtw.QCheckBox()
        self.e_date_label = qtw.QLabel(self.headers[5])
        self.e_date_line_edit = qtw.QDateEdit(calendarPopup=True)
        self.e_date_line_edit.setDate(qtc.QDate(1, 1, 1))
        self.open_e_date_section_label.setHidden(True)
        self.open_e_date_section_checkbox.setHidden(True)
        self.e_date_label.setHidden(True)
        self.e_date_line_edit.setHidden(True)
        self.layout.addRow(self.headers[0], self.id_line_edit)
        self.layout.addRow(self.headers[1], self.name_line_edit)
        self.layout.addRow(self.headers[2], self.birthday_line_edit)
        self.layout.addRow(self.headers[3], self.func_line_edit)
        self.layout.addRow(self.headers[4], self.st_date_line_edit)
        self.layout.addRow(self.open_e_date_section_label, self.open_e_date_section_checkbox)
        self.layout.addRow(self.e_date_label, self.e_date_line_edit)

    def fill_fields_with_data(self) -> None:
        self.id_line_edit.setText(self.row_data[0])
        self.name_line_edit.setText(self.row_data[1])
        self.birthday_line_edit.setDate(self.str_to_table_date(self.row_data[2]))
        self.func_line_edit.setCurrentIndex(self.func_line_edit.findText(self.row_data[3]))
        self.st_date_line_edit.setDate(self.str_to_table_date(self.row_data[4]))
        self.open_e_date_section_label.setHidden(False)
        self.open_e_date_section_checkbox.setHidden(False)
        self.open_e_date_section_checkbox.stateChanged.connect(self.open_e_date_section)
        if self.row_data[5]:
            self.open_e_date_section_checkbox.setChecked(True)

    def open_e_date_section(self):
        if self.open_e_date_section_checkbox.isChecked():
            self.e_date_label.setHidden(False)
            self.e_date_line_edit.setHidden(False)
            if self.row_data[5]:
                self.e_date_line_edit.setDate(self.str_to_table_date(self.row_data[5]))
            else:
                self.e_date_line_edit.setDate(qtc.QDate.currentDate())
        else:
            self.e_date_label.setHidden(True)
            self.e_date_line_edit.setHidden(True)
            self.e_date_line_edit.setDate(qtc.QDate(1, 1, 1))
            # print(self.e_date_line_edit.minimumDate())

    def on_submit(self) -> None:
        uid, name, birth, func, st_date, e_date = self.id_line_edit.text(), self.name_line_edit.text(), \
                                               self.birthday_line_edit.text(), self.func_line_edit.currentText(), \
                                               self.st_date_line_edit.text(), self.e_date_line_edit.text()
        birth, st_date, e_date = map(self.date_to_database_format, (birth, st_date, e_date))
        if e_date == "1752-09-14":
            e_date = None
        try:
            if self.row_data:
                Units.edit_data(uid, name, birth, func, st_date, e_date, self.row_data[0])
            else:
                Units.add_data(uid, name, birth, func, st_date)
        except Exception as e:
            print(e)
        else:
            self.close()


class DismissalOrderDialogWidget(BaseDialogWidget):
    """
        Описывает поведение диалогового окна для таблицы "Приказ об увольнении".
    """

    def __init__(self, headers: list[str], row_data: list[str] | None = None):
        super().__init__(headers, row_data)

    def create_fields(self) -> None:
        self.id_line_edit = qtw.QLineEdit()
        self.date_line_edit = qtw.QDateEdit(calendarPopup=True)
        self.date_line_edit.setDate(qtc.QDate.currentDate())
        self.name_line_edit = qtw.QComboBox()
        self.name_line_edit.setFixedWidth(250)
        self.name_line_edit.addItems(self.get_active_spec_list())
        self.reas_line_edit = qtw.QComboBox()
        self.reas_line_edit.setFixedWidth(250)
        self.reas_line_edit.addItems(self.get_reas_list())
        self.real_reas_line_edit = qtw.QLineEdit()
        self.layout.addRow(self.headers[0], self.id_line_edit)
        self.layout.addRow(self.headers[1], self.date_line_edit)
        self.layout.addRow(self.headers[2], self.name_line_edit)
        self.layout.addRow(self.headers[3], self.reas_line_edit)
        self.layout.addRow(self.headers[4], self.real_reas_line_edit)

    def fill_fields_with_data(self) -> None:
        self.id_line_edit.setText(self.row_data[0])
        self.date_line_edit.setDate(self.str_to_table_date(self.row_data[1]))
        name_id = self.name_line_edit.findText(self.row_data[2])
        if name_id == -1:
            self.name_line_edit.addItem(self.row_data[2])
        self.name_line_edit.setCurrentIndex(self.name_line_edit.findText(self.row_data[2]))
        self.reas_line_edit.setCurrentIndex(self.reas_line_edit.findText(self.row_data[3]))
        self.real_reas_line_edit.setText(self.row_data[4])

    def on_submit(self) -> None:
        doid, date, name, reas, real_reas = self.id_line_edit.text(), self.date_line_edit.text(), \
                                                  self.name_line_edit.currentText(), self.reas_line_edit.currentText(), \
                                                  self.real_reas_line_edit.text()
        date = self.date_to_database_format(date)
        try:
            if self.row_data:
                DismissalOrder.edit_data(doid, date, name, reas, real_reas, self.row_data[0])
            else:
                DismissalOrder.add_data(doid, date, name, reas, real_reas)
        except Exception as e:
            print(e)
        else:
            self.close()


class DismissalInfoDialogWidget(BaseDialogWidget):
    """
        Описывает поведение диалогового окна для таблицы "Расшифровка причин увольнения".
    """

    def __init__(self, headers: list[str], row_data: list[str] | None = None):
        super().__init__(headers, row_data)

    def create_fields(self) -> None:
        self.id_line_edit = qtw.QLineEdit()
        self.sh_reas_line_edit = qtw.QLineEdit()
        self.f_reas_line_edit = qtw.QLineEdit()
        self.layout.addRow(self.headers[0], self.id_line_edit)
        self.layout.addRow(self.headers[1], self.sh_reas_line_edit)
        self.layout.addRow(self.headers[2], self.f_reas_line_edit)

    def fill_fields_with_data(self) -> None:
        self.id_line_edit.setText(self.row_data[0])
        self.sh_reas_line_edit.setText(self.row_data[1])
        self.f_reas_line_edit.setText(self.row_data[2])

    def on_submit(self) -> None:
        did, sh_reas, f_reas = self.id_line_edit.text(), self.sh_reas_line_edit.text(), \
                                            self.f_reas_line_edit.text()
        try:
            if self.row_data:
                DismissalInfo.edit_data(did, sh_reas, f_reas, self.row_data[0])
            else:
                DismissalInfo.add_data(did, sh_reas, f_reas)
        except Exception as e:
            print(e)
        else:
            self.close()


class TimeInfoDialogWidget(BaseDialogWidget):
    """
        Описывает поведение диалогового окна для таблицы "Данные о рабочем времени".
    """

    def __init__(self, headers: list[str], row_data: list[str] | None = None):
        super().__init__(headers, row_data)

    def create_fields(self) -> None:
        self.year_line_edit = qtw.QLineEdit()
        self.hy_line_edit = qtw.QLineEdit()
        self.hd_line_edit = qtw.QLineEdit()
        self.dy_line_edit = qtw.QLineEdit()
        self.layout.addRow(self.headers[0], self.year_line_edit)
        self.layout.addRow(self.headers[1], self.hy_line_edit)
        self.layout.addRow(self.headers[2], self.hd_line_edit)
        self.layout.addRow(self.headers[3], self.dy_line_edit)

    def fill_fields_with_data(self) -> None:
        self.year_line_edit.setText(self.row_data[0])
        self.hy_line_edit.setText(self.row_data[1])
        self.hd_line_edit.setText(self.row_data[2])
        self.dy_line_edit.setText(self.row_data[3])

    def on_submit(self) -> None:
        year, hy, hd, dy = self.year_line_edit.text(), self.hy_line_edit.text(), \
                               self.hd_line_edit.text(), self.dy_line_edit.text()
        try:
            if self.row_data:
                TimeInfo.edit_data(year, hy, hd, dy, self.row_data[0])
            else:
                TimeInfo.add_data(year, hy, hd, dy)
        except Exception as e:
            print(e)
        else:
            self.close()


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec())