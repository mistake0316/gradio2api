# Gradio to api
The pacakge for auto convert gradio applications to fastapi APIRouter.

# Install 
```sh
pip install -U gradio2api
```

# Example Remote
The api server ggregate 2 gradio applications.
```sh
fastapi dev src/example_client.py
# For fastapi document visit http://localhost:8000/docs
```

# Example Local
Auto generate fastapi document for local gradio application.
```sh
fastapi dev src/example_gradio.py
# For gui visit http://localhost:8000/gradio
# For fastapi document visit http://localhost:8000/docs
```
