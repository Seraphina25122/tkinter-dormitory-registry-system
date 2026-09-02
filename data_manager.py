import csv
import datetime
import os
import shutil
import re

import openpyxl

from utils import log_operation, is_valid_date, is_return_date_valid


class DataManager:
    """数据管理类，负责CSV文件的读写、备份和查询"""
    
    def __init__(self):
        self.data_dir = "data"
        self.data_file = os.path.join(self.data_dir, "records.csv")
        self.backup_dir = os.path.join(self.data_dir, "backups")
        self.fields = ["楼栋", "姓名", "寝室号", "床位号", "离楼日期", "回楼日期", "备注"]
        self._init_directories()
        self._auto_backup()
        self.repair_building_format()
    
    def _init_directories(self):
        try:
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
            if not os.path.exists(self.data_file):
                self._create_empty_file()
        except Exception as e:
            print(f"初始化目录异常: {e}")
    
    def _create_empty_file(self):
        try:
            with open(self.data_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=self.fields)
                writer.writeheader()
        except Exception as e:
            print(f"创建空文件异常: {e}")
    
    def _auto_backup(self):
        try:
            if os.path.exists(self.data_file):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(self.backup_dir, f"records_backup_{timestamp}.csv")
                shutil.copy2(self.data_file, backup_file)
                self._clean_old_backups()
        except Exception as e:
            print(f"自动备份异常: {e}")
    
    def _clean_old_backups(self):
        try:
            backups = sorted([f for f in os.listdir(self.backup_dir) if f.startswith("records_backup_")])
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    os.remove(os.path.join(self.backup_dir, old_backup))
        except Exception as e:
            print(f"清理旧备份异常: {e}")
    
    def load_records(self):
        records = []
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if "楼栋" not in row or not row["楼栋"]:
                            row["楼栋"] = "1号楼"
                        else:
                            normalized = self._normalize_building(row["楼栋"])
                            if normalized:
                                row["楼栋"] = normalized
                        records.append(row)
        except Exception as e:
            print(f"加载记录异常: {e}")
        return records
    
    def load_records_by_building(self, building):
        if building == "全部":
            return self.load_records()
        
        records = self.load_records()
        filtered = [r for r in records if r.get("楼栋") == building]
        return filtered
    
    def repair_building_format(self):
        records = self.load_records()
        fixed_count = 0
        has_empty_field = False
        
        for record in records:
            required_fields_check = ["姓名", "寝室号", "床位号", "离楼日期"]
            for field in required_fields_check:
                if not record.get(field) or record[field].strip() == "":
                    has_empty_field = True
                    break
            
            original_building = record.get("楼栋", "")
            normalized_building = self._normalize_building(original_building)
            
            if normalized_building and normalized_building != original_building:
                record["楼栋"] = normalized_building
                fixed_count += 1
            elif not normalized_building:
                record["楼栋"] = "1号楼"
                fixed_count += 1
        
        if fixed_count > 0 or has_empty_field:
            self.save_records(records)
        
        return (fixed_count, has_empty_field)
    
    def save_records(self, records):
        try:
            with open(self.data_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=self.fields)
                writer.writeheader()
                writer.writerows(records)
            return True
        except Exception as e:
            print(f"保存记录异常: {e}")
            return False
    
    def add_record(self, record):
        records = self.load_records()
        records.append(record)
        self.save_records(records)
        details = f"楼栋：{record['楼栋']}，姓名：{record['姓名']}，寝室号：{record['寝室号']}，床位号：{record['床位号']}，离楼日期：{record['离楼日期']}"
        log_operation("新增记录", details)
    
    def update_record(self, index, new_record):
        records = self.load_records()
        if 0 <= index < len(records):
            old_record = records[index]
            records[index] = new_record
            self.save_records(records)
            details = f"索引{index}：楼栋：{new_record['楼栋']}，回楼日期从\"{old_record['回楼日期']}\"改为\"{new_record['回楼日期']}\""
            log_operation("修改记录", details)
            return True
        return False
    
    def delete_record(self, index):
        records = self.load_records()
        if 0 <= index < len(records):
            deleted_record = records[index]
            del records[index]
            self.save_records(records)
            details = f"索引{index}：楼栋：{deleted_record['楼栋']}，姓名：{deleted_record['姓名']}，寝室号：{deleted_record['寝室号']}，床位号：{deleted_record['床位号']}"
            log_operation("删除记录", details)
            return True
        return False
    
    def get_unreturned_students(self):
        records = self.load_records()
        unreturned = []
        for record in records:
            if not record.get("回楼日期") or record["回楼日期"].strip() == "":
                unreturned.append(record)
        return unreturned
    
    def batch_import(self, file_path):
        required_fields = ["楼栋", "姓名", "寝室号", "床位号", "离楼日期"]
        optional_fields = ["回楼日期", "备注"]
        all_fields = required_fields + optional_fields
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == ".csv":
                data_rows = self._read_csv_file(file_path)
            elif file_ext in [".xlsx", ".xls"]:
                data_rows = self._read_excel_file(file_path)
            else:
                return (False, "不支持的文件格式，仅支持CSV和Excel(.xlsx)文件", 0, 0, 0)
            
            if not data_rows:
                return (False, "文件内容为空", 0, 0, 0)
            
            raw_headers = data_rows[0]
            headers = [str(h).strip() if h else "" for h in raw_headers]
            
            missing_fields = [f for f in required_fields if f not in headers]
            if missing_fields:
                return (False, f"表头缺少必填字段：{', '.join(missing_fields)}", 0, 0, 0)
            
            existing_records = self.load_records()
            existing_keys = set()
            for r in existing_records:
                key = f"{r['楼栋']}_{r['姓名']}_{r['寝室号']}_{r['床位号']}_{r['离楼日期']}"
                existing_keys.add(key)
            
            added_count = 0
            duplicate_count = 0
            invalid_count = 0
            new_records = []
            
            for row in data_rows[1:]:
                try:
                    record = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            value = str(row[i]).strip() if row[i] is not None else ""
                            value = value.replace('\n', ' ').replace('\r', ' ')
                            record[header] = value
                        else:
                            record[header] = ""
                    
                    is_valid = True
                    for field in required_fields:
                        if not record.get(field) or record[field].strip() == "":
                            is_valid = False
                            break
                    
                    if not is_valid:
                        invalid_count += 1
                        continue
                    
                    building = self._normalize_building(record["楼栋"])
                    if not building:
                        invalid_count += 1
                        continue
                    record["楼栋"] = building
                    
                    leave_date = self._normalize_date(record["离楼日期"])
                    if not leave_date:
                        invalid_count += 1
                        continue
                    record["离楼日期"] = leave_date
                    
                    return_date = record.get("回楼日期", "").strip()
                    if return_date:
                        return_date = self._normalize_date(return_date)
                        if not return_date:
                            invalid_count += 1
                            continue
                        valid, _ = is_return_date_valid(record["离楼日期"], return_date)
                        if not valid:
                            invalid_count += 1
                            continue
                        record["回楼日期"] = return_date
                    
                    key = f"{record['楼栋']}_{record['姓名']}_{record['寝室号']}_{record['床位号']}_{record['离楼日期']}"
                    if key in existing_keys:
                        duplicate_count += 1
                        continue
                    
                    for field in all_fields:
                        if field not in record:
                            record[field] = ""
                    
                    new_records.append(record)
                    existing_keys.add(key)
                    added_count += 1
                    
                except Exception:
                    invalid_count += 1
                    continue
            
            if new_records:
                all_records = existing_records + new_records
                self.save_records(all_records)
                
                log_operation("批量导入", f"从{file_path}导入，新增{added_count}条，重复{duplicate_count}条，无效{invalid_count}条")
            
            message = f"导入完成，新增 {added_count} 条，重复跳过 {duplicate_count} 条，无效行跳过 {invalid_count} 条"
            if invalid_count > 5:
                message += "\n\n提示：如有过多无效行，请检查表头、必填字段和日期格式是否正确"
            
            return (True, message, added_count, duplicate_count, invalid_count)
            
        except Exception as e:
            return (False, f"导入失败，原因：{str(e)}", 0, 0, 0)
    
    def _normalize_building(self, building_str):
        if not building_str:
            return None
        
        building_str = str(building_str).strip()
        if not building_str:
            return None
        
        building_str = building_str.replace(' ', '')
        
        number_map = {
            "一": "1", "二": "2", "三": "3", "四": "4",
            "壹": "1", "贰": "2", "叁": "3", "肆": "4",
            "五": "5", "六": "6", "七": "7", "八": "8", "九": "9", "十": "10"
        }
        
        for cn_num, arabic_num in number_map.items():
            building_str = building_str.replace(cn_num, arabic_num)
        
        number_match = re.search(r'\d+', building_str)
        if not number_match:
            return None
        
        building_num = number_match.group()
        
        if building_num in ["1", "2", "3", "4"]:
            return f"{building_num}号楼"
        
        return None
    
    def _normalize_date(self, date_str):
        if not date_str:
            return None
        
        date_str = str(date_str).strip()
        if not date_str:
            return None
        
        if is_valid_date(date_str):
            return date_str
        
        date_str = date_str.replace('/', '-')
        
        if is_valid_date(date_str):
            return date_str
        
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%d/%m/%Y",
            "%m/%d/%Y",
        ]
        
        for fmt in formats:
            try:
                dt = datetime.datetime.strptime(date_str.split()[0], fmt.split()[0] if ' ' in date_str else fmt)
                return dt.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                continue
        
        return None
    
    def _read_csv_file(self, file_path):
        rows = []
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                rows.append(cleaned_row)
        return rows
    
    def _read_excel_file(self, file_path):
        rows = []
        workbook = openpyxl.load_workbook(file_path, read_only=True)
        sheet = workbook.active
        
        for row in sheet.iter_rows(values_only=True):
            row_data = []
            for cell in row:
                if cell is None:
                    row_data.append("")
                elif isinstance(cell, datetime.datetime):
                    row_data.append(cell.strftime("%Y-%m-%d"))
                elif isinstance(cell, datetime.date):
                    row_data.append(cell.strftime("%Y-%m-%d"))
                else:
                    row_data.append(str(cell).strip())
            rows.append(row_data)
        
        workbook.close()
        return rows
