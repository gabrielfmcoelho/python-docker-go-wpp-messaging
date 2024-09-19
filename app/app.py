from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router
from .settings import app_settings as settings
from .logger import LoggerHandler, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI): # pylint: disable=unused-argument, redefined-outer-name
    app.state.logger_handler = LoggerHandler()
    app.state.logger_handler.log_lifespan()
    yield
    app.state.logger_handler.log_lifespan(shutdown=True)

app = FastAPI(
    title=settings.title,
    description=settings.generate_description(),
    version=settings.version,
    contact=settings.contact,
    lifespan=lifespan,
    root_path=settings.root_path,
    openapi_tags=settings.generate_openapi_tags(),
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allowed_credentials,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

app.include_router(router)

@app.get('/', include_in_schema=False)
async def root():
    with get_logger(task='healthcheck') as logger:
        try:
            return {'message': f'Bem-vindo a {settings.title}! Acesse a documentação em {settings.root_path}{settings.docs_url} ou {settings.root_path}{settings.redoc_url}.'}
        except Exception as e:
            logger.exception('Failed to GET /')
            raise e
        finally:
            logger.info('Successfully GET /')

@app.post('/ping', include_in_schema=False)
async def root_post():
    with get_logger(task='healthcheck') as logger:
        try:
            return {'data': 'pong'}
        except Exception as e:
            logger.exception('Failed to POST /ping')
            raise e
        finally:
            logger.info('Successfully POST /ping')