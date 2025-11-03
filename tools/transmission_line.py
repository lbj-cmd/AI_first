import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox, QGridLayout, QDoubleSpinBox, QMessageBox, QSplitter
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from data.history_manager import HistoryManager

class TransmissionLineCalculator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.history_manager = HistoryManager()
        self.calculation_results = []
    
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建标题
        title_label = QLabel('传输线参数计算器')
        title_label.setFont(QFont('Consolas', 16, QFont.Bold))
        main_layout.addWidget(title_label)
        
        # 创建输入区域
        input_group = QGroupBox('传输线参数')
        input_layout = QGridLayout(input_group)
        
        # 频率输入
        freq_label = QLabel('频率 (GHz):')
        self.freq_edit = QDoubleSpinBox()
        self.freq_edit.setRange(0.1, 100.0)
        self.freq_edit.setValue(2.4)
        input_layout.addWidget(freq_label, 0, 0)
        input_layout.addWidget(self.freq_edit, 0, 1)
        
        # 传输线类型
        line_type_label = QLabel('传输线类型:')
        self.line_type_combo = QComboBox()
        self.line_type_combo.addItems(['微带线', '带状线', '同轴线', '波导'])
        self.line_type_combo.currentTextChanged.connect(self.update_line_params)
        input_layout.addWidget(line_type_label, 0, 2)
        input_layout.addWidget(self.line_type_combo, 0, 3)
        
        # 特性阻抗
        z0_label = QLabel('特性阻抗 (Ω):')
        self.z0_edit = QDoubleSpinBox()
        self.z0_edit.setRange(10.0, 200.0)
        self.z0_edit.setValue(50.0)
        input_layout.addWidget(z0_label, 1, 0)
        input_layout.addWidget(self.z0_edit, 1, 1)
        
        # 负载阻抗
        zl_label = QLabel('负载阻抗 (Ω):')
        self.zl_real_edit = QDoubleSpinBox()
        self.zl_real_edit.setRange(1.0, 1000.0)
        self.zl_real_edit.setValue(75.0)
        self.zl_imag_edit = QDoubleSpinBox()
        self.zl_imag_edit.setRange(-1000.0, 1000.0)
        self.zl_imag_edit.setValue(0.0)
        zl_layout = QHBoxLayout()
        zl_layout.addWidget(self.zl_real_edit)
        zl_layout.addWidget(QLabel('+ j'))
        zl_layout.addWidget(self.zl_imag_edit)
        input_layout.addWidget(zl_label, 1, 2)
        input_layout.addLayout(zl_layout, 1, 3)
        
        # 介电常数
        er_label = QLabel('相对介电常数:')
        self.er_edit = QDoubleSpinBox()
        self.er_edit.setRange(1.0, 20.0)
        self.er_edit.setValue(4.4)
        input_layout.addWidget(er_label, 2, 0)
        input_layout.addWidget(self.er_edit, 2, 1)
        
        # 损耗正切
        tand_label = QLabel('损耗正切:')
        self.tand_edit = QDoubleSpinBox()
        self.tand_edit.setRange(0.0, 0.1)
        self.tand_edit.setValue(0.02)
        self.tand_edit.setSingleStep(0.001)
        input_layout.addWidget(tand_label, 2, 2)
        input_layout.addWidget(self.tand_edit, 2, 3)
        
        # 导体电导率
        sigma_label = QLabel('导体电导率 (S/m):')
        self.sigma_edit = QDoubleSpinBox()
        self.sigma_edit.setRange(1e6, 1e8)
        self.sigma_edit.setValue(5.8e7)  # 铜的电导率
        self.sigma_edit.setSuffix('e6')
        input_layout.addWidget(sigma_label, 3, 0)
        input_layout.addWidget(self.sigma_edit, 3, 1)
        
        # 传输线长度
        length_label = QLabel('传输线长度:')
        self.length_edit = QDoubleSpinBox()
        self.length_edit.setRange(0.0, 1000.0)
        self.length_edit.setValue(10.0)
        self.length_unit_combo = QComboBox()
        self.length_unit_combo.addItems(['mm', 'cm', 'm', 'λ'])
        length_layout = QHBoxLayout()
        length_layout.addWidget(self.length_edit)
        length_layout.addWidget(self.length_unit_combo)
        input_layout.addWidget(length_label, 3, 2)
        input_layout.addLayout(length_layout, 3, 3)
        
        main_layout.addWidget(input_group)
        
        # 创建计算按钮区域
        button_layout = QHBoxLayout()
        
        # 计算按钮
        calc_button = QPushButton('计算传输线参数')
        calc_button.setIcon(QIcon('resources/icons/calculate.png'))
        calc_button.clicked.connect(self.calculate_transmission_line)
        button_layout.addWidget(calc_button)
        
        # 阻抗匹配按钮
        match_button = QPushButton('阻抗匹配设计')
        match_button.setIcon(QIcon('resources/icons/match.png'))
        match_button.clicked.connect(self.design_impedance_match)
        button_layout.addWidget(match_button)
        
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
        
        # 创建史密斯圆图区域
        smith_group = QGroupBox('史密斯圆图')
        smith_layout = QVBoxLayout(smith_group)
        
        # 创建史密斯圆图画布
        self.smith_figure, self.smith_ax = plt.subplots(figsize=(6, 6))
        self.smith_canvas = FigureCanvas(self.smith_figure)
        smith_layout.addWidget(self.smith_canvas)
        
        # 史密斯圆图控制按钮
        smith_button_layout = QHBoxLayout()
        
        # 绘制负载阻抗按钮
        plot_load_button = QPushButton('绘制负载阻抗')
        plot_load_button.clicked.connect(self.plot_load_impedance)
        smith_button_layout.addWidget(plot_load_button)
        
        # 绘制传输线按钮
        plot_line_button = QPushButton('绘制传输线')
        plot_line_button.clicked.connect(self.plot_transmission_line)
        smith_button_layout.addWidget(plot_line_button)
        
        # 清空史密斯圆图按钮
        clear_smith_button = QPushButton('清空圆图')
        clear_smith_button.clicked.connect(self.clear_smith_chart)
        smith_button_layout.addWidget(clear_smith_button)
        
        smith_layout.addLayout(smith_button_layout)
        
        main_layout.addWidget(smith_group)
        
        # 填充剩余空间
        main_layout.addStretch()
    
    def update_line_params(self, line_type):
        # 根据传输线类型更新默认参数
        if line_type == '微带线':
            self.z0_edit.setValue(50.0)
            self.er_edit.setValue(4.4)
            self.tand_edit.setValue(0.02)
        elif line_type == '带状线':
            self.z0_edit.setValue(50.0)
            self.er_edit.setValue(3.38)
            self.tand_edit.setValue(0.0027)
        elif line_type == '同轴线':
            self.z0_edit.setValue(50.0)
            self.er_edit.setValue(2.2)
            self.tand_edit.setValue(0.0009)
        elif line_type == '波导':
            self.z0_edit.setValue(50.0)
            self.er_edit.setValue(1.0)
            self.tand_edit.setValue(0.0)
    
    def calculate_transmission_line(self):
        # 计算传输线参数
        try:
            # 获取输入参数
            freq = self.freq_edit.value() * 1e9  # Hz
            z0 = self.z0_edit.value()  # Ω
            zl_real = self.zl_real_edit.value()  # Ω
            zl_imag = self.zl_imag_edit.value()  # Ω
            er = self.er_edit.value()
            tand = self.tand_edit.value()
            sigma = self.sigma_edit.value() * 1e6  # S/m
            length = self.length_edit.value()
            length_unit = self.length_unit_combo.currentText()
            line_type = self.line_type_combo.currentText()
            
            # 计算波长
            c0 = 299792458  # 真空中的光速
            vp = c0 / np.sqrt(er)  # 相速度
            lambda0 = c0 / freq  # 自由空间波长
            lambda_g = vp / freq  # 波导波长
            
            # 转换传输线长度为米
            if length_unit == 'mm':
                length_m = length / 1000
            elif length_unit == 'cm':
                length_m = length / 100
            elif length_unit == 'm':
                length_m = length
            elif length_unit == 'λ':
                length_m = length * lambda_g
            else:
                length_m = length / 1000  # 默认mm
            
            # 计算传播常数
            alpha_conductor = np.sqrt(np.pi * freq * 4e-7 / sigma) / (2 * z0)  # 导体损耗
            alpha_dielectric = (2 * np.pi * freq * np.sqrt(er) / c0) * (tand / 2)  # 介质损耗
            alpha = alpha_conductor + alpha_dielectric  # 总衰减常数
            beta = 2 * np.pi / lambda_g  # 相位常数
            gamma = alpha + 1j * beta  # 传播常数
            
            # 计算输入阻抗
            zl = complex(zl_real, zl_imag)
            zin = z0 * (zl + z0 * np.tanh(gamma * length_m)) / (z0 + zl * np.tanh(gamma * length_m))
            
            # 计算反射系数
            gamma_l = (zl - z0) / (zl + z0)
            gamma_in = gamma_l * np.exp(-2 * gamma * length_m)
            
            # 计算VSWR
            vswr = (1 + abs(gamma_l)) / (1 - abs(gamma_l))
            
            # 计算损耗
            attenuation = 20 * np.log10(1 / abs(gamma_in))  # dB
            
            # 显示结果
            self.display_results({
                '频率': freq,
                '特性阻抗': z0,
                '负载阻抗': zl,
                '介电常数': er,
                '损耗正切': tand,
                '导体电导率': sigma,
                '传输线长度': length_m,
                '自由空间波长': lambda0,
                '波导波长': lambda_g,
                '相速度': vp,
                '衰减常数': alpha,
                '相位常数': beta,
                '传播常数': gamma,
                '输入阻抗': zin,
                '负载反射系数': gamma_l,
                '输入反射系数': gamma_in,
                'VSWR': vswr,
                '衰减': attenuation,
                '传输线类型': line_type
            })
            
            # 保存到历史
            self.history_manager.add_history(
                tool_name='传输线参数计算器',
                input_data=f"频率: {freq/1e9} GHz, 特性阻抗: {z0} Ω, 负载阻抗: {zl_real}+j{zl_imag} Ω",
                output_data=f"输入阻抗: {zin.real:.2f}+j{zin.imag:.2f} Ω, VSWR: {vswr:.2f}, 衰减: {attenuation:.2f} dB",
                calculation_type='transmission_line'
            )
            
        except Exception as e:
            QMessageBox.warning(self, '警告', f'计算错误: {str(e)}')
    
    def display_results(self, results):
        # 显示计算结果到表格
        self.result_table.setRowCount(0)
        self.calculation_results.append(results)
        
        # 添加结果到表格
        self.add_result_row('频率', results['频率']/1e9, 'GHz')
        self.add_result_row('特性阻抗', results['特性阻抗'], 'Ω')
        self.add_result_row('负载阻抗', f"{results['负载阻抗'].real:.2f}+j{results['负载阻抗'].imag:.2f}", 'Ω')
        self.add_result_row('介电常数', results['介电常数'], '')
        self.add_result_row('损耗正切', results['损耗正切'], '')
        self.add_result_row('导体电导率', results['导体电导率']/1e6, 'e6 S/m')
        self.add_result_row('传输线长度', results['传输线长度']*1000, 'mm')
        self.add_result_row('自由空间波长', results['自由空间波长']*1e3, 'mm')
        self.add_result_row('波导波长', results['波导波长']*1e3, 'mm')
        self.add_result_row('相速度', results['相速度']/1e6, 'e6 m/s')
        self.add_result_row('衰减常数', results['衰减常数'], 'Np/m')
        self.add_result_row('相位常数', results['相位常数'], 'rad/m')
        self.add_result_row('输入阻抗', f"{results['输入阻抗'].real:.2f}+j{results['输入阻抗'].imag:.2f}", 'Ω')
        self.add_result_row('负载反射系数', f"{abs(results['负载反射系数']):.4f} ∠{np.angle(results['负载反射系数'], deg=True):.2f}°", '')
        self.add_result_row('输入反射系数', f"{abs(results['输入反射系数']):.4f} ∠{np.angle(results['输入反射系数'], deg=True):.2f}°", '')
        self.add_result_row('VSWR', results['VSWR'], '')
        self.add_result_row('衰减', results['衰减'], 'dB')
        self.add_result_row('传输线类型', results['传输线类型'], '')
        
        # 显示结果详情
        detail_text = "传输线参数计算结果：\n\n"
        detail_text += f"传输线类型: {results['传输线类型']}\n"
        detail_text += f"频率: {results['频率']/1e9:.2f} GHz\n"
        detail_text += f"特性阻抗: {results['特性阻抗']:.2f} Ω\n"
        detail_text += f"负载阻抗: {results['负载阻抗'].real:.2f} + j{results['负载阻抗'].imag:.2f} Ω\n"
        detail_text += f"介电常数: {results['介电常数']:.2f}\n"
        detail_text += f"损耗正切: {results['损耗正切']:.4f}\n"
        detail_text += f"导体电导率: {results['导体电导率']/1e6:.2f}e6 S/m\n"
        detail_text += f"传输线长度: {results['传输线长度']*1000:.2f} mm\n"
        detail_text += f"自由空间波长: {results['自由空间波长']*1e3:.2f} mm\n"
        detail_text += f"波导波长: {results['波导波长']*1e3:.2f} mm\n"
        detail_text += f"相速度: {results['相速度']/1e6:.2f}e6 m/s\n"
        detail_text += f"衰减常数: {results['衰减常数']:.4f} Np/m\n"
        detail_text += f"相位常数: {results['相位常数']:.2f} rad/m\n"
        detail_text += f"输入阻抗: {results['输入阻抗'].real:.2f} + j{results['输入阻抗'].imag:.2f} Ω\n"
        detail_text += f"负载反射系数: {abs(results['负载反射系数']):.4f} ∠{np.angle(results['负载反射系数'], deg=True):.2f}°\n"
        detail_text += f"输入反射系数: {abs(results['输入反射系数']):.4f} ∠{np.angle(results['输入反射系数'], deg=True):.2f}°\n"
        detail_text += f"VSWR: {results['VSWR']:.2f}\n"
        detail_text += f"衰减: {results['衰减']:.2f} dB\n"
        
        self.result_detail.setText(detail_text)
    
    def add_result_row(self, name, value, unit):
        # 添加结果行到表格
        row = self.result_table.rowCount()
        self.result_table.insertRow(row)
        self.result_table.setItem(row, 0, QTableWidgetItem(name))
        self.result_table.setItem(row, 1, QTableWidgetItem(str(value)))
        self.result_table.setItem(row, 2, QTableWidgetItem(unit))
    
    def design_impedance_match(self):
        # 阻抗匹配设计
        try:
            # 获取输入参数
            z0 = self.z0_edit.value()  # Ω
            zl_real = self.zl_real_edit.value()  # Ω
            zl_imag = self.zl_imag_edit.value()  # Ω
            freq = self.freq_edit.value() * 1e9  # Hz
            er = self.er_edit.value()
            
            # 计算负载阻抗
            zl = complex(zl_real, zl_imag)
            
            # 归一化负载阻抗
            z_normalized = zl / z0
            
            # 计算反射系数
            gamma_l = (z_normalized - 1) / (z_normalized + 1)
            
            # 计算匹配所需的传输线长度和阻抗
            # 使用单节传输线匹配
            rho = abs(gamma_l)
            phi = np.angle(gamma_l)
            
            # 计算传输线长度（波长）
            if rho == 1:
                QMessageBox.warning(self, '警告', '负载阻抗为无穷大或零，无法匹配')
                return
            
            theta = (np.arccos((1 - rho**2) / (2 * rho * np.sin(phi))) - phi) / 2
            length_lambda = theta / (2 * np.pi)
            
            # 计算传输线特性阻抗
            z1_normalized = np.sqrt((1 + rho**2 + 2 * rho * np.cos(phi)) / (1 - rho**2))
            z1 = z1_normalized * z0
            
            # 计算匹配网络
            match_network = {
                '类型': '单节传输线匹配',
                '传输线长度': length_lambda,
                '传输线特性阻抗': z1,
                '归一化负载阻抗': z_normalized,
                '反射系数': gamma_l,
                'VSWR': (1 + rho) / (1 - rho)
            }
            
            # 显示匹配结果
            self.display_match_results(match_network)
            
            # 保存到历史
            self.history_manager.add_history(
                tool_name='传输线参数计算器',
                input_data=f"特性阻抗: {z0} Ω, 负载阻抗: {zl_real}+j{zl_imag} Ω",
                output_data=f"匹配传输线长度: {length_lambda:.4f}λ, 特性阻抗: {z1:.2f} Ω",
                calculation_type='impedance_match'
            )
            
        except Exception as e:
            QMessageBox.warning(self, '警告', f'阻抗匹配设计错误: {str(e)}')
    
    def display_match_results(self, match_network):
        # 显示阻抗匹配结果
        result_text = "阻抗匹配设计结果：\n\n"
        result_text += f"匹配网络类型: {match_network['类型']}\n"
        result_text += f"归一化负载阻抗: {match_network['归一化负载阻抗'].real:.2f} + j{match_network['归一化负载阻抗'].imag:.2f}\n"
        result_text += f"负载反射系数: {abs(match_network['反射系数']):.4f} ∠{np.angle(match_network['反射系数'], deg=True):.2f}°\n"
        result_text += f"匹配前VSWR: {match_network['VSWR']:.2f}\n"
        result_text += f"匹配传输线长度: {match_network['传输线长度']:.4f}λ\n"
        result_text += f"匹配传输线特性阻抗: {match_network['传输线特性阻抗']:.2f} Ω\n"
        result_text += "\n匹配后VSWR将接近1.0\n"
        
        self.result_detail.setText(result_text)
        
        # 在史密斯圆图上绘制匹配网络
        self.plot_smith_chart(match_network)
    
    def plot_smith_chart(self, match_network=None):
        # 绘制史密斯圆图
        self.smith_ax.clear()
        
        # 绘制史密斯圆图网格
        self.draw_smith_grid()
        
        if match_network:
            # 绘制负载阻抗
            z_normalized = match_network['归一化负载阻抗']
            self.plot_smith_point(z_normalized.real, z_normalized.imag, 'red', '负载阻抗')
            
            # 绘制匹配传输线
            gamma_l = match_network['反射系数']
            rho = abs(gamma_l)
            phi = np.angle(gamma_l)
            
            # 计算传输线对应的反射系数轨迹
            theta = np.linspace(0, 2 * np.pi * match_network['传输线长度'], 100)
            gamma = rho * np.exp(1j * (phi - 2 * theta))
            
            # 转换为归一化阻抗
            z_real = (1 + gamma.real) / (1 - gamma.real**2 - gamma.imag**2)
            z_imag = gamma.imag / (1 - gamma.real**2 - gamma.imag**2)
            
            # 绘制轨迹
            self.smith_ax.plot(z_real, z_imag, 'b-', linewidth=2, label='传输线轨迹')
            
            # 绘制匹配点（归一化阻抗为1）
            self.plot_smith_point(1.0, 0.0, 'green', '匹配点')
        
        self.smith_ax.legend()
        self.smith_canvas.draw()
    
    def draw_smith_grid(self):
        # 绘制史密斯圆图网格
        # 绘制等电阻圆
        for r in [0.2, 0.5, 1, 2, 5]:
            x = r / (1 + r)
            y = 0
            radius = 1 / (1 + r)
            circle = plt.Circle((x, y), radius, fill=False, color='gray', linestyle='--', linewidth=0.5)
            self.smith_ax.add_patch(circle)
        
        # 绘制等电抗圆
        for x in [-5, -2, -1, -0.5, -0.2, 0.2, 0.5, 1, 2, 5]:
            if x == 0:
                # 绘制虚轴
                self.smith_ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.5)
            else:
                y = 1 / x
                radius = abs(1 / x)
                circle = plt.Circle((1, y), radius, fill=False, color='gray', linestyle='--', linewidth=0.5)
                self.smith_ax.add_patch(circle)
        
        # 绘制单位圆
        unit_circle = plt.Circle((0, 0), 1, fill=False, color='black', linewidth=1)
        self.smith_ax.add_patch(unit_circle)
        
        # 设置坐标轴
        self.smith_ax.set_xlim(-0.1, 2.1)
        self.smith_ax.set_ylim(-1.1, 1.1)
        self.smith_ax.set_aspect('equal')
        self.smith_ax.set_xlabel('归一化电阻')
        self.smith_ax.set_ylabel('归一化电抗')
        self.smith_ax.set_title('史密斯圆图')
        self.smith_ax.grid(True, linestyle='--', alpha=0.5)
    
    def plot_smith_point(self, r, x, color, label):
        # 在史密斯圆图上绘制点
        self.smith_ax.plot(r, x, 'o', color=color, markersize=8, label=label)
        self.smith_ax.text(r + 0.05, x + 0.05, f'({r:.2f}, {x:.2f})', fontsize=8)
    
    def plot_load_impedance(self):
        # 绘制负载阻抗到史密斯圆图
        try:
            z0 = self.z0_edit.value()  # Ω
            zl_real = self.zl_real_edit.value()  # Ω
            zl_imag = self.zl_imag_edit.value()  # Ω
            
            # 归一化负载阻抗
            z_normalized = complex(zl_real, zl_imag) / z0
            
            # 绘制史密斯圆图
            self.smith_ax.clear()
            self.draw_smith_grid()
            self.plot_smith_point(z_normalized.real, z_normalized.imag, 'red', '负载阻抗')
            self.smith_ax.legend()
            self.smith_canvas.draw()
        
        except Exception as e:
            QMessageBox.warning(self, '警告', f'绘制错误: {str(e)}')
    
    def plot_transmission_line(self):
        # 绘制传输线到史密斯圆图
        try:
            z0 = self.z0_edit.value()  # Ω
            zl_real = self.zl_real_edit.value()  # Ω
            zl_imag = self.zl_imag_edit.value()  # Ω
            length = self.length_edit.value()
            length_unit = self.length_unit_combo.currentText()
            freq = self.freq_edit.value() * 1e9  # Hz
            er = self.er_edit.value()
            
            # 计算波长
            c0 = 299792458  # 真空中的光速
            vp = c0 / np.sqrt(er)  # 相速度
            lambda_g = vp / freq  # 波导波长
            
            # 转换传输线长度为波长
            if length_unit == 'mm':
                length_m = length / 1000
            elif length_unit == 'cm':
                length_m = length / 100
            elif length_unit == 'm':
                length_m = length
            elif length_unit == 'λ':
                length_m = length * lambda_g
            else:
                length_m = length / 1000  # 默认mm
            
            length_lambda = length_m / lambda_g
            
            # 归一化负载阻抗
            z_normalized = complex(zl_real, zl_imag) / z0
            
            # 计算反射系数
            gamma_l = (z_normalized - 1) / (z_normalized + 1)
            
            # 计算传输线对应的反射系数轨迹
            theta = np.linspace(0, 2 * np.pi * length_lambda, 100)
            gamma = gamma_l * np.exp(-2j * theta)
            
            # 转换为归一化阻抗
            z_real = (1 + gamma.real) / (1 - gamma.real**2 - gamma.imag**2)
            z_imag = gamma.imag / (1 - gamma.real**2 - gamma.imag**2)
            
            # 绘制史密斯圆图
            self.smith_ax.clear()
            self.draw_smith_grid()
            self.plot_smith_point(z_normalized.real, z_normalized.imag, 'red', '负载阻抗')
            self.smith_ax.plot(z_real, z_imag, 'b-', linewidth=2, label='传输线轨迹')
            
            # 计算输入阻抗
            zin_normalized = (1 + gamma[-1]) / (1 - gamma[-1])
            self.plot_smith_point(zin_normalized.real, zin_normalized.imag, 'blue', '输入阻抗')
            
            self.smith_ax.legend()
            self.smith_canvas.draw()
        
        except Exception as e:
            QMessageBox.warning(self, '警告', f'绘制错误: {str(e)}')
    
    def clear_smith_chart(self):
        # 清空史密斯圆图
        self.smith_ax.clear()
        self.draw_smith_grid()
        self.smith_canvas.draw()
    
    def clear(self):
        # 清空输入和结果
        self.freq_edit.setValue(2.4)
        self.z0_edit.setValue(50.0)
        self.zl_real_edit.setValue(75.0)
        self.zl_imag_edit.setValue(0.0)
        self.er_edit.setValue(4.4)
        self.tand_edit.setValue(0.02)
        self.sigma_edit.setValue(5.8)
        self.length_edit.setValue(10.0)
        self.length_unit_combo.setCurrentText('mm')
        self.result_table.setRowCount(0)
        self.result_detail.clear()
        self.clear_smith_chart()