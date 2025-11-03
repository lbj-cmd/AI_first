from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication

class ThemeManager:
    def __init__(self):
        self.current_theme = 'system'  # 'light', 'dark', or 'system'
        self.light_theme = self._create_light_theme()
        self.dark_theme = self._create_dark_theme()
        self.system_theme = self._detect_system_theme()
    
    def _create_light_theme(self):
        # 创建浅色主题
        palette = QPalette()
        
        # 背景色
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        
        # 基础颜色
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
        palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        
        # 文本颜色
        palette.setColor(QPalette.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.Link, QColor(0, 100, 200))
        
        # 按钮颜色
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        # 禁用颜色
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
        palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(180, 180, 180))
        
        return palette
    
    def _create_dark_theme(self):
        # 创建深色主题
        palette = QPalette()
        
        # 背景色
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        
        # 基础颜色
        palette.setColor(QPalette.Base, QColor(40, 40, 40))
        palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))
        palette.setColor(QPalette.ToolTipBase, QColor(60, 60, 60))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        
        # 文本颜色
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.Link, QColor(100, 180, 255))
        
        # 按钮颜色
        palette.setColor(QPalette.Button, QColor(50, 50, 50))
        palette.setColor(QPalette.Highlight, QColor(100, 180, 255))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        
        # 禁用颜色
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(100, 100, 100))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(100, 100, 100))
        palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
        
        return palette
    
    def _detect_system_theme(self):
        # 检测系统主题
        if hasattr(QApplication, 'styleHints') and hasattr(QApplication.styleHints(), 'colorScheme'):
            # Qt 6.5+ 支持系统主题检测
            color_scheme = QApplication.styleHints().colorScheme()
            return 'dark' if color_scheme == QApplication.Dark else 'light'
        else:
            # 对于旧版本Qt，默认返回浅色主题
            return 'light'
    
    def set_theme(self, theme):
        # 设置主题
        self.current_theme = theme
        
        if theme == 'system':
            detected_theme = self._detect_system_theme()
            palette = self.dark_theme if detected_theme == 'dark' else self.light_theme
        elif theme == 'dark':
            palette = self.dark_theme
        else:
            palette = self.light_theme
        
        QApplication.instance().setPalette(palette)
    
    def get_current_theme(self):
        # 获取当前主题
        return self.current_theme
    
    def is_dark_theme(self):
        # 检查是否为深色主题
        if self.current_theme == 'system':
            return self._detect_system_theme() == 'dark'
        return self.current_theme == 'dark'
    
    def get_theme_colors(self):
        # 获取当前主题的颜色
        if self.current_theme == 'system':
            detected_theme = self._detect_system_theme()
            return self._get_dark_theme_colors() if detected_theme == 'dark' else self._get_light_theme_colors()
        elif self.current_theme == 'dark':
            return self._get_dark_theme_colors()
        else:
            return self._get_light_theme_colors()
    
    def _get_light_theme_colors(self):
        # 获取浅色主题的颜色
        return {
            'background': '#F0F0F0',
            'window': '#FFFFFF',
            'text': '#000000',
            'accent': '#0078D7',
            'secondary': '#EDEDED',
            'border': '#CCCCCC',
            'success': '#00B050',
            'warning': '#FFC107',
            'error': '#FF0000',
            'info': '#17A2B8'
        }
    
    def _get_dark_theme_colors(self):
        # 获取深色主题的颜色
        return {
            'background': '#1E1E1E',
            'window': '#2D2D30',
            'text': '#FFFFFF',
            'accent': '#1E90FF',
            'secondary': '#3E3E42',
            'border': '#555555',
            'success': '#00B050',
            'warning': '#FFC107',
            'error': '#FF0000',
            'info': '#17A2B8'
        }