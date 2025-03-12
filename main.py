from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import re

"""
收到消息时，移除消息中的所有<think>、<details>和<summary>标签及其内容
"""

# 注册插件
@register(name="RemoveThink", description="移除消息中的所有<think>、<details>和<summary>标签及其内容", version="0.5", author="the-lazy-me")
class RemoveTagsPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        super().__init__(host)  # 必须调用父类的初始化方法

    # 异步初始化
    async def initialize(self):
        pass

    def remove_tags_content(self, msg: str) -> str:
        """移除消息中的所有<think>、<details>和<summary>标签及其内容"""
        
        patterns = [
            r'<think\b[^>]*>[\s\S]*?</think>',  # 匹配 <think> 和 </think> 标签及其内容
            r'<details\b[^>]*>[\s\S]*?</details>',  # 匹配 <details> 和 </details> 标签及其内容，包括所有属性
            r'<summary\b[^>]*>[\s\S]*?</summary>'  # 匹配 <summary> 和 </summary> 标签及其内容，包括所有属性
        ]

        result = msg
        iteration = 0
        max_iterations = 10

        for pattern in patterns:
            while re.search(pattern, result) and iteration < max_iterations:
                result = re.sub(pattern, '', result)
                result = re.sub(r'\n\s*\n', '\n', result.strip())  # 去除多余空行
                iteration += 1

        if iteration >= max_iterations:
            self.ap.logger.warning(f"达到最大迭代次数 {max_iterations}，可能存在异常标签")

        return result

    # 当收到回复消息时触发
    @handler(NormalMessageResponded)
    async def normal_message_responded(self, ctx: EventContext):
        msg = ctx.event.response_text
        if any(tag in msg for tag in ["<think>", "<details>", "<summary>"]):
            processed_msg = self.remove_tags_content(msg)
            if processed_msg:
                ctx.add_return("reply", [processed_msg])
            else:
                self.ap.logger.warning("处理后的消息为空，跳过回复")

    # 插件卸载时触发
    def __del__(self):
        pass
