# core/file_handler.py
# -*- coding: utf-8 -*-

import pandas as pd
import json
from tqdm import tqdm
from prompts import get_evaluation_prompt, get_json_schema

class FileHandler:
    """处理文件的读取、转换和写入。"""

    def read_spreadsheet(self, file_path: str) -> pd.DataFrame:
        """根据文件扩展名读取CSV或Excel文件。"""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path)
        else:
            raise ValueError("不支持的文件格式，请使用.csv 或.xlsx 文件。")

    def create_jsonl_request_file(self, df: pd.DataFrame, source_col: str, target_cols: list, context: str, model_name: str, output_path: str):
        """
        根据DataFrame创建Google Batch API所需的JSONL请求文件。
        [7, 20, 21]
        """
        requests =
        # 使用tqdm显示本地文件处理进度
        for index, row in tqdm(df.iterrows(), total=df.shape, desc="准备API请求"):
            for lang_col in target_cols:
                if pd.notna(row[source_col]) and pd.notna(row[lang_col]):
                    # 为每个评估任务创建一个唯一的key
                    request_key = f"row_{index}_lang_{lang_col}"
                    
                    prompt = get_evaluation_prompt(
                        source_text=row[source_col],
                        target_text=row[lang_col],
                        target_language=lang_col,
                        context=context
                    )
                    
                    # 构建符合Gemini Batch API格式的请求
                    api_request = {
                        "key": request_key,
                        "request": {
                            "contents": [{"parts": [{"text": prompt}]}],
                            "generationConfig": {
                                "response_mime_type": "application/json",
                                "responseSchema": get_json_schema()
                            }
                        }
                    }
                    requests.append(api_request)
        
        # 将请求列表写入JSONL文件
        with open(output_path, 'w', encoding='utf-8') as f:
            for req in requests:
                f.write(json.dumps(req, ensure_ascii=False) + '\n')

    def write_results(self, df: pd.DataFrame, file_path: str):
        """将带有评估结果的DataFrame写入文件。"""
        if file_path.endswith('.csv'):
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
        elif file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)

# file_handler.py (部分)
api_request = {
    "key": request_key,
    "request": {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "response_mime_type": "application/json",
            "responseSchema": get_json_schema() # <-- 强制执行JSON输出
        }
    }
}