import sys

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PIL.ImageQt import *
from PIL import *
from PyQt5.QtCore import *
import sqlite3
import subprocess


class MainWidgetPupil(QWidget):
    def __init__(self, login):
        super().__init__()
        self.initUI(login)

    def initUI(self, login):
        self.login = login
        mainlayout = QHBoxLayout(self)
        layout = QVBoxLayout()
        self.setWindowTitle('Главное меню')
        self.btn_tsk = QPushButton("Задачи")
        self.btn_tsk.clicked.connect(self.Task)
        self.setFixedSize(300, 150)
        self.btn_prfl = QPushButton(self)
        self.btn_prfl.setIcon(QIcon('профиль.png'))
        self.btn_prfl.setFixedSize(QSize(50, 50))
        self.btn_prfl.clicked.connect(self.ProfileBtn)

        layout.addWidget(self.btn_tsk)
        mainlayout.addLayout(layout)
        mainlayout.addWidget(self.btn_prfl)

    def Task(self):
        self.tskwindow = TaskWindow(self.login)
        self.tskwindow.show()

    def ProfileBtn(self):
        self.prfl = ProfileWidget(self.login)
        self.prfl.show()


class ProfileWidget(QWidget):
    def __init__(self, login):
        super().__init__()
        self.initUI(login)

    def initUI(self, login):
        super(ProfileWidget, self).__init__()
        self.login = login
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        res = cur.execute(
            "SELECT * FROM users WHERE login=?", (login,)).fetchone()
        summ = 0
        for i in res[5].split(";"):
            summ += int(i)
        if res[3]:
            pic = res[3]
        else:
            pic = 'профиль.png'
        im = Image.open(pic).resize((50, 50)).save(pic)
        pixmap = QPixmap(pic)
        layout = QFormLayout(self)
        self.pic = QLabel(self)
        self.pic.setPixmap(pixmap)

        score = QLabel(str(summ))
        name = QLabel(self)
        name.setText(login)
        level = QLabel(self)
        level.setText(res[4])
        btn = QPushButton("Сменить изображение профиля")
        btn.clicked.connect(self.Change)
        layout.addRow(name, self.pic)
        layout.addRow("Уровень аккаунта: ", level)
        layout.addRow("Points: ", score)
        layout.addWidget(btn)
        con.close()

    def Change(self):
        fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
        im = Image.open(fname).resize((50, 50)).save(fname)
        pixmap = QPixmap(fname)
        self.pic.setPixmap(pixmap)
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        res = cur.execute("""UPDATE users
            SET picture = ?
            WHERE login = ?""", (fname, self.login))
        con.commit()
        con.close()


class TaskWindow(QWidget):
    def __init__(self, login):
        super().__init__()
        self.initUI(login)

    def initUI(self, login):
        self.login = login
        con = sqlite3.connect("exercises.db")
        cur = con.cursor()

        res = cur.execute("SELECT title FROM exercises").fetchall()
        btns = []
        layout = QFormLayout(self)
        for i in res:
            btn = QPushButton(i[0])
            btn.clicked.connect(self.Task)
            btns.append(btn)
            layout.addRow(btn)
        con.close()

    def Task(self):
        btn = self.sender().text()
        self.task = Task(btn, self.login)
        self.task.show()


