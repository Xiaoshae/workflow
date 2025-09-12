import os
import sys
from loguru import logger
from datetime import datetime

# 将当前脚本的目录添加到 Python 模块搜索路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import config
from acme_client import AcmeClient
from aliyun_dns import AliyunDNSManager
from send_email import send_email_with_attachments

LOG_FILE = "main_run.log"

def _initialize_config(config, logger):
    """
    初始化和验证配置，并设置默认值。

    如果基本配置有效，则返回 True，否则返回 False。
    """
    # 检查基本云服务商配置
    required_aliyun_keys = ['ALIYUN_ACCESS_KEY_ID', 'ALIYUN_ACCESS_KEY_SECRET', 'ALIYUN_DNS_ENDPOINT']
    if not all(hasattr(config, key) and getattr(config, key) for key in required_aliyun_keys):
        logger.error("阿里云配置不完整, 请在 config.py 中配置 ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET, ALIYUN_DNS_ENDPOINT。")
        return False

    # 检查域名配置
    if not getattr(config, 'DOMAINS', []):
        logger.error("域名列表不能为空, 请在 config.py 中配置 DOMAINS。")
        return False
    
    # 检查 ACME 联系邮箱
    if not getattr(config, 'ACME_CONTACT_EMAIL', None):
        logger.error("ACME 联系邮箱不能为空, 请在 config.py 中配置 ACME_CONTACT_EMAIL。")
        return False
    
    # 设置 ACME 目录 URL 的默认值
    if not getattr(config, 'ACME_DIRECTORY_URL', None):
        config.ACME_DIRECTORY_URL = "https://acme-staging-v02.api.letsencrypt.org/directory"
        logger.info(f"ACME_DIRECTORY_URL 未配置，使用默认值: {config.ACME_DIRECTORY_URL}")

    # 设置密钥和证书的默认路径和文件名
    if not hasattr(config, 'ACCOUNT_KEY_NAME'):
        config.ACCOUNT_KEY_NAME = "account.key"

    if not hasattr(config, 'KEY_PATH'):
        config.KEY_PATH = "./keys"
    
    if not hasattr(config, 'CERT_PATH'):
        config.CERT_PATH = "./certs"
    
    # 根据域名自动生成证书相关文件名
    domain = config.DOMAINS[0]
    base_name = domain[2:] if domain.startswith("*.") else domain
    
    if getattr(config, 'CERT_KEY_NAME', None) is None:
        config.CERT_KEY_NAME = f"{base_name}.key"

    if getattr(config, 'CERT_NAME', None) is None:
        config.CERT_NAME = f"{base_name}.crt"

    if getattr(config, 'CERT_CHAIN_NAME', None) is None:
        config.CERT_CHAIN_NAME = f"{base_name}-chain.crt"

    # 构造并存储完整的密钥和证书文件路径
    config.account_key_path = os.path.join(config.KEY_PATH, config.ACCOUNT_KEY_NAME)
    config.cert_key_path = os.path.join(config.KEY_PATH, config.CERT_KEY_NAME)
    config.certificate_path = os.path.join(config.CERT_PATH, config.CERT_NAME)
    config.certificate_chain_path = os.path.join(config.CERT_PATH, config.CERT_CHAIN_NAME)

    # 设置密钥大小和加密密码的默认值
    if not hasattr(config, 'CERT_KEY_SIZE'):
        config.CERT_KEY_SIZE = 3072
    
    if not hasattr(config, 'COMMON_PASSWORD'):
        config.COMMON_PASSWORD = None

    # 处理邮件发送配置
    if not hasattr(config, 'SEND_EMAIL'):
        config.SEND_EMAIL = True
    
    if config.SEND_EMAIL:
        email_configs = ['SMTP_SENDER_EMAIL', 'SMTP_SENDER_PASSWORD', 'SMTP_RECIPIENTS', 'SMTP_HOST', 'SMTP_PORT']
        if not all(hasattr(config, key) and getattr(config, key) for key in email_configs):
            logger.warning("邮件发送功能已启用，但 SMTP 配置不完整，将禁用邮件发送。")
            config.SEND_EMAIL = False
    
    return True

