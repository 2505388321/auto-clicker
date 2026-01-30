# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import random
import time
import threading
import math
import sys
from pynput import keyboard

pyautogui.FAILSAFE = False

def get_pixel_color(x, y):
    try:
        img = pyautogui.screenshot(region=(x, y, 1, 1))
        return img.getpixel((0, 0))
    except:
        return (0, 0, 0)

def color_distance(c1, c2):
    return math.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2)

def find_color_nearby(tx, ty, target_color, radius=200, tolerance=30):
    best_pos = (tx, ty)
    best_dist = float('inf')
    c = get_pixel_color(tx, ty)
    if color_distance(c, target_color) <= tolerance:
        return tx, ty
    for r in range(5, radius+1, 5):
        for angle in range(0, 360, 15):
            x = int(tx + r * math.cos(math.radians(angle)))
            y = int(ty + r * math.sin(math.radians(angle)))
            c = get_pixel_color(x, y)
            d = color_distance(c, target_color)
            if d < best_dist:
                best_dist = d
                best_pos = (x, y)
            if d <= tolerance:
                return x, y
    return best_pos if best_dist <= tolerance * 2 else (tx, ty)

def human_path(sx, sy, ex, ey):
    pts = [(sx, sy)]
    dist = math.sqrt((ex-sx)**2 + (ey-sy)**2)
    for i in range(random.randint(2, 5)):
        p = (i+1) / (random.randint(2,5)+1)
        off = dist * 0.3 * (1 - abs(p-0.5)*2)
        ox, oy = random.uniform(-off, off), random.uniform(-off, off)
        if random.random() < 0.2: ox, oy = ox*random.uniform(1.5,2.5), oy*random.uniform(1.5,2.5)
        pts.append((sx+(ex-sx)*p+ox, sy+(ey-sy)*p+oy))
    pts.append((ex, ey))
    smooth = []
    for i in range(len(pts)-1):
        for j in range(random.randint(8,15)):
            t = j / random.randint(8,15)
            smooth.append((int(pts[i][0]+(pts[i+1][0]-pts[i][0])*t+random.uniform(-3,3)),
                          int(pts[i][1]+(pts[i+1][1]-pts[i][1])*t+random.uniform(-3,3))))
    smooth.append((ex, ey))
    return smooth


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("自动点击器")
        self.root.geometry("400x680")
        self.root.resizable(False, False)
        self.running, self.count = False, 0
        
        self.p1x, self.p1y = tk.StringVar(value="0"), tk.StringVar(value="0")
        self.p2x, self.p2y = tk.StringVar(value="0"), tk.StringVar(value="0")
        self.c1 = tk.StringVar(value="未采集")
        self.c2 = tk.StringVar(value="未采集")
        self.color1, self.color2 = None, None
        self.round_min, self.round_max = tk.StringVar(value="4"), tk.StringVar(value="6")
        self.m_min, self.m_max = tk.StringVar(value="0.3"), tk.StringVar(value="0.8")
        self.amount = tk.StringVar(value="10")
        self.search_radius = tk.StringVar(value="200")
        self.use_color = tk.BooleanVar(value=True)
        
        self.build_ui()
        self.listen_keys()
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        
    def build_ui(self):
        m = ttk.Frame(self.root, padding="10")
        m.pack(fill='both', expand=True)
        
        # 位置1
        f1 = ttk.LabelFrame(m, text="点击位置 1", padding="6")
        f1.pack(fill='x', pady=2)
        r1 = ttk.Frame(f1)
        r1.pack(fill='x')
        ttk.Label(r1, text="X:").pack(side='left')
        ttk.Entry(r1, textvariable=self.p1x, width=7).pack(side='left', padx=(2,8))
        ttk.Label(r1, text="Y:").pack(side='left')
        ttk.Entry(r1, textvariable=self.p1y, width=7).pack(side='left', padx=(2,8))
        ttk.Button(r1, text="采集(F1)", command=lambda:self.get_pos(1), width=9).pack(side='left')
        r1c = ttk.Frame(f1)
        r1c.pack(fill='x', pady=(3,0))
        ttk.Label(r1c, text="颜色:").pack(side='left')
        self.lbl_c1 = ttk.Label(r1c, textvariable=self.c1, width=18)
        self.lbl_c1.pack(side='left', padx=5)
        self.box_c1 = tk.Label(r1c, width=3, bg='gray')
        self.box_c1.pack(side='left')
        
        # 位置2
        f2 = ttk.LabelFrame(m, text="点击位置 2", padding="6")
        f2.pack(fill='x', pady=2)
        r2 = ttk.Frame(f2)
        r2.pack(fill='x')
        ttk.Label(r2, text="X:").pack(side='left')
        ttk.Entry(r2, textvariable=self.p2x, width=7).pack(side='left', padx=(2,8))
        ttk.Label(r2, text="Y:").pack(side='left')
        ttk.Entry(r2, textvariable=self.p2y, width=7).pack(side='left', padx=(2,8))
        ttk.Button(r2, text="采集(F2)", command=lambda:self.get_pos(2), width=9).pack(side='left')
        r2c = ttk.Frame(f2)
        r2c.pack(fill='x', pady=(3,0))
        ttk.Label(r2c, text="颜色:").pack(side='left')
        self.lbl_c2 = ttk.Label(r2c, textvariable=self.c2, width=18)
        self.lbl_c2.pack(side='left', padx=5)
        self.box_c2 = tk.Label(r2c, width=3, bg='gray')
        self.box_c2.pack(side='left')
        
        # 颜色搜索设置
        fc = ttk.LabelFrame(m, text="颜色识别", padding="6")
        fc.pack(fill='x', pady=2)
        rc = ttk.Frame(fc)
        rc.pack(fill='x')
        ttk.Checkbutton(rc, text="启用颜色定位", variable=self.use_color).pack(side='left')
        ttk.Label(rc, text="搜索半径:").pack(side='left', padx=(15,0))
        ttk.Entry(rc, textvariable=self.search_radius, width=5).pack(side='left', padx=2)
        ttk.Label(rc, text="像素").pack(side='left')
        
        # 移动时间
        f3 = ttk.LabelFrame(m, text="鼠标移动时间(秒)", padding="6")
        f3.pack(fill='x', pady=2)
        r3 = ttk.Frame(f3)
        r3.pack(fill='x')
        ttk.Label(r3, text="最小:").pack(side='left')
        ttk.Entry(r3, textvariable=self.m_min, width=6).pack(side='left', padx=(2,15))
        ttk.Label(r3, text="最大:").pack(side='left')
        ttk.Entry(r3, textvariable=self.m_max, width=6).pack(side='left')
        
        # 轮次间隔
        f4 = ttk.LabelFrame(m, text="轮次间隔 - 完成一轮后等待(秒)", padding="6")
        f4.pack(fill='x', pady=2)
        r4 = ttk.Frame(f4)
        r4.pack(fill='x')
        ttk.Label(r4, text="最小:").pack(side='left')
        ttk.Entry(r4, textvariable=self.round_min, width=6).pack(side='left', padx=(2,15))
        ttk.Label(r4, text="最大:").pack(side='left')
        ttk.Entry(r4, textvariable=self.round_max, width=6).pack(side='left')
        ttk.Label(m, text="※ 交易所卡、成交慢时，请调大轮次间隔", foreground='red', font=('微软雅黑', 8)).pack(anchor='w')
        
        # 订单
        f5 = ttk.LabelFrame(m, text="订单设置", padding="6")
        f5.pack(fill='x', pady=2)
        r5 = ttk.Frame(f5)
        r5.pack(fill='x')
        ttk.Label(r5, text="每笔:").pack(side='left')
        ttk.Entry(r5, textvariable=self.amount, width=6).pack(side='left', padx=(2,3))
        ttk.Label(r5, text="U    (总额 = 每笔 × 2 × 次数)").pack(side='left')
        
        # 按钮
        bf = ttk.Frame(m)
        bf.pack(fill='x', pady=10)
        self.btn_start = ttk.Button(bf, text="▶ 开始(A)", command=self.start, width=14)
        self.btn_start.pack(side='left', padx=5, expand=True)
        self.btn_stop = ttk.Button(bf, text="⏹ 停止(S)", command=self.stop, width=14, state='disabled')
        self.btn_stop.pack(side='left', padx=5, expand=True)
        
        # 状态
        sf = ttk.LabelFrame(m, text="运行状态", padding="15")
        sf.pack(fill='both', expand=True, pady=5)
        self.lbl_status = ttk.Label(sf, text="⏸ 等待启动", font=('微软雅黑', 11))
        self.lbl_status.pack()
        self.lbl_count = ttk.Label(sf, text="次数：0", font=('微软雅黑', 14, 'bold'))
        self.lbl_count.pack(pady=10)
        self.lbl_total = ttk.Label(sf, text="总额：0 U", font=('微软雅黑', 12))
        self.lbl_total.pack()
        
        ttk.Label(m, text="F1/F2采集 | A开始 | S停止", foreground='gray', font=('微软雅黑', 9)).pack(pady=10)
        
    def get_pos(self, n):
        x, y = pyautogui.position()
        color = get_pixel_color(x, y)
        hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
        
        if n == 1:
            self.p1x.set(str(x))
            self.p1y.set(str(y))
            self.color1 = color
            self.c1.set(f"RGB{color}")
            self.box_c1.config(bg=hex_color)
        else:
            self.p2x.set(str(x))
            self.p2y.set(str(y))
            self.color2 = color
            self.c2.set(f"RGB{color}")
            self.box_c2.config(bg=hex_color)
            
    def listen_keys(self):
        def on_press(key):
            try:
                if key == keyboard.Key.f1: self.root.after(0, lambda: self.get_pos(1))
                elif key == keyboard.Key.f2: self.root.after(0, lambda: self.get_pos(2))
                elif hasattr(key,'char') and key.char:
                    if key.char.lower()=='a' and not self.running: self.root.after(0, self.start)
                    elif key.char.lower()=='s' and self.running: self.root.after(0, self.stop)
            except: pass
        keyboard.Listener(on_press=on_press, daemon=True).start()
        
    def start(self):
        if self.running: return
        try:
            p1 = (int(self.p1x.get()), int(self.p1y.get()))
            p2 = (int(self.p2x.get()), int(self.p2y.get()))
            rm, rx = float(self.round_min.get()), float(self.round_max.get())
            mm, mx = float(self.m_min.get()), float(self.m_max.get())
            amt = float(self.amount.get())
            radius = int(self.search_radius.get())
            if rm<0 or rx<0 or rm>rx or mm<=0 or mx<=0 or mm>mx or amt<=0 or radius<0: raise ValueError()
        except:
            messagebox.showerror("错误", "参数无效")
            return
        self.running, self.count = True, 0
        self.btn_start.config(state='disabled')
        self.btn_stop.config(state='normal')
        self.lbl_status.config(text="🟢 运行中")
        threading.Thread(target=self.loop, args=(p1,p2,rm,rx,mm,mx,amt,radius), daemon=True).start()
        
    def stop(self):
        self.running = False
        self.btn_start.config(state='normal')
        self.btn_stop.config(state='disabled')
        self.lbl_status.config(text="⏹ 已停止")
        
    def move(self, tx, ty, dur):
        path = human_path(*pyautogui.position(), tx, ty)
        dt = dur / len(path)
        for x, y in path:
            if not self.running: break
            pyautogui.moveTo(x, y, _pause=False)
            time.sleep(dt * random.uniform(0.5, 1.5))
        pyautogui.moveTo(tx, ty, _pause=False)
        
    def loop(self, p1, p2, rm, rx, mm, mx, amt, radius):
        while self.running:
            self.count += 1
            total = amt * 2 * self.count
            
            # 点位1
            tx, ty = p1
            if self.use_color.get() and self.color1:
                tx, ty = find_color_nearby(p1[0], p1[1], self.color1, radius)
            self.move(tx, ty, random.uniform(mm, mx))
            if self.running: pyautogui.click()
            
            # 点位2
            tx, ty = p2
            if self.use_color.get() and self.color2:
                tx, ty = find_color_nearby(p2[0], p2[1], self.color2, radius)
            self.move(tx, ty, random.uniform(mm, mx))
            if self.running: pyautogui.click()
            
            # 更新显示
            self.root.after(0, lambda c=self.count, t=total: self.update_display(c, t))
            
            # 轮次间隔
            e = 0
            d = random.uniform(rm, rx)
            while e < d and self.running: time.sleep(0.1); e += 0.1
    
    def update_display(self, count, total):
        self.lbl_count.config(text=f"次数：{count}")
        self.lbl_total.config(text=f"总额：{total:.1f} U")
        
    def quit(self):
        self.running = False
        self.root.destroy()
        sys.exit(0)
        
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    App().run()
