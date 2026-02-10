# coding=utf-8
# Installation instructions for pyaudio:
# APPLE Mac OS X
#   brew install portaudio
#   pip install pyaudio
# Debian/Ubuntu
#   sudo apt-get install python-pyaudio python3-pyaudio
#   or
#   pip install pyaudio
# CentOS
#   sudo yum install -y portaudio portaudio-devel && pip install pyaudio
# Microsoft Windows
#   python -m pip install pyaudio

import pyaudio
import os
import base64
import threading
import time
import dashscope  # DashScope Python SDK 版本需要不低于1.23.9
from dashscope.audio.qwen_tts_realtime import QwenTtsRealtime, QwenTtsRealtimeCallback, AudioFormat

# ======= 常量配置 =======
TEXT_TO_SYNTHESIZE = [
    '对吧~我就特别喜欢这种超市，',
    '尤其是过年的时候',
    '去逛超市',
    '就会觉得',
    '超级超级开心！',
    '想买好多好多的东西呢！'
]

def init_dashscope_api_key():
    """
    初始化 dashscope SDK 的 API key
    """
    # 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
    # 若没有配置环境变量，请用百炼API Key将下行替换为：dashscope.api_key = "sk-xxx"
    dashscope.api_key = "sk-629275e7c8fe414e953cf5312160d07e"

# ======= 回调类 =======
class MyCallback(QwenTtsRealtimeCallback):
    """
    自定义 TTS 流式回调
    """
    def __init__(self):
        self.complete_event = threading.Event()
        self._player = pyaudio.PyAudio()
        self._stream = self._player.open(
            format=pyaudio.paInt16, channels=1, rate=24000, output=True
        )

    def on_open(self) -> None:
        print('[TTS] 连接已建立')

    def on_close(self, close_status_code, close_msg) -> None:
        self._stream.stop_stream()
        self._stream.close()
        self._player.terminate()
        print(f'[TTS] 连接关闭 code={close_status_code}, msg={close_msg}')

    def on_event(self, response: dict) -> None:
        try:
            event_type = response.get('type', '')
            if event_type == 'session.created':
                print(f'[TTS] 会话开始: {response["session"]["id"]}')
            elif event_type == 'response.audio.delta':
                audio_data = base64.b64decode(response['delta'])
                self._stream.write(audio_data)
            elif event_type == 'response.done':
                print(f'[TTS] 响应完成, Response ID: {qwen_tts_realtime.get_last_response_id()}')
            elif event_type == 'session.finished':
                print('[TTS] 会话结束')
                self.complete_event.set()
        except Exception as e:
            print(f'[Error] 处理回调事件异常: {e}')

    def wait_for_finished(self):
        self.complete_event.wait()

# ======= 主执行逻辑 =======
if __name__ == '__main__':
    init_dashscope_api_key()
    print('[系统] 初始化 Qwen TTS Realtime ...')

    callback = MyCallback()
    qwen_tts_realtime = QwenTtsRealtime(
        # 声音设计、语音合成要使用相同的模型
        model="qwen3-tts-vd-realtime-2026-01-15",
        callback=callback,
        # 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：wss://dashscope-intl.aliyuncs.com/api-ws/v1/realtime
        url='wss://dashscope.aliyuncs.com/api-ws/v1/realtime'
    )
    qwen_tts_realtime.connect()
    
    qwen_tts_realtime.update_session(
        voice="qwen-tts-vd-announcer-voice-20260210134905306-eb51", # 将voice参数替换为声音设计生成的专属音色
        response_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
        mode='server_commit'
    )

    for text_chunk in TEXT_TO_SYNTHESIZE:
        print(f'[发送文本]: {text_chunk}')
        qwen_tts_realtime.append_text(text_chunk)
        time.sleep(0.1)

    qwen_tts_realtime.finish()
    callback.wait_for_finished()

    print(f'[Metric] session_id={qwen_tts_realtime.get_session_id()}, '
          f'first_audio_delay={qwen_tts_realtime.get_first_audio_delay()}ms')