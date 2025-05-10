import asyncio
import re
import tkinter as tk
from tkinter import scrolledtext

from app.agent.orchestrator import Orchestrator
from app.logger import logger


class ChatbotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Orchestrator Chatbot")

        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        self.create_widgets()
        self.agent = None
        self.initialize_agent()
        self.original_logger_id = None  # 存储原始logger处理器ID

    def create_widgets(self):
        self.chat_display = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, state="disabled", font=("Courier New", 11)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.user_input = tk.Entry(input_frame, font=("Arial", 12))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", self.on_enter_pressed)

        self.send_button = tk.Button(
            input_frame, text="Send", command=self.process_input, font=("Arial", 12)
        )
        self.send_button.pack(side=tk.RIGHT, padx=(10, 0))

        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 10),
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def initialize_agent(self):
        async def _initialize():
            try:
                self.status_var.set("Initializing agent...")
                self.agent = await Orchestrator.create()
                self.status_var.set("Ready")
                self.add_to_chat("System", "Agent initialized and ready to chat!")
            except Exception as e:
                self.status_var.set("Initialization failed")
                self.add_to_chat("System", f"Failed to initialize agent: {str(e)}")
                logger.error(f"Agent initialization failed: {e}")

        asyncio.create_task(_initialize())

    def add_to_chat(self, sender, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see(tk.END)

    def process_log_message(self, log_message):
        marker = "| INFO     | app.agent.toolcall:act:152 - "
        if marker in log_message:
            start = log_message.find(marker)
            end = log_message.find("\n", start)
            return log_message[start : end if end != -1 else None].strip()
        return None

    def process_tool_output1(self, log_message):
        """
        提取并返回工具输出内容（去掉前面的标记行）
        保留所有后续行（包括多行内容）
        """
        pattern = r"🎯 Tool '[^']+' completed its mission! Result: Observed output of cmd `[^`]+` executed:\s*(.*)"
        match = re.search(pattern, log_message, re.DOTALL)

        if match:
            return match.group(1).strip()
        return None

    def process_tool_output2(self, log_message):
        """
        提取并返回工具输出内容（去掉前面的标记行）
        保留所有后续行（包括多行内容）
        """
        pattern = r"✨ Orchestrator's thoughts:\s*(.*)"
        match = re.search(pattern, log_message, re.DOTALL)

        if match:
            return match.group(1).strip()
        return None

    def on_enter_pressed(self, event):
        self.process_input()

    def process_input(self):
        prompt = self.user_input.get().strip()
        if not prompt:
            return

        self.add_to_chat("You", prompt)
        self.user_input.delete(0, tk.END)

        async def _run_agent():
            try:
                self.status_var.set("Processing...")
                self.send_button.config(state=tk.DISABLED)

                # 添加自定义处理器并保存原始处理器ID
                self.original_logger_id = logger.add(
                    self.custom_logger_sink, level="INFO", format="{message}"
                )

                await self.agent.run(prompt)

                self.status_var.set("Ready")
                self.add_to_chat("System", "Request processing completed.")
            except Exception as e:
                self.status_var.set("Error occurred")
                self.add_to_chat("System", f"Error: {str(e)}")
                logger.error(f"Error processing request: {e}")
            finally:
                # 恢复原始logger配置
                if self.original_logger_id is not None:
                    logger.remove(self.original_logger_id)
                    self.original_logger_id = None
                self.send_button.config(state=tk.NORMAL)

        asyncio.create_task(_run_agent())

    def custom_logger_sink(self, message):
        """处理日志消息，只显示工具输出内容"""
        raw_message = message.record["message"]

        # 尝试提取工具输出
        tool_output1 = self.process_tool_output1(raw_message)
        tool_output2 = self.process_tool_output2(raw_message)
        if tool_output1:
            self.add_to_chat("Output", tool_output1)
            return
        elif tool_output2:
            self.add_to_chat("Think", tool_output2)
            return

    async def cleanup(self):
        if self.agent:
            await self.agent.cleanup()
        if self.original_logger_id is not None:
            logger.remove(self.original_logger_id)


async def main():
    root = tk.Tk()
    app = ChatbotUI(root)

    try:
        while True:
            root.update()
            await asyncio.sleep(0.05)
    except tk.TclError:
        pass
    finally:
        await app.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
