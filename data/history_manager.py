import sqlite3
import json
import csv
import os
from datetime import datetime

class HistoryManager:
    def __init__(self):
        self.db_path = 'data/rf_toolbox.db'
        self.init_database()
    
    def init_database(self):
        # 初始化数据库
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建历史记录表格
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT NOT NULL,
                input_data TEXT NOT NULL,
                output_data TEXT NOT NULL,
                calculation_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_favorite INTEGER DEFAULT 0
            )
        ''')
        
        # 创建项目表格
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                data TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_history(self, tool_name, input_data, output_data, calculation_type, is_favorite=False):
        # 添加历史记录
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO history (tool_name, input_data, output_data, calculation_type, is_favorite)
            VALUES (?, ?, ?, ?, ?)
        ''', (tool_name, input_data, output_data, calculation_type, int(is_favorite)))
        
        conn.commit()
        conn.close()
    
    def get_history(self, limit=10, offset=0, calculation_type=None, is_favorite=None):
        # 获取历史记录
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM history ORDER BY timestamp DESC LIMIT ? OFFSET ?'
        params = (limit, offset)
        
        if calculation_type:
            query = 'SELECT * FROM history WHERE calculation_type = ? ORDER BY timestamp DESC LIMIT ? OFFSET ?'
            params = (calculation_type, limit, offset)
        
        if is_favorite is not None:
            query = 'SELECT * FROM history WHERE is_favorite = ? ORDER BY timestamp DESC LIMIT ? OFFSET ?'
            params = (int(is_favorite), limit, offset)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        return self._format_history_rows(rows)
    
    def search_history(self, keyword):
        # 搜索历史记录
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM history 
            WHERE tool_name LIKE ? OR input_data LIKE ? OR output_data LIKE ? 
            ORDER BY timestamp DESC
        '''
        params = (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%')
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        return self._format_history_rows(rows)
    
    def favorite_history(self, history_id, is_favorite=True):
        # 收藏/取消收藏历史记录
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE history SET is_favorite = ? WHERE id = ?
        ''', (int(is_favorite), history_id))
        
        conn.commit()
        conn.close()
    
    def delete_history(self, history_id):
        # 删除历史记录
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM history WHERE id = ?', (history_id,))
        
        conn.commit()
        conn.close()
    
    def clear_history(self):
        # 清空历史记录
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM history')
        
        conn.commit()
        conn.close()
    
    def get_recent_history(self, limit=3):
        # 获取最近的历史记录
        return self.get_history(limit=limit)
    
    def add_project(self, name, description='', data=None):
        # 添加项目
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data_json = json.dumps(data) if data else None
        
        cursor.execute('''
            INSERT INTO projects (name, description, data)
            VALUES (?, ?, ?)
        ''', (name, description, data_json))
        
        conn.commit()
        conn.close()
    
    def get_projects(self):
        # 获取所有项目
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        conn.close()
        
        return self._format_project_rows(rows)
    
    def get_project(self, project_id):
        # 获取单个项目
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        return self._format_project_row(row) if row else None
    
    def update_project(self, project_id, name=None, description=None, data=None):
        # 更新项目
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if name is not None:
            cursor.execute('UPDATE projects SET name = ? WHERE id = ?', (name, project_id))
        
        if description is not None:
            cursor.execute('UPDATE projects SET description = ? WHERE id = ?', (description, project_id))
        
        if data is not None:
            data_json = json.dumps(data)
            cursor.execute('UPDATE projects SET data = ? WHERE id = ?', (data_json, project_id))
        
        cursor.execute('UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = ?', (project_id,))
        
        conn.commit()
        conn.close()
    
    def delete_project(self, project_id):
        # 删除项目
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        
        conn.commit()
        conn.close()
    
    def export_history(self, format_type, file_path, history_ids=None):
        # 导出历史记录
        if history_ids:
            history = self.get_history_by_ids(history_ids)
        else:
            history = self.get_history(limit=1000)
        
        if format_type == 'csv':
            self._export_history_to_csv(history, file_path)
        elif format_type == 'json':
            self._export_history_to_json(history, file_path)
        elif format_type == 'txt':
            self._export_history_to_txt(history, file_path)
        else:
            raise ValueError(f'不支持的导出格式: {format_type}')
    
    def export_project(self, project_id, format_type, file_path):
        # 导出项目
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f'找不到项目: {project_id}')
        
        if format_type == 'csv':
            self._export_project_to_csv(project, file_path)
        elif format_type == 'json':
            self._export_project_to_json(project, file_path)
        elif format_type == 'txt':
            self._export_project_to_txt(project, file_path)
        else:
            raise ValueError(f'不支持的导出格式: {format_type}')
    
    def get_history_by_ids(self, history_ids):
        # 根据ID获取历史记录
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join('?' for _ in history_ids)
        query = f'SELECT * FROM history WHERE id IN ({placeholders}) ORDER BY timestamp DESC'
        
        cursor.execute(query, history_ids)
        rows = cursor.fetchall()
        
        conn.close()
        
        return self._format_history_rows(rows)
    
    def _format_history_rows(self, rows):
        # 格式化历史记录行
        return [self._format_history_row(row) for row in rows]
    
    def _format_history_row(self, row):
        # 格式化历史记录行
        return {
            'id': row[0],
            'tool_name': row[1],
            'input_data': row[2],
            'output_data': row[3],
            'calculation_type': row[4],
            'timestamp': row[5],
            'is_favorite': bool(row[6])
        }
    
    def _format_project_rows(self, rows):
        # 格式化项目行
        return [self._format_project_row(row) for row in rows]
    
    def _format_project_row(self, row):
        # 格式化项目行
        return {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'created_at': row[3],
            'updated_at': row[4],
            'data': json.loads(row[5]) if row[5] else None
        }
    
    def _export_history_to_csv(self, history, file_path):
        # 导出历史记录到CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', '工具名称', '输入数据', '输出数据', '计算类型', '时间戳', '是否收藏'])
            
            for item in history:
                writer.writerow([
                    item['id'],
                    item['tool_name'],
                    item['input_data'],
                    item['output_data'],
                    item['calculation_type'],
                    item['timestamp'],
                    '是' if item['is_favorite'] else '否'
                ])
    
    def _export_history_to_json(self, history, file_path):
        # 导出历史记录到JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2, default=str)
    
    def _export_history_to_txt(self, history, file_path):
        # 导出历史记录到TXT
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in history:
                f.write(f"ID: {item['id']}\n")
                f.write(f"工具名称: {item['tool_name']}\n")
                f.write(f"输入数据: {item['input_data']}\n")
                f.write(f"输出数据: {item['output_data']}\n")
                f.write(f"计算类型: {item['calculation_type']}\n")
                f.write(f"时间戳: {item['timestamp']}\n")
                f.write(f"是否收藏: {'是' if item['is_favorite'] else '否'}\n")
                f.write("\n" + "="*50 + "\n\n")
    
    def _export_project_to_csv(self, project, file_path):
        # 导出项目到CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['项目ID', '项目名称', '项目描述', '创建时间', '更新时间'])
            writer.writerow([
                project['id'],
                project['name'],
                project['description'],
                project['created_at'],
                project['updated_at']
            ])
            
            # 如果有数据，写入数据部分
            if project['data']:
                writer.writerow([])
                writer.writerow(['项目数据:'])
                
                # 写入数据的键值对
                for key, value in project['data'].items():
                    writer.writerow([key, value])
    
    def _export_project_to_json(self, project, file_path):
        # 导出项目到JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(project, f, ensure_ascii=False, indent=2, default=str)
    
    def _export_project_to_txt(self, project, file_path):
        # 导出项目到TXT
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"项目ID: {project['id']}\n")
            f.write(f"项目名称: {project['name']}\n")
            f.write(f"项目描述: {project['description']}\n")
            f.write(f"创建时间: {project['created_at']}\n")
            f.write(f"更新时间: {project['updated_at']}\n")
            
            # 如果有数据，写入数据部分
            if project['data']:
                f.write("\n" + "="*50 + "\n")
                f.write("项目数据:\n")
                f.write("="*50 + "\n")
                
                # 写入数据的键值对
                for key, value in project['data'].items():
                    f.write(f"{key}: {value}\n")
    
    def backup_database(self, backup_path):
        # 备份数据库
        conn = sqlite3.connect(self.db_path)
        backup_conn = sqlite3.connect(backup_path)
        
        with backup_conn:
            conn.backup(backup_conn)
        
        conn.close()
        backup_conn.close()
    
    def restore_database(self, backup_path):
        # 恢复数据库
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f'备份文件不存在: {backup_path}')
        
        # 关闭所有连接
        conn = sqlite3.connect(self.db_path)
        conn.close()
        
        # 恢复数据库
        os.replace(backup_path, self.db_path)
    
    def get_statistics(self):
        # 获取统计信息
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总历史记录数
        cursor.execute('SELECT COUNT(*) FROM history')
        total_history = cursor.fetchone()[0]
        
        # 总项目数
        cursor.execute('SELECT COUNT(*) FROM projects')
        total_projects = cursor.fetchone()[0]
        
        # 收藏的历史记录数
        cursor.execute('SELECT COUNT(*) FROM history WHERE is_favorite = 1')
        favorite_history = cursor.fetchone()[0]
        
        # 按工具统计使用次数
        cursor.execute('SELECT tool_name, COUNT(*) FROM history GROUP BY tool_name ORDER BY COUNT(*) DESC')
        tool_usage = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_history': total_history,
            'total_projects': total_projects,
            'favorite_history': favorite_history,
            'tool_usage': tool_usage
        }