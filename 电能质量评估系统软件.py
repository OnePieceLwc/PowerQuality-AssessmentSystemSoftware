import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import math
import numpy as np
from tkinter import PhotoImage
from PIL import Image, ImageTk
from PIL import Image

# 电压偏差计算
def calculate_voltage_deviation(voltage, nominal_voltage):
    deviation = (voltage - nominal_voltage) / nominal_voltage
    return deviation

# 频率偏差计算
def calculate_frequency_deviation(frequency, nominal_frequency):
    deviation = frequency - nominal_frequency
    return deviation

# 电压波动计算
def calculate_voltage_fluctuation(u_max, u_min, nominal_voltage):
    fluctuation = (u_max - u_min) / nominal_voltage
    return fluctuation

# 并网测电压偏差计算
def calculate_grid_voltage_deviation(ua, ub, uc):
    u = math.sqrt((ua * ua + ub * ub + uc * uc) / 3)
    deviation = (u - 380) / 380
    return deviation

# 并网侧电压波动计算
def calculate_grid_voltage_fluctuation(ua, ub, uc):
    # 使用numpy库的hilbert函数计算希尔伯特变换
    data = np.array([ua, ub, uc])
    hht = np.fft.fft(data)
    hht_imag = np.imag(hht)
    # 计算包络线
    envelope = np.sqrt(np.real(hht)**2 + hht_imag**2)
    # 计算相邻极差
    diff_sign = np.diff(np.sign(np.diff(envelope)))
    max_index = np.where(diff_sign == -2)[0] + 1
    min_index = np.where(diff_sign == 2)[0] + 1

    # 检查是否有足够的极大值和极小值
    if len(max_index) > 0 and len(min_index) > 0:
        fluctuation = (envelope[max_index[0]] - envelope[min_index[0]]) / 380
        return fluctuation
    else:
        return float('nan')  # 返回一个 NaN 值，表示无法计算

# 三相电压不平衡度计算
def calculate_voltage_unbalance(ua, ub, uc, phaA, phaB, phaC):
    complex_UA = complex(ua * np.cos(phaA), ua * np.sin(phaA))
    complex_UB = complex(ub * np.cos(phaB), ub * np.sin(phaB))
    complex_UC = complex(uc * np.cos(phaC), uc * np.sin(phaC))

    # 计算正序、负序、零序电压
    complex_U1 = complex_UA - 0.5 * (complex_UB + complex_UC) - 0.86602 * (complex_UB.imag - complex_UC.imag) + 0.86602 * (complex_UB.real - complex_UC.real) * 1j
    complex_U2 = complex_UA - 0.5 * (complex_UB + complex_UC) + 0.86602 * (complex_UB.imag - complex_UC.imag) + 0.86602 * (complex_UC.real - complex_UB.real) * 1j
    complex_U0 = (complex_UA + complex_UB + complex_UC) / 3

    # 计算U2/U1
    complex_U2_U1 = complex_U2 / complex_U1

    # 返回不平衡度
    return np.sqrt(complex_U2_U1.real * complex_U2_U1.real + complex_U2_U1.imag * complex_U2_U1.imag)

# 判断合格/不合格
def judge_result(deviation, lower_limit, upper_limit):
    if math.isnan(deviation):
        return "无法计算"
    elif lower_limit <= deviation <= upper_limit:
        return "合格"
    else:
        return "不合格"

# 创建主窗口
window = tk.Tk()
window.title("电能质量评估系统")

# 固定窗口大小
window.geometry("400x300")

# 加载背景图片
bg_image = PhotoImage(file="电能质量评估系统.png")

# 获取图片大小
img = Image.open("电能质量评估系统.png")
width, height = img.size

# 调整图片大小
resized_bg_image = img.resize((int(width * 1.5), int(height * 2)), Image.Resampling.LANCZOS)
resized_bg_image = ImageTk.PhotoImage(resized_bg_image)

# 创建一个标签,并将背景图片设置为标签的背景
bg_label = tk.Label(window, image=resized_bg_image)  # 使用调整后的图片
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# 模式选择
mode_frame = tk.Frame(window)
mode_frame.pack()

modes = ["光伏发电模式", "并网模式", "柴油发电模式"]
mode_var = tk.StringVar(mode_frame)
mode_var.set(modes[0])  # 设置默认模式

for mode in modes:
    tk.Radiobutton(mode_frame, text=mode, variable=mode_var, value=mode).pack(side="left", padx=5)

