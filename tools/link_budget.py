import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox, QGridLayout, QDoubleSpinBox, QMessageBox, QSplitter, QSpinBox, QTabWidget, QFormLayout, QHeaderView
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from data.history_manager import HistoryManager

class LinkBudgetAnalyzer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.history_manager = HistoryManager()
        self.link_results = []
    
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建标题
        title_label = QLabel('射频链路预算分析器')
        title_label.setFont(QFont('Consolas', 16, QFont.Bold))
        main_layout.addWidget(title_label)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 创建设计标签
        design_tab = QWidget()
        design_layout = QVBoxLayout(design_tab)
        
        # 创建系统参数区域
        system_group = QGroupBox('系统参数')
        system_layout = QGridLayout(system_group)
        
        # 频率
        freq_label = QLabel('频率 (GHz):')
        self.freq_edit = QDoubleSpinBox()
        self.freq_edit.setRange(0.1, 100.0)
        self.freq_edit.setValue(2.4)
        system_layout.addWidget(freq_label, 0, 0)
        system_layout.addWidget(self.freq_edit, 0, 1)
        
        # 距离
        distance_label = QLabel('距离 (km):')
        self.distance_edit = QDoubleSpinBox()
        self.distance_edit.setRange(0.1, 1000.0)
        self.distance_edit.setValue(1.0)
        system_layout.addWidget(distance_label, 0, 2)
        system_layout.addWidget(self.distance_edit, 0, 3)
        
        # 传播环境
        env_label = QLabel('传播环境:')
        self.env_combo = QComboBox()
        self.env_combo.addItems(['自由空间', '市区', '郊区', '农村', '室内'])
        system_layout.addWidget(env_label, 1, 0)
        system_layout.addWidget(self.env_combo, 1, 1)
        
        # 极化损耗
        polarization_label = QLabel('极化损耗 (dB):')
        self.polarization_edit = QDoubleSpinBox()
        self.polarization_edit.setRange(0.0, 10.0)
        self.polarization_edit.setValue(3.0)
        system_layout.addWidget(polarization_label, 1, 2)
        system_layout.addWidget(self.polarization_edit, 1, 3)
        
        # 雨衰
        rain_label = QLabel('雨衰 (dB):')
        self.rain_edit = QDoubleSpinBox()
        self.rain_edit.setRange(0.0, 20.0)
        self.rain_edit.setValue(0.0)
        system_layout.addWidget(rain_label, 2, 0)
        system_layout.addWidget(self.rain_edit, 2, 1)
        
        # 大气损耗
        atm_label = QLabel('大气损耗 (dB):')
        self.atm_edit = QDoubleSpinBox()
        self.atm_edit.setRange(0.0, 10.0)
        self.atm_edit.setValue(0.5)
        system_layout.addWidget(atm_label, 2, 2)
        system_layout.addWidget(self.atm_edit, 2, 3)
        
        design_layout.addWidget(system_group)
        
        # 创建发射机参数区域
        tx_group = QGroupBox('发射机参数')
        tx_layout = QGridLayout(tx_group)
        
        # 发射功率
        tx_power_label = QLabel('发射功率 (dBm):')
        self.tx_power_edit = QDoubleSpinBox()
        self.tx_power_edit.setRange(-50.0, 50.0)
        self.tx_power_edit.setValue(20.0)
        tx_layout.addWidget(tx_power_label, 0, 0)
        tx_layout.addWidget(self.tx_power_edit, 0, 1)
        
        # 发射机效率
        tx_efficiency_label = QLabel('发射机效率 (%):')
        self.tx_efficiency_edit = QDoubleSpinBox()
        self.tx_efficiency_edit.setRange(10.0, 100.0)
        self.tx_efficiency_edit.setValue(80.0)
        tx_layout.addWidget(tx_efficiency_label, 0, 2)
        tx_layout.addWidget(self.tx_efficiency_edit, 0, 3)
        
        # 发射天线增益
        tx_antenna_gain_label = QLabel('发射天线增益 (dBi):')
        self.tx_antenna_gain_edit = QDoubleSpinBox()
        self.tx_antenna_gain_edit.setRange(-10.0, 50.0)
        self.tx_antenna_gain_edit.setValue(10.0)
        tx_layout.addWidget(tx_antenna_gain_label, 1, 0)
        tx_layout.addWidget(self.tx_antenna_gain_edit, 1, 1)
        
        # 发射天线效率
        tx_antenna_efficiency_label = QLabel('发射天线效率 (%):')
        self.tx_antenna_efficiency_edit = QDoubleSpinBox()
        self.tx_antenna_efficiency_edit.setRange(50.0, 100.0)
        self.tx_antenna_efficiency_edit.setValue(90.0)
        tx_layout.addWidget(tx_antenna_efficiency_label, 1, 2)
        tx_layout.addWidget(self.tx_antenna_efficiency_edit, 1, 3)
        
        design_layout.addWidget(tx_group)
        
        # 创建接收机参数区域
        rx_group = QGroupBox('接收机参数')
        rx_layout = QGridLayout(rx_group)
        
        # 接收天线增益
        rx_antenna_gain_label = QLabel('接收天线增益 (dBi):')
        self.rx_antenna_gain_edit = QDoubleSpinBox()
        self.rx_antenna_gain_edit.setRange(-10.0, 50.0)
        self.rx_antenna_gain_edit.setValue(10.0)
        rx_layout.addWidget(rx_antenna_gain_label, 0, 0)
        rx_layout.addWidget(self.rx_antenna_gain_edit, 0, 1)
        
        # 接收天线效率
        rx_antenna_efficiency_label = QLabel('接收天线效率 (%):')
        self.rx_antenna_efficiency_edit = QDoubleSpinBox()
        self.rx_antenna_efficiency_edit.setRange(50.0, 100.0)
        self.rx_antenna_efficiency_edit.setValue(90.0)
        rx_layout.addWidget(rx_antenna_efficiency_label, 0, 2)
        rx_layout.addWidget(self.rx_antenna_efficiency_edit, 0, 3)
        
        # 接收机噪声系数
        rx_noise_label = QLabel('接收机噪声系数 (dB):')
        self.rx_noise_edit = QDoubleSpinBox()
        self.rx_noise_edit.setRange(1.0, 10.0)
        self.rx_noise_edit.setValue(3.0)
        rx_layout.addWidget(rx_noise_label, 1, 0)
        rx_layout.addWidget(self.rx_noise_edit, 1, 1)
        
        # 接收机带宽
        rx_bandwidth_label = QLabel('接收机带宽 (MHz):')
        self.rx_bandwidth_edit = QDoubleSpinBox()
        self.rx_bandwidth_edit.setRange(0.1, 100.0)
        self.rx_bandwidth_edit.setValue(20.0)
        rx_layout.addWidget(rx_bandwidth_label, 1, 2)
        rx_layout.addWidget(self.rx_bandwidth_edit, 1, 3)
        
        # 灵敏度要求
        sensitivity_label = QLabel('灵敏度要求 (dBm):')
        self.sensitivity_edit = QDoubleSpinBox()
        self.sensitivity_edit.setRange(-150.0, -50.0)
        self.sensitivity_edit.setValue(-100.0)
        rx_layout.addWidget(sensitivity_label, 2, 0)
        rx_layout.addWidget(self.sensitivity_edit, 2, 1)
        
        design_layout.addWidget(rx_group)
        
        # 创建链路组件区域
        components_group = QGroupBox('链路组件')
        components_layout = QVBoxLayout(components_group)
        
        # 创建组件表格
        self.components_table = QTableWidget()
        self.components_table.setColumnCount(4)
        self.components_table.setHorizontalHeaderLabels(['组件类型', '参数值', '单位', '备注'])
        self.components_table.horizontalHeader().setStretchLastSection(True)
        components_layout.addWidget(self.components_table)
        
        # 创建组件操作按钮
        component_button_layout = QHBoxLayout()
        
        # 添加组件按钮
        add_button = QPushButton('添加组件')
        add_button.setIcon(QIcon('resources/icons/add.png'))
        add_button.clicked.connect(self.add_component)
        component_button_layout.addWidget(add_button)
        
        # 删除组件按钮
        delete_button = QPushButton('删除组件')
        delete_button.setIcon(QIcon('resources/icons/delete.png'))
        delete_button.clicked.connect(self.delete_component)
        component_button_layout.addWidget(delete_button)
        
        # 清除组件按钮
        clear_components_button = QPushButton('清除组件')
        clear_components_button.setIcon(QIcon('resources/icons/clear.png'))
        clear_components_button.clicked.connect(self.clear_components)
        component_button_layout.addWidget(clear_components_button)
        
        components_layout.addLayout(component_button_layout)
        
        design_layout.addWidget(components_group)
        
        # 创建计算按钮区域
        button_layout = QHBoxLayout()
        
        # 计算链路预算按钮
        calc_button = QPushButton('计算链路预算')
        calc_button.setIcon(QIcon('resources/icons/calculate.png'))
        calc_button.clicked.connect(self.calculate_link_budget)
        button_layout.addWidget(calc_button)
        
        # 优化链路按钮
        optimize_button = QPushButton('优化链路')
        optimize_button.setIcon(QIcon('resources/icons/optimize.png'))
        optimize_button.clicked.connect(self.optimize_link)
        button_layout.addWidget(optimize_button)
        
        # 清除按钮
        clear_button = QPushButton('清除')
        clear_button.setIcon(QIcon('resources/icons/clear.png'))
        clear_button.clicked.connect(self.clear)
        button_layout.addWidget(clear_button)
        
        design_layout.addLayout(button_layout)
        
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
        
        design_layout.addWidget(result_group)
        
        tab_widget.addTab(design_tab, '链路预算设计')
        
        # 创建分析标签
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        
        # 创建可视化区域
        visual_group = QGroupBox('链路预算可视化')
        visual_layout = QVBoxLayout(visual_group)
        
        # 创建图表画布
        self.figure = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        visual_layout.addWidget(self.canvas)
        
        # 图表控制按钮
        chart_button_layout = QHBoxLayout()
        
        # 绘制链路预算图按钮
        plot_link_button = QPushButton('绘制链路预算图')
        plot_link_button.clicked.connect(self.plot_link_budget)
        chart_button_layout.addWidget(plot_link_button)
        
        # 绘制参数扫描图按钮
        plot_scan_button = QPushButton('绘制参数扫描')
        plot_scan_button.clicked.connect(self.plot_parameter_scan)
        chart_button_layout.addWidget(plot_scan_button)
        
        # 清空图表按钮
        clear_chart_button = QPushButton('清空图表')
        clear_chart_button.clicked.connect(self.clear_chart)
        chart_button_layout.addWidget(clear_chart_button)
        
        visual_layout.addLayout(chart_button_layout)
        
        analysis_layout.addWidget(visual_group)
        
        tab_widget.addTab(analysis_tab, '链路分析')
        
        main_layout.addWidget(tab_widget)
        
        # 填充剩余空间
        main_layout.addStretch()
    
    def add_component(self):
        # 添加链路组件
        component_types = ['放大器', '滤波器', '电缆', '功分器', '耦合器', '衰减器']
        
        # 创建组件对话框
        dialog = QWidget()
        dialog.setWindowTitle('添加链路组件')
        dialog.setWindowModality(Qt.ApplicationModal)
        
        layout = QVBoxLayout(dialog)
        
        # 组件类型
        type_label = QLabel('组件类型:')
        type_combo = QComboBox()
        type_combo.addItems(component_types)
        layout.addWidget(type_label)
        layout.addWidget(type_combo)
        
        # 组件参数
        value_label = QLabel('参数值:')
        value_edit = QDoubleSpinBox()
        value_edit.setRange(-100.0, 100.0)
        value_edit.setValue(0.0)
        layout.addWidget(value_label)
        layout.addWidget(value_edit)
        
        # 单位
        unit_label = QLabel('单位:')
        unit_combo = QComboBox()
        unit_combo.addItems(['dB', 'Ω', 'W'])
        layout.addWidget(unit_label)
        layout.addWidget(unit_combo)
        
        # 备注
        note_label = QLabel('备注:')
        note_edit = QLineEdit()
        layout.addWidget(note_label)
        layout.addWidget(note_edit)
        
        # 确认按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton('确定')
        ok_button.clicked.connect(lambda: self.add_component_to_table(type_combo.currentText(), value_edit.value(), unit_combo.currentText(), note_edit.text(), dialog))
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton('取消')
        cancel_button.clicked.connect(dialog.close)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def add_component_to_table(self, type_, value, unit, note, dialog):
        # 添加组件到表格
        row = self.components_table.rowCount()
        self.components_table.insertRow(row)
        self.components_table.setItem(row, 0, QTableWidgetItem(type_))
        self.components_table.setItem(row, 1, QTableWidgetItem(f"{value:.2f}"))
        self.components_table.setItem(row, 2, QTableWidgetItem(unit))
        self.components_table.setItem(row, 3, QTableWidgetItem(note))
        
        dialog.close()
    
    def delete_component(self):
        # 删除选中的组件
        current_row = self.components_table.currentRow()
        if current_row >= 0:
            self.components_table.removeRow(current_row)
        else:
            QMessageBox.warning(self, '警告', '请选择要删除的组件')
    
    def clear_components(self):
        # 清除所有组件
        self.components_table.setRowCount(0)
    
    def calculate_link_budget(self):
        # 计算链路预算
        try:
            # 获取输入参数
            freq = self.freq_edit.value() * 1e9  # Hz
            distance = self.distance_edit.value() * 1e3  # m
            env = self.env_combo.currentText()
            polarization_loss = self.polarization_edit.value()  # dB
            rain_loss = self.rain_edit.value()  # dB
            atm_loss = self.atm_edit.value()  # dB
            
            # 发射机参数
            tx_power = self.tx_power_edit.value()  # dBm
            tx_efficiency = self.tx_efficiency_edit.value() / 100  # 小数
            tx_antenna_gain = self.tx_antenna_gain_edit.value()  # dBi
            tx_antenna_efficiency = self.tx_antenna_efficiency_edit.value() / 100  # 小数
            
            # 接收机参数
            rx_antenna_gain = self.rx_antenna_gain_edit.value()  # dBi
            rx_antenna_efficiency = self.rx_antenna_efficiency_edit.value() / 100  # 小数
            rx_noise_figure = self.rx_noise_edit.value()  # dB
            rx_bandwidth = self.rx_bandwidth_edit.value() * 1e6  # Hz
            sensitivity_req = self.sensitivity_edit.value()  # dBm
            
            # 计算自由空间路径损耗
            fspl = self.calculate_fspl(freq, distance)
            
            # 计算传播损耗（考虑环境因素）
            propagation_loss = self.calculate_propagation_loss(fspl, env, freq, distance)
            
            # 计算总路径损耗
            total_path_loss = propagation_loss + polarization_loss + rain_loss + atm_loss
            
            # 计算天线增益（考虑效率）
            tx_antenna_gain_eff = tx_antenna_gain + 10 * np.log10(tx_antenna_efficiency)
            rx_antenna_gain_eff = rx_antenna_gain + 10 * np.log10(rx_antenna_efficiency)
            
            # 计算链路组件损耗/增益
            component_loss = 0.0
            components = []
            for row in range(self.components_table.rowCount()):
                type_ = self.components_table.item(row, 0).text()
                value = float(self.components_table.item(row, 1).text())
                unit = self.components_table.item(row, 2).text()
                note = self.components_table.item(row, 3).text()
                
                # 转换为dB
                if unit == 'dB':
                    component_loss += value
                elif unit == 'W':
                    component_loss += 10 * np.log10(value / 0.001)  # 转换为dBm
                
                components.append({
                    'type': type_,
                    'value': value,
                    'unit': unit,
                    'note': note,
                    'loss': value if unit == 'dB' else 10 * np.log10(value / 0.001)
                })
            
            # 计算发射功率（考虑效率）
            tx_power_eff = tx_power + 10 * np.log10(tx_efficiency)
            
            # 计算接收功率
            received_power = tx_power_eff + tx_antenna_gain_eff - total_path_loss - component_loss + rx_antenna_gain_eff
            
            # 计算接收机灵敏度
            noise_power = -174 + 10 * np.log10(rx_bandwidth) + rx_noise_figure  # dBm
            sensitivity = noise_power + 6  # 假设SNR要求为6dB
            
            # 计算链路余量
            link_margin = received_power - sensitivity_req
            
            # 计算SNR
            snr = received_power - noise_power
            
            # 保存结果
            result = {
                'freq': freq,
                'distance': distance,
                'env': env,
                'polarization_loss': polarization_loss,
                'rain_loss': rain_loss,
                'atm_loss': atm_loss,
                'tx_power': tx_power,
                'tx_efficiency': tx_efficiency,
                'tx_antenna_gain': tx_antenna_gain,
                'tx_antenna_efficiency': tx_antenna_efficiency,
                'rx_antenna_gain': rx_antenna_gain,
                'rx_antenna_efficiency': rx_antenna_efficiency,
                'rx_noise_figure': rx_noise_figure,
                'rx_bandwidth': rx_bandwidth,
                'sensitivity_req': sensitivity_req,
                'fspl': fspl,
                'propagation_loss': propagation_loss,
                'total_path_loss': total_path_loss,
                'tx_antenna_gain_eff': tx_antenna_gain_eff,
                'rx_antenna_gain_eff': rx_antenna_gain_eff,
                'component_loss': component_loss,
                'tx_power_eff': tx_power_eff,
                'received_power': received_power,
                'noise_power': noise_power,
                'sensitivity': sensitivity,
                'link_margin': link_margin,
                'snr': snr,
                'components': components
            }
            
            self.link_results.append(result)
            
            # 显示结果
            self.display_results(result)
            
            # 保存到历史
            self.history_manager.add_history(
                tool_name='射频链路预算分析器',
                input_data=f"频率: {freq/1e9} GHz, 距离: {distance/1e3} km, 发射功率: {tx_power} dBm",
                output_data=f"接收功率: {received_power:.2f} dBm, 链路余量: {link_margin:.2f} dB, SNR: {snr:.2f} dB",
                calculation_type='link_budget'
            )
            
        except Exception as e:
            QMessageBox.warning(self, '警告', f'计算错误: {str(e)}')
    
    def calculate_fspl(self, freq, distance):
        # 计算自由空间路径损耗 (dB)
        c0 = 299792458  # 真空中的光速
        wavelength = c0 / freq
        fspl = 20 * np.log10(distance) + 20 * np.log10(freq) + 20 * np.log10(4 * np.pi / c0)
        return fspl
    
    def calculate_propagation_loss(self, fspl, env, freq, distance):
        # 计算传播损耗（考虑环境因素）
        # 基于Okumura-Hata模型的简化版本
        if env == '自由空间':
            return fspl
        elif env == '市区':
            # 市区环境增加20-30dB损耗
            return fspl + 25
        elif env == '郊区':
            # 郊区环境增加10-20dB损耗
            return fspl + 15
        elif env == '农村':
            # 农村环境增加5-10dB损耗
            return fspl + 7
        elif env == '室内':
            # 室内环境增加15-30dB损耗
            return fspl + 20
        else:
            return fspl
    
    def optimize_link(self):
        # 优化链路预算
        try:
            # 获取当前计算结果
            if not self.link_results:
                QMessageBox.warning(self, '警告', '没有计算结果可以优化')
                return
            
            current_result = self.link_results[-1]
            
            # 检查链路余量是否足够
            if current_result['link_margin'] >= 10:
                QMessageBox.information(self, '优化完成', '当前链路余量已经足够（>10dB），无需优化')
                return
            
            # 优化建议
            suggestions = []
            
            # 1. 增加发射功率
            if current_result['tx_power'] < 30:  # 假设最大发射功率为30dBm
                new_tx_power = current_result['tx_power'] + 5
                suggestions.append(f"增加发射功率到 {new_tx_power} dBm")
                
            # 2. 增加天线增益
            if current_result['tx_antenna_gain'] < 20:
                new_tx_gain = current_result['tx_antenna_gain'] + 5
                suggestions.append(f"增加发射天线增益到 {new_tx_gain} dBi")
            
            if current_result['rx_antenna_gain'] < 20:
                new_rx_gain = current_result['rx_antenna_gain'] + 5
                suggestions.append(f"增加接收天线增益到 {new_rx_gain} dBi")
            
            # 3. 减少链路损耗
            if current_result['component_loss'] > 0:
                suggestions.append("减少链路组件损耗")
            
            # 4. 提高天线效率
            if current_result['tx_antenna_efficiency'] < 0.95:
                suggestions.append("提高发射天线效率")
            
            if current_result['rx_antenna_efficiency'] < 0.95:
                suggestions.append("提高接收天线效率")
            
            # 5. 降低接收机噪声系数
            if current_result['rx_noise_figure'] > 1.5:
                suggestions.append("降低接收机噪声系数")
            
            # 显示优化建议
            if suggestions:
                suggestion_text = "链路优化建议：\n\n"
                for i, suggestion in enumerate(suggestions, 1):
                    suggestion_text += f"{i}. {suggestion}\n"
                
                QMessageBox.information(self, '优化建议', suggestion_text)
            else:
                QMessageBox.information(self, '优化完成', '当前链路已经无法进一步优化')
                
        except Exception as e:
            QMessageBox.warning(self, '警告', f'优化错误: {str(e)}')
    
    def display_results(self, result):
        # 显示计算结果
        self.result_table.setRowCount(0)
        
        # 显示链路预算结果
        detail_text = "射频链路预算计算结果：\n\n"
        
        # 系统参数
        detail_text += "系统参数：\n"
        detail_text += f"频率: {result['freq']/1e9:.2f} GHz\n"
        detail_text += f"距离: {result['distance']/1e3:.2f} km\n"
        detail_text += f"传播环境: {result['env']}\n"
        detail_text += f"极化损耗: {result['polarization_loss']:.2f} dB\n"
        detail_text += f"雨衰: {result['rain_loss']:.2f} dB\n"
        detail_text += f"大气损耗: {result['atm_loss']:.2f} dB\n\n"
        
        # 发射机参数
        detail_text += "发射机参数：\n"
        detail_text += f"发射功率: {result['tx_power']:.2f} dBm\n"
        detail_text += f"发射机效率: {result['tx_efficiency']*100:.2f}%\n"
        detail_text += f"发射天线增益: {result['tx_antenna_gain']:.2f} dBi\n"
        detail_text += f"发射天线效率: {result['tx_antenna_efficiency']*100:.2f}%\n"
        detail_text += f"有效发射天线增益: {result['tx_antenna_gain_eff']:.2f} dBi\n"
        detail_text += f"有效发射功率: {result['tx_power_eff']:.2f} dBm\n\n"
        
        # 接收机参数
        detail_text += "接收机参数：\n"
        detail_text += f"接收天线增益: {result['rx_antenna_gain']:.2f} dBi\n"
        detail_text += f"接收天线效率: {result['rx_antenna_efficiency']*100:.2f}%\n"
        detail_text += f"有效接收天线增益: {result['rx_antenna_gain_eff']:.2f} dBi\n"
        detail_text += f"接收机噪声系数: {result['rx_noise_figure']:.2f} dB\n"
        detail_text += f"接收机带宽: {result['rx_bandwidth']/1e6:.2f} MHz\n"
        detail_text += f"灵敏度要求: {result['sensitivity_req']:.2f} dBm\n"
        detail_text += f"计算灵敏度: {result['sensitivity']:.2f} dBm\n"
        detail_text += f"噪声功率: {result['noise_power']:.2f} dBm\n\n"
        
        # 路径损耗
        detail_text += "路径损耗：\n"
        detail_text += f"自由空间路径损耗: {result['fspl']:.2f} dB\n"
        detail_text += f"传播损耗: {result['propagation_loss']:.2f} dB\n"
        detail_text += f"总路径损耗: {result['total_path_loss']:.2f} dB\n\n"
        
        # 链路组件
        if result['components']:
            detail_text += "链路组件损耗：\n"
            for i, component in enumerate(result['components']):
                detail_text += f"{component['type']}: {component['loss']:.2f} dB ({component['note']})\n"
            detail_text += f"总组件损耗: {result['component_loss']:.2f} dB\n\n"
        
        # 最终结果
        detail_text += "最终结果：\n"
        detail_text += f"接收功率: {result['received_power']:.2f} dBm\n"
        detail_text += f"链路余量: {result['link_margin']:.2f} dB\n"
        detail_text += f"信噪比 (SNR): {result['snr']:.2f} dB\n\n"
        
        # 添加到结果表格
        self.add_result_row('频率', result['freq']/1e9, 'GHz')
        self.add_result_row('距离', result['distance']/1e3, 'km')
        self.add_result_row('传播环境', result['env'], '')
        self.add_result_row('总路径损耗', result['total_path_loss'], 'dB')
        self.add_result_row('有效发射功率', result['tx_power_eff'], 'dBm')
        self.add_result_row('有效发射天线增益', result['tx_antenna_gain_eff'], 'dBi')
        self.add_result_row('有效接收天线增益', result['rx_antenna_gain_eff'], 'dBi')
        self.add_result_row('总组件损耗', result['component_loss'], 'dB')
        self.add_result_row('接收功率', result['received_power'], 'dBm')
        self.add_result_row('噪声功率', result['noise_power'], 'dBm')
        self.add_result_row('计算灵敏度', result['sensitivity'], 'dBm')
        self.add_result_row('灵敏度要求', result['sensitivity_req'], 'dBm')
        self.add_result_row('链路余量', result['link_margin'], 'dB')
        self.add_result_row('信噪比', result['snr'], 'dB')
        
        self.result_detail.setText(detail_text)
    
    def add_result_row(self, name, value, unit):
        # 添加结果行到表格
        row = self.result_table.rowCount()
        self.result_table.insertRow(row)
        self.result_table.setItem(row, 0, QTableWidgetItem(name))
        self.result_table.setItem(row, 1, QTableWidgetItem(f"{value:.2f}" if isinstance(value, float) else str(value)))
        self.result_table.setItem(row, 2, QTableWidgetItem(unit))
    
    def plot_link_budget(self):
        # 绘制链路预算图
        if not self.link_results:
            QMessageBox.warning(self, '警告', '没有计算结果可以绘制')
            return
        
        # 获取最新的计算结果
        result = self.link_results[-1]
        
        # 创建链路预算数据
        stages = ['发射功率', '发射天线增益', '路径损耗', '组件损耗', '接收天线增益', '接收功率']
        values = [
            result['tx_power_eff'],
            result['tx_antenna_gain_eff'],
            -result['total_path_loss'],
            -result['component_loss'],
            result['rx_antenna_gain_eff'],
            result['received_power']
        ]
        
        # 计算累积功率
        cumulative = [result['tx_power_eff']]
        for i in range(1, len(values)):
            cumulative.append(cumulative[-1] + values[i])
        
        # 绘制链路预算图
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 绘制累积功率曲线
        ax.plot(range(len(stages)), cumulative, marker='o', linewidth=2, markersize=8)
        
        # 添加标签
        for i, (stage, value, cum) in enumerate(zip(stages, values, cumulative)):
            ax.text(i, cum + 0.5, f'{cum:.2f} dBm', ha='center', va='bottom')
            if i > 0:
                ax.text(i - 0.5, (cumulative[i-1] + cum)/2, f'{value:+.2f} dB', ha='center', va='center', backgroundcolor='white')
        
        ax.set_xticks(range(len(stages)))
        ax.set_xticklabels(stages, rotation=45, ha='right')
        ax.set_title('射频链路预算分析')
        ax.set_ylabel('功率 (dBm)')
        ax.grid(True)
        
        # 添加水平线显示灵敏度要求
        ax.axhline(result['sensitivity_req'], color='red', linestyle='--', label=f'灵敏度要求: {result["sensitivity_req"]:.2f} dBm')
        ax.legend()
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_parameter_scan(self):
        # 绘制参数扫描图
        if not self.link_results:
            QMessageBox.warning(self, '警告', '没有计算结果可以绘制')
            return
        
        # 获取最新的计算结果
        result = self.link_results[-1]
        
        # 扫描距离对链路余量的影响
        distances = np.linspace(0.1, 10.0, 50)  # km
        link_margins = []
        
        for d in distances:
            # 重新计算链路预算
            distance_m = d * 1e3
            fspl = self.calculate_fspl(result['freq'], distance_m)
            propagation_loss = self.calculate_propagation_loss(fspl, result['env'], result['freq'], distance_m)
            total_path_loss = propagation_loss + result['polarization_loss'] + result['rain_loss'] + result['atm_loss']
            
            received_power = result['tx_power_eff'] + result['tx_antenna_gain_eff'] - total_path_loss - result['component_loss'] + result['rx_antenna_gain_eff']
            link_margin = received_power - result['sensitivity_req']
            link_margins.append(link_margin)
        
        # 绘制参数扫描图
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(distances, link_margins)
        ax.set_title('距离对链路余量的影响')
        ax.set_xlabel('距离 (km)')
        ax.set_ylabel('链路余量 (dB)')
        ax.grid(True)
        
        # 添加水平线显示最小链路余量要求
        ax.axhline(10, color='red', linestyle='--', label='最小链路余量要求: 10 dB')
        ax.legend()
        
        self.canvas.draw()
    
    def clear_chart(self):
        # 清空图表
        self.figure.clear()
        self.canvas.draw()
    
    def clear(self):
        # 清空输入和结果
        self.freq_edit.setValue(2.4)
        self.distance_edit.setValue(1.0)
        self.env_combo.setCurrentText('自由空间')
        self.polarization_edit.setValue(3.0)
        self.rain_edit.setValue(0.0)
        self.atm_edit.setValue(0.5)
        self.tx_power_edit.setValue(20.0)
        self.tx_efficiency_edit.setValue(80.0)
        self.tx_antenna_gain_edit.setValue(10.0)
        self.tx_antenna_efficiency_edit.setValue(90.0)
        self.rx_antenna_gain_edit.setValue(10.0)
        self.rx_antenna_efficiency_edit.setValue(90.0)
        self.rx_noise_edit.setValue(3.0)
        self.rx_bandwidth_edit.setValue(20.0)
        self.sensitivity_edit.setValue(-100.0)
        self.clear_components()
        self.result_table.setRowCount(0)
        self.result_detail.clear()
        self.clear_chart()