import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtWidgets

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, 
                                   QtWidgets.QSizePolicy.Expanding, 
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

def plot_wavelength_distribution(frequencies, wavelengths,介质=None):
    """
    绘制频率与波长的关系图
    
    参数:
    frequencies: 频率数组 (Hz)
    wavelengths: 波长数组 (m)
    介质: 介质名称 (可选)
    
    返回:
    PlotCanvas: 包含图表的Qt部件
    """
    canvas = PlotCanvas(width=8, height=6, dpi=100)
    
    # 清除之前的绘图
    canvas.axes.clear()
    
    # 绘制频率与波长的关系
    canvas.axes.plot(frequencies, wavelengths, 'b-', linewidth=2, label='波长')
    
    # 设置坐标轴标签
    canvas.axes.set_xlabel('频率 (Hz)', fontsize=12)
    canvas.axes.set_ylabel('波长 (m)', fontsize=12)
    
    # 设置标题
    if 介质:
        canvas.axes.set_title(f'频率与波长的关系 ({介质})', fontsize=14, fontweight='bold')
    else:
        canvas.axes.set_title('频率与波长的关系', fontsize=14, fontweight='bold')
    
    # 添加网格
    canvas.axes.grid(True, linestyle='--', alpha=0.7)
    
    # 添加图例
    canvas.axes.legend()
    
    # 自动调整布局
    canvas.fig.tight_layout()
    
    return canvas

def plot_power_conversion(power_values, unit_from, unit_to):
    """
    绘制功率转换结果图
    
    参数:
    power_values: 功率值数组
    unit_from: 原始单位
    unit_to: 目标单位
    
    返回:
    PlotCanvas: 包含图表的Qt部件
    """
    canvas = PlotCanvas(width=8, height=6, dpi=100)
    
    # 清除之前的绘图
    canvas.axes.clear()
    
    # 创建x轴数据 (样本索引)
    x = np.arange(len(power_values))
    
    # 绘制功率转换结果
    canvas.axes.plot(x, power_values, 'r-', linewidth=2, marker='o', markersize=5)
    
    # 设置坐标轴标签
    canvas.axes.set_xlabel('样本', fontsize=12)
    canvas.axes.set_ylabel(f'功率 ({unit_to})', fontsize=12)
    
    # 设置标题
    canvas.axes.set_title(f'功率转换结果: {unit_from} 到 {unit_to}', fontsize=14, fontweight='bold')
    
    # 添加网格
    canvas.axes.grid(True, linestyle='--', alpha=0.7)
    
    # 自动调整布局
    canvas.fig.tight_layout()
    
    return canvas

def plot_transmission_line_parameters(frequency, parameter_values, parameter_name, unit):
    """
    绘制传输线参数随频率变化的关系图
    
    参数:
    frequency: 频率数组 (Hz)
    parameter_values: 参数值数组
    parameter_name: 参数名称 (如"特性阻抗", "衰减常数")
    unit: 参数单位
    
    返回:
    PlotCanvas: 包含图表的Qt部件
    """
    canvas = PlotCanvas(width=8, height=6, dpi=100)
    
    # 清除之前的绘图
    canvas.axes.clear()
    
    # 绘制参数随频率变化的关系
    canvas.axes.plot(frequency, parameter_values, 'g-', linewidth=2)
    
    # 设置坐标轴标签
    canvas.axes.set_xlabel('频率 (Hz)', fontsize=12)
    canvas.axes.set_ylabel(f'{parameter_name} ({unit})', fontsize=12)
    
    # 设置标题
    canvas.axes.set_title(f'{parameter_name} 随频率变化的关系', fontsize=14, fontweight='bold')
    
    # 添加网格
    canvas.axes.grid(True, linestyle='--', alpha=0.7)
    
    # 自动调整布局
    canvas.fig.tight_layout()
    
    return canvas

