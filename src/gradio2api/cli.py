from fastapi import FastAPI
from .clients_aggregator import create_gradio2api
import argparse
import uvicorn
import json
import gradio as gr

def cli_remote():
  parser = argparse.ArgumentParser(
    description="""\
    This is the command line tool for gradio2api remote server, please use `gardio2api.Aggregator` detail setting.
    Sample command:
    ```sh
    gradio2api SinDarSoup/TheWorld;/TheWorld 
    ```
    """,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
  )
  parser.add_argument("servers", nargs="*", type=str, help="""server configs, format "{uri};{router}". (e.g. "http://localhost:7860;/local", "SinDarSoup/audio_tagging_mit;") """)
  parser.add_argument("--gradio_client_config_path", type=str, default=None, help="The json file path of gradio_client.")
  parser.add_argument("--host", type=str, default="127.0.0.1", help="The host for uvicorn.")
  parser.add_argument("--port", type=int, default=8000, help="The port for uvicorn.")

  group = parser.add_mutually_exclusive_group(required=False)
  group.add_argument('--allow-error', dest='error_allowed', action='store_true', help="Allow error")
  group.add_argument('--not-allow-error', dest='error_allowed', action='store_false', help="Do not allow error")
  parser.set_defaults(error_allowed=True)

  kwargs = parser.parse_args().__dict__
  host = kwargs.pop("host")
  port = kwargs.pop("port")
  
  servers = kwargs.pop("servers")
  kwargs["servers"] = []
  for s in servers:
    ss = s.split(";")
    assert len(ss) <= 2
    if len(ss) == 2:
      uri, prefix = ss
    else:
      uri, prefix = ss[0], ""
    kwargs["servers"].append({
      "uri":uri,
      "prefix":prefix,
    })
  
  app = create_gradio2api(**kwargs)

  uvicorn.run(
    app,
    host=host,
    port=port,
  )

if __name__ == "__main__":
  cli_remote()