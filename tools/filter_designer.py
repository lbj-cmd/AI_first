import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox, QGridLayout, QDoubleSpinBox, QMessageBox, QSplitter, QSpinBox, QTabWidget
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from data.history_manager import HistoryManager
from scipy.signal import butter, cheby1, cheby2, ellip, bessel, freqs, freqz

class FilterDesigner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.history_manager = HistoryManager()
        self.filter_results = []
    
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建标题
        title_label = QLabel('滤波器设计工具')
        title_label.setFont(QFont('Consolas', 16, QFont.Bold))
        main_layout.addWidget(title_label)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 创建设计标签
        design_tab = QWidget()
        design_layout = QVBoxLayout(design_tab)
        
        # 创建输入区域
        input_group = QGroupBox('滤波器参数')
        input_layout = QGridLayout(input_group)
        
        # 滤波器类型
        filter_type_label = QLabel('滤波器类型:')
        self.filter_type_combo = QComboBox()
        self.filter_type_combo.addItems(['低通', '高通', '带通', '带阻'])
        self.filter_type_combo.currentTextChanged.connect(self.update_filter_params)
        input_layout.addWidget(filter_type_label, 0, 0)
        input_layout.addWidget(self.filter_type_combo, 0, 1)
        
        # 滤波器响应
        response_label = QLabel('滤波器响应:')
        self.response_combo = QComboBox()
        self.response_combo.addItems(['巴特沃斯', '切比雪夫I型', '切比雪夫II型', '椭圆', '贝塞尔'])
        input_layout.addWidget(response_label, 0, 2)
        input_layout.addWidget(self.response_combo, 0, 3)
        
        # 滤波器阶数
        order_label = QLabel('滤波器阶数:')
        self.order_spin = QSpinBox()
        self.order_spin.setRange(1, 20)
        self.order_spin.setValue(4)
        input_layout.addWidget(order_label, 1, 0)
        input_layout.addWidget(self.order_spin, 1, 1)
        
        # 截止频率1
        cutoff1_label = QLabel('截止频率1 (GHz):')
        self.cutoff1_edit = QDoubleSpinBox()
        self.cutoff1_edit.setRange(0.1, 100.0)
        self.cutoff1_edit.setValue(1.0)
        input_layout.addWidget(cutoff1_label, 1, 2)
        input_layout.addWidget(self.cutoff1_edit, 1, 3)
        
        # 截止频率2
        cutoff2_label = QLabel('截止频率2 (GHz):')
        self.cutoff2_edit = QDoubleSpinBox()
        self.cutoff2_edit.setRange(0.1, 100.0)
        self.cutoff2_edit.setValue(2.0)
        self.cutoff2_edit.setEnabled(False)
        input_layout.addWidget(cutoff2_label, 2, 2)
        input_layout.addWidget(self.cutoff2_edit, 2, 3)
        
        # 通带波纹
        ripple_label = QLabel('通带波纹 (dB):')
        self.ripple_edit = QDoubleSpinBox()
        self.ripple_edit.setRange(0.1, 10.0)
        self.ripple_edit.setValue(1.0)
        input_layout.addWidget(ripple_label, 2, 0)
        input_layout.addWidget(self.ripple_edit, 2, 1)
        
        # 阻带衰减
        attenuation_label = QLabel('阻带衰减 (dB):')
        self.attenuation_edit = QDoubleSpinBox()
        self.attenuation_edit.setRange(10.0, 100.0)
        self.attenuation_edit.setValue(40.0)
        input_layout.addWidget(attenuation_label, 3, 0)
        input_layout.addWidget(self.attenuation_edit, 3, 1)
        
        # 特征阻抗
        z0_label = QLabel('特征阻抗 (Ω):')
        self.z0_edit = QDoubleSpinBox()
        self.z0_edit.setRange(50.0, 75.0)
        self.z0_edit.setValue(50.0)
        input_layout.addWidget(z0_label, 3, 2)
        input_layout.addWidget(self.z0_edit, 3, 3)
        
        design_layout.addWidget(input_group)
        
        # 创建计算按钮区域
        button_layout = QHBoxLayout()
        
        # 设计滤波器按钮
        design_button = QPushButton('设计滤波器')
        design_button.setIcon(QIcon('resources/icons/design.png'))
        design_button.clicked.connect(self.design_filter)
        button_layout.addWidget(design_button)
        
        # 优化滤波器按钮
        optimize_button = QPushButton('优化设计')
        optimize_button.setIcon(QIcon('resources/icons/optimize.png'))
        optimize_button.clicked.connect(self.optimize_filter)
        button_layout.addWidget(optimize_button)
        
        # 清除按钮
        clear_button = QPushButton('清除')
        clear_button.setIcon(QIcon('resources/icons/clear.png'))
        clear_button.clicked.connect(self.clear)
        button_layout.addWidget(clear_button)
        
        design_layout.addLayout(button_layout)
        
        # 创建结果显示区域
        result_group = QGroupBox('设计结果')
        result_layout = QVBoxLayout(result_group)
        
        # 创建结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(['元件类型', '元件值', '单位', '位置'])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        result_layout.addWidget(self.result_table)
        
        # 创建结果详情区域
        self.result_detail = QTextEdit()
        self.result_detail.setReadOnly(True)
        self.result_detail.setFont(QFont('Consolas', 10))
        result_layout.addWidget(self.result_detail)
        
        design_layout.addWidget(result_group)
        
        tab_widget.addTab(design_tab, '滤波器设计')
        
        # 创建分析标签
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        
        # 创建可视化区域
        visual_group = QGroupBox('频率响应')
        visual_layout = QVBoxLayout(visual_group)
        
        # 创建图表画布
        self.figure = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        visual_layout.addWidget(self.canvas)
        
        # 图表控制按钮
        chart_button_layout = QHBoxLayout()
        
        # 绘制幅频响应按钮
        plot_mag_button = QPushButton('绘制幅频响应')
        plot_mag_button.clicked.connect(self.plot_magnitude_response)
        chart_button_layout.addWidget(plot_mag_button)
        
        # 绘制相频响应按钮
        plot_phase_button = QPushButton('绘制相频响应')
        plot_phase_button.clicked.connect(self.plot_phase_response)
        chart_button_layout.addWidget(plot_phase_button)
        
        # 绘制群延迟按钮
        plot_group_button = QPushButton('绘制群延迟')
        plot_group_button.clicked.connect(self.plot_group_delay)
        chart_button_layout.addWidget(plot_group_button)
        
        # 清空图表按钮
        clear_chart_button = QPushButton('清空图表')
        clear_chart_button.clicked.connect(self.clear_chart)
        chart_button_layout.addWidget(clear_chart_button)
        
        visual_layout.addLayout(chart_button_layout)
        
        analysis_layout.addWidget(visual_group)
        
        tab_widget.addTab(analysis_tab, '频率响应分析')
        
        main_layout.addWidget(tab_widget)
        
        # 填充剩余空间
        main_layout.addStretch()
    
    def update_filter_params(self, filter_type):
        # 根据滤波器类型更新参数
        if filter_type in ['带通', '带阻']:
            self.cutoff2_edit.setEnabled(True)
        else:
            self.cutoff2_edit.setEnabled(False)
    
    def design_filter(self):
        # 设计滤波器
        try:
            # 获取输入参数
            filter_type = self.filter_type_combo.currentText()
            response = self.response_combo.currentText()
            order = self.order_spin.value()
            cutoff1 = self.cutoff1_edit.value() * 1e9  # Hz
            cutoff2 = self.cutoff2_edit.value() * 1e9  # Hz
            ripple = self.ripple_edit.value()  # dB
            attenuation = self.attenuation_edit.value()  # dB
            z0 = self.z0_edit.value()  # Ω
            
            # 确定滤波器类型
            btype = self.get_filter_type(filter_type)
            
            # 确定截止频率
            if filter_type in ['低通', '高通']:
                Wn = cutoff1 / (2 * np.pi)  # rad/s
            else:
                Wn = [cutoff1 / (2 * np.pi), cutoff2 / (2 * np.pi)]  # rad/s
            
            # 设计滤波器
            if response == '巴特沃斯':
                b, a = butter(order, Wn, btype=btype, analog=True)
            elif response == '切比雪夫I型':
                b, a = cheby1(order, ripple, Wn, btype=btype, analog=True)
            elif response == '切比雪夫II型':
                b, a = cheby2(order, attenuation, Wn, btype=btype, analog=True)
            elif response == '椭圆':
                b, a = ellip(order, ripple, attenuation, Wn, btype=btype, analog=True)
            elif response == '贝塞尔':
                b, a = bessel(order, Wn, btype=btype, analog=True, norm='delay')
            else:
                b, a = butter(order, Wn, btype=btype, analog=True)
            
            # 计算元件值
            elements = self.calculate_filter_elements(b, a, z0, filter_type)
            
            # 保存结果
            result = {
                'filter_type': filter_type,
                'response': response,
                'order': order,
                'cutoff1': cutoff1,
                'cutoff2': cutoff2,
                'ripple': ripple,
                'attenuation': attenuation,
                'z0': z0,
                'b': b,
                'a': a,
                'elements': elements
            }
            
            self.filter_results.append(result)
            
            # 显示结果
            self.display_results(result)
            
            # 保存到历史
            self.history_manager.add_history(
                tool_name='滤波器设计工具',
                input_data=f"类型: {filter_type}, 响应: {response}, 阶数: {order}, 截止频率: {cutoff1/1e9} GHz",
                output_data=f"滤波器设计完成，包含 {len(elements)} 个元件",
                calculation_type='filter_design'
            )
            
        except Exception as e:
            QMessageBox.warning(self, '警告', f'设计错误: {str(e)}')
    
    def get_filter_type(self, filter_type):
        # 转换滤波器类型为scipy.signal所需的格式
        if filter_type == '低通':
            return 'lowpass'
        elif filter_type == '高通':
            return 'highpass'
        elif filter_type == '带通':
            return 'bandpass'
        elif filter_type == '带阻':
            return 'bandstop'
        else:
            return 'lowpass'
    
    def calculate_filter_elements(self, b, a, z0, filter_type):
        # 计算滤波器元件值
        elements = []
        
        # 归一化传输函数
        b_norm = b / b[0]
        a_norm = a / a[0]
        
        # 实现巴特沃斯滤波器的元件计算
        if self.response_combo.currentText() == '巴特沃斯':
            # 使用巴特沃斯滤波器的设计公式
            for i in range(1, len(b_norm)):
                if i % 2 == 1:
                    # 串联部分
                    if i == 1:
                        # 第一个元件
                        r = z0
                        elements.append({'type': 'R', 'value': r, 'unit': 'Ω', 'position': '输入'})
                    
                    # 计算电感和电容
                    if filter_type in ['低通', '带通']:
                        l = z0 * b_norm[i]
                        c = 1 / (z0 * a_norm[i])
                        
                        elements.append({'type': 'L', 'value': l, 'unit': 'H', 'position': f'串联{i}'})
                        elements.append({'type': 'C', 'value': c, 'unit': 'F', 'position': f'并联{i}'})
                    elif filter_type in ['高通', '带阻']:
                        c = 1 / (z0 * b_norm[i])
                        l = z0 / a_norm[i]
                        
                        elements.append({'type': 'C', 'value': c, 'unit': 'F', 'position': f'串联{i}'})
                        elements.append({'type': 'L', 'value': l, 'unit': 'H', 'position': f'并联{i}'})
        
        # 转换单位为更实用的单位
        for element in elements:
            if element['type'] == 'L':
                if element['value'] < 1e-6:
                    element['value'] *= 1e9
                    element['unit'] = 'nH'
                else:
                    element['value'] *= 1e6
                    element['unit'] = 'μH'
            elif element['type'] == 'C':
                if element['value'] < 1e-9:
                    element['value'] *= 1e12
                    element['unit'] = 'pF'
                else:
                    element['value'] *= 1e9
                    element['unit'] = 'nF'
        
        return elements
    
    def optimize_filter(self):
        # 优化滤波器设计
        try:
            # 获取当前设计结果
            if not self.filter_results:
                QMessageBox.warning(self, '警告', '没有设计结果可以优化')
                return
            
            current_result = self.filter_results[-1]
            
            # 简单的优化算法：调整阶数以满足阻带衰减要求
            order = current_result['order']
            attenuation = current_result['attenuation']
            
            # 计算当前阻带衰减
            w, h = freqs(current_result['b'], current_result['a'], worN=np.logspace(0, 12, 1000))
            mag = 20 * np.log10(np.abs(h))
            
            # 找到阻带中的最小衰减
            if current_result['filter_type'] == '低通':
                stopband_mag = mag[w > 2 * current_result['cutoff1']]
            elif current_result['filter_type'] == '高通':
                stopband_mag = mag[w < 0.5 * current_result['cutoff1']]
            elif current_result['filter_type'] == '带通':
                stopband_mag = np.concatenate([
                    mag[w < 0.5 * current_result['cutoff1']],
                    mag[w > 2 * current_result['cutoff2']]
                ])
            elif current_result['filter_type'] == '带阻':
                stopband_mag = mag[
                    (w > 0.5 * current_result['cutoff1']) & 
                    (w < 2 * current_result['cutoff2'])
                ]
            else:
                stopband_mag = mag
            
            current_attenuation = np.min(stopband_mag) if len(stopband_mag) > 0 else 0
            
            # 如果当前衰减不满足要求，增加阶数
            if current_attenuation > -attenuation:
                new_order = order + 1
                self.order_spin.setValue(new_order)
                
                # 重新设计滤波器
                self.design_filter()
                
                QMessageBox.information(self, '优化完成', f'滤波器阶数已从 {order} 增加到 {new_order}，以满足阻带衰减要求')
            else:
                QMessageBox.information(self, '优化完成', '当前设计已经满足要求，无需优化')
                
        except Exception as e:
            QMessageBox.warning(self, '警告', f'优化错误: {str(e)}')
    
    def display_results(self, result):
        # 显示设计结果
        self.result_table.setRowCount(0)
        
        # 显示滤波器参数
        detail_text = "滤波器设计结果：\n\n"
        detail_text += f"滤波器类型: {result['filter_type']}\n"
        detail_text += f"滤波器响应: {result['response']}\n"
        detail_text += f"滤波器阶数: {result['order']}\n"
        detail_text += f"截止频率1: {result['cutoff1']/1e9:.2f} GHz\n"
        if result['filter_type'] in ['带通', '带阻']:
            detail_text += f"截止频率2: {result['cutoff2']/1e9:.2f} GHz\n"
        detail_text += f"通带波纹: {result['ripple']:.2f} dB\n"
        detail_text += f"阻带衰减: {result['attenuation']:.2f} dB\n"
        detail_text += f"特征阻抗: {result['z0']:.2f} Ω\n"
        detail_text += f"元件数量: {len(result['elements'])}\n\n"
        detail_text += "元件列表：\n"
        
        # 显示元件值
        for i, element in enumerate(result['elements']):
            self.add_result_row(element['type'], element['value'], element['unit'], element['position'])
            detail_text += f"{element['type']}{i+1}: {element['value']:.2f} {element['unit']} ({element['position']})\n"
        
        self.result_detail.setText(detail_text)
    
    def add_result_row(self, type_, value, unit, position):
        # 添加结果行到表格
        row = self.result_table.rowCount()
        self.result_table.insertRow(row)
        self.result_table.setItem(row, 0, QTableWidgetItem(type_))
        self.result_table.setItem(row, 1, QTableWidgetItem(f"{value:.2f}"))
        self.result_table.setItem(row, 2, QTableWidgetItem(unit))
        self.result_table.setItem(row, 3, QTableWidgetItem(position))
    
    def plot_magnitude_response(self):
        # 绘制幅频响应
        if not self.filter_results:
            QMessageBox.warning(self, '警告', '没有设计结果可以绘制')
            return
        
        # 获取最新的设计结果
        result = self.filter_results[-1]
        
        # 计算频率响应
        w, h = freqs(result['b'], result['a'], worN=np.logspace(0, 12, 1000))
        
        # 绘制幅频响应
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.semilogx(w / (2 * np.pi), 20 * np.log10(np.abs(h)))
        ax.set_title(f'{result["filter_type"]} {result["response"]} 滤波器幅频响应')
        ax.set_xlabel('频率 (Hz)')
        ax.set_ylabel('增益 (dB)')
        ax.grid(True, which='both')
        ax.axhline(-result['attenuation'], color='red', linestyle='--', label=f'阻带衰减: {result["attenuation"]} dB')
        ax.axvline(result['cutoff1'], color='green', linestyle='--', label=f'截止频率1: {result["cutoff1"]/1e9:.2f} GHz')
        if result['filter_type'] in ['带通', '带阻']:
            ax.axvline(result['cutoff2'], color='blue', linestyle='--', label=f'截止频率2: {result["cutoff2"]/1e9:.2f} GHz')
        ax.legend()
        self.canvas.draw()
    
    def plot_phase_response(self):
        # 绘制相频响应
        if not self.filter_results:
            QMessageBox.warning(self, '警告', '没有设计结果可以绘制')
            return
        
        # 获取最新的设计结果
        result = self.filter_results[-1]
        
        # 计算频率响应
        w, h = freqs(result['b'], result['a'], worN=np.logspace(0, 12, 1000))
        
        # 绘制相频响应
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.semilogx(w / (2 * np.pi), np.angle(h, deg=True))
        ax.set_title(f'{result["filter_type"]} {result["response"]} 滤波器相频响应')
        ax.set_xlabel('频率 (Hz)')
        ax.set_ylabel('相位 (度)')
        ax.grid(True, which='both')
        self.canvas.draw()
    
    def plot_group_delay(self):
        # 绘制群延迟
        if not self.filter_results:
            QMessageBox.warning(self, '警告', '没有设计结果可以绘制')
            return
        
        # 获取最新的设计结果
        result = self.filter_results[-1]
        
        # 计算频率响应
        w, h = freqs(result['b'], result['a'], worN=np.logspace(0, 12, 1000))
        
        # 计算群延迟
        group_delay = -np.diff(np.angle(h)) / np.diff(w)
        w_group = (w[1:] + w[:-1]) / 2
        
        # 绘制群延迟
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.semilogx(w_group / (2 * np.pi), group_delay)
        ax.set_title(f'{result["filter_type"]} {result["response"]} 滤波器群延迟')
        ax.set_xlabel('频率 (Hz)')
        ax.set_ylabel('群延迟 (s)')
        ax.grid(True, which='both')
        self.canvas.draw()
    
    def clear_chart(self):
        # 清空图表
        self.figure.clear()
        self.canvas.draw()
    
    def clear(self):
        # 清空输入和结果
        self.filter_type_combo.setCurrentText('低通')
        self.response_combo.setCurrentText('巴特沃斯')
        self.order_spin.setValue(4)
        self.cutoff1_edit.setValue(1.0)
        self.cutoff2_edit.setValue(2.0)
        self.ripple_edit.setValue(1.0)
        self.attenuation_edit.setValue(40.0)
        self.z0_edit.setValue(50.0)
        self.result_table.setRowCount(0)
        self.result_detail.clear()
        self.clear_chart()