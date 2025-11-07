"""客服机器人主程序"""
import os
import sys
from src.config import Config
from src.chatbot import ChatBot, DeepSeekClient
from src.knowledge_base import KnowledgeBase


def setup_logging(config: Config):
    """设置日志"""
    import logging
    
    log_config = config.get_logging_config()
    log_level = log_config.get('level', 'INFO')
    log_file = log_config.get('file', 'logs/chatbot.log')
    
    # 创建日志目录
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def initialize_bot(config: Config) -> ChatBot:
    """初始化机器人"""
    # 获取配置
    deepseek_config = config.get_deepseek_config()
    kb_config = config.get_knowledge_base_config()
    conv_config = config.get_conversation_config()
    
    # 初始化 DeepSeek 客户端
    deepseek_client = DeepSeekClient(
        api_key=deepseek_config.get('api_key'),
        api_base=deepseek_config.get('api_base'),
        model=deepseek_config.get('model', 'deepseek-chat'),
        max_tokens=deepseek_config.get('max_tokens', 2000),
        temperature=deepseek_config.get('temperature', 0.7)
    )
    
    # 初始化知识库
    knowledge_base = None
    if conv_config.get('enable_knowledge_base', True):
        knowledge_base = KnowledgeBase(
            data_path=kb_config.get('data_path', 'data/knowledge_base.json'),
            similarity_threshold=kb_config.get('similarity_threshold', 0.6),
            max_results=kb_config.get('max_results', 3)
        )
    
    # 初始化机器人
    bot = ChatBot(
        deepseek_client=deepseek_client,
        knowledge_base=knowledge_base,
        system_prompt=conv_config.get('system_prompt', ''),
        max_history=conv_config.get('max_history', 10),
        enable_knowledge_base=conv_config.get('enable_knowledge_base', True)
    )
    
    return bot


def interactive_mode(bot: ChatBot, logger):
    """交互式对话模式"""
    print("\n" + "="*60)
    print("客服机器人已启动！")
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'clear' 清空对话历史")
    print("输入 'search <关键词>' 直接搜索知识库")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("用户: ").strip()
            
            if not user_input:
                continue
            
            # 处理特殊命令
            if user_input.lower() in ['quit', 'exit']:
                print("\n再见！")
                break
            
            if user_input.lower() == 'clear':
                bot.clear_history()
                print("\n对话历史已清空\n")
                continue
            
            if user_input.lower().startswith('search '):
                query = user_input[7:].strip()
                results = bot.search_knowledge_base(query)
                
                if results:
                    print("\n知识库搜索结果：")
                    for i, result in enumerate(results, 1):
                        print(f"\n{i}. 问题: {result['question']}")
                        print(f"   答案: {result['answer']}")
                        print(f"   相似度: {result['similarity']:.2f}")
                else:
                    print("\n未找到相关信息")
                print()
                continue
            
            # 正常对话
            logger.info(f"用户: {user_input}")
            
            print("机器人: ", end="", flush=True)
            
            # 使用流式输出
            for chunk in bot.chat_stream(user_input):
                print(chunk, end="", flush=True)
            
            print("\n")
            logger.info(f"机器人: {bot.get_history()[-1]['content']}")
        
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        
        except Exception as e:
            logger.error(f"错误: {str(e)}")
            print(f"\n发生错误: {str(e)}\n")


def main():
    """主函数"""
    try:
        # 加载配置
        config = Config()
        
        # 设置日志
        logger = setup_logging(config)
        logger.info("客服机器人启动")
        
        # 初始化机器人
        bot = initialize_bot(config)
        logger.info("机器人初始化完成")
        
        # 启动交互模式
        interactive_mode(bot, logger)
    
    except FileNotFoundError as e:
        print(f"\n错误: {str(e)}\n")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n启动失败: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
