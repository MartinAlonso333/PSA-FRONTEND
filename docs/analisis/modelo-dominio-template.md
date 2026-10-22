# Modelo de dominio de la tribu

## Alcance del modelo

Modelar el dominio compartido por la tribu a nivel conceptual, sin bajar a tecnología, UI ni base de datos.

## Inputs usados

- `docs/vision/vision-tribu.md`
- `docs/arquitectura/api-integracion.md`
- `docs/ux/prototipos.md`, si la tribu necesita validar vocabulario o recorridos
- Escenarios, contratos y decisiones de integración relevantes

## Historias priorizadas tomadas como base

Listar los casos de uso o historias relevantes del sistema. Agrúpalos por área si ayuda a ordenar y conservá el vocabulario del negocio.

## Clases conceptuales

Nombrar conceptos del negocio. Evitar palabras como `controller`, `service`, `endpoint`, `DTO`, `API`, `screen` o `tabla`.

## Asociaciones

Describir las relaciones relevantes entre las clases conceptuales y su cardinalidad.

## Atributos

Anotar los atributos que ayuden a entender el dominio. Si un atributo no aporta claridad, se omite.

## Diagrama

El diagrama conceptual editable debe vivir en `docs/analisis/modelo-dominio.puml`. El archivo `docs/analisis/modelo-dominio-template.puml` es solo el scaffold inicial del template; si se exporta una imagen, referenciarla desde ese mismo bloque.

## Trazabilidad

Explicar cómo se llega desde visión, historias y, si existen, prototipos hasta el modelo de dominio.

## Fuera de alcance y exclusiones

Explicitar límites, supuestos y temas pendientes del análisis.

## Dudas abiertas

- Confirmar el vocabulario común antes de convertir este modelo en su versión viva.
