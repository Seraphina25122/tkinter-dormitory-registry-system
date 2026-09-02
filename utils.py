import datetime
import os
import tkinter as tk

from config import STUDENT_LIST


def setup_global_font():
    default_font = ("Microsoft YaHei", 12)
    root = tk.Tk()
    root.option_add("*Font", default_font)
    root.destroy()


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def validate_student_data(name, building, dorm_room=None, bed=None):
    if not name or not building:
        return (True, "", {})
    
    same_name_students = [s for s in STUDENT_LIST if s["姓名"] == name]
    
    if not same_name_students:
        return (False, f"警告：此条数据不属于名单！", {})
    
    building_matches = [s for s in same_name_students if s["楼栋"] == building]
    
    if building_matches:
        student = building_matches[0]
        suggestion = {}
        if dorm_room and dorm_room != student["寝室号"]:
            suggestion["寝室号"] = student["寝室号"]
        if bed and bed != student["床位号"]:
            suggestion["床位号"] = student["床位号"]
        
        if suggestion:
            suggest_text = "、".join([f"{k}：{v}" for k, v in suggestion.items()])
            return (False, f"您是否要输入{suggest_text}？", suggestion)
        return (True, "", {})
    else:
        suggestion = {
            "楼栋": same_name_students[0]["楼栋"],
            "寝室号": same_name_students[0]["寝室号"],
            "床位号": same_name_students[0]["床位号"]
        }
        suggest_text = "、".join([f"{k}：{v}" for k, v in suggestion.items()])
        return (False, f"您是否要输入{suggest_text}？", suggestion)


def log_operation(operation_type, details):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} | {operation_type} | {details}\n"
        
        with open("audit_log.txt", "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f"日志记录失败: {e}")


def is_valid_date(date_str):
    if not date_str:
        return False
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_return_date_valid(leave_date, return_date):
    if not return_date or return_date.strip() == "":
        return (True, "")
    
    if not is_valid_date(leave_date):
        return (False, "离楼日期格式无效！")
    
    if not is_valid_date(return_date):
        return (False, "回楼日期格式无效！")
    
    leave_dt = datetime.datetime.strptime(leave_date, "%Y-%m-%d")
    return_dt = datetime.datetime.strptime(return_date, "%Y-%m-%d")
    
    if return_dt < leave_dt:
        return (False, "回楼日期不能早于离楼日期！")
    
    return (True, "")
