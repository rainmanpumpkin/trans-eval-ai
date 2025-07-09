# core/batch_processor.py
# -*- coding: utf-8 -*-

import google.generativeai as genai
import time
import os
import logging
import json
import pandas as pd

class BatchProcessor:
    """封装与Google Gemini Batch API的交互逻辑。"""

    def __init__(self, api_key: str, model_name: str):
        genai.configure(api_key=api_key)
        self.model_name = model_name

    def run_batch_job(self, jsonl_path: str, polling_interval: int, max_wait: int) -> list:
        """
        执行完整的批处理流程：上传、创建、轮询、下载、解析。
        [11, 20]
        """
        # 1. 上传文件
        logging.info(f"正在上传请求文件: {jsonl_path}...")
        uploaded_file = genai.upload_file(path=jsonl_path)
        logging.info(f"文件上传成功: {uploaded_file.name}")

        # 2. 创建批处理作业
        logging.info(f"正在使用模型 '{self.model_name}' 创建批处理作业...")
        batch_job = genai.create_batch_job(
            model=f"models/{self.model_name}",
            requests=uploaded_file
        )
        logging.info(f"批处理作业已创建: {batch_job.name}")

        # 3. 轮询作业状态
        start_time = time.time()
        while time.time() - start_time < max_wait:
            job_status = genai.get_batch_job(name=batch_job.name)
            logging.info(f"作业 '{job_status.name}' 当前状态: {job_status.state.name}")
            
            if job_status.state.name == "JOB_STATE_SUCCEEDED":
                logging.info("作业成功完成！")
                # 4. 下载并解析结果
                return self._download_and_parse_results(job_status)
            elif job_status.state.name in:
                logging.error(f"作业失败或被取消。错误详情: {job_status.error}")
                raise RuntimeError(f"批处理作业失败: {job_status.error}")
            
            time.sleep(polling_interval)
        
        raise TimeoutError("批处理作业等待超时。")

    def _download_and_parse_results(self, job_status) -> list:
        """下载结果文件并解析为字典列表。"""
        logging.info("正在下载结果文件...")
        result_file_meta = job_status.result_file
        result_file_content = genai.download_file(name=result_file_meta.name).read()
        
        results =
        # 结果文件也是JSONL格式
        for line in result_file_content.decode('utf-8').splitlines():
            results.append(json.loads(line))
        
        logging.info(f"成功下载并解析了 {len(results)} 条结果。")
        return results

    def merge_results_to_df(self, df: pd.DataFrame, results: list) -> pd.DataFrame:
        """将API返回的结果合并回原始的DataFrame。"""
        # 创建用于存放结果的临时字典
        results_map = {}
        for res in results:
            if res.get('response') and 'candidates' in res['response']:
                try:
                    # 解析JSON响应内容
                    content = json.loads(res['response']['candidates']['content']['parts']['text'])
                    results_map[res['key']] = content
                except (json.JSONDecodeError, KeyError, IndexError) as e:
                    logging.warning(f"无法解析请求 '{res['key']}' 的响应: {e}")
                    results_map[res['key']] = {"评估分数": "解析错误", "评估理由": str(e), "优化建议": ""}
            else:
                 results_map[res['key']] = {"评估分数": "API错误", "评估理由": res.get('error', {}).get('message', '未知错误'), "优化建议": ""}


        # 将结果映射回DataFrame
        for index, row in tqdm(df.iterrows(), total=df.shape, desc="合并评估结果"):
            for lang_col in df.columns: # 检查所有可能的语言列
                request_key = f"row_{index}_lang_{lang_col}"
                if request_key in results_map:
                    result_data = results_map[request_key]
                    df.loc[index, f"{lang_col}_评估分数"] = result_data.get("评估分数")
                    df.loc[index, f"{lang_col}_评估理由"] = result_data.get("评估理由")
                    df.loc[index, f"{lang_col}_优化建议"] = result_data.get("优化建议")
        
        return df