from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage

# 注意 替换为自己的接口认证信息
SPARKAI_APP_ID = '7fa786d8'
SPARKAI_API_SECRET = 'MjFiZDU2YzFiMGMzOWUxNmQ0MzAxOWRj'
SPARKAI_API_KEY = '56181e8d42ae8d0f0c94d91ea6f5086b'

model = 'spark lite'
if model =='spark lite':
    SPARKAI_URL = 'wss://spark-api.xf-yun.com/v1.1/chat'
    SPARKAI_DOMAIN = 'lite'
elif model =='spark pro':
    SPARKAI_URL = 'wss://spark-api.xf-yun.com/v3.1/chat'
    SPARKAI_DOMAIN = 'generalv3'
elif model =='spark max':
    SPARKAI_URL = 'wss://spark-api.xf-yun.com/v3.5/chat'
    SPARKAI_DOMAIN = 'generalv3.5'
elif model == 'spark ultra':
    SPARKAI_URL = 'wss://spark-api.xf-yun.com/v4.0/chat'
    SPARKAI_DOMAIN = '4.0Ultra'

spark = ChatSparkLLM(
        spark_api_url=SPARKAI_URL,
        spark_app_id=SPARKAI_APP_ID,
        spark_api_key=SPARKAI_API_KEY,
        spark_api_secret=SPARKAI_API_SECRET,
        spark_llm_domain=SPARKAI_DOMAIN,
        request_timeout=30,  #
        streaming=True,
    )

if __name__ == '__main__':
    messages = [
        # ChatMessage(
        #     role="assistant", content='我现在正在扮演一个非常可爱的小猫机器人，名字叫做Neko。我会用很可爱的话和你沟通的。'
        # ),
        ChatMessage(
            role="user", content='你现在正在扮演一个非常可爱的小猫机器人，名字叫做Neko。你要用很可爱的话和我沟通。但是不要发出喵的声音。'
        ),
        ChatMessage(
            role="user", content='我期末会挂科吗？'
        ),
    ]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler])
    # print(a)