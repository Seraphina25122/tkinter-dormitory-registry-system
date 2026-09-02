import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import csv
import webbrowser

from utils import center_window, is_valid_date, is_return_date_valid, validate_student_data, log_operation
from config import STUDENT_LIST, BUILDING_LIST


class DatePicker(tk.Toplevel):
    """日期选择器弹窗"""
    
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("选择日期")
        self.geometry("600x400")
        center_window(self, 600, 400)
        self.resizable(False, False)
        self._setup_ui()
    
    def _setup_ui(self):
        today = datetime.date.today()
        self.year = tk.IntVar(value=today.year)
        self.month = tk.IntVar(value=today.month)
        self.day = tk.IntVar(value=today.day)
        
        frame = tk.Frame(self, padx=30, pady=30)
        frame.pack(fill=tk.BOTH, expand=True)
        
        year_frame = tk.Frame(frame)
        year_frame.pack(fill=tk.X, pady=8)
        tk.Label(year_frame, text="年份:", font=("Microsoft YaHei", 14), width=8).pack(side=tk.LEFT)
        tk.Spinbox(year_frame, from_=2020, to=2030, textvariable=self.year, 
                   font=("Microsoft YaHei", 14), width=12).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        month_frame = tk.Frame(frame)
        month_frame.pack(fill=tk.X, pady=8)
        tk.Label(month_frame, text="月份:", font=("Microsoft YaHei", 14), width=8).pack(side=tk.LEFT)
        tk.Spinbox(month_frame, from_=1, to=12, textvariable=self.month, 
                   font=("Microsoft YaHei", 14), width=12).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        day_frame = tk.Frame(frame)
        day_frame.pack(fill=tk.X, pady=8)
        tk.Label(day_frame, text="日期:", font=("Microsoft YaHei", 14), width=8).pack(side=tk.LEFT)
        tk.Spinbox(day_frame, from_=1, to=31, textvariable=self.day, 
                   font=("Microsoft YaHei", 14), width=12).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="确定", command=self._on_ok, 
                  font=("Microsoft YaHei", 14), width=25, height=2, padx=10, pady=5,
                  bg="#e0e0e0", activebackground="#d0d0d0").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="今天", command=self._on_today, 
                  font=("Microsoft YaHei", 14), width=25, height=2, padx=10, pady=5,
                  bg="#e0e0e0", activebackground="#d0d0d0").pack(side=tk.LEFT, padx=10)
    
    def _on_ok(self):
        try:
            date_str = f"{self.year.get()}-{self.month.get():02d}-{self.day.get():02d}"
            datetime.date(self.year.get(), self.month.get(), self.day.get())
            self.callback(date_str)
            self.destroy()
        except ValueError:
            messagebox.showerror("错误", "日期无效，请重新选择！")
    
    def _on_today(self):
        today = datetime.date.today()
        date_str = today.strftime("%Y-%m-%d")
        self.callback(date_str)
        self.destroy()