def plot_antenna_radiation_pattern(theta, phi, gain, antenna_type):
    """
    绘制天线辐射方向图
    
    参数:
    theta: 方位角数组
    phi: 仰角数组
    gain: 增益数组
    antenna_type: 天线类型
    
    返回:
    PlotCanvas: 包含图表的Qt部件
    """
    canvas = PlotCanvas(width=8, height=6, dpi=100)
    
    # 清除之前的绘图
    canvas.axes.clear()
    
    # 创建极坐标图
    ax = canvas.fig.add_subplot(111, projection='polar')
    
    # 绘制辐射方向图
    ax.plot(theta, gain, 'b-', linewidth=2)
    
    # 设置标题
    ax.set_title(f'{antenna_type} 辐射方向图', fontsize=14, fontweight='bold', y=1.1)
    
    # 添加网格
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # 自动调整布局
    canvas.fig.tight_layout()
    
    return canvas

def plot_filter_response(frequency, magnitude, phase, filter_type):
    """
    绘制滤波器的幅频响应和相频响应
    
    参数:
    frequency: 频率数组 (Hz)
    magnitude: 幅度响应数组 (dB)
    phase: 相位响应数组 (度)
    filter_type: 滤波器类型
    
    返回:
    PlotCanvas: 包含图表的Qt部件
    """
    canvas = PlotCanvas(width=10, height=6, dpi=100)
    
    # 清除之前的绘图
    canvas.axes.clear()
    
    # 创建上下两个子图
    ax1 = canvas.fig.add_subplot(211)
    ax2 = canvas.fig.add_subplot(212)
    
    # 绘制幅频响应
    ax1.plot(frequency, magnitude, 'b-', linewidth=2)
    ax1.set_title(f'{filter_type} 滤波器响应', fontsize=14, fontweight='bold')
    ax1.set_ylabel('幅度 (dB)', fontsize=12)
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    # 绘制相频响应
    ax2.plot(frequency, phase, 'r-', linewidth=2)
    ax2.set_xlabel('频率 (Hz)', fontsize=12)
    ax2.set_ylabel('相位 (度)', fontsize=12)
    ax2.grid(True, linestyle='--', alpha=0.7)
    
    # 自动调整布局
    canvas.fig.tight_layout()
    
    return canvas

def plot_link_budget(components, gains, losses):
    """
    绘制链路预算的增益和损耗分布
    
    参数:
    components: 组件名称数组
    gains: 增益数组 (dB)
    losses: 损耗数组 (dB)
    
    返回:
    PlotCanvas: 包含图表的Qt部件
    """
    canvas = PlotCanvas(width=10, height=6, dpi=100)
    
    # 清除之前的绘图
    canvas.axes.clear()
    
    # 创建x轴数据 (组件索引)
    x = np.arange(len(components))
    
    # 绘制增益和损耗
    canvas.axes.bar(x - 0.2, gains, 0.4, label='增益 (dB)', color='g')
    canvas.axes.bar(x + 0.2, losses, 0.4, label='损耗 (dB)', color='r')
    
    # 设置坐标轴标签
    canvas.axes.set_xlabel('组件', fontsize=12)
    canvas.axes.set_ylabel('值 (dB)', fontsize=12)
    
    # 设置标题
    canvas.axes.set_title('链路预算分布', fontsize=14, fontweight='bold')
    
    # 设置x轴刻度标签
    canvas.axes.set_xticks(x)
    canvas.axes.set_xticklabels(components, rotation=45, ha='right')
    
    # 添加网格
    canvas.axes.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    # 添加图例
    canvas.axes.legend()
    
    # 自动调整布局
    canvas.fig.tight_layout()
    
    return canvas

def plot_smith_chart(reflection_coefficient):
    """
    绘制史密斯圆图
    
    参数:
    reflection_coefficient: 反射系数数组
    
    返回:
    PlotCanvas: 包含图表的Qt部件
    """
    canvas = PlotCanvas(width=8, height=6, dpi=100)
    
    # 清除之前的绘图
    canvas.axes.clear()
    
    # 创建史密斯圆图
    ax = canvas.fig.add_subplot(111, projection='polar')
    
    # 绘制单位圆
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(theta, np.ones_like(theta), 'k-', linewidth=2)
    
    # 绘制反射系数点
    for gamma in reflection_coefficient:
        ax.plot(np.angle(gamma), np.abs(gamma), 'ro', markersize=5)
    
    # 设置标题
    ax.set_title('史密斯圆图', fontsize=14, fontweight='bold', y=1.1)
    
    # 添加网格
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # 自动调整布局
    canvas.fig.tight_layout()
    
    return canvas