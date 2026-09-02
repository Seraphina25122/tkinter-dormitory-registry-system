import tkinter as tk
from tkinter import ttk, messagebox

from utils import setup_global_font, log_operation
from data_manager import DataManager
from windows import (
    LeaveWindow,
    ReturnWindow,
    UnreturnedWindow,
    EditWindow,
    AllStudentsWindow,
    AIAssistantWindow
)


class DormitoryManagerApp:
    """宿舍离楼回楼登记管理系统主界面"""
    
    def __init__(self, root, data_manager=None):
        self.root = root
        self.root.title("宿舍离楼回楼登记管理系统")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        from utils import center_window
        center_window(self.root, 800, 600)
        self.data_manager = data_manager if data_manager else DataManager()
        self.current_building = tk.StringVar(value="全部")
        self._setup_ui()
    
    def _setup_ui(self):
        main_frame = tk.Frame(self.root, padx=50, pady=40, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.main_frame = main_frame
        
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="打开智能助手", command=self._open_ai_assistant)
        
        main_frame.bind("<Button-3>", self._show_context_menu)
        
        title_label = tk.Label(main_frame, text="宿舍离楼回楼登记管理系统", 
                              font=("Microsoft YaHei", 20, "bold"), bg="#f0f0f0")
        title_label.pack(pady=(0, 15))
        
        building_frame = tk.Frame(main_frame, bg="#f0f0f0")
        building_frame.pack(pady=(0, 10), fill=tk.X)
        tk.Label(building_frame, text="当前楼栋:", font=("Microsoft YaHei", 12), bg="#f0f0f0").pack(side=tk.LEFT, padx=(0, 10))
        self.building_combo = ttk.Combobox(building_frame, textvariable=self.current_building, 
                                           values=["全部", "1号楼", "2号楼", "3号楼", "4号楼"],
                                           state="readonly", width=15, font=("Microsoft YaHei", 12))
        self.building_combo.pack(side=tk.LEFT)
        self.building_combo.bind("<<ComboboxSelected>>", self._on_building_change)
        
        import_btn = tk.Button(building_frame, text="导入新数据", command=self._import_data,
                              font=("Microsoft YaHei", 12), width=12, height=1,
                              bg="#4CAF50", fg="white", activebackground="#45a049")
        import_btn.pack(side=tk.LEFT, padx=(20, 0))
        
        all_students_btn = tk.Button(building_frame, text="查看全部学生名单", command=self._open_all_students_window,
                              font=("Microsoft YaHei", 12), width=15, height=1,
                              bg="#2196F3", fg="white", activebackground="#1976D2")
        all_students_btn.pack(side=tk.LEFT, padx=(20, 0))
        
        self.stats_label = tk.Label(main_frame, text="总记录数: 0 | 未回楼: 0 | 已回楼: 0", 
                                   bg="#f0f0f0")
        self.stats_label.pack(pady=(0, 15), fill=tk.X)
        self._update_stats()
        
        buttons = [
            ("学生离楼登记", self._open_leave_window),
            ("学生回楼登记", self._open_return_window),
            ("未回楼学生查询", self._open_unreturned_window),
            ("修改已有记录", self._open_edit_window)
        ]
        
        for text, command in buttons:
            btn = tk.Button(main_frame, text=text, command=command,
                           font=("Microsoft YaHei", 14), width=25, height=2, padx=10, pady=5,
                           bg="#e0e0e0", activebackground="#d0d0d0")
            btn.pack(pady=10, fill=tk.X, expand=True, padx=20)
        
        import os
        footer_label = tk.Label(main_frame, text=f"数据位置: {os.path.abspath(self.data_manager.data_dir)}", 
                              font=("Microsoft YaHei", 10), fg="gray", bg="#f0f0f0")
        footer_label.pack(side=tk.BOTTOM, pady=20)
    
    def _on_building_change(self, event):
        self._update_stats()
    
    def _show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)
    
    def _open_ai_assistant(self):
        AIAssistantWindow(self.root, self.data_manager, self)
    
    def _open_all_students_window(self):
        AllStudentsWindow(self.root, self.data_manager, self.current_building.get())
    
    def _update_stats(self):
        building = self.current_building.get()
        records = self.data_manager.load_records_by_building(building)
        total = len(records)
        unreturned = sum(1 for r in records if not r.get("回楼日期") or r["回楼日期"].strip() == "")
        returned = total - unreturned
        self.stats_label.config(text=f"总记录数: {total} | 未回楼: {unreturned} | 已回楼: {returned}")
    
    def _import_data(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="选择导入文件",
            filetypes=[
                ("CSV文件", "*.csv"),
                ("Excel文件", "*.xlsx;*.xls"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        success, message, added_count, duplicate_count, invalid_count = self.data_manager.batch_import(file_path)
        
        if success:
            messagebox.showinfo("导入成功", message)
            self._update_stats()
        else:
            messagebox.showerror("导入失败", message)
    
    def _open_leave_window(self):
        LeaveWindow(self.root, self.data_manager, self.current_building.get())
        self._update_stats()
    
    def _open_return_window(self):
        ReturnWindow(self.root, self.data_manager, self.current_building.get())
        self._update_stats()
    
    def _open_unreturned_window(self):
        UnreturnedWindow(self.root, self.data_manager, self.current_building.get())
        self._update_stats()
    
    def _open_edit_window(self):
        EditWindow(self.root, self.data_manager, self.current_building.get())
        self._update_stats()


class LoginWindow(tk.Toplevel):
    """登录窗口"""
    
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.parent = parent
        self.on_success = on_success
        self.title("用户登录")
        self.geometry("600x400")
        self.resizable(False, False)
        from utils import center_window
        center_window(self, 600, 400)
        self.parent.withdraw()
        
        self.failed_attempts = 0
        self.max_attempts = 3
        self.lock_seconds = 5
        
        self._setup_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _setup_ui(self):
        frame = tk.Frame(self, padx=50, pady=30, bg="#f0f0f0")
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="用户登录", font=("Microsoft YaHei", 20, "bold"), bg="#f0f0f0").pack(pady=(0, 40))
        
        username_frame = tk.Frame(frame, bg="#f0f0f0")
        username_frame.pack(fill=tk.X, pady=15)
        tk.Label(username_frame, text="用户名:", font=("Microsoft YaHei", 14), bg="#f0f0f0", width=10).pack(side=tk.LEFT)
        self.username_entry = tk.Entry(username_frame, font=("Microsoft YaHei", 14), width=25)
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        password_frame = tk.Frame(frame, bg="#f0f0f0")
        password_frame.pack(fill=tk.X, pady=15)
        tk.Label(password_frame, text="密码:", font=("Microsoft YaHei", 14), bg="#f0f0f0", width=10).pack(side=tk.LEFT)
        self.password_entry = tk.Entry(password_frame, font=("Microsoft YaHei", 14), width=25, show="*")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.error_label = tk.Label(frame, text="", font=("Microsoft YaHei", 12), fg="red", bg="#f0f0f0")
        self.error_label.pack(pady=10)
        
        self.login_btn = tk.Button(frame, text="登录", command=self._on_login,
                                   font=("Microsoft YaHei", 16), width=12, height=2,
                                   bg="#4CAF50", fg="white", activebackground="#45a049")
        self.login_btn.pack(pady=30)
    
    def _on_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("提示", "用户名和密码不能为空！")
            return
        
        if username == "admin" and password == "123456":
            self._log_event("成功", "登录成功")
            self.parent.deiconify()
            self.destroy()
            self.on_success()
        else:
            self.failed_attempts += 1
            remaining = self.max_attempts - self.failed_attempts
            
            if self.failed_attempts >= self.max_attempts:
                self._log_event("失败", f"登录失败，连续失败{self.max_attempts}次，账号已锁定")
                self._lock_account()
            else:
                self._log_event("失败", f"登录失败，用户名或密码错误")
                messagebox.showwarning("登录失败", f"登录失败，还剩{remaining}次机会")
    
    def _lock_account(self):
        self.username_entry.config(state=tk.DISABLED)
        self.password_entry.config(state=tk.DISABLED)
        self.login_btn.config(state=tk.DISABLED)
        
        self.error_label.config(text=f"登录失败次数过多，已锁定{self.lock_seconds}秒")
        
        self._update_lock_timer(self.lock_seconds)
    
    def _update_lock_timer(self, seconds_left):
        if seconds_left > 0:
            self.error_label.config(text=f"登录失败次数过多，已锁定，还剩{seconds_left}秒解锁")
            self.login_btn.config(text=f"锁定{seconds_left}秒")
            self.after(1000, lambda: self._update_lock_timer(seconds_left - 1))
        else:
            self._unlock_account()
    
    def _unlock_account(self):
        self.failed_attempts = 0
        self.username_entry.config(state=tk.NORMAL)
        self.password_entry.config(state=tk.NORMAL)
        self.login_btn.config(state=tk.NORMAL)
        self.login_btn.config(text="登录")
        self.error_label.config(text="")
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
    
    def _log_event(self, status, detail):
        log_operation(status, detail)
    
    def _on_close(self):
        self.parent.destroy()
        self.destroy()


def main():
    setup_global_font()
    
    root = tk.Tk()
    root.option_add("*Font", ("Microsoft YaHei", 12)) 
    
    data_manager = DataManager()
    
    def on_login_success():
        app = DormitoryManagerApp(root, data_manager)
        AIAssistantWindow(root, data_manager, app)
    
    LoginWindow(root, on_login_success)
    root.mainloop()


if __name__ == "__main__":
    main()
