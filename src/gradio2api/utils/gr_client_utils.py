from gradio_client import Client
from retry import retry

# For trigger the reload funciton at server
@retry(tries=5, delay=2)
def LoadGradioClient(src:str,*args, **kwargs)->Client:
  return Client(src, *args, **kwargs)