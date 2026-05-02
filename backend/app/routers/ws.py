"""
Router WebSocket — conexión persistente por usuario autenticado.

Endpoint: ws://localhost:8000/ws/{user_id}?token=<JWT>

El frontend se conecta al hacer login. El servidor valida el token
y registra la conexión en el ConnectionManager global.
Cuando el servidor quiere notificar al usuario, usa manager.send_to(user_id, data).
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from jose import jwt, JWTError
from app.websocket_manager import manager
from app.security import SECRET_KEY, ALGORITHM

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    token: str = Query(...),
):
    # Validar token antes de aceptar la conexión
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_user_id = int(payload["sub"])
        if token_user_id != user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except (JWTError, KeyError, ValueError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(user_id, websocket)
    try:
        # Mantener la conexión viva esperando mensajes del cliente (ping/pong)
        while True:
            data = await websocket.receive_text()
            # El cliente puede enviar "ping" para mantener la conexión activa
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
