# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from typing import List, Dict, Any, Optional

from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
# from alibabacloud_credentials.client import Client as CredentialClient # 不再需要CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_tea_util import models as util_models
from loguru import logger

class AliyunDNSManager:
    """
    阿里云 DNS 解析记录管理类
    """
    def __init__(self, access_key_id: str, access_key_secret: str, endpoint: str):
        """
        初始化 AliyunDNSManager.
        :param access_key_id: 阿里云 AccessKey ID.
        :param access_key_secret: 阿里云 AccessKey Secret.
        :param endpoint: 阿里云 API Endpoint.
        """
        if not all([access_key_id, access_key_secret, endpoint]):
            raise ValueError("AccessKey ID, Secret 和 Endpoint 不能为空。")
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.endpoint = endpoint
        logger.info("AliyunDNSManager 初始化成功。")

    def create_client(self) -> Alidns20150109Client:
        """
        使用提供的凭证初始化阿里云 DNS 客户端。
        @return: Alidns20150109Client
        @throws Exception
        """
        config = open_api_models.Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret
        )
        config.endpoint = self.endpoint
        return Alidns20150109Client(config)

    def add_record(
        self,
        domain_name: str,
        rr: str,
        record_type: str,
        value: str,
        ttl: int = 600,
        priority: int = None,
        line: str = 'default'
    ) -> str:
        """
        添加解析记录
        :param domain_name: 域名名称
        :param rr: 主机记录，例如 www, @, * 等
        :param record_type: 解析记录类型，例如 A, CNAME, MX, TXT 等
        :param value: 记录值
        :param ttl: 解析生效时间，默认为 600 秒
        :param priority: MX 记录的优先级，取值范围：[1,50]，非 MX 记录类型可不填
        :param line: 解析线路，默认为 default
        :return: 解析记录的 ID
        :raises Exception: 如果添加失败则抛出异常
        """
        client = self.create_client()
        add_domain_record_request = alidns_20150109_models.AddDomainRecordRequest(
            lang='zh',  # 设置请求和接收消息的语言类型为中文
            domain_name=domain_name,
            rr=rr,
            type=record_type,
            value=value,
            ttl=ttl,
            priority=priority,
            line=line
        )
        runtime = util_models.RuntimeOptions()

        record_info = f"域名={domain_name}, 主机={rr}, 类型={record_type}, 值={value}, TTL={ttl}, 优先级={priority if priority is not None else 'N/A'}, 线路={line}"

        try:
            response = client.add_domain_record_with_options(add_domain_record_request, runtime)
            logger.info(f"[添加解析]添加解析记录成功: {record_info}, RecordId={response.body.record_id}")
            return response.body.record_id
        except Exception as error:
            logger.error(f"[添加解析]添加解析记录失败: {record_info}, 错误={error.message}")
            raise  # 重新抛出异常，以便调用者处理

    def delete_sub_records(
        self,
        domain_name: str,
        rr: str,
        record_type: str = None
    ) -> None:
        """
        删除指定子域名的所有解析记录列表。
        如果被删除的解析记录中存在锁定解析，则该锁定解析不会被删除。
        :param domain_name: 域名名称
        :param rr: 主机记录，例如 www, @, * 等
        :param record_type: 解析记录类型，例如 A, CNAME, MX, TXT 等。如果不填写，则删除子域名对应的全部解析记录类型。
        :return: 被删除的解析记录总数
        :raises Exception: 如果删除失败则抛出异常
        """
        client = self.create_client()
        delete_sub_domain_records_request = alidns_20150109_models.DeleteSubDomainRecordsRequest(
            lang='zh',  # 设置请求和接收消息的语言类型为中文
            domain_name=domain_name,
            rr=rr,
            type=record_type
        )
        runtime = util_models.RuntimeOptions()
        record_info = f"域名={domain_name}, 主机={rr}, 类型={record_type if record_type else '所有类型'}"


        try:
            response = client.delete_sub_domain_records_with_options(delete_sub_domain_records_request, runtime)
            total_count = int(response.body.total_count)
            logger.info(f"[删除解析]删除子域名解析记录成功: {record_info}, 删除了 {total_count} 条记录。")
        except Exception as error:
            logger.error(f"[删除解析]删除子域名解析记录失败: {record_info}, 错误={error.message}")
            raise  # 重新抛出异常，以便调用者处理

    def update_record(
        self,
        record_id: str,
        rr: str,
        record_type: str,
        value: str,
        ttl: int = None,
        priority: int = None,
        line: str = None
    ) -> None:
        """
        修改解析记录
        :param record_id: 解析记录的 ID
        :param rr: 主机记录，例如 www, @, * 等
        :param record_type: 解析记录类型，例如 A, CNAME, MX, TXT 等
        :param value: 记录值
        :param ttl: 解析生效时间，默认为 600 秒（不传则使用原值）
        :param priority: MX 记录的优先级，取值范围：[1,50]，非 MX 记录类型可不填（不传则使用原值）
        :param line: 解析线路，默认为 default（不传则使用原值）
        :return: 解析记录的 ID
        :raises Exception: 如果修改失败则抛出异常
        """
        client = self.create_client()
        update_domain_record_request = alidns_20150109_models.UpdateDomainRecordRequest(
            lang='zh',  # 设置请求和接收消息的语言类型为中文
            record_id=record_id,
            rr=rr,
            type=record_type,
            value=value,
            ttl=ttl,
            priority=priority,
            line=line
        )
        runtime = util_models.RuntimeOptions()

        record_info = f"RecordId={record_id}, 主机={rr}, 类型={record_type}, 新值={value}, TTL={ttl if ttl is not None else '保持原值'}, 优先级={priority if priority is not None else '保持原值'}, 线路={line if line is not None else '保持原值'}"

        try:
            # response = client.update_domain_record_with_options(update_domain_record_request, runtime)
            # 注意：此方法直接通过 record_id 更新，不直接知道 domain_name。
            # 如果需要 domain_name，需要先查询 record_id 获取其所在的 domain_name，但通常 upsert_record 会提供更完整的上下文。

            client.update_domain_record_with_options(update_domain_record_request, runtime)
            logger.info(f"[更新解析]更新解析记录成功: {record_info}")

        except Exception as error:
            logger.error(f"[更新解析]更新解析记录失败: {record_info}, 错误={error.message}")
            raise  # 重新抛出异常，以便调用者处理

    def list_records(
        self,
        domain_name: str,
        page_number: int = None,
        page_size: int = None,
        rr_key_word: str = None,
        type_key_word: str = None,
        value_key_word: str = None,
        order_by: str = None,
        direction: str = None,
        search_mode: str = None,
        group_id: int = None,
        record_type: str = None,
        line: str = None,
        status: str = None
    ) -> Dict[str, Any]:
        """
        根据传入参数获取指定主域名的所有解析记录列表
        :param domain_name: 域名名称
        :param page_number: 当前页数，起始值为 1，默认为 1
        :param page_size: 分页查询时设置的每页行数，最大值 500，默认为 20
        :param rr_key_word: 主机记录的关键字，按照 RRKeyWord（前后模糊匹配）模式搜索，不区分大小写
        :param type_key_word: 解析类型的关键字，按照全匹配搜索，不区分大小写
        :param value_key_word: 记录值的关键字，按照 ValueKeyWord（前后模糊匹配）模式搜索，不区分大小写
        :param order_by: 排序方式，例如：default (按照解析添加的时间从新到旧排序)
        :param direction: 排序方向，取值范围：DESC、ASC。默认为：DESC
        :param search_mode: 搜索模式，取值：LIKE/EXACT/ADVANCED/COMBINATION
        :param group_id: 域名分组 ID
        :param record_type: 解析记录类型，例如 A, CNAME, MX, TXT 等
        :param line: 解析线路，例如 default, cn_mobile_anhui 等
        :param status: 解析记录状态。取值：Enable (启用), Disable (禁用)
        :return: 包含解析记录列表、总数、当前页数、每页行数的字典
        :raises Exception: 如果查询失败则抛出异常
        """
        client = self.create_client()
        describe_domain_records_request = alidns_20150109_models.DescribeDomainRecordsRequest(
            lang='zh',  # 设置请求和接收消息的语言类型为中文
            domain_name=domain_name,
            page_number=page_number,
            page_size=page_size,
            rrkey_word=rr_key_word,
            type_key_word=type_key_word,
            value_key_word=value_key_word,
            order_by=order_by,
            direction=direction,
            search_mode=search_mode,
            group_id=group_id,
            type=record_type,  # 注意这里参数名是'type'而不是'record_type'
            line=line,
            status=status
        )
        runtime = util_models.RuntimeOptions()
        record_info = f"域名={domain_name}, 主机关键字={rr_key_word if rr_key_word else 'N/A'}, 类型关键字={type_key_word if type_key_word else 'N/A'}, 值关键字={value_key_word if value_key_word else 'N/A'}, 页面大小={page_size if page_size else '默认'}, 页码={page_number if page_number else '默认'}"
        try:
            response = client.describe_domain_records_with_options(describe_domain_records_request, runtime)
            records = [record.to_map() for record in response.body.domain_records.record] if response.body.domain_records and response.body.domain_records.record else []
            result = {
                "TotalCount": int(response.body.total_count) if response.body.total_count else 0,
                "PageSize": int(response.body.page_size) if response.body.page_size else 0,
                "PageNumber": int(response.body.page_number) if response.body.page_number else 0,
                "DomainRecords": records
            }
            logger.info(f"[精确查询]查询解析记录成功: {record_info}, 共 {result['TotalCount']} 条记录。")
            return result
        except Exception as error:
            logger.error(f"[精确查询]查询解析记录失败: {record_info}, 错误={error.message}")
            raise  # 重新抛出异常，以便调用者处理

    def check_record(
        self,
        domain_name: str,
        rr: str,
        record_type: str,
        value: str = None
    ) -> Optional[str]:
        """
        检查是否存在特定的解析记录。
        如果存在解析记录则返回 RecordId，不存在则返回 None。
        如果用户使用可选参数：value，则需要对比解析记录的值。
        :param domain_name: 域名名称，例如：xiaoshae.cn
        :param rr: 主机记录，例如：www
        :param record_type: 解析记录类型，例如：A
        :param value: (可选) 记录值，例如：127.0.0.1。如果提供，将对比解析记录的值。
        :return: RecordId 如果找到匹配的记录，None 否则。
        :raises Exception: 如果查询失败则抛出异常
        """
        try:
            query_result = self.list_records(
                domain_name=domain_name,
                rr_key_word=rr,
                type_key_word=record_type,
                page_size=10 # 只需要找到一个匹配项，无需查询全部
            )

            record_info = f"域名={domain_name}, 主机={rr}, 类型={record_type}, 值={value if value else 'N/A'}"

            if query_result and query_result['DomainRecords']:
                for record in query_result['DomainRecords']:
                    # 严格匹配 rr 和 type
                    if record.get('RR') == rr and record.get('Type') == record_type:
                        # 如果没有提供 value 参数，只要找到匹配的 rr 和 type 就返回 True
                        if value is None:
                            logger.info(f"[快速查询]查询到解析记录: {record_info}, 记录值={record.get('Value')}, RecordId={record.get('RecordId')}")
                            return record.get('RecordId') # 返回 RecordId
                    
                        # 如果提供了 value 参数，需要对比记录值
                        elif record.get('Value') == value:
                            logger.debug(f"[快速查询]查询到解析记录（值匹配）: {record_info}, 记录值={record.get('Value')}, RecordId={record.get('RecordId')}")
                            return record.get('RecordId') # 返回 RecordId

            logger.info(f"[快速查询]未查询到解析记录: {record_info}")
            return None # 未找到匹配记录时返回 None

        except Exception as e:
            logger.error(f"[快速查询]查询解析记录时发生错误: {record_info}, 错误={e}")
            raise # 重新抛出异常

    def upsert_record(
        self,
        domain_name: str,
        rr: str,
        record_type: str,
        value: str,
        ttl: int = None,
        priority: int = None,
        line: str = None
    ) -> Optional[str]:
        """
        添加或更新解析记录。
        先查询是否存在对应解析记录，如果存在则使用更新函数进行更新，如果不存在，则使用新增函数。
        :param domain_name: 域名名称，如 xiaoshae.cn
        :param rr: 主机记录，如 www, @
        :param record_type: 解析记录类型，如 A, CNAME
        :param value: 记录值，如 127.0.0.1
        :param ttl: 解析生效时间，默认为 600 秒
        :param priority: MX 记录的优先级，取值范围：[1,50]，非 MX 记录类型可不填
        :param line: 解析线路，默认为 default
        :return: 新增或更新成功返回 RecordId，无需更新或失败返回 None
        :raises Exception: 如果操作失败则抛出异常
        """
        record_info = f"域名={domain_name}, 主机={rr}, 类型={record_type}, 值={value}, TTL={ttl if ttl is not None else 'N/A'}, 优先级={priority if priority is not None else 'N/A'}, 线路={line if line is not None else 'N/A'}"

        try:
            # 第一次查询：检查是否存在主机记录和类型匹配的记录（不比较值），并获取 RecordId
            record_id_general = self.check_record(
                domain_name=domain_name,
                rr=rr,
                record_type=record_type
            )

            # 第二次查询：检查是否存在主机记录、类型和值都匹配的记录，并获取 RecordId
            record_id_exact_value = self.check_record(
                domain_name=domain_name,
                rr=rr,
                record_type=record_type,
                value=value
            )

            if record_id_exact_value: # 判断是否存在完全匹配的记录
                # 如果存在完全匹配的记录，则表示已是最新，无需更新
                logger.info(f"[添加或更新解析]解析记录已是最新，无需更新。{record_info}")
                return record_id_exact_value # 返回现有 RecordId

            elif record_id_general: # 判断是否存在同主机记录和类型但值不匹配的记录
                # 如果存在同主机记录和类型但值不匹配的记录，则执行更新
                # 直接使用 record_id_general 进行更新，无需再次查询
                self.update_record(
                    record_id=record_id_general, # 使用获取到的 RecordId
                    rr=rr,
                    record_type=record_type,
                    value=value,
                    ttl=ttl,
                    priority=priority,
                    line=line
                )
                logger.info(f"[添加或更新解析]更新解析记录成功。{record_info}")
                return record_id_general # 返回更新的 RecordId
            else:
                # 如果不存在任何匹配的记录，则执行新增
                new_record_id = self.add_record( # 捕获新增的 RecordId
                    domain_name=domain_name,
                    rr=rr,
                    record_type=record_type,
                    value=value,
                    ttl=ttl,
                    priority=priority,
                    line=line
                )
                logger.info(f"[添加或更新解析]添加解析记录成功。{record_info}")
                return new_record_id # 返回新增的 RecordId

        except Exception as e:
            logger.error(f"[添加或更新解析]添加或更新解析记录失败: {record_info}, 错误={e}")
            raise # 重新抛出异常

