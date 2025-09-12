# AcmeCert

`AcmeCert` 是一个用于自动化 Let's Encrypt 证书申请和续期的 Python 脚本。它集成了阿里云 DNS 验证，并支持通过邮件通知证书申请结果及发送证书文件。



## ✨ 主要特性

*   **全自动化**: 一键申请或续期 Let's Encrypt SSL/TLS 证书。
*   **DNS 验证**: 支持通过阿里云 DNS API 自动完成 ACME DNS-01 挑战。
*   **泛域名支持**: 轻松申请和管理泛域名证书（如 `*.example.com`）。
*   **邮件通知**: 申请结果（成功/失败）及生成的证书文件可通过邮件发送。
*   **可配置性**: 灵活的配置选项，包括 ACME 服务器、域名、DNS 凭证、邮件设置、证书存储路径和文件名等。
*   **模块化设计**: 核心功能封装在 `acme_client.py`、`aliyun_dns.py` 和 `send_email.py` 中，易于扩展和维护。



## 🚀 快速开始

本节将指导您如何快速、简单地使用 `AcmeCert` 脚本。



### 📋 先决条件

在运行脚本之前，请确保您已具备以下条件：

1.  **Python 3**: 您的系统上安装了 Python 3.6 或更高版本。
2.  **pip**: Python 包管理器，通常随 Python 3 一起安装。
3.  **域名**: 您拥有一个或多个域名，并且可以通过阿里云 DNS 进行管理。
4.  **阿里云 AccessKey**: 您的阿里云账户需要有 DNS 服务的 `AccessKey ID` 和 `AccessKey Secret`，以便脚本能够操作您的 DNS 记录。
5.  **SMTP 邮箱 (可选)**: 如果您想接收邮件通知，需要一个支持 SMTP 发送的邮箱及其授权码。



### 📦 安装

1.  **克隆仓库**:
    ```bash
    git clone https://github.com/xiaoshae/acmecert.git
    cd acmecert
    ```

2.  **安装依赖**:
    
    ```bash
    pip install -r requirements.txt
    ```
    
    如果服务器位于国内，可以指定 pipy 镜像站
    
    ```bash
    pip install -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
    ```



### ⚙️ 配置 `config.py`

`config.py` 是脚本的主要配置文件。您需要根据您的实际情况修改其中的变量。



打开 `config.py` 文件，并按照以下说明进行配置：

1.  **ACME 服务配置**:
    *   `ACME_DIRECTORY_URL`:
        *   **测试环境 (推荐初次使用)**: `"https://acme-staging-v02.api.letsencrypt.org/directory"`
            此环境用于测试，不会消耗生产配额，但颁发的证书不受浏览器信任。
        *   **生产环境**: `"https://acme-v02.api.letsencrypt.org/directory"`
            用于获取真实、可信的生产证书。**在确认一切工作正常后切换到此环境。**
    *   `ACME_CONTACT_EMAIL`: 您的邮箱地址。Let's Encrypt 将通过此邮箱发送重要通知。

    ```python
    # config.py
    ACME_DIRECTORY_URL = "https://acme-staging-v02.api.letsencrypt.org/directory" # 默认为测试环境
    ACME_CONTACT_EMAIL = "your_email@example.com" # 替换为您的邮箱
    ```



2. **证书配置**:

*   `DOMAINS`: 您需要申请证书的域名列表。第一个域名将作为证书的主域名 (Common Name)。
    *   单个域名: `["example.com"]`
    *   多个域名 (SAN 证书): `["example.com", "www.example.com"]`
    *   泛域名: `["*.example.com", "example.com"]` (泛域名通常需要 DNS 验证)

```python
# config.py
DOMAINS = ["*.yourdomain.cn", "yourdomain.cn"] # 替换为您的域名
```



3. **DNS 服务商配置 (以阿里云为例)**:

   *   `ALIYUN_ACCESS_KEY_ID`: 您的阿里云 AccessKey ID。
   *   `ALIYUN_ACCESS_KEY_SECRET`: 您的阿里云 AccessKey Secret。
   *   `ALIYUN_DNS_ENDPOINT`: 阿里云 DNS 服务的 API 端点。例如 `alidns.cn-beijing.aliyuncs.com`。请根据您的地域选择。

   ```python
   # config.py
   ALIYUN_ACCESS_KEY_ID = "YOUR_ALIYUN_ACCESS_KEY_ID" # 替换为您的 AccessKey ID
   ALIYUN_ACCESS_KEY_SECRET = "YOUR_ALIYUN_ACCESS_KEY_SECRET" # 替换为您的 AccessKey Secret
   ALIYUN_DNS_ENDPOINT = "alidns.cn-beijing.aliyuncs.com"
   ```



