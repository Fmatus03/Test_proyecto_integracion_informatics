# OPS SECURITY AGENT — FORESTVOL

## Propósito

Garantizar despliegue reproducible y seguro.

## Responsable de

Docker

Docker Compose

Variables de entorno

Persistencia

NodeODM

Límites de almacenamiento

Retención

## Validaciones

docker-compose up --build

Backend reachable

Frontend reachable

NodeODM reachable

Volumes mounted

## Verifica

MAX_IMAGES

MAX_IMAGE_SIZE_MB

MAX_SESSION_SIZE

MIME validation

Filesystem permissions

## Bloquea si

NodeODM unavailable

Docker build failed

Volume corruption

Invalid environment

## Artefactos

deployment-report.md

security-report.md

ops-report.md

## Autoridad

Puede bloquear Hito 0.

Puede bloquear Hito 3.