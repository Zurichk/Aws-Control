from ...utils.aws_client import get_aws_client

class GlueMCPTools:
    """Herramientas MCP para AWS Glue"""

    def list_crawlers(self, max_results=50, region='us-east-1'):
        """
        Listar crawlers de AWS Glue

        Args:
            max_results (int): Número máximo de resultados (default: 50)
            region (str): Región de AWS (default: us-east-1)

        Returns:
            dict: Lista de crawlers
        """
        try:
            glue = get_aws_client('glue', region)
            response = glue.get_crawlers(MaxResults=max_results)
            return {
                'success': True,
                'crawlers': response.get('Crawlers', []),
                'region': region
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'region': region
            }

    def create_crawler(self, crawler_name, role, database_name, s3_targets, region='us-east-1'):
        """
        Crear un nuevo crawler en AWS Glue

        Args:
            crawler_name (str): Nombre del crawler
            role (str): ARN del rol IAM
            database_name (str): Nombre de la base de datos
            s3_targets (list): Lista de rutas S3
            region (str): Región de AWS (default: us-east-1)

        Returns:
            dict: Resultado de la creación
        """
        try:
            glue = get_aws_client('glue', region)
            glue.create_crawler(
                Name=crawler_name,
                Role=role,
                DatabaseName=database_name,
                Targets={
                    'S3Targets': [{'Path': target} for target in s3_targets]
                }
            )
            return {
                'success': True,
                'message': f'Crawler "{crawler_name}" creado exitosamente',
                'crawler_name': crawler_name,
                'region': region
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'crawler_name': crawler_name,
                'region': region
            }

    def start_crawler(self, crawler_name, region='us-east-1'):
        """
        Iniciar un crawler en AWS Glue

        Args:
            crawler_name (str): Nombre del crawler
            region (str): Región de AWS (default: us-east-1)

        Returns:
            dict: Resultado del inicio
        """
        try:
            glue = get_aws_client('glue', region)
            glue.start_crawler(Name=crawler_name)
            return {
                'success': True,
                'message': f'Crawler "{crawler_name}" iniciado',
                'crawler_name': crawler_name,
                'region': region
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'crawler_name': crawler_name,
                'region': region
            }

    def list_jobs(self, max_results=50, region='us-east-1'):
        """
        Listar jobs ETL de AWS Glue

        Args:
            max_results (int): Número máximo de resultados (default: 50)
            region (str): Región de AWS (default: us-east-1)

        Returns:
            dict: Lista de jobs
        """
        try:
            glue = get_aws_client('glue', region)
            response = glue.get_jobs(MaxResults=max_results)
            return {
                'success': True,
                'jobs': response.get('Jobs', []),
                'region': region
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'region': region
            }

    def create_job(self, job_name, role, script_location, max_capacity=2.0, region='us-east-1'):
        """
        Crear un nuevo job ETL en AWS Glue

        Args:
            job_name (str): Nombre del job
            role (str): ARN del rol IAM
            script_location (str): Ubicación del script en S3
            max_capacity (float): Capacidad máxima (default: 2.0)
            region (str): Región de AWS (default: us-east-1)

        Returns:
            dict: Resultado de la creación
        """
        try:
            glue = get_aws_client('glue', region)
            glue.create_job(
                Name=job_name,
                Role=role,
                Command={
                    'Name': 'glueetl',
                    'ScriptLocation': script_location
                },
                MaxCapacity=max_capacity
            )
            return {
                'success': True,
                'message': f'Job "{job_name}" creado exitosamente',
                'job_name': job_name,
                'region': region
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'job_name': job_name,
                'region': region
            }

    def start_job_run(self, job_name, region='us-east-1'):
        """
        Ejecutar un job ETL en AWS Glue

        Args:
            job_name (str): Nombre del job
            region (str): Región de AWS (default: us-east-1)

        Returns:
            dict: Resultado de la ejecución
        """
        try:
            glue = get_aws_client('glue', region)
            response = glue.start_job_run(JobName=job_name)
            job_run_id = response.get('JobRunId')
            return {
                'success': True,
                'message': f'Job "{job_name}" ejecutado',
                'job_name': job_name,
                'job_run_id': job_run_id,
                'region': region
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'job_name': job_name,
                'region': region
            }