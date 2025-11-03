from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
                             QMenuBar, QToolBar, QAction, QStatusBar, QLabel, QSplitter,
                             QMessageBox, QInputDialog, QFileDialog)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, QSize
import os
import sys

# 导入工具模块
from tools.frequency_wavelength import FrequencyWavelengthTool
from tools.power_converter import PowerConverterTool
from tools.transmission_line import TransmissionLineTool
from tools.antenna_calculator import AntennaCalculatorTool
from tools.filter_designer import FilterDesignerTool
from tools.link_budget import LinkBudgetTool

# 导入数据和知识库模块
from data.history_manager import HistoryManager
from knowledge.knowledge_base import KnowledgeBase

# 导入界面组件
from ui.theme_manager import ThemeManager
from ui.navigation_bar import NavigationBar
from ui.breadcrumb_bar import BreadcrumbBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 初始化数据和知识库
        self.history_manager = HistoryManager()
        self.knowledge_base = KnowledgeBase()
        
        # 初始化主题管理器
        self.theme_manager = ThemeManager()
        
        # 初始化工具列表
        self.tools = {}
        self.current_tool = None
        
        # 初始化界面
        self.init_ui()
        
        # 初始化工具
        self.init_tools()
    
    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle('射频工具箱专业版 - RF Toolbox Professional')
        self.setMinimumSize(1024, 768)
        self.resize(1200, 800)
        
        # 设置窗口图标
        if os.path.exists('icons/rf_toolbox.ico'):
            self.setWindowIcon(QIcon('icons/rf_toolbox.ico'))
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 创建面包屑导航
        self.breadcrumb_bar = BreadcrumbBar()
        self.breadcrumb_bar.item_clicked.connect(self.on_breadcrumb_clicked)
        main_layout.addWidget(self.breadcrumb_bar)
        
        # 创建主内容区域（导航栏 + 内容）
        self.create_main_content_area(main_layout)
        
        # 创建状态栏
        self.create_status_bar()
        
        # 设置默认主题
        self.theme_manager.set_theme('system')
        self.update_theme()
        
        # 设置默认工具
        self.show_home()
    
    def create_menu_bar(self):
        # 创建菜单栏
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu('文件')
        
        new_project_action = QAction('新建项目', self)
        new_project_action.setShortcut('Ctrl+N')
        new_project_action.triggered.connect(self.new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction('打开项目', self)
        open_project_action.setShortcut('Ctrl+O')
        open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(open_project_action)
        
        save_project_action = QAction('保存项目', self)
        save_project_action.setShortcut('Ctrl+S')
        save_project_action.triggered.connect(self.save_project)
        file_menu.addAction(save_project_action)
        
        file_menu.addSeparator()
        
        import_data_action = QAction('导入数据', self)
        import_data_action.triggered.connect(self.import_data)
        file_menu.addAction(import_data_action)
        
        export_data_action = QAction('导出数据', self)
        export_data_action.triggered.connect(self.export_data)
        file_menu.addAction(export_data_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menu_bar.addMenu('编辑')
        
        undo_action = QAction('撤销', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('重做', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction('剪切', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction('复制', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction('粘贴', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        # 视图菜单
        view_menu = menu_bar.addMenu('视图')
        
        # 主题子菜单
        theme_menu = view_menu.addMenu('主题')
        
        system_theme_action = QAction('跟随系统', self, checkable=True)
        system_theme_action.triggered.connect(lambda: self.set_theme('system'))
        theme_menu.addAction(system_theme_action)
        
        light_theme_action = QAction('浅色主题', self, checkable=True)
        light_theme_action.triggered.connect(lambda: self.set_theme('light'))
        theme_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction('深色主题', self, checkable=True)
        dark_theme_action.triggered.connect(lambda: self.set_theme('dark'))
        theme_menu.addAction(dark_theme_action)
        
        # 根据当前主题设置选中状态
        current_theme = self.theme_manager.get_current_theme()
        if current_theme == 'system':
            system_theme_action.setChecked(True)
        elif current_theme == 'light':
            light_theme_action.setChecked(True)
        else:
            dark_theme_action.setChecked(True)
        
        view_menu.addSeparator()
        
        full_screen_action = QAction('全屏', self, checkable=True)
        full_screen_action.setShortcut('F11')
        full_screen_action.triggered.connect(self.toggle_full_screen)
        view_menu.addAction(full_screen_action)
        
        # 工具菜单
        tools_menu = menu_bar.addMenu('工具')
        
        frequency_wavelength_action = QAction('频率-波长计算', self)
        frequency_wavelength_action.triggered.connect(lambda: self.show_tool('频率-波长计算'))
        tools_menu.addAction(frequency_wavelength_action)
        
        power_converter_action = QAction('功率单位换算', self)
        power_converter_action.triggered.connect(lambda: self.show_tool('功率单位换算'))
        tools_menu.addAction(power_converter_action)
        
        transmission_line_action = QAction('传输线参数计算', self)
        transmission_line_action.triggered.connect(lambda: self.show_tool('传输线参数计算'))
        tools_menu.addAction(transmission_line_action)
        
        antenna_calculator_action = QAction('天线参数计算', self)
        antenna_calculator_action.triggered.connect(lambda: self.show_tool('天线参数计算'))
        tools_menu.addAction(antenna_calculator_action)
        
        filter_designer_action = QAction('滤波器设计', self)
        filter_designer_action.triggered.connect(lambda: self.show_tool('滤波器设计'))
        tools_menu.addAction(filter_designer_action)
        
        link_budget_action = QAction('射频链路预算', self)
        link_budget_action.triggered.connect(lambda: self.show_tool('射频链路预算'))
        tools_menu.addAction(link_budget_action)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu('帮助')
        
        documentation_action = QAction('文档', self)
        documentation_action.triggered.connect(self.show_documentation)
        help_menu.addAction(documentation_action)
        
        tutorials_action = QAction('教程', self)
        tutorials_action.triggered.connect(self.show_tutorials)
        help_menu.addAction(tutorials_action)
        
        help_menu.addSeparator()
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_tool_bar(self):
        # 创建工具栏
        tool_bar = self.addToolBar('工具')
        tool_bar.setIconSize(QSize(24, 24))
        
        # 添加常用工具按钮
        frequency_wavelength_btn = QAction(QIcon('icons/frequency_wavelength.png'), '频率-波长计算', self)
        frequency_wavelength_btn.triggered.connect(lambda: self.show_tool('频率-波长计算'))
        tool_bar.addAction(frequency_wavelength_btn)
        
        power_converter_btn = QAction(QIcon('icons/power_converter.png'), '功率单位换算', self)
        power_converter_btn.triggered.connect(lambda: self.show_tool('功率单位换算'))
        tool_bar.addAction(power_converter_btn)
        
        transmission_line_btn = QAction(QIcon('icons/transmission_line.png'), '传输线参数计算', self)
        transmission_line_btn.triggered.connect(lambda: self.show_tool('传输线参数计算'))
        tool_bar.addAction(transmission_line_btn)
        
        antenna_btn = QAction(QIcon('icons/antenna.png'), '天线参数计算', self)
        antenna_btn.triggered.connect(lambda: self.show_tool('天线参数计算'))
        tool_bar.addAction(antenna_btn)
        
        filter_btn = QAction(QIcon('icons/filter.png'), '滤波器设计', self)
        filter_btn.triggered.connect(lambda: self.show_tool('滤波器设计'))
        tool_bar.addAction(filter_btn)
        
        link_budget_btn = QAction(QIcon('icons/link_budget.png'), '射频链路预算', self)
        link_budget_btn.triggered.connect(lambda: self.show_tool('射频链路预算'))
        tool_bar.addAction(link_budget_btn)
        
        tool_bar.addSeparator()
        
        history_btn = QAction(QIcon('icons/history.png'), '计算历史', self)
        history_btn.triggered.connect(lambda: self.show_tool('计算历史'))
        tool_bar.addAction(history_btn)
        
        knowledge_btn = QAction(QIcon('icons/knowledge.png'), '射频知识库', self)
        knowledge_btn.triggered.connect(lambda: self.show_tool('射频知识库'))
        tool_bar.addAction(knowledge_btn)
    
    def create_main_content_area(self, main_layout):
        # 创建主内容区域
        splitter = QSplitter(Qt.Horizontal)
        
        # 创建导航栏
        self.navigation_bar = NavigationBar()
        self.navigation_bar.tool_selected.connect(self.show_tool)
        self.navigation_bar.search_triggered.connect(self.on_search_triggered)
        
        # 创建内容堆叠窗口
        self.content_stack = QStackedWidget()
        
        # 添加到分隔器
        splitter.addWidget(self.navigation_bar)
        splitter.addWidget(self.content_stack)
        
        # 设置分隔器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        
        main_layout.addWidget(splitter)
    
    def create_status_bar(self):
        # 创建状态栏
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # 添加状态栏信息
        self.status_label = QLabel('就绪')
        status_bar.addWidget(self.status_label)
        
        # 添加主题显示
        self.theme_label = QLabel('主题: ' + self.theme_manager.get_current_theme())
        status_bar.addPermanentWidget(self.theme_label)
    
    def init_tools(self):
        # 初始化所有工具
        self.tools['频率-波长计算'] = FrequencyWavelengthTool(self.history_manager)
        self.tools['功率单位换算'] = PowerConverterTool(self.history_manager)
        self.tools['传输线参数计算'] = TransmissionLineTool(self.history_manager)
        self.tools['天线参数计算'] = AntennaCalculatorTool(self.history_manager)
        self.tools['滤波器设计'] = FilterDesignerTool(self.history_manager)
        self.tools['射频链路预算'] = LinkBudgetTool(self.history_manager)
        
        # 添加工具到内容堆叠窗口
        for tool_name, tool_widget in self.tools.items():
            self.content_stack.addWidget(tool_widget)
    
    def show_home(self):
        # 显示首页
        home_widget = QWidget()
        home_layout = QVBoxLayout(home_widget)
        
        # 标题
        title_label = QLabel('欢迎使用射频工具箱专业版')
        title_label.setFont(QFont('Arial', 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        home_layout.addWidget(title_label)
        
        home_layout.addStretch()
        
        # 最近使用工具
        recent_label = QLabel('最近使用工具')
        recent_label.setFont(QFont('Arial', 16, QFont.Bold))
        home_layout.addWidget(recent_label)
        
        recent_tools = self.navigation_bar.get_recent_tools()
        if recent_tools:
            for tool_name in recent_tools[:3]:  # 显示最近3个工具
                tool_btn = QPushButton(tool_name)
                tool_btn.setFont(QFont('Arial', 12))
                tool_btn.setStyleSheet('''
                    QPushButton { 
                        background-color: #0078D7; 
                        color: white; 
                        border: none; 
                        padding: 10px; 
                        border-radius: 5px; 
                        margin: 5px 0; 
                    }
                    QPushButton:hover { 
                        background-color: #005A9E; 
                    }
                ''')
                tool_btn.clicked.connect(lambda checked, tn=tool_name: self.show_tool(tn))
                home_layout.addWidget(tool_btn)
        else:
            no_recent_label = QLabel('暂无最近使用工具')
            no_recent_label.setFont(QFont('Arial', 12))
            no_recent_label.setStyleSheet('color: #666666;')
            home_layout.addWidget(no_recent_label)
        
        home_layout.addStretch()
        
        # 添加首页到内容堆叠窗口
        if not hasattr(self, 'home_index'):
            self.home_index = self.content_stack.addWidget(home_widget)
        else:
            # 如果已经存在，更新内容
            self.content_stack.removeWidget(self.content_stack.widget(self.home_index))
            self.home_index = self.content_stack.addWidget(home_widget)
        
        # 切换到首页
        self.content_stack.setCurrentIndex(self.home_index)
        
        # 更新面包屑
        self.breadcrumb_bar.set_path([('首页', '首页')])
        
        # 更新当前工具
        self.current_tool = None
    
    def show_tool(self, tool_name):
        # 显示指定工具
        if tool_name == '首页':
            self.show_home()
            return
        
        if tool_name in self.tools:
            # 切换到对应的工具界面
            tool_widget = self.tools[tool_name]
            index = self.content_stack.indexOf(tool_widget)
            self.content_stack.setCurrentIndex(index)
            
            # 更新面包屑
            self.breadcrumb_bar.set_path([('工具', '工具'), (tool_name, tool_name)])
            
            # 更新当前工具
            self.current_tool = tool_name
            
            # 更新状态栏
            self.status_label.setText(f'当前工具: {tool_name}')
            
            # 通知工具更新主题
            tool_widget.set_theme(self.theme_manager.get_current_theme())
        elif tool_name == '计算历史':
            self.show_history()
        elif tool_name == '射频知识库':
            self.show_knowledge_base()
        elif tool_name == '项目管理':
            self.show_project_manager()
        elif tool_name == '设置':
            self.show_settings()
    
    def show_history(self):
        # 显示计算历史
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        
        # 标题
        history_label = QLabel('计算历史')
        history_label.setFont(QFont('Arial', 18, QFont.Bold))
        history_layout.addWidget(history_label)
        
        # 这里可以添加历史记录的显示和搜索功能
        history_layout.addStretch()
        
        # 添加历史界面到内容堆叠窗口
        if not hasattr(self, 'history_index'):
            self.history_index = self.content_stack.addWidget(history_widget)
        else:
            # 如果已经存在，更新内容
            self.content_stack.removeWidget(self.content_stack.widget(self.history_index))
            self.history_index = self.content_stack.addWidget(history_widget)
        
        # 切换到历史界面
        self.content_stack.setCurrentIndex(self.history_index)
        
        # 更新面包屑
        self.breadcrumb_bar.set_path([('历史记录', '计算历史')])
        
        # 更新当前工具
        self.current_tool = '计算历史'
    
    def show_knowledge_base(self):
        # 显示知识库
        knowledge_widget = QWidget()
        knowledge_layout = QVBoxLayout(knowledge_widget)
        
        # 标题
        knowledge_label = QLabel('射频知识库')
        knowledge_label.setFont(QFont('Arial', 18, QFont.Bold))
        knowledge_layout.addWidget(knowledge_label)
        
        # 这里可以添加知识库的分类和搜索功能
        knowledge_layout.addStretch()
        
        # 添加知识库界面到内容堆叠窗口
        if not hasattr(self, 'knowledge_index'):
            self.knowledge_index = self.content_stack.addWidget(knowledge_widget)
        else:
            # 如果已经存在，更新内容
            self.content_stack.removeWidget(self.content_stack.widget(self.knowledge_index))
            self.knowledge_index = self.content_stack.addWidget(knowledge_widget)
        
        # 切换到知识库界面
        self.content_stack.setCurrentIndex(self.knowledge_index)
        
        # 更新面包屑
        self.breadcrumb_bar.set_path([('知识库', '射频知识库')])
        
        # 更新当前工具
        self.current_tool = '射频知识库'
    
    def show_project_manager(self):
        # 显示项目管理
        project_widget = QWidget()
        project_layout = QVBoxLayout(project_widget)
        
        # 标题
        project_label = QLabel('项目管理')
        project_label.setFont(QFont('Arial', 18, QFont.Bold))
        project_layout.addWidget(project_label)
        
        # 这里可以添加项目管理的功能
        project_layout.addStretch()
        
        # 添加项目管理界面到内容堆叠窗口
        if not hasattr(self, 'project_index'):
            self.project_index = self.content_stack.addWidget(project_widget)
        else:
            # 如果已经存在，更新内容
            self.content_stack.removeWidget(self.content_stack.widget(self.project_index))
            self.project_index = self.content_stack.addWidget(project_widget)
        
        # 切换到项目管理界面
        self.content_stack.setCurrentIndex(self.project_index)
        
        # 更新面包屑
        self.breadcrumb_bar.set_path([('项目管理', '项目管理')])
        
        # 更新当前工具
        self.current_tool = '项目管理'
    
    def show_settings(self):
        # 显示设置
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        # 标题
        settings_label = QLabel('设置')
        settings_label.setFont(QFont('Arial', 18, QFont.Bold))
        settings_layout.addWidget(settings_label)
        
        # 这里可以添加设置功能
        settings_layout.addStretch()
        
        # 添加设置界面到内容堆叠窗口
        if not hasattr(self, 'settings_index'):
            self.settings_index = self.content_stack.addWidget(settings_widget)
        else:
            # 如果已经存在，更新内容
            self.content_stack.removeWidget(self.content_stack.widget(self.settings_index))
            self.settings_index = self.content_stack.addWidget(settings_widget)
        
        # 切换到设置界面
        self.content_stack.setCurrentIndex(self.settings_index)
        
        # 更新面包屑
        self.breadcrumb_bar.set_path([('设置', '设置')])
        
        # 更新当前工具
        self.current_tool = '设置'
    
    def on_breadcrumb_clicked(self, tool_name):
        # 面包屑点击事件
        self.show_tool(tool_name)
    
    def on_search_triggered(self, keyword):
        # 搜索触发事件
        QMessageBox.information(self, '搜索结果', f'搜索: {keyword}')
    
    def set_theme(self, theme):
        # 设置主题
        self.theme_manager.set_theme(theme)
        self.update_theme()
        
        # 更新状态栏主题显示
        self.theme_label.setText('主题: ' + self.theme_manager.get_current_theme())
    
    def update_theme(self):
        # 更新界面主题
        theme = self.theme_manager.get_current_theme()
        
        # 更新导航栏主题
        self.navigation_bar.set_theme(theme)
        
        # 更新面包屑主题
        self.breadcrumb_bar.set_theme(theme)
        
        # 更新所有工具的主题
        for tool_widget in self.tools.values():
            tool_widget.set_theme(theme)
        
        # 更新主窗口样式
        if theme == 'dark':
            self.setStyleSheet('''
                QMainWindow { background-color: #1E1E1E; }
                QMenuBar { background-color: #2D2D30; color: #FFFFFF; }
                QMenuBar::item { background-color: #2D2D30; color: #FFFFFF; padding: 5px 10px; }
                QMenuBar::item:selected { background-color: #3E3E42; }
                QMenu { background-color: #2D2D30; color: #FFFFFF; }
                QMenu::item { background-color: #2D2D30; color: #FFFFFF; padding: 5px 20px; }
                QMenu::item:selected { background-color: #1E90FF; }
                QToolBar { background-color: #2D2D30; }
                QStatusBar { background-color: #2D2D30; color: #FFFFFF; }
            ''')
        else:
            self.setStyleSheet('''
                QMainWindow { background-color: #F0F0F0; }
                QMenuBar { background-color: #EDEDED; color: #000000; }
                QMenuBar::item { background-color: #EDEDED; color: #000000; padding: 5px 10px; }
                QMenuBar::item:selected { background-color: #0078D7; color: #FFFFFF; }
                QMenu { background-color: #FFFFFF; color: #000000; }
                QMenu::item { background-color: #FFFFFF; color: #000000; padding: 5px 20px; }
                QMenu::item:selected { background-color: #0078D7; color: #FFFFFF; }
                QToolBar { background-color: #EDEDED; }
                QStatusBar { background-color: #EDEDED; color: #000000; }
            ''')
    
    def toggle_full_screen(self):
        # 切换全屏
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def new_project(self):
        # 新建项目
        project_name, ok = QInputDialog.getText(self, '新建项目', '项目名称:')
        if ok and project_name:
            self.history_manager.add_project(project_name)
            QMessageBox.information(self, '新建项目', f'项目 "{project_name}" 已创建')
    
    def open_project(self):
        # 打开项目
        projects = self.history_manager.get_projects()
        if not projects:
            QMessageBox.information(self, '打开项目', '暂无项目')
            return
        
        project_names = [p['name'] for p in projects]
        project_name, ok = QInputDialog.getItem(self, '打开项目', '选择项目:', project_names, 0, False)
        if ok and project_name:
            QMessageBox.information(self, '打开项目', f'项目 "{project_name}" 已打开')
    
    def save_project(self):
        # 保存项目
        if self.current_tool:
            QMessageBox.information(self, '保存项目', f'当前工具 "{self.current_tool}" 的数据已保存')
        else:
            QMessageBox.information(self, '保存项目', '请先选择一个工具')
    
    def import_data(self):
        # 导入数据
        file_path, _ = QFileDialog.getOpenFileName(self, '导入数据', '', 'JSON Files (*.json);;CSV Files (*.csv);;All Files (*.*)')
        if file_path:
            QMessageBox.information(self, '导入数据', f'数据已从 "{file_path}" 导入')
    
    def export_data(self):
        # 导出数据
        if self.current_tool:
            file_path, _ = QFileDialog.getSaveFileName(self, '导出数据', '', 'JSON Files (*.json);;CSV Files (*.csv);;Text Files (*.txt)')
            if file_path:
                QMessageBox.information(self, '导出数据', f'数据已导出到 "{file_path}"')
        else:
            QMessageBox.information(self, '导出数据', '请先选择一个工具')
    
    def undo(self):
        # 撤销操作
        if self.current_tool and self.current_tool in self.tools:
            self.tools[self.current_tool].undo()
    
    def redo(self):
        # 重做操作
        if self.current_tool and self.current_tool in self.tools:
            self.tools[self.current_tool].redo()
    
    def cut(self):
        # 剪切操作
        if self.current_tool and self.current_tool in self.tools:
            self.tools[self.current_tool].cut()
    
    def copy(self):
        # 复制操作
        if self.current_tool and self.current_tool in self.tools:
            self.tools[self.current_tool].copy()
    
    def paste(self):
        # 粘贴操作
        if self.current_tool and self.current_tool in self.tools:
            self.tools[self.current_tool].paste()
    
    def show_documentation(self):
        # 显示文档
        QMessageBox.information(self, '文档', '射频工具箱专业版使用文档')
    
    def show_tutorials(self):
        # 显示教程
        QMessageBox.information(self, '教程', '射频工具箱专业版教程')
    
    def show_about(self):
        # 显示关于
        about_text = '''
        射频工具箱专业版
        RF Toolbox Professional
        
        版本: 2.0
        作者: 射频工程团队
        
        一个功能强大的射频工程设计工具
        包含频率-波长计算、功率转换、传输线计算、天线设计、滤波器设计和链路预算等功能
        '''
        QMessageBox.about(self, '关于', about_text)