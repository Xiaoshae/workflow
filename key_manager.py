import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from josepy.jwk import JWKRSA
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from typing import List
from loguru import logger

class KeyManager:
    def __init__(self):
        self._account_key = None
        self._cert_key = None
        self._certificate_chain = None

        # 账户密钥对（始终新生成）
        self._account_key = self._generate_key()
        logger.info("[账户密钥] 生成账户密钥成功。")

    def _generate_key(self,key_size=3072):
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )

    def _save_key_to_file(self, key, file_path, password=None) -> bool:
        """
        辅助函数：保存私钥到指定文件，并支持密码加密。
        Returns:
            bool: 保存成功返回 True，否则返回 False。
        """
        if not key:
            logger.warning(f"[保存密钥]跳过保存密钥到 {file_path}: 密钥为空。")
            return False

        encoding = serialization.Encoding.PEM
        format = serialization.PrivateFormat.PKCS8
        encryption_algorithm = serialization.NoEncryption()
        if password:
            encryption_algorithm = serialization.BestAvailableEncryption(password.encode('utf-8'))

        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(key.private_bytes(
                    encoding=encoding,
                    format=format,
                    encryption_algorithm=encryption_algorithm
                ))
            logger.info(f"[保存密钥]保存密钥成功，位置：{file_path}。")
            return True
        except Exception as e:
            logger.error(f"[保存密钥]保存密钥失败，位置：{file_path}，错误：{e}")
            return False

    @property
    def account_jwk(self):
        return JWKRSA(key=self._account_key)

    @property
    def cert_public(self):
        if self._cert_key:
            return self._cert_key.public_key()
        return None

    @property
    def cert_private(self):
        return self._cert_key

    @property
    def certificate(self):
        """
        从证书链中提取并返回终端用户证书。
        """
        if not self._certificate_chain:
            return None
        try:
            certs = x509.load_pem_x509_certificates(self._certificate_chain)
            if certs:
                return certs[0].public_bytes(serialization.Encoding.PEM)
            return None
        except Exception as e:
            logger.error(f"从证书链中提取终端证书失败: {e}")
            return None

    @property
    def certificate_chain(self):
        return self._certificate_chain

    @certificate_chain.setter
    def certificate_chain(self, cert_data):
        self._certificate_chain = cert_data

    def generate_new_cert_key(self, key_size=3072):
        """
        生成新的数字证书密钥对（仅支持 RSA）。
        Args:
            key_size (int): RSA 密钥的位数，例如 2048, 4096。
        """
        self._cert_key = self._generate_key(key_size=key_size)
        logger.info("[证书密钥] 生成新证书密钥成功。")

    def load_cert_key_from_file(self, file_path, password=None):
        """
        从指定文件路径加载数字证书私钥。
        加载成功后，公钥会自动从私钥中提取。
        Args:
            file_path (str): 私钥文件的路径。
            password (str, optional): 私钥的密码（如果存在）。
        Returns:
            bool: 如果加载成功返回 True，否则返回 False。
        """
        try:
            with open(file_path, "rb") as f:
                if password:
                    self._cert_key = serialization.load_pem_private_key(
                        f.read(),
                        password=password.encode('utf-8'),
                    )
                else:
                    self._cert_key = serialization.load_pem_private_key(
                        f.read(),
                        password=None,
                    )
            logger.info(f"[证书密钥]加载数字证书私钥成功，位置：{file_path}。")
            return True
        except Exception as e:
            logger.error(f"[证书密钥]加载数字证书私钥失败，位置：{file_path}，错误：{e}")
            self._cert_key = None
            return False

    def generate_csr(self, domains: List[str]):
        """
        使用内部证书私钥生成 CSR 文件。
        此函数将用于 ACME 订单的创建。
        注意：此实现目前仅支持 RSA 密钥。
        Args:
            domains (List[str]): 包含所有需要申请证书的域名的列表，例如 ["example.com", "*.example.com"]。
                                 第一个域名将作为 Common Name (CN)，所有域名将作为 Subject Alternative Names (SANs)。
            organization (str, optional): 组织名称。默认为 "MyOrganization"。
            country (str, optional): 国家代码 (例如 "CN")。默认为 "CN"。
        Returns:
            cryptography.x509.CertificateSigningRequest: 生成的 CSR 对象。
        Raises:
            ValueError: 如果证书私钥不存在或域名列表为空。
            TypeError: 如果证书私钥不是 RSA 类型。
        """
        if not self._cert_key:
            logger.error("[生成CSR]证书私钥不存在，无法生成 CSR。请先生成或加载证书私钥。")
            raise ValueError("CSR 生成失败，请检查证书私钥是否存在。")

        # 检查是否为 RSA 密钥，因为原始的 generate_csr 仅支持 RSA
        if not isinstance(self._cert_key, rsa.RSAPrivateKey):
            logger.error("[生成CSR]目前 generate_csr 方法仅支持 RSA 证书私钥。")
            raise TypeError("CSR 生成失败，请检查证书私钥是否为 RSA 类型。")

        if not domains:
            logger.error("[生成CSR]域名列表为空，无法生成 CSR。")
            raise ValueError("CSR 生成失败，请检查域名列表是否为空。")

        common_name = domains[0] # 第一个域名作为 Common Name

        subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])

        # 为所有域名创建 Subject Alternative Names (SANs) 扩展
        san_extension = x509.SubjectAlternativeName([
            x509.DNSName(domain) for domain in domains
        ])

        csr = x509.CertificateSigningRequestBuilder().subject_name(
            subject
        ).add_extension(
            san_extension, critical=False # SANs 扩展通常不是关键的
        ).sign(self._cert_key, hashes.SHA256(), default_backend())

        logger.info("[生成CSR]生成CSR成功。")

        return csr

    def save_keys_and_certificate(self, account_key_path: str, cert_key_path: str,
                                  certificate_path: str, certificate_chain_path: str,
                                  common_password: str = None) -> bool:
        """
        保存账户私钥、证书私钥、终端数字证书和数字证书链到指定文件。
        Args:
            account_key_path (str): 账户私钥的保存路径。
            cert_key_path (str): 证书私钥的保存路径。
            certificate_path (str): 终端数字证书的保存路径（即证书链中的第一个证书）。
            certificate_chain_path (str): 完整的数字证书链的保存路径。
            common_password (str, optional): 如果指定，将作为账户私钥和证书私钥的统一加密密码。
        Returns:
            bool: 如果所有文件都保存成功，返回 True，否则返回 False。
        """
        all_success = True

        # 保存账户私钥
        if self._account_key:
            if not self._save_key_to_file(self._account_key, account_key_path, common_password):
                all_success = False
        else:
            logger.warning("[保存密钥]账户私钥不存在，跳过保存。")
            all_success = False

        # 保存证书私钥
        if self._cert_key:
            if not self._save_key_to_file(self._cert_key, cert_key_path, common_password):
                all_success = False
        else:
            logger.warning("[保存密钥]证书私钥不存在，跳过保存。")
            all_success = False

        # 保存终端数字证书
        cert_saved = False
        if self.certificate: # 使用 self.certificate 属性获取终端证书
            try:
                os.makedirs(os.path.dirname(certificate_path), exist_ok=True)
                with open(certificate_path, "wb") as f:
                    f.write(self.certificate) # 保存终端证书
                logger.info(f"[保存证书]保存终端数字证书成功，位置：{certificate_path}。")
                cert_saved = True
            except Exception as e:
                logger.error(f"[保存证书]保存终端数字证书失败，位置：{certificate_path}，错误：{e}")
        else:
            logger.warning("[保存证书]终端数字证书不存在，跳过保存。")
        if not cert_saved:
            all_success = False

        # 保存完整的数字证书链
        chain_saved = False
        if self._certificate_chain:
            try:
                os.makedirs(os.path.dirname(certificate_chain_path), exist_ok=True)
                with open(certificate_chain_path, "wb") as f:
                    f.write(self._certificate_chain) # 保存完整的证书链
                logger.info(f"[保存证书]保存数字证书链成功，位置：{certificate_chain_path}。")
                chain_saved = True
            except Exception as e:
                logger.error(f"[保存证书]保存数字证书链失败，位置：{certificate_chain_path}，错误：{e}")
        else:
            logger.warning("[保存证书]数字证书链不存在，跳过保存。")
        if not chain_saved:
            all_success = False
            
        return all_success

