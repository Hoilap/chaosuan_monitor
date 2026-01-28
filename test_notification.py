"""
通知功能测试脚本
用于测试邮件、Server酱、钉钉等通知方式是否配置正确
"""

from notifier import NotificationManager
from datetime import datetime

# ==================== 测试配置 ====================
# 请根据需要修改以下配置进行测试

# 邮件配置
TEST_EMAIL = False  # 是否测试邮件
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SENDER_EMAIL = ""  # 填入你的发件邮箱
SENDER_PASSWORD = ""  # 填入授权码
RECEIVER_EMAIL = ""  # 填入收件邮箱

# Server酱配置
TEST_SERVERCHAN = False  # 是否测试Server酱
SERVERCHAN_KEY = ""  # 填入你的SendKey

# 钉钉配置
TEST_DINGTALK = False  # 是否测试钉钉
DINGTALK_WEBHOOK = ""  # 填入Webhook地址
DINGTALK_SECRET = ""  # 填入加签密钥（可选）

# ==================================================

def test_notifications():
    """测试所有配置的通知方式"""
    
    print("=" * 60)
    print("通知功能测试")
    print("=" * 60)
    
    # 创建通知管理器
    notif_mgr = NotificationManager()
    
    # 添加邮件通知
    if TEST_EMAIL:
        if not SENDER_EMAIL or not RECEIVER_EMAIL:
            print("⚠️ 邮件配置不完整，跳过邮件测试")
        else:
            print(f"✓ 添加邮件通知: {SENDER_EMAIL} -> {RECEIVER_EMAIL}")
            notif_mgr.add_email_notifier(
                SMTP_SERVER, SMTP_PORT,
                SENDER_EMAIL, SENDER_PASSWORD,
                RECEIVER_EMAIL
            )
    
    # 添加Server酱通知
    if TEST_SERVERCHAN:
        if not SERVERCHAN_KEY:
            print("⚠️ Server酱配置不完整，跳过Server酱测试")
        else:
            print(f"✓ 添加Server酱通知")
            notif_mgr.add_serverchan_notifier(SERVERCHAN_KEY)
    
    # 添加钉钉通知
    if TEST_DINGTALK:
        if not DINGTALK_WEBHOOK:
            print("⚠️ 钉钉配置不完整，跳过钉钉测试")
        else:
            print(f"✓ 添加钉钉通知")
            notif_mgr.add_dingtalk_notifier(DINGTALK_WEBHOOK, DINGTALK_SECRET or None)
    
    # 检查是否有通知方式
    if not notif_mgr.notifiers:
        print("\n❌ 没有配置任何通知方式！")
        print("请修改脚本顶部的配置，将需要测试的通知方式设为 True，并填入相关信息")
        return
    
    print(f"\n共配置了 {len(notif_mgr.notifiers)} 种通知方式")
    print("-" * 60)
    
    # 发送测试通知
    test_title = "🧪 GPU监控通知测试"
    test_message = f"""这是一条测试消息
    
测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
测试内容: GPU任务监控通知功能测试

如果你收到这条消息，说明通知配置成功！✅

接下来你可以：
1. 在 monitor.py 中启用相应的通知方式
2. 填写相同的配置信息
3. 运行监控程序，开始接收实际的任务通知

---
发送者: GPU监控程序
"""
    
    print("\n开始发送测试通知...")
    notif_mgr.send_all(test_title, test_message)
    
    print("\n" + "=" * 60)
    print("测试完成！请检查是否收到通知。")
    print("=" * 60)

def test_individual():
    """单独测试某个通知方式（用于调试）"""
    
    print("\n单独通知测试模式")
    print("请选择要测试的通知方式：")
    print("1. 邮件")
    print("2. Server酱")
    print("3. 钉钉")
    
    choice = input("请输入选项 (1/2/3): ").strip()
    
    if choice == "1":
        if not SENDER_EMAIL or not RECEIVER_EMAIL:
            print("❌ 请先配置邮件相关信息")
            return
        
        from notifier import EmailNotifier
        notifier = EmailNotifier(SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL)
        result = notifier.send("测试邮件", f"这是一封测试邮件\n发送时间: {datetime.now()}")
        print(f"\n结果: {'成功 ✅' if result else '失败 ❌'}")
        
    elif choice == "2":
        if not SERVERCHAN_KEY:
            print("❌ 请先配置Server酱SendKey")
            return
        
        from notifier import ServerChanNotifier
        notifier = ServerChanNotifier(SERVERCHAN_KEY)
        result = notifier.send("测试通知", f"这是一条测试通知\n发送时间: {datetime.now()}")
        print(f"\n结果: {'成功 ✅' if result else '失败 ❌'}")
        
    elif choice == "3":
        if not DINGTALK_WEBHOOK:
            print("❌ 请先配置钉钉Webhook地址")
            return
        
        from notifier import DingTalkNotifier
        notifier = DingTalkNotifier(DINGTALK_WEBHOOK, DINGTALK_SECRET or None)
        result = notifier.send("测试通知", f"这是一条测试通知\n发送时间: {datetime.now()}")
        print(f"\n结果: {'成功 ✅' if result else '失败 ❌'}")
        
    else:
        print("❌ 无效选项")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--single":
        test_individual()
    else:
        test_notifications()
        
    print("\n提示:")
    print("  - 运行 'python test_notification.py' 测试所有配置的通知方式")
    print("  - 运行 'python test_notification.py --single' 单独测试某个通知方式")