4. **邮件通知配置 (可选)**:
   如果您希望在证书申请成功或失败时收到邮件通知，请设置 `SEND_EMAIL` 为 `True`，并配置以下 SMTP 参数。

   *   `SEND_EMAIL`: 是否发送邮件通知。
   *   `SMTP_SENDER_EMAIL`: 发件人邮箱（需要开启 SMTP 服务）。
   *   `SMTP_SENDER_PASSWORD`: 发件人邮箱的 SMTP 授权码（**注意不是登录密码**）。
   *   `SMTP_RECIPIENTS`: 收件人邮箱列表。
   *   `SMTP_HOST`: SMTP 服务器地址（例如 `smtp.163.com` 或 `smtp.gmail.com`）。
   *   `SMTP_PORT`: SMTP 服务器端口（通常 465 (SSL) 或 587 (TLS)）。

   ```python
   # config.py
   SEND_EMAIL = True # 设置为 True 启用邮件通知
   
   SMTP_SENDER_EMAIL = "your_sender_email@example.com" # 替换为发件人邮箱
   SMTP_SENDER_PASSWORD = "YOUR_SMTP_AUTHORIZATION_CODE" # 替换为 SMTP 授权码
   SMTP_RECIPIENTS = ["your_recipient_email@example.com"] # 替换为收件人邮箱
   SMTP_HOST = "smtp.163.com"
   SMTP_PORT = 587
   ```



### 🏃 运行脚本

配置完成后，您只需运行 `main.py` 脚本：

```bash
python main.py
```



### 📄 证书和日志

*   **生成的证书和密钥**: 默认存储在 `./certs` 和 `./keys` 目录下。例如，对于域名 `yourdomain.cn`，您会找到 `yourdomain.cn.key` (私钥)、`yourdomain.cn.crt` (主证书) 和 `yourdomain.cn-chain.crt` (证书链)。
*   **运行日志**: 详细的运行日志会输出到控制台，并保存到 `main_run.log` 文件中。如果配置了邮件通知，此日志也会作为邮件正文的一部分发送。



## 💡 高级使用

`config.py` 中还提供了一些高级配置选项，通常有合理的默认值，但在特定场景下可能需要修改。



### A. 密钥和证书的存储路径

您可以自定义生成的密钥和证书文件的存储目录。

*   `KEY_PATH`: 存储 ACME 账户私钥和证书私钥的本地目录路径。
*   `CERT_PATH`: 存储生成的证书文件（包括主证书和证书链）的本地目录路径。

```python
# config.py
# KEY_PATH = "./my_custom_keys" # 默认: "./keys"
# CERT_PATH = "./my_custom_certs" # 默认: "./certs"
```



### B. 生成的密钥和证书文件名

如果未配置，文件名将根据 `DOMAINS` 列表中的第一个域名自动生成。

*   `ACCOUNT_KEY_NAME`: ACME 账户私钥的文件名 (默认: "account.key")。
*   `CERT_KEY_NAME`: 证书私钥的文件名 (默认: 根据域名生成，如 `yourdomain.cn.key`)。
*   `CERT_NAME`: 主证书文件名 (默认: 根据域名生成，如 `yourdomain.cn.crt`)。
*   `CERT_CHAIN_NAME`: 证书链文件名 (默认: 根据域名生成，如 `yourdomain.cn-chain.crt`)。

```python
# config.py
# ACCOUNT_KEY_NAME = "my_account.key"
# CERT_KEY_NAME = "server.key"
# CERT_NAME = "fullchain.crt"
# CERT_CHAIN_NAME = "ca_bundle.crt"
```



### C. 密钥参数

*   `CERT_KEY_SIZE`: 生成证书私钥时使用的 RSA 密钥位数 (默认: 3072)。位数越高，安全性越强。
*   `COMMON_PASSWORD`: 用于加密生成的证书私钥的密码。如果设置为 `None` 或留空，则私钥将不加密。**请注意，如果设置了密码，在部署证书时通常需要解密私钥。**

```python
# config.py
# CERT_KEY_SIZE = 4096 # 更高的安全性
# COMMON_PASSWORD = "your_secret_password" # 设置密码以加密私钥
```



## ⚠️ 故障排除

*   **`_initialize_config` 错误**:
    *   **"阿里云配置不完整"**: 请检查 `ALIYUN_ACCESS_KEY_ID`, `ALIYUN_ACCESS_KEY_SECRET`, `ALIYUN_DNS_ENDPOINT` 是否已正确填写。
    *   **"域名列表不能为空"**: 请在 `DOMAINS` 中至少配置一个域名。
    *   **"ACME 联系邮箱不能为空"**: 请配置 `ACME_CONTACT_EMAIL`。
*   **服务初始化失败**:
    *   检查您的阿里云 AccessKey ID 和 Secret 是否正确。
    *   确认 `ALIYUN_DNS_ENDPOINT` 与您的阿里云 DNS 区域匹配。
*   **ACME 流程失败**:
    *   **DNS 验证失败**: 可能是 DNS 记录传播需要时间，或您的 AccessKey 没有足够的权限来添加/删除 DNS 记录。请查看 `main_run.log` 中的详细错误信息。
    *   **Let's Encrypt 速率限制**: 在生产环境频繁申请证书可能会触发速率限制。请使用测试环境进行调试。
*   **邮件发送失败**:
    *   检查 `SMTP_SENDER_EMAIL`, `SMTP_SENDER_PASSWORD`, `SMTP_RECIPIENTS`, `SMTP_HOST`, `SMTP_PORT` 配置是否正确。
    *   确认发件人邮箱已开启 SMTP 服务，并且使用了正确的**授权码**而不是登录密码。
    *   检查防火墙或网络设置是否阻止了对 SMTP 服务器的连接。



## 🤝 贡献

欢迎通过 Pull Request 贡献代码，或通过 Issue 报告 Bug 和提出建议。



## 📄 许可证

本项目基于 MIT 许可证。详见 `LICENSE` 文件。
