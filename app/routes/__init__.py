# Routes package
# Computo
from .Computo.ec2 import bp as ec2
from .Computo.batch import bp as batch
from .lambda_service import bp as lambda_bp

# Almacenamiento
from .Almacenamiento.s3 import bp as s3
from .Almacenamiento.ebs import bp as ebs
from .Almacenamiento.efs import bp as efs
from .Almacenamiento.fsx import bp as fsx

# Base de Datos
from .Base_de_Datos.rds import bp as rds
from .Base_de_Datos.dynamodb import bp as dynamodb
from .Base_de_Datos.neptune import bp as neptune
from .Base_de_Datos.documentdb import bp as documentdb
from .Base_de_Datos.elasticache import bp as elasticache

# Mensajería
from .Mensajeria.sns import bp as sns
from .Mensajeria.sqs import bp as sqs
from .Mensajeria.kinesis import bp as kinesis

# Redes
from .Redes.vpc import bp as vpc
from .Redes.route53 import bp as route53
from .Redes.cloudfront import bp as cloudfront
from .Redes.elbv2 import bp as elbv2
from .Redes.apigateway import bp as apigateway

# Seguridad
from .Seguridad.iam import bp as iam
from .Seguridad.kms import kms_bp as kms
from .Seguridad.acm import acm_bp
from .Seguridad.secretsmanager import secretsmanager_bp as secretsmanager
from .Seguridad.security_groups import bp as security_groups

# Analytics
from .Analytics.athena import bp as athena
from .Analytics.glue import bp as glue
from .Analytics.emr import emr_bp as emr

# Integración
from .Integracion.cloudformation import bp as cloudformation

# Contenedores
from .Contenedores.ecs import bp as ecs
from .Contenedores.ecr import bp as ecr
from .Contenedores.eks import bp as eks

# ML/AI
from .ML_AI.sagemaker import bp as sagemaker
from .ML_AI.bedrock import bedrock
from .ML_AI.rekognition import rekognition

# Gestión
from .Gestion.autoscaling import bp as autoscaling
from .Gestion.cloudwatch import bp as cloudwatch
from .Gestion.cost_explorer import cost_explorer

# Config
from .Config.config import bp as config

# AI_Assistant
# from .AI_Assistant.chat import bp as chat  # Temporalmente comentado por error de importación