class Task(QWidget):
    def __init__(self, title, login):
        super().__init__()
        self.initUI(title, login)

    def initUI(self, title, login):
        mainlayout = QVBoxLayout(self)
        self.login = login
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        result1 = cur.execute(
            "SELECT * FROM users WHERE login=?", (login,)).fetchone()
        task = result1[5].split(";")
        con.close()
        self.setWindowTitle(title)
        con = sqlite3.connect("exercises.db")
        cur = con.cursor()
        btn = QPushButton("Проверить")
        btn.clicked.connect(self.Click)
        self.label = QLabel("")
        ID = cur.execute(
            "SELECT id FROM exercises WHERE title=?", (title,)).fetchone()
        res = cur.execute(
            """SELECT task,score,test1,answer1,test2,answer2,test3,answer3 FROM exercises WHERE title=?""", (title,)).fetchone()
        a = ".\n".join(res[0].split('. '))
        self.text = QPlainTextEdit(self)
        self.list_ = [str(res[1]), title, a, self.text, self.label, btn, "Ввод 1", "Вывод 1", str(res[2]),
                      str(res[3]), "Ввод 2", "Вывод 2", str(res[4]), str(res[5])]
        layout = QHBoxLayout()
        c = 0
        for i in self.list_:
            c += 1
            if c <= 2:
                if isinstance(i, str):
                    layout.addWidget(QLabel(i))
                else:
                    layout.addWidget(i)
            if c == 2:
                mainlayout.addLayout(layout)
                layout = QHBoxLayout()
                c = 0
        con.close()
        if int(task[int(ID[0]) - 1]) != 0:
            self.label.setText(self.list_[0] + '/' + self.list_[0])
        self.ID = int(ID[0] - 1)

    def Click(self):
        a = self.text.toPlainText()
        f = open('aaa.py', 'w', encoding='utf8')
        f.write(a)
        f.close()
        text1 = "\n".join(self.list_[8].split())
        ans1 = "\n".join(self.list_[9].split())
        text2 = "\n".join(self.list_[12].split())
        ans2 = "\n".join(self.list_[13].split())
        results = [[text1, ans1], [text2, ans2]]
        flag = True
        for i in results:
            p = subprocess.Popen('aaa.py', stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, shell=True)
            p.poll()
            p.stdin.write(i[0].encode('utf-8'))
            p.stdin.close()
            answ = i[1].split()
            res = bytes.decode(p.stdout.read(), encoding='utf-8').split()
            if not (flag and answ == res):
                flag = False
                answ1 = answ
                res1 = res
                break
        if flag:
            con = sqlite3.connect("users.db")
            cur = con.cursor()
            res = cur.execute("SELECT task FROM users WHERE login=?",
                              (self.login,)).fetchone()
            res = res[0]
            task = res.split(";")
            task[self.ID] = self.list_[0]
            task = ";".join(task)
            cur.execute("UPDATE users SET task= ? WHERE login=?",
                        (task, self.login))

            self.label.setText("Points " + self.list_[0] + '/' + self.list_[0])
            con.commit()
            con.close()

        else:
            self.label.setText(
                "Wrong Answer\nПравильный ответ: " + "".join(answ1) + '\nВаш ответ: ' + "".join(res1))
            print(answ1, res1)


class MainWidgetAdmin(QWidget):
    def __init__(self, login):
        super().__init__()
        self.initUI(login)

    def initUI(self, login):
        super(MainWidgetAdmin, self).__init__()
        self.login = login
        mainlayout = QHBoxLayout(self)
        self.setWindowTitle('Главное меню')
        self.addwndw = AddWindow()
        self.setFixedSize(300, 150)
        self.btn_tsk = QPushButton("Задачи")
        self.btn_tsk.clicked.connect(self.Task)
        self.btn_tsk.setFixedSize(70, 70)

        self.btn_prfl = QPushButton(self)
        self.btn_prfl.setIcon(QIcon('профиль.png'))
        self.btn_prfl.setFixedSize(QSize(70, 70))
        self.btn_prfl.clicked.connect(self.ProfileBtn)

        self.add = QPushButton(self)
        self.add.setIcon(QIcon('плюс.png'))
        self.add.setFixedSize(QSize(70, 70))
        self.add.clicked.connect(self.Add)

        mainlayout.addWidget(self.btn_tsk)
        mainlayout.addWidget(self.add)
        mainlayout.addWidget(self.btn_prfl)

    def Task(self):
        self.tskwindow = TaskWindow(self.login)
        self.tskwindow.show()

    def ProfileBtn(self):
        self.prfl = ProfileWidget(self.login)
        self.prfl.show()

    def Add(self):
        self.addwndw.show()


class AddWindow(QWidget):
    def __init__(self):
        super(AddWindow, self).__init__()

        self.setWindowTitle("Добавить задачу")
        layout = QFormLayout(self)
        self.name = QLineEdit(self)
        layout.addRow('Название', self.name)
        self.text = QPlainTextEdit(self)
        layout.addRow('Условие задачи:\n', self.text)
        hlayout1 = QHBoxLayout()
        hlayout2 = QHBoxLayout()
        self.inps = []
        self.answs = []
        self.points = QLineEdit(self)
        for i in range(1, 4):
            inp = QLineEdit(self)
            answ = QLineEdit(self)
            self.answs.append(answ)
            self.inps.append(inp)
            label1 = QLabel(str(i) + ") ")
            label2 = QLabel(str(i) + ") ")
            hlayout1.addWidget(label1)
            hlayout1.addWidget(inp)
            hlayout2.addWidget(label2)
            hlayout2.addWidget(answ)
        btn = QPushButton("Добавить")
        btn.clicked.connect(self.Add)
        layout.addRow("Пользовательские\nтесты:", hlayout1)
        layout.addRow("Пользовательские\nответы:", hlayout2)
        layout.addRow("Количество баллов:\n", self.points)
        self.label = QLabel(self)
        layout.addRow(self.label, btn)

    def Add(self):
        list_ = []
        for i in range(3):
            list_.append(self.inps[i].text())
            list_.append(self.answs[i].text())
        flag = True
        for i in list_:
            if not i:
                flag = False
        if self.name.text() and self.text.toPlainText() and flag and self.points.text().isdigit():
            con = sqlite3.connect("exercises.db")
            cur = con.cursor()
            ids = cur.execute("SELECT id FROM exercises",).fetchall()
            ID = ids[-1][0] + 1
            cur.execute("INSERT INTO exercises VALUES(?,?,?,?,?,?,?,?,?,?)", (ID, self.name.text(
            ), self.points.text(), self.text.toPlainText(), list_[0], list_[2], list_[4], list_[1], list_[3], list_[5]))
            ids = cur.execute("SELECT * FROM exercises",).fetchall()
            con.commit()
            con.close()
            con = sqlite3.connect("users.db")
            cur = con.cursor()
            task = cur.execute("SELECT task from users").fetchone()
            right_task = task[0] + ";" + '0'
            cur.execute("UPDATE users SET task=?", (right_task,))
            con.commit()
            con.close()
        else:
            self.label.setText("Неправильный ввод")


