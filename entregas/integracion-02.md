# Integración 02 - MVP desplegado y demo

## Entrega y alcance

MVP integrado de la Tribu B desplegado en URLs públicas. El frontend React SPA conecta con dos backends independientes (Marketing y Ventas) exponiendo el flujo completo de captación comercial: desde la creación de campañas y registro de leads hasta la gestión de oportunidades y clientes en Ventas.

## Artefactos consolidados

### Frontend

| Artefacto | Descripción |
| --- | --- |
| `src/` | Código fuente React + TypeScript + Vite |
| `src/.env.production` | URLs de APIs de producción |
| `src/.env.development` | URLs de APIs locales |
| `src/config.ts` | Configuración de endpoints con VITE env vars |
| `vite.config.ts` | Build config (root en `src/`, outDir en `dist/`) |

### Documentación

| Artefacto | Descripción |
| --- | --- |
| `docs/vision/vision-tribu.md` | Visión integrada del MVP |
| `docs/analisis/modelo-dominio.md` | Modelo de dominio conceptual |
| `docs/analisis/modelo-dominio.puml` | Diagrama PlantUML del modelo |
| `docs/arquitectura/api-integracion.md` | Contrato de integración entre frontend y backends |
| `docs/operacion/guia-tribu.md` | Guía operativa del equipo |
| `docs/operacion/guia-deploy.md` | Guía de deploy para ambos squads |
| `docs/ux/prototipos.md` | Prototipos de interfaz |
| `entregas/integracion-01.md` | Manifiesto de integración anterior |
| `entregas/integracion-02.md` | Este documento |

### Scripts de verificación

| Artefacto | Descripción |
| --- | --- |
| `scripts/smoke-mvp.sh` | Smoke test de producción |
| `scripts/dev-server.sh` | Servidor de desarrollo local |
| `scripts/dev-integration.sh` | Servidor de integración local |
| `scripts/preflight-integracion-01.sh` | Preflight de integración 01 |
| `scripts/preflight-integracion-02.sh` | Preflight de integración 02 |

### Infraestructura

| Artefacto | Descripción |
| --- | --- |
| `config.json` | Configuración de la tribu con URLs públicas de ambos backends |
| `.env.production` / `.env.development` | Variables de entorno por entorno |

## Cambios principales

### Backend Marketing (Squad 1) — Mejoras en calidad y cobertura

- Se completó la cobertura BDD con Cucumber para todos los endpoints del módulo de Marketing: PUT/DELETE de campañas, listado y detalle de leads, actualización de datos de lead y nuevos catálogos de productos, canales y empresas (HU-25 y HU-26).
- Se agregaron 115 pasos Gherkin distribuidos en 6 features, todos verificados con `./gradlew check` (144 tests, 0 failures).
- Se corrigió `LazyInitializationException` en los métodos de consulta de leads (`LeadService.listar()` y `obtener()`).
- Se agregaron índices JPA (`@Index`) en las entidades `Campania` y `LeadComercial` para optimizar consultas frecuentes por nombre, estado, fechas y FK.

### Configuración del frontend para múltiples entornos

- Se migró `src/config.ts` de URLs hardcodeadas a `import.meta.env.VITE_*` con fallback a localhost.
- Se crearon `.env.production` y `.env.development` para separar config de producción y desarrollo.
- Se ubican en `src/` por la directiva `root: 'src'` de Vite.

### Despliegue

- **Frontend**: Static Site en Render, rama `integracion-02`, build automático con `pnpm build`, publish `dist/`.
- **Backend Marketing**: Web Service en Render con Docker, rama `iteracion-06`, PostgreSQL gestionado en Render.
- **Backend Ventas**: Web Service en Render, rama `iteracion-06`, deployado por el Squad 3.
- Se configuró SPA routing con rewrite rule `/* → /index.html`.
- Se agregó cron-job cada 10 min al health endpoint de ambos backends para mantenerlos activos.

### CORS

- El backend Marketing permite el origin del frontend via `CORS_ALLOWED_ORIGINS`.
- El backend Ventas incluye el origin del frontend en su configuración de CORS.
- Se soportan múltiples origins separados por coma para desarrollo y producción.

### Integración con Squad 3 (Ventas)

- El Squad 3 deployó su backend en `https://two026-1c-tpg-squad-3.onrender.com`.
- Actualizaron `src/.env.production` y `src/config.ts` con su URL y los prefijos `/api/` para sus endpoints.
- El frontend ya consume ambos backends sin problemas de CORS.

## Decisiones tomadas

| Decisión | Justificación |
| --- | --- |
| VITE env vars para URLs de API | Permite buildear para cada entorno sin tocar código |
| Render Static Site + Web Service | Capa gratuita suficiente para el MVP con HTTPS automático |
| Rama separada `deploy_oficial` → `integracion-02` / `iteracion-06` | Aísla cambios de deploy del trabajo activo |
| CORS parametrizado por env var | Misma imagen de backend sirve para local y prod |
| Cron-job cada 10 min | Mitiga cold start del plan free de Render |

## Evidencia de despliegue o ejecucion demostrable

| Componente | URL | Estado |
| --- | --- | --- |
| Frontend | `https://two026-1c-tpg-tribu-b.onrender.com` | ✅ Live |
| Backend Marketing (health) | `https://two026-1c-tpg-squad-1-tv35.onrender.com/api/health` | ✅ `{"status":"ok"}` |
| Backend Ventas (health) | `https://two026-1c-tpg-squad-3.onrender.com/api/health` | ✅ `{"status":"ok"}` |
| Swagger Marketing | `https://two026-1c-tpg-squad-1-tv35.onrender.com/docs` | ✅ |
| Datos semilla | Canales, productos, empresas, campañas y leads cargados | ✅ |
| Deploy automático | Push a `integracion-02` → redeploy frontend | ✅ |
| Keep-awake | cron-job.org cada 10 min a ambos health endpoints | ✅ |

## Riesgos y pendientes

- El plan free de Render **duerme** los Web Services tras 15 min sin uso. Primer request tarda ~30s en despertar (mitigado con cron-job).
- La base de datos PostgreSQL free **expira a los 90 días**. Verificar antes de la defensa.
- No hay comunicación backend-a-backend entre Marketing y Ventas. La conversión de lead no crea automáticamente la oportunidad en Ventas.
- El backend Ventas puede tener endpoints aún no implementados o diferencias en el contrato de integración.
- El `smoke-mvp.sh` no fue ejecutado formalmente contra las URLs de producción.

## Proximos pasos

1. Ejecutar `scripts/smoke-mvp.sh` contra las URLs de producción y verificar que todos los checks pasen.
2. Probar el flujo end-to-end: crear campaña → registrar lead → convertir → verificar oportunidad en Ventas.
3. Resolver la comunicación backend-a-backend para la creación automática de oportunidades.
4. Preparar el guion de demo con narrativa clara del flujo integrado.
5. Verificar fecha de expiración de la DB antes de la defensa.
