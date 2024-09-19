from fastapi import APIRouter, Request, Response, Depends, HTTPException, status

from .logger import get_logger
from .docker_client import DockerClient, get_docker_client
from .repository import SERVICES
import requests
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
    internal_port: int = None,
):
    """
    Start a service
    """
    with get_logger(task='docker service', request=request, service_name=image_name) as logger:
        try:
            logger.info(f'Starting service {service_name}')
            if image_name in [alias for service in SERVICES for alias in service.image_aliases]:
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
            status_code = status.HTTP_409_CONFLICT if 'Port is already allocated' in str(
                e) or 'Service already exists' in str(e) else status.HTTP_500_INTERNAL_SERVER_ERROR
            raise HTTPException(status_code=status_code, detail=str(e))


@router.get("/go-whatsapp/run")
async def run_go_whatsapp_service(
    request: Request,
    docker_client: DockerClient = Depends(get_docker_client),
    custom_image: str = 'go-whatsapp-proxy',
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
                if custom_image in [alias for service in SERVICES for alias in service.image_aliases]:
                    service = next(service for service in SERVICES if custom_image in service.image_aliases)
                    # logger.info(f'Using existing service with nickname {service.nickname}')
                    service.name = service_name
                    service.main_external_port = external_port
                else:
                    raise ValueError(
                        f'Image {custom_image} not found in repository')
            docker_client.service_up(service)
        except Exception as e:
            logger.exception(f'Failed to start service')
            status_code = status.HTTP_409_CONFLICT if 'Port is already allocated' in str(
                e) or 'Service already exists' in str(e) else status.HTTP_500_INTERNAL_SERVER_ERROR
            status_code = status.HTTP_404_NOT_FOUND if 'Image' in str(
                e) else status_code
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/fetchInstances")
async def list_service(
    request: Request,
    docker_client: DockerClient = Depends(get_docker_client),
):
    """
    Fetch instances and return them in a JSON format
    """
    with get_logger(task='docker service', request=request) as logger:
        try:
            logger.info(f'Searching for service')
            containers = docker_client.list_services()
            filtered_services = []
            instances = []

            for service in containers:
                service_name = service['name']
                service_status = service['status']

                # Verifica se a chave 'ports' existe e extrai a HostPort
                if 'ports' in service and '3000/tcp' in service['ports']:
                    service_port = service['ports']['3000/tcp'][0]['HostPort']
                    if service_name.startswith("go-whatsapp") and service_status == "running":
                        filtered_services.append(service)

            if filtered_services:
                logger.info(f'Found {len(filtered_services)} services matching the criteria:')
                for service in filtered_services:
                    service_name = service["name"]
                    service_status = service["status"]
                    service_port = service['ports']['3000/tcp'][0]['HostPort']

                    # Faz a requisição para pegar o status da instância
                    instance_status = requests.get(
                        f'http://localhost:{service_port}/app/devices').json()

                    # Verifica o status da instância e monta o JSON conforme solicitado
                    if instance_status['results']:
                        instance_data = {
                            "instanceName": service_name,
                            "status": "open",
                            "number": instance_status['results'][0]['device'],
                            "port": service_port,
                        }
                    else:
                        instance_data = {
                            "instanceName": service_name,
                            "status": "close",
                            "number": None,
                            "port": service_port,
                        }

                    instances.append(instance_data)

                # Retorna a lista de instâncias no formato JSON
                return {"instances": instances}
            else:
                logger.info('No services found matching the criteria.')
                return {"instances": []}

        except Exception as e:
            logger.error(f"Error while searching for services: {str(e)}")
            raise


@router.get("/fetchInstance/{instance_name}")
async def get_instance_status(
    instance_name: str,
    request: Request,
    docker_client: DockerClient = Depends(get_docker_client),
):
    """
    Fetch the status of a specific instance by name and return it in JSON format.
    """
    with get_logger(task='docker service', request=request) as logger:
        try:
            logger.info(f'Searching for service: {instance_name}')
            containers = docker_client.list_services()

            for service in containers:
                service_name = service['name']
                service_status = service['status']

                # Verifica se o nome do serviço corresponde ao solicitado e se está rodando
                if service_name == instance_name and service_status == "running":
                    if 'ports' in service and '3000/tcp' in service['ports']:
                        service_port = service['ports']['3000/tcp'][0]['HostPort']

                        # Faz a requisição para pegar o status da instância
                        instance_status = requests.get(
                            f'http://localhost:{service_port}/app/devices').json()

                        # Verifica o status da instância e monta o JSON conforme solicitado
                        if instance_status['results']:
                            instance_data = {
                                "instanceName": service_name,
                                "status": "open",
                                "number": instance_status['results'][0]['device'],
                                "port": service_port,
                            }
                        else:
                            instance_data = {
                                "instanceName": service_name,
                                "status": "close",
                                "number": None,
                                "port": service_port,
                            }

                        # Retorna os dados da instância
                        return {"instance": instance_data}

            logger.info(f'No service found with the name: {instance_name}')
            return {"instance": None, "message": "No service found with the given name"}

        except Exception as e:
            logger.error(f"Error while searching for the service: {str(e)}")
            raise
