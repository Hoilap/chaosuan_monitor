# 通知功能配置指南

## 功能说明

监控程序现在支持三种通知方式：
1. **邮件通知** - 通过SMTP发送邮件到指定邮箱
2. **Server酱** - 通过微信接收推送消息
3. **钉钉机器人** - 通过钉钉群机器人接收消息

## 通知时机

程序会在以下情况发送通知：
1. ✅ 监控启动时
2. ⚠️ 检测到任务闲置即将关闭时
3. ✅ 任务成功关闭时
4. ❌ 任务关闭失败时
5. ❌ 监控数据获取失败时

## 配置方法

### 1. 邮件通知配置

在 `monitor.py` 中修改以下配置：

```python
ENABLE_EMAIL = True  # 启用邮件通知
SMTP_SERVER = "smtp.qq.com"  # SMTP服务器
SMTP_PORT = 465  # 端口
SENDER_EMAIL = "your_email@qq.com"  # 发件人邮箱
SENDER_PASSWORD = "your_auth_code"  # 授权码（不是登录密码！）
RECEIVER_EMAIL = "receiver@example.com"  # 收件人邮箱
```

#### 常用邮箱配置

**QQ邮箱:**
- SMTP服务器: `smtp.qq.com`
- 端口: `465`
- 获取授权码: QQ邮箱 → 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务 → 生成授权码

**163邮箱:**
- SMTP服务器: `smtp.163.com`
- 端口: `465`
- 获取授权码: 163邮箱 → 设置 → POP3/SMTP/IMAP → 客户端授权密码

**Gmail:**
- SMTP服务器: `smtp.gmail.com`
- 端口: `465`
- 需要开启"不太安全的应用访问权限"或使用应用专用密码

**Outlook/Hotmail:**
- SMTP服务器: `smtp-mail.outlook.com`
- 端口: `587`

### 2. Server酱(微信)配置

Server酱可以将通知推送到微信，非常方便。

```python
ENABLE_SERVERCHAN = True  # 启用Server酱
SERVERCHAN_KEY = "SCT123456ABCDEFG"  # 你的SendKey
```

**获取SendKey步骤:**
1. 访问 [https://sct.ftqq.com/](https://sct.ftqq.com/)
2. 使用微信扫码登录
3. 在"发送消息"页面找到你的SendKey
4. 将SendKey复制到配置中

### 3. 钉钉机器人配置

如果你使用钉钉办公，可以通过钉钉群机器人接收通知。

```python
ENABLE_DINGTALK = True  # 启用钉钉通知
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=xxxxx"
DINGTALK_SECRET = "SECxxxxxxxxxxxxxx"  # 可选，加签密钥
```

**获取钉钉机器人配置步骤:**
1. 在钉钉群中添加自定义机器人
2. 选择"自定义机器人"
3. 安全设置选择"加签"或"自定义关键词"
4. 复制Webhook地址和加签密钥（如果使用加签）

## 使用示例

### 示例1: 只使用邮件通知

```python
# 邮件配置
ENABLE_EMAIL = True
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SENDER_EMAIL = "myemail@qq.com"
SENDER_PASSWORD = "abcdefghijklmnop"  # QQ邮箱授权码
RECEIVER_EMAIL = "myemail@qq.com"  # 可以发给自己

# 其他通知方式关闭
ENABLE_SERVERCHAN = False
ENABLE_DINGTALK = False
```

### 示例2: 同时使用多种通知

```python
# 邮件 + 微信
ENABLE_EMAIL = True
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465
SENDER_EMAIL = "myemail@163.com"
SENDER_PASSWORD = "my_auth_code"
RECEIVER_EMAIL = "myemail@163.com"

ENABLE_SERVERCHAN = True
SERVERCHAN_KEY = "SCT123456ABCDEFG"

ENABLE_DINGTALK = False
```

### 示例3: 不使用任何通知

```python
ENABLE_EMAIL = False
ENABLE_SERVERCHAN = False
ENABLE_DINGTALK = False
```

程序会正常运行，只是不会发送通知。

## 测试通知

修改配置后，可以运行程序测试通知是否正常：

```bash
python monitor.py
```

程序启动后会立即发送一条"监控已启动"的通知，你可以检查是否收到。

## 故障排除

### 邮件发送失败

1. **检查是否使用授权码**: 大部分邮箱需要使用授权码而不是登录密码
2. **检查SMTP服务器和端口**: 确认配置正确
3. **检查网络**: 确保能访问SMTP服务器
4. **查看错误信息**: 程序会打印具体的错误信息

### Server酱推送失败

1. **检查SendKey**: 确保复制完整
2. **检查配额**: 免费版每天有推送次数限制
3. **微信关注"方糖"公众号**: 确保已关注才能收到推送

### 钉钉推送失败

1. **检查Webhook地址**: 确保完整复制
2. **检查安全设置**: 如果使用关键词，确保消息中包含关键词
3. **检查加签配置**: 如果使用加签，确保密钥正确

## 注意事项

1. **保护隐私**: 配置文件包含敏感信息，不要上传到公共代码仓库
2. **测试环境**: 建议先在测试环境验证通知功能
3. **避免频繁通知**: 合理设置检查间隔，避免过度通知
4. **多种方式备份**: 建议配置至少两种通知方式，防止单点失败

## 推荐配置

对于重要任务，推荐同时配置：
- **邮件**: 作为正式记录，可以查看历史
- **Server酱或钉钉**: 作为即时提醒，手机可以快速收到

这样既有正式记录，又能及时收到通知。
