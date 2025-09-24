import tkinter as tk
from tkinter import ttk
import psutil
from threading import Thread
from time import sleep

class RealTimeTaskManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Монитор процессов в реальном времени")
        self.geometry("1000x600")
        
        # Верхняя панель инструментов
        toolbar_frame = tk.Frame(self)
        toolbar_frame.pack(fill='x', pady=10)
        
        # Кнопка обновления
        refresh_button = tk.Button(toolbar_frame, text="Обновить", command=self.refresh_processes)
        refresh_button.pack(side='left', padx=10)
        
        # Основная таблица процессов
        columns = ('PID', 'Имя', 'CPU%', 'Память(MB)', 'Статус')
        self.treeview = ttk.Treeview(self, columns=columns, show='headings')
        
        # Прокрутка для дерева
        scroll_y = ttk.Scrollbar(self, orient="vertical", command=self.treeview.yview)
        scroll_y.pack(side='right', fill='y')
        self.treeview.configure(yscrollcommand=scroll_y.set)
        
        # Названия столбцов таблицы
        for col in columns:
            self.treeview.heading(col, text=col)
        
        # Отображаем сетку
        self.treeview.pack(expand=True, fill='both')
        
        # Автоматический режим мониторинга
        self.monitor_running = True
        monitor_thread = Thread(target=self.auto_monitor)
        monitor_thread.daemon = True  # Поток завершится вместе с основным окном
        monitor_thread.start()
    
    def auto_monitor(self):
        while self.monitor_running:
            self.refresh_processes()
            sleep(1)  # Задержка в 1 секунду
    
    def refresh_processes(self):
        """Обновление таблицы процессов"""
        self.clear_treeview()
        processes = list(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']))
        
        for proc in processes:
            try:
                info = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_info', 'status'])
                pid = info['pid']
                name = info['name']
                cpu_usage = round(info['cpu_percent'], 2)
                memory_mb = round(info['memory_info'].rss / (1024 * 1024), 2)
                status = info['status']
                
                # Добавляем строку в таблицу
                self.add_to_table(pid, name, cpu_usage, memory_mb, status)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    
    def clear_treeview(self):
        """Очистка содержимого таблицы"""
        for item in self.treeview.get_children():
            self.treeview.delete(item)
    
    def add_to_table(self, pid, name, cpu_usage, memory_mb, status):
        """Добавляет запись в таблицу процессов"""
        self.treeview.insert("", tk.END, values=(pid, name, f"{cpu_usage}%", f"{memory_mb:.2f}", status))

# Основной запуск приложения
if __name__ == "__main__":
    app = RealTimeTaskManager()
    app.mainloop()
