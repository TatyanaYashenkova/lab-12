import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import sqlite3
import os

class TitanicDBApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа 12. Вариант 28")
        self.root.geometry("1100x700")
        self.db_name = "titanic.db"
        self.conn = None
        self.cursor = None
        #перейти к записи
        self.current_id = None
        #интерфейс (вкладки)
        self.create_ui()
        #подключаем БД
        self.init_db()

    def create_ui(self):
        """Создание интерфейса с тремя вкладками (II окна)"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        #Вкладка 1: База данных
        self.tab_db = tk.Frame(self.notebook)
        self.notebook.add(self.tab_db, text="База данных (Просмотр/Управление)")
        self.setup_tab_db()

        #Вкладка 2: Вычисленные характеристики
        self.tab_calc = tk.Frame(self.notebook)
        self.notebook.add(self.tab_calc, text="Вычисленные характеристики")
        self.setup_tab_calc()

        #Вкладка 3: Поиск и Редактирование
        self.tab_edit = tk.Frame(self.notebook)
        self.notebook.add(self.tab_edit, text="Поиск и Редактирование")
        self.setup_tab_edit()

    #ВКЛАДКА 1: БД
    def setup_tab_db(self):
        # Панель кнопок
        top = tk.Frame(self.tab_db, pady=10, bg="#f0f0f0")
        top.pack(fill=tk.X)

        tk.Button(top, text="1. Импортировать CSV", command=self.import_csv, bg="#e1f5fe").pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="2. Просмотр БД", command=self.view_all, bg="#c8e6c9").pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="3. Ввести запись", command=self.open_add_window, bg="#fff9c4").pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="4. Перейти к записи", command=self.go_to_record, bg="#ffe0b2").pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="5. Удалить запись", command=self.delete_record, bg="#ffcdd2").pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="6. Очистить БД", command=self.clear_db, bg="#ffcdd2").pack(side=tk.LEFT, padx=5)

        # Область вывода
        self.text_db = tk.Text(self.tab_db, wrap="word", font=("Consolas", 10))
        scroll = tk.Scrollbar(self.tab_db, command=self.text_db.yview)
        self.text_db.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_db.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    #ВКЛАДКА 2: РАСЧЕТ
    def setup_tab_calc(self):
        top = tk.Frame(self.tab_calc, pady=10)
        top.pack(fill=tk.X)

        tk.Button(top, text="ВЫПОЛНИТЬ РАСЧЕТ (Вариант 28)", command=self.calculate_task,
                  bg="#fff9c4", font=("Arial", 12, "bold")).pack(pady=10)

        self.text_calc = tk.Text(self.tab_calc, wrap="word", font=("Consolas", 11))
        scroll = tk.Scrollbar(self.tab_calc, command=self.text_calc.yview)
        self.text_calc.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_calc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    #ВКЛАДКА 3: ПОИСК И РЕДАКТИРОВАНИЕ
    def setup_tab_edit(self):
        # Поиск
        search_frame = tk.LabelFrame(self.tab_edit, text="Поиск по полям", pady=10, padx=10)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(search_frame, text="Введите имя или пол:").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=10)
        tk.Button(search_frame, text="Найти", command=self.search_records).pack(side=tk.LEFT)
        tk.Button(search_frame, text="Сбросить", command=lambda: self.text_edit.delete(1.0, tk.END)).pack(side=tk.LEFT,
                                                                                                          padx=10)
        # Редактирование
        edit_frame = tk.LabelFrame(self.tab_edit, text="Редактирование записи (введите ID и новые данные)", pady=10,
                                   padx=10)
        edit_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(edit_frame, text="ID записи:").grid(row=0, column=0, padx=5, pady=5)
        self.edit_id_entry = tk.Entry(edit_frame, width=10)
        self.edit_id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(edit_frame, text="Новое Имя:").grid(row=1, column=0, padx=5, pady=5)
        self.edit_name_entry = tk.Entry(edit_frame, width=40)
        self.edit_name_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(edit_frame, text="Новый Возраст:").grid(row=2, column=0, padx=5, pady=5)
        self.edit_age_entry = tk.Entry(edit_frame, width=10)
        self.edit_age_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(edit_frame, text="Новая Цена (Fare):").grid(row=3, column=0, padx=5, pady=5)
        self.edit_fare_entry = tk.Entry(edit_frame, width=10)
        self.edit_fare_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Button(edit_frame, text="Сохранить изменения", command=self.update_record, bg="#c8e6c9").grid(row=4,
                                                                                                         column=0,
                                                                                                         columnspan=2,
                                                                                                         pady=10)

        # Вывод результатов поиска
        self.text_edit = tk.Text(self.tab_edit, wrap="word", font=("Consolas", 10), height=10)
        self.text_edit.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    #РАБОТА С БД
    def init_db(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS passengers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    PassengerId INTEGER, Survived INTEGER, Pclass INTEGER,
                    Name TEXT, Sex TEXT, Age REAL, SibSp INTEGER, Parch INTEGER,
                    Ticket TEXT, Fare REAL, Cabin TEXT, Embarked TEXT
                )
            """)
            self.conn.commit()
            self.log_db("База данных подключена.")
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))

    def log_db(self, msg):
        self.text_db.insert(tk.END, msg + "\n")
        self.text_db.see(tk.END)

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=(("CSV", "*.csv"), ("Все", "*.*")))
        if not path: return
        try:
            self.cursor.execute("DELETE FROM passengers")
            with open(path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    age = float(row['Age']) if row.get('Age') else None
                    fare = float(row['Fare']) if row.get('Fare') else 0.0
                    self.cursor.execute("""
                        INSERT INTO passengers (PassengerId, Survived, Pclass, Name, Sex, Age, SibSp, Parch, Ticket, Fare, Cabin, Embarked)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (row.get('PassengerId'), row.get('Survived'), row.get('Pclass'), row.get('Name'),
                          row.get('Sex'), age, row.get('SibSp'), row.get('Parch'), row.get('Ticket'),
                          fare, row.get('Cabin'), row.get('Embarked')))
                    count += 1
            self.conn.commit()
            self.log_db(f"Импортировано {count} записей.")
        except Exception as e:
            messagebox.showerror("Ошибка импорта", str(e))

    def view_all(self):
        self.text_db.delete(1.0, tk.END)
        self.cursor.execute("SELECT id, Name, Sex, Age, Survived FROM passengers LIMIT 100")
        rows = self.cursor.fetchall()
        self.log_db(f"--- ПРОСМОТР (первые 100 из {len(rows)}) ---")
        for r in rows:
            self.log_db(f"ID:{r[0]} | {r[1]} | {r[2]} | Возраст:{r[3]} | Выжил:{r[4]}")

    def go_to_record(self):
        idx = tk.simpledialog.askstring("Переход", "Введите ID записи:")
        if not idx: return
        self.cursor.execute("SELECT * FROM passengers WHERE id=?", (idx,))
        row = self.cursor.fetchone()
        if row:
            self.text_db.delete(1.0, tk.END)
            self.log_db(f"--- ЗАПИСЬ ID {idx} ---")
            self.log_db(
                f"PassengerId: {row[1]}\nSurvived: {row[2]}\nPclass: {row[3]}\nName: {row[4]}\nSex: {row[5]}\nAge: {row[6]}\nFare: {row[10]}")
        else:
            messagebox.showinfo("Поиск", "Запись не найдена.")

    def delete_record(self):
        idx = tk.simpledialog.askstring("Удаление", "Введите ID для удаления:")
        if idx:
            self.cursor.execute("DELETE FROM passengers WHERE id=?", (idx,))
            self.conn.commit()
            self.log_db(f"Запись {idx} удалена.")

    def clear_db(self):
        if messagebox.askyesno("Очистка", "Удалить все данные из БД?"):
            self.cursor.execute("DELETE FROM passengers")
            self.conn.commit()
            self.log_db("База данных очищена.")

    def open_add_window(self):
        """Окно для ввода новой записи"""
        win = tk.Toplevel(self.root)
        win.title("Добавление записи")
        win.geometry("400x500")

        fields = [("Name", "Имя"), ("Sex", "Пол (male/female)"), ("Age", "Возраст"),
                  ("Fare", "Цена билета"), ("Survived", "Выжил (0/1)"), ("Pclass", "Класс (1/2/3)")]
        entries = {}

        for i, (key, label) in enumerate(fields):
            tk.Label(win, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            e = tk.Entry(win)
            e.grid(row=i, column=1, padx=5, pady=5)
            entries[key] = e

        def save():
            try:
                self.cursor.execute("""
                    INSERT INTO passengers (Name, Sex, Age, Fare, Survived, Pclass)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (entries['Name'].get(), entries['Sex'].get(), entries['Age'].get(),
                      entries['Fare'].get(), entries['Survived'].get(), entries['Pclass'].get()))
                self.conn.commit()
                self.log_db("Запись добавлена.")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(win, text="Сохранить", command=save, bg="#c8e6c9").grid(row=len(fields), column=0, columnspan=2,
                                                                          pady=20)

    #РАСЧЕТ (ВАРИАНТ 28)
    def calculate_task(self):
        self.text_calc.delete(1.0, tk.END)
        self.text_calc.insert(tk.END, "--- РАСЧЕТ (Вариант 28) ---\n")
        self.text_calc.insert(tk.END, "Средняя стоимость билетов мужчин в интервале мода±5\n")
        self.text_calc.insert(tk.END, "в разрезе выжившие / погибшие.\n\n")

        try:
            # 1. Мода возраста
            self.cursor.execute("""
                SELECT CAST(Age AS INT), COUNT(*) as C FROM passengers 
                WHERE Sex='male' AND Age IS NOT NULL 
                GROUP BY CAST(Age AS INT) ORDER BY C DESC LIMIT 1
            """)
            res = self.cursor.fetchone()
            if not res:
                self.text_calc.insert(tk.END, "Нет данных о мужчинах с возрастом.\n")
                return
            mode_age = res[0]
            min_a, max_a = mode_age - 5, mode_age + 5
            self.text_calc.insert(tk.END, f"Мода возраста: {mode_age} лет\n")
            self.text_calc.insert(tk.END, f"Интервал: {min_a} - {max_a} лет\n\n")

            # 2. Средняя цена
            for surv, label in [(1, "ВЫЖИВШИЕ"), (0, "ПОГИБШИЕ")]:
                self.cursor.execute("""
                    SELECT AVG(Fare), COUNT(*) FROM passengers 
                    WHERE Sex='male' AND Age BETWEEN ? AND ? AND Survived=?
                """, (min_a, max_a, surv))
                avg_fare, count = self.cursor.fetchone()
                if count > 0:
                    self.text_calc.insert(tk.END, f"{label}:\n")
                    self.text_calc.insert(tk.END, f"  Количество: {count}\n")
                    self.text_calc.insert(tk.END, f"  Средняя стоимость: {avg_fare:.2f}\n\n")
                else:
                    self.text_calc.insert(tk.END, f"{label}: Нет данных в интервале.\n\n")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    #ПОИСК И РЕДАКТИРОВАНИЕ
    def search_records(self):
        q = self.search_entry.get()
        if not q: return
        self.text_edit.delete(1.0, tk.END)
        self.cursor.execute("SELECT id, Name, Sex, Age, Fare FROM passengers WHERE Name LIKE ? OR Sex LIKE ?",
                            (f'%{q}%', f'%{q}%'))
        rows = self.cursor.fetchall()
        self.text_edit.insert(tk.END, f"--- РЕЗУЛЬТАТЫ ПОИСКА: '{q}' ---\n")
        for r in rows:
            self.text_edit.insert(tk.END, f"ID:{r[0]} | {r[1]} | Пол:{r[2]} | Возраст:{r[3]} | Цена:{r[4]}\n")

    def update_record(self):
        idx = self.edit_id_entry.get()
        name = self.edit_name_entry.get()
        age = self.edit_age_entry.get()
        fare = self.edit_fare_entry.get()
        if not idx:
            messagebox.showwarning("Внимание", "Введите ID записи!")
            return
        try:
            if name:
                self.cursor.execute("UPDATE passengers SET Name=? WHERE id=?", (name, idx))
            if age:
                self.cursor.execute("UPDATE passengers SET Age=? WHERE id=?", (age, idx))
            if fare:
                self.cursor.execute("UPDATE passengers SET Fare=? WHERE id=?", (fare, idx))
            self.conn.commit()
            messagebox.showinfo("Успех", f"Запись {idx} обновлена!")
            self.log_db(f"Запись {idx} обновлена.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    from tkinter import simpledialog

    root = tk.Tk()
    app = TitanicDBApp(root)
    root.mainloop()