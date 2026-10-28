# NestHive

Webapp de simulación y operación de una flota AGV en la planta **ESPOL Fusion**. Esta es la versión final del escenario: mapa de rutas, órdenes de suministro y recogida, paletizaje, transporte, mantenimiento preventivo, averías y asistente Néstor.

La documentación completa de funcionalidades, archivos modificados, verificaciones y operación está en **[vf.md](vf.md)**.

## Iniciar la webapp de desarrollo

Con Docker Desktop abierto:

```bash
cd nestlink
docker compose -f compose.dev.yml up -d --build
```

Web: **http://localhost:3001** · API: **http://localhost:8001**.

## Apagarla

```bash
cd nestlink
docker compose -f compose.dev.yml down
```

`nestlink/` contiene la webapp FastAPI + Next.js y conserva la planta `realistic`. `agv-espol/` contiene la aplicación ESPOL original y sus pruebas. El entorno estándar de `nestlink/compose.yml` usa los puertos 3000 y 8000; su despliegue lo gestiona el responsable del entorno en vivo.
