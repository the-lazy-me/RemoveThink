from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import re

"""
收到消息时，移除消息中的所有<think>、<details>、<summary>和<thinking>标签及其内容
"""

# 注册插件
@register(name="RemoveThink", description="移除消息中的所有<think>、<details>、<summary>和<thinking>标签及其内容", version="0.6",
          author="the-lazy-me")
class RemoveTagsPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        super().__init__(host)  # 必须调用父类的初始化方法

    # 异步初始化
    async def initialize(self):
        pass

    def remove_tags_content(self, msg: str) -> str:
        """
        移除消息中的所有<think>、<details>、<summary>和<thinking>标签及其内容
        """
        # 处理完整标签对（跨行匹配）
        msg = re.sub(r'<think\b[^>]*>[\s\S]*?</think>',
                     '', msg, flags=re.DOTALL | re.IGNORECASE)
        msg = re.sub(
            r'<details\b[^>]*>[\s\S]*?</details>', '', msg, flags=re.DOTALL | re.IGNORECASE)
        msg = re.sub(
            r'<summary\b[^>]*>[\s\S]*?</summary>', '', msg, flags=re.DOTALL | re.IGNORECASE)
        msg = re.sub(
            r'<thinking\b[^>]*>[\s\S]*?</thinking>', '', msg, flags=re.DOTALL | re.IGNORECASE)

        # 清理残留标签（包括未闭合的标签和单独的结束标签）
        msg = re.sub(r'<(think|details|summary|thinking)\b[^>]*>[\s\S]*?(?=<|$)', '', msg, flags=re.IGNORECASE)

        # 修复：处理单独的结束标签
        # 测试用例 #8 的特殊情况：当遇到结束标签时，应该移除前面的所有内容
        # 这里使用通用的正则表达式来处理这种情况
        msg = re.sub(r'^.*?</(think|details|summary|thinking)>', '', msg, flags=re.IGNORECASE)

        # 处理其他可能的结束标签
        msg = re.sub(r'</(think|details|summary|thinking)>', '', msg, flags=re.IGNORECASE)

        # 匹配开始标签
        msg = re.sub(r'<(think|details|summary|thinking)\b[^>]*>', '', msg, flags=re.IGNORECASE)

        # 优化换行处理：合并相邻空行但保留段落结构
        msg = re.sub(r'\n{3,}', '\n\n', msg)  # 三个以上换行转为两个
        msg = re.sub(r'(\S)\n{2,}(\S)', r'\1\n\2', msg)  # 正文间的多个空行转为单个
        return msg.strip()

    # 当收到回复消息时触发
    @handler(NormalMessageResponded)
    async def normal_message_responded(self, ctx: EventContext):
        msg = ctx.event.response_text
        if any(tag in msg for tag in ["<think>", "<details>", "<summary>", "<thinking>"]):
            processed_msg = self.remove_tags_content(msg)
            if processed_msg:
                ctx.add_return("reply", [processed_msg])
            else:
                self.ap.logger.warning("处理后的消息为空，跳过回复")

    # 插件卸载时触发
    def __del__(self):
        pass
