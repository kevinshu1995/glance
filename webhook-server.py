from flask import Flask, request
import subprocess
import threading
import os
import json
import hmac
import hashlib
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError
import logging

app = Flask(__name__)

# 日誌配置
log_dir = '/home/pie/glance/logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DEPLOY_SCRIPT = '/home/pie/glance/scripts/deploy.sh'
REPO_DIR = '/home/pie/glance'

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')
DEPLOY_BRANCH = os.getenv('DEPLOY_BRANCH', 'pi')


def verify_github_signature(payload: bytes, signature: str) -> bool:
    """驗證 GitHub webhook 的 HMAC-SHA256 簽名"""
    if not GITHUB_WEBHOOK_SECRET:
        logger.error("GITHUB_WEBHOOK_SECRET 環境變數未設定")
        return False
    expected = 'sha256=' + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def read_deploy_log(lines: int = 20) -> str:
    """讀取 deploy.log 的最後幾行"""
    try:
        with open(f'{log_dir}/deploy.log', 'r') as f:
            return ''.join(f.readlines()[-lines:])
    except FileNotFoundError:
        return '(deploy.log not found)'


def notify_telegram(message: str):
    """推送 Telegram 通知，失敗時僅記錄日誌不中斷流程"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.debug("Telegram 環境變數未設定，跳過通知")
        return

    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        payload = json.dumps({
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }).encode('utf-8')
        req = Request(url, data=payload, headers={'Content-Type': 'application/json'})
        urlopen(req, timeout=10)
    except (URLError, Exception) as e:
        logger.error(f"Telegram 通知失敗: {e}")

def run_deploy():
    """背景執行部署腳本，結果透過 Telegram 通知"""
    try:
        result = subprocess.run(
            [DEPLOY_SCRIPT],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            logger.info("✓ Deployment successful")
            notify_telegram(f'<b>[Pi Dashboard] [Deploy] 部署成功</b>\n<code>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</code>')
        else:
            output = result.stdout or result.stderr or '(no output)'
            deploy_log = read_deploy_log(20)
            logger.error(f"✗ Deployment failed (exit code {result.returncode}): {output}")
            notify_telegram(
                f'<b>[Pi Dashboard] [Deploy] 部署失敗</b>\n'
                f'<code>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | exit code: {result.returncode}</code>\n'
                f'<code>{deploy_log[-500:]}</code>'
            )

    except subprocess.TimeoutExpired:
        logger.error("Deployment timeout")
        notify_telegram(
            f'<b>[Pi Dashboard] [Deploy] 部署超時</b>\n'
            f'<code>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</code>\n'
            f'超過 5 分鐘未完成'
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        notify_telegram(
            f'<b>[Pi Dashboard] [Deploy] 部署錯誤</b>\n'
            f'<code>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</code>\n'
            f'<code>{str(e)}</code>'
        )


@app.route('/deploy', methods=['POST'])
def deploy():
    """觸發部署（由 GitHub webhook 觸發），馬上回傳 202，實際執行在背景"""
    # 驗證 GitHub 簽名
    signature = request.headers.get('X-Hub-Signature-256', '')
    if not verify_github_signature(request.get_data(), signature):
        logger.warning("Webhook 簽名驗證失敗")
        return {'status': 'error', 'message': 'Invalid signature'}, 401

    # 篩選 branch，只有推送到指定 branch 才觸發
    payload = request.get_json(silent=True) or {}
    ref = payload.get('ref', '')
    if ref != f'refs/heads/{DEPLOY_BRANCH}':
        logger.info(f"Skipped deploy: ref={ref}, target=refs/heads/{DEPLOY_BRANCH}")
        return {'status': 'skipped', 'message': f'Not target branch ({DEPLOY_BRANCH})'}, 200

    logger.info("=" * 50)
    logger.info("Deploy triggered")
    notify_telegram(f'<b>[Pi Dashboard] [Deploy] 部署觸發</b>\n<code>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</code>')

    # 背景執行，馬上回傳給 GitHub
    thread = threading.Thread(target=run_deploy, daemon=True)
    thread.start()

    return {'status': 'accepted', 'message': 'Deploy queued'}, 202

@app.route('/health', methods=['GET'])
def health():
    """健康檢查"""
    return {'status': 'ok'}, 200

@app.route('/status', methods=['GET'])
def status():
    """容器狀態"""
    try:
        result = subprocess.run(
            ['docker-compose', '-f', f'{REPO_DIR}/docker-compose.yml', 'ps'],
            capture_output=True,
            text=True,
            cwd=REPO_DIR
        )
        return {'status': 'ok', 'containers': result.stdout}, 200
    except:
        return {'status': 'error'}, 500

@app.route('/logs', methods=['GET'])
def get_logs():
    """獲取最近的部署日誌"""
    try:
        log_file = f'{log_dir}/deploy.log'
        with open(log_file, 'r') as f:
            logs = f.readlines()[-30:]
        return {'logs': logs}, 200
    except:
        return {'logs': []}, 200

if __name__ == '__main__':
    logger.info("Starting Webhook Server on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)