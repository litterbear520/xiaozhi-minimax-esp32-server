import os
import uuid
import queue
import base64
import traceback
import threading
from config.logger import setup_logging
from core.utils import opus_encoder_utils
from core.utils.tts import MarkdownCleaner
from core.providers.tts.base import TTSProviderBase
from core.providers.tts.dto.dto import SentenceType, ContentType, InterfaceType

# 导入 DashScope SDK
import dashscope
from dashscope.audio.qwen_tts_realtime import QwenTtsRealtime, QwenTtsRealtimeCallback, AudioFormat

TAG = __name__
logger = setup_logging()


class TTSProvider(TTSProviderBase):
    """
    通义千问3实时语音合成（Qwen3-TTS-VD-Realtime）
    使用官方 DashScope SDK
    """
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)

        self.interface_type = InterfaceType.DUAL_STREAM
        
        # 基础配置
        self.api_key = config.get("api_key")
        if not self.api_key:
            raise ValueError("api_key is required for Qwen3 TTS Realtime")

        # 设置 DashScope API Key
        dashscope.api_key = self.api_key

        # WebSocket配置
        self.ws_url = config.get("url", "wss://dashscope.aliyuncs.com/api-ws/v1/realtime")
        
        # 模型配置
        self.model = config.get("model", "qwen3-tts-vd-realtime-2026-01-15")
        
        # 音色配置
        if config.get("private_voice"):
            self.voice = config.get("private_voice")
        else:
            self.voice = config.get("voice", "myvoice")

        # 音频参数配置
        self.format = config.get("format", "pcm")
        sample_rate = config.get("sample_rate", "24000")
        self.sample_rate = int(sample_rate) if sample_rate else 24000

        # 模式配置
        self.mode = config.get("mode", "server_commit")

        # SDK 实例
        self.qwen_tts = None
        self.tts_callback = None
        
        # 创建Opus编码器
        self.opus_encoder = opus_encoder_utils.OpusEncoderUtils(
            sample_rate=self.sample_rate, channels=1, frame_size_ms=60
        )

    def tts_text_priority_thread(self):
        """流式TTS文本处理线程（使用 SDK）"""
        while not self.conn.stop_event.is_set():
            try:
                message = self.tts_text_queue.get(timeout=1)
                logger.bind(tag=TAG).debug(
                    f"收到TTS任务｜{message.sentence_type.name} ｜ {message.content_type.name} ｜ 内容: {message.content_detail[:50] if message.content_detail else 'None'}"
                )

                if message.sentence_type == SentenceType.FIRST:
                    self.conn.client_abort = False

                if self.conn.client_abort:
                    logger.bind(tag=TAG).info("收到打断信息，终止TTS文本处理线程")
                    continue

                if message.sentence_type == SentenceType.FIRST:
                    # 初始化会话
                    try:
                        if not getattr(self.conn, "sentence_id", None): 
                            self.conn.sentence_id = uuid.uuid4().hex
                            logger.bind(tag=TAG).info(f"自动生成新的 会话ID: {self.conn.sentence_id}")

                        logger.bind(tag=TAG).info("开始启动TTS会话...")
                        self.start_session_sync()
                        self.before_stop_play_files.clear()
                        logger.bind(tag=TAG).info("TTS会话启动成功")
                    except Exception as e:
                        logger.bind(tag=TAG).error(f"启动TTS会话失败: {str(e)}")
                        continue
                    
                    # FIRST 消息可能同时包含 TEXT 内容，这里不处理，等下一个消息
                    # 如果 FIRST 消息包含文本，继续处理
                    if message.content_type != ContentType.TEXT or not message.content_detail:
                        continue

                # 处理 TEXT 内容（包括 FIRST 消息中的文本和后续的 MIDDLE 消息）
                if ContentType.TEXT == message.content_type:
                    if message.content_detail:
                        try:
                            # 过滤 Markdown
                            filtered_text = MarkdownCleaner.clean_markdown(message.content_detail)
                            if filtered_text.strip():  # 只发送非空文本
                                logger.bind(tag=TAG).info(f"服务器发送语音段: {filtered_text}")
                                # 使用 SDK 发送文本
                                self.qwen_tts.append_text(filtered_text)
                        except Exception as e:
                            logger.bind(tag=TAG).error(f"发送TTS文本失败: {str(e)}")
                            continue
                    else:
                        logger.bind(tag=TAG).debug(f"收到空文本内容，跳过发送")

                elif ContentType.FILE == message.content_type:
                    logger.bind(tag=TAG).info(
                        f"添加音频文件到待播放列表: {message.content_file}"
                    )
                    if message.content_file and os.path.exists(message.content_file):
                        self._process_audio_file_stream(
                            message.content_file, 
                            callback=lambda audio_data: self.handle_audio_file(audio_data, message.content_detail)
                        )

                if message.sentence_type == SentenceType.LAST:
                    try:
                        logger.bind(tag=TAG).info("开始结束TTS会话...")
                        self.finish_session_sync()
                    except Exception as e:
                        logger.bind(tag=TAG).error(f"结束TTS会话失败: {str(e)}")
                        continue

            except queue.Empty:
                continue
            except Exception as e:
                logger.bind(tag=TAG).error(
                    f"处理TTS文本失败: {str(e)}, 类型: {type(e).__name__}, 堆栈: {traceback.format_exc()}"
                )
                continue

    def start_session_sync(self):
        """启动TTS会话（同步方法，使用 SDK）"""
        try:
            # 创建回调实例
            self.tts_callback = Qwen3TtsCallback(self)
            
            # 创建 SDK 实例
            self.qwen_tts = QwenTtsRealtime(
                model=self.model,
                callback=self.tts_callback,
                url=self.ws_url
            )
            
            # 连接
            self.qwen_tts.connect()
            logger.bind(tag=TAG).info("SDK 连接成功")
            
            # 配置会话
            response_format = AudioFormat.PCM_24000HZ_MONO_16BIT if self.sample_rate == 24000 else AudioFormat.PCM_16000HZ_MONO_16BIT
            self.qwen_tts.update_session(
                voice=self.voice,
                response_format=response_format,
                mode=self.mode
            )
            logger.bind(tag=TAG).info(f"会话配置成功: voice={self.voice}, mode={self.mode}")
            
        except Exception as e:
            logger.bind(tag=TAG).error(f"启动会话失败: {str(e)}")
            raise

    def finish_session_sync(self):
        """结束TTS会话（同步方法，使用 SDK）"""
        try:
            if self.qwen_tts:
                logger.bind(tag=TAG).info("触发语音合成...")
                self.qwen_tts.finish()
                
                # 等待完成
                if self.tts_callback:
                    self.tts_callback.wait_for_finished()
                
                # 打印性能指标
                session_id = self.qwen_tts.get_session_id()
                first_audio_delay = self.qwen_tts.get_first_audio_delay()
                metric_msg = f"[Metric] session_id={session_id}, first_audio_delay={first_audio_delay}ms"
                logger.bind(tag=TAG).info(metric_msg)
                
                # 发送指标到前端
                try:
                    import asyncio
                    import json
                    metric_data = {
                        "type": "metric",
                        "session_id": session_id,
                        "first_audio_delay": first_audio_delay,
                        "message": metric_msg
                    }
                    asyncio.run_coroutine_threadsafe(
                        self.conn.websocket.send(json.dumps(metric_data)),
                        self.conn.loop
                    )
                except Exception as e:
                    logger.bind(tag=TAG).debug(f"发送指标到前端失败: {str(e)}")
                    
                logger.bind(tag=TAG).info("会话结束成功")
        except Exception as e:
            logger.bind(tag=TAG).error(f"结束会话失败: {str(e)}")
            raise

    async def text_to_speak(self, text, output_file):
        """实现基类的抽象方法（但实际不使用，因为我们用 SDK）"""
        # 这个方法是为了满足基类的抽象方法要求
        # 实际的文本发送在 tts_text_priority_thread 中通过 SDK 的 append_text 完成
        pass

    def to_tts(self, text: str) -> list:
        """非流式生成音频数据，用于生成音频及测试场景"""
        try:
            audio_data = []
            
            # 创建临时回调
            class TempCallback(QwenTtsRealtimeCallback):
                def __init__(self, opus_encoder):
                    self.opus_encoder = opus_encoder
                    self.complete_event = threading.Event()
                    self.audio_list = []
                
                def on_open(self):
                    pass
                
                def on_close(self, close_status_code, close_msg):
                    pass
                
                def on_event(self, message: dict):
                    event_type = message.get('type', '')
                    if event_type == 'response.audio.delta':
                        audio_base64 = message.get('delta', '')
                        if audio_base64:
                            audio_bytes = base64.b64decode(audio_base64)
                            self.opus_encoder.encode_pcm_to_opus_stream(
                                audio_bytes,
                                end_of_stream=False,
                                callback=lambda opus: self.audio_list.append(opus)
                            )
                    elif event_type == 'session.finished':
                        self.complete_event.set()
                
                def wait_for_finished(self):
                    self.complete_event.wait()
            
            callback = TempCallback(self.opus_encoder)
            qwen_tts = QwenTtsRealtime(
                model=self.model,
                callback=callback,
                url=self.ws_url
            )
            
            qwen_tts.connect()
            response_format = AudioFormat.PCM_24000HZ_MONO_16BIT if self.sample_rate == 24000 else AudioFormat.PCM_16000HZ_MONO_16BIT
            qwen_tts.update_session(
                voice=self.voice,
                response_format=response_format,
                mode=self.mode
            )
            
            filtered_text = MarkdownCleaner.clean_markdown(text)
            qwen_tts.append_text(filtered_text)
            qwen_tts.finish()
            callback.wait_for_finished()
            
            return callback.audio_list

        except Exception as e:
            logger.bind(tag=TAG).error(f"生成音频数据失败: {str(e)}")
            return []


