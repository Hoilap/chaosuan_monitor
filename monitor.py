import time
import requests
from datetime import datetime, timedelta
from notifier import NotificationManager
from get_token import get_bihu_token
import config

# 全局 HEADERS，将在 main 中初始化和更新
HEADERS = {}

def update_headers(token):
    """更新全局 HEADERS"""
    global HEADERS
    HEADERS = {
        "bihu-token": token,
        "user-agent": config.USER_AGENT,
        "accept": "application/json, text/plain, */*"
    }

def get_current_gpu_memory():
    """从 API 获取最新的显存占用值"""
    # 动态生成最近一小时的时间范围（API要求）
    now = datetime.utcnow()
    start_time = (now - timedelta(minutes=60)).isoformat() + "Z"
    end_time = now.isoformat() + "Z"

    params = {
        "node_list": config.NODE_NAME,
        "pod_list": config.POD_NAME,
        "metric": "gpu_memory",
        "start": start_time,
        "end": end_time,
        "limit": "10", # 我们只需要最新的几个点
        "cluster_name": config.CLUSTER,
        "job_name": config.JOB_ID,
        "job_id": config.JOB_ID
    }

    try:
        response = requests.get(config.METRIC_URL, params=params, headers=HEADERS, timeout=15, verify=False)
        res_json = response.json()
        
        if res_json.get("code") != 200:
            print(f"API error: {res_json.get('info')}")
            return None

        # 解析 spec -> device -> data
        devices = res_json.get("spec", {}).get("device", [])
        if not devices:
            print(res_json)
            print("Can't find device data in response.")
            return None

        max_usage = 0
        for dev in devices:
            data_points = dev.get("data", [])
            if data_points:
                # 取最后一个数据点 [timestamp, value] 的 value
                latest_val = float(data_points[-1][1])
                max_usage = max(max_usage, latest_val)
        
        return max_usage
    
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL连接错误: {e}")
        # 如果遇到 SSL EOF，通常等待几秒重试可能有效
        return None 
    
    except Exception as e:
        print(f"Request data exception: {e}")
        return None

def get_job_status():
    """从 API 获取任务状态（spec.status）"""
    try:
        response = requests.get(config.JOB_STATUS_URL, headers=HEADERS, timeout=15, verify=False)
        res_json = response.json()

        if "code" in res_json and res_json.get("code") != 200:
            print(f"Job status API error: {res_json.get('info')}")
            return None

        status = res_json.get("spec", {}).get("status")
        if status is None:
            print("Can't find spec.status in response.")
            return None

        try:
            return int(status)
        except (TypeError, ValueError):
            print(f"Invalid status value: {status}")
            return None

    except requests.exceptions.SSLError as e:
        print(f"❌ SSL连接错误: {e}")
        return None

    except Exception as e:
        print(f"Request job status exception: {e}")
        return None
    

