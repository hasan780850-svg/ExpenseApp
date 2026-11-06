from datetime import datetime
import os
import sqlite3
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput

# إعداد قاعدة البيانات المحلية SQLite
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        amount REAL,
        category TEXT,
        description TEXT
    )
""")
conn.commit()


class HomeWindow(Screen):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    layout = BoxLayout(
        orientation="vertical",
        padding=30,
        spacing=20,
        pos_hint={"center_x": 0.5, "center_y": 0.5},
    )

    # عرض الصورة الشخصية إن وجدت
    if os.path.exists("profile.png"):
      self.img = Image(
          source="profile.png", size_hint=(None, None), size=(130, 130)
      )
      self.img.pos_hint = {"center_x": 0.5}
      layout.add_widget(self.img)

    title = Label(
        text="نظام إدارة المصاريف الشخصية",
        font_size=22,
        bold=True,
        color=(1, 1, 1, 1),
    )
    layout.add_widget(title)

    btn_add = Button(
        text="تسجيل مصروف جديد",
        font_size=16,
        size_hint=(1, None),
        height=50,
        background_color=(0.15, 0.68, 0.37, 1),
    )
    btn_add.bind(
        on_press=lambda x: setattr(self.manager, "current", "add_expense")
    )
    layout.add_widget(btn_add)

    btn_view = Button(
        text="سجل المصروفات",
        font_size=16,
        size_hint=(1, None),
        height=50,
        background_color=(0.2, 0.6, 0.86, 1),
    )
    btn_view.bind(
        on_press=lambda x: setattr(self.manager, "current", "view_expenses")
    )
    layout.add_widget(btn_view)

    self.add_widget(layout)


class AddExpenseWindow(Screen):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    layout = BoxLayout(
        orientation="vertical", padding=30, spacing=15, size_hint=(0.9, 0.9)
    )

    layout.add_widget(
        Label(
            text="تسجيل مصروف جديد",
            font_size=18,
            bold=True,
            color=(0.15, 0.2, 0.25, 1),
        )
    )

    # اختيار الفئة
    layout.add_widget(Label(text="الفئة:", color=(0, 0, 0, 1)))
    self.category_btn = Button(
        text="غذاء ومأكولات", size_hint=(1, None), height=45
    )
    self.dropdown = DropDown()
    categories = [
        "غذاء ومأكولات",
        "مواصلات",
        "فواتير وخدمات",
        "مصاريف منزلية",
        "شخصية",
        "أخرى",
    ]
    for cat in categories:
      btn = Button(text=cat, size_hint_y=None, height=44)
      btn.bind(
          on_release=lambda btn: self.dropdown.select(btn.text)
      )  # type: ignore
      self.dropdown.add_widget(btn)

    self.category_btn.bind(on_release=self.dropdown.open)
    self.dropdown.bind(
        on_select=lambda instance, x: setattr(self.category_btn, "text", x)
    )
    layout.add_widget(self.category_btn)

    # إدخال المبلغ
    layout.add_widget(Label(text="المبلغ:", color=(0, 0, 0, 1)))
    self.amount_input = TextInput(
        font_size=16, multiline=False, input_filter="float"
    )
    layout.add_widget(self.amount_input)

    # إدخال البيان
    layout.add_widget(Label(text="البيان (اختياري):", color=(0, 0, 0, 1)))
    self.desc_input = TextInput(font_size=16, multiline=False)
    layout.add_widget(self.desc_input)

    # أزرار الحفظ والعودة
    btn_save = Button(
        text="حفظ المصروف",
        size_hint=(1, None),
        height=50,
        background_color=(0.15, 0.68, 0.37, 1),
    )
    btn_save.bind(on_press=self.save_expense)
    layout.add_widget(btn_save)

    btn_back = Button(
        text="العودة للرئيسية",
        size_hint=(1, None),
        height=40,
        background_color=(0.5, 0.5, 0.5, 1),
    )
    btn_back.bind(
        on_press=lambda x: setattr(self.manager, "current", "home")
    )
    layout.add_widget(btn_back)

    self.add_widget(layout)

  def save_expense(self, instance):
    amt_text = self.amount_input.text.strip()
    if not amt_text:
      popup = Popup(
          title="تنبيه",
          content=Label(text="حقل المبلغ إجباري!"),
          size_hint=(0.8, 0.4),
      )
      popup.open()
      return

    try:
      amount = float(amt_text)
    except ValueError:
      return

    category = self.category_btn.text
    desc = self.desc_input.text
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute(
        "INSERT INTO expenses (date, amount, category, description) VALUES"
        " (?, ?, ?, ?)",
        (date, amount, category, desc),
    )
    conn.commit()

    self.amount_input.text = ""
    self.desc_input.text = ""
    popup = Popup(
        title="نجاح",
        content=Label(text="تمت إضافة المصروف بنجاح"),
        size_hint=(0.8, 0.4),
    )
    popup.open()


class ViewExpensesWindow(Screen):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

    btn_back = Button(
        text="← الرئيسية",
        size_hint=(None, None),
        size=(100, 40),
        background_color=(0.5, 0.5, 0.5, 1),
    )
    btn_back.bind(
        on_press=lambda x: setattr(self.manager, "current", "home")
    )
    self.layout.add_widget(btn_back)

    self.result_label = Label(
        text="جاري تحميل السجل...",
        font_size=14,
        color=(0, 0, 0, 1),
        valign="top",
    )
    self.layout.add_widget(self.result_label)

    self.add_widget(self.layout)

  def on_enter(self):
    cursor.execute("SELECT category, amount, date FROM expenses ORDER BY id DESC")
    rows = cursor.fetchall()
    total = sum(row[1] for row in rows) if rows else 0.0

    text_content = f"الإجمالي العام: {total:,.2f} ريال\n\n"
    for r in rows[:15]:  # عرض اخر 15 مصروف للتناسب مع شاشة الجوال
      text_content += f"[{r[0]}] - {r[1]:,} ريال ({r[2]})\n"

    self.result_label.text = text_content


class ExpenseApp(App):

  def build(self):
    Window.clearcolor = (0.95, 0.96, 0.97, 1)
    sm = ScreenManager()
    sm.add_widget(HomeWindow(name="home"))
    sm.add_widget(AddExpenseWindow(name="add_expense"))
    sm.add_widget(ViewExpensesWindow(name="view_expenses"))
    return sm


if __name__ == "__main__":
  ExpenseApp().run()