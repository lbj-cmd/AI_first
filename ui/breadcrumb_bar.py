from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal

class BreadcrumbBar(QWidget):
    item_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_path = []
        self.init_ui()
    
    def init_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(5)
        self.layout.addStretch()
        
        # 添加首页项
        self.add_home_item()
    
    def add_home_item(self):
        # 添加首页按钮
        home_btn = QPushButton("首页")
        home_btn.setFont(QFont('Arial', 10))
        home_btn.setStyleSheet('''
            QPushButton { 
                background: transparent; 
                border: none; 
                color: #0078D7; 
                padding: 2px 5px; 
                border-radius: 3px;
            }
            QPushButton:hover { 
                background-color: rgba(0, 120, 215, 0.1); 
            }
        ''')
        home_btn.clicked.connect(lambda: self.item_clicked.emit("首页"))
        self.layout.insertWidget(0, home_btn)
    
    def set_path(self, path):
        # 设置面包屑路径
        self.clear()
        self.add_home_item()
        
        # 添加新路径项
        for name, tool_name in path:
            # 添加分隔符
            separator = QLabel(">")
            separator.setFont(QFont('Arial', 10))
            separator.setStyleSheet('color: #666666;')
            self.layout.insertWidget(self.layout.count() - 1, separator)
            
            # 添加项按钮
            item_btn = QPushButton(name)
            item_btn.setFont(QFont('Arial', 10))
            item_btn.setStyleSheet('''
                QPushButton { 
                    background: transparent; 
                    border: none; 
                    color: #0078D7; 
                    padding: 2px 5px; 
                    border-radius: 3px;
                }
                QPushButton:hover { 
                    background-color: rgba(0, 120, 215, 0.1); 
                }
            ''')
            item_btn.clicked.connect(lambda checked, tn=tool_name: self.item_clicked.emit(tn))
            self.layout.insertWidget(self.layout.count() - 1, item_btn)
            
            # 保存到当前路径
            self.current_path.append((name, tool_name))
    
    def clear(self):
        # 清空面包屑（保留最后一个拉伸项）
        while self.layout.count() > 1:
            widget = self.layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        self.current_path = []
    
    def set_theme(self, theme):
        # 根据主题更新样式
        if theme == 'dark':
            home_btn = self.layout.itemAt(0).widget()
            home_btn.setStyleSheet('''
                QPushButton { 
                    background: transparent; 
                    border: none; 
                    color: #1E90FF; 
                    padding: 2px 5px; 
                    border-radius: 3px;
                }
                QPushButton:hover { 
                    background-color: rgba(30, 144, 255, 0.1); 
                }
            ''')
            
            # 更新分隔符和项
            for i in range(1, self.layout.count() - 1):
                widget = self.layout.itemAt(i).widget()
                if isinstance(widget, QLabel):
                    widget.setStyleSheet('color: #AAAAAA;')
                elif isinstance(widget, QPushButton):
                    widget.setStyleSheet('''
                        QPushButton { 
                            background: transparent; 
                            border: none; 
                            color: #1E90FF; 
                            padding: 2px 5px; 
                            border-radius: 3px;
                        }
                        QPushButton:hover { 
                            background-color: rgba(30, 144, 255, 0.1); 
                        }
                    ''')
        else:
            home_btn = self.layout.itemAt(0).widget()
            home_btn.setStyleSheet('''
                QPushButton { 
                    background: transparent; 
                    border: none; 
                    color: #0078D7; 
                    padding: 2px 5px; 
                    border-radius: 3px;
                }
                QPushButton:hover { 
                    background-color: rgba(0, 120, 215, 0.1); 
                }
            ''')
            
            # 更新分隔符和项
            for i in range(1, self.layout.count() - 1):
                widget = self.layout.itemAt(i).widget()
                if isinstance(widget, QLabel):
                    widget.setStyleSheet('color: #666666;')
                elif isinstance(widget, QPushButton):
                    widget.setStyleSheet('''
                        QPushButton { 
                            background: transparent; 
                            border: none; 
                            color: #0078D7; 
                            padding: 2px 5px; 
                            border-radius: 3px;
                        }
                        QPushButton:hover { 
                            background-color: rgba(0, 120, 215, 0.1); 
                        }
                    ''')
    
    def get_current_path(self):
        # 获取当前路径
        return self.current_path