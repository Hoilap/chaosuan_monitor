import re

log = "0001-01-01 00:00:00 +0000 UTC	Normal	Scheduled	Successfully assigned 13957/deeplearni-2903845-r8lcz to an35"

# ==================== 配置区 ====================
# 1. 基础信息
CLUSTER = "k8s_xingyiAI"
# 使用正则表达式匹配
match = re.search(r"Successfully assigned .*/(\S+) to (\S+)", log)
if match:
    POD_NAME = match.group(1)
    NODE_NAME = match.group(2)
    # 提取 JOB_ID
    JOB_ID = POD_NAME.rpartition('-')[0]
else:
    # 默认值，防止未匹配时报错
    POD_NAME = ""
    NODE_NAME = ""
    JOB_ID = ""

# 2. 监控判定参数
IDLE_THRESHOLD_MB = 3  # 显存占用低于 3MB 认为闲置
MAX_IDLE_COUNT = 1      # 连续闲置次数达到该值则触发关闭
CHECK_INTERVAL = 120      # 检查间隔（秒）

# 3. API 地址
METRIC_URL = "https://starlight.nscc-gz.cn/api/monitor/metric"
DELETE_URL = f"https://starlight.nscc-gz.cn/api/job/running/{CLUSTER}/{JOB_ID}"

# 4. 通知配置（可选 - 留空则不发送通知）
# ============== 邮件通知配置 ==============
ENABLE_EMAIL = False
SMTP_SERVER = "smtp.qq.com"  # SMTP服务器
SMTP_PORT = 465  # SMTP端口
SENDER_EMAIL = ""  # 发件人邮箱
SENDER_PASSWORD = ""  # 邮箱密码或授权码
RECEIVER_EMAIL = ""  # 收件人邮箱

# ============== Server酱(微信)通知配置 ==============
ENABLE_SERVERCHAN = False
SERVERCHAN_KEY = ""  # Server酱SendKey

# ============== 钉钉机器人通知配置 ==============
ENABLE_DINGTALK = True
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=8462fe5ab6ae20d68a6bd0c49377fe5aa038c20684b1323e191d9124a28783d6"
DINGTALK_SECRET = "SEC3dfbc622eaad681399357a4d885ef1f8eb3ad590b1d2918d77ef25d673ba440b"

# User Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
