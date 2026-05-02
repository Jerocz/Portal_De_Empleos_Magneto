"""
WebSocket Connection Manager

Cómo funciona:
- Mantiene un diccionario {user_id: WebSocket} con las conexiones activas.
- Cuando un empleado hace login y abre el dashboard, el frontend conecta a ws://.../ws/{user_id}.
- El manager registra esa conexión en memoria.
- Cuando el empleador cambia el estado de una postulación, el router llama a
  manager.send_to(employee_id, mensaje) y el mensaje llega INSTANTÁNEAMENTE
  al navegador del empleado sin que este tenga que recargar ni preguntar.
- Si el empleado no está conectado, el mensaje se descarta (no hay cola offline).
"""
from fastapi import WebSocket
import json


class ConnectionManager:
    def __init__(self):
        # user_id → WebSocket activo
        self._connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self._connections[user_id] = websocket

    def disconnect(self, user_id: int):
        self._connections.pop(user_id, None)

    async def send_to(self, user_id: int, data: dict):
        """Envía un mensaje JSON al usuario si está conectado."""
        ws = self._connections.get(user_id)
        if ws:
            try:
                await ws.send_text(json.dumps(data, ensure_ascii=False))
            except Exception:
                # Conexión caída — limpiar
                self.disconnect(user_id)

    def is_connected(self, user_id: int) -> bool:
        return user_id in self._connections

    @property
    def active_connections(self) -> int:
        return len(self._connections)


# Instancia global — compartida por todos los routers
manager = ConnectionManager()
