"""Bijou 桌面宠物 —— 透明悬浮 + 直接聊天 + 语音"""
import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
import logging
import threading
import time
import requests
import uuid
import io
import pyaudio
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(HERE, "static")
API = "http://127.0.0.1:8001"

logging.basicConfig(
    level=logging.INFO,
    format="[pet] %(asctime)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler(os.path.join(HERE, "pet.log"), encoding="utf-8"),
    ],
)
logger = logging.getLogger("pet")

IDLE_IMG = os.path.join(STATIC, "IMG_SEGMENT_20260520_005328.png")
TALK_IMG = os.path.join(STATIC, "IMG_SEGMENT_20260520_005345.png")

# 视频动画帧目录
IDLE_FRAMES_DIR = os.path.join(STATIC, "video_frames_idle")
TALK_FRAMES_DIR = os.path.join(STATIC, "video_frames_talk")
ANIM_FPS = 8  # 帧率
ANIM_INTERVAL = 1000 // ANIM_FPS  # 帧间隔 ms

MIC_IDLE_COLOR = "#2a2a3e"
MIC_REC_COLOR = "#cc3333"
REC_MAX_SECS = 10  # 最长录音秒数

# ─── 窗口监控（Win32 API） ───
import ctypes

def _get_active_window_info():
    """返回 (进程名, 窗口标题)，失败返回 ("", "")
    优先用 psutil 取进程名，不可用时从窗口标题提取。"""
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return "", ""
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value

        # 获取进程 ID
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

        # 尝试 psutil（快），不行则从窗口标题提取
        process = ""
        try:
            import psutil
            process = psutil.Process(pid.value).name()
            if process.lower().endswith('.exe'):
                process = process[:-4]
        except Exception:
            pass

        return process, title
    except Exception:
        return "", ""

def _guess_app_from_title(title: str) -> str:
    """从窗口标题猜测应用名，如 'main.py - VS Code' → 'VS Code'"""
    # 常见 IDE/编辑器模式：文件名 - 应用名
    for sep in (" - ", " — "):
        if sep in title:
            parts = title.rsplit(sep, 1)
            if len(parts) == 2 and len(parts[1]) < 40:
                return parts[1]
    return ""

# 常用进程名 → 中文名映射
_PROCESS_LABELS = {
    "code": "VS Code", "devenv": "Visual Studio",
    "chrome": "Chrome", "msedge": "Edge", "firefox": "Firefox",
    "wechat": "微信", "weixin": "微信", "qq": "QQ",
    "explorer": "文件管理器", "notepad": "记事本",
    "terminal": "终端", "windowsterminal": "终端", "wt": "终端",
    "cmd": "命令行", "powershell": "PowerShell",
    "word": "Word", "excel": "Excel", "powerpoint": "PowerPoint",
    "wps": "WPS", "typora": "Typora", "obsidian": "Obsidian",
    "steam": "Steam", "discord": "Discord",
    "feishu": "飞书", "dingtalk": "钉钉", "lark": "Lark",
    "spotify": "Spotify", "netease": "网易云音乐",
    "wsl": "WSL", "ubuntu": "Ubuntu",
}

# 活动分类（用于场景切换检测）
_WORK_APPS = {"code", "pycharm64", "devenv", "terminal", "windowsterminal", "wt",
              "cmd", "powershell", "word", "excel", "powerpoint", "wps",
              "feishu", "dingtalk", "lark", "notepad"}
_PLAY_APPS = {"steam", "discord", "spotify", "netease", "epicgameslauncher"}
_COMMS_APPS = {"wechat", "weixin", "qq", "wemeet", "zoom", "teams", "telegram"}
_BROWSER_APPS = {"chrome", "msedge", "firefox", "browser", "brave", "opera"}

def _classify_activity(process: str) -> str:
    """返回活动类别: work / play / comms / browser / other"""
    p = process.lower()
    if p in _WORK_APPS: return "work"
    if p in _PLAY_APPS: return "play"
    if p in _COMMS_APPS: return "comms"
    if p in _BROWSER_APPS: return "browser"
    return "other"

