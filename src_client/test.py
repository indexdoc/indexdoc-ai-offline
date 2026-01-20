import tkinter as tk

# 创建窗口
root = tk.Tk()
root.title("Tkinter 测试窗口")

# 创建按钮
quit_button = tk.Button(root, text="Quit", command=root.quit)
quit_button.pack()

# 启动 Tkinter 主事件循环
root.mainloop()