class LeaveWindow(tk.Toplevel):
    """学生离楼登记窗口"""
    
    def __init__(self, parent, data_manager, current_building="全部"):
        super().__init__(parent)
        self.data_manager = data_manager
        self.title("学生离楼登记")
        self.geometry("500x520")
        self.resizable(False, False)
        center_window(self, 500, 520)
        self.default_building = current_building if current_building != "全部" else "1号楼"
        self._setup_ui()
    
    def _setup_ui(self):
        frame = tk.Frame(self, padx=40, pady=30)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="学生离楼登记", font=("Microsoft YaHei", 18, "bold")).pack(pady=(0, 30))
        
        building_frame = tk.Frame(frame)
        building_frame.pack(fill=tk.X, pady=10)
        tk.Label(building_frame, text="楼栋:", font=("Microsoft YaHei", 14), width=10).pack(side=tk.LEFT)
        self.building_combo = ttk.Combobox(building_frame, values=["1号楼", "2号楼", "3号楼", "4号楼"],
                                           state="readonly", width=20, font=("Microsoft YaHei", 14))
        self.building_combo.set(self.default_building)
        self.building_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.entries = {}
        fields = ["姓名", "寝室号", "床位号", "离楼日期", "备注"]
        
        for field in fields:
            field_frame = tk.Frame(frame)
            field_frame.pack(fill=tk.X, pady=10)
            
            tk.Label(field_frame, text=f"{field}:", font=("Microsoft YaHei", 14), width=10).pack(side=tk.LEFT)
            
            if field == "离楼日期":
                date_frame = tk.Frame(field_frame)
                date_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                self.entries[field] = tk.Entry(date_frame, font=("Microsoft YaHei", 14), width=18)
                self.entries[field].pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
                self.entries[field].insert(0, datetime.date.today().strftime("%Y-%m-%d"))
                
                tk.Button(date_frame, text="选择日期", command=lambda f=field: self._pick_date(f),
                         font=("Microsoft YaHei", 12), width=10, height=1).pack(side=tk.LEFT)
            else:
                self.entries[field] = tk.Entry(field_frame, font=("Microsoft YaHei", 14), width=25)
                self.entries[field].pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=(20, 25))
        
        tk.Button(button_frame, text="确认登记", command=self._on_submit,
                 font=("Microsoft YaHei", 14), width=15, height=2, padx=10, pady=5,
                 bg="#e0e0e0", activebackground="#d0d0d0").pack(side=tk.LEFT, padx=15)
        tk.Button(button_frame, text="取消", command=self.destroy,
                 font=("Microsoft YaHei", 14), width=15, height=2, padx=10, pady=5,
                 bg="#e0e0e0", activebackground="#d0d0d0").pack(side=tk.LEFT, padx=15)
    
    def _pick_date(self, field):
        def set_date(date_str):
            self.entries[field].delete(0, tk.END)
            self.entries[field].insert(0, date_str)
        DatePicker(self, set_date)
    
    def _on_submit(self):
        name = self.entries["姓名"].get().strip()
        building = self.building_combo.get()
        dorm_room = self.entries["寝室号"].get().strip()
        bed = self.entries["床位号"].get().strip()
        leave_date = self.entries["离楼日期"].get().strip()
        remark = self.entries["备注"].get().strip()
        
        if not all([building, name, dorm_room, bed, leave_date]):
            messagebox.showwarning("警告", "请填写完整必填信息（楼栋、姓名、寝室号、床位号、离楼日期）！")
            return
            
        if not is_valid_date(leave_date):
            messagebox.showwarning("警告", "离楼日期格式无效，请确保使用 YYYY-MM-DD 格式且日期真实存在！")
            return
        
        is_valid, msg, suggestion = validate_student_data(name, building, dorm_room, bed)
        
        if not is_valid:
            if "警告：此条数据不属于名单！" in msg:
                messagebox.showwarning("警告", msg)
                return
            else:
                result = messagebox.askyesno("确认", msg + "\n\n是否使用建议值？")
                if result and suggestion:
                    if "楼栋" in suggestion:
                        building = suggestion["楼栋"]
                        self.building_combo.set(suggestion["楼栋"])
                    if "寝室号" in suggestion:
                        dorm_room = suggestion["寝室号"]
                        self.entries["寝室号"].delete(0, tk.END)
                        self.entries["寝室号"].insert(0, suggestion["寝室号"])
                    if "床位号" in suggestion:
                        bed = suggestion["床位号"]
                        self.entries["床位号"].delete(0, tk.END)
                        self.entries["床位号"].insert(0, suggestion["床位号"])
        
        records = self.data_manager.load_records()
        key = f"{building}_{dorm_room}_{bed}"
        
        found_index = -1
        for i, record in enumerate(records):
            if f"{record['楼栋']}_{record['寝室号']}_{record['床位号']}" == key:
                found_index = i
                break
        
        if found_index >= 0:
            record = records[found_index]
            record["离楼日期"] = leave_date
            record["回楼日期"] = ""
            record["备注"] = remark
            self.data_manager.update_record(found_index, record)
            messagebox.showinfo("成功", "离楼登记成功！学生已标记为未回楼状态！")
        else:
            record = {
                "楼栋": building,
                "姓名": name,
                "寝室号": dorm_room,
                "床位号": bed,
                "离楼日期": leave_date,
                "回楼日期": "",
                "备注": remark
            }
            self.data_manager.add_record(record)
            messagebox.showinfo("成功", "离楼登记成功！学生已标记为未回楼状态！")
        
        self.destroy()