def _read_log_file(log_path, logger):
    """
    读取日志文件内容。
    """
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"读取日志文件失败: {e}")
        return f"无法读取日志文件: {e}"

def _create_email_html_body(success, config, log_content):
    """
    创建带样式的 HTML 邮件正文。
    """
    status_text = "成功" if success else "失败"
    
    if success:
        body_intro = "<p>ACME 证书申请流程已成功完成。所有生成的密钥和证书文件已作为附件发送。</p>"
    else:
        body_intro = "<p>ACME 证书申请流程失败。请查看以下日志了解详情。</p>"

    # 准备邮件摘要
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    domains_str = ", ".join(config.DOMAINS)
    result_color = "green" if success else "red"
    

    summary_html = f"""
<p>以下是本次 ACME 证书申请的摘要信息：</p>
<table border="1" style="width:100%; border-collapse: collapse;">
    <tr>
        <td style="padding: 8px;">执行时间</td>
        <td style="padding: 8px;">{current_time}</td>
    </tr>
    <tr>
        <td style="padding: 8px;">申请域名</td>
        <td style="padding: 8px;">{domains_str}</td>
    </tr>
    <tr>
        <td style="padding: 8px;">执行结果</td>
        <td style="padding: 8px;"><span style="color: {result_color};"><b>{status_text}</b></span></td>
    </tr>
</table>
"""
    # 构建完整邮件正文
    return f"""
{body_intro}
{summary_html}
<p>详细运行日志如下：</p>
<pre><code>{log_content}</code></pre>
"""

def _send_notification_email(success, config, logger):
    """
    根据 ACME 流程的执行结果发送邮件通知，邮件中始终包含日志。
    """
    # 准备邮件主题
    main_domain = config.DOMAINS[0]
    base_domain = main_domain[2:] if main_domain.startswith("*.") else main_domain
    status_text = "成功" if success else "失败"
    subject = f"ACME 证书申请{status_text} - {base_domain}"

    attachments = []
    if success:
        # 从配置中获取附件路径
        attachments_to_send = [
            config.account_key_path,
            config.cert_key_path,
            config.certificate_path,
            config.certificate_chain_path
        ]
        attachments = [f for f in attachments_to_send if os.path.exists(f)]
        if len(attachments) != len(attachments_to_send):
            logger.warning("一个或多个证书/密钥文件未找到，邮件附件可能不完整。")
    
    # 读取日志并创建邮件正文
    log_content = _read_log_file(LOG_FILE, logger)
    email_body_html = _create_email_html_body(success, config, log_content)

    logger.info(f"准备发送通知邮件 (状态: {status_text})...")
    try:
        send_email_with_attachments(
            sender_email=config.SMTP_SENDER_EMAIL,
            sender_password=config.SMTP_SENDER_PASSWORD,
            recipients=config.SMTP_RECIPIENTS,
            subject=subject,
            contents=[email_body_html],
            smtp_host=config.SMTP_HOST,
            smtp_port=config.SMTP_PORT,
            attachments=attachments
        )
        logger.info("通知邮件已发送。")
    except Exception as e:
        logger.error(f"发送邮件时发生错误: {e}", exc_info=True)

def _setup_logging(log_file, logger_obj):
    """
    配置 loguru 日志，包括标准输出和文件输出。
    """
    logger_obj.remove()  # 移除默认的处理器
    logger_obj.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss.SSS Z} <level>{level}</level> {file.name}/{function} {message}")
    # 将日志也输出到文件，以便在邮件中发送
    logger_obj.add(log_file, format="{time:YYYY-MM-DD HH:mm:ss.SSS Z} <level>{level}</level> {file.name}/{function} {message}", encoding="utf-8", mode="w")
    logger_obj.info("开始执行 ACME 证书申请流程...")