# 主动会话参数（随机化版本）
PROACTIVE_COOLDOWN_BASE = 80     # 基础冷却（秒），实际=base+random(0,30) ≈ 80~110s
PROACTIVE_CHECK_INTERVAL_MIN = 15
PROACTIVE_CHECK_INTERVAL_MAX = 25
SWITCH_TRIGGER_DELAY = 35        # 切换后最早可触发时间（秒）
SWITCH_TRIGGER_PROB = 0.80       # 切换触发概率（每轮检查）
LONG_STAY_TRIGGER = 360          # 长时间停留起始（秒，6分钟）
LONG_STAY_PROB = 0.65            # 长停留触发概率（每轮检查）
SCENE_CHANGE_DELAY = 25          # 场景切换后等待（秒）
SCENE_CHANGE_PROB = 0.85         # 场景切换触发概率（每轮检查）

PROACTIVE_MESSAGES = {
    "switch": "（你注意到用户切换到了{activity}，请以虞晚的身份自然地评论一句。不要提问，不超过30字，直接说出话语。）",
    "long_stay": "（你注意到用户已经{minutes}分钟在{activity}了，请以虞晚的身份关心一句。不要提问，不超过30字，直接说出话语。）",
    "scene_change": "（你注意到用户从{from_app}换到了{to_app}，请以虞晚的身份调侃一句。不要提问，不超过30字，直接说出话语。）",
}

# 对话活跃窗口参数
CONVERSATION_ACTIVE_WINDOW = 300  # 聊天窗口关闭后 5 分钟内视为对话活跃
MAX_HISTORY_ROUNDS = 10           # 保留最近 10 轮对话

CONVERSATION_CONTINUE_PROMPT = """## 对话状态
用户暂时没有回复，但对话还没结束。以下是最近的对话内容：

{history}

请根据上下文做出自然的反应——可以表达情绪、撒娇、或者带着宠溺催促一下。保持御姐人设，不要提问，不超过30字，直接说出话语。"""

def _format_activity(process, title):
    """把进程名和窗口标题格式化为自然语言"""
    if not process and not title:
        return ""
    label = _PROCESS_LABELS.get(process.lower(), process or _guess_app_from_title(title) or "未知应用")
    if title:
        return f"正在使用 {label}（窗口：{title}）"
    return f"正在使用 {label}"

WINDOW_W = 170
WINDOW_H = 450
IMG_W = 150
IMG_H = 285


class PetApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("yuwan")
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}+100+100")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        logger.info("宠物启动")

        self.bg = "#010101"
        self.root.configure(bg=self.bg)
        self.root.wm_attributes("-transparentcolor", self.bg)

        self.idle_img = ImageTk.PhotoImage(Image.open(IDLE_IMG).resize((IMG_W, IMG_H), Image.LANCZOS))
        self.talk_img = ImageTk.PhotoImage(Image.open(TALK_IMG).resize((IMG_W, IMG_H), Image.LANCZOS))

        # 加载视频动画帧
        self._idle_frames = []
        self._talk_frames = []
        self._anim_index = 0
        self._use_video_anim = False
        if os.path.isdir(IDLE_FRAMES_DIR) and os.path.isdir(TALK_FRAMES_DIR):
            import glob
            idle_files = sorted(glob.glob(os.path.join(IDLE_FRAMES_DIR, "frame_*.png")))
            talk_files = sorted(glob.glob(os.path.join(TALK_FRAMES_DIR, "frame_*.png")))
            if idle_files and talk_files:
                for fp in idle_files:
                    img = Image.open(fp).resize((IMG_W, IMG_H), Image.LANCZOS)
                    img = self._composite_onto_key(img)
                    self._idle_frames.append(ImageTk.PhotoImage(img))
                for fp in talk_files:
                    img = Image.open(fp).resize((IMG_W, IMG_H), Image.LANCZOS)
                    img = self._composite_onto_key(img)
                    self._talk_frames.append(ImageTk.PhotoImage(img))
                self._use_video_anim = True
                logger.info("加载动画帧: 待机 %d / 对话 %d", len(self._idle_frames), len(self._talk_frames))

        # 人物标签
        initial_img = self._idle_frames[0] if self._use_video_anim else self.idle_img
        self.label = tk.Label(self.root, image=initial_img, bg=self.bg, borderwidth=0)
        self.label.place(x=10, y=70)
        self.label.bind("<Button-1>", self.on_click)
        self.label.bind("<B1-Motion>", self.on_drag)

        # 气泡（AI 回复）—— 短则紧凑，长则滚动
        self.bubble_frame = tk.Frame(self.root, bg="#1e1e32", highlightthickness=0, borderwidth=0)
        self.bubble = tk.Text(
            self.bubble_frame,
            bg="#1e1e32", fg="#e0e0e0",
            font=("Microsoft YaHei", 8),
            wrap=tk.WORD,
            state=tk.DISABLED,
            cursor="hand2",
            borderwidth=0, highlightthickness=0,
            padx=5, pady=2,
            height=1, width=22,
        )
        self.bubble_scroll = tk.Scrollbar(
            self.bubble_frame, command=self.bubble.yview,
            width=6, bg="#2a2a3e", troughcolor="#0f0f1e",
        )
        self.bubble.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.bubble_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.bubble.configure(yscrollcommand=self.bubble_scroll.set)
        self.bubble.bind("<Button-1>", self.on_bubble_click)
        self.bubble.bind("<MouseWheel>", self._on_mousewheel)

        # 输入框
        self.input = tk.Entry(
            self.root, font=("Microsoft YaHei", 10),
            bg="#0f0f1e", fg="#e0e0e0", insertbackground="#e0e0e0",
            relief="flat", borderwidth=0,
        )
        self.input.bind("<Return>", self.send_msg)
        self.input.bind("<Escape>", lambda e: self.close_all())

        # 麦克风按钮（PTT：按住说话，松手识别+发送）
        self.mic_btn = tk.Label(
            self.root, text="语音", font=("Microsoft YaHei", 8),
            bg=MIC_IDLE_COLOR, fg="#cccccc",
            width=4, height=1, anchor="center",
        )
        self.mic_btn.bind("<ButtonPress-1>", self.start_record)
        self.mic_btn.bind("<ButtonRelease-1>", self.stop_record)

        # 状态
        self.busy = False
        self.chat_open = False
        self.session_id = ""
        self.last_reply = ""
        self.current_activity = ""
        self._float_offset = 0
        self._float_base_y = 70

        # 主动会话状态
        self._activity_start = 0.0
        self._activity_key = ""
        self._activity_category = ""
        self._prev_activity_key = ""
        self._prev_activity_category = ""
        self._commented_activities = set()
        self._last_proactive_time = 0.0
        self._chat_closed_time = 0.0
        self._conversation_history = []  # [(user_msg, ai_reply), ...]

        # 录音状态
        self.recording = False
        self._audio_frames = []
        self._audio_stream = None
        self._audio_p = None
        self._rec_stop_flag = False

        # 启动漂浮动画 + 窗口监控 + 主动循环 + 视频帧动画
        self._animate_float()
        if self._use_video_anim:
            self._animate_frame()
        threading.Thread(target=self._monitor_window, daemon=True).start()
        threading.Thread(target=self._proactive_loop, daemon=True).start()

        self.root.mainloop()

    def _monitor_window(self):
        """后台线程：每2秒检测活跃窗口变化，跳过宠物自身窗口。
        同类别内切换不重置计时器（如 PyCharm 切文件、Edge 切标签页）。"""
        while True:
            try:
                process, title = _get_active_window_info()
                # 跳过宠物自己的窗口，保留上一个真实活动
                if title == "yuwan" or "pet_tk" in (process or ""):
                    time.sleep(2)
                    continue
                if process or title:
                    current = f"{process}|{title}"
                    if current != getattr(self, '_last_window_id', ''):
                        new_category = _classify_activity(process)
                        old_category = getattr(self, '_activity_category', '')
                        now = time.time()
                        # 同类别内切换：保留活动开始时间和类别，只更新详情
                        if new_category == old_category and old_category:
                            self._last_window_id = current
                            self._activity_key = current
                            self._activity_category = new_category
                            self.current_activity = _format_activity(process, title)
                            # 不重置 _activity_start，不重置评论标记
                            continue
                        # 跨类别切换：记录旧活动、重置计时器
                        self._prev_activity_key = getattr(self, '_activity_key', '')
                        self._prev_activity_category = old_category
                        self._prev_activity_leave_time = now  # 记录离开旧类别的时间
                        self._last_window_id = current
                        self._activity_key = current
                        self._activity_start = now
                        self._activity_category = new_category
                        self.current_activity = _format_activity(process, title)
                        if self.current_activity:
                            logger.info("活动切换: %s (类别:%s→%s)",
                                       self.current_activity, old_category or "-", new_category)
                            self._commented_activities.discard(new_category)
            except Exception:
                pass
            time.sleep(2)

    def _composite_onto_key(self, img):
        """将 RGBA 的透明像素填充为透明色，不透明像素保持不变。无羽化，纯二值。"""
        if img.mode != "RGBA":
            return img.convert("RGB")
        bg_rgb = tuple(int(self.bg[i:i+2], 16) for i in (1, 3, 5))
        px = img.load()
        w, h = img.size
        for x in range(w):
            for y in range(h):
                r, g, b, a = px[x, y]
                if a < 128:
                    px[x, y] = bg_rgb + (255,)  # 透明区 → 填充透明色
                # else: 保持原色，alpha=255
        return img.convert("RGB")

    def _animate_float(self):
        """顺滑漂浮：高频 + 即时渲染"""
        import math
        self._float_offset += 0.008
        dy = math.sin(self._float_offset) * 4
        self.label.place_configure(y=self._float_base_y + int(round(dy)))
        self.root.update_idletasks()
        self.root.after(10, self._animate_float)

    def _animate_frame(self):
        """视频帧动画循环，待机和对话用不同帧组"""
        if self._use_video_anim:
            if self.chat_open and self._talk_frames:
                self._anim_index = (self._anim_index + 1) % len(self._talk_frames)
                self.label.configure(image=self._talk_frames[self._anim_index])
            elif not self.chat_open and self._idle_frames:
                self._anim_index = (self._anim_index + 1) % len(self._idle_frames)
                self.label.configure(image=self._idle_frames[self._anim_index])
        self.root.after(ANIM_INTERVAL, self._animate_frame)

    # ─── 主动会话 ───

    def _proactive_loop(self):
        """后台线程：随机间隔检查是否应该主动说话"""
        import random
        time.sleep(10)  # 启动后先等10秒
        while True:
            try:
                self._check_proactive(random)
            except Exception:
                logger.exception("主动循环异常")
            interval = random.uniform(PROACTIVE_CHECK_INTERVAL_MIN, PROACTIVE_CHECK_INTERVAL_MAX)
            time.sleep(interval)

    def _is_conversation_active(self) -> bool:
        """判断对话是否处于活跃期"""
        if self.chat_open:
            return True
        if self._chat_closed_time and time.time() - self._chat_closed_time < CONVERSATION_ACTIVE_WINDOW:
            return True
        return False

    def _check_proactive(self, random):
        """检查触发条件，概率触发 + 随机冷却，更自然"""
        if self.busy:
            return
        if not self.current_activity or not self._activity_key:
            return
        now = time.time()

        # 全局冷却（基础120s + 随机0~60s抖动）
        cooldown = PROACTIVE_COOLDOWN_BASE + random.uniform(0, 60)
        if now - self._last_proactive_time < cooldown:
            return
        # 不再按类别去重，只靠冷却控制频率

        duration = now - self._activity_start
        trigger_type = None
        prob = 0.0
        msg_kwargs = {"activity": self.current_activity}

        # 条件 c: 场景切换（work↔play）
        if self._prev_activity_category and self._activity_category:
            if (self._prev_activity_category in ("work", "play") and
                self._activity_category in ("work", "play") and
                self._prev_activity_category != self._activity_category and
                duration >= SCENE_CHANGE_DELAY):
                trigger_type = "scene_change"
                prob = SCENE_CHANGE_PROB
                old_label = _guess_app_from_title(self._prev_activity_key.split("|", 1)[1] if "|" in self._prev_activity_key else "") or self._prev_activity_category
                new_label = self.current_activity
                msg_kwargs = {"from_app": old_label, "to_app": new_label}

        # 条件 b: 长时间停留
        if not trigger_type and duration >= LONG_STAY_TRIGGER:
            trigger_type = "long_stay"
            prob = LONG_STAY_PROB
            msg_kwargs["minutes"] = int(duration // 60)

        # 条件 a: 切换应用（进入新活动60s后，在长停留之前）
        if not trigger_type and duration >= SWITCH_TRIGGER_DELAY and duration < LONG_STAY_TRIGGER:
            trigger_type = "switch"
            prob = SWITCH_TRIGGER_PROB

        if not trigger_type:
            return

        # 概率判定
        if random.random() > prob:
            logger.info("主动跳过 | type=%s | prob=%.0f%% | duration=%ds",
                       trigger_type, prob * 100, int(duration))
            return

        message = PROACTIVE_MESSAGES[trigger_type].format(**msg_kwargs)
        logger.info("主动触发 | type=%s | prob=%.0f%% | duration=%ds",
                   trigger_type, prob * 100, int(duration))
        threading.Thread(target=self._do_proactive_chat, args=(message,), daemon=True).start()

    def _do_proactive_chat(self, message):
        """发送主动对话请求"""
        try:
            if not self.session_id:
                self.session_id = uuid.uuid4().hex[:16]

            ctx = self.current_activity or ""
            logger.info("主动消息 | session=%s | msg=%s", self.session_id, message[:60])

            r = requests.post(f"{API}/api/chat/bijou", json={
                "session_id": self.session_id, "message": message, "context": ctx,
            }, timeout=60)
            reply = r.json().get("reply", "")
            self.last_reply = reply
            self._last_proactive_time = time.time()
            self._commented_activities.add(self._activity_category)  # 按类别去重

            logger.info("主动回复 | session=%s | reply=%s", self.session_id, reply[:60])

            # 显示气泡 + 自动消失
            self.root.after(0, lambda r=reply: self._show_proactive_bubble(r))
            self.play_tts(reply)

        except Exception:
            logger.exception("主动对话失败")

    def _show_proactive_bubble(self, text):
        """显示主动气泡，5秒后自动隐藏"""
        self._set_bubble_text(text)
        self.bubble_frame.place(x=5, y=2)
        # 30秒后自动隐藏
        self.root.after(30000, self._hide_proactive_bubble)

    def _hide_proactive_bubble(self):
        """隐藏主动气泡（如果聊天没开着）"""
        if not self.chat_open:
            self.bubble_frame.place_forget()

    # ─── 交互 ───

    def on_click(self, event):
        if self.busy:
            return
        if self.chat_open:
            self.close_all()
        else:
            self.open_chat()

    def on_bubble_click(self, event):
        """点气泡重新播放语音"""
        if self.last_reply:
            threading.Thread(target=self.play_tts, args=(self.last_reply,), daemon=True).start()

    def _set_bubble_text(self, text):
        self.bubble.configure(state=tk.NORMAL)
        self.bubble.delete("1.0", tk.END)
        self.bubble.insert("1.0", text)
        self.bubble.configure(state=tk.DISABLED)
        # 自适应高度：短回复紧凑，长回复最多 4 行 + 滚动条
        self.root.update_idletasks()
        try:
            result = self.bubble.count("1.0", "end", "displaylines")
            lines = result[0] if result and result[0] else max(1, len(text) // 15 + text.count('\n') + 1)
        except Exception:
            lines = max(1, len(text) // 15 + text.count('\n') + 1)
        height = max(1, min(lines, 4))
        self.bubble.configure(height=height)
        if lines > 4:
            self.bubble_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            self.bubble_scroll.pack_forget()

    def _on_mousewheel(self, event):
        self.bubble.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def on_drag(self, event):
        x = self.root.winfo_x() + event.x - WINDOW_W // 2
        y = self.root.winfo_y() + event.y - WINDOW_H // 2
        self.root.geometry(f"+{x}+{y}")

    # ─── 聊天 ───

    def open_chat(self):
        self.chat_open = True
        if self._use_video_anim and self._talk_frames:
            self.label.configure(image=self._talk_frames[self._anim_index % len(self._talk_frames)])
        else:
            self.label.configure(image=self.talk_img)
        self._set_bubble_text("嗯？")
        self.bubble_frame.place(x=5, y=2)
        self.input.place(x=5, y=365, width=130, height=28)
        self.mic_btn.place(x=138, y=365, width=32, height=28)
        self.input.focus_set()

    def close_all(self):
        self.chat_open = False
        self.bubble_frame.place_forget()
        self.input.place_forget()
        self.mic_btn.place_forget()
        if self._use_video_anim:
            self.label.configure(image=self._idle_frames[self._anim_index])
        else:
            self.label.configure(image=self.idle_img)

    def send_msg(self, event=None):
        text = self.input.get().strip()
        if not text or self.busy:
            return
        self.input.delete(0, "end")

        # 告别语 → 关闭宠物
        farewell = ["待会见", "再见", "拜拜", "晚安", "回头见", "下次见", "走了", "先这样", "bye", "goodbye"]
        if any(fw in text for fw in farewell):
            logger.info("告别触发关闭 | text=%s", text)
            self.busy = True
            self._set_bubble_text("好的，待会见~")
            self.bubble_frame.place(x=5, y=5)
            self.root.after(1500, self.root.destroy)
            return

        self.busy = True
        self._set_bubble_text("...")
        self.bubble_frame.place(x=5, y=2)
        threading.Thread(target=self._do_chat, args=(text,), daemon=True).start()

    # ─── 语音录制 ───

    def start_record(self, event=None):
        """按住开始录音"""
        if self.busy or self.recording:
            return
        self.recording = True
        self._rec_stop_flag = False
        self._audio_frames = []
        self.mic_btn.configure(bg=MIC_REC_COLOR, fg="#ffffff", text="录音中")
        logger.info("开始录音")
        threading.Thread(target=self._rec_thread, daemon=True).start()

    def _rec_thread(self):
        """录音线程"""
        try:
            p = pyaudio.PyAudio()
            self._audio_p = p
            self._audio_stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024,
            )
            started = time.time()
            while not self._rec_stop_flag:
                data = self._audio_stream.read(1024, exception_on_overflow=False)
                self._audio_frames.append(data)
                if time.time() - started > REC_MAX_SECS:
                    logger.info("录音达到最大时长 %ds", REC_MAX_SECS)
                    break
        except Exception as e:
            logger.error("录音异常 | %s", e)
        finally:
            self._cleanup_audio()

    def _cleanup_audio(self):
        try:
            if self._audio_stream:
                self._audio_stream.stop_stream()
                self._audio_stream.close()
                self._audio_stream = None
        except Exception:
            pass
        try:
            if self._audio_p:
                self._audio_p.terminate()
                self._audio_p = None
        except Exception:
            pass

    def stop_record(self, event=None):
        """松手停止录音，发送 ASR"""
        if not self.recording:
            return
        self.recording = False
        self._rec_stop_flag = True
        self.mic_btn.configure(bg=MIC_IDLE_COLOR, fg="#cccccc", text="语音")
        logger.info("停止录音 | frames=%d", len(self._audio_frames))

        if not self._audio_frames:
            logger.info("录音为空，跳过")
            return

        # 构建 WAV 并发送 ASR
        frames = self._audio_frames[:]
        threading.Thread(target=self._do_asr, args=(frames,), daemon=True).start()

    def _do_asr(self, frames):
        """将录音帧编码为 WAV，发送 ASR，拿到文本后自动发送聊天"""
        import io
        buf = io.BytesIO()
        wf = wave.open(buf, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"".join(frames))
        wf.close()
        wav_bytes = buf.getvalue()

        try:
            logger.info("ASR请求 | size=%d", len(wav_bytes))
            r = requests.post(f"{API}/api/chat/asr",
                              files={"file": ("rec.wav", wav_bytes, "audio/wav")},
                              timeout=300)
            if r.status_code == 200:
                text = r.json().get("text", "").strip()
                logger.info("ASR结果 | text=%s", text[:60])
                if text:
                    # 在主线程发送消息
                    self.root.after(0, lambda t=text: self._send_voice_text(t))
                else:
                    self.root.after(0, lambda: self._set_bubble_text("没听清，请再说一次"))
                    self.root.after(3000, self._hide_proactive_bubble)
            else:
                logger.warning("ASR返回非200 | status=%d | %s", r.status_code, r.text[:100])
                self.root.after(0, lambda: self._set_bubble_text("语音识别失败"))
                self.root.after(3000, self._hide_proactive_bubble)
        except Exception as e:
            logger.error("ASR请求异常 | %s", e)
            self.root.after(0, lambda: self._set_bubble_text("语音识别出错"))
            self.root.after(3000, self._hide_proactive_bubble)

    def _send_voice_text(self, text):
        """语音识别文本 → 自动发送聊天"""
        if not text or self.busy:
            return
        self.busy = True
        self._set_bubble_text("...")
        self.bubble_frame.place(x=5, y=2)
        threading.Thread(target=self._do_chat, args=(text,), daemon=True).start()

    def _do_chat(self, text):
        try:
            if not self.session_id:
                self.session_id = uuid.uuid4().hex[:16]

            ctx = self.current_activity or ""
            logger.info("发送消息 | session=%s | text=%s | ctx=%s",
                       self.session_id, text[:60], ctx[:40] if ctx else "-")

            # 对话
            r = requests.post(f"{API}/api/chat/bijou", json={
                "session_id": self.session_id, "message": text, "context": ctx,
            }, timeout=60)
            reply = r.json().get("reply", "……")
            self.last_reply = reply

            logger.info("收到回复 | session=%s | reply=%s", self.session_id, reply[:60])

            # 显示完整回复（气泡可滚动）
            self.root.after(0, lambda r=reply: self._set_bubble_text(r))
            self.play_tts(reply)

        except Exception as e:
            logger.error("对话失败 | %s", e)
            self.root.after(0, lambda msg=str(e): self._set_bubble_text(f"出错: {msg}"))
        finally:
            self.root.after(0, self._done)

    def _parse_tts_text(self, text):
        """提取括号内情绪指令，清洗正文。返回 (cleaned_text, instruction)"""
        import re
        instructions = re.findall(r"[（([{（]([^）)}\]）]*)[）)}\]]", text)
        clean = re.sub(r"[（([{（][^）)}\]）]*[）)}\]）]", "", text)
        clean = re.sub(r"\s+", "", clean)
        inst = "、".join(i for i in instructions if i.strip()) if instructions else "用温柔亲切的语气说话"
        return clean, inst

    def play_tts(self, text):
        try:
            clean, instruction = self._parse_tts_text(text)
            logger.info("TTS请求 | text=%s | inst=%s", clean[:50], instruction[:50])
            r = requests.post(f"{API}/api/chat/tts/bijou", json={
                "text": clean,
                "instruction": instruction
            }, timeout=120)
            if r.status_code == 200:
                self._play_wav(r.content)
                logger.info("TTS播放完成")
            else:
                logger.warning("TTS返回非200 | status=%d", r.status_code)
        except Exception:
            logger.exception("TTS播放异常")

    def _play_wav(self, data):
        try:
            wf = wave.open(io.BytesIO(data), 'rb')
            p = pyaudio.PyAudio()
            stream = p.open(
                format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
            )
            chunk = 1024
            d = wf.readframes(chunk)
            while d:
                stream.write(d)
                d = wf.readframes(chunk)
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception:
            logger.exception("音频播放异常")

    def _done(self):
        self.busy = False
        self._last_proactive_time = time.time()  # 手动聊天后重置冷却


if __name__ == "__main__":
    PetApp()
