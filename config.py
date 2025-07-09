# config.py
# -*- coding: utf-8 -*-

# 使用的模型名称，gemini-2.5-flash提供了最佳的成本效益
MODEL_NAME = "gemini-2.5-flash"

# 批处理作业的轮询间隔时间（秒）
POLLING_INTERVAL_SECONDS = 30

# 批处理作业的最大等待时间（秒）
MAX_WAIT_SECONDS = 3600  # 1小时