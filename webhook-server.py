from flask import Flask, request
import subprocess
import os
from datetime import datetime
import logging

app = Flask(__name__)

# 日誌配置
log_dir = '/var/log/glance'
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

DEPLOY_SCRIPT = '/home/pi/glance/scripts/deploy.sh'
REPO_DIR = '/home/pi/glance'

@app.route('/deploy', methods=['POST'])
def deploy():
    """觸發部署"""
    try:
        logger.info("=" * 50)
        logger.info("Deploy triggered")
        
        # 執行部署腳本
        result = subprocess.run(
            [DEPLOY_SCRIPT],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            logger.info("✓ Deployment successful")
            return {
                'status': 'success',
                'message': 'Deployment completed',
            }, 200
        else:
            logger.error(f"✗ Deployment failed: {result.stderr}")
            return {
                'status': 'error',
                'message': 'Deployment failed',
                'error': result.stderr
            }, 500
    
    except subprocess.TimeoutExpired:
        logger.error("Deployment timeout")
        return {
            'status': 'error',
            'message': 'Deployment timeout (>5 minutes)'
        }, 500
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }, 500

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