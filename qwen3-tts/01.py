import requests
import base64
import os

def create_voice_and_play():
    # 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key = "sk-xxx"
    api_key = "sk-629275e7c8fe414e953cf5312160d07e"
    
    if not api_key:
        print("错误: 未找到DASHSCOPE_API_KEY环境变量，请先设置API Key")
        return None, None, None
    
    # 准备请求数据
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "qwen-voice-design",
        "input": {
            "action": "create",
            "target_model": "qwen3-tts-vd-realtime-2026-01-15",
            "voice_prompt": "沉稳的中年男性播音员，音色低沉浑厚，富有磁性，语速平稳，吐字清晰，适合用于新闻播报或纪录片解说。",
            "preview_text": "各位听众朋友，大家好，欢迎收听晚间新闻。",
            "preferred_name": "announcer",
            "language": "zh"
        },
        "parameters": {
            "sample_rate": 24000,
            "response_format": "wav"
        }
    }
    
    # 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：https://dashscope-intl.aliyuncs.com/api/v1/services/audio/tts/customization
    url = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/customization"
    
    try:
        # 发送请求
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=60  # 添加超时设置
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # 获取音色名称
            voice_name = result["output"]["voice"]
            print(f"音色名称: {voice_name}")
            
            # 获取预览音频数据
            base64_audio = result["output"]["preview_audio"]["data"]
            
            # 解码Base64音频数据
            audio_bytes = base64.b64decode(base64_audio)
            
            # 保存音频文件到本地
            filename = f"{voice_name}_preview.wav"
            
            # 将音频数据写入本地文件
            with open(filename, 'wb') as f:
                f.write(audio_bytes)
            
            print(f"音频已保存到本地文件: {filename}")
            print(f"文件路径: {os.path.abspath(filename)}")
            
            return voice_name, audio_bytes, filename
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None, None, None
            
    except requests.exceptions.RequestException as e:
        print(f"网络请求发生错误: {e}")
        return None, None, None
    except KeyError as e:
        print(f"响应数据格式错误，缺少必要的字段: {e}")
        print(f"响应内容: {response.text if 'response' in locals() else 'No response'}")
        return None, None, None
    except Exception as e:
        print(f"发生未知错误: {e}")
        return None, None, None

if __name__ == "__main__":
    print("开始创建语音...")
    voice_name, audio_data, saved_filename = create_voice_and_play()
    
    if voice_name:
        print(f"\n成功创建音色 '{voice_name}'")
        print(f"音频文件已保存: '{saved_filename}'")
        print(f"文件大小: {os.path.getsize(saved_filename)} 字节")
    else:
        print("\n音色创建失败")