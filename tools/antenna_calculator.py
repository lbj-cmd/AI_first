import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox, QGridLayout, QDoubleSpinBox, QMessageBox, QSplitter
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from data.history_manager import HistoryManager

class AntennaCalculator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.history_manager = HistoryManager()
        self.calculation_results = []
    
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建标题
        title_label = QLabel('天线参数计算器')
        title_label.setFont(QFont('Consolas', 16, QFont.Bold))
        main_layout.addWidget(title_label)
        
        # 创建输入区域
        input_group = QGroupBox('天线参数')
        input_layout = QGridLayout(input_group)
        
        # 天线类型
        antenna_type_label = QLabel('天线类型:')
        self.antenna_type_combo = QComboBox()
        self.antenna_type_combo.addItems(['偶极子天线', '贴片天线', '喇叭天线', '八木天线', '抛物面天线'])
        self.antenna_type_combo.currentTextChanged.connect(self.update_antenna_params)
        input_layout.addWidget(antenna_type_label, 0, 0)
        input_layout.addWidget(self.antenna_type_combo, 0, 1)
        
        # 频率输入
        freq_label = QLabel('频率 (GHz):')
        self.freq_edit = QDoubleSpinBox()
        self.freq_edit.setRange(0.1, 100.0)
        self.freq_edit.setValue(2.4)
        input_layout.addWidget(freq_label, 0, 2)
        input_layout.addWidget(self.freq_edit, 0, 3)
        
        # 天线长度
        length_label = QLabel('天线长度:')
        self.length_edit = QDoubleSpinBox()
        self.length_edit.setRange(0.01, 1000.0)
        self.length_edit.setValue(62.5)
        self.length_unit_combo = QComboBox()
        self.length_unit_combo.addItems(['mm', 'cm', 'm', 'λ'])
        length_layout = QHBoxLayout()
        length_layout.addWidget(self.length_edit)
        length_layout.addWidget(self.length_unit_combo)
        input_layout.addWidget(length_label, 1, 0)
        input_layout.addLayout(length_layout, 1, 1)
        
        # 天线宽度
        width_label = QLabel('天线宽度:')
        self.width_edit = QDoubleSpinBox()
        self.width_edit.setRange(0.01, 1000.0)
        self.width_edit.setValue(31.25)
        self.width_unit_combo = QComboBox()
        self.width_unit_combo.addItems(['mm', 'cm', 'm', 'λ'])
        width_layout = QHBoxLayout()
        width_layout.addWidget(self.width_edit)
        width_layout.addWidget(self.width_unit_combo)
        input_layout.addWidget(width_label, 1, 2)
        input_layout.addLayout(width_layout, 1, 3)
        
        # 介电常数
        er_label = QLabel('相对介电常数:')
        self.er_edit = QDoubleSpinBox()
        self.er_edit.setRange(1.0, 20.0)
        self.er_edit.setValue(4.4)
        input_layout.addWidget(er_label, 2, 0)
        input_layout.addWidget(self.er_edit, 2, 1)
        
        # 介质厚度
        thickness_label = QLabel('介质厚度:')
        self.thickness_edit = QDoubleSpinBox()
        self.thickness_edit.setRange(0.01, 100.0)
        self.thickness_edit.setValue(1.6)
        self.thickness_unit_combo = QComboBox()
        self.thickness_unit_combo.addItems(['mm', 'cm', 'm'])
        thickness_layout = QHBoxLayout()
        thickness_layout.addWidget(self.thickness_edit)
        thickness_layout.addWidget(self.thickness_unit_combo)
        input_layout.addWidget(thickness_label, 2, 2)
        input_layout.addLayout(thickness_layout, 2, 3)
        
        # 天线效率
        efficiency_label = QLabel('天线效率 (%):')
        self.efficiency_edit = QDoubleSpinBox()
        self.efficiency_edit.setRange(1.0, 100.0)
        self.efficiency_edit.setValue(90.0)
        input_layout.addWidget(efficiency_label, 3, 0)
        input_layout.addWidget(self.efficiency_edit, 3, 1)
        
        # 天线增益
        gain_label = QLabel('天线增益 (dBi):')
        self.gain_edit = QDoubleSpinBox()
        self.gain_edit.setRange(-10.0, 50.0)
        self.gain_edit.setValue(2.15)
        self.gain_edit.setReadOnly(True)
        input_layout.addWidget(gain_label, 3, 2)
        input_layout.addWidget(self.gain_edit, 3, 3)
        
        main_layout.addWidget(input_group)
        
        # 创建计算按钮区域
        button_layout = QHBoxLayout()
        
        # 计算按钮
        calc_button = QPushButton('计算天线参数')
        calc_button.setIcon(QIcon('resources/icons/calculate.png'))
        calc_button.clicked.connect(self.calculate_antenna_params)
        button_layout.addWidget(calc_button)
        
        # 设计天线按钮
        design_button = QPushButton('天线设计优化')
        design_button.setIcon(QIcon('resources/icons/design.png'))
        design_button.clicked.connect(self.design_antenna)
        button_layout.addWidget(design_button)
        
        # 清除按钮
        clear_button = QPushButton('清除')
        clear_button.setIcon(QIcon('resources/icons/clear.png'))
        clear_button.clicked.connect(self.clear)
        button_layout.addWidget(clear_button)
        
        main_layout.addLayout(button_layout)
        
        # 创建结果显示区域
        result_group = QGroupBox('计算结果')
        result_layout = QVBoxLayout(result_group)
        
        # 创建结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(['参数名称', '数值', '单位'])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        result_layout.addWidget(self.result_table)
        
        # 创建结果详情区域
        self.result_detail = QTextEdit()
        self.result_detail.setReadOnly(True)
        self.result_detail.setFont(QFont('Consolas', 10))
        result_layout.addWidget(self.result_detail)
        
        main_layout.addWidget(result_group)
        
        # 创建可视化区域
        visual_group = QGroupBox('天线辐射方向图')
        visual_layout = QVBoxLayout(visual_group)
        
        # 创建图表画布
        self.figure = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        visual_layout.addWidget(self.canvas)
        
        # 图表控制按钮
        chart_button_layout = QHBoxLayout()
        
        # 绘制2D方向图按钮
        plot_2d_button = QPushButton('绘制2D方向图')
        plot_2d_button.clicked.connect(self.plot_2d_radiation_pattern)
        chart_button_layout.addWidget(plot_2d_button)
        
        # 绘制3D方向图按钮
        plot_3d_button = QPushButton('绘制3D方向图')
        plot_3d_button.clicked.connect(self.plot_3d_radiation_pattern)
        chart_button_layout.addWidget(plot_3d_button)
        
        # 清空图表按钮
        clear_chart_button = QPushButton('清空图表')
        clear_chart_button.clicked.connect(self.clear_chart)
        chart_button_layout.addWidget(clear_chart_button)
        
        visual_layout.addLayout(chart_button_layout)
        
        main_layout.addWidget(visual_group)
        
        # 填充剩余空间
        main_layout.addStretch()
    
    def update_antenna_params(self, antenna_type):
        # 根据天线类型更新默认参数
        if antenna_type == '偶极子天线':
            self.length_edit.setValue(62.5)
            self.width_edit.setValue(31.25)
            self.er_edit.setValue(1.0)
            self.thickness_edit.setValue(0.1)
            self.efficiency_edit.setValue(90.0)
            self.gain_edit.setValue(2.15)
        elif antenna_type == '贴片天线':
            self.length_edit.setValue(31.25)
            self.width_edit.setValue(41.7)
            self.er_edit.setValue(4.4)
            self.thickness_edit.setValue(1.6)
            self.efficiency_edit.setValue(85.0)
            self.gain_edit.setValue(6.5)
        elif antenna_type == '喇叭天线':
            self.length_edit.setValue(150.0)
            self.width_edit.setValue(100.0)
            self.er_edit.setValue(1.0)
            self.thickness_edit.setValue(10.0)
            self.efficiency_edit.setValue(95.0)
            self.gain_edit.setValue(15.0)
        elif antenna_type == '八木天线':
            self.length_edit.setValue(120.0)
            self.width_edit.setValue(80.0)
            self.er_edit.setValue(1.0)
            self.thickness_edit.setValue(1.0)
            self.efficiency_edit.setValue(80.0)
            self.gain_edit.setValue(12.0)
        elif antenna_type == '抛物面天线':
            self.length_edit.setValue(1000.0)
            self.width_edit.setValue(1000.0)
            self.er_edit.setValue(1.0)
            self.thickness_edit.setValue(50.0)
            self.efficiency_edit.setValue(70.0)
            self.gain_edit.setValue(30.0)
    
    def calculate_antenna_params(self):
        # 计算天线参数
        try:
            # 获取输入参数
            antenna_type = self.antenna_type_combo.currentText()
            freq = self.freq_edit.value() * 1e9  # Hz
            length = self.length_edit.value()
            length_unit = self.length_unit_combo.currentText()
            width = self.width_edit.value()
            width_unit = self.width_unit_combo.currentText()
            er = self.er_edit.value()
            thickness = self.thickness_edit.value()
            thickness_unit = self.thickness_unit_combo.currentText()
            efficiency = self.efficiency_edit.value() / 100  # 转换为小数
            
            # 计算波长
            c0 = 299792458  # 真空中的光速
            lambda0 = c0 / freq  # 自由空间波长
            
            # 转换长度单位为米
            if length_unit == 'mm':
                length_m = length / 1000
            elif length_unit == 'cm':
                length_m = length / 100
            elif length_unit == 'm':
                length_m = length
            elif length_unit == 'λ':
                length_m = length * lambda0
            else:
                length_m = length / 1000  # 默认mm
            
            # 转换宽度单位为米
            if width_unit == 'mm':
                width_m = width / 1000
            elif width_unit == 'cm':
                width_m = width / 100
            elif width_unit == 'm':
                width_m = width
            elif width_unit == 'λ':
                width_m = width * lambda0
            else:
                width_m = width / 1000  # 默认mm
            
            # 转换厚度单位为米
            if thickness_unit == 'mm':
                thickness_m = thickness / 1000
            elif thickness_unit == 'cm':
                thickness_m = thickness / 100
            elif thickness_unit == 'm':
                thickness_m = thickness
            else:
                thickness_m = thickness / 1000  # 默认mm
            
            # 根据天线类型计算参数
            if antenna_type == '偶极子天线':
                params = self.calculate_dipole_antenna(freq, length_m, efficiency)
            elif antenna_type == '贴片天线':
                params = self.calculate_patch_antenna(freq, length_m, width_m, er, thickness_m, efficiency)
            elif antenna_type == '喇叭天线':
                params = self.calculate_horn_antenna(freq, length_m, width_m, efficiency)
            elif antenna_type == '八木天线':
                params = self.calculate_yagi_antenna(freq, length_m, width_m, efficiency)
            elif antenna_type == '抛物面天线':
                params = self.calculate_parabolic_antenna(freq, length_m, efficiency)
            else:
                params = {}
            
            # 添加通用参数
            params['天线类型'] = antenna_type
            params['频率'] = freq
            params['自由空间波长'] = lambda0
            params['天线长度'] = length_m
            params['天线宽度'] = width_m
            params['相对介电常数'] = er
            params['介质厚度'] = thickness_m
            params['天线效率'] = efficiency
            
            # 显示结果
            self.display_results(params)
            
            # 保存到历史
            self.history_manager.add_history(
                tool_name='天线参数计算器',
                input_data=f"天线类型: {antenna_type}, 频率: {freq/1e9} GHz",
                output_data=f"天线增益: {params['天线增益']:.2f} dBi, 波束宽度: {params['波束宽度H']:.2f}° × {params['波束宽度E']:.2f}°",
                calculation_type='antenna_parameters'
            )
            
        except Exception as e:
            QMessageBox.warning(self, '警告', f'计算错误: {str(e)}')
    
    def calculate_dipole_antenna(self, freq, length, efficiency):
        # 计算偶极子天线参数
        c0 = 299792458  # 真空中的光速
        lambda0 = c0 / freq  # 自由空间波长
        
        # 计算天线增益 (dBi)
        if length < lambda0 / 2:
            # 短偶极子
            gain = 2.15  # dBi
        else:
            # 半波偶极子
            gain = 2.15  # dBi
        
        # 计算波束宽度
        beamwidth_h = 78.0  # 水平波束宽度 (度)
        beamwidth_e = 78.0  # 垂直波束宽度 (度)
        
        # 计算有效面积
        effective_area = (lambda0**2 * 10**(gain/10)) / (4 * np.pi)
        
        # 计算输入阻抗
        input_impedance = 73.1 + 42.5j  # Ω
        
        return {
            '天线增益': gain,
            '波束宽度H': beamwidth_h,
            '波束宽度E': beamwidth_e,
            '有效面积': effective_area,
            '输入阻抗': input_impedance,
            '天线效率': efficiency
        }
    
    def calculate_patch_antenna(self, freq, length, width, er, thickness, efficiency):
        # 计算贴片天线参数
        c0 = 299792458  # 真空中的光速
        lambda0 = c0 / freq  # 自由空间波长
        
        # 计算有效介电常数
        er_eff = (er + 1) / 2 + (er - 1) / 2 * np.sqrt(1 + 12 * thickness / width)
        
        # 计算贴片长度扩展
        delta_l = (thickness / 0.001) * 0.412 * (er_eff + 0.3) * (width / thickness + 0.264) / ((er_eff - 0.258) * (width / thickness + 0.8))
        delta_l_m = delta_l * 0.001  # 转换为米
        
        # 计算实际贴片长度
        lambda_g = lambda0 / np.sqrt(er_eff)
        patch_length = lambda_g / 2 - 2 * delta_l_m
        
        # 计算天线增益 (dBi)
        gain = 10 * np.log10((60 * er_eff * (length / lambda0)**2 * width / lambda0) / ((er_eff + 1) * (1 + 0.25 * thickness / lambda_g)))
        gain_dbi = gain + 2.15  # 转换为dBi
        
        # 计算波束宽度
        beamwidth_h = 101 * lambda0 / width  # 水平波束宽度 (度)
        beamwidth_e = 101 * lambda0 / length  # 垂直波束宽度 (度)
        
        # 计算有效面积
        effective_area = (lambda0**2 * 10**(gain_dbi/10)) / (4 * np.pi)
        
        # 计算输入阻抗
        input_impedance = 377 * (width / length) * np.sqrt(er)  # Ω
        
        return {
            '天线增益': gain_dbi,
            '波束宽度H': beamwidth_h,
            '波束宽度E': beamwidth_e,
            '有效面积': effective_area,
            '输入阻抗': input_impedance,
            '有效介电常数': er_eff,
            '贴片长度': patch_length,
            '天线效率': efficiency
        }
    
    def calculate_horn_antenna(self, freq, length, width, efficiency):
        # 计算喇叭天线参数
        c0 = 299792458  # 真空中的光速
        lambda0 = c0 / freq  # 自由空间波长
        
        # 计算天线增益 (dBi)
        gain = 10 * np.log10((4 * np.pi * length * width) / lambda0**2)
        gain_dbi = gain * efficiency
        
        # 计算波束宽度
        beamwidth_h = 51 * lambda0 / width  # 水平波束宽度 (度)
        beamwidth_e = 51 * lambda0 / length  # 垂直波束宽度 (度)
        
        # 计算有效面积
        effective_area = (length * width) * efficiency
        
        # 计算输入阻抗
        input_impedance = 50  # Ω
        
        return {
            '天线增益': gain_dbi,
            '波束宽度H': beamwidth_h,
            '波束宽度E': beamwidth_e,
            '有效面积': effective_area,
            '输入阻抗': input_impedance,
            '天线效率': efficiency
        }
    
    def calculate_yagi_antenna(self, freq, length, width, efficiency):
        # 计算八木天线参数
        c0 = 299792458  # 真空中的光速
        lambda0 = c0 / freq  # 自由空间波长
        
        # 计算天线增益 (dBi)
        # 假设八木天线有6个元素
        gain_dbi = 12.0 * efficiency
        
        # 计算波束宽度
        beamwidth_h = 45  # 水平波束宽度 (度)
        beamwidth_e = 45  # 垂直波束宽度 (度)
        
        # 计算有效面积
        effective_area = (lambda0**2 * 10**(gain_dbi/10)) / (4 * np.pi)
        
        # 计算输入阻抗
        input_impedance = 50  # Ω
        
        return {
            '天线增益': gain_dbi,
            '波束宽度H': beamwidth_h,
            '波束宽度E': beamwidth_e,
            '有效面积': effective_area,
            '输入阻抗': input_impedance,
            '天线效率': efficiency
        }
    
    def calculate_parabolic_antenna(self, freq, diameter, efficiency):
        # 计算抛物面天线参数
        c0 = 299792458  # 真空中的光速
        lambda0 = c0 / freq  # 自由空间波长
        
        # 计算天线增益 (dBi)
        gain = 10 * np.log10((np.pi * diameter / lambda0)**2 * efficiency)
        gain_dbi = gain
        
        # 计算波束宽度
        beamwidth = 70 * lambda0 / diameter  # 波束宽度 (度)
        
        # 计算有效面积
        effective_area = (np.pi * (diameter / 2)**2) * efficiency
        
        # 计算输入阻抗
        input_impedance = 50  # Ω
        
        return {
            '天线增益': gain_dbi,
            '波束宽度H': beamwidth,
            '波束宽度E': beamwidth,
            '有效面积': effective_area,
            '输入阻抗': input_impedance,
            '天线效率': efficiency
        }
    
    def design_antenna(self):
        # 天线设计优化
        try:
            # 获取输入参数
            antenna_type = self.antenna_type_combo.currentText()
            freq = self.freq_edit.value() * 1e9  # Hz
            er = self.er_edit.value()
            
            # 根据天线类型进行设计优化
            if antenna_type == '偶极子天线':
                design_results = self.design_dipole_antenna(freq)
            elif antenna_type == '贴片天线':
                design_results = self.design_patch_antenna(freq, er)
            elif antenna_type == '喇叭天线':
                design_results = self.design_horn_antenna(freq)
            elif antenna_type == '八木天线':
                design_results = self.design_yagi_antenna(freq)
            elif antenna_type == '抛物面天线':
                design_results = self.design_parabolic_antenna(freq)
            else:
                design_results = {}
            
            # 显示设计结果
            self.display_design_results(design_results)
            
        except Exception as e:
            QMessageBox.warning(self, '警告', f'设计错误: {str(e)}')
    
    def design_dipole_antenna(self, freq):
        # 设计偶极子天线
        c0 = 299792458  # 真空中的光速
        lambda0 = c0 / freq  # 自由空间波长
        
        # 计算半波偶极子长度
        length = lambda0 / 2
        
        return {
            '天线类型': '偶极子天线',
            '设计频率': freq,
            '半波偶极子长度': length,
            '建议导线直径': length / 100,
            '预期增益': 2.15,
            '预期效率': 90.0
        }
    
    def design_patch_antenna(self, freq, er):
        # 设计贴片天线
        c0 = 299792458  # 真空中的光速
        lambda0 = c0 / freq  # 自由空间波长
        
        # 计算贴片宽度
        width = lambda0 / (2 * np.sqrt((er + 1) / 2))
        
        # 计算有效介电常数
        er_eff = (er + 1) / 2 + (er - 1) / 2 * np.sqrt(1 + 12 * 0.0016 / width)  # 假设介质厚度为1.6mm
        
        # 计算贴片长度
        lambda_g = lambda0 / np.sqrt(er_eff)
        length = lambda_g / 2
        
        return {
            '天线类型': '贴片天线',
            '设计频率': freq,
            '贴片宽度': width,
            '贴片长度': length,
            '相对介电常数': er,
            '建议介质厚度': 0.0016,
            '预期增益': 6.5,
            '预期效率': 85.0
        }
    
    def design_horn_antenna(self, freq):
        # 设计喇叭天线
        c0 = 299792458  # 真空中的光速
        lambda0 = c0 / freq  # 自由空间波长
        
        # 计算喇叭尺寸
        width = 3 * lambda0
        length = 5 * lambda0
        
        return {
            '天线类型': '喇叭天线',
            '设计频率': freq,
            '喇叭宽度': width,
            '喇叭长度': length,
            '预期增益': 15.0,
            '预期效率': 95.0
        }
    
    def design_yagi_antenna(self, freq):
        # 设计八木天线
        c0 = 299792458  # 真空中的光速
        lambda0 = c0 / freq  # 自由空间波长
        
        # 计算八木天线尺寸
        director_length = 0.47 * lambda0
        reflector_length = 0.52 * lambda0
        driven_element_length = 0.49 * lambda0
        spacing = 0.2 * lambda0
        
        return {
            '天线类型': '八木天线',
            '设计频率': freq,
            '引向器长度': director_length,
            '反射器长度': reflector_length,
            '辐射器长度': driven_element_length,
            '元素间距': spacing,
            '建议元素数量': 6,
            '预期增益': 12.0,
            '预期效率': 80.0
        }
    
    def design_parabolic_antenna(self, freq):
        # 设计抛物面天线
        c0 = 299792458  # 真空中的光速
        lambda0 = c0 / freq  # 自由空间波长
        
        # 计算抛物面直径（假设增益为30dBi）
        gain = 30.0
        efficiency = 0.7
        diameter = lambda0 * np.sqrt(4 * np.pi * 10**(gain/10) / (efficiency * 4 * np.pi))
        
        return {
            '天线类型': '抛物面天线',
            '设计频率': freq,
            '抛物面直径': diameter,
            '预期增益': gain,
            '预期效率': efficiency * 100
        }
    
    def display_results(self, params):
        # 显示计算结果到表格
        self.result_table.setRowCount(0)
        self.calculation_results.append(params)
        
        # 添加结果到表格
        self.add_result_row('天线类型', params['天线类型'], '')
        self.add_result_row('频率', params['频率']/1e9, 'GHz')
        self.add_result_row('自由空间波长', params['自由空间波长']*1e3, 'mm')
        self.add_result_row('天线长度', params['天线长度']*1e3, 'mm')
        self.add_result_row('天线宽度', params['天线宽度']*1e3, 'mm')
        self.add_result_row('相对介电常数', params['相对介电常数'], '')
        self.add_result_row('介质厚度', params['介质厚度']*1e3, 'mm')
        self.add_result_row('天线效率', params['天线效率']*100, '%')
        self.add_result_row('天线增益', params['天线增益'], 'dBi')
        self.add_result_row('水平波束宽度', params['波束宽度H'], '°')
        self.add_result_row('垂直波束宽度', params['波束宽度E'], '°')
        self.add_result_row('有效面积', params['有效面积']*1e6, 'cm²')
        self.add_result_row('输入阻抗', f"{params['输入阻抗'].real:.2f}+j{params['输入阻抗'].imag:.2f}" if hasattr(params['输入阻抗'], 'real') else params['输入阻抗'], 'Ω')
        
        # 添加特定天线类型的参数
        if '有效介电常数' in params:
            self.add_result_row('有效介电常数', params['有效介电常数'], '')
        if '贴片长度' in params:
            self.add_result_row('贴片长度', params['贴片长度']*1e3, 'mm')
        
        # 更新增益显示
        self.gain_edit.setValue(params['天线增益'])
        
        # 显示结果详情
        detail_text = "天线参数计算结果：\n\n"
        detail_text += f"天线类型: {params['天线类型']}\n"
        detail_text += f"频率: {params['频率']/1e9:.2f} GHz\n"
        detail_text += f"自由空间波长: {params['自由空间波长']*1e3:.2f} mm\n"
        detail_text += f"天线长度: {params['天线长度']*1e3:.2f} mm\n"
        detail_text += f"天线宽度: {params['天线宽度']*1e3:.2f} mm\n"
        detail_text += f"相对介电常数: {params['相对介电常数']:.2f}\n"
        detail_text += f"介质厚度: {params['介质厚度']*1e3:.2f} mm\n"
        detail_text += f"天线效率: {params['天线效率']*100:.2f}%\n"
        detail_text += f"天线增益: {params['天线增益']:.2f} dBi\n"
        detail_text += f"水平波束宽度: {params['波束宽度H']:.2f}°\n"
        detail_text += f"垂直波束宽度: {params['波束宽度E']:.2f}°\n"
        detail_text += f"有效面积: {params['有效面积']*1e6:.2f} cm²\n"
        detail_text += f"输入阻抗: {params['输入阻抗']:.2f} Ω\n"
        
        self.result_detail.setText(detail_text)
    
    def display_design_results(self, design_results):
        # 显示天线设计结果
        if not design_results:
            return
        
        result_text = "天线设计优化结果：\n\n"
        result_text += f"天线类型: {design_results['天线类型']}\n"
        result_text += f"设计频率: {design_results['设计频率']/1e9:.2f} GHz\n"
        
        if '半波偶极子长度' in design_results:
            result_text += f"半波偶极子长度: {design_results['半波偶极子长度']*1e3:.2f} mm\n"
            result_text += f"建议导线直径: {design_results['建议导线直径']*1e3:.2f} mm\n"
        
        if '贴片宽度' in design_results:
            result_text += f"贴片宽度: {design_results['贴片宽度']*1e3:.2f} mm\n"
            result_text += f"贴片长度: {design_results['贴片长度']*1e3:.2f} mm\n"
            result_text += f"相对介电常数: {design_results['相对介电常数']:.2f}\n"
            result_text += f"建议介质厚度: {design_results['建议介质厚度']*1e3:.2f} mm\n"
        
        if '喇叭宽度' in design_results:
            result_text += f"喇叭宽度: {design_results['喇叭宽度']*1e3:.2f} mm\n"
            result_text += f"喇叭长度: {design_results['喇叭长度']*1e3:.2f} mm\n"
        
        if '引向器长度' in design_results:
            result_text += f"引向器长度: {design_results['引向器长度']*1e3:.2f} mm\n"
            result_text += f"反射器长度: {design_results['反射器长度']*1e3:.2f} mm\n"
            result_text += f"辐射器长度: {design_results['辐射器长度']*1e3:.2f} mm\n"
            result_text += f"元素间距: {design_results['元素间距']*1e3:.2f} mm\n"
            result_text += f"建议元素数量: {design_results['建议元素数量']}\n"
        
        if '抛物面直径' in design_results:
            result_text += f"抛物面直径: {design_results['抛物面直径']*1e3:.2f} mm\n"
        
        result_text += f"预期增益: {design_results['预期增益']:.2f} dBi\n"
        result_text += f"预期效率: {design_results['预期效率']:.2f}%\n"
        
        self.result_detail.setText(result_text)
    
    def add_result_row(self, name, value, unit):
        # 添加结果行到表格
        row = self.result_table.rowCount()
        self.result_table.insertRow(row)
        self.result_table.setItem(row, 0, QTableWidgetItem(name))
        self.result_table.setItem(row, 1, QTableWidgetItem(str(value)))
        self.result_table.setItem(row, 2, QTableWidgetItem(unit))
    
    def plot_2d_radiation_pattern(self):
        # 绘制2D辐射方向图
        if not self.calculation_results:
            QMessageBox.warning(self, '警告', '没有计算结果可以绘制')
            return
        
        # 获取最新的计算结果
        params = self.calculation_results[-1]
        
        # 生成角度数据
        theta = np.linspace(0, 2 * np.pi, 360)
        
        # 生成辐射方向图数据
        if params['天线类型'] == '偶极子天线':
            # 偶极子天线辐射方向图
            pattern = np.sin(theta)**2
        elif params['天线类型'] == '贴片天线':
            # 贴片天线辐射方向图
            pattern = (np.sin(theta))**2 * (np.cos(np.pi * np.sin(theta) / 2))**2
        elif params['天线类型'] == '喇叭天线':
            # 喇叭天线辐射方向图
            pattern = (np.sin(theta))**2 * (np.cos(np.pi * np.sin(theta) / 2))**2
        elif params['天线类型'] == '八木天线':
            # 八木天线辐射方向图
            pattern = (np.sin(theta))**4
        elif params['天线类型'] == '抛物面天线':
            # 抛物面天线辐射方向图
            pattern = (np.sin(theta))**10
        else:
            # 默认辐射方向图
            pattern = np.sin(theta)**2
        
        # 绘制极坐标图
        self.figure.clear()
        ax = self.figure.add_subplot(111, polar=True)
        ax.plot(theta, pattern)
        ax.set_title(f'{params["天线类型"]} 2D辐射方向图')
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        self.canvas.draw()
    
    def plot_3d_radiation_pattern(self):
        # 绘制3D辐射方向图
        if not self.calculation_results:
            QMessageBox.warning(self, '警告', '没有计算结果可以绘制')
            return
        
        # 获取最新的计算结果
        params = self.calculation_results[-1]
        
        # 生成角度数据
        theta = np.linspace(0, 2 * np.pi, 180)
        phi = np.linspace(0, np.pi, 90)
        theta, phi = np.meshgrid(theta, phi)
        
        # 生成辐射方向图数据
        if params['天线类型'] == '偶极子天线':
            # 偶极子天线辐射方向图
            pattern = np.sin(phi)**2
        elif params['天线类型'] == '贴片天线':
            # 贴片天线辐射方向图
            pattern = (np.sin(phi))**2 * (np.cos(np.pi * np.sin(phi) / 2))**2
        elif params['天线类型'] == '喇叭天线':
            # 喇叭天线辐射方向图
            pattern = (np.sin(phi))**2 * (np.cos(np.pi * np.sin(phi) / 2))**2
        elif params['天线类型'] == '八木天线':
            # 八木天线辐射方向图
            pattern = (np.sin(phi))**4
        elif params['天线类型'] == '抛物面天线':
            # 抛物面天线辐射方向图
            pattern = (np.sin(phi))**10
        else:
            # 默认辐射方向图
            pattern = np.sin(phi)**2
        
        # 转换为笛卡尔坐标
        x = pattern * np.sin(phi) * np.cos(theta)
        y = pattern * np.sin(phi) * np.sin(theta)
        z = pattern * np.cos(phi)
        
        # 绘制3D图
        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='3d')
        ax.plot_surface(x, y, z, cmap='viridis')
        ax.set_title(f'{params["天线类型"]} 3D辐射方向图')
        self.canvas.draw()
    
    def clear_chart(self):
        # 清空图表
        self.figure.clear()
        self.canvas.draw()
    
    def clear(self):
        # 清空输入和结果
        self.antenna_type_combo.setCurrentText('偶极子天线')
        self.freq_edit.setValue(2.4)
        self.length_edit.setValue(62.5)
        self.length_unit_combo.setCurrentText('mm')
        self.width_edit.setValue(31.25)
        self.width_unit_combo.setCurrentText('mm')
        self.er_edit.setValue(4.4)
        self.thickness_edit.setValue(1.6)
        self.thickness_unit_combo.setCurrentText('mm')
        self.efficiency_edit.setValue(90.0)
        self.result_table.setRowCount(0)
        self.result_detail.clear()
        self.clear_chart()