def stop_job():
    """Send DELETE request to stop the job"""
    print(f"\n[{datetime.now()}] !!! Triggering auto shutdown command !!!")
    try:
        res = requests.delete(config.DELETE_URL, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            print(">>> Platform confirmed job shutdown, billing stopped.")
            return True
        else:
            print(f">>> Shutdown failed: {res.status_code} {res.text}")
    except Exception as e:
        print(f">>> Command send exception: {e}")
    return False

def setup_notifications():
    """配置通知管理器"""
    notif_mgr = NotificationManager()
    
    # 添加邮件通知
    if config.ENABLE_EMAIL and config.SENDER_EMAIL and config.RECEIVER_EMAIL:
        notif_mgr.add_email_notifier(
            config.SMTP_SERVER, config.SMTP_PORT, 
            config.SENDER_EMAIL, config.SENDER_PASSWORD, 
            config.RECEIVER_EMAIL
        )
    
    # 添加Server酱通知
    if config.ENABLE_SERVERCHAN and config.SERVERCHAN_KEY:
        notif_mgr.add_serverchan_notifier(config.SERVERCHAN_KEY)
    
    # 添加钉钉通知
    if config.ENABLE_DINGTALK and config.DINGTALK_WEBHOOK:
        notif_mgr.add_dingtalk_notifier(config.DINGTALK_WEBHOOK, config.DINGTALK_SECRET or None)
    
    return notif_mgr

def send_notification(notif_mgr, title, message):
    """发送通知（如果配置了通知方式）"""
    if notif_mgr.notifiers:
        notif_mgr.send_all(title, message)

def connection_retry(notif_mgr):
    fail_counter = 1
    MAX_FAIL_COUNT = 2
    while True:
        print(f"Can't get data. Failure count: {fail_counter}/{MAX_FAIL_COUNT}")
        if fail_counter > MAX_FAIL_COUNT:
            print("Too many consecutive failures. Exiting.")
            send_notification(
                notif_mgr,
                "❌ GPU监控异常退出",
                f"任务ID: {config.JOB_ID}\n"
                f"原因: 连续获取数据失败超过 {MAX_FAIL_COUNT} 次\n"
                f"停止时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"请检查网络或Token有效性"
            )
            return -1

        print("Attempting to refresh token...")
        # 自动重新获取 Token 并重试
        try:
            token = get_bihu_token()
            update_headers(token)
            print("Token refreshed successfully.")
            return 0
        except Exception as e:
            print(f"Failed to refresh token: {e}")
            # 发送通知报告 Token 刷新失败
            send_notification(
                notif_mgr,
                "❌ get_bihu_token失败",
                f"任务ID: {config.JOB_ID}\n"
                f"错误: {str(e)}\n"
                f"监控程序仍在运行，将重试..."
            )
            fail_counter += 1
        # 继续循环，会先 sleep 再重试
        time.sleep(120)

def main():
    idle_counter = 0
    
    last_status = None
    print(f"Starting monitoring job: {config.JOB_ID}")
    print(f"Criteria: GPU memory < {config.IDLE_THRESHOLD_MB}MB for {config.MAX_IDLE_COUNT} consecutive checks")
    
    # 初始化 Token 和 Headers
    print("Initializing token...")
    token = get_bihu_token()
    update_headers(token)

    # 初始化通知管理器
    notif_mgr = setup_notifications()
    
    while True:
        status = get_job_status()
        if status is not None:
            if last_status == 0 and status == 2:  # 任务开始运行
                send_notification(
                    notif_mgr,
                    "✅ 作业排队完成，",
                    f"任务ID: {config.JOB_ID}\n"
                    f"节点: {config.NODE_NAME}\n"
                    f"Pod: {config.POD_NAME}\n"
                    f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                return
            elif last_status == None and status == 2: # 一开始就是运行中
                break
            elif last_status == None and status == 0:
                send_notification(
                    notif_mgr,
                    "✅ 作业正在排队",
                    f"任务ID: {config.JOB_ID}\n"
                    f"节点: {config.NODE_NAME}\n"
                    f"Pod: {config.POD_NAME}\n"
                    f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            last_status = status
            time.sleep(120)
        else:
            return_code = connection_retry(notif_mgr)
            if return_code == -1:
                break


    # 发送监控启动通知
    send_notification(
        notif_mgr,
        "🚀 GPU自动关闭监控已启动",
        f"任务ID: {config.JOB_ID}\n"
        f"节点: {config.NODE_NAME}\n"
        f"Pod: {config.POD_NAME}\n"
        f"闲置阈值: GPU显存 < {config.IDLE_THRESHOLD_MB}MB\n"
        f"触发条件: 连续闲置{config.MAX_IDLE_COUNT}次（约{config.MAX_IDLE_COUNT * config.CHECK_INTERVAL // 60}分钟）\n"
        f"检查间隔: {config.CHECK_INTERVAL}秒\n"
        f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    while True:
        usage = get_current_gpu_memory()
        if usage is not None:
            fail_counter = 0
            if usage < config.IDLE_THRESHOLD_MB:
                idle_counter += 1
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Status: Idle ({usage} MB) | Counter: {idle_counter}/{config.MAX_IDLE_COUNT}")
            else:
                if idle_counter > 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Status: Active ({usage} MB) | Counter reset to 0")
                idle_counter = 0
            
            if idle_counter == config.MAX_IDLE_COUNT:
                # 发送任务即将关闭通知
                send_notification(
                    notif_mgr,
                    "⚠️ GPU任务即将自动关闭",
                    f"任务ID: {config.JOB_ID}\n"
                    f"节点: {config.NODE_NAME}\n"
                    f"原因: GPU连续闲置{config.MAX_IDLE_COUNT}次\n"
                    f"当前显存: {usage} MB\n"
                    f"触发时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"2min后将会自动关闭任务，请及时检查bug"
                )
                time.sleep(120)
                
            elif idle_counter > config.MAX_IDLE_COUNT:
                if stop_job():
                    # 发送任务已关闭通知
                    send_notification(
                        notif_mgr,
                        "✅ GPU任务已成功关闭",
                        f"任务ID: {config.JOB_ID}\n"
                        f"节点: {config.NODE_NAME}\n"
                        f"Pod: {config.POD_NAME}\n"
                        f"关闭时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"计费已停止"
                    )
                    break
                else:
                    # 发送关闭失败通知
                    send_notification(
                        notif_mgr,
                        "❌ GPU任务关闭失败",
                        f"任务ID: {config.JOB_ID}\n"
                        f"失败时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"请手动检查并关闭任务"
                    )
        else:
            return_code = connection_retry(notif_mgr)
            if return_code == -1:
                break

            

        time.sleep(config.CHECK_INTERVAL)

if __name__ == "__main__":
    main()

