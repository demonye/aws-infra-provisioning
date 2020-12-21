from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def read_root():
    return {'Hello': 'World'}


@app.get('/{name:str}')
def greeting(name):
    return {'Hello': name}


@app.get('/version')
def version():
    with open('VERSION') as fp:
        version = fp.read().strip()
    return {'version': version}
