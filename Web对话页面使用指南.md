# 🌐 Web对话页面使用指南

## 📋 概述

已为您部署了Web对话测试页面，可以在没有小智硬件的情况下，直接通过浏览器与小智AI进行对话交互。

## 🚀 快速访问

### 方式1：直接访问测试页面（推荐）

```
http://10.73.194.94:8006/test_page.html
```

**特点**：
- ✅ 功能完整，支持文本和语音对话
- ✅ 实时WebSocket连接
- ✅ 支持音频录制和播放
- ✅ 设备配置管理

### 方式2：通过智控台访问

智控台地址：`http://10.73.194.94:8002`

## 🎯 功能说明

### 1. 设备配置

首次使用需要配置：

```
设备MAC: 任意MAC地址（如：AA:BB:CC:DD:EE:FF）
设备名称: Web测试设备
客户端ID: web_test_client
认证Token: 从智控台获取
```

**获取Token的步骤**：
1. 登录智控台：http://10.73.194.94:8002
2. 进入【设备管理】
3. 添加或查看设备
4. 复制设备的Token

### 2. 连接服务器

**WebSocket地址**（Python服务）：
```
ws://10.73.194.94:8000/xiaozhi/v1/
```

**OTA地址**（管理后端）：
```
http://10.73.194.94:8002/xiaozhi/ota/
```

点击【连接】按钮建立WebSocket连接。

### 3. 对话方式

#### 📝 文本对话
1. 在"文本消息"标签页
2. 输入框中输入问题
3. 点击【发送】或按Enter键
4. 等待AI回复

#### 🎤 语音对话
1. 切换到"语音消息"标签页
2. 点击【开始录音】
3. 说话（支持中文/英文）
4. 点击【停止录音】
5. 自动发送并接收AI语音回复

### 4. 高级功能

- **音频播放控制**：收到语音回复后可播放/暂停
- **消息历史**：自动保存对话记录
- **日志查看**：调试连接问题
- **设备状态**：实时显示连接状态

## 🔧 技术架构

```
浏览器 Web页面
    ↓ (WebSocket)
Python服务器 (xiaozhi-server:8000)
    ↓
Manager API (8002)
    ↓
MySQL + Redis
```

## 📊 服务状态检查

### 检查Python服务（xiaozhi-server）

```bash
# 查看服务状态
sudo docker ps | grep xiaozhi-esp32-server

# 查看日志
sudo docker logs xiaozhi-esp32-server --tail 50
```

**预期状态**：
- 容器应该在运行中（Up）
- WebSocket服务监听8000端口

### 检查Web服务（manager-web）

```bash
# 查看状态
sudo docker ps | grep xiaozhi-esp32-server-web

# 测试访问
curl -I http://localhost:8002
```

## 🐛 常见问题

### 1. WebSocket连接失败

**症状**：显示"ws未连接"

**解决方案**：
```bash
# 检查xiaozhi-server是否运行
sudo docker ps | grep xiaozhi-esp32-server

# 如果没运行，需要配置secret后启动
# 1. 登录智控台获取server.secret
# 2. 更新配置文件
# 3. 重启容器
```

### 2. 认证失败

**症状**：提示"认证失败"或"Token无效"

**解决方案**：
1. 登录智控台 http://10.73.194.94:8002
2. 进入【参数管理】
3. 找到`server.secret`并复制
4. 进入【设备管理】
5. 添加Web测试设备并获取Token
6. 在Web页面更新Token

### 3. 页面无法访问

**症状**：http://10.73.194.94:8006 打不开

**解决方案**：
```bash
# 重启测试页面服务
cd /home/moshu/xiaozhi-esp32-server/main/xiaozhi-server/test
python3 -m http.server 8006 &

# 检查服务
curl http://localhost:8006/test_page.html
```

### 4. 语音功能不工作

**症状**：无法录音或播放

**解决方案**：
- 检查浏览器麦克风权限
- 使用Chrome/Edge浏览器（推荐）
- 确保使用http://而非https://

## 🎨 页面功能截图说明

### 主要区域

1. **顶部状态栏**
   - OTA连接状态
   - WebSocket连接状态
   - 设备MAC地址

2. **设备配置区**
   - 可编辑设备信息
   - Token认证配置

3. **连接控制区**
   - WebSocket地址配置
   - 连接/断开按钮
   - 认证测试

4. **对话交互区**
   - 文本消息标签页
   - 语音消息标签页
   - 消息历史显示

5. **底部日志区**
   - 实时显示连接和消息日志
   - 便于调试

## 📖 使用流程

### 首次使用完整流程

1. **访问智控台**
   ```
   http://10.73.194.94:8002
   ```

2. **登录/注册账号**
   - 第一个注册的用户自动成为管理员

3. **配置server.secret**（如果xiaozhi-server未运行）
   - 进入【参数管理】
   - 复制`server.secret`
   - 执行配置脚本（如果有）

4. **添加Web测试设备**
   - 进入【设备管理】
   - 点击【添加设备】
   - 设备名称：Web测试设备
   - 客户端：web_test_client
   - 获取并复制Token

5. **配置AI模型**（可选）
   - 进入【模型配置】
   - 配置ASR、LLM、TTS模型
   - 填入您的API Keys

6. **访问Web对话页面**
   ```
   http://10.73.194.94:8006/test_page.html
   ```

7. **配置并连接**
   - 填入Token
   - 点击【连接】
   - 等待连接成功

8. **开始对话**
   - 文本输入或语音录制
   - 享受AI对话！

## 🔐 安全提示

- Token是敏感信息，不要泄露
- 生产环境建议使用HTTPS
- 定期更新Token
- 限制设备访问权限

## 📝 API接口说明

### WebSocket消息格式

**发送文本消息**：
```json
{
  "type": "text",
  "content": "你好，小智",
  "device_id": "web_test_client"
}
```

**发送语音消息**：
```json
{
  "type": "audio",
  "data": "base64_encoded_audio",
  "format": "opus"
}
```

### HTTP API

**设备认证**：
```
POST /xiaozhi/ota/auth
Headers: {
  "Authorization": "Bearer <token>"
}
```

**获取设备配置**：
```
GET /xiaozhi/ota/config?device_id=<device_id>
```

## 🎓 开发参考

如果您想自定义Web对话界面，可以参考：

- **测试页面源码**：`/home/moshu/xiaozhi-esp32-server/main/xiaozhi-server/test/test_page.html`
- **WebSocket通信**：`/home/moshu/xiaozhi-esp32-server/main/xiaozhi-server/core/websocket_server.py`
- **API文档**：http://10.73.194.94:8002/xiaozhi/doc.html

## 🌟 下一步

1. **配置AI模型**：让对话更智能
2. **自定义声音**：配置TTS音色
3. **添加技能**：配置智能体功能
4. **优化提示词**：提升对话质量

---

**当前状态**：
- ✅ 智控台：http://10.73.194.94:8002（已部署）
- ✅ Web对话页面：http://10.73.194.94:8006/test_page.html（已部署）
- ⏸️ Python服务：等待配置server.secret

**技术支持**：
- GitHub：https://github.com/xinnan-tech/xiaozhi-esp32-server
- 文档：项目docs目录

---

**最后更新**：2025-10-16