# 评估指标选择
def show_evaluation_items():
    selected_mode = mode_var.get()
    evaluation_items = []

    if selected_mode == "光伏发电模式":
        evaluation_items = ["电压偏差", "频率偏差", "电压波动"]
    elif selected_mode == "并网模式":
        evaluation_items = ["光伏测电压偏差", "并网侧电压偏差", "系统频率偏差",
                            "光伏侧电压波动", "并网侧电压波动", "电网三相电压不平衡度"]
    elif selected_mode == "柴油发电模式":
        evaluation_items = ["电压偏差", "频率偏差", "电压波动"]

    # 清除之前选择的指标
    for child in evaluation_frame.winfo_children():
        child.destroy()

    # 显示新的指标选择
    for item in evaluation_items:
        tk.Button(evaluation_frame, text=item, command=lambda i=item: show_input_window(i)).pack()

evaluation_frame = tk.Frame(window)
evaluation_frame.pack()

tk.Button(window, text="选择评估指标", command=show_evaluation_items).pack(pady=10)

# 输入窗口
def show_input_window(item):
    input_window = tk.Toplevel(window)
    input_window.title(item)

    input_window.geometry("250x250")

    # 根据指标设置输入项
    input_labels = []
    input_entries = []

    if item == "电压偏差":
        input_labels.append("电压U (V):")
    elif item == "频率偏差":
        input_labels.append("频率f (Hz):")
    elif item == "电压波动":
        input_labels.append("Umax (V):")
        input_labels.append("Umin (V):")
    elif item == "光伏测电压偏差":
        input_labels.append("电压U (V):")
    elif item == "并网侧电压偏差":
        input_labels.append("UA (V):")
        input_labels.append("UB (V):")
        input_labels.append("UC (V):")
    elif item == "系统频率偏差":
        input_labels.append("频率f (Hz):")
    elif item == "光伏侧电压波动":
        input_labels.append("Umax (V):")
        input_labels.append("Umin (V):")
    elif item == "并网侧电压波动":
        input_labels.append("UA (V):")
        input_labels.append("UB (V):")
        input_labels.append("UC (V):")
    elif item == "电网三相电压不平衡度":
        input_labels.append("UA (V):")
        input_labels.append("UB (V):")
        input_labels.append("UC (V):")
        input_labels.append("相位A (度):")
        input_labels.append("相位B (度):")
        input_labels.append("相位C (度):")

    for i, label in enumerate(input_labels):
        tk.Label(input_window, text=label).grid(row=i, column=0, padx=5, pady=5)
        input_entry = tk.Entry(input_window)
        input_entry.grid(row=i, column=1, padx=5, pady=5)
        input_entries.append(input_entry)

    # 计算按钮
    def calculate_and_display():
        # 检查是否输入
        if any([entry.get() == "" for entry in input_entries]):
            messagebox.showwarning("警告", "请输入所有参数！")
            return

        # 获取输入值
        input_values = [float(entry.get()) for entry in input_entries]

        # 进行计算
        result = None
        selected_mode = mode_var.get()
        if item == "电压偏差":
            result = calculate_voltage_deviation(input_values[0], 800)
        elif item == "频率偏差":
            result = calculate_frequency_deviation(input_values[0], 50)
        elif item == "电压波动":
            result = calculate_voltage_fluctuation(input_values[0], input_values[1], 800)
        elif item == "光伏测电压偏差":
            result = calculate_voltage_deviation(input_values[0], 800)
        elif item == "并网侧电压偏差":
            result = calculate_grid_voltage_deviation(input_values[0], input_values[1], input_values[2])
        elif item == "系统频率偏差":
            result = calculate_frequency_deviation(input_values[0], 50)
        elif item == "光伏侧电压波动":
            result = calculate_voltage_fluctuation(input_values[0], input_values[1], 800)
        elif item == "并网侧电压波动":
            result = calculate_grid_voltage_fluctuation(input_values[0], input_values[1], input_values[2])
            if result is not None:  # 检查是否成功计算
                judgment = judge_result(result, -0.04, 0.04)
            else:
                judgment = "无法计算"  # 如果没有足够的极大值和极小值，显示无法计算
        elif item == "电网三相电压不平衡度":
            result = calculate_voltage_unbalance(input_values[0], input_values[1], input_values[2],
                                                input_values[3], input_values[4], input_values[5])

        # 判断合格/不合格
        if item == "电压偏差" or item == "光伏测电压偏差" or item == "并网侧电压偏差":
            judgment = judge_result(result, -0.1, 0.07)
        elif item == "频率偏差" or item == "系统频率偏差":
            judgment = judge_result(result, -0.2, 0.2)
        elif item == "电压波动" or item == "光伏侧电压波动" or item == "并网侧电压波动":
            judgment = judge_result(result, -0.04, 0.04)
        elif item == "电网三相电压不平衡度":
            judgment = judge_result(result, -0.04, 0.04)
        else:
            judgment = "N/A"

        # 显示结果
        messagebox.showinfo(f"{item} 结果", f"计算结果：{result:.7f}\n判断结果：{judgment}")

    tk.Button(input_window, text="计算", command=calculate_and_display).grid(row=len(input_labels), column=0, columnspan=2, pady=10)

window.mainloop()
