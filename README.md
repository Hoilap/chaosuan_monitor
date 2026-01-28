# SYSU 超算 GPU 自动监控与闲置释放工具

本项目用于监控超算平台（Starlight）https://starlight.nscc-gz.cn/ 的 GPU 任务。当显存占用持续低于阈值时，自动结束任务以节省费用，并通过钉钉机器人发送实时通知。

## 主要功能

* **自动监控**：定时检查 GPU 显存使用情况。
* **闲置判定**：连续 N 次显存低于阈值（例如 3MB）即视为闲置。
* **自动停止**：确认闲置后自动调用 API 停止任务。
* **消息通知**：支持钉钉机器人（推荐）、Server酱、邮件通知。

## 快速配置指南

一般来说，你只需要配置以下 **3 个** 部分即可运行程序。

### 1. 配置账号信息 (`private_config.py`)

在项目根目录下确保存在 `private_config.py` 文件（如果不存在请新建），并填入你的平台登录账号和密码：

```python
# private_config.py
username = "your_email@example.com"
password_plain = "your_password"
```

### 2. 配置任务信息 (`config.py`)

打开 `config.py` 文件，找到最上方的 `log` 变量。

**无需手动填写复杂的 Pod 名或节点名**，程序会自动化处理：

1. 在网页端的任务事件或日志中，找到包含 `Successfully assigned ... to ...` 的那一行日志。
2. 直接将整行文本复制过来，赋值给 `log` 变量。

程序会利用正则表达式自动解析出 `POD_NAME`、`NODE_NAME` 和 `JOB_ID`。

```python
# config.py 示例
log = "0001-01-01 00:00:00 +0000 UTC	Normal	Scheduled	Successfully assigned 13957/deeplearni-2903845-r8lcz to an35"
```

### 3. 配置钉钉通知 (`config.py`)

推荐使用钉钉群机器人进行状态通知。在 `config.py` 中找到 **钉钉机器人通知配置** 部分：

1. 确保 `ENABLE_DINGTALK = True`。
2. 填入机器人的 `Webhook` 链接。
3. 填入机器人的 `加签密钥 (Secret)`。

```python
# config.py
ENABLE_DINGTALK = True
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=xxxx..."
DINGTALK_SECRET = "SECxxxx..."
```

*(邮件和 Server酱通知默认关闭，如需使用可在 config.py 中自行配置)*

---

## 运行方法

1. 安装依赖库：

   ```bash
   pip install requests
   ```
2. 启动监控程序：

   ```bash
   python monitor.py
   ```

   或者直接双击运行目录下的 `run_monitor.bat` (Windows)。

## 监控参数说明 (config.py)

如果需要调整灵敏度，可修改 `config.py` 中的以下参数：

* `IDLE_THRESHOLD_MB`: **闲置阈值** (默认 3MB)，显存占用低于此值视为闲置。
* `MAX_IDLE_COUNT`: **关闭触发次数** (默认 1次)，连续检测到闲置达到此次数后触发自动关闭流程。
* `CHECK_INTERVAL`: **检查间隔** (默认 120秒)。
