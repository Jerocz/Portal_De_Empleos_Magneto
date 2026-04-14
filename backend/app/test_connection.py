from app.database import engine

try:
    conn = engine.connect()
    print("✅ Conexión exitosa a MySQL")
    conn.close()
except Exception as e:
    print("❌ Error conectando:", e)