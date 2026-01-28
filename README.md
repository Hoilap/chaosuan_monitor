# GPU任务监控程序

自动监控GPU任务的显存使用情况，当任务闲置时自动关闭，避免资源浪费。支持多种通知方式（邮件、微信、钉钉）实时提醒任务状态。

## 功能特性

- ✅ **自动监控**: 定时检查GPU显存使用情况
- ✅ **智能判断**: 根据阈值和连续次数判断是否闲置
- ✅ **自动关闭**: 检测到闲置后自动关闭任务，停止计费
- ✅ **多种通知**: 支持邮件、Server酱(微信)、钉钉机器人
- ✅ **实时提醒**: 任务启动、即将关闭、已关闭、异常等状态都会通知

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置监控参数

编辑 `monitor.py` 文件，修改以下配置：

```python
# 任务信息
CLUSTER = "k8s_xingyiAI"
JOB_ID = "deeplearni-22135328"
POD_NAME = "deeplearni-22135328-4wfm6"
NODE_NAME = "an42"

# 鉴权信息
BIHU_TOKEN = "your_token_here"

# 监控参数
IDLE_THRESHOLD_MB = 100  # 显存低于100MB认为闲置
MAX_IDLE_COUNT = 2       # 连续闲置2次则关闭
CHECK_INTERVAL = 120     # 每120秒检查一次
```

### 3. 配置通知方式（可选）

#### 邮件通知

```python
ENABLE_EMAIL = True
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SENDER_EMAIL = "your_email@qq.com"
SENDER_PASSWORD = "your_auth_code"  # 邮箱授权码
RECEIVER_EMAIL = "receiver@example.com"
```

#### Server酱(微信)

```python
ENABLE_SERVERCHAN = True
SERVERCHAN_KEY = "SCT123456ABCDEFG"  # 从 https://sct.ftqq.com/ 获取
```

#### 钉钉机器人

```python
ENABLE_DINGTALK = True
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=xxxxx"
DINGTALK_SECRET = "SECxxxxxxxxxxxxxx"
```

详细配置说明请查看 [通知功能配置指南](NOTIFICATION_GUIDE.md)

### 4. 测试通知配置

```bash
python test_notification.py
```

### 5. 启动监控

```bash
python monitor.py
```

或在Windows上双击 `run_monitor.bat`

## 通知消息示例

程序会在以下时机发送通知：

### 监控启动
```
🚀 GPU监控已启动

任务ID: deeplearni-22135328
节点: an42
Pod: deeplearni-22135328-4wfm6
闲置阈值: GPU显存 < 100MB
触发条件: 连续闲置2次（约4分钟）
检查间隔: 120秒
启动时间: 2026-01-22 10:30:00
```

### 任务即将关闭
```
⚠️ GPU任务即将自动关闭

任务ID: deeplearni-22135328
节点: an42
原因: GPU连续闲置2次
当前显存: 45 MB
触发时间: 2026-01-22 10:34:00
正在执行关闭操作...
```

### 任务已关闭
```
✅ GPU任务已成功关闭

任务ID: deeplearni-22135328
节点: an42
Pod: deeplearni-22135328-4wfm6
关闭时间: 2026-01-22 10:34:05
计费已停止
```

## 文件说明

- `monitor.py` - 主监控程序
- `notifier.py` - 通知模块（邮件、Server酱、钉钉）
- `test_notification.py` - 通知功能测试脚本
- `NOTIFICATION_GUIDE.md` - 详细的通知配置指南
- `run_monitor.bat` - Windows启动脚本

## 常见问题

### Q: 如何获取BIHU_TOKEN？
A: 在浏览器中登录平台，打开开发者工具(F12)，在网络请求的Headers中找到 `bihu-token` 字段。

### Q: 邮件发送失败怎么办？
A: 
1. 确认使用的是授权码而不是登录密码
2. 检查SMTP服务器和端口配置
3. 查看控制台的错误提示

### Q: Server酱推送失败？
A: 
1. 确认SendKey正确
2. 确保关注了"方糖"微信公众号
3. 检查是否超过每日推送限额

### Q: 如何关闭通知功能？
A: 将所有的 `ENABLE_*` 配置设为 `False`

### Q: 可以同时使用多种通知方式吗？
A: 可以！同时启用多种通知方式，程序会并发发送所有通知。

## 注意事项

1. **Token有效期**: BIHU_TOKEN有过期时间，失效后需要重新获取
2. **网络连接**: 确保能访问监控API和SMTP服务器
3. **隐私保护**: 配置文件包含敏感信息，不要上传到公共仓库
4. **合理配置**: 避免检查间隔过短导致频繁请求

## 更新日志

### v2.0 (2026-01-22)
- ✨ 新增邮件通知功能
- ✨ 新增Server酱(微信)通知功能
- ✨ 新增钉钉机器人通知功能
- ✨ 新增通知管理器，支持多种通知方式
- ✨ 新增通知测试脚本
- 📝 完善文档和配置指南

### v1.0
- ✅ 基础监控功能
- ✅ 自动关闭闲置任务

## 许可证

MIT License
