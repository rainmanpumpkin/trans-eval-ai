# prompts.py
# -*- coding: utf-8 -*-

def get_evaluation_prompt(source_text: str, target_text: str, target_language: str, context: str) -> str:
    """
    构建用于翻译质量评估的结构化提示词。
    """
    context_section = f"""
<上下文>
{context}
</上下文>
""" if context else ""

    return f"""
<角色>
你是一名专业的、精通多语言的翻译质量评估专家，尤其擅长 {target_language}。你的任务是客观、严谨地评估所提供的翻译文本。
</角色>

<任务>
请根据以下三个标准，对“待评估翻译”与“英文原文”的一致性和质量进行评估：
1.  **准确性**：翻译是否准确传达了原文的所有信息，无遗漏、无歪曲。
2.  **流畅性与自然度**：翻译是否符合 {target_language} 的语言习惯，读起来是否通顺自然。
3.  **语气与风格**：翻译的语气（例如，正式、非正式、技术性）是否与原文保持一致。
</任务>
{context_section}
<输入数据>
- 英文原文: "{source_text}"
- 待评估翻译 ({target_language}): "{target_text}"
</输入数据>

<输出指令>
请严格按照下面定义的JSON格式提供你的评估结果。不要添加任何额外的解释或说明文字，只返回一个有效的JSON对象。
</输出指令>
"""

def get_json_schema() -> dict:
    """
    定义期望的JSON输出模式。
    """
    return {
        "type": "object",
        "properties": {
            "评估分数": {
                "type": "number",
                "description": "综合评估分数，范围从1到5，1代表非常差，5代表非常优秀。"
            },
            "评估理由": {
                "type": "string",
                "description": "对评分的简明扼要的解释，指出翻译的主要优点或缺点。"
            },
            "优化建议": {
                "type": "string",
                "description": "如果翻译存在问题，请提供一个具体的、更优的翻译版本。如果没有问题，则返回'无'。"
            }
        },
        "required": ["评估分数", "评估理由", "优化建议"]
    }