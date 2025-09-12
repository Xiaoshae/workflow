# acme_client.py
import sys
import os

# 将当前脚本的目录添加到 Python 模块搜索路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import time
from loguru import logger
from cryptography.hazmat.primitives import serialization
from acme import challenges
import acme.client as acme_client_module
from acme import messages
from acme.errors import Error

# 从你的项目中导入
from aliyun_dns import AliyunDNSManager
from key_manager import KeyManager
from typing import List, Dict, Any, Tuple
from cryptography.hazmat.primitives import serialization


class AcmeClient:
    def __init__(self, acme_directory_url: str, aliyun_dns_manager: AliyunDNSManager):
        self.acme_directory_url = acme_directory_url
        self.aliyun_dns_manager = aliyun_dns_manager
        self.client = None # ACME 客户端实例
        self.key_manager = KeyManager() # 实例化 KeyManager

    def _init_acme_client(self) -> None:
        """
        初始化 ACME 客户端。
        ACME 客户端在每次需要与 ACME 服务器通信时都需要初始化，
        确保使用了正确的账户密钥。
        """
        # 如果客户端已经初始化，则直接返回，避免重复操作和网络请求
        if self.client is not None:
            logger.info("ACME 客户端已初始化，跳过重复初始化。")
            return

        try:
            # 使用 KeyManager 获取账户 JWK
            account_jwk = self.key_manager.account_jwk

            net=acme_client_module.ClientNetwork(account_jwk,user_agent="acme-python-client") # 使用同一个 signer 作为网络客户端的 key

            directory = messages.Directory.from_json(net.get(self.acme_directory_url).json())

            # 使用目录 URL 和账户密钥创建 ACME 客户端实例
            self.client = acme_client_module.ClientV2(
                directory=directory,
                net=net
            )

            logger.info(f"ACME 客户端初始化完成。目录 URL：{self.acme_directory_url}")

        except Exception as e:
            logger.error(f"ACME 客户端初始化失败，错误: {e}")
            raise # 重新抛出异常

        return

    def register_acme_account(self, email: str) -> None:
        """
        注册或更新 ACME 账户。
        如果账户已存在，将加载现有账户信息；否则，将注册新账户。
        :param email: 账户联系邮箱。
        """
        if self.client is None:
            self._init_acme_client() # 确保客户端已初始化

        try:
            # 尝试根据账户密钥查找现有账户
            # Let's Encrypt 不直接提供通过 email 查询账户的功能，
            # 它是通过账户密钥来识别账户的。
            # 这里我们假设如果密钥存在且有效，client 初始化时会识别到。
            # 对于新密钥，需要执行 new_account。
            # ACME 库通常会智能处理，如果密钥已注册，则直接使用，否则注册。
            # 为了确保账户注册，即使密钥存在也尝试注册一次，因为 new_account 是幂等的。

            # 创建 NewRegistration 对象，包含联系信息和接受条款
            new_reg_msg = messages.NewRegistration.from_data(
                email=email,
                terms_of_service_agreed=True
            )

            # 尝试注册新账户。
            self.account = self.client.new_account(new_reg_msg)

            logger.info(f"ACME 账户注册成功。邮箱：{email}，账户 URI：{self.account.uri}")

        except Error as e:
            logger.error(f"ACME 账户注册失败，错误：{e}")
            raise
            
        return

    def create_acme_order(self, domains: list[str],cert_key_path : str = None,key_size: int = 3072): # 添加 organization 和 country 参数
        """
        创建 ACME 证书订单。
        :param domains: 需要申请证书的域名列表，例如 ["example.com", "*.example.com"]。
        :param organization: 组织名称，默认为 "MyOrganization"。
        :param country: 国家代码，默认为 "CN"。
        :return: ACME 订单对象。
        """
        if self.client is None:
            raise Error("ACME 客户端未初始化")

        logger.info(f"正在为域名 {domains} 创建 ACME 订单...")

        try:

            # 尝试加载证书私钥，如果未提供路径或加载失败，则生成新的
            cert_key_loaded_successfully = False
            if cert_key_path and os.path.exists(cert_key_path):
                if self.key_manager.load_cert_key_from_file(cert_key_path):
                    logger.info(f"成功从 {cert_key_path} 加载证书私钥。")
                    cert_key_loaded_successfully = True
                else:
                    logger.warning(f"从 {cert_key_path} 加载证书私钥失败。将生成一个新的。")
            else:
                logger.info("未提供证书私钥路径或文件不存在。将生成一个新的证书私钥。")

            if not cert_key_loaded_successfully:
                self.key_manager.generate_new_cert_key(key_size)
                logger.info("已生成一个新的证书私钥。")

            # 2. 生成 CSR
            # 确保 domains 列表不为空
            if not domains:
                raise ValueError("domains 列表不能为空，无法生成 CSR。")

            csr_object = self.key_manager.generate_csr( # 使用 KeyManager 生成 CSR
                domains
            )
            # 将 CSR 对象转换为 PEM 编码的字节
            csr_pem = csr_object.public_bytes(serialization.Encoding.PEM)
            logger.info("CSR 已生成。")

            # 3. 创建新订单，传递 CSR 的 PEM 编码字节
            order = self.client.new_order(csr_pem)
            logger.info(f"ACME 订单创建成功。订单 URI: {order.uri}")
            return order
        except Error as e:
            logger.error(f"ACME 订单创建失败: {e}")
            raise

    def get_dns_challenges(self, order):
        """
        从 ACME 订单中获取 DNS 挑战信息。
        :param order: ACME 订单对象。
        :return: 包含域名和对应 DNS 挑战的列表，例如 [{"domain": "example.com", "authz": challenge_obj, ...}]。
        """
        challenges_map = [] # 将 challenges_map 更改为列表
        for authz in order.authorizations:
            domain_from_authz = authz.body.identifier.value # 获取授权对象中的域名
            logger.info(f"正在获取域名 {domain_from_authz} 的挑战信息...")
            for challenge_body in authz.body.challenges:
                # 寻找 DNS-01 挑战
                if isinstance(challenge_body.chall, challenges.DNS01):

                    dns_value = challenge_body.chall.validation(self.client.net.key)

                    challenges_map.append({ # 将挑战信息作为字典添加到列表中
                        "domain": domain_from_authz, # 新增的 domain 字段
                        "authz": authz,
                        "challenge_body": challenge_body,
                        "dns_value": dns_value
                    })

                    logger.info(f"获取到域名 {domain_from_authz} 的 DNS 挑战值: {dns_value}")

                    break # 每个域名我们只需要一个 DNS-01 挑战

        if not challenges_map:
            logger.error("未找到任何 DNS-01 挑战。")
            raise ValueError("未找到任何 DNS-01 挑战。")
        return challenges_map

    def _get_dns_rr_and_base_domain(self, domain: str) -> Tuple[str, str]:
        """
        根据域名生成 ACME 挑战所需的 DNS TXT 记录的 RR (主机记录) 和主域名。
        例如：
        - "example.com" -> ("_acme-challenge", "example.com")
        - "www.example.com" -> ("_acme-challenge.www", "example.com")
        - "*.example.com" -> ("_acme-challenge", "example.com")
        """
        rr_prefix = '_acme-challenge'
        effective_domain = domain

        # 处理通配符域名，将 '*.example.com' 转换为 'example.com' 以便后续解析
        if effective_domain.startswith('*.'):
            effective_domain = effective_domain[2:]

        domain_parts = effective_domain.split('.')
        # 假设主域名是最后两段 (例如 example.com)。对于复杂的 TLD (如 co.uk)，可能需要更高级的库。
        base_domain = '.'.join(domain_parts[-2:])

        # 确定 RR (主机记录) 中的子域部分
        sub_domain_part = ''
        if len(domain_parts) > 2: # 如果存在子域
            sub_domain_part = '.'.join(domain_parts[:-2])

        if sub_domain_part:
            rr = f"{rr_prefix}.{sub_domain_part}"
        else:
            rr = rr_prefix
        
        return rr, base_domain

    def _validate_single_domain_challenge(self, domain: str, authz: Any, challenge_body: Any):
        """
        发送单个域名的挑战响应给 ACME 服务器，并等待验证结果。
        此方法封装了验证逻辑，避免 perform_dns_challenge 过长。
        :param domain: 当前正在处理的域名。
        :param authz: 当前域名的授权对象。
        :param challenge_body: 当前域名的挑战体对象。
        """
        if self.client is None:
            logger.info("ACME 客户端未初始化")
            raise Error("ACME 客户端未初始化")

        try:
            self.client.answer_challenge(challenge_body, challenge_body.chall)
            logger.info(f"域名 {domain} 挑战响应已发送。5 秒后检查挑战状态。")

            time.sleep(5)

            max_retries = 10
            retry_delay_seconds = 5
            for i in range(max_retries):
                # 重新获取最新的授权对象，确保状态是最新的
                authz, _ = self.client.poll(authz)

                logger.info(f"域名 {domain} 挑战状态：{authz.body.status}。当前次数：{i+1}，最大重试次数：{max_retries}，重试间隔：{retry_delay_seconds} 秒。")
                if authz.body.status == messages.STATUS_VALID:
                    logger.info(f"域名 {domain} 挑战验证成功！")
                    return # 验证成功，函数结束
                elif authz.body.status == messages.STATUS_PENDING:
                    logger.info(f"域名 {domain} 挑战仍在等待验证，等待 {retry_delay_seconds} 秒后重试。")
                    time.sleep(retry_delay_seconds)
                else:
                    raise Error(f"域名 {domain} 挑战验证失败，状态：{authz.body.status}")

            raise Error(f"域名 {domain} 挑战验证超时。")
        except Exception as e:
            logger.error(f"验证域名 {domain} 挑战时发生错误：{e}")
            raise

    def perform_dns_challenge(self, domain_challenges_map: List[Dict[str, Any]]) -> List[Dict[str, str]]: # 更新参数类型提示
        """
        执行 DNS 挑战，将 TXT 记录添加到阿里云 DNS，并逐个等待验证。
        :param domain_challenges_map: 包含域名和对应 DNS 挑战信息的列表。
        :return: 包含成功处理的、需要清理的唯一 DNS 记录信息的列表。
        """
        if self.client is None:
            logger.info("ACME 客户端未初始化")
            raise Error("ACME 客户端未初始化")

        logger.info("开始逐个执行 DNS 挑战。")
        cleanup = [] # 用于存储成功处理的 DNS 记录信息，以便后续清理

        for challenge_info in domain_challenges_map: # 遍历列表中的每个挑战信息字典
            domain = challenge_info["domain"] # 从字典中获取 domain
            dns_value = challenge_info["dns_value"]
            authz = challenge_info["authz"]
            challenge_body = challenge_info["challenge_body"]

            rr, base_domain = self._get_dns_rr_and_base_domain(domain)
            
            logger.info(f"---------- 正在处理域名 {domain} 的 DNS 挑战 ----------")
            logger.info(f"准备为域名 {domain} 添加 DNS TXT 记录: RR='{rr}', 主域名: '{base_domain}'")
            try:
                # Add/Upsert the DNS record
                self.aliyun_dns_manager.upsert_record(
                    domain_name=base_domain,
                    rr=rr,
                    record_type="TXT",
                    value=dns_value,
                    ttl=600 # Let's Encrypt 建议使用小 TTL
                )
                logger.info(f"已为域名 {domain} 添加/更新 TXT 记录。等待 DNS 传播。")

                rr_domain = ( rr , domain )
                if rr_domain in cleanup:
                    time.sleep(60)

                # 调用独立的函数来验证当前域名的挑战
                self._validate_single_domain_challenge(domain, authz, challenge_body)
                
                # 将需要清理的记录信息添加到列表中，确保唯一性
                if rr_domain not in cleanup:
                    cleanup.append(rr_domain)

            except Exception as e:
                logger.error(f"处理域名 {domain} 的挑战时发生错误：{e}")
                raise
        
        logger.info("所有域名挑战逐个验证完成。")
        return cleanup

    def finalize_order_and_fetch_certificate(self, order, domains: list[str]) -> bool:
        """
        生成 CSR 并最终确定订单，然后获取证书。
        :param order: ACME 订单对象。
        :param domains: 包含所有域名（包括通配符域名）的列表。
        :return: 成功获取并保存证书到 KeyManager 返回 True，否则返回 False。
        """
        if self.client is None:
            logger.info("ACME 客户端未初始化")
            raise Error("ACME 客户端未初始化")

        logger.info("最终确定订单并获取证书...")
        try:
            order = self.client.poll_and_finalize(order)
            fullchain_certificate_pem = order.fullchain_pem
            # 将完整链证书保存到 KeyManager 中，确保编码为字节
            self.key_manager.certificate_chain = fullchain_certificate_pem.encode('utf-8') # 编码为字节
            logger.info("证书获取成功，并已保存到 KeyManager。")
            return True
        except Exception as e:
            logger.error(f"最终确定订单或获取证书时发生错误：{e}")
            return False

    def save_certificate(self,
                         account_key_path: str,
                         cert_key_path: str,
                         certificate_path: str,
                         certificate_chain_path: str,  # 新增参数
                         common_password: bytes = None) -> bool:
        """
        保存 TLS 证书和私钥到文件。
        此方法将直接调用 KeyManager 中的成员方法来执行保存。
        :param account_key_path: 账户私钥的保存路径。
        :param cert_key_path: 证书私钥的保存路径。
        :param certificate_path: 终端数字证书的保存路径（即证书链中的第一个证书）。
        :param certificate_chain_path: 完整的数字证书链的保存路径。
        :param common_password: 如果指定，将作为账户私钥和证书私钥的统一加密密码。
        :return: 保存成功返回 True，否则返回 False。
        """
        logger.info(f"正在保存账户私钥到 {account_key_path}, 证书私钥到 {cert_key_path}, 终端证书到 {certificate_path} 和完整链证书到 {certificate_chain_path}...")
        try:
            # 直接将参数传递给 KeyManager 的 save_keys_and_certificate 成员方法
            self.key_manager.save_keys_and_certificate(
                account_key_path=account_key_path,
                cert_key_path=cert_key_path,
                certificate_path=certificate_path,
                certificate_chain_path=certificate_chain_path, # 传递新增参数
                common_password=common_password
            )
            logger.info("所有密钥和证书保存成功。")
            return True
        except Exception as e:
            logger.error(f"保存证书和私钥失败: {e}")
            return False

    def cleanup_dns_records(self, processed_domains_info: List[Tuple[str, str]]): # 更新参数类型提示
        """
        清理 DNS 挑战过程中添加的 TXT 记录。
        :param processed_domains_info: 包含成功处理并需要清理的 DNS 记录信息的列表。
        例如：[{"rr": "_acme-challenge", "base_domain": "example.com"}]
        """
        logger.info("开始清理 DNS 挑战记录...")
        for rr_to_delete , base_domain in processed_domains_info: # 直接遍历列表
            logger.info(f"正在清理域名 {base_domain} 的 DNS TXT 记录: RR='{rr_to_delete}', DomainName='{base_domain}'。")
            try:
                self.aliyun_dns_manager.delete_sub_records(
                    domain_name=base_domain,
                    rr=rr_to_delete,
                    record_type="TXT"
                )
                logger.info(f"已成功清理域名 {base_domain} 的 DNS TXT 记录。")
            except Exception as e:
                logger.warning(f"清理域名 {base_domain} 的 DNS TXT 记录失败，错误：{e}")
        logger.info("DNS 挑战记录清理完成。")