class Qwen3TtsCallback(QwenTtsRealtimeCallback):
    """TTS 回调类"""
    def __init__(self, tts_provider):
        self.tts_provider = tts_provider
        self.complete_event = threading.Event()
        self.first_audio_received = False  # 标记是否已收到第一个音频

    def on_open(self) -> None:
        logger.bind(tag=TAG).info("TTS 连接已建立")

    def on_close(self, close_status_code, close_msg) -> None:
        logger.bind(tag=TAG).info(f"TTS 连接关闭: code={close_status_code}, msg={close_msg}")

    def on_event(self, message: dict) -> None:
        try:
            event_type = message.get('type', '')
            
            if event_type == 'session.created':
                session_id = message.get("session", {}).get("id")
                logger.bind(tag=TAG).info(f"会话开始: {session_id}")
                # 发送 FIRST 消息（不带文本）
                self.tts_provider.tts_audio_queue.put((SentenceType.FIRST, [], None))
            
            elif event_type == 'response.created':
                # 任务已启动
                response_id = message.get("response", {}).get("id")
                logger.bind(tag=TAG).debug(f"响应任务已启动: {response_id}")
                
            elif event_type == 'response.audio.delta':
                # 接收音频数据并编码为 Opus
                audio_base64 = message.get('delta', '')
                if audio_base64:
                    audio_data = base64.b64decode(audio_base64)
                    
                    # 第一次收到音频时，发送文本到前端显示
                    if not self.first_audio_received:
                        self.first_audio_received = True
                        # 从 conn 获取缓存的文本
                        if hasattr(self.tts_provider.conn, 'tts_MessageText') and self.tts_provider.conn.tts_MessageText:
                            logger.bind(tag=TAG).debug(f"发送文本到前端: {self.tts_provider.conn.tts_MessageText}")
                            self.tts_provider.tts_audio_queue.put(
                                (SentenceType.FIRST, [], self.tts_provider.conn.tts_MessageText)
                            )
                            self.tts_provider.conn.tts_MessageText = None
                    
                    self.tts_provider.opus_encoder.encode_pcm_to_opus_stream(
                        audio_data, False, callback=self.tts_provider.handle_opus
                    )
                    
            elif event_type == 'response.done':
                logger.bind(tag=TAG).info("响应完成")
                
            elif event_type == 'session.finished':
                logger.bind(tag=TAG).info("会话结束")
                self.tts_provider._process_before_stop_play_files()
                self.complete_event.set()
                
            elif event_type == 'error':
                error_info = message.get("error", {})
                logger.bind(tag=TAG).error(f"TTS错误: {error_info}")
                
        except Exception as e:
            logger.bind(tag=TAG).error(f"处理回调事件异常: {e}")

    def wait_for_finished(self):
        """等待会话完成"""
        self.complete_event.wait()
