# Integración 01 - Visión, dominio y contrato

## Entrega y alcance

Cerrar el recorte de la Tribu B con una visión integrada, un modelo de dominio en PlantUML y un contrato mínimo de integración entre el frontend y los dos backends (Marketing y Ventas).

El foco de esta iteración es establecer una base estable y compartida: vocabulario común, flujo de captación y conversión de leads, y contratos de API que ambos squads puedan implementar de forma independiente sin romper la experiencia integrada.

## Artefactos consolidados

| Artefacto | Descripción |
| --- | --- |
| `docs/vision/vision-tribu.md` | Visión integrada del MVP: problema, alcance, criterios de éxito e integración entre squads |
| `docs/analisis/modelo-dominio.md` | Modelo conceptual con clases, asociaciones, atributos, diccionario de datos y trazabilidad |
| `docs/analisis/modelo-dominio.puml` | Diagrama PlantUML del modelo de dominio, fuente de verdad visual |
| `docs/arquitectura/api-integracion.md` | Contrato de integración: endpoints, request/response, validaciones y manejo de errores |
| `docs/operacion/guia-tribu.md` | Guía operativa: proceso de trabajo, configuración, desarrollo local, verificaciones y demo |
| `entregas/integracion-01.md` | Este documento |

## Cambios principales

### Visión

- Se unificó el enunciado del problema: Marketing genera leads sin visibilidad sobre su conversión y Ventas recibe oportunidades sin contexto de origen. La tribu resuelve ambos lados en un único flujo.
- Se dejó explícito que el lead de Marketing y la oportunidad de Ventas son el **mismo objeto en distintas etapas**, no dos entidades de productos separados.
- Se recortaron fuera del MVP: reportes avanzados, automatización, integración con herramientas externas, segmentación avanzada e IA.

### Modelo de dominio

- Se identificaron ocho clases conceptuales: `Campaña`, `Lead`, `Contacto`, `Canal`, `Empresa`, `Cliente`, `Oportunidad` y `Producto`.
- La cadena `Campaña → Lead → Oportunidad → Cliente` es el eje central del modelo y materializa la trazabilidad end-to-end.
- Se separaron `Lead` y `Oportunidad` como clases distintas (no se fusionaron) porque pertenecen a dominios diferentes con ciclos de vida propios.
- Se incorporó `/Roi` como atributo derivado de `Campaña`, calculado solo cuando `Costo > 0`.
- Se definieron los estados de cada entidad con ciclo de vida: `Campaña` (Planificada → Activa → Finalizada), `Lead` (Nuevo → Contactado → Calificado → Convertido / Perdido) y `Oportunidad` (Nueva → Contactada → Propuesta → Ganada / Perdida).
- El modelo se expresó en PlantUML (`modelo-dominio.puml`) como fuente de verdad; el SVG exportado es solo apoyo visual.

### Contrato de integración

- Se acordaron **12 endpoints para Marketing** (campañas y leads) en estado propuesto y **21 endpoints para Ventas** (empresas, clientes, oportunidades y productos), de los cuales la mayoría están implementados.
- Se definieron los contratos de request/response y validaciones para todos los endpoints críticos del flujo.
- El punto de integración clave entre ambos backends es `PATCH /api/leads/{id}/cierre`: cuando el resultado es `Convertido`, Marketing llama a `POST /api/oportunidades` con `{ leadId: <id>, estado: "Nueva" }` y devuelve el `oportunidadId` creado; si la llamada falla, el lead queda en estado `Convertido` sin oportunidad asociada (inconsistencia a resolver manualmente o en iteración futura).
- Se documentaron las reglas de integridad cruzada: no se puede crear una empresa sin lead, ni un cliente sin empresa, ni una oportunidad sin lead asociado.
- Se estableció que cada backend debe permitir el origin del frontend mediante CORS con allowlist explícita.

## Decisiones tomadas

