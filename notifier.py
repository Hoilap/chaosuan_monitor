"""
通知模块 - 支持邮件和手机提醒
"""
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class EmailNotifier:
    """邮件通知器"""
    
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password, receiver_email):
        """
        初始化邮件通知器
        
        Args:
            smtp_server: SMTP服务器地址 (例如: smtp.qq.com, smtp.163.com, smtp.gmail.com)
            smtp_port: SMTP端口 (通常: 465-SSL, 587-TLS)
            sender_email: 发件人邮箱
            sender_password: 发件人密码或授权码
            receiver_email: 收件人邮箱
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.receiver_email = receiver_email
    
    def send(self, subject, message):
        """
        发送邮件
        
        Args:
            subject: 邮件主题
            message: 邮件内容
        
        Returns:
            bool: 是否发送成功
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.receiver_email
            msg['Subject'] = subject
            
            # 添加邮件正文
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            # 连接SMTP服务器并发送
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 邮件发送成功: {self.receiver_email}")
            return True
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 邮件发送失败: {e}")
            return False


class ServerChanNotifier:
    """Server酱通知器 - 微信推送"""
    
    def __init__(self, send_key):
        """
        初始化Server酱通知器
        
        Args:
            send_key: Server酱的SendKey (从 https://sct.ftqq.com/ 获取)
        """
        self.send_key = send_key
        self.api_url = f"https://sctapi.ftqq.com/{send_key}.send"
    
    def send(self, title, content):
        """
        发送微信通知
        
        Args:
            title: 通知标题
            content: 通知内容
        
        Returns:
            bool: 是否发送成功
        """
        try:
            data = {
                "title": title,
                "desp": content
            }
            response = requests.post(self.api_url, data=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Server酱推送成功")
                return True
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Server酱推送失败: {result.get('message')}")
                return False
                
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Server酱推送异常: {e}")
            return False


class DingTalkNotifier:
    """钉钉机器人通知器"""
    
    def __init__(self, webhook_url, secret=None):
        """
        初始化钉钉机器人通知器
        
        Args:
            webhook_url: 钉钉机器人webhook地址
            secret: 加签密钥（可选）
        """
        self.webhook_url = webhook_url
        self.secret = secret
    
    def send(self, title, content):
        """
        发送钉钉消息
        
        Args:
            title: 消息标题
            content: 消息内容
        
        Returns:
            bool: 是否发送成功
        """
        try:
            # 如果有加签，需要计算签名
            url = self.webhook_url
            if self.secret:
                import time
                import hmac
                import hashlib
                import base64
                import urllib.parse
                
                timestamp = str(round(time.time() * 1000))
                secret_enc = self.secret.encode('utf-8')
                string_to_sign = '{}\n{}'.format(timestamp, self.secret)
                string_to_sign_enc = string_to_sign.encode('utf-8')
                hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
                sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
                url = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"
            
            # 构建消息内容
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": f"### {title}\n\n{content}"
                }
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get("errcode") == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 钉钉消息发送成功")
                return True
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 钉钉消息发送失败: {result.get('errmsg')}")
                return False
                
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 钉钉消息发送异常: {e}")
            return False


class NotificationManager:
    """通知管理器 - 统一管理多种通知方式"""
    
    def __init__(self):
        self.notifiers = []
    
    def add_email_notifier(self, smtp_server, smtp_port, sender_email, sender_password, receiver_email):
        """添加邮件通知"""
        notifier = EmailNotifier(smtp_server, smtp_port, sender_email, sender_password, receiver_email)
        self.notifiers.append(('邮件', notifier))
        return self
    
    def add_serverchan_notifier(self, send_key):
        """添加Server酱通知"""
        notifier = ServerChanNotifier(send_key)
        self.notifiers.append(('Server酱', notifier))
        return self
    
    def add_dingtalk_notifier(self, webhook_url, secret=None):
        """添加钉钉通知"""
        notifier = DingTalkNotifier(webhook_url, secret)
        self.notifiers.append(('钉钉', notifier))
        return self
    
    def send_all(self, title, message):
        """
        通过所有配置的通知方式发送消息
        
        Args:
            title: 消息标题
            message: 消息内容
        """
        if not self.notifiers:
            print("⚠️ 未配置任何通知方式")
            return
        
        print(f"\n📢 开始发送通知: {title}")
        for name, notifier in self.notifiers:
            notifier.send(title, message)
