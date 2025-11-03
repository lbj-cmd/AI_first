import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import math

class RFToolbox:
    def __init__(self, root):
        self.root = root
        self.root.title("RF Toolbox V1.0")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # 存储计算历史
        self.calc_history = []

        # 创建主布局（左侧导航+右侧内容）
        self.create_navigation()
        self.create_content_frame()

        # 默认显示首页
        self.show_home()

    def create_navigation(self):
        """创建左侧导航栏"""
        nav_frame = tk.Frame(self.root, width=150, bg="#333", height=600, relief="sunken", bd=2)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y)
        nav_frame.pack_propagate(False)

        # 导航按钮
        buttons = [
            ("首页", self.show_home),
            ("频率-波长计算", self.show_freq_wavelength),
            ("功率单位换算", self.show_power_converter),
            ("传输线参数计算", self.show_transmission_line),
            ("射频常识库", self.show_knowledge_base),
            ("计算历史", self.show_history)
        ]

        for text, command in buttons:
            btn = tk.Button(
                nav_frame, text=text, command=command,
                bg="#555", fg="white", width=15, height=2,
                relief="flat", font=("SimHei", 10)
            )
            btn.pack(pady=5, padx=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#777"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#555"))

    def create_content_frame(self):
        """创建右侧内容显示区"""
        self.content_frame = tk.Frame(self.root, bg="#f0f0f0", width=650, height=600)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def clear_content(self):
        """清空内容区"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # ------------------------------
    # 首页
    # ------------------------------
    def show_home(self):
        self.clear_content()
        title = tk.Label(
            self.content_frame, text="RF Toolbox 射频工具箱",
            font=("SimHei", 20, "bold"), bg="#f0f0f0", pady=20
        )
        title.pack()

        desc = tk.Label(
            self.content_frame, 
            text="一款专注于射频领域基础计算与常识查询的工具\n"
                 "支持频率-波长转换、功率单位换算、传输线参数计算等功能",
            font=("SimHei", 12), bg="#f0f0f0", justify=tk.CENTER
        )
        desc.pack(pady=10)

        # 快捷功能入口
        tk.Label(self.content_frame, text="常用工具", font=("SimHei", 14, "bold"), bg="#f0f0f0").pack(pady=10)
        tools_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        tools_frame.pack(pady=10)

        tools = [
            ("频率-波长计算", self.show_freq_wavelength),
            ("功率单位换算", self.show_power_converter),
            ("传输线参数计算", self.show_transmission_line)
        ]

        for i, (text, cmd) in enumerate(tools):
            btn = tk.Button(
                tools_frame, text=text, command=cmd,
                width=20, height=3, font=("SimHei", 11),
                bg="#4CAF50", fg="white", relief="raised"
            )
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)

    # ------------------------------
    # 1. 频率-波长计算器
    # ------------------------------
    def show_freq_wavelength(self):
        self.clear_content()
        tk.Label(
            self.content_frame, text="频率-波长计算器",
            font=("SimHei", 16, "bold"), bg="#f0f0f0"
        ).pack(pady=10)

        frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        frame.pack(padx=20, fill=tk.X)

        # 输入频率
        tk.Label(frame, text="输入频率：", font=("SimHei", 12), bg="#f0f0f0").grid(row=0, column=0, pady=10)
        self.freq_value = tk.StringVar()
        ttk.Entry(frame, textvariable=self.freq_value, width=15, font=("SimHei", 12)).grid(row=0, column=1)
        
        self.freq_unit = tk.StringVar(value="GHz")
        ttk.Combobox(
            frame, textvariable=self.freq_unit, 
            values=["Hz", "KHz", "MHz", "GHz"], width=8
        ).grid(row=0, column=2, padx=5)

        # 介质介电常数
        tk.Label(frame, text="介质介电常数 (ε)：", font=("SimHei", 12), bg="#f0f0f0").grid(row=1, column=0, pady=10)
        self.epsilon = tk.StringVar(value="1")  # 空气默认1
        ttk.Entry(frame, textvariable=self.epsilon, width=15, font=("SimHei", 12)).grid(row=1, column=1)

        # 计算按钮
        calc_btn = tk.Button(
            frame, text="计算波长", command=self.calc_wavelength,
            bg="#2196F3", fg="white", font=("SimHei", 12)
        )
        calc_btn.grid(row=2, column=0, columnspan=3, pady=10)

        # 结果显示
        self.wavelength_result = tk.StringVar()
        tk.Label(
            self.content_frame, textvariable=self.wavelength_result,
            font=("SimHei", 12), bg="#f0f0f0", fg="red"
        ).pack(pady=20)

        # 公式说明
        tk.Label(
            self.content_frame, text="公式：λ = c / (f × √ε)  （c=3×10^8 m/s）",
            font=("SimHei", 10), bg="#f0f0f0", fg="#666"
        ).pack(anchor=tk.W, padx=20)

    def calc_wavelength(self):
        try:
            # 解析输入
            freq = float(self.freq_value.get())
            unit = self.freq_unit.get()
            epsilon = float(self.epsilon.get())

            # 频率单位转换为Hz
            unit_factor = {
                "Hz": 1,
                "KHz": 1e3,
                "MHz": 1e6,
                "GHz": 1e9
            }[unit]
            freq_hz = freq * unit_factor

            # 计算波长（米）
            c = 3e8  # 光速
            wavelength_m = c / (freq_hz * math.sqrt(epsilon))

            # 转换为合适单位
            if wavelength_m >= 1:
                result = f"波长 = {wavelength_m:.3f} 米 (m)"
            elif wavelength_m >= 0.01:
                result = f"波长 = {wavelength_m*100:.3f} 厘米 (cm)"
            else:
                result = f"波长 = {wavelength_m*1000:.3f} 毫米 (mm)"

            self.wavelength_result.set(result)
            self.calc_history.append(f"频率-波长：{freq}{unit} → {result}")

        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字！")

    # ------------------------------
    # 2. 功率单位换算器
    # ------------------------------
    def show_power_converter(self):
        self.clear_content()
        tk.Label(
            self.content_frame, text="功率单位换算器",
            font=("SimHei", 16, "bold"), bg="#f0f0f0"
        ).pack(pady=10)

        frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        frame.pack(padx=20, fill=tk.X)

        # 输入功率
        tk.Label(frame, text="输入功率：", font=("SimHei", 12), bg="#f0f0f0").grid(row=0, column=0, pady=10)
        self.power_value = tk.StringVar()
        ttk.Entry(frame, textvariable=self.power_value, width=15, font=("SimHei", 12)).grid(row=0, column=1)
        
        self.power_unit = tk.StringVar(value="dBm")
        ttk.Combobox(
            frame, textvariable=self.power_unit, 
            values=["dBm", "W", "dBW"], width=8
        ).grid(row=0, column=2, padx=5)

        # 转换按钮
        calc_btn = tk.Button(
            frame, text="转换", command=self.convert_power,
            bg="#2196F3", fg="white", font=("SimHei", 12)
        ).grid(row=1, column=0, columnspan=3, pady=10)

        # 结果显示
        self.power_result = tk.Text(self.content_frame, height=5, width=50, font=("SimHei", 12))
        self.power_result.pack(pady=20)

        # 公式说明
        tk.Label(
            self.content_frame, 
            text="公式：\n"
                 "dBm = 10×log10(P(mW))\n"
                 "dBW = 10×log10(P(W))\n"
                 "1 W = 1000 mW = 30 dBm = 0 dBW",
            font=("SimHei", 10), bg="#f0f0f0", fg="#666", justify=tk.LEFT
        ).pack(anchor=tk.W, padx=20)

    def convert_power(self):
        try:
            power = float(self.power_value.get())
            unit = self.power_unit.get()
            result = []

            if unit == "dBm":
                # dBm → mW → W → dBW
                mw = 10 **(power / 10)
                w = mw / 1000
                dbw = power - 30
                result = [
                    f"{power} dBm = {mw:.3f} mW",
                    f"{power} dBm = {w:.6f} W",
                    f"{power} dBm = {dbw:.3f} dBW"
                ]

            elif unit == "W":
                # W → mW → dBm → dBW
                mw = power * 1000
                dbm = 10 * math.log10(mw) if mw > 0 else -float('inf')
                dbw = 10 * math.log10(power) if power > 0 else -float('inf')
                result = [
                    f"{power} W = {mw:.3f} mW",
                    f"{power} W = {dbm:.3f} dBm",
                    f"{power} W = {dbw:.3f} dBW"
                ]

            elif unit == "dBW":
                # dBW → W → mW → dBm
                w = 10** (power / 10)
                mw = w * 1000
                dbm = power + 30
                result = [
                    f"{power} dBW = {w:.6f} W",
                    f"{power} dBW = {mw:.3f} mW",
                    f"{power} dBW = {dbm:.3f} dBm"
                ]

            self.power_result.delete(1.0, tk.END)
            self.power_result.insert(tk.END, "\n".join(result))
            self.calc_history.append(f"功率转换：{power}{unit} → {result[0]}")

        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字！")
        except Exception as e:
            messagebox.showerror("错误", f"计算失败：{str(e)}")

    # ------------------------------
    # 3. 传输线参数计算（VSWR/反射系数/回波损耗）
    # ------------------------------
    def show_transmission_line(self):
        self.clear_content()
        tk.Label(
            self.content_frame, text="传输线参数计算",
            font=("SimHei", 16, "bold"), bg="#f0f0f0"
        ).pack(pady=10)

        frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        frame.pack(padx=20, fill=tk.X)

        # 输入参数类型选择
        tk.Label(frame, text="输入参数类型：", font=("SimHei", 12), bg="#f0f0f0").grid(row=0, column=0, pady=10)
        self.tline_param_type = tk.StringVar(value="VSWR")
        ttk.Combobox(
            frame, textvariable=self.tline_param_type, 
            values=["VSWR", "反射系数(Γ)", "回波损耗(dB)"], width=15
        ).grid(row=0, column=1, padx=5)

        # 输入值
        tk.Label(frame, text="输入值：", font=("SimHei", 12), bg="#f0f0f0").grid(row=1, column=0, pady=10)
        self.tline_value = tk.StringVar()
        ttk.Entry(frame, textvariable=self.tline_value, width=15, font=("SimHei", 12)).grid(row=1, column=1)

        # 计算按钮
        calc_btn = tk.Button(
            frame, text="计算其他参数", command=self.calc_transmission_line,
            bg="#2196F3", fg="white", font=("SimHei", 12)
        ).grid(row=2, column=0, columnspan=2, pady=10)

        # 结果显示
        self.tline_result = tk.Text(self.content_frame, height=5, width=50, font=("SimHei", 12))
        self.tline_result.pack(pady=20)

        # 公式说明
        tk.Label(
            self.content_frame, 
            text="公式：\n"
                 "VSWR = (1 + |Γ|) / (1 - |Γ|)\n"
                 "回波损耗 RL(dB) = -20×log10(|Γ|)\n"
                 "（Γ为反射系数，范围0~1）",
            font=("SimHei", 10), bg="#f0f0f0", fg="#666", justify=tk.LEFT
        ).pack(anchor=tk.W, padx=20)

    def calc_transmission_line(self):
        try:
            value = float(self.tline_value.get())
            param_type = self.tline_param_type.get()
            result = []

            if param_type == "VSWR":
                if value < 1:
                    raise ValueError("VSWR值必须≥1")
                gamma = (value - 1) / (value + 1)  # 反射系数
                rl = -20 * math.log10(gamma)       # 回波损耗
                result = [
                    f"VSWR = {value} → 反射系数 Γ = {gamma:.3f}",
                    f"VSWR = {value} → 回波损耗 RL = {rl:.3f} dB"
                ]

            elif param_type == "反射系数(Γ)":
                if not (0 <= value <= 1):
                    raise ValueError("反射系数范围应为0~1")
                vswr = (1 + value) / (1 - value)
                rl = -20 * math.log10(value)
                result = [
                    f"反射系数 Γ = {value} → VSWR = {vswr:.3f}",
                    f"反射系数 Γ = {value} → 回波损耗 RL = {rl:.3f} dB"
                ]

            elif param_type == "回波损耗(dB)":
                if value < 0:
                    raise ValueError("回波损耗值应为正数")
                gamma = 10 **(-value / 20)
                vswr = (1 + gamma) / (1 - gamma)
                result = [
                    f"回波损耗 RL = {value} dB → 反射系数 Γ = {gamma:.3f}",
                    f"回波损耗 RL = {value} dB → VSWR = {vswr:.3f}"
                ]

            self.tline_result.delete(1.0, tk.END)
            self.tline_result.insert(tk.END, "\n".join(result))
            self.calc_history.append(f"传输线参数：{value}{param_type} → {result[0]}")

        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
        except Exception as e:
            messagebox.showerror("错误", f"计算失败：{str(e)}")

    # ------------------------------
    # 4. 射频常识库（简化版）
    # ------------------------------
    def show_knowledge_base(self):
        self.clear_content()
        tk.Label(
            self.content_frame, text="射频常识库",
            font=("SimHei", 16, "bold"), bg="#f0f0f0"
        ).pack(pady=10)

        # 创建标签页分类显示
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # 1. 核心概念
        concept_frame = tk.Frame(notebook, bg="#f0f0f0")
        notebook.add(concept_frame, text="核心概念")
        concept_text = scrolledtext.ScrolledText(concept_frame, wrap=tk.WORD, font=("SimHei", 10))
        concept_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        concept_text.insert(tk.END, """
1. 频率与波长
   - 频率(f)：电磁波每秒振动的次数，单位Hz（赫兹），常用单位：KHz(1e3)、MHz(1e6)、GHz(1e9)
   - 波长(λ)：电磁波在一个周期内传播的距离，单位米(m)
   - 关系：λ = c / f （真空中c=3×10^8 m/s）

2. 功率单位
   - dBm：以1mW为参考的功率分贝，公式：dBm = 10×log10(P(mW))
   - dBW：以1W为参考的功率分贝，公式：dBW = 10×log10(P(W))
   - 换算：1W = 30 dBm = 0 dBW；0 dBm = 1 mW

3. 传输线关键参数
   - 驻波比(VSWR)：衡量阻抗匹配程度，理想值=1（完全匹配），值越大匹配越差
   - 反射系数(Γ)：反射波与入射波的振幅比，范围0~1，0表示无反射
   - 回波损耗(RL)：反射功率的衰减量，单位dB，值越大反射越小（匹配越好）
            """)
        concept_text.config(state=tk.DISABLED)

        # 2. 频段划分
        band_frame = tk.Frame(notebook, bg="#f0f0f0")
        notebook.add(band_frame, text="频段划分")
        band_text = scrolledtext.ScrolledText(band_frame, wrap=tk.WORD, font=("SimHei", 10))
        band_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        band_text.insert(tk.END, """
常用射频频段划分：
- HF（高频）：3~30 MHz，用于短波通信
- VHF（甚高频）：30~300 MHz，用于FM广播、电视、对讲机
- UHF（特高频）：300 MHz~3 GHz，用于WiFi(2.4GHz)、蓝牙、电视
- SHF（超高频）：3~30 GHz，用于5G(Sub-6GHz)、卫星通信、雷达
- EHF（极高频）：30~300 GHz，用于毫米波雷达、6G试验频段

5G NR主要频段：
- FR1（Sub-6GHz）：450 MHz~6 GHz（主流商用频段）
- FR2（毫米波）：24.25~52.6 GHz（高速率场景）
            """)
        band_text.config(state=tk.DISABLED)

    # ------------------------------
    # 5. 计算历史
    # ------------------------------
    def show_history(self):
        self.clear_content()
        tk.Label(
            self.content_frame, text="计算历史",
            font=("SimHei", 16, "bold"), bg="#f0f0f0"
        ).pack(pady=10)

        history_text = scrolledtext.ScrolledText(self.content_frame, wrap=tk.WORD, font=("SimHei", 11))
        history_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        if not self.calc_history:
            history_text.insert(tk.END, "暂无计算记录")
        else:
            for i, record in enumerate(reversed(self.calc_history[-10:]), 1):  # 显示最近10条
                history_text.insert(tk.END, f"{i}. {record}\n\n")

        history_text.config(state=tk.DISABLED)

        # 清空历史按钮
        clear_btn = tk.Button(
            self.content_frame, text="清空历史", command=lambda: self.clear_history(history_text),
            bg="#f44336", fg="white", font=("SimHei", 10)
        )
        clear_btn.pack(pady=10)

    def clear_history(self, text_widget):
        self.calc_history = []
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, "暂无计算记录")
        text_widget.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = RFToolbox(root)
    root.mainloop()