Las siguientes decisiones se acordaron como **estables hasta el siguiente corte** (Integración 02):

| Decisión | Alcance |
| --- | --- |
| Los ocho conceptos del modelo de dominio y sus nombres en español | Vocabulario compartido entre squads; no renombrar sin revisar el contrato |
| La cadena de asociaciones `Campaña → Lead → Oportunidad → Cliente` | Estructura del flujo principal; no agregar atajos ni saltar etapas |
| Los estados y sus secuencias para `Campaña`, `Lead` y `Oportunidad` | Las máquinas de estado son contratos; cambiarlas requiere coordinación entre squads |
| El endpoint `PATCH /api/leads/{id}/cierre` como punto de integración entre backends | Es el evento que conecta Marketing con Ventas; su contrato no debe cambiar unilateralmente |
| El campo `CampañaOrigen` en `Lead` como trazador de origen | Garantiza el cálculo de métricas en Marketing; es obligatorio en la creación del lead |
| CORS con allowlist explícita por cada backend | Requerimiento operativo no negociable para que el frontend funcione en demo |
| `config.json` como fuente de configuración del frontend | Las URLs públicas de los backends se leen de ahí; no hardcodear |

## Riesgos y pendientes

### Dependencias cruzadas

| Dependencia | Entre | Riesgo |
| --- | --- | --- |
| Generación automática de oportunidad al convertir un lead | Marketing → Ventas | Si el backend de Ventas no está disponible, la conversión queda en estado inconsistente |
| Visibilidad del estado de la oportunidad desde Marketing | Ventas → Marketing | Sin este dato, el ROI y la tasa de conversión no se pueden calcular con precisión |
| CORS habilitado en ambos backends | Ambos → Frontend | Si un backend no permite el origin del frontend, el smoke de demo falla |
| URLs públicas estables antes de la demo | Ambos backends | Servicios en capa gratuita pueden tener latencia de arranque ("cold start") |

### Dudas de alcance sin resolver

- No está definido qué información del lead es visible para Ventas al momento de la conversión (¿solo campaña y canal, o el historial completo de estados?).
- No está definido si Marketing tendrá visibilidad sobre el estado de la oportunidad en Ventas.
- La fórmula exacta de cálculo de ROI no fue acordada formalmente.
- No se determinó si se mantendrá historial de cambios de canal de origen para auditoría.
- Las restricciones de acceso al reporte de leads por canal no fueron especificadas.

### Riesgos de integración

- El mecanismo técnico de traspaso entre backends (llamada directa, evento o webhook) quedó diferido a iteraciones posteriores; hasta que se defina, la integración puede ser manual o simulada.
- El valor admitido para `motivoPerdida` en Oportunidad está hardcodeado como `"Precio"`, lo que limita la expresividad del dominio.
- El tipo del atributo `Codigo` de `Producto` no fue confirmado (String vs Int), lo que puede generar incompatibilidad entre los contratos de ambos backends.

## Próximos pasos

El objetivo de la siguiente iteración (Integración 02) es llevar la tribu a un **MVP integrado y desplegado**:

1. **Despliegue público**: frontend web accesible por HTTPS y ambos backends con URLs estables y documentadas en `config.json`.
2. **CORS verificado**: el origin del frontend debe aparecer en la allowlist de ambos backends antes de la demo.
3. **Smoke de demo operativo**: ejecutar `scripts/smoke-mvp.sh` contra el entorno desplegado y lograr que todos los checks pasen.
4. **Flujo integrado de punta a punta**: crear una campaña → registrar un lead → convertirlo → verificar que la oportunidad existe en Ventas.
5. **Resolver dudas abiertas priorizadas**: acordar la fórmula de ROI, el contrato de traspaso entre backends y qué datos del lead viajan a Ventas.
6. **Estabilizar endpoints propuestos**: los endpoints de Marketing en estado `propuesto` deben pasar a `implementado` para habilitar el flujo completo.