class AuthWindow(QWidget):
    def __init__(self):
        super(AuthWindow, self).__init__()
        self.setWindowTitle('Вход')
        self.reg_window = RegistWindow()
        self.setFixedSize(300, 120)
        mainlayout = QFormLayout(self)

        self.inputlogin = QLineEdit(self)
        self.inputpassword = QLineEdit(self)

        mainlayout.addRow("логин:", self.inputlogin)
        mainlayout.addRow("пароль:", self.inputpassword)

        btn1 = QPushButton("Войти")
        btn1.clicked.connect(self.LogIn)

        btn2 = QPushButton("Зарегистрироваться")
        btn2.clicked.connect(self.Regist)

        self.text = QLabel(self)

        mainlayout.addRow(btn1, btn2)
        mainlayout.addRow(self.text)

    def LogIn(self):
        flag = False
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        login = self.inputlogin.text()
        password = self.inputpassword.text()
        result = cur.execute(
            """SELECT login,pass,level FROM users""",).fetchall()
        self.windowpupil = MainWidgetPupil(self.inputlogin.text())
        self.windowadmin = MainWidgetAdmin(self.inputlogin.text())
        for i in result:
            if i[0] == login and i[1] == password:
                if i[2] == "pupil":
                    flag = True
                    self.windowpupil.show()
                    self.text.setText("")
                    self.destroy()
                elif i[2] == "admin":
                    flag = True
                    self.windowadmin.show()
                    self.text.setText("")
                    self.destroy()
                break
        if not flag:
            self.text.setText("Неверный логин или пароль")
        else:
            self.close()

        con.close()

    def Regist(self):
        self.reg_window.show()


class RegistWindow(QWidget):
    def __init__(self):
        super(RegistWindow, self).__init__()

        mainlayout = QFormLayout(self)
        self.setFixedSize(300, 150)
        self.admin_promo = "WEQ76Y"

        self.inputlogin = QLineEdit(self)
        self.inputpassword = QLineEdit(self)
        self.inputpromo = QLineEdit(self)

        mainlayout.addRow("логин:", self.inputlogin)
        mainlayout.addRow("пароль:", self.inputpassword)
        mainlayout.addRow("промокод:", self.inputpromo)

        btn1 = QPushButton("Завершить")
        btn1.clicked.connect(self.Regist)

        self.text = QLabel(self)

        mainlayout.addRow(btn1)
        mainlayout.addRow(self.text)

    def Regist(self):
        login = self.inputlogin.text()
        password = self.inputpassword.text()
        promo = self.inputpromo.text()
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        ids = cur.execute(
            """SELECT id FROM users""",).fetchall()
        logins = cur.execute(
            """SELECT login FROM users""",).fetchall()
        loginss = []
        for i in logins:
            loginss.append(i[0])
        con.close()
        ID = 0
        for i in ids:
            if i[0] > ID:
                ID = i[0]
        ID += 1
        if promo == self.admin_promo:
            level = 'admin'
        else:
            level = 'pupil'
        list_ = [ID, login, password, "None", level]
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        if login not in loginss:
            cur.execute(
                "INSERT INTO users (id, login, pass, picture, level) VALUES (?, ?, ?, ?, ?)", (list_))
            self.close()
            self.inputlogin.setText("")
            self.inputpassword.setText("")
            self.inputpromo.setText("")
            self.text.setText('')
        else:
            self.text.setText("Логин уже занят")
        con.commit()
        con.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    wnd = AuthWindow()
    wnd.show()
    sys.exit(app.exec())