class ReturnWindow(tk.Toplevel):
    """学生回楼登记窗口"""
    
    def __init__(self, parent, data_manager, current_building="全部"):
        super().__init__(parent)
        self.data_manager = data_manager
        self.title("学生回楼登记")
        self.geometry("700x720")
        self.resizable(False, False)
        center_window(self, 700, 720)
        self.current_filter = ""
        self.current_building = current_building
        self._setup_ui()
    
    def _setup_ui(self):
        frame = tk.Frame(self, padx=30, pady=25)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="学生回楼登记", font=("Microsoft YaHei", 18, "bold")).pack(pady=(0, 20))
        
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("楼栋", "姓名", "寝室号", "床位号", "离楼日期")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Microsoft YaHei", 12))
        style.configure("Treeview", font=("Microsoft YaHei", 12), rowheight=30)
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = 80 if col == "楼栋" else 130
            self.tree.column(col, width=width, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self._load_unreturned()
        
        date_frame = tk.Frame(frame)
        date_frame.pack(pady=15)
        
        tk.Label(date_frame, text="回楼日期:", font=("Microsoft YaHei", 14)).pack(side=tk.LEFT, padx=(0, 10))
        self.return_date = tk.Entry(date_frame, font=("Microsoft YaHei", 14), width=18)
        self.return_date.pack(side=tk.LEFT, padx=(0, 10))
        self.return_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        tk.Button(date_frame, text="选择日期", command=self._pick_date,
                 font=("Microsoft YaHei", 12), width=10, height=1).pack(side=tk.LEFT)
        
        filter_frame = tk.Frame(frame)
        filter_frame.pack(pady=10)
        
        tk.Label(filter_frame, text="筛选离楼日期:", font=("Microsoft YaHei", 14)).pack(side=tk.LEFT, padx=(0, 10))
        self.filter_date = tk.Entry(filter_frame, font=("Microsoft YaHei", 14), width=18)
        self.filter_date.pack(side=tk.LEFT, padx=(0, 10))
        self.filter_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        tk.Button(filter_frame, text="选择日期", command=lambda: self._pick_filter_date(self.filter_date),
                 font=("Microsoft YaHei", 12), width=10, height=1).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(filter_frame, text="筛选", command=self._filter_records,
                 font=("Microsoft YaHei", 12), width=8, height=1).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(filter_frame, text="重置", command=self._reset_filter,
                 font=("Microsoft YaHei", 12), width=8, height=1).pack(side=tk.LEFT, padx=(0, 10))

        button_frame = tk.Frame(frame)
        button_frame.pack(pady=15)
        
        tk.Button(button_frame, text="确认回楼", command=self._on_submit,
                 font=("Microsoft YaHei", 14), width=15, height=2, padx=10, pady=5,
                 bg="#e0e0e0", activebackground="#d0d0d0").pack(side=tk.LEFT, padx=12)
        tk.Button(button_frame, text="刷新", command=self._load_unreturned,
                 font=("Microsoft YaHei", 14), width=15, height=2, padx=10, pady=5,
                 bg="#e0e0e0", activebackground="#d0d0d0").pack(side=tk.LEFT, padx=12)
        tk.Button(button_frame, text="关闭", command=self.destroy,
                 font=("Microsoft YaHei", 14), width=15, height=2, padx=10, pady=5,
                 bg="#e0e0e0", activebackground="#d0d0d0").pack(side=tk.LEFT, padx=12)
    
    def _load_unreturned(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        records = self.data_manager.load_records()
        for i, record in enumerate(records):
            if not record.get("回楼日期") or record["回楼日期"].strip() == "":
                if self.current_filter and record["离楼日期"] != self.current_filter:
                    continue
                if self.current_building != "全部" and record.get("楼栋") != self.current_building:
                    continue
                self.tree.insert("", tk.END, iid=str(i), values=(
                    record.get("楼栋", "1号楼"),
                    record["姓名"], 
                    record["寝室号"], 
                    record["床位号"], 
                    record["离楼日期"]
                ))
    
    def _pick_date(self):
        def set_date(date_str):
            self.return_date.delete(0, tk.END)
            self.return_date.insert(0, date_str)
        DatePicker(self, set_date)

    def _pick_filter_date(self, entry_widget):
        def set_date(date_str):
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, date_str)
        DatePicker(self, set_date)

    def _filter_records(self):
        self.current_filter = self.filter_date.get().strip()
        self._load_unreturned()

    def _reset_filter(self):
        self.current_filter = ""
        self.filter_date.delete(0, tk.END)
        self.filter_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self._load_unreturned()
    
    def _on_submit(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要登记回楼的学生！")
            return
        
        return_date_str = self.return_date.get().strip()
        if not return_date_str:
            messagebox.showwarning("警告", "请填写回楼日期！")
            return
        if not is_valid_date(return_date_str):
            messagebox.showwarning("警告", "回楼日期格式无效，请确保使用 YYYY-MM-DD 格式且日期真实存在！")
            return
        
        success_count = 0
        fail_count = 0
        records = self.data_manager.load_records()
        
        for selected_item in selected:
            index = int(selected_item)
            
            if 0 <= index < len(records):
                record = records[index]
                
                leave_date = record["离楼日期"]
                valid, msg = is_return_date_valid(leave_date, return_date_str)
                if not valid:
                    fail_count += 1
                    continue
                
                record["回楼日期"] = return_date_str
                self.data_manager.update_record(index, record)
                success_count += 1
        
        if success_count > 0:
            messagebox.showinfo("成功", f"回楼登记成功！{success_count}名学生已标记为已回楼状态！")
        if fail_count > 0:
            messagebox.showwarning("警告", f"有{fail_count}名学生回楼日期无效，未完成登记！")
        
        self._load_unreturned()


class UnreturnedWindow(tk.Toplevel):
    """未回楼学生查询窗口"""
    
    def __init__(self, parent, data_manager, current_building="全部"):
        super().__init__(parent)
        self.data_manager = data_manager
        self.title("未回楼学生查询")
        self.geometry("750x680")
        self.resizable(False, False)
        center_window(self, 750, 680)
        self.current_filter = ""
        self.search_keyword = ""
        self.sort_column = None
        self.sort_ascending = True
        self.current_building = current_building
        self._setup_ui()
    
    def _setup_ui(self):
        frame = tk.Frame(self, padx=30, pady=25)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="未回楼学生列表", font=("Microsoft YaHei", 18, "bold")).pack(pady=(0, 15))
        
        search_frame = tk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(search_frame, text="搜索:", font=("Microsoft YaHei", 12)).pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry = tk.Entry(search_frame, font=("Microsoft YaHei", 12), width=30)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("楼栋", "姓名", "寝室号", "床位号", "离楼日期", "备注")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12, selectmode="extended")
        
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Microsoft YaHei", 12))
        style.configure("Treeview", font=("Microsoft YaHei", 12), rowheight=30)
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self._on_sort(c))
            width = 80 if col == "楼栋" else 130
            self.tree.column(col, width=width, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Button-1>", self._on_click)
        
        self._load_unreturned()
        
        filter_frame = tk.Frame(frame)
        filter_frame.pack(pady=15)
        
        tk.Label(filter_frame, text="筛选离楼日期:", font=("Microsoft YaHei", 14)).pack(side=tk.LEFT, padx=(0, 10))
        self.filter_date = tk.Entry(filter_frame, font=("Microsoft YaHei", 14), width=18)
        self.filter_date.pack(side=tk.LEFT, padx=(0, 10))
        self.filter_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        tk.Button(filter_frame, text="选择日期", command=lambda: self._pick_filter_date(self.filter_date),
                 font=("Microsoft YaHei", 12), width=10, height=1).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(filter_frame, text="筛选", command=self._filter_records,
                 font=("Microsoft YaHei", 12), width=8, height=1).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(filter_frame, text="重置", command=self._reset_filter,
                 font=("Microsoft YaHei", 12), width=8, height=1).pack(side=tk.LEFT)

        button_frame = tk.Frame(frame)
        button_frame.pack(pady=(15, 20))

        self.contact_btn = tk.Button(button_frame, text="联系辅导员", command=self._contact_counselor,
                 font=("Microsoft YaHei", 14), width=15, height=2, padx=10, pady=5,
                 bg="#e0e0e0", activebackground="#d0d0d0", state=tk.DISABLED)
        self.contact_btn.pack(side=tk.LEFT, padx=12)

        tk.Button(button_frame, text="关闭", command=self.destroy,
                 font=("Microsoft YaHei", 14), width=15, height=2, padx=10, pady=5,
                 bg="#e0e0e0", activebackground="#d0d0d0").pack(side=tk.LEFT, padx=12)
    
    def _load_unreturned(self):
        selected_ids = set(self.tree.selection())
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        records = self.data_manager.load_records()
        
        self.tree.tag_configure("unreturned", background="#FFFF00")
        
        unreturned_list = []
        for i, record in enumerate(records):
            is_unreturned = not record.get("回楼日期") or record["回楼日期"].strip() == ""
            
            if is_unreturned:
                if self.current_building != "全部" and record.get("楼栋") != self.current_building:
                    continue
                
                if self.search_keyword:
                    keyword = self.search_keyword.strip()
                    match = False
                    
                    if keyword.endswith("号楼"):
                        if keyword == record.get("楼栋", ""):
                            match = True
                    elif len(keyword) == 1 and keyword.isdigit():
                        if keyword == record.get("床位号", ""):
                            match = True
                    elif keyword.isdigit():
                        if keyword in record.get("寝室号", ""):
                            match = True
                    else:
                        if keyword in record.get("姓名", ""):
                            match = True
                    
                    if not match:
                        continue
                
                unreturned_list.append((i, record))
        
        if self.sort_column:
            unreturned_list.sort(key=lambda x: x[1].get(self.sort_column, ""), reverse=not self.sort_ascending)
        
        for i, record in unreturned_list:
            self.tree.insert("", tk.END, iid=str(i), values=(
                record.get("楼栋", ""),
                record.get("姓名", ""),
                record.get("寝室号", ""),
                record.get("床位号", ""),
                record.get("离楼日期", ""),
                record.get("备注", "")
            ), tags=("unreturned",))
        
        for item_id in selected_ids:
            if item_id in self.tree.get_children():
                self.tree.selection_add(item_id)

    def _pick_filter_date(self, entry_widget):
        def set_date(date_str):
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, date_str)
        DatePicker(self, set_date)

    def _filter_records(self):
        self.current_filter = self.filter_date.get().strip()
        self._load_unreturned()

    def _reset_filter(self):
        self.current_filter = ""
        self.filter_date.delete(0, tk.END)
        self.filter_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self._load_unreturned()
    
    def _on_sort(self, column):
        if self.sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column
            self.sort_ascending = True
        self._load_unreturned()
    
    def _on_search(self, event):
        self.search_keyword = self.search_entry.get().strip()
        self._load_unreturned()

    def _on_select(self, event):
        if len(self.tree.selection()) >= 1:
            self.contact_btn.config(state=tk.NORMAL)
        else:
            self.contact_btn.config(state=tk.DISABLED)
    
    def _on_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            if item_id in self.tree.selection():
                self.tree.selection_remove(item_id)
            else:
                self.tree.selection_add(item_id)
        return "break"
    
    def _contact_counselor(self):
        dialog = tk.Toplevel(self)
        dialog.title("联系辅导员")
        dialog.geometry("300x250")
        dialog.resizable(False, False)
        center_window(dialog, 300, 250)
        
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="请选择联系方式：", font=("Microsoft YaHei", 14)).pack(pady=(0, 15))
        
        def phone_contact():
            dialog.clipboard_clear()
            dialog.clipboard_append("13800138000")
            messagebox.showinfo("提示", "辅导员电话已复制到剪贴板，可直接粘贴使用！")
        
        def wechat_contact():
            webbrowser.open("https://u.wechat.com/")
            messagebox.showinfo("提示", "已为您打开微信添加好友页面，请按提示添加辅导员微信")
        
        tk.Button(frame, text="电话联系", command=phone_contact,
                  font=("Microsoft YaHei", 14), width=25, height=2, padx=10, pady=5,
                  bg="#e0e0e0", activebackground="#d0d0d0").pack(pady=5)
        tk.Button(frame, text="微信联系", command=wechat_contact,
                  font=("Microsoft YaHei", 14), width=25, height=2, padx=10, pady=5,
                  bg="#e0e0e0", activebackground="#d0d0d0").pack(pady=5)
        tk.Button(frame, text="关闭", command=dialog.destroy,
                  font=("Microsoft YaHei", 14), width=25, height=2, padx=10, pady=5,
                  bg="#e0e0e0", activebackground="#d0d0d0").pack(pady=10)


