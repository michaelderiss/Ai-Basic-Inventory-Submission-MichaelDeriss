# Bucle de Agente de Inventario Básico con IA

## Tu reto

Un pequeño negocio local — una tienda de suministros para cafeterías con dos ubicaciones físicas — está perdiendo dinero. No porque las ventas hayan caído, sino porque nadie en el equipo puede responder una pregunta simple en cualquier momento: "¿Tenemos suficiente de este producto para cubrir la semana?"

El stock se lleva en una hoja compartida que nadie actualiza de manera consistente. La dueña, Carla, te ha contactado después de ver una demo de un asistente de IA en una feria comercial. No quiere un panel que tenga que mantener manualmente; quiere poder hablar con un sistema y obtener respuestas. También quiere que el sistema actúe como caja registradora: que lleve un registro de entregas, ventas y alertas cuando algo se está quedando sin stock.

Tu trabajo es construir ese sistema. Tiene dos partes que deben trabajar juntas:

1. Una API REST construida con FastAPI que gestione los datos del inventario. Expone endpoints para listar productos, registrar nuevos, actualizar niveles de stock y consultar alertas de stock bajo. Los productos se almacenan en un archivo CSV para que persistan entre sesiones.
2. Un agente de IA escrito en Python que se conecta a un LLM y usa tu API como conjunto de herramientas. El agente corre en un bucle: recibe un mensaje de Carla, decide qué acción tomar, llama al endpoint correcto como herramienta y responde con el resultado. Cada paso se registra en un archivo `conversation_log.csv` separado.

## Cómo iniciar el proyecto

Este proyecto usa una plantilla inicial de Python. Haz fork y clónala:

https://github.com/4GeeksAcademy/python-hello

Puedes trabajar desde GitHub Codespaces o clonándolo localmente. Cuando lo hayas clonado, crea tu propio repositorio de GitHub y cambia el remoto para seguir tu progreso.

```bash
# Terminal 1 - iniciar la API
uvicorn api.app:app --reload

# Terminal 2 - iniciar el agente
python agent.py
```

Antes de ejecutar el agente completo, crea un archivo `.env` en la raíz con tu clave del LLM:

```bash
GROQ_API_KEY=tu_clave_aqui
```

IMPORTANTE: Nunca subas tu archivo `.env` al repositorio. Añádelo a `.gitignore` antes del primer commit.

## Qué debes hacer

### API (`api/app.py`)

- [ ] Crear una aplicación FastAPI que guarde los datos en `products.csv`.
- [ ] `GET /api/products` — devuelve la lista completa.
- [ ] `POST /api/products` — agrega un producto nuevo.
- [ ] `PATCH /api/inventory/{product_id}` — actualiza el stock.
- [ ] `GET /api/inventory/alerts` — devuelve productos con cantidad menor al umbral.
- [ ] Todos los endpoints deben devolver códigos HTTP correctos y mensajes descriptivos.

### Agente (`agent.py`)

- [ ] Definir los endpoints como herramientas para el LLM.
- [ ] Implementar el bucle completo: Observar -> Pensar -> Actuar -> Actualizar -> Repetir.
- [ ] Mantener el historial de conversación en memoria durante la sesión.
- [ ] Cuando el LLM seleccione una herramienta, el agente debe llamarla e inyectar el resultado al contexto.
- [ ] Terminar limpiamente cuando el LLM devuelva una respuesta final.

### Registro de conversación

- [ ] Cada evento debe añadirse a `conversation_log.csv` con `actor`, `message`, `tool_call` y `timestamp`.
- [ ] El archivo debe persistir entre sesiones (append-only).

## Cómo entregar

Haz push a GitHub y comparte el enlace del repositorio. Asegúrate de actualizar el README según estas instrucciones.

```bash
git init
git add .
git commit -m "Add inventory API and agent scaffold"
git branch -M main
git remote add origin <tu_repo_url>
git push -u origin main
```

La parte final que falta es el bucle manual del agente en Python.
