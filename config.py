"""
主配置文件

请根据您的实际需求修改以下配置。
"""

# --- 1. ACME 服务配置 ---
# ACME 服务器地址，用于证书申请。
# Let's Encrypt 生产环境: "https://acme-v02.api.letsencrypt.org/directory"
# Let's Encrypt 测试环境: "https://acme-staging-v02.api.letsencrypt.org/directory"
# 解释：这是用于与 ACME (Automated Certificate Management Environment) 服务器通信的 URL。
# ACME 服务器负责颁发和管理 SSL/TLS 证书。
# `Let's Encrypt 生产环境` 用于获取真实、可信的生产证书。
# `Let's Encrypt 测试环境` (当前配置) 用于测试证书申请流程，不会消耗生产环境的配额，但颁发的证书是不可信的（浏览器会报错）。
# ACME_DIRECTORY_URL = "https://acme-v02.api.letsencrypt.org/directory"
ACME_DIRECTORY_URL = "https://acme-staging-v02.api.letsencrypt.org/directory" # 默认使用测试环境

# ACME 账户联系邮箱。Let's Encrypt 会通过此邮箱发送重要通知（如证书即将过期）。
# 解释：您注册 ACME 账户时使用的邮箱地址。Let's Encrypt 可能会通过此邮箱发送关于证书过期、重要服务通知等邮件。
ACME_CONTACT_EMAIL = "your_email@example.com"


# --- 2. 证书配置 ---
# 需要申请证书的域名列表。第一个域名将作为证书的主域名。
# 示例: ["example.com", "www.example.com"] 或 ["*.example.com", "example.com"]
# 解释：一个 Python 列表，包含您希望申请证书的所有域名。
# - 如果是单个域名，例如 `["example.com"]`。
# - 如果是多个域名（SAN 证书），例如 `["example.com", "www.example.com"]`。
# - 如果是泛域名，例如 `["*.example.com", "example.com"]`。泛域名证书可以保护 `example.com` 的所有子域名（如 `www.example.com`, `blog.example.com` 等）。请注意，申请泛域名证书通常需要 DNS 验证。
# 列表中的第一个域名通常被视为证书的"主域名"或"通用名称 (CN)"。
DOMAINS = [
    "example.com",
    "www.example.com",
]


# --- 3. DNS 服务商配置 (以阿里云为例) ---
# 用于验证域名所有权的 DNS 服务商 API 凭证。
# 解释：这些是用于通过 DNS 记录验证您对域名的所有权的凭据。
# ACME 协议通常通过在您的域名下创建特定的 DNS TXT 记录来验证域名控制权。
# `ALIYUN_ACCESS_KEY_ID`：您的阿里云 AccessKey ID，用于身份验证。
# `ALIYUN_ACCESS_KEY_SECRET`：您的阿里云 AccessKey Secret，与 AccessKey ID 配对使用。
# `ALIYUN_DNS_ENDPOINT`：阿里云 DNS 服务的 API 端点。根据您选择的地域而异，例如 `alidns.cn-beijing.aliyuncs.com`。
ALIYUN_ACCESS_KEY_ID = "YOUR_ALIYUN_ACCESS_KEY_ID"
ALIYUN_ACCESS_KEY_SECRET = "YOUR_ALIYUN_ACCESS_KEY_SECRET"
ALIYUN_DNS_ENDPOINT = "alidns.cn-beijing.aliyuncs.com"  # 阿里云 API 端点，例如: 'alidns.cn-beijing.aliyuncs.com'


# --- 4. 邮件通知配置 ---
# 是否在证书申请成功后发送邮件通知。
# 如果设置为 True，请确保下面的 SMTP 配置完整且正确。
# 解释：一个布尔值，决定是否在证书申请流程结束后发送邮件通知。
# 如果设置为 `True`，系统会尝试发送邮件，您必须正确配置下面的 SMTP 参数。
# 如果设置为 `False`，则不会发送邮件。
SEND_EMAIL = False

# 发件人邮箱 (需要开启 SMTP 服务)
# 解释：用于发送通知邮件的邮箱地址。此邮箱需要开启 SMTP 服务。
SMTP_SENDER_EMAIL = "sender@example.com"
# 发件人邮箱的 SMTP 授权码 (注意不是登录密码)
# 解释：发件人邮箱的 SMTP 授权码，不是邮箱的登录密码。许多邮箱服务提供商为了安全会要求使用授权码进行 SMTP 认证。
SMTP_SENDER_PASSWORD = "YOUR_SMTP_PASSWORD"
# 收件人邮箱列表
# 解释：一个 Python 列表，包含接收通知邮件的所有邮箱地址。
SMTP_RECIPIENTS = ["recipient@example.com"]
# SMTP 服务器地址
# 解释：发件人邮箱所属的 SMTP 服务器地址。例如，网易邮箱是 `smtp.163.com`，Gmail 是 `smtp.gmail.com`。
SMTP_HOST = "smtp.example.com"
# SMTP 服务器端口 (通常为 465 (SSL) 或 587 (TLS))
SMTP_PORT = 587


# --- 5. 高级配置 (可选) ---
# 以下配置项都有合理的默认值，通常无需修改。
# 如果需要自定义，请取消注释并修改。

# A. 密钥和证书的存储路径
# 默认: "./keys"
# 解释：用于存储 ACME 账户私钥和证书私钥的本地目录路径。
# KEY_PATH = "./keys"
# 默认: "./certs"
# 解释：用于存储生成的证书文件（包括主证书和证书链）的本地目录路径。
# CERT_PATH = "./certs"

# B. 生成的密钥和证书文件名
# 如果不配置，将根据第一个域名自动生成。例如，域名为 example.com，则生成 example.com.key, example.com.crt 等。
# ACME 账户私钥文件名 (默认: "account.key")
# 解释：存储 ACME 账户私钥的文件名。这个私钥用于标识您的 ACME 账户，请妥善保管。
# ACCOUNT_KEY_NAME = "account.key"
# 证书私钥文件名 (默认: 根据域名生成)
# 解释：存储新生成证书的私钥文件名。这个私钥非常重要，必须与证书文件配对使用。
# CERT_KEY_NAME = "private.key"
# 证书文件名 (默认: 根据域名生成)
# 解释：存储主证书文件（通常是 `domain.crt`）的文件名。这是您的网站需要部署的证书。
# CERT_NAME = "cert.crt"
# 证书链文件名 (默认: 根据域名生成)
# 解释：存储证书链文件（通常是 `domain-chain.crt`）的文件名。证书链包含了从您的证书到根证书的所有中间证书，用于帮助浏览器验证证书的合法性。
# CERT_CHAIN_NAME = "cert-chain.crt"

# C. 密钥参数
# 证书私钥的 RSA 密钥位数 (默认: 3072)
# 解释：生成证书私钥时使用的 RSA 密钥长度。位数越高，安全性越强，但计算开销也越大。3072 位通常是一个安全且性能合理的选择。
# CERT_KEY_SIZE = 3072
# 加密私钥的密码 (如果设置为 None 或留空，则不加密)
# 解释：一个可选密码，用于加密生成的证书私钥。如果设置为 `None` 或空字符串，则私钥将不加密。
# 如果您需要额外的安全层，可以设置密码。请注意，加密后的私钥在每次使用时都需要提供密码。
# COMMON_PASSWORD = None