class EditWindow(tk.Toplevel):
    """修改记录窗口"""
    
    def __init__(self, parent, data_manager, current_building="全部"):
        super().__init__(parent)
        self.data_manager = data_manager
        self.title("修改已有记录")
        self.geometry("850x750")
        self.resizable(False, False)
        center_window(self, 850, 750)
        self.current_filter = ""
        self.current_building = current_building
        self._setup_ui()
    
    def _setup_ui(self):
        frame = tk.Frame(self, padx=30, pady=25)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="修改已有记录", font=("Microsoft YaHei", 18, "bold")).pack(pady=(0, 20))
        
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("楼栋", "姓名", "寝室号", "床位号", "离楼日期", "回楼日期", "备注")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Microsoft YaHei", 12))
        style.configure("Treeview", font=("Microsoft YaHei", 12), rowheight=30)
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = 80 if col == "楼栋" else 120
            self.tree.column(col, width=width, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self._load_records()
        
        filter_frame = tk.Frame(frame)
        filter_frame.pack(pady=15)
        
        tk.Label(filter_frame, text="筛选离楼日期:", font=("Microsoft YaHei", 14)).pack(side=tk.LEFT, padx=(0, 10))
        self.filter_date = tk.Entry(filter_frame, font=("Microsoft YaHei", 14), width=18)
        self.filter_date.pack(side=tk.LEFT, padx=(0, 10))
        self.filter_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        tk.Button(filter_frame, text="选择日期", command=lambda: self._pick_filter_date(self.filter_date),
                 font=("Microsoft YaHei", 12), width=10, height=1).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(filter_frame, text="筛选", command=self._filter_records,
                 font=("Microsoft YaHei", 12), width=8, height=1).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(filter_frame, text="重置", command=self._reset_filter,
                 font=("Microsoft YaHei", 12), width=8, height=1).pack(side=tk.LEFT)

        button_frame = tk.Frame(frame)
        button_frame.pack(pady=15)
        
        tk.Button(button_frame, text="修改选中", command=self._edit_record,
                 font=("Microsoft YaHei", 14), width=15, height=2, padx=10, pady=5,
                 bg="#e0e0e0", activebackground="#d0d0d0").pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="删除选中", command=self._delete_record,
                 font=("Microsoft YaHei", 14), width=15, height=2, padx=10, pady=5,
                 bg="#e0e0e0", activebackground="#d0d0d0").pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="刷新", command=self._load_records,
                 font=("Microsoft YaHei", 14), width=15, height=2, padx=10, pady=5,
                 bg="#e0e0e0", activebackground="#d0d0d0").pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="关闭", command=self.destroy,
                 font=("Microsoft YaHei", 14), width=15, height=2, padx=10, pady=5,
                 bg="#e0e0e0", activebackground="#d0d0d0").pack(side=tk.LEFT, padx=12)
    
    def _load_records(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        records = self.data_manager.load_records()
        for i, record in enumerate(records):
            if self.current_filter and record["离楼日期"] != self.current_filter:
                continue
            if self.current_building != "全部" and record.get("楼栋") != self.current_building:
                continue
            self.tree.insert("", tk.END, iid=str(i), values=(
                record.get("楼栋", "1号楼"),
                record["姓名"], 
                record["寝室号"], 
                record["床位号"], 
                record["离楼日期"], 
                record["回楼日期"], 
                record["备注"]
            ))

    def _pick_filter_date(self, entry_widget):
        def set_date(date_str):
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, date_str)
        DatePicker(self, set_date)

    def _filter_records(self):
        self.current_filter = self.filter_date.get().strip()
        self._load_records()

    def _reset_filter(self):
        self.current_filter = ""
        self.filter_date.delete(0, tk.END)
        self.filter_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self._load_records()
    
    def _edit_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要修改的记录！")
            return
        
        selected_item = selected[0]
        index = int(selected_item)
        records = self.data_manager.load_records()
        
        if 0 <= index < len(records):
            self._open_edit_dialog(index, records[index])
    
    def _open_edit_dialog(self, index, record):
        dialog = tk.Toplevel(self)
        dialog.title("修改记录")
        dialog.geometry("520x600")
        dialog.resizable(False, False)
        center_window(dialog, 520, 600)
        
        frame = tk.Frame(dialog, padx=40, pady=30)
        frame.pack(fill=tk.BOTH, expand=True)
        
        entries = {}
        fields = ["楼栋", "姓名", "寝室号", "床位号", "离楼日期", "回楼日期", "备注"]
        
        for field in fields:
            field_frame = tk.Frame(frame)
            field_frame.pack(fill=tk.X, pady=10)
            
            tk.Label(field_frame, text=f"{field}:", font=("Microsoft YaHei", 14), width=10).pack(side=tk.LEFT)
            
            if field == "楼栋":
                entries[field] = ttk.Combobox(field_frame, values=["1号楼", "2号楼", "3号楼", "4号楼"],
                                              state="readonly", width=20, font=("Microsoft YaHei", 14))
                entries[field].pack(side=tk.LEFT, fill=tk.X, expand=True)
                entries[field].set(record.get(field, "1号楼"))
            elif field in ["离楼日期", "回楼日期"]:
                date_frame = tk.Frame(field_frame)
                date_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                entries[field] = tk.Entry(date_frame, font=("Microsoft YaHei", 14), width=18)
                entries[field].pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
                entries[field].insert(0, record.get(field, ""))
                
                def make_pick_date(f):
                    return lambda: self._pick_date_for_dialog(entries, f, dialog)
                
                tk.Button(date_frame, text="选择", command=make_pick_date(field),
                         font=("Microsoft YaHei", 12), width=8, height=1).pack(side=tk.LEFT)
            else:
                entries[field] = tk.Entry(field_frame, font=("Microsoft YaHei", 14), width=25)
                entries[field].pack(side=tk.LEFT, fill=tk.X, expand=True)
                entries[field].insert(0, record.get(field, ""))
        
        def on_save():
            new_record = {f: entries[f].get().strip() for f in fields}
            
            if not all([new_record["楼栋"], new_record["姓名"], new_record["寝室号"], new_record["床位号"], new_record["离楼日期"]]):
                messagebox.showwarning("警告", "请填写完整必填信息（楼栋、姓名、寝室号、床位号、离楼日期）！")
                return
                
            if not is_valid_date(new_record["离楼日期"]):
                messagebox.showwarning("警告", "离楼日期格式无效，请确保使用 YYYY-MM-DD 格式且日期真实存在！")
                return
            if new_record["回楼日期"] and not is_valid_date(new_record["回楼日期"]):
                messagebox.showwarning("警告", "回楼日期格式无效，请确保使用 YYYY-MM-DD 格式且日期真实存在！")
                return
            
            if new_record["回楼日期"]:
                valid, msg = is_return_date_valid(new_record["离楼日期"], new_record["回楼日期"])
                if not valid:
                    messagebox.showwarning("警告", msg)
                    return

            if messagebox.askyesno("确认", "确定要修改这条记录吗？"):
                self.data_manager.update_record(index, new_record)
                messagebox.showinfo("成功", "记录修改成功！")
                self._load_records()
                dialog.destroy()
        
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=30)
        
        tk.Button(button_frame, text="保存", command=on_save,
                 font=("Microsoft YaHei", 14), width=25, height=2, padx=10, pady=5,
                 bg="#e0e0e0", activebackground="#d0d0d0").pack(side=tk.LEFT, padx=15)
        tk.Button(button_frame, text="取消", command=dialog.destroy,
                 font=("Microsoft YaHei", 14), width=25, height=2, padx=10, pady=5,
                 bg="#e0e0e0", activebackground="#d0d0d0").pack(side=tk.LEFT, padx=15)
    
    def _pick_date_for_dialog(self, entries, field, parent):
        def set_date(date_str):
            entries[field].delete(0, tk.END)
            entries[field].insert(0, date_str)
        DatePicker(parent, set_date)
    
    def _delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的记录！")
            return
        
        if not messagebox.askyesno("确认", "确定要删除这条记录吗？此操作不可恢复！"):
            return
        
        selected_item = selected[0]
        index = int(selected_item)
        
        self.data_manager.delete_record(index)
        messagebox.showinfo("成功", "记录删除成功！")
        self._load_records()


