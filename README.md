# FIUBA IS1 2026 1C - TPG Tribu

Este repositorio es el espacio de trabajo de una tribu compuesta por dos squads. Los squads siguen manteniendo sus propios backends; este repo concentra el frontend web de la tribu y la documentación de nivel de integración.

## Entregables de tribu

- Visión integrada y MVP.
- Modelo de dominio.
- MVP integrado y funcionando en un ambiente similar a producción.
- Demo MVP.

## Estructura

- `AGENTS.md`: reglas fijas de trabajo dentro del repositorio.
- `iteraciones/`: objetivos y criterios de cada corte de integración.
- `entregas/`: manifiestos formales de cada entrega.
- `docs/vision/`: visión integrada de la tribu.
- `docs/analisis/`: modelo de dominio y contexto conceptual.
- `docs/arquitectura/`: contenedores e integración entre el frontend y los dos backends.
- Cada backend puede exponer Swagger UI en `/docs` y el spec en `/v3/api-docs` (`/swagger-ui.html` queda como alias de compatibilidad).
- `docs/ux/`: prototipos, si la tribu los usa, y decisiones de experiencia.
- `docs/operacion/`: guía didáctica de configuración, verificación, despliegue y demo.
- `docs/analisis/modelo-dominio-template.md` y `docs/analisis/modelo-dominio-template.puml`: guía narrativa y scaffold PlantUML del modelo de dominio.
- `index.html`, `styles.css`, `app.js`, `config.json`, `config.example.json`: frontend web starter.
- `scripts/`: preflights, servidor local, helper de integración local y smoke tests.
- `.github/workflows/`: validaciones automáticas del repo.

## Como se trabaja

1. Leer `docs/operacion/guia-tribu-template.md`.
2. Completar o derivar los templates a sus archivos vivos, incluyendo `docs/analisis/modelo-dominio.puml`.
3. Configurar `config.json` con la URL del frontend y las URLs de los dos backends.
4. Verificar que cada backend exponga `GET /api/health`, permita el origin del frontend en CORS y publique Swagger UI en `/docs`.
5. Usar `scripts/dev-server.sh` para levantar el frontend localmente, `scripts/dev-integration.sh` para ver el front y los backends juntos en un mismo origen y `scripts/smoke-mvp.sh` para validar el entorno desplegado. El helper de integracion admite `TRIBU_BACKEND_1_URL` y `TRIBU_BACKEND_2_URL` para apuntar cada uno de los dos backends por separado.

## Desarrollo local

- `bash scripts/dev-server.sh`: levanta el frontend solo, sin proxys ni dependencias externas.
- `bash scripts/dev-integration.sh`: levanta el frontend y publica los dos backends bajo un mismo origin para probar Swagger UI y `Try it out` sin pelear con CORS.
- `bash scripts/smoke-mvp.sh`: valida el entorno desplegado con las URLs reales.

## Verificacion rapida

- `bash scripts/preflight-integracion-01.sh`
- `bash scripts/preflight-integracion-02.sh`

## Idea tecnica

El frontend es agnóstico: puede seguir como HTML/CSS/JS simple o migrar a un framework si la tribu lo decide. El starter solo fija el contrato mínimo de integración y la experiencia operativa esperada.
