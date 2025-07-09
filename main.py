# main.py
# -*- coding: utf-8 -*-

import argparse
import os
from dotenv import load_dotenv
from core.file_handler import FileHandler
from core.batch_processor import BatchProcessor
import logging

#... (日志配置)...

def main():
    """主函数，处理命令行参数并协调整个评估流程。"""
    load_dotenv()  # 从.env文件加载环境变量

    parser = argparse.ArgumentParser(description="AI驱动的多语言翻译质量评估工具。")
    parser.add_argument("--input-file", required=True, help="输入的Excel或CSV文件路径。")
    parser.add_argument("--output-file", required=True, help="输出结果的Excel或CSV文件路径。")
    parser.add_argument("--source-col", required=True, help="包含英文原文的列名。")
    parser.add_argument("--target-cols", required=True, nargs='+', help="一个或多个包含目标语言翻译的列名。")
    parser.add_argument("--context", default="", help="（可选）为AI提供评估上下文，以提高准确性。")

    args = parser.parse_args()

    # 检查API密钥是否存在
    if not os.getenv("GOOGLE_API_KEY"):
        logging.error("错误：未找到 GOOGLE_API_KEY 环境变量。请在.env 文件中设置。")
        return

    #... (后续流程调用)...

if __name__ == "__main__":
    main()

# main.py (续)
def main():
    #... (参数解析)...
    try:
        file_handler = FileHandler()
        batch_processor = BatchProcessor(os.getenv("GOOGLE_API_KEY"), config.MODEL_NAME)

        logging.info(f"正在从 '{args.input_file}' 读取数据...")
        df = file_handler.read_spreadsheet(args.input_file)
        
        # 验证列名是否存在
        for col in [args.source_col] + args.target_cols:
            if col not in df.columns:
                logging.error(f"错误：输入文件中未找到列 '{col}'。")
                return

        jsonl_path = "temp_batch_requests.jsonl"
        logging.info(f"正在创建请求文件 '{jsonl_path}'...")
        file_handler.create_jsonl_request_file(df, args.source_col, args.target_cols, args.context, config.MODEL_NAME, jsonl_path)

        results = batch_processor.run_batch_job(jsonl_path, config.POLLING_INTERVAL_SECONDS, config.MAX_WAIT_SECONDS)

        logging.info("正在将评估结果合并回数据表...")
        result_df = batch_processor.merge_results_to_df(df.copy(), results)

        logging.info(f"正在将最终结果写入 '{args.output_file}'...")
        file_handler.write_results(result_df, args.output_file)

        logging.info("所有任务已成功完成！")

    except (ValueError, FileNotFoundError, RuntimeError, TimeoutError) as e:
        logging.error(f"处理过程中发生严重错误: {e}")
    finally:
        # 清理临时文件
        if os.path.exists("temp_batch_requests.jsonl"):
            os.remove("temp_batch_requests.jsonl")

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=)
    main()