class AllStudentsWindow(tk.Toplevel):
    """查看全部学生名单窗口"""
    
    def __init__(self, parent, data_manager, current_building="全部"):
        super().__init__(parent)
        self.data_manager = data_manager
        self.title("全部学生名单")
        self.geometry("750x680")
        self.resizable(False, False)
        center_window(self, 750, 680)
        self.current_building = current_building
        self.search_keyword = ""
        self.sort_column = None
        self.sort_ascending = True
        self._setup_ui()
    
    def _setup_ui(self):
        frame = tk.Frame(self, padx=30, pady=25)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="全部学生名单", font=("Microsoft YaHei", 18, "bold")).pack(pady=(0, 15))
        
        search_frame = tk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(search_frame, text="搜索:", font=("Microsoft YaHei", 12)).pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry = tk.Entry(search_frame, font=("Microsoft YaHei", 12), width=30)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("楼栋", "姓名", "寝室号", "床位号", "离楼日期", "状态")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Microsoft YaHei", 12))
        style.configure("Treeview", font=("Microsoft YaHei", 12), rowheight=30)
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self._on_sort(c))
            width = 80 if col == "楼栋" else 120
            self.tree.column(col, width=width, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self._load_all_students()
        
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=(15, 20))

        tk.Button(button_frame, text="刷新", command=self._load_all_students,
                 font=("Microsoft YaHei", 14), width=15, height=2, padx=10, pady=5,
                 bg="#e0e0e0", activebackground="#d0d0d0").pack(side=tk.LEFT, padx=12)
        
        tk.Button(button_frame, text="关闭", command=self.destroy,
                 font=("Microsoft YaHei", 14), width=15, height=2, padx=10, pady=5,
                 bg="#e0e0e0", activebackground="#d0d0d0").pack(side=tk.LEFT, padx=12)
    
    def _load_all_students(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.tree.tag_configure("unreturned", background="#FFFF00")
        self.tree.tag_configure("returned", background="#FFFFFF")
        
        all_students = []
        
        for student in STUDENT_LIST:
            all_students.append(student)
        
        records = self.data_manager.load_records()
        record_index = {}
        for i, record in enumerate(records):
            key = f"{record['楼栋']}_{record['寝室号']}_{record['床位号']}"
            record_index[key] = (i, record)
            
            found_in_list = False
            for student in STUDENT_LIST:
                if f"{student['楼栋']}_{student['寝室号']}_{student['床位号']}" == key:
                    found_in_list = True
                    break
            
            if not found_in_list:
                new_student = {
                    "楼栋": record["楼栋"],
                    "姓名": record["姓名"],
                    "寝室号": record["寝室号"],
                    "床位号": record["床位号"]
                }
                already_added = False
                for s in all_students:
                    if f"{s['楼栋']}_{s['寝室号']}_{s['床位号']}" == key:
                        already_added = True
                        break
                if not already_added:
                    all_students.append(new_student)
        
        filtered_students = []
        for student in all_students:
            if self.current_building != "全部" and student["楼栋"] != self.current_building:
                continue
            
            if self.search_keyword:
                keyword = self.search_keyword.strip()
                match = False
                
                if keyword.endswith("号楼"):
                    if keyword == student["楼栋"]:
                        match = True
                elif len(keyword) == 1 and keyword.isdigit():
                    if keyword == student["床位号"]:
                        match = True
                elif keyword.isdigit():
                    if keyword in student["寝室号"]:
                        match = True
                else:
                    if keyword in student["姓名"]:
                        match = True
                
                if not match:
                    continue
            
            filtered_students.append(student)
        
        if self.sort_column:
            filtered_students.sort(key=lambda x: x.get(self.sort_column, ""), reverse=not self.sort_ascending)
        
        for student in filtered_students:
            key = f"{student['楼栋']}_{student['寝室号']}_{student['床位号']}"
            
            if key in record_index:
                i, record = record_index[key]
                is_unreturned = not record.get("回楼日期") or record["回楼日期"].strip() == ""
                
                tag = "unreturned" if is_unreturned else "returned"
                status = "离楼未回" if is_unreturned else "已回楼"
                
                self.tree.insert("", tk.END, values=(
                    student["楼栋"],
                    student["姓名"],
                    student["寝室号"],
                    student["床位号"],
                    record.get("离楼日期", ""),
                    status
                ), tags=(tag,))
            else:
                self.tree.insert("", tk.END, values=(
                    student["楼栋"],
                    student["姓名"],
                    student["寝室号"],
                    student["床位号"],
                    "",
                    "未离楼"
                ), tags=("returned",))
    
    def _on_sort(self, column):
        if self.sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column
            self.sort_ascending = True
        self._load_all_students()
    
    def _on_search(self, event):
        self.search_keyword = self.search_entry.get().strip()
        self._load_all_students()


class AIAssistantWindow(tk.Toplevel):
    """宿舍管理智能助手窗口"""
    
    def __init__(self, parent, data_manager, main_app=None):
        super().__init__(parent)
        self.title("宿舍管理智能助手")
        self.geometry("400x300")
        self.resizable(False, False)
        center_window(self, 400, 300)
        self.data_manager = data_manager
        self.main_app = main_app
        self._setup_ui()
    
    def _setup_ui(self):
        frame = tk.Frame(self, padx=30, pady=20, bg="#f0f0f0")
        frame.pack(fill=tk.BOTH, expand=True)
        
        self.stats_label = tk.Label(frame, text="", font=("Microsoft YaHei", 13, "bold"), bg="#f0f0f0")
        self.stats_label.pack(pady=(0, 5))
        
        self.building_label = tk.Label(frame, text="", font=("Microsoft YaHei", 12), bg="#f0f0f0", fg="#666666")
        self.building_label.pack(pady=(0, 20))
        
        self.tip_label = tk.Label(frame, text="", font=("Microsoft YaHei", 12), fg="#f44336", bg="#f0f0f0", wraplength=300)
        self.tip_label.pack(pady=(0, 20), padx=10)
        
        export_btn = tk.Button(frame, text="导出数据为CSV", command=self._export_data,
                              font=("Microsoft YaHei", 14), width=15, height=2,
                              bg="#4CAF50", fg="white", activebackground="#45a049")
        export_btn.pack(pady=10)
        
        self._update_stats()
        self._schedule_refresh()
    
    def _schedule_refresh(self):
        self._refresh_id = self.after(1000, self._on_refresh)
    
    def _on_refresh(self):
        if self.winfo_exists():
            self._update_stats()
            self._schedule_refresh()
    
    def _update_stats(self):
        building = "全部"
        if self.main_app and hasattr(self.main_app, 'current_building'):
            building = self.main_app.current_building.get()
        
        records = self.data_manager.load_records_by_building(building)
        total = len(records)
        unreturned = sum(1 for r in records if not r.get("回楼日期") or r["回楼日期"].strip() == "")
        returned = total - unreturned
        
        self.stats_label.config(text=f"总记录数：{total} | 未回楼：{unreturned} | 已回楼：{returned}")
        if building != "全部":
            self.building_label.config(text=f"当前楼栋：{building}")
        else:
            self.building_label.config(text="当前楼栋：全部楼栋")
        if unreturned > 0:
            self.tip_label.config(text=f"风险预警：当前有{unreturned}名学生未回楼，请及时联系辅导员")
        else:
            self.tip_label.config(text="✅ 所有学生已回楼，安全正常")
    
    def _export_data(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
                initialfile="宿舍登记记录.csv"
            )
            
            if not file_path:
                return
            
            building = "全部"
            if self.main_app and hasattr(self.main_app, 'current_building'):
                building = self.main_app.current_building.get()
            
            records = self.data_manager.load_records_by_building(building)
            fieldnames = ["楼栋", "姓名", "寝室号", "床位号", "离楼日期", "回楼日期", "备注"]
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)
            
            log_operation("导出数据", f"导出到{file_path}，共{len(records)}条记录（{building}）")
            
            messagebox.showinfo("提示", "数据已成功导出为CSV文件！")
        except Exception as e:
            messagebox.showerror("错误", "导出失败，请检查文件权限！")
