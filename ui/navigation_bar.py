from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
                             QLabel, QPushButton, QHBoxLayout, QMenu, QAction,
                             QLineEdit, QCompleter)
from PyQt5.QtGui import QIcon, QFont, QBrush, QColor
from PyQt5.QtCore import Qt, pyqtSignal
import os

class NavigationBar(QWidget):
    tool_selected = pyqtSignal(str)
    category_selected = pyqtSignal(str)
    search_triggered = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_category = None
        self.favorites = self.load_favorites()
        self.recent_tools = self.load_recent_tools()
        self.init_ui()
    
    def init_ui(self):
        self.setMinimumWidth(250)
        self.setMaximumWidth(350)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 搜索框
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('搜索工具或知识库...')
        self.search_edit.setFont(QFont('Consolas', 10))
        self.search_edit.setStyleSheet('padding: 8px; border-radius: 5px; border: 1px solid #ccc;')
        self.search_edit.textChanged.connect(self.on_search_text_changed)
        layout.addWidget(self.search_edit)
        
        # 收藏夹
        favorites_label = QLabel('收藏夹')
        favorites_label.setFont(QFont('Arial', 12, QFont.Bold))
        layout.addWidget(favorites_label)
        
        self.favorites_list = QListWidget()
        self.favorites_list.itemClicked.connect(self.on_favorite_clicked)
        self.favorites_list.setStyleSheet('border: 1px solid #ccc; border-radius: 5px;')
        self.update_favorites_list()
        layout.addWidget(self.favorites_list)
        
        # 最近使用
        recent_label = QLabel('最近使用')
        recent_label.setFont(QFont('Arial', 12, QFont.Bold))
        layout.addWidget(recent_label)
        
        self.recent_list = QListWidget()
        self.recent_list.itemClicked.connect(self.on_recent_clicked)
        self.recent_list.setStyleSheet('border: 1px solid #ccc; border-radius: 5px;')
        self.update_recent_list()
        layout.addWidget(self.recent_list)
        
        # 工具分类
        category_label = QLabel('工具分类')
        category_label.setFont(QFont('Arial', 12, QFont.Bold))
        layout.addWidget(category_label)
        
        self.category_list = QListWidget()
        self.category_list.itemClicked.connect(self.on_category_clicked)
        self.category_list.setStyleSheet('border: 1px solid #ccc; border-radius: 5px;')
        
        # 添加分类
        categories = [
            ('频率与波长', 'frequency_wavelength.png', '频率-波长计算'),
            ('功率转换', 'power_converter.png', '功率单位换算'),
            ('传输线', 'transmission_line.png', '传输线参数计算'),
            ('天线', 'antenna.png', '天线参数计算'),
            ('滤波器', 'filter.png', '滤波器设计'),
            ('链路预算', 'link_budget.png', '射频链路预算'),
            ('知识库', 'knowledge.png', '射频知识库'),
            ('历史记录', 'history.png', '计算历史'),
            ('项目管理', 'project.png', '项目管理'),
            ('设置', 'settings.png', '设置')
        ]
        
        for category_name, icon_name, tool_name in categories:
            item = QListWidgetItem(QIcon(f'icons/{icon_name}'), category_name)
            item.setData(Qt.UserRole, tool_name)
            self.category_list.addItem(item)
        
        layout.addWidget(self.category_list)
        
        # 填充空间
        layout.addStretch()
    
    def on_search_text_changed(self, text):
        if len(text) > 2:
            self.search_triggered.emit(text)
    
    def on_category_clicked(self, item):
        tool_name = item.data(Qt.UserRole)
        self.tool_selected.emit(tool_name)
        
        # 更新最近使用
        self.add_to_recent(tool_name)
    
    def on_favorite_clicked(self, item):
        tool_name = item.data(Qt.UserRole)
        self.tool_selected.emit(tool_name)
    
    def on_recent_clicked(self, item):
        tool_name = item.data(Qt.UserRole)
        self.tool_selected.emit(tool_name)
        
        # 重新添加到最近使用（更新顺序）
        self.add_to_recent(tool_name)
    
    def add_to_recent(self, tool_name):
        # 添加到最近使用
        if tool_name in self.recent_tools:
            self.recent_tools.remove(tool_name)
        
        self.recent_tools.insert(0, tool_name)
        
        # 限制最近使用工具的数量
        if len(self.recent_tools) > 10:
            self.recent_tools = self.recent_tools[:10]
        
        self.save_recent_tools()
        self.update_recent_list()
    
    def update_recent_list(self):
        # 更新最近使用列表
        self.recent_list.clear()
        
        for tool_name in self.recent_tools:
            item = QListWidgetItem(QIcon('icons/recent.png'), tool_name)
            item.setData(Qt.UserRole, tool_name)
            self.recent_list.addItem(item)
    
    def toggle_favorite(self, tool_name):
        # 切换收藏状态
        if tool_name in self.favorites:
            self.favorites.remove(tool_name)
        else:
            self.favorites.append(tool_name)
        
        self.save_favorites()
        self.update_favorites_list()
    
    def is_favorite(self, tool_name):
        # 检查是否为收藏
        return tool_name in self.favorites
    
    def update_favorites_list(self):
        # 更新收藏夹列表
        self.favorites_list.clear()
        
        for tool_name in self.favorites:
            item = QListWidgetItem(QIcon('icons/favorite.png'), tool_name)
            item.setData(Qt.UserRole, tool_name)
            self.favorites_list.addItem(item)
    
    def load_favorites(self):
        # 加载收藏夹
        try:
            if os.path.exists('data/favorites.json'):
                with open('data/favorites.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        
        return []
    
    def save_favorites(self):
        # 保存收藏夹
        os.makedirs('data', exist_ok=True)
        
        try:
            with open('data/favorites.json', 'w') as f:
                json.dump(self.favorites, f)
        except:
            pass
    
    def load_recent_tools(self):
        # 加载最近使用工具
        try:
            if os.path.exists('data/recent.json'):
                with open('data/recent.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        
        return []
    
    def save_recent_tools(self):
        # 保存最近使用工具
        os.makedirs('data', exist_ok=True)
        
        try:
            with open('data/recent.json', 'w') as f:
                json.dump(self.recent_tools, f)
        except:
            pass
    
    def set_theme(self, theme):
        # 设置主题
        if theme == 'dark':
            self.setStyleSheet('''
                QWidget { background-color: #1E1E1E; color: #FFFFFF; }
                QListWidget { background-color: #2D2D30; border: 1px solid #555555; border-radius: 5px; }
                QListWidget::item { padding: 8px; border-bottom: 1px solid #555555; }
                QListWidget::item:hover { background-color: #3E3E42; }
                QListWidget::item:selected { background-color: #1E90FF; }
                QLineEdit { background-color: #2D2D30; color: #FFFFFF; border: 1px solid #555555; padding: 8px; border-radius: 5px; }
                QLabel { color: #FFFFFF; }
            ''')
        else:
            self.setStyleSheet('''
                QWidget { background-color: #F0F0F0; color: #000000; }
                QListWidget { background-color: #FFFFFF; border: 1px solid #CCCCCC; border-radius: 5px; }
                QListWidget::item { padding: 8px; border-bottom: 1px solid #EDEDED; }
                QListWidget::item:hover { background-color: #EDEDED; }
                QListWidget::item:selected { background-color: #0078D7; color: #FFFFFF; }
                QLineEdit { background-color: #FFFFFF; color: #000000; border: 1px solid #CCCCCC; padding: 8px; border-radius: 5px; }
                QLabel { color: #000000; }
            ''')