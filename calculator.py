import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error

def annuity_payment(principal, annual_rate, years):
    monthly_rate = annual_rate / 12 / 100
    months = years * 12
    payment = principal * monthly_rate / (1 - (1 + monthly_rate) ** -months)
    balance = principal
    schedule = []
    for m in range(1, months + 1):
        interest = balance * monthly_rate
        principal_payment = payment - interest
        balance -= principal_payment
        schedule.append([m, round(payment, 2), round(principal_payment, 2), round(interest, 2), round(max(balance, 0), 2)])
    return pd.DataFrame(schedule, columns=["Месяц", "Платеж", "Погашение тела", "Проценты", "Остаток долга"])

def differentiated_payment(principal, annual_rate, years):
    monthly_rate = annual_rate / 12 / 100
    months = years * 12
    principal_payment = principal / months
    balance = principal
    schedule = []
    for m in range(1, months + 1):
        interest = balance * monthly_rate
        payment = principal_payment + interest
        balance -= principal_payment
        schedule.append([m, round(payment, 2), round(principal_payment, 2), round(interest, 2), round(max(balance, 0), 2)])
    return pd.DataFrame(schedule, columns=["Месяц", "Платеж", "Погашение тела", "Проценты", "Остаток долга"])

def calculate():
    try:
        credit_sum = float(entry_sum.get())
        rate = float(entry_rate.get())
        years = int(entry_years.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректные числовые значения!")
        return

    annuity_df = annuity_payment(credit_sum, rate, years)
    diff_df = differentiated_payment(credit_sum, rate, years)

    total_annuity = annuity_df["Платеж"].sum()
    total_diff = diff_df["Платеж"].sum()

    # Очистка старых данных
    for tree in (tree_annuity, tree_diff):
        for i in tree.get_children():
            tree.delete(i)

    # Заполнение таблиц
    for _, row in annuity_df.iterrows():
        tree_annuity.insert("", "end", values=list(row))
    for _, row in diff_df.iterrows():
        tree_diff.insert("", "end", values=list(row))


    np.random.seed(42) # Фиксируем генератор для повторяемости
    
    # Генерация синтетических данных на основе ВВЕДЕННЫХ пользователем параметров
    # Мы создаем 1000 гипотетических кредитов вокруг введенных данных
    amounts = np.random.normal(credit_sum, credit_sum * 0.3, 1000).clip(10000) # Сумма с отклонением 30%
    rates = np.random.normal(rate, rate * 0.2, 1000).clip(1)                   # Ставка с отклонением 20%
    terms = np.random.randint(max(1, years - 2), years + 5, 1000)              # Срок от -2 до +5 лет

    # Считаем переплату для каждого сгенерированного кредита
    data = []
    for a, r, t in zip(amounts, rates, terms):
        # ВАЖНО: Мы не вызываем тяжелую функцию annuity_payment, а считаем переплату по формуле "на лету" (это намного быстрее!)
        
        # Формула аннуитетного платежа
        monthly_rate = r / 12 / 100
        months = t * 12
        payment = a * monthly_rate / (1 - (1 + monthly_rate) ** -months)
        total_payment = payment * months
        over = total_payment - a  # Это переплата
        
        # Добавляем случайный шум
        noise = np.random.normal(0, over * 0.02) 
        data.append([a, r, t, over + noise])

    df = pd.DataFrame(data, columns=['Сумма', 'Ставка_проц', 'Срок_лет', 'Переплата'])

    # ml
    X = df[['Сумма', 'Ставка_проц', 'Срок_лет']]
    y = df['Переплата']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Метрики качества
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    # Предсказание для КОНКРЕТНОГО введенного кредита
    user_prediction = model.predict([[credit_sum, rate, years]])[0]


    result_text.set(
        f"ТРАДИЦИОННЫЙ РАСЧЕТ\n"
        f"Аннуитет: общая выплата = {round(total_annuity, 2)} руб., переплата = {round(total_annuity - credit_sum, 2)} руб.\n"
        f"Дифференцированные: общая выплата = {round(total_diff, 2)} руб., переплата = {round(total_diff - credit_sum, 2)} руб.\n"
        f"Вывод: {'Дифференцированные выгоднее по переплате' if total_annuity > total_diff else 'Аннуитет удобнее для планирования'}.\n\n"
        f"ML-АНАЛИЗ (РЕГРЕССИЯ)\n"
        f"Модель обучена на 1000 синтетических кредитах.\n"
        f"Точность модели (R2-score): {r2:.4f} (чем ближе к 1, тем лучше).\n"
        f"Средняя ошибка предсказания переплаты: {mae:,.0f} руб.\n"
        f"Предсказанная переплата для вашего кредита: {round(user_prediction, 2)} руб."
    )
    print("Текст успешно сформирован!")
    print(result_text.get())

# Интерфейс 
root = tk.Tk()
root.title("Кредитный калькулятор")
root.geometry("1200x700")
root.configure(bg="#5a8945")

# Ввод данных 
frame_input = tk.Frame(root, bg="#5a8945")
frame_input.pack(pady=10)

tk.Label(frame_input, text="Сумма кредита (руб):", bg="#64a53e").grid(row=0, column=0, padx=5, pady=5)
entry_sum = tk.Entry(frame_input)
entry_sum.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_input, text="Ставка (% годовых):", bg="#64a53e").grid(row=1, column=0, padx=5, pady=5)
entry_rate = tk.Entry(frame_input)
entry_rate.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_input, text="Срок (лет):", bg="#64a53e").grid(row=2, column=0, padx=5, pady=5)
entry_years = tk.Entry(frame_input)
entry_years.grid(row=2, column=1, padx=5, pady=5)

tk.Button(frame_input, text="Рассчитать", command=calculate, bg="#4CAF50", fg="black", width=20).grid(row=3, column=0, columnspan=2, pady=10)

# Результат
result_text = tk.StringVar()
tk.Label(root, textvariable=result_text, bg="#006f09", justify="left", font=("Arial", 10, "bold"), wraplength=800).pack(pady=10)

# Таблицы 
frame_tables = tk.Frame(root, bg="#ffffff")
frame_tables.pack(fill="both", expand=True, padx=10, pady=10)

columns = ["Месяц", "Платеж", "Погашение тела", "Проценты", "Остаток долга"]

# Аннуитетная таблица
tk.Label(frame_tables, text="Аннуитетные платежи", bg="#ffffff", font=("Arial", 12, "bold")).grid(row=0, column=0)
tree_annuity = ttk.Treeview(frame_tables, columns=columns, show="headings", height=15)
for col in columns:
    tree_annuity.heading(col, text=col)
    tree_annuity.column(col, width=110)
tree_annuity.grid(row=1, column=0, padx=10)

# Дифференцированные таблица
tk.Label(frame_tables, text="Дифференцированные платежи", bg="#ffffff", font=("Arial", 12, "bold")).grid(row=0, column=1)
tree_diff = ttk.Treeview(frame_tables, columns=columns, show="headings", height=15)
for col in columns:
    tree_diff.heading(col, text=col)
    tree_diff.column(col, width=110)
tree_diff.grid(row=1, column=1, padx=10)

root.mainloop()