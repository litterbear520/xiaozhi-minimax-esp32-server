#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通义千问3 TTS 音色创建工具
用于创建自定义音色并保存预览音频
"""

import requests
import base64
import os
import sys

def create_voice_and_save(
    api_key,
    voice_prompt,
    preview_text,
    preferred_name="myvoice",
    language="zh",
    sample_rate=24000,
    response_format="wav"
):
    """
    创建自定义音色并保存预览音频
    
    参数:
        api_key: 阿里云百炼API密钥
        voice_prompt: 音色描述（例如："沉稳的中年男性播音员，音色低沉浑厚"）
        preview_text: 预览文本
        preferred_name: 音色名称（用于后续TTS调用）
        language: 语言（zh/en）
        sample_rate: 采样率
        response_format: 音频格式
    
    返回:
        (voice_name, audio_filename) 或 (None, None)
    """
    
    if not api_key:
        print("错误: 未提供API Key")
        return None, None
    
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
            "voice_prompt": voice_prompt,
            "preview_text": preview_text,
            "preferred_name": preferred_name,
            "language": language
        },
        "parameters": {
            "sample_rate": sample_rate,
            "response_format": response_format
        }
    }
    
    # 北京地域URL
    url = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/customization"
    # 新加坡地域URL
    # url = "https://dashscope-intl.aliyuncs.com/api/v1/services/audio/tts/customization"
    
    try:
        print("正在创建音色...")
        print(f"音色描述: {voice_prompt}")
        print(f"预览文本: {preview_text}")
        print(f"音色名称: {preferred_name}")
        print()
        
        # 发送请求
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # 获取音色名称
            voice_name = result["output"]["voice"]
            print(f"✅ 音色创建成功!")
            print(f"音色名称: {voice_name}")
            print()
            
            # 获取预览音频数据
            base64_audio = result["output"]["preview_audio"]["data"]
            
            # 解码Base64音频数据
            audio_bytes = base64.b64decode(base64_audio)
            
            # 保存音频文件
            filename = f"{voice_name}_preview.{response_format}"
            with open(filename, 'wb') as f:
                f.write(audio_bytes)
            
            print(f"✅ 预览音频已保存")
            print(f"文件名: {filename}")
            print(f"文件路径: {os.path.abspath(filename)}")
            print(f"文件大小: {len(audio_bytes)} 字节")
            print()
            print("=" * 60)
            print("🎉 配置信息")
            print("=" * 60)
            print(f"请在TTS配置中使用以下音色名称:")
            print(f"voice: \"{voice_name}\"")
            print("=" * 60)
            
            return voice_name, filename
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None, None
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求发生错误: {e}")
        return None, None
    except KeyError as e:
        print(f"❌ 响应数据格式错误，缺少必要的字段: {e}")
        if 'response' in locals():
            print(f"响应内容: {response.text}")
        return None, None
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")
        return None, None


def main():
    """主函数"""
    print("=" * 60)
    print("通义千问3 TTS 音色创建工具")
    print("=" * 60)
    print()
    
    # 从环境变量或命令行参数获取API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    if not api_key:
        print("请提供API Key:")
        print("方式1: 设置环境变量 DASHSCOPE_API_KEY")
        print("方式2: 运行时传入参数 python create_qwen3_voice.py sk-xxx")
        print()
        api_key = input("请输入API Key: ").strip()
    
    if not api_key:
        print("❌ 未提供API Key，退出")
        return
    
    print()
    print("请输入音色信息:")
    print()
    
    # 音色描述
    voice_prompt = input("音色描述（例如：温柔的女性声音，语速适中）: ").strip()
    if not voice_prompt:
        voice_prompt = "温柔的女性声音，语速适中，音色清晰自然"
    
    # 预览文本
    preview_text = input("预览文本（例如：你好，我是小智）: ").strip()
    if not preview_text:
        preview_text = "你好，我是小智，很高兴为你服务"
    
    # 音色名称
    preferred_name = input("音色名称（例如：myvoice）: ").strip()
    if not preferred_name:
        preferred_name = "myvoice"
    
    print()
    
    # 创建音色
    voice_name, filename = create_voice_and_save(
        api_key=api_key,
        voice_prompt=voice_prompt,
        preview_text=preview_text,
        preferred_name=preferred_name
    )
    
    if voice_name:
        print()
        print("✅ 完成！你可以播放预览音频试听效果")
        print(f"然后在TTS配置中使用音色: {voice_name}")
    else:
        print()
        print("❌ 音色创建失败")


if __name__ == "__main__":
    main()
