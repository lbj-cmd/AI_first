import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox, QGridLayout, QSpinBox, QDoubleSpinBox, QMessageBox
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from utils.visualization import plot_wavelength_distribution
from data.history_manager import HistoryManager

class FrequencyWavelengthCalculator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.history_manager = HistoryManager()
        self.calculation_results = []
    
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建标题
        title_label = QLabel('频率-波长计算器')
        title_label.setFont(QFont('Consolas', 16, QFont.Bold))
        main_layout.addWidget(title_label)
        
        # 创建输入区域
        input_group = QGroupBox('输入参数')
        input_layout = QGridLayout(input_group)
        
        # 频率输入
        freq_label = QLabel('频率:')
        self.freq_edit = QLineEdit()
        self.freq_edit.setPlaceholderText('输入频率值，支持逗号分隔批量输入')
        freq_unit_label = QLabel('单位:')
        self.freq_unit_combo = QComboBox()
        self.freq_unit_combo.addItems(['Hz', 'kHz', 'MHz', 'GHz', 'THz'])
        
        input_layout.addWidget(freq_label, 0, 0)
        input_layout.addWidget(self.freq_edit, 0, 1)
        input_layout.addWidget(freq_unit_label, 0, 2)
        input_layout.addWidget(self.freq_unit_combo, 0, 3)
        
        # 波长输入
        wave_label = QLabel('波长:')
        self.wave_edit = QLineEdit()
        self.wave_edit.setPlaceholderText('输入波长值，支持逗号分隔批量输入')
        wave_unit_label = QLabel('单位:')
        self.wave_unit_combo = QComboBox()
        self.wave_unit_combo.addItems(['m', 'cm', 'mm', 'μm', 'nm'])
        
        input_layout.addWidget(wave_label, 1, 0)
        input_layout.addWidget(self.wave_edit, 1, 1)
        input_layout.addWidget(wave_unit_label, 1, 2)
        input_layout.addWidget(self.wave_unit_combo, 1, 3)
        
        # 介质参数
        medium_label = QLabel('介质类型:')
        self.medium_combo = QComboBox()
        self.medium_combo.addItems(['真空', '空气', 'FR-4', '罗杰斯RO4003C', '氧化铝陶瓷'])
        self.medium_combo.currentTextChanged.connect(self.update_medium_params)
        
        permittivity_label = QLabel('相对介电常数:')
        self.permittivity_edit = QLineEdit()
        self.permittivity_edit.setText('1.0006')
        self.permittivity_edit.setReadOnly(True)
        
        permeability_label = QLabel('相对磁导率:')
        self.permeability_edit = QLineEdit()
        self.permeability_edit.setText('1.0')
        self.permeability_edit.setReadOnly(True)
        
        input_layout.addWidget(medium_label, 2, 0)
        input_layout.addWidget(self.medium_combo, 2, 1)
        input_layout.addWidget(permittivity_label, 2, 2)
        input_layout.addWidget(self.permittivity_edit, 2, 3)
        
        input_layout.addWidget(permeability_label, 3, 2)
        input_layout.addWidget(self.permeability_edit, 3, 3)
        
        main_layout.addWidget(input_group)
        
        # 创建计算按钮区域
        button_layout = QHBoxLayout()
        
        # 计算按钮
        calc_button = QPushButton('计算')
        calc_button.setIcon(QIcon('resources/icons/calculate.png'))
        calc_button.clicked.connect(self.calculate)
        button_layout.addWidget(calc_button)
        
        # 清除按钮
        clear_button = QPushButton('清除')
        clear_button.setIcon(QIcon('resources/icons/clear.png'))
        clear_button.clicked.connect(self.clear)
        button_layout.addWidget(clear_button)
        
        # 批量计算按钮
        batch_button = QPushButton('批量计算')
        batch_button.setIcon(QIcon('resources/icons/batch.png'))
        batch_button.clicked.connect(self.batch_calculate)
        button_layout.addWidget(batch_button)
        
        # 频段预设按钮
        preset_button = QPushButton('频段预设')
        preset_button.setIcon(QIcon('resources/icons/preset.png'))
        preset_button.clicked.connect(self.show_preset_bands)
        button_layout.addWidget(preset_button)
        
        main_layout.addLayout(button_layout)
        
        # 创建结果显示区域
        result_group = QGroupBox('计算结果')
        result_layout = QVBoxLayout(result_group)
        
        # 创建表格显示结果
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(['频率', '波长', '介质', '计算时间'])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        result_layout.addWidget(self.result_table)
        
        # 创建结果详情区域
        self.result_detail = QTextEdit()
        self.result_detail.setReadOnly(True)
        self.result_detail.setFont(QFont('Consolas', 10))
        result_layout.addWidget(self.result_detail)
        
        main_layout.addWidget(result_group)
        
        # 创建可视化区域
        visual_group = QGroupBox('可视化')
        visual_layout = QVBoxLayout(visual_group)
        
        # 创建图表画布
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        visual_layout.addWidget(self.canvas)
        
        # 图表控制按钮
        chart_button_layout = QHBoxLayout()
        
        # 频率分布按钮
        freq_dist_button = QPushButton('频率分布')
        freq_dist_button.clicked.connect(self.plot_frequency_distribution)
        chart_button_layout.addWidget(freq_dist_button)
        
        # 波长分布按钮
        wave_dist_button = QPushButton('波长分布')
        wave_dist_button.clicked.connect(self.plot_wavelength_distribution)
        chart_button_layout.addWidget(wave_dist_button)
        
        # 清空图表按钮
        clear_chart_button = QPushButton('清空图表')
        clear_chart_button.clicked.connect(self.clear_chart)
        chart_button_layout.addWidget(clear_chart_button)
        
        visual_layout.addLayout(chart_button_layout)
        
        main_layout.addWidget(visual_group)
        
        # 填充剩余空间
        main_layout.addStretch()
    
    def update_medium_params(self, medium):
        # 更新介质参数
        medium_params = {
            '真空': {'permittivity': 1.0, 'permeability': 1.0},
            '空气': {'permittivity': 1.0006, 'permeability': 1.0},
            'FR-4': {'permittivity': 4.4, 'permeability': 1.0},
            '罗杰斯RO4003C': {'permittivity': 3.38, 'permeability': 1.0},
            '氧化铝陶瓷': {'permittivity': 9.8, 'permeability': 1.0}
        }
        
        if medium in medium_params:
            self.permittivity_edit.setText(str(medium_params[medium]['permittivity']))
            self.permeability_edit.setText(str(medium_params[medium]['permeability']))
    
    def calculate(self):
        # 计算频率和波长
        freq_text = self.freq_edit.text().strip()
        wave_text = self.wave_edit.text().strip()
        
        # 检查输入
        if not freq_text and not wave_text:
            QMessageBox.warning(self, '警告', '请输入频率或波长值')
            return
        
        # 获取介质参数
        permittivity = float(self.permittivity_edit.text())
        permeability = float(self.permeability_edit.text())
        
        # 计算光速
        c0 = 299792458  # 真空中的光速
        c = c0 / np.sqrt(permittivity * permeability)
        
        results = []
        
        # 从频率计算波长
        if freq_text:
            try:
                freqs = [float(f) for f in freq_text.split(',')]
                freq_unit = self.freq_unit_combo.currentText()
                
                for freq in freqs:
                    # 转换为Hz
                    if freq_unit == 'kHz':
                        freq_hz = freq * 1e3
                    elif freq_unit == 'MHz':
                        freq_hz = freq * 1e6
                    elif freq_unit == 'GHz':
                        freq_hz = freq * 1e9
                    elif freq_unit == 'THz':
                        freq_hz = freq * 1e12
                    else:
                        freq_hz = freq
                    
                    # 计算波长
                    wavelength = c / freq_hz
                    
                    # 转换为合适的单位
                    wave_unit = self.wave_unit_combo.currentText()
                    if wave_unit == 'cm':
                        wavelength_unit = wavelength * 100
                    elif wave_unit == 'mm':
                        wavelength_unit = wavelength * 1000
                    elif wave_unit == 'μm':
                        wavelength_unit = wavelength * 1e6
                    elif wave_unit == 'nm':
                        wavelength_unit = wavelength * 1e9
                    else:
                        wavelength_unit = wavelength
                    
                    results.append({
                        'type': 'frequency',
                        'input': freq,
                        'input_unit': freq_unit,
                        'output': wavelength_unit,
                        'output_unit': wave_unit,
                        'medium': self.medium_combo.currentText()
                    })
            except ValueError:
                QMessageBox.warning(self, '警告', '频率输入格式错误')
                return
        
        # 从波长计算频率
        if wave_text:
            try:
                waves = [float(w) for w in wave_text.split(',')]
                wave_unit = self.wave_unit_combo.currentText()
                
                for wave in waves:
                    # 转换为m
                    if wave_unit == 'cm':
                        wave_m = wave / 100
                    elif wave_unit == 'mm':
                        wave_m = wave / 1000
                    elif wave_unit == 'μm':
                        wave_m = wave / 1e6
                    elif wave_unit == 'nm':
                        wave_m = wave / 1e9
                    else:
                        wave_m = wave
                    
                    # 计算频率
                    frequency = c / wave_m
                    
                    # 转换为合适的单位
                    freq_unit = self.freq_unit_combo.currentText()
                    if freq_unit == 'kHz':
                        frequency_unit = frequency / 1e3
                    elif freq_unit == 'MHz':
                        frequency_unit = frequency / 1e6
                    elif freq_unit == 'GHz':
                        frequency_unit = frequency / 1e9
                    elif freq_unit == 'THz':
                        frequency_unit = frequency / 1e12
                    else:
                        frequency_unit = frequency
                    
                    results.append({
                        'type': 'wavelength',
                        'input': wave,
                        'input_unit': wave_unit,
                        'output': frequency_unit,
                        'output_unit': freq_unit,
                        'medium': self.medium_combo.currentText()
                    })
            except ValueError:
                QMessageBox.warning(self, '警告', '波长输入格式错误')
                return
        
        # 显示结果
        self.display_results(results)
        
        # 保存到历史
        for result in results:
            self.history_manager.add_history(
                tool_name='频率-波长计算器',
                input_data=f"{result['input']} {result['input_unit']}",
                output_data=f"{result['output']:.6e} {result['output_unit']}",
                medium=result['medium'],
                calculation_type=result['type']
            )
    
    def batch_calculate(self):
        # 批量计算
        pass
    
    def show_preset_bands(self):
        # 显示频段预设
        preset_dialog = PresetBandsDialog(self)
        if preset_dialog.exec_() == preset_dialog.Accepted:
            selected_bands = preset_dialog.get_selected_bands()
            if selected_bands:
                # 将选中的频段添加到输入框
                freq_text = ','.join([str(band['frequency']) for band in selected_bands])
                self.freq_edit.setText(freq_text)
                self.freq_unit_combo.setCurrentText('GHz')
    
    def display_results(self, results):
        # 显示结果到表格
        self.result_table.setRowCount(len(results))
        self.calculation_results = results
        
        for i, result in enumerate(results):
            if result['type'] == 'frequency':
                freq_str = f"{result['input']} {result['input_unit']}"
                wave_str = f"{result['output']:.6e} {result['output_unit']}"
            else:
                wave_str = f"{result['input']} {result['input_unit']}"
                freq_str = f"{result['output']:.6e} {result['output_unit']}"
            
            self.result_table.setItem(i, 0, QTableWidgetItem(freq_str))
            self.result_table.setItem(i, 1, QTableWidgetItem(wave_str))
            self.result_table.setItem(i, 2, QTableWidgetItem(result['medium']))
            self.result_table.setItem(i, 3, QTableWidgetItem('刚刚'))
        
        # 显示结果详情
        detail_text = "计算结果详情：\n\n"
        for result in results:
            if result['type'] == 'frequency':
                detail_text += f"频率: {result['input']} {result['input_unit']} = {result['output']:.6e} {result['output_unit']} (波长)\n"
            else:
                detail_text += f"波长: {result['input']} {result['input_unit']} = {result['output']:.6e} {result['output_unit']} (频率)\n"
            
            detail_text += f"介质: {result['medium']}\n"
            detail_text += f"介电常数: {self.permittivity_edit.text()}, 磁导率: {self.permeability_edit.text()}\n"
            detail_text += "\n"
        
        self.result_detail.setText(detail_text)
    
    def plot_frequency_distribution(self):
        # 绘制频率分布图表
        if not self.calculation_results:
            QMessageBox.warning(self, '警告', '没有计算结果可以绘制')
            return
        
        # 提取频率数据
        frequencies = []
        for result in self.calculation_results:
            if result['type'] == 'frequency':
                # 转换为Hz
                freq = result['input']
                unit = result['input_unit']
                if unit == 'kHz':
                    freq *= 1e3
                elif unit == 'MHz':
                    freq *= 1e6
                elif unit == 'GHz':
                    freq *= 1e9
                elif unit == 'THz':
                    freq *= 1e12
                frequencies.append(freq)
            else:
                # 转换为Hz
                freq = result['output']
                unit = result['output_unit']
                if unit == 'kHz':
                    freq *= 1e3
                elif unit == 'MHz':
                    freq *= 1e6
                elif unit == 'GHz':
                    freq *= 1e9
                elif unit == 'THz':
                    freq *= 1e12
                frequencies.append(freq)
        
        if frequencies:
            plot_wavelength_distribution(self.figure, self.ax, frequencies, 'frequency')
            self.canvas.draw()
    
    def plot_wavelength_distribution(self):
        # 绘制波长分布图表
        if not self.calculation_results:
            QMessageBox.warning(self, '警告', '没有计算结果可以绘制')
            return
        
        # 提取波长数据
        wavelengths = []
        for result in self.calculation_results:
            if result['type'] == 'frequency':
                # 转换为m
                wave = result['output']
                unit = result['output_unit']
                if unit == 'cm':
                    wave /= 100
                elif unit == 'mm':
                    wave /= 1000
                elif unit == 'μm':
                    wave /= 1e6
                elif unit == 'nm':
                    wave /= 1e9
                wavelengths.append(wave)
            else:
                # 转换为m
                wave = result['input']
                unit = result['input_unit']
                if unit == 'cm':
                    wave /= 100
                elif unit == 'mm':
                    wave /= 1000
                elif unit == 'μm':
                    wave /= 1e6
                elif unit == 'nm':
                    wave /= 1e9
                wavelengths.append(wave)
        
        if wavelengths:
            plot_wavelength_distribution(self.figure, self.ax, wavelengths, 'wavelength')
            self.canvas.draw()
    
    def clear_chart(self):
        # 清空图表
        self.ax.clear()
        self.canvas.draw()
    
    def clear(self):
        # 清空输入和结果
        self.freq_edit.clear()
        self.wave_edit.clear()
        self.result_table.setRowCount(0)
        self.result_detail.clear()
        self.clear_chart()

class PresetBandsDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('频段预设')
        self.setGeometry(200, 200, 400, 300)
        
        # 预设频段数据
        self.preset_bands = [
            {'name': 'GSM 900', 'frequency': 900, 'unit': 'MHz', 'description': '全球移动通信系统'}, 
            {'name': 'GSM 1800', 'frequency': 1800, 'unit': 'MHz', 'description': '全球移动通信系统'}, 
            {'name': 'UMTS', 'frequency': 2100, 'unit': 'MHz', 'description': '通用移动通信系统'}, 
            {'name': 'LTE 800', 'frequency': 800, 'unit': 'MHz', 'description': '长期演进技术'}, 
            {'name': 'LTE 1800', 'frequency': 1800, 'unit': 'MHz', 'description': '长期演进技术'}, 
            {'name': 'LTE 2600', 'frequency': 2600, 'unit': 'MHz', 'description': '长期演进技术'}, 
            {'name': 'WiFi 2.4GHz', 'frequency': 2.4, 'unit': 'GHz', 'description': '无线局域网'}, 
            {'name': 'WiFi 5GHz', 'frequency': 5, 'unit': 'GHz', 'description': '无线局域网'}, 
            {'name': 'Bluetooth', 'frequency': 2.4, 'unit': 'GHz', 'description': '蓝牙技术'}, 
            {'name': 'GPS', 'frequency': 1.575, 'unit': 'GHz', 'description': '全球定位系统'}, 
            {'name': '5G NR FR1', 'frequency': 3.5, 'unit': 'GHz', 'description': '第五代移动通信'}, 
            {'name': '5G NR FR2', 'frequency': 28, 'unit': 'GHz', 'description': '第五代移动通信'} 
        ]
        
        self.init_ui()
    
    def init_ui(self):
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 创建表格
        self.band_table = QTableWidget()
        self.band_table.setColumnCount(3)
        self.band_table.setHorizontalHeaderLabels(['频段名称', '频率', '描述'])
        self.band_table.horizontalHeader().setStretchLastSection(True)
        self.band_table.setRowCount(len(self.preset_bands))
        
        for i, band in enumerate(self.preset_bands):
            self.band_table.setItem(i, 0, QTableWidgetItem(band['name']))
            self.band_table.setItem(i, 1, QTableWidgetItem(f"{band['frequency']} {band['unit']}"))
            self.band_table.setItem(i, 2, QTableWidgetItem(band['description']))
        
        layout.addWidget(self.band_table)
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        
        # 确定按钮
        ok_button = QPushButton('确定')
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        # 取消按钮
        cancel_button = QPushButton('取消')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def get_selected_bands(self):
        # 获取选中的频段
        selected_bands = []
        selected_rows = self.band_table.selectedItems()
        
        # 去重行号
        rows = list(set(item.row() for item in selected_rows))
        
        for row in rows:
            selected_bands.append(self.preset_bands[row])
        
        return selected_bands
    
    def accept(self):
        # 确定按钮点击
        self.close()
        return True
    
    def reject(self):
        # 取消按钮点击
        self.close()
        return False
    
    def exec_(self):
        # 执行对话框
        self.show()
        self.exec_()