def _initialize_services(config_obj, logger_obj):
    """
    初始化阿里云 DNS 管理器和 ACME 客户端。
    返回 AliyunDNSManager 和 AcmeClient 实例，如果初始化失败则返回 None, None。
    """
    try:
        aliyun_manager = AliyunDNSManager(
            access_key_id=config_obj.ALIYUN_ACCESS_KEY_ID,
            access_key_secret=config_obj.ALIYUN_ACCESS_KEY_SECRET,
            endpoint=config_obj.ALIYUN_DNS_ENDPOINT
        )
        acme_client = AcmeClient(
            acme_directory_url=config_obj.ACME_DIRECTORY_URL,
            aliyun_dns_manager=aliyun_manager
        )
        logger_obj.info("服务初始化成功。")
        return acme_client
    except Exception as e:
        logger_obj.error(f"服务初始化失败: {e}")
        return None

def _execute_acme_process(acme_client_obj, config_obj, logger_obj):
    """
    执行 ACME 证书申请的核心流程。
    返回 (process_success: bool, cleanup_list: list)。
    """
    cleanup = []
    process_success = False
    try:
        logger_obj.info("开始 ACME 流程...")
        acme_client_obj._init_acme_client()
        acme_client_obj.register_acme_account(email=config_obj.ACME_CONTACT_EMAIL)
        
        order = acme_client_obj.create_acme_order(
            domains=config_obj.DOMAINS,
            key_size=config_obj.CERT_KEY_SIZE
        )
        
        challenges_map = acme_client_obj.get_dns_challenges(order)
        
        cleanup = acme_client_obj.perform_dns_challenge(challenges_map)
        
        cert_retrieved = acme_client_obj.finalize_order_and_fetch_certificate(order, config_obj.DOMAINS)

        if cert_retrieved:
            logger_obj.info("证书申请成功！")
            
            # 保存密钥和证书
            logger_obj.info("开始保存密钥和证书...")
            save_success = acme_client_obj.key_manager.save_keys_and_certificate(
                account_key_path=config_obj.account_key_path,
                cert_key_path=config_obj.cert_key_path,
                certificate_path=config_obj.certificate_path,
                certificate_chain_path=config_obj.certificate_chain_path,
                common_password=config_obj.COMMON_PASSWORD
            )
            
            if not save_success:
                 logger_obj.warning("未能成功保存所有密钥和证书文件，请检查日志。")
            
            process_success = True
        else:
            logger_obj.error("证书申请失败。请查看以上日志获取详细信息。")

    except Exception as e:
        logger_obj.error(f"执行 ACME 流程时发生严重错误: {e}", exc_info=True)
    finally:
        return process_success, cleanup

def main():
    """
    主函数，用于申请 ACME 证书并发送邮件通知。
    """
    # 1. 配置日志
    _setup_logging(LOG_FILE, logger)

    # 2. 初始化和验证配置
    if not _initialize_config(config, logger):
        logger.error("配置初始化失败，程序退出。")
        return

    # 3. 初始化服务
    acme_client = _initialize_services(config, logger)

    if acme_client is None:
        # 如果服务初始化失败，尝试发送失败邮件通知
        if config.SEND_EMAIL:
            _send_notification_email(success=False, config=config, logger=logger)
        return

    # 4. 执行 ACME 流程
    process_success, cleanup = _execute_acme_process(acme_client, config, logger)

    # 5. 清理 DNS 记录
    if cleanup:
        logger.info("开始清理 DNS 挑战记录...")
        acme_client.cleanup_dns_records(cleanup)
        logger.info("DNS 清理完成。")
    
    logger.info("ACME 证书申请流程结束。")

    # 6. 发送邮件通知
    if config.SEND_EMAIL:
        _send_notification_email(process_success, config, logger)

if __name__ == "__main__":
    main()