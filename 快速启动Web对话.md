# 🚀 快速启动Web对话功能

## ✅ 当前状态

- ✅ **智控台**：正常运行（http://10.73.194.94:8002）
- ✅ **Web测试页面**：已部署（http://10.73.194.94:8006/test_page.html）
- ⏸️ **Python对话服务**：需要配置secret后才能启动

## 📝 完整操作步骤

### 步骤1：登录智控台获取Secret

1. **访问智控台**：
   ```
   http://10.73.194.94:8002
   ```

2. **登录账号**（如果还没注册，先注册第一个账号会自动成为管理员）

3. **进入参数管理**：
   - 左侧菜单点击【参数管理】
   - 找到`server.secret`参数
   - **复制这个值**（类似：95294d8c-f7b3-44ac-a336-6cf6c4b488a1）

### 步骤2：配置Secret

有两种方式：

#### 方式A：使用配置脚本（最简单）

```bash
cd /home/moshu/xiaozhi-esp32-server/main/xiaozhi-server/data

# 编辑.config.yaml文件
nano .config.yaml
```

在文件中添加（将YOUR_SECRET替换为刚才复制的值）：

```yaml
manager-api:
  url: http://xiaozhi-esp32-server-web:8003/xiaozhi/
  secret: YOUR_SECRET_HERE
```

保存后按`Ctrl+X`，然后按`Y`，最后按`Enter`。

#### 方式B：使用命令直接更新

```bash
cd /home/moshu/xiaozhi-esp32-server/main/xiaozhi-server/data

# 创建配置文件（替换YOUR_SECRET为实际值）
cat > .config.yaml << 'EOF'
manager-api:
  url: http://xiaozhi-esp32-server-web:8003/xiaozhi/
  secret: YOUR_SECRET_HERE
EOF
```

### 步骤3：重启Python服务

```bash
cd /home/moshu/xiaozhi-esp32-server/main/xiaozhi-server

# 重启容器
sudo docker compose -f docker-compose_all.yml restart xiaozhi-esp32-server

# 等待30秒让服务启动
sleep 30

# 查看日志确认成功
sudo docker logs xiaozhi-esp32-server --tail 20
```

**成功标志**：日志中看到：
```
Websocket地址是    ws://0.0.0.0:8000/xiaozhi/v1/
HTTP服务器启动在端口 8080
```

### 步骤4：添加Web测试设备

1. **进入设备管理**：
   - 智控台 → 左侧菜单【设备管理】

2. **添加设备**：
   - 点击【添加设备】按钮
   - 设备名称：`Web测试设备`
   - MAC地址：`AA:BB:CC:DD:EE:FF`（任意）
   - 客户端：`web_test_client`
   - 保存后获取Token

3. **复制Token**（用于Web页面认证）

### 步骤5：配置AI模型（可选但推荐）

在智控台【模型配置】中配置您想使用的模型：

**推荐免费组合**：
- **ASR**：FunASR（免费）
- **LLM**：使用您之前配置的MinimaxLLM
- **TTS**：EdgeTTS（免费）或您之前配置的MinimaxTTS

### 步骤6：使用Web对话页面

1. **访问页面**：
   ```
   http://10.73.194.94:8006/test_page.html
   ```

2. **配置设备信息**：
   - 点击【编辑】按钮
   - 填入设备MAC：`AA:BB:CC:DD:EE:FF`
   - 填入Token：（步骤4中获取的）
   - 客户端ID：`web_test_client`

3. **连接服务器**：
   - WebSocket地址保持默认：`ws://10.73.194.94:8000/xiaozhi/v1/`
   - 点击【连接】按钮
   - 等待显示"WS: 已连接"

4. **开始对话**：
   - 在文本框输入：`你好，小智`
   - 点击发送或按Enter
   - 等待AI回复

## 🎉 成功标志

1. **智控台状态**：
   - ✅ 可以正常登录
   - ✅ 可以看到设备列表
   - ✅ 模型配置正常

2. **Python服务状态**：
   ```bash
   $ sudo docker ps | grep xiaozhi-esp32-server
   # 应该显示 "Up X minutes" 而不是 "Restarting"
   ```

3. **Web页面状态**：
   - ✅ OTA: 已连接（绿色）
   - ✅ WS: 已连接（绿色）
   - ✅ 能够发送和接收消息

## 🐛 故障排除

### 问题1：Python服务一直Restarting

**原因**：secret未配置或配置错误

**解决**：
```bash
# 检查配置文件
cat /home/moshu/xiaozhi-esp32-server/main/xiaozhi-server/data/.config.yaml

# 查看错误日志
sudo docker logs xiaozhi-esp32-server --tail 50
```

### 问题2：WebSocket连接失败

**症状**：显示"ws未连接"

**解决**：
```bash
# 1. 确认Python服务已启动
sudo docker ps | grep xiaozhi-esp32-server

# 2. 检查8000端口
sudo netstat -tlnp | grep 8000

# 3. 查看防火墙
sudo ufw status
```

### 问题3：认证失败

**症状**：提示"Token无效"

**解决**：
1. 确认Token是从智控台最新获取的
2. 检查设备MAC地址是否匹配
3. 检查客户端ID是否正确

### 问题4：测试页面打不开

**解决**：
```bash
# 重启测试服务
pkill -f "python3 -m http.server 8006"
cd /home/moshu/xiaozhi-esp32-server/main/xiaozhi-server/test
python3 -m http.server 8006 > /tmp/web_test_server.log 2>&1 &

# 检查服务
curl -I http://localhost:8006/test_page.html
```

## 📖 快速命令参考

```bash
# 查看所有服务状态
sudo docker ps

# 重启Python服务
cd /home/moshu/xiaozhi-esp32-server/main/xiaozhi-server
sudo docker compose -f docker-compose_all.yml restart xiaozhi-esp32-server

# 查看Python服务日志
sudo docker logs xiaozhi-esp32-server --tail 50 -f

# 查看Web服务日志
sudo docker logs xiaozhi-esp32-server-web --tail 50

# 检查端口
sudo netstat -tlnp | grep -E "8000|8002|8006"
```

## 🎯 快捷访问链接

| 服务 | 地址 | 用途 |
|------|------|------|
| 智控台 | http://10.73.194.94:8002 | 系统管理 |
| Web对话 | http://10.73.194.94:8006/test_page.html | AI对话 |
| API文档 | http://10.73.194.94:8002/xiaozhi/doc.html | 接口文档 |

## 💡 使用技巧

1. **首次使用建议先用文本对话**测试连接
2. **配置好ASR和TTS后再用语音功能**
3. **在智控台的智能体配置**中可以自定义AI人设
4. **查看对话历史**可以在智控台的对话记录中看到

---

**需要帮助？**
- 详细文档：`/home/moshu/xiaozhi-esp32-server/Web对话页面使用指南.md`
- GitHub：https://github.com/xinnan-tech/xiaozhi-esp32-server

---

**最后更新**：2025-10-16
**当前进度**：✅ 智控台和Web页面已部署，⏸️ 等待配置secret启动Python服务


