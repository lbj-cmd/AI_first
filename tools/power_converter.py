import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox, QGridLayout, QSpinBox, QDoubleSpinBox, QMessageBox
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, pyqtSignal
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from data.history_manager import HistoryManager

class PowerConverter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.history_manager = HistoryManager()
        self.calculation_results = []
    
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建标题
        title_label = QLabel('功率单位换算器')
        title_label.setFont(QFont('Consolas', 16, QFont.Bold))
        main_layout.addWidget(title_label)
        
        # 创建换算区域
        convert_group = QGroupBox('功率换算')
        convert_layout = QGridLayout(convert_group)
        
        # 功率输入
        power_label = QLabel('功率:')
        self.power_edit = QLineEdit()
        self.power_edit.setPlaceholderText('输入功率值')
        self.power_edit.textChanged.connect(self.real_time_convert)
        power_unit_label = QLabel('单位:')
        self.power_unit_combo = QComboBox()
        self.power_unit_combo.addItems(['W', 'mW', 'μW', 'nW'])
        self.power_unit_combo.currentTextChanged.connect(self.real_time_convert)
        
        convert_layout.addWidget(power_label, 0, 0)
        convert_layout.addWidget(self.power_edit, 0, 1)
        convert_layout.addWidget(power_unit_label, 0, 2)
        convert_layout.addWidget(self.power_unit_combo, 0, 3)
        
        # dB值输入
        db_label = QLabel('dB值:')
        self.db_edit = QLineEdit()
        self.db_edit.setPlaceholderText('输入dB值')
        self.db_edit.textChanged.connect(self.real_time_convert)
        db_unit_label = QLabel('单位:')
        self.db_unit_combo = QComboBox()
        self.db_unit_combo.addItems(['dBm', 'dBW'])
        self.db_unit_combo.currentTextChanged.connect(self.real_time_convert)
        
        convert_layout.addWidget(db_label, 1, 0)
        convert_layout.addWidget(self.db_edit, 1, 1)
        convert_layout.addWidget(db_unit_label, 1, 2)
        convert_layout.addWidget(self.db_unit_combo, 1, 3)
        
        # 换算方向
        direction_label = QLabel('换算方向:')
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(['功率 → dB', 'dB → 功率', '双向实时'])
        self.direction_combo.currentTextChanged.connect(self.real_time_convert)
        
        convert_layout.addWidget(direction_label, 2, 0)
        convert_layout.addWidget(self.direction_combo, 2, 1, 1, 3)
        
        main_layout.addWidget(convert_group)
        
        # 创建结果显示区域
        result_group = QGroupBox('换算结果')
        result_layout = QVBoxLayout(result_group)
        
        # 创建结果标签
        self.result_label = QLabel('')
        self.result_label.setFont(QFont('Consolas', 12))
        self.result_label.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(self.result_label)
        
        # 创建详细结果文本框
        self.result_detail = QTextEdit()
        self.result_detail.setReadOnly(True)
        self.result_detail.setFont(QFont('Consolas', 10))
        result_layout.addWidget(self.result_detail)
        
        main_layout.addWidget(result_group)
        
        # 创建链路预算区域
        budget_group = QGroupBox('链路预算分析')
        budget_layout = QVBoxLayout(budget_group)
        
        # 创建链路预算表格
        self.budget_table = QTableWidget()
        self.budget_table.setColumnCount(4)
        self.budget_table.setHorizontalHeaderLabels(['部件名称', '增益/损耗(dB)', '类型', '备注'])
        self.budget_table.horizontalHeader().setStretchLastSection(True)
        
        # 添加默认行
        self.budget_table.setRowCount(3)
        self.budget_table.setItem(0, 0, QTableWidgetItem('发射机功率'))
        self.budget_table.setItem(0, 1, QTableWidgetItem('30'))
        self.budget_table.setItem(0, 2, QTableWidgetItem('增益'))
        self.budget_table.setItem(0, 3, QTableWidgetItem('dBm'))
        
        self.budget_table.setItem(1, 0, QTableWidgetItem('传输损耗'))
        self.budget_table.setItem(1, 1, QTableWidgetItem('-10'))
        self.budget_table.setItem(1, 2, QTableWidgetItem('损耗'))
        self.budget_table.setItem(1, 3, QTableWidgetItem('自由空间损耗'))
        
        self.budget_table.setItem(2, 0, QTableWidgetItem('接收机灵敏度'))
        self.budget_table.setItem(2, 1, QTableWidgetItem('-90'))
        self.budget_table.setItem(2, 2, QTableWidgetItem('损耗'))
        self.budget_table.setItem(2, 3, QTableWidgetItem('dBm'))
        
        budget_layout.addWidget(self.budget_table)
        
        # 链路预算按钮
        budget_button_layout = QHBoxLayout()
        
        # 添加部件按钮
        add_button = QPushButton('添加部件')
        add_button.setIcon(QIcon('resources/icons/add.png'))
        add_button.clicked.connect(self.add_budget_item)
        budget_button_layout.addWidget(add_button)
        
        # 删除部件按钮
        delete_button = QPushButton('删除部件')
        delete_button.setIcon(QIcon('resources/icons/delete.png'))
        delete_button.clicked.connect(self.delete_budget_item)
        budget_button_layout.addWidget(delete_button)
        
        # 计算链路预算按钮
        calc_budget_button = QPushButton('计算链路预算')
        calc_budget_button.setIcon(QIcon('resources/icons/calculate.png'))
        calc_budget_button.clicked.connect(self.calculate_link_budget)
        budget_button_layout.addWidget(calc_budget_button)
        
        budget_layout.addLayout(budget_button_layout)
        
        # 链路预算结果
        self.budget_result = QTextEdit()
        self.budget_result.setReadOnly(True)
        self.budget_result.setFont(QFont('Consolas', 10))
        budget_layout.addWidget(self.budget_result)
        
        main_layout.addWidget(budget_group)
        
        # 创建批量计算区域
        batch_group = QGroupBox('批量计算')
        batch_layout = QVBoxLayout(batch_group)
        
        # 批量输入
        batch_label = QLabel('批量输入(逗号分隔):')
        self.batch_edit = QLineEdit()
        self.batch_edit.setPlaceholderText('输入多个功率值，逗号分隔')
        
        batch_layout.addWidget(batch_label)
        batch_layout.addWidget(self.batch_edit)
        
        # 批量计算按钮
        batch_button = QPushButton('批量计算')
        batch_button.setIcon(QIcon('resources/icons/batch.png'))
        batch_button.clicked.connect(self.batch_calculate)
        batch_layout.addWidget(batch_button)
        
        # 批量结果表格
        self.batch_table = QTableWidget()
        self.batch_table.setColumnCount(4)
        self.batch_table.setHorizontalHeaderLabels(['输入值', '输入单位', '输出值', '输出单位'])
        self.batch_table.horizontalHeader().setStretchLastSection(True)
        batch_layout.addWidget(self.batch_table)
        
        main_layout.addWidget(batch_group)
        
        # 创建可视化区域
        visual_group = QGroupBox('可视化')
        visual_layout = QVBoxLayout(visual_group)
        
        # 创建图表画布
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        visual_layout.addWidget(self.canvas)
        
        # 图表控制按钮
        chart_button_layout = QHBoxLayout()
        
        # 绘制功率分布按钮
        power_chart_button = QPushButton('绘制功率分布')
        power_chart_button.clicked.connect(self.plot_power_distribution)
        chart_button_layout.addWidget(power_chart_button)
        
        # 绘制dB分布按钮
        db_chart_button = QPushButton('绘制dB分布')
        db_chart_button.clicked.connect(self.plot_db_distribution)
        chart_button_layout.addWidget(db_chart_button)
        
        # 清空图表按钮
        clear_chart_button = QPushButton('清空图表')
        clear_chart_button.clicked.connect(self.clear_chart)
        chart_button_layout.addWidget(clear_chart_button)
        
        visual_layout.addLayout(chart_button_layout)
        
        main_layout.addWidget(visual_group)
        
        # 填充剩余空间
        main_layout.addStretch()
    
    def real_time_convert(self):
        # 实时换算功率和dB值
        power_text = self.power_edit.text().strip()
        db_text = self.db_edit.text().strip()
        direction = self.direction_combo.currentText()
        
        # 检查输入
        if not power_text and not db_text:
            self.result_label.setText('')
            self.result_detail.setText('')
            return
        
        try:
            if direction == '功率 → dB' or (direction == '双向实时' and power_text):
                # 从功率转换为dB
                power = float(power_text)
                power_unit = self.power_unit_combo.currentText()
                
                # 转换为W
                if power_unit == 'mW':
                    power_w = power / 1000
                elif power_unit == 'μW':
                    power_w = power / 1e6
                elif power_unit == 'nW':
                    power_w = power / 1e9
                else:
                    power_w = power
                
                # 计算dB值
                if self.db_unit_combo.currentText() == 'dBm':
                    # dBm = 10 * log10(power_mW)
                    power_mw = power_w * 1000
                    if power_mw <= 0:
                        self.result_label.setText('功率值必须大于0')
                        return
                    db_value = 10 * np.log10(power_mw)
                else:
                    # dBW = 10 * log10(power_W)
                    if power_w <= 0:
                        self.result_label.setText('功率值必须大于0')
                        return
                    db_value = 10 * np.log10(power_w)
                
                # 显示结果
                self.db_edit.setText(f"{db_value:.6f}")
                self.display_result(power, power_unit, db_value, self.db_unit_combo.currentText())
                
                # 保存到历史
                self.history_manager.add_history(
                    tool_name='功率单位换算器',
                    input_data=f"{power} {power_unit}",
                    output_data=f"{db_value:.6f} {self.db_unit_combo.currentText()}",
                    calculation_type='power_to_db'
                )
            
            elif direction == 'dB → 功率' or (direction == '双向实时' and db_text):
                # 从dB转换为功率
                db_value = float(db_text)
                db_unit = self.db_unit_combo.currentText()
                
                # 计算功率
                if db_unit == 'dBm':
                    # power_mW = 10^(dBm / 10)
                    power_mw = 10 ** (db_value / 10)
                    power_w = power_mw / 1000
                else:
                    # power_W = 10^(dBW / 10)
                    power_w = 10 ** (db_value / 10)
                
                # 转换为选择的功率单位
                power_unit = self.power_unit_combo.currentText()
                if power_unit == 'mW':
                    power = power_w * 1000
                elif power_unit == 'μW':
                    power = power_w * 1e6
                elif power_unit == 'nW':
                    power = power_w * 1e9
                else:
                    power = power_w
                
                # 显示结果
                self.power_edit.setText(f"{power:.6e}")
                self.display_result(power, power_unit, db_value, db_unit)
                
                # 保存到历史
                self.history_manager.add_history(
                    tool_name='功率单位换算器',
                    input_data=f"{db_value} {db_unit}",
                    output_data=f"{power:.6e} {power_unit}",
                    calculation_type='db_to_power'
                )
        
        except ValueError:
            self.result_label.setText('输入格式错误')
    
    def display_result(self, power, power_unit, db_value, db_unit):
        # 显示换算结果
        result_text = f"{power:.6e} {power_unit} = {db_value:.6f} {db_unit}"
        self.result_label.setText(result_text)
        
        # 显示详细结果
        detail_text = "换算详情：\n\n"
        detail_text += f"输入值: {power:.6e} {power_unit}\n"
        detail_text += f"输出值: {db_value:.6f} {db_unit}\n"
        detail_text += f"换算方向: {self.direction_combo.currentText()}\n"
        detail_text += f"换算时间: 刚刚\n"
        
        self.result_detail.setText(detail_text)
        
        # 保存到计算结果列表
        self.calculation_results.append({
            'power': power,
            'power_unit': power_unit,
            'db_value': db_value,
            'db_unit': db_unit
        })
    
    def calculate_link_budget(self):
        # 计算链路预算
        total_gain = 0.0
        transmit_power = 0.0
        receive_sensitivity = 0.0
        
        # 遍历表格中的所有行
        for row in range(self.budget_table.rowCount()):
            try:
                gain_loss = float(self.budget_table.item(row, 1).text())
                component_type = self.budget_table.item(row, 2).text()
                component_name = self.budget_table.item(row, 0).text()
                
                # 累加增益/损耗
                if component_type == '增益':
                    total_gain += gain_loss
                else:
                    total_gain += gain_loss  # 损耗已经是负值
                
                # 记录发射功率和接收机灵敏度
                if component_name == '发射机功率':
                    transmit_power = gain_loss
                elif component_name == '接收机灵敏度':
                    receive_sensitivity = gain_loss
            
            except (ValueError, AttributeError):
                continue
        
        # 计算接收功率
        receive_power = transmit_power + total_gain - transmit_power  # 去除发射机功率的重复计算
        
        # 计算链路余量
        link_margin = receive_power - receive_sensitivity
        
        # 显示结果
        result_text = "链路预算结果：\n\n"
        result_text += f"发射机功率: {transmit_power:.2f} dBm\n"
        result_text += f"总增益/损耗: {total_gain - transmit_power:.2f} dB\n"
        result_text += f"接收功率: {receive_power:.2f} dBm\n"
        result_text += f"接收机灵敏度: {receive_sensitivity:.2f} dBm\n"
        result_text += f"链路余量: {link_margin:.2f} dB\n\n"
        
        # 判断链路是否可行
        if link_margin >= 0:
            result_text += "✅ 链路可行，有足够的余量"
        else:
            result_text += "❌ 链路不可行，余量不足"
        
        self.budget_result.setText(result_text)
        
        # 保存到历史
        self.history_manager.add_history(
            tool_name='功率单位换算器',
            input_data=f"发射机功率: {transmit_power} dBm, 总增益/损耗: {total_gain - transmit_power} dB",
            output_data=f"接收功率: {receive_power} dBm, 链路余量: {link_margin} dB",
            calculation_type='link_budget'
        )
    
    def add_budget_item(self):
        # 添加链路预算部件
        row = self.budget_table.rowCount()
        self.budget_table.insertRow(row)
        self.budget_table.setItem(row, 0, QTableWidgetItem('新部件'))
        self.budget_table.setItem(row, 1, QTableWidgetItem('0'))
        self.budget_table.setItem(row, 2, QTableWidgetItem('增益'))
        self.budget_table.setItem(row, 3, QTableWidgetItem(''))
    
    def delete_budget_item(self):
        # 删除链路预算部件
        selected_rows = self.budget_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, '警告', '请选择要删除的部件')
            return
        
        # 去重行号
        rows = list(set(item.row() for item in selected_rows))
        
        # 按降序删除行
        for row in sorted(rows, reverse=True):
            self.budget_table.removeRow(row)
    
    def batch_calculate(self):
        # 批量计算
        batch_text = self.batch_edit.text().strip()
        if not batch_text:
            QMessageBox.warning(self, '警告', '请输入批量计算值')
            return
        
        try:
            # 解析输入
            inputs = [float(v) for v in batch_text.split(',')]
            direction = self.direction_combo.currentText().split('→')[0].strip()
            
            # 执行批量计算
            results = []
            for input_val in inputs:
                if direction == '功率':
                    # 功率 → dB
                    power = input_val
                    power_unit = self.power_unit_combo.currentText()
                    
                    # 转换为W
                    if power_unit == 'mW':
                        power_w = power / 1000
                    elif power_unit == 'μW':
                        power_w = power / 1e6
                    elif power_unit == 'nW':
                        power_w = power / 1e9
                    else:
                        power_w = power
                    
                    # 计算dB值
                    if self.db_unit_combo.currentText() == 'dBm':
                        power_mw = power_w * 1000
                        if power_mw <= 0:
                            db_value = '无效值'
                        else:
                            db_value = 10 * np.log10(power_mw)
                    else:
                        if power_w <= 0:
                            db_value = '无效值'
                        else:
                            db_value = 10 * np.log10(power_w)
                    
                    results.append({
                        'input': input_val,
                        'input_unit': power_unit,
                        'output': db_value,
                        'output_unit': self.db_unit_combo.currentText()
                    })
                
                else:
                    # dB → 功率
                    db_value = input_val
                    db_unit = self.db_unit_combo.currentText()
                    
                    # 计算功率
                    if db_unit == 'dBm':
                        power_mw = 10 ** (db_value / 10)
                        power_w = power_mw / 1000
                    else:
                        power_w = 10 ** (db_value / 10)
                    
                    # 转换为选择的功率单位
                    power_unit = self.power_unit_combo.currentText()
                    if power_unit == 'mW':
                        power = power_w * 1000
                    elif power_unit == 'μW':
                        power = power_w * 1e6
                    elif power_unit == 'nW':
                        power = power_w * 1e9
                    else:
                        power = power_w
                    
                    results.append({
                        'input': input_val,
                        'input_unit': db_unit,
                        'output': power,
                        'output_unit': power_unit
                    })
            
            # 显示结果
            self.batch_table.setRowCount(len(results))
            for i, result in enumerate(results):
                self.batch_table.setItem(i, 0, QTableWidgetItem(f"{result['input']:.6e}"))
                self.batch_table.setItem(i, 1, QTableWidgetItem(result['input_unit']))
                if isinstance(result['output'], str):
                    self.batch_table.setItem(i, 2, QTableWidgetItem(result['output']))
                else:
                    self.batch_table.setItem(i, 2, QTableWidgetItem(f"{result['output']:.6e}"))
                self.batch_table.setItem(i, 3, QTableWidgetItem(result['output_unit']))
            
            # 保存到历史
            for result in results:
                self.history_manager.add_history(
                    tool_name='功率单位换算器',
                    input_data=f"{result['input']} {result['input_unit']}",
                    output_data=f"{result['output']} {result['output_unit']}",
                    calculation_type='batch_calculate'
                )
        
        except ValueError:
            QMessageBox.warning(self, '警告', '批量输入格式错误')
    
    def plot_power_distribution(self):
        # 绘制功率分布图表
        if not self.calculation_results:
            QMessageBox.warning(self, '警告', '没有计算结果可以绘制')
            return
        
        # 提取功率数据
        powers = []
        for result in self.calculation_results:
            # 转换为W
            power = result['power']
            unit = result['power_unit']
            if unit == 'mW':
                power /= 1000
            elif unit == 'μW':
                power /= 1e6
            elif unit == 'nW':
                power /= 1e9
            powers.append(power)
        
        if powers:
            self.ax.clear()
            self.ax.hist(powers, bins=20, alpha=0.75)
            self.ax.set_xlabel('功率 (W)')
            self.ax.set_ylabel('数量')
            self.ax.set_title('功率分布直方图')
            self.ax.grid(True)
            self.canvas.draw()
    
    def plot_db_distribution(self):
        # 绘制dB分布图表
        if not self.calculation_results:
            QMessageBox.warning(self, '警告', '没有计算结果可以绘制')
            return
        
        # 提取dB数据
        db_values = [result['db_value'] for result in self.calculation_results if isinstance(result['db_value'], float)]
        
        if db_values:
            self.ax.clear()
            self.ax.hist(db_values, bins=20, alpha=0.75)
            self.ax.set_xlabel('dB值')
            self.ax.set_ylabel('数量')
            self.ax.set_title('dB值分布直方图')
            self.ax.grid(True)
            self.canvas.draw()
    
    def clear_chart(self):
        # 清空图表
        self.ax.clear()
        self.canvas.draw()