import docker
from icecream import ic
import random

from .logger import logger
from .schemas import Service, ServiceStatus
from .settings import app_settings as settings


class DockerClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DockerClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize the logger and setup basic configurations
        """
        if not hasattr(self, 'initialized'):
            self.create_instance()
            self.initialized = True

    def create_instance(self):
        """
        Create a new instance of the logger
        """
        try:
            self.client = docker.DockerClient(
                base_url='unix:///var/run/docker.sock'
                #base_url='tcp://0.0.0.0:2375'
                )
            with logger.contextualize(task='docker client', args=''):
                logger.info('Docker client initialized successfully')
        except Exception as e:
            err_msg = 'Failed to initialize docker client'
            print(f"{err_msg}: {e}")
            raise ValueError(err_msg)
        
    def check_docker_name_existence(self, name: str):
        """
        Check if a docker service exists
        """
        try:
            return name in [container.attrs['Name'].replace('/', '') for container in self.client.containers.list()]
        except Exception as e:
            err_msg = f'Failed to check if service {name} exists'
            logger.exception(err_msg, task='docker client', args='')
            raise ValueError(err_msg)
    
    def generate_available_name(self, name: str):
        """
        Generate a name that is not already in use
        """
        try:
            if not self.check_docker_name_existence(name):
                return name
            i = 1
            while True:
                new_name = f'{name}_{i}'
                if not self.check_docker_name_existence(new_name):
                    return new_name
                i += 1
        except Exception as e:
            err_msg = f'Failed to generate a new name for service {name}'
            logger.exception(err_msg, task='docker client', args='')
            raise ValueError(err_msg)
        
    def check_docker_port_allocated(self, port: int):
        """
        Check if a port is already allocated
        """
        try:
            return port in [container.ports for container in self.client.containers.list()]
        except Exception as e:
            err_msg = f'Failed to check if port {port} is already allocated'
            logger.exception(err_msg, task='docker client', args='')
            raise ValueError(err_msg)
        
    def check_avaliability(self, image_name: str, port: int):
        """
        Check if a service meets the requirements to be started
        """
        try:
            if self.check_docker_port_allocated(port):
                raise ValueError(f'Port is already allocated')
            if self.check_docker_name_existence(image_name):
                raise ValueError(f'Service already exists')
        except Exception as e:
            if e != 'Service already exists' and e != 'Port is already allocated':
                err_msg = f'Failed to check availability of service {image_name}'
                logger.exception(err_msg, task='docker client', args='')
                raise ValueError(err_msg)
        
    def service_up(self, service: Service):
        """
        Start a service
        """
        try:
            self.client.containers.run(
                service.image,
                name=service.name,
                ports=service.ports,
                environment=service.env,
                detach=True,
                restart_policy={'Name': 'always'}
                )
        except Exception as e:
            err_msg = f'Failed to start service {service.name}'
            logger.exception(err_msg, task='docker client', args='')
            raise ValueError(err_msg)
        
    def service_restart(self, service_name: str):
        """
        Restart a service
        """
        try:
            if self.check_docker_name_existence(service_name):
                container = self.client.containers.get(service_name)
                if container.status != 'running':
                    container.start()
                container.restart()
            else:
                raise ValueError(f'Service {service_name} does not exist')
        except Exception as e:
            err_msg = f'Failed to restart service {service_name}'
            logger.exception(err_msg, task='docker client', args='')
            raise ValueError(err_msg)

    def service_down(self, service_name: str):
        """
        Stop a service
        """
        try:
            if self.check_docker_name_existence(service_name):
                container = self.client.containers.get(service_name)
                container.stop()
        except Exception as e:
            err_msg = f'Failed to stop service {service_name}'
            logger.exception(err_msg, task='docker client', args='')
            raise ValueError(err_msg)
        
    def service_logs(self, service: str):
        """
        Get logs from a service
        """
        try:
            container = self.client.containers.get(service)
            return container.logs()
        except Exception as e:
            err_msg = f'Failed to get logs from service {service}'
            logger.exception(err_msg, task='docker client', args='')
            raise ValueError(err_msg)
        
    def get_service_info(self, container):
        return {
            'dt_creation': container.attrs['Created'].split('.')[0],
            'name': container.attrs['Name'].replace('/', ''),
            'status': container.attrs['State']['Status'],
            'ports': container.attrs['NetworkSettings']['Ports'],
            'image': container.attrs['Config']['Image'],
        }
    
    def get_used_ports(self):
        running_services_info = self.list_services(ServiceStatus.RUNNING)
        ports = []
        for service in running_services_info:
            for port in service['ports']:
                if service['ports'][port] is not None:
                    ports.append(service['ports'][port][0]['HostPort'])
        return ports
    
    def list_services(self, status: ServiceStatus):
        """
        List all services
        """
        try:
            all = True if status == ServiceStatus.ALL or status == ServiceStatus.DOWN else False
            services = self.client.containers.list(all=all)
            services_info = []
            for container in services:
                if status == ServiceStatus.DOWN and container.attrs['State']['Status'] == 'running':
                    continue
                services_info.append(self.get_service_info(container))
            return services_info
        except Exception as e:
            err_msg = 'Failed to list services'
            logger.exception(err_msg, task='docker client', args='')
            raise ValueError(err_msg)
        
    def check_port_availability(self, port):
        """
        Check if a port is available
        """
        try:
            return str(port) not in self.get_used_ports()
        except Exception as e:
            err_msg = f'Failed to check if port {port} is available'
            logger.exception(err_msg, task='docker client', args='')
            raise ValueError(err_msg)
        
    def generate_random_available_port(self):
        """
        Generate a random available port
        """
        try:
            range_start = 3000
            range_end = 4000
            port = range_start
            while True:
                if self.check_port_availability(port):
                    return port
                port += 1
                if port > range_end:
                    raise ValueError('No available ports')
        except Exception as e:
            err_msg = 'Failed to generate a random available port'
            logger.exception(err_msg, task='docker client', args='')
            raise ValueError(err_msg)
        
    def generate_custom_proxy_port(self):
        """
        Generate a custom proxy port
        """
        try:
            random_port = random.randint(10000, 11000)
            proxy_url = settings.default_proxy_url + f':{random_port}'
            return proxy_url
        except Exception as e:
            err_msg = 'Failed to generate a custom proxy port'
            logger.exception(err_msg, task='docker client', args='')
            raise ValueError(err_msg)
        
def get_docker_client():
    return DockerClient()