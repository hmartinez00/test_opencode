# Curso Rapido: Fundamentos de Docker y Contenedores

**Audiencia:** Desarrolladores y Arquitectos de Software
**Proposito:** Comprender los conceptos clave de la contenerizacion y dominar los comandos basicos de Docker.

---

## Sesion 1: Arquitectura y Conceptos Clave

### Objetivo Pedagogico
Comprender la diferencia entre Maquinas Virtuales y Contenedores, y conocer la arquitectura cliente-servidor de Docker.

### Contenido

1. **Que es un Contenedor?**
   - Unidades de software estandarizadas que empaquetan codigo y dependencias.
   - Comparativa: Maquinas Virtuales (Guest OS pesado) vs Contenedores (Aislamiento a nivel de Kernel).
   - Ventajas: portabilidad, eficiencia en recursos, tiempo de arranque instantaneo.

2. **Arquitectura de Docker**
   - Docker Client (CLI) vs Docker Daemon (dockerd).
   - Registros (Docker Hub), Imagenes (templates inmutables) y Contenedores (instancias en ejecucion).
   - Flujo de comunicacion: Cliente -> Socket Unix/TCP -> Daemon -> Registry.

3. **Insumos para lamina interactiva:**
   - Comparador interactivo (un control deslizante para alternar entre la vista de arquitectura de VM y la de Contenedores Docker, mostrando las diferencias de capas).

---

## Sesion 2: Flujo de Trabajo Practico y Comandos

### Objetivo Pedagogico
Aprender el ciclo de vida de un contenedor (`docker pull`, `run`, `stop`, `rm`) y construir un `Dockerfile` basico.

### Contenido

1. **Ciclo de Vida de un Contenedor**
   - Diagrama de flujo: `docker pull` (obtener imagen) -> `docker run` (crear e iniciar) -> `docker ps` (listar) -> `docker stop` (detener) -> `docker rm` (eliminar).
   - Diferencia entre `stop` (SIGTERM) y `kill` (SIGKILL).

2. **Anatomia de un Dockerfile**
   - Directivas principales:
     - `FROM`: imagen base (ej. `node:20-alpine`, `php:8.3-fpm`).
     - `WORKDIR`: directorio de trabajo dentro del contenedor.
     - `COPY`: copiar archivos del host al contenedor.
     - `RUN`: ejecutar comandos durante la construccion (build time).
     - `CMD`: comando por defecto al iniciar el contenedor (run time).
     - `EXPOSE`: documentar puertos que usara la app.
   - Ejemplo de Dockerfile basico para una aplicacion Node.js con Express.

3. **Lamina de Cierre / Resumen**
   - Tarjetas resumen con 5 comandos indispensables: `docker run -d -p`, `docker logs`, `docker exec -it`, `docker compose up -d`, `docker system prune`.
   - Buenas practicas: usar imagenes oficiales, multi-stage builds para reducir tamano, nunca usar root en produccion.
