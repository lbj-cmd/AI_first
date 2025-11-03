import json
import os
import sqlite3
from datetime import datetime

class KnowledgeBase:
    def __init__(self):
        self.db_path = 'data/knowledge_base.db'
        self.init_database()
    
    def init_database(self):
        # 初始化知识库数据库
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建知识条目表格
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                keywords TEXT,
                difficulty INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                views INTEGER DEFAULT 0
            )
        ''')
        
        # 创建学习进度表格
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                knowledge_id INTEGER NOT NULL,
                completed INTEGER DEFAULT 0,
                progress INTEGER DEFAULT 0,
                last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (knowledge_id) REFERENCES knowledge_items (id)
            )
        ''')
        
        # 创建练习表格
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                knowledge_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                correct_answer INTEGER NOT NULL,
                explanation TEXT,
                difficulty INTEGER DEFAULT 1,
                FOREIGN KEY (knowledge_id) REFERENCES knowledge_items (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # 初始化基础数据
        self.init_base_data()
    
    def init_base_data(self):
        # 检查是否已有数据
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM knowledge_items')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # 导入基础知识库数据
            base_data = self._load_base_knowledge()
            for item in base_data:
                cursor.execute('''
                    INSERT INTO knowledge_items (category, subcategory, title, content, keywords, difficulty)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (item['category'], item['subcategory'], item['title'], item['content'], item['keywords'], item['difficulty']))
            
            conn.commit()
        
        conn.close()
    
    def _load_base_knowledge(self):
        # 加载基础知识库数据
        return [
            {
                'category': '基础理论',
                'subcategory': '射频基础知识',
                'title': '射频波的特性',
                'content': '射频波是一种电磁波，频率范围通常在3 kHz到300 GHz之间。射频波具有以下特性：\n\n1. **传播特性**：射频波可以通过空气、真空或介质传播，具有反射、折射、绕射和散射等特性。\n\n2. **频率与波长**：频率(f)和波长(λ)的关系为λ = c/f，其中c是光速(约3×10^8 m/s)。\n\n3. **功率与能量**：射频信号的功率通常用分贝毫瓦(dBm)表示，1 dBm = 10^(-3) W。\n\n4. **阻抗匹配**：在射频系统中，阻抗匹配非常重要，不匹配会导致信号反射和功率损失。\n\n5. **传输线效应**：当传输线长度与信号波长可比拟时，会出现传输线效应，需要使用传输线理论分析。',
                'keywords': '射频波,电磁波,频率,波长,功率,阻抗匹配,传输线',
                'difficulty': 1
            },
            {
                'category': '基础理论',
                'subcategory': '传输线理论',
                'title': '传输线的基本参数',
                'content': '传输线的基本参数包括：\n\n1. **特性阻抗(Z0)**：传输线在无限长时的输入阻抗，对于均匀传输线，Z0 = √(L/C)，其中L是单位长度电感，C是单位长度电容。\n\n2. **传播常数(γ)**：表示信号在传输线上的衰减和相位变化，γ = α + jβ，其中α是衰减常数(Np/m)，β是相位常数(rad/m)。\n\n3. **衰减常数(α)**：表示信号在传输线上的功率衰减，单位为dB/m或Np/m。\n\n4. **相位常数(β)**：表示信号在传输线上的相位变化，β = 2π/λg，其中λg是传输线的波长。\n\n5. **群速(vg)**：信号包络的传播速度，vg = ω/β，其中ω是角频率。',
                'keywords': '传输线,特性阻抗,传播常数,衰减常数,相位常数,群速',
                'difficulty': 2
            },
            {
                'category': '器件知识',
                'subcategory': '天线',
                'title': '天线的基本参数',
                'content': '天线的基本参数包括：\n\n1. **增益(G)**：天线将输入功率转换为定向辐射功率的能力，通常用dBi表示(相对于各向同性天线)。\n\n2. **方向性(D)**：天线在最大辐射方向上的辐射强度与平均辐射强度的比值。\n\n3. **波束宽度**：天线辐射方向图中，功率下降3 dB(半功率点)时的夹角，包括水平波束宽度和垂直波束宽度。\n\n4. **输入阻抗(Zin)**：天线输入端的阻抗，通常需要与传输线阻抗匹配。\n\n5. **驻波比(VSWR)**：表示天线与传输线之间的匹配程度，VSWR = (1 + Γ)/(1 - Γ)，其中Γ是反射系数。\n\n6. **带宽(BW)**：天线性能保持在指定范围内的频率范围。',
                'keywords': '天线,增益,方向性,波束宽度,输入阻抗,驻波比,带宽',
                'difficulty': 2
            },
            {
                'category': '系统设计',
                'subcategory': '链路预算',
                'title': '射频链路预算的基本概念',
                'content': '射频链路预算是分析射频系统中信号从发射端到接收端的功率变化和信噪比(SNR)的过程。链路预算的主要组成部分包括：\n\n1. **发射机部分**：发射功率、发射天线增益、馈线损耗。\n\n2. **传播部分**：自由空间损耗、大气损耗、多径损耗、阴影损耗。\n\n3. **接收机部分**：接收天线增益、馈线损耗、接收机噪声系数、接收机灵敏度。\n\n链路预算的目的是确保接收端的信号功率大于接收机灵敏度，并有足够的余量。常用的链路余量计算公式为：\n\n链路余量 = 发射功率 + 发射天线增益 - 馈线损耗 - 自由空间损耗 - 其他损耗 + 接收天线增益 - 接收馈线损耗 - 接收机灵敏度\n\n链路余量通常需要大于10 dB，以保证系统的可靠性。',
                'keywords': '链路预算,发射功率,接收灵敏度,自由空间损耗,噪声系数,链路余量',
                'difficulty': 2
            },
            {
                'category': '标准规范',
                'subcategory': '频率分配',
                'title': '常用射频频段分配',
                'content': '国际电信联盟(ITU)对射频频段进行了统一分配，常用频段包括：\n\n1. **HF(高频)**：3-30 MHz，用于短波通信。\n\n2. **VHF(甚高频)**：30-300 MHz，用于电视、调频广播、航空通信。\n\n3. **UHF(特高频)**：300 MHz-3 GHz，用于手机、卫星通信、雷达。\n\n4. **L波段**：1-2 GHz，用于GPS、卫星通信。\n\n5. **S波段**：2-4 GHz，用于雷达、卫星通信。\n\n6. **C波段**：4-8 GHz，用于卫星通信、雷达。\n\n7. **X波段**：8-12 GHz，用于雷达、卫星通信。\n\n8. **Ku波段**：12-18 GHz，用于卫星电视、卫星通信。\n\n9. **K波段**：18-27 GHz，用于雷达、卫星通信。\n\n10. **Ka波段**：27-40 GHz，用于卫星通信、毫米波通信。',
                'keywords': '频段分配,HF,VHF,UHF,L波段,S波段,C波段,X波段,Ku波段,Ka波段',
                'difficulty': 1
            }
        ]
    
    def get_categories(self):
        # 获取所有分类
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT category FROM knowledge_items ORDER BY category')
        categories = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return categories
    
    def get_subcategories(self, category):
        # 获取指定分类下的所有子分类
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT subcategory FROM knowledge_items WHERE category = ? ORDER BY subcategory', (category,))
        subcategories = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return subcategories
    
    def get_knowledge_items(self, category=None, subcategory=None, difficulty=None, keywords=None):
        # 获取知识条目
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM knowledge_items ORDER BY category, subcategory, title'
        params = []
        
        if category:
            query = 'SELECT * FROM knowledge_items WHERE category = ? ORDER BY subcategory, title'
            params = [category]
        
        if subcategory:
            if category:
                query = 'SELECT * FROM knowledge_items WHERE category = ? AND subcategory = ? ORDER BY title'
                params = [category, subcategory]
            else:
                query = 'SELECT * FROM knowledge_items WHERE subcategory = ? ORDER BY category, title'
                params = [subcategory]
        
        if difficulty:
            if category and subcategory:
                query = 'SELECT * FROM knowledge_items WHERE category = ? AND subcategory = ? AND difficulty = ? ORDER BY title'
                params = [category, subcategory, difficulty]
            elif category:
                query = 'SELECT * FROM knowledge_items WHERE category = ? AND difficulty = ? ORDER BY subcategory, title'
                params = [category, difficulty]
            elif subcategory:
                query = 'SELECT * FROM knowledge_items WHERE subcategory = ? AND difficulty = ? ORDER BY category, title'
                params = [subcategory, difficulty]
            else:
                query = 'SELECT * FROM knowledge_items WHERE difficulty = ? ORDER BY category, subcategory, title'
                params = [difficulty]
        
        if keywords:
            keyword_list = keywords.split()
            if keyword_list:
                where_clauses = []
                for keyword in keyword_list:
                    where_clauses.append(f'(title LIKE ? OR content LIKE ? OR keywords LIKE ?)')
                
                keyword_where = ' AND '.join(where_clauses)
                
                if 'WHERE' in query:
                    query = f'{query} AND {keyword_where}'
                else:
                    query = f'{query} WHERE {keyword_where}'
                
                # 为每个关键词添加三个参数(标题、内容、关键词)
                for keyword in keyword_list:
                    params.extend([f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        return self._format_knowledge_rows(rows)
    
    def get_knowledge_item(self, item_id):
        # 获取单个知识条目
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM knowledge_items WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        
        if row:
            # 更新浏览次数
            cursor.execute('UPDATE knowledge_items SET views = views + 1 WHERE id = ?', (item_id,))
            conn.commit()
        
        conn.close()
        
        return self._format_knowledge_row(row) if row else None
    
    def search_knowledge(self, keyword):
        # 搜索知识库
        return self.get_knowledge_items(keywords=keyword)
    
    def get_learning_progress(self, user_id='default'):
        # 获取学习进度
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT k.*, lp.completed, lp.progress, lp.last_accessed
            FROM knowledge_items k
            LEFT JOIN learning_progress lp ON k.id = lp.knowledge_id AND lp.user_id = ?
            ORDER BY k.category, k.subcategory, k.title
        ''', (user_id,))
        rows = cursor.fetchall()
        
        conn.close()
        
        progress = []
        for row in rows:
            progress.append({
                'id': row[0],
                'category': row[1],
                'subcategory': row[2],
                'title': row[3],
                'completed': bool(row[10]) if row[10] is not None else False,
                'progress': row[11] if row[11] is not None else 0,
                'last_accessed': row[12]
            })
        
        return progress
    
    def update_learning_progress(self, knowledge_id, completed=False, progress=0, user_id='default'):
        # 更新学习进度
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查是否已有记录
        cursor.execute('''
            SELECT id FROM learning_progress 
            WHERE knowledge_id = ? AND user_id = ?
        ''', (knowledge_id, user_id))
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有记录
            cursor.execute('''
                UPDATE learning_progress 
                SET completed = ?, progress = ?, last_accessed = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (int(completed), progress, existing[0]))
        else:
            # 创建新记录
            cursor.execute('''
                INSERT INTO learning_progress (user_id, knowledge_id, completed, progress)
                VALUES (?, ?, ?, ?)
            ''', (user_id, knowledge_id, int(completed), progress))
        
        conn.commit()
        conn.close()
    
    def get_exercises(self, knowledge_id=None, difficulty=None):
        # 获取练习
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM exercises ORDER BY knowledge_id, difficulty'
        params = []
        
        if knowledge_id:
            query = 'SELECT * FROM exercises WHERE knowledge_id = ? ORDER BY difficulty'
            params = [knowledge_id]
        
        if difficulty:
            if knowledge_id:
                query = 'SELECT * FROM exercises WHERE knowledge_id = ? AND difficulty = ? ORDER BY id'
                params = [knowledge_id, difficulty]
            else:
                query = 'SELECT * FROM exercises WHERE difficulty = ? ORDER BY knowledge_id'
                params = [difficulty]
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        return self._format_exercise_rows(rows)
    
    def get_exercise(self, exercise_id):
        # 获取单个练习
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM exercises WHERE id = ?', (exercise_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        return self._format_exercise_row(row) if row else None
    
    def add_knowledge_item(self, category, subcategory, title, content, keywords=None, difficulty=1):
        # 添加知识条目
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO knowledge_items (category, subcategory, title, content, keywords, difficulty)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (category, subcategory, title, content, keywords, difficulty))
        
        conn.commit()
        conn.close()
    
    def update_knowledge_item(self, item_id, category=None, subcategory=None, title=None, content=None, keywords=None, difficulty=None):
        # 更新知识条目
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category is not None:
            cursor.execute('UPDATE knowledge_items SET category = ? WHERE id = ?', (category, item_id))
        
        if subcategory is not None:
            cursor.execute('UPDATE knowledge_items SET subcategory = ? WHERE id = ?', (subcategory, item_id))
        
        if title is not None:
            cursor.execute('UPDATE knowledge_items SET title = ? WHERE id = ?', (title, item_id))
        
        if content is not None:
            cursor.execute('UPDATE knowledge_items SET content = ? WHERE id = ?', (content, item_id))
        
        if keywords is not None:
            cursor.execute('UPDATE knowledge_items SET keywords = ? WHERE id = ?', (keywords, item_id))
        
        if difficulty is not None:
            cursor.execute('UPDATE knowledge_items SET difficulty = ? WHERE id = ?', (difficulty, item_id))
        
        cursor.execute('UPDATE knowledge_items SET updated_at = CURRENT_TIMESTAMP WHERE id = ?', (item_id,))
        
        conn.commit()
        conn.close()
    
    def delete_knowledge_item(self, item_id):
        # 删除知识条目
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM knowledge_items WHERE id = ?', (item_id,))
        cursor.execute('DELETE FROM learning_progress WHERE knowledge_id = ?', (item_id,))
        cursor.execute('DELETE FROM exercises WHERE knowledge_id = ?', (item_id,))
        
        conn.commit()
        conn.close()
    
    def _format_knowledge_rows(self, rows):
        # 格式化知识条目行
        return [self._format_knowledge_row(row) for row in rows]
    
    def _format_knowledge_row(self, row):
        # 格式化知识条目行
        return {
            'id': row[0],
            'category': row[1],
            'subcategory': row[2],
            'title': row[3],
            'content': row[4],
            'keywords': row[5],
            'difficulty': row[6],
            'created_at': row[7],
            'updated_at': row[8],
            'views': row[9]
        }
    
    def _format_exercise_rows(self, rows):
        # 格式化练习行
        return [self._format_exercise_row(row) for row in rows]
    
    def _format_exercise_row(self, row):
        # 格式化练习行
        return {
            'id': row[0],
            'knowledge_id': row[1],
            'question': row[2],
            'options': json.loads(row[3]),
            'correct_answer': row[4],
            'explanation': row[5],
            'difficulty': row[6]
        }
    
    def get_statistics(self):
        # 获取知识库统计信息
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总知识条目数
        cursor.execute('SELECT COUNT(*) FROM knowledge_items')
        total_items = cursor.fetchone()[0]
        
        # 分类统计
        cursor.execute('SELECT category, COUNT(*) FROM knowledge_items GROUP BY category ORDER BY COUNT(*) DESC')
        category_stats = cursor.fetchall()
        
        # 难度统计
        cursor.execute('SELECT difficulty, COUNT(*) FROM knowledge_items GROUP BY difficulty ORDER BY difficulty')
        difficulty_stats = cursor.fetchall()
        
        # 总练习数
        cursor.execute('SELECT COUNT(*) FROM exercises')
        total_exercises = cursor.fetchone()[0]
        
        # 学习进度统计
        cursor.execute('SELECT COUNT(*) FROM learning_progress WHERE completed = 1')
        completed_items = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_items': total_items,
            'category_stats': category_stats,
            'difficulty_stats': difficulty_stats,
            'total_exercises': total_exercises,
            'completed_items': completed_items,
            'completion_rate': (completed_items / total_items) * 100 if total_items > 0 else 0
        }