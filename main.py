import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit, QTabWidget, QScrollArea, QFrame, QSplitter, QAction, QMenuBar, QMenu, QToolBar, QStatusBar
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
import qdarkstyle
from PyQt5.QtWidgets import QStyleFactory

# 导入工具模块
from tools.frequency_wavelength import FrequencyWavelengthCalculator
from tools.power_converter import PowerConverter
from tools.transmission_line import TransmissionLineCalculator
from tools.antenna_calculator import AntennaCalculator
from tools.filter_designer import FilterDesigner
from tools.link_budget import LinkBudgetAnalyzer

# 导入数据管理模块
from data.project_manager import ProjectManager
from data.history_manager import HistoryManager

# 导入知识库模块
from knowledge.knowledge_base import KnowledgeBase

# 导入工具函数
from utils.visualization import plot_wavelength_distribution
from utils.config import ConfigManager

class RFToolboxProfessional(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RF Toolbox Professional")
        self.setGeometry(100, 100, 1200, 800)
        
        # 初始化配置管理器
        self.config = ConfigManager()
        
        # 初始化项目管理器
        self.project_manager = ProjectManager()
        
        # 初始化历史管理器
        self.history_manager = HistoryManager()
        
        # 初始化知识库
        self.knowledge_base = KnowledgeBase()
        
        # 最近使用的工具
        self.recent_tools = self.history_manager.get_recent_tools(3)
        
        # 创建菜单和工具栏
        self.create_menu_bar()
        self.create_tool_bar()
        
        # 创建主布局
        self.create_main_layout()
        
        # 应用主题
        self.apply_theme()
        
        # 显示首页
        self.show_home()
    
    def create_menu_bar(self):
        # 创建菜单栏
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('&文件')
        
        # 新建项目
        new_project_action = QAction('新建项目', self)
        new_project_action.triggered.connect(self.project_manager.new_project)
        file_menu.addAction(new_project_action)
        
        # 打开项目
        open_project_action = QAction('打开项目', self)
        open_project_action.triggered.connect(self.project_manager.open_project)
        file_menu.addAction(open_project_action)
        
        # 保存项目
        save_project_action = QAction('保存项目', self)
        save_project_action.triggered.connect(self.project_manager.save_project)
        file_menu.addAction(save_project_action)
        
        # 导出项目
        export_menu = file_menu.addMenu('导出项目')
        export_csv_action = QAction('导出为CSV', self)
        export_csv_action.triggered.connect(lambda: self.project_manager.export_project('csv'))
        export_menu.addAction(export_csv_action)
        
        export_json_action = QAction('导出为JSON', self)
        export_json_action.triggered.connect(lambda: self.project_manager.export_project('json'))
        export_menu.addAction(export_json_action)
        
        export_pdf_action = QAction('导出为PDF', self)
        export_pdf_action.triggered.connect(lambda: self.project_manager.export_project('pdf'))
        export_menu.addAction(export_pdf_action)
        
        # 分隔线
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('&工具')
        
        # 频率-波长计算器
        freq_wave_action = QAction('频率-波长计算器', self)
        freq_wave_action.triggered.connect(self.show_freq_wavelength_calculator)
        tools_menu.addAction(freq_wave_action)
        
        # 功率单位换算
        power_conv_action = QAction('功率单位换算', self)
        power_conv_action.triggered.connect(self.show_power_converter)
        tools_menu.addAction(power_conv_action)
        
        # 传输线计算
        trans_line_action = QAction('传输线计算', self)
        trans_line_action.triggered.connect(self.show_transmission_line_calculator)
        tools_menu.addAction(trans_line_action)
        
        # 天线参数计算器
        antenna_action = QAction('天线参数计算器', self)
        antenna_action.triggered.connect(self.show_antenna_calculator)
        tools_menu.addAction(antenna_action)
        
        # 滤波器设计工具
        filter_action = QAction('滤波器设计工具', self)
        filter_action.triggered.connect(self.show_filter_designer)
        tools_menu.addAction(filter_action)
        
        # 射频链路预算分析
        link_budget_action = QAction('射频链路预算分析', self)
        link_budget_action.triggered.connect(self.show_link_budget_analyzer)
        tools_menu.addAction(link_budget_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('&视图')
        
        # 主题切换
        theme_menu = view_menu.addMenu('主题')
        
        # 浅色主题
        light_theme_action = QAction('浅色主题', self)
        light_theme_action.triggered.connect(lambda: self.set_theme('light'))
        theme_menu.addAction(light_theme_action)
        
        # 深色主题
        dark_theme_action = QAction('深色主题', self)
        dark_theme_action.triggered.connect(lambda: self.set_theme('dark'))
        theme_menu.addAction(dark_theme_action)
        
        # 跟随系统
        system_theme_action = QAction('跟随系统', self)
        system_theme_action.triggered.connect(lambda: self.set_theme('system'))
        theme_menu.addAction(system_theme_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('&帮助')
        
        # 内置教程
        tutorial_action = QAction('内置教程', self)
        tutorial_action.triggered.connect(self.show_tutorial)
        help_menu.addAction(tutorial_action)
        
        # 常见问题
        faq_action = QAction('常见问题', self)
        faq_action.triggered.connect(self.show_faq)
        help_menu.addAction(faq_action)
        
        # 关于
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_tool_bar(self):
        # 创建工具栏
        toolbar = self.addToolBar('工具栏')
        toolbar.setIconSize(QSize(16, 16))
        
        # 新建项目
        new_project_action = QAction(QIcon('resources/icons/new_project.png'), '新建项目', self)
        new_project_action.triggered.connect(self.project_manager.new_project)
        toolbar.addAction(new_project_action)
        
        # 打开项目
        open_project_action = QAction(QIcon('resources/icons/open_project.png'), '打开项目', self)
        open_project_action.triggered.connect(self.project_manager.open_project)
        toolbar.addAction(open_project_action)
        
        # 保存项目
        save_project_action = QAction(QIcon('resources/icons/save_project.png'), '保存项目', self)
        save_project_action.triggered.connect(self.project_manager.save_project)
        toolbar.addAction(save_project_action)
        
        toolbar.addSeparator()
        
        # 频率-波长计算器
        freq_wave_action = QAction(QIcon('resources/icons/frequency.png'), '频率-波长计算器', self)
        freq_wave_action.triggered.connect(self.show_freq_wavelength_calculator)
        toolbar.addAction(freq_wave_action)
        
        # 功率单位换算
        power_conv_action = QAction(QIcon('resources/icons/power.png'), '功率单位换算', self)
        power_conv_action.triggered.connect(self.show_power_converter)
        toolbar.addAction(power_conv_action)
        
        # 传输线计算
        trans_line_action = QAction(QIcon('resources/icons/transmission_line.png'), '传输线计算', self)
        trans_line_action.triggered.connect(self.show_transmission_line_calculator)
        toolbar.addAction(trans_line_action)
        
        # 天线参数计算器
        antenna_action = QAction(QIcon('resources/icons/antenna.png'), '天线参数计算器', self)
        antenna_action.triggered.connect(self.show_antenna_calculator)
        toolbar.addAction(antenna_action)
        
        # 滤波器设计工具
        filter_action = QAction(QIcon('resources/icons/filter.png'), '滤波器设计工具', self)
        filter_action.triggered.connect(self.show_filter_designer)
        toolbar.addAction(filter_action)
        
        # 射频链路预算分析
        link_budget_action = QAction(QIcon('resources/icons/link_budget.png'), '射频链路预算分析', self)
        link_budget_action.triggered.connect(self.show_link_budget_analyzer)
        toolbar.addAction(link_budget_action)
        
        toolbar.addSeparator()
        
        # 主题切换
        theme_action = QAction(QIcon('resources/icons/theme.png'), '主题切换', self)
        theme_menu = QMenu(self)
        
        light_theme_action = QAction('浅色主题', self)
        light_theme_action.triggered.connect(lambda: self.set_theme('light'))
        theme_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction('深色主题', self)
        dark_theme_action.triggered.connect(lambda: self.set_theme('dark'))
        theme_menu.addAction(dark_theme_action)
        
        system_theme_action = QAction('跟随系统', self)
        system_theme_action.triggered.connect(lambda: self.set_theme('system'))
        theme_menu.addAction(system_theme_action)
        
        theme_action.setMenu(theme_menu)
        toolbar.addAction(theme_action)
    
    def create_main_layout(self):
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建左侧导航栏
        self.nav_frame = QFrame()
        self.nav_frame.setFixedWidth(200)
        self.nav_frame.setFrameShape(QFrame.StyledPanel)
        
        # 创建导航布局
        nav_layout = QVBoxLayout(self.nav_frame)
        
        # 创建logo
        logo_label = QLabel('RF Toolbox')
        logo_label.setFont(QFont('Consolas', 16, QFont.Bold))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet('padding: 10px; margin-bottom: 20px;')
        nav_layout.addWidget(logo_label)
        
        # 创建导航按钮
        self.create_nav_buttons(nav_layout)
        
        # 创建搜索框
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_label = QLabel('搜索:')
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.search_tools)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        nav_layout.addWidget(search_frame)
        
        # 填充剩余空间
        nav_layout.addStretch()
        
        # 创建右侧内容区
        self.content_frame = QFrame()
        
        # 创建内容布局
        content_layout = QVBoxLayout(self.content_frame)
        
        # 创建面包屑导航
        self.breadcrumb_label = QLabel('首页')
        self.breadcrumb_label.setFont(QFont('Consolas', 10))
        content_layout.addWidget(self.breadcrumb_label)
        
        # 创建内容显示区
        self.content_display = QWidget()
        content_layout.addWidget(self.content_display)
        
        # 添加到主布局
        main_layout.addWidget(self.nav_frame)
        main_layout.addWidget(self.content_frame)
    
    def create_nav_buttons(self, layout):
        # 导航按钮数据
        nav_buttons = [
            ('首页', 'home', self.show_home),
            ('频率-波长计算', 'frequency', self.show_freq_wavelength_calculator),
            ('功率单位换算', 'power', self.show_power_converter),
            ('传输线计算', 'transmission_line', self.show_transmission_line_calculator),
            ('天线参数计算', 'antenna', self.show_antenna_calculator),
            ('滤波器设计', 'filter', self.show_filter_designer),
            ('链路预算分析', 'link_budget', self.show_link_budget_analyzer),
            ('知识库', 'knowledge', self.show_knowledge_base),
            ('计算历史', 'history', self.show_history),
            ('项目管理', 'project', self.show_project_manager)
        ]
        
        # 创建按钮
        self.nav_buttons = []
        for text, icon_name, callback in nav_buttons:
            button = QPushButton(text)
            button.setIcon(QIcon(f'resources/icons/{icon_name}.png'))
            button.setIconSize(QSize(16, 16))
            button.setStyleSheet('text-align: left; padding: 10px;')
            button.clicked.connect(callback)
            layout.addWidget(button)
            self.nav_buttons.append(button)
    
    def show_home(self):
        # 更新面包屑
        self.breadcrumb_label.setText('首页')
        
        # 清空内容区
        self.clear_content()
        
        # 创建首页布局
        home_layout = QVBoxLayout(self.content_display)
        
        # 创建标题
        title_label = QLabel('RF Toolbox Professional')
        title_label.setFont(QFont('Consolas', 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        home_layout.addWidget(title_label)
        
        # 创建描述
        desc_label = QLabel('覆盖射频工程全流程的专业设计平台')
        desc_label.setFont(QFont('Consolas', 12))
        desc_label.setAlignment(Qt.AlignCenter)
        home_layout.addWidget(desc_label)
        
        # 最近使用的工具
        if self.recent_tools:
            recent_label = QLabel('最近使用的工具')
            recent_label.setFont(QFont('Consolas', 14, QFont.Bold))
            home_layout.addWidget(recent_label)
            
            recent_frame = QFrame()
            recent_layout = QVBoxLayout(recent_frame)
            
            for tool_name, tool_icon, tool_callback in self.recent_tools:
                tool_button = QPushButton(tool_name)
                tool_button.setIcon(QIcon(f'resources/icons/{tool_icon}.png'))
                tool_button.setIconSize(QSize(16, 16))
                tool_button.setStyleSheet('padding: 10px; margin: 5px 0;')
                tool_button.clicked.connect(tool_callback)
                recent_layout.addWidget(tool_button)
            
            home_layout.addWidget(recent_frame)
        
        # 常用工具
        tools_label = QLabel('常用工具')
        tools_label.setFont(QFont('Consolas', 14, QFont.Bold))
        home_layout.addWidget(tools_label)
        
        tools_frame = QFrame()
        tools_layout = QGridLayout(tools_frame)
        
        # 常用工具数据
        common_tools = [
            ('频率-波长计算', 'frequency', self.show_freq_wavelength_calculator),
            ('功率单位换算', 'power', self.show_power_converter),
            ('传输线计算', 'transmission_line', self.show_transmission_line_calculator),
            ('天线参数计算', 'antenna', self.show_antenna_calculator),
            ('滤波器设计', 'filter', self.show_filter_designer),
            ('链路预算分析', 'link_budget', self.show_link_budget_analyzer)
        ]
        
        # 创建工具按钮
        for i, (text, icon_name, callback) in enumerate(common_tools):
            tool_button = QPushButton(text)
            tool_button.setIcon(QIcon(f'resources/icons/{icon_name}.png'))
            tool_button.setIconSize(QSize(16, 16))
            tool_button.setStyleSheet('padding: 15px;')
            tool_button.clicked.connect(callback)
            tools_layout.addWidget(tool_button, i//2, i%2)
        
        home_layout.addWidget(tools_frame)
        
        # 填充剩余空间
        home_layout.addStretch()
    
    def show_freq_wavelength_calculator(self):
        # 更新面包屑
        self.breadcrumb_label.setText('首页 > 频率-波长计算器')
        
        # 清空内容区
        self.clear_content()
        
        # 创建频率-波长计算器
        calculator = FrequencyWavelengthCalculator(self.content_display)
        
        # 添加到内容区
        layout = QVBoxLayout(self.content_display)
        layout.addWidget(calculator)
        
        # 记录到最近使用
        self.history_manager.add_recent_tool('频率-波长计算器', 'frequency', self.show_freq_wavelength_calculator)
    
    def show_power_converter(self):
        # 更新面包屑
        self.breadcrumb_label.setText('首页 > 功率单位换算')
        
        # 清空内容区
        self.clear_content()
        
        # 创建功率单位换算器
        converter = PowerConverter(self.content_display)
        
        # 添加到内容区
        layout = QVBoxLayout(self.content_display)
        layout.addWidget(converter)
        
        # 记录到最近使用
        self.history_manager.add_recent_tool('功率单位换算', 'power', self.show_power_converter)
    
    def show_transmission_line_calculator(self):
        # 更新面包屑
        self.breadcrumb_label.setText('首页 > 传输线计算')
        
        # 清空内容区
        self.clear_content()
        
        # 创建传输线计算器
        calculator = TransmissionLineCalculator(self.content_display)
        
        # 添加到内容区
        layout = QVBoxLayout(self.content_display)
        layout.addWidget(calculator)
        
        # 记录到最近使用
        self.history_manager.add_recent_tool('传输线计算', 'transmission_line', self.show_transmission_line_calculator)
    
    def show_antenna_calculator(self):
        # 更新面包屑
        self.breadcrumb_label.setText('首页 > 天线参数计算器')
        
        # 清空内容区
        self.clear_content()
        
        # 创建天线参数计算器
        calculator = AntennaCalculator(self.content_display)
        
        # 添加到内容区
        layout = QVBoxLayout(self.content_display)
        layout.addWidget(calculator)
        
        # 记录到最近使用
        self.history_manager.add_recent_tool('天线参数计算器', 'antenna', self.show_antenna_calculator)
    
    def show_filter_designer(self):
        # 更新面包屑
        self.breadcrumb_label.setText('首页 > 滤波器设计工具')
        
        # 清空内容区
        self.clear_content()
        
        # 创建滤波器设计工具
        designer = FilterDesigner(self.content_display)
        
        # 添加到内容区
        layout = QVBoxLayout(self.content_display)
        layout.addWidget(designer)
        
        # 记录到最近使用
        self.history_manager.add_recent_tool('滤波器设计工具', 'filter', self.show_filter_designer)
    
    def show_link_budget_analyzer(self):
        # 更新面包屑
        self.breadcrumb_label.setText('首页 > 射频链路预算分析')
        
        # 清空内容区
        self.clear_content()
        
        # 创建射频链路预算分析器
        analyzer = LinkBudgetAnalyzer(self.content_display)
        
        # 添加到内容区
        layout = QVBoxLayout(self.content_display)
        layout.addWidget(analyzer)
        
        # 记录到最近使用
        self.history_manager.add_recent_tool('射频链路预算分析', 'link_budget', self.show_link_budget_analyzer)
    
    def show_knowledge_base(self):
        # 更新面包屑
        self.breadcrumb_label.setText('首页 > 知识库')
        
        # 清空内容区
        self.clear_content()
        
        # 创建知识库界面
        knowledge_widget = self.knowledge_base.get_widget(self.content_display)
        
        # 添加到内容区
        layout = QVBoxLayout(self.content_display)
        layout.addWidget(knowledge_widget)
        
        # 记录到最近使用
        self.history_manager.add_recent_tool('知识库', 'knowledge', self.show_knowledge_base)
    
    def show_history(self):
        # 更新面包屑
        self.breadcrumb_label.setText('首页 > 计算历史')
        
        # 清空内容区
        self.clear_content()
        
        # 创建历史记录界面
        history_widget = self.history_manager.get_widget(self.content_display)
        
        # 添加到内容区
        layout = QVBoxLayout(self.content_display)
        layout.addWidget(history_widget)
        
        # 记录到最近使用
        self.history_manager.add_recent_tool('计算历史', 'history', self.show_history)
    
    def show_project_manager(self):
        # 更新面包屑
        self.breadcrumb_label.setText('首页 > 项目管理')
        
        # 清空内容区
        self.clear_content()
        
        # 创建项目管理界面
        project_widget = self.project_manager.get_widget(self.content_display)
        
        # 添加到内容区
        layout = QVBoxLayout(self.content_display)
        layout.addWidget(project_widget)
        
        # 记录到最近使用
        self.history_manager.add_recent_tool('项目管理', 'project', self.show_project_manager)
    
    def show_tutorial(self):
        # 显示内置教程
        pass
    
    def show_faq(self):
        # 显示常见问题
        pass
    
    def show_about(self):
        # 显示关于信息
        pass
    
    def clear_content(self):
        # 清空内容区
        for widget in self.content_display.findChildren(QWidget):
            widget.deleteLater()
    
    def search_tools(self, text):
        # 搜索工具
        pass
    
    def set_theme(self, theme):
        # 设置主题
        self.config.set_theme(theme)
        self.apply_theme()
    
    def apply_theme(self):
        # 应用主题
        theme = self.config.get_theme()
        
        if theme == 'dark':
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        else:
            app.setStyleSheet('')
            
        if theme == 'system':
            # 跟随系统主题
            if sys.platform == 'darwin':
                # macOS
                if app.style().objectName().lower().contains('dark'):
                    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
                else:
                    app.setStyleSheet('')
            elif sys.platform == 'win32':
                # Windows
                import ctypes
                try:
                    ctypes.windll.dwmapi.DwmIsCompositionEnabled()
                    if ctypes.windll.uxtheme.GetCurrentThemeName(None, 0, None, 0) == 0:
                        # Windows 10/11 深色主题
                        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
                    else:
                        app.setStyleSheet('')
                except:
                    app.setStyleSheet('')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('RF Toolbox Professional')
    
    # 设置默认字体
    font = QFont('Consolas', 10)
    app.setFont(font)
    
    # 创建主窗口
    main_window = RFToolboxProfessional()
    main_window.show()
    
    sys.exit(app.exec_())