from fastapi import APIRouter, Request, Response, Depends, HTTPException, status

from .logger import get_logger
from .docker_client import DockerClient, get_docker_client
from .repository import SERVICES
from .schemas import Service

router = APIRouter(
    prefix="/service",
    tags=["service"],
)


@router.post("/run")
async def run_service(
    request: Request,
    docker_client: DockerClient = Depends(get_docker_client),
    image_name: str = 'aldinokemal2104/go-whatsapp-web-multidevice:latest',
    service_name: str = 'go-whatsapp-web-multidevice',
    external_port: int = 8080,
    internal_port: int|None = None,
):
    """
    Start a service
    """
    with get_logger(task='docker service', request=request, service_name=image_name) as logger:
        try:
            logger.info(f'Starting service {service_name}')
            if image_name in [service.image_aliases for service in SERVICES]:
                service = next(service for service in SERVICES if image_name in service.image_aliases)
                logger.info(f'Using existing service with nickname {service.nickname}')
                if internal_port:
                    service.main_internal_port = internal_port
                service.main_external_port = external_port
                service.name = service_name
            else:
                service = Service(
                    image=image_name,
                    name=service_name,
                    internal_port=internal_port,
                    main_external_port=external_port,
                )
            docker_client.service_up(service)
        except Exception as e:
            logger.exception(f'Failed to start service')
            status_code = status.HTTP_409_CONFLICT if 'Port is already allocated' in str(e) or 'Service already exists' in str(e) else status.HTTP_500_INTERNAL_SERVER_ERROR
            raise HTTPException(status_code=status_code, detail=str(e))
        
@router.get("/go-whatsapp/run")
async def run_go_whatsapp_service(
    request: Request,
    docker_client: DockerClient = Depends(get_docker_client),
    custom_image: str|None = None,
    service_name: str = 'go-whatsapp-web-multidevice',
    external_port: int = 3000,
):
    with get_logger(task='docker service', request=request, service_name=service_name) as logger:
        try:
            logger.info(f'Starting service {service_name}')
            if not custom_image:
                service = SERVICES[0]
                service.name = service_name
                service.main_external_port = external_port
            else:
                if custom_image in [service.image_aliases for service in SERVICES]:
                    service = next(service for service in SERVICES if custom_image in service.image_aliases)
                    logger.info(f'Using existing service with nickname {service.nickname}')
                    service.name = service_name
                    service.main_external_port = external_port
                else:
                    raise ValueError(f'Image {custom_image} not found in repository')
            docker_client.service_up(service)
        except Exception as e:
            logger.exception(f'Failed to start service')
            status_code = status.HTTP_409_CONFLICT if 'Port is already allocated' in str(e) or 'Service already exists' in str(e) else status.HTTP_500_INTERNAL_SERVER_ERROR
            status_code = status.HTTP_404_NOT_FOUND if 'Image' in str(e) else status_code
            raise HTTPException(status_code=status_code, detail=str(e))
        
@router.get("/list")
async def list_service(
    request: Request,
    docker_client: DockerClient = Depends(get_docker_client),
):
    """
    Search for a service
    """
    with get_logger(task='docker service', request=request) as logger:
        try:
            logger.info(f'Searching for service')
            return docker_client.list_services()
        except Exception as e:
            logger.exception(f'Failed to search for service')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
@router.get("/stop")
async def stop_service(
    request: Request,
    service_name: str,
    docker_client: DockerClient = Depends(get_docker_client)
):
    """
    Stop a service
    """
    with get_logger(task='docker service', request=request) as logger:
        try:
            logger.info(f'Stopping service {service_name}')
            docker_client.service_down(service_name)
        except Exception as e:
            logger.exception(f'Failed to stop service')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))