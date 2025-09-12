import yagmail

def send_email_with_attachments(
    sender_email: str,
    sender_password: str,
    recipients: str | list[str],
    subject: str,
    contents: str | list[str],
    smtp_host: str,
    attachments: str | list[str] | None = None,
    smtp_port: int | None = None
):
    """
    使用 yagmail 发送邮件。

    Args:
        sender_email (str): 发件人邮箱地址。
        sender_password (str): 发件人邮箱密码或授权码。
        recipients (str | list[str]): 收件人邮箱地址，可以是单个字符串或字符串列表。
        subject (str): 邮件主题。
        contents (str | list[str]): 邮件内容，可以是单个字符串或字符串列表。
        smtp_host (str): SMTP 服务器地址（必填）。
        attachments (str | list[str] | None): 附件文件路径，可以是单个字符串路径、字符串路径列表或 None。
        smtp_port (int | None): 可选的 SMTP 服务器端口。如果指定，将使用此端口。
                                如果未指定，yagmail 将使用 smtp_host 的默认端口。
    """
    try:
        # 准备 yagmail.SMTP 客户端的参数
        yag_args = {
            "user": sender_email,
            "password": sender_password,
            "host": smtp_host
        }

        if smtp_port:
            yag_args["port"] = smtp_port

        # 初始化 yagmail SMTP 客户端
        yag = yagmail.SMTP(**yag_args)

        # 发送邮件
        yag.send(
            to=recipients,
            subject=subject,
            contents=contents,
            attachments=attachments
        )
        print("邮件发送成功！")

    except yagmail.YagAddressError as e:
        print(f"邮件地址错误：{e}")
    except yagmail.YagConnectionError as e:
        print(f"连接错误，请检查网络或SMTP配置：{e}")
    except yagmail.YagAuthenticationError as e:
        print(f"认证失败，请检查邮箱账号或授权码：{e}")
    except Exception as e:
        print(f"发送邮件时发生错误：{e}")

"""
# 示例用法 (请替换为您的实际信息)
if __name__ == "__main__":
    # 您的邮箱信息
    my_email = "zoning5232@163.com"  # 替换为您的发件邮箱
    my_password = "XRUYpWqqaEnkkZLn"  # 替换为您的邮箱密码或授权码

    # 收件人信息
    recipient_emails = ["3255968096@qq.com"] # 替换为收件人邮箱

    # 邮件主题
    email_subject = "测试邮件主题"

    # 邮件内容
    email_content_text = "这是一封由 Python yagmail 发送的测试邮件。"

    # 附件 (可以是0个，1个或多个)
    # 创建一些虚拟文件用于测试
    with open("test_attachment_1.txt", "w") as f:
        f.write("这是第一个附件的内容。")
    attachments_list = [
        "test_attachment_1.txt"
    ]

    print("\n--- 示例 1: 指定 SMTP 主机和端口 (例如 Gmail) ---")
    # 请替换为您的 SMTP 服务器地址和端口
    # 对于 Gmail: smtp.gmail.com, 587 (TLS) 或 465 (SSL)
    # 对于 QQ 邮箱: smtp.qq.com, 465 (SSL)
    send_email_with_attachments(
        sender_email=my_email,
        sender_password=my_password,
        recipients=recipient_emails,
        subject=email_subject + " (指定主机和端口)",
        contents=email_content_text,
        attachments=attachments_list,
        smtp_host="smtp.163.com", # 替换为您的 SMTP 主机 (必填)
        smtp_port=587 # 替换为您的 SMTP 端口 (可选)
    )

    print("\n--- 示例 2: 只指定 SMTP 主机，端口使用默认值 ---")
    send_email_with_attachments(
        sender_email=my_email,
        sender_password=my_password,
        recipients=recipient_emails,
        subject=email_subject + " (只指定主机)",
        contents=email_content_text,
        attachments=attachments_list,
        smtp_host="smtp.163.com" # 替换为您的 SMTP 主机 (必填)
    )

    # 清理测试文件
    if os.path.exists("test_attachment_1.txt"):
        os.remove("test_attachment_1.txt")
"""