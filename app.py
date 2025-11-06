from flask import Flask, render_template, redirect, url_for, session, jsonify, request
import os
import uuid # Necesario para generar item_key únicas

# NOTA: La clave secreta debe ser una cadena de bytes aleatoria en producción
# Para Canvas, usamos un valor placeholder.
app = Flask(__name__)
app.secret_key = "clave-secreta"  # Necesario para manejar sesiones

# --- PRODUCTOS ACTUALIZADOS A MILANESAS ---
# Ahora la clave 'imagen' solo contiene el nombre del archivo para evitar rutas duplicadas.
productos = [
    {"id": 1, "nombre": "Milanesa Napolitana", "precio": 25, "imagen": "milanesa_napolitana.webp"},
    {"id": 2, "nombre": "Milanesa a Caballo", "precio": 22, "imagen": "milanesa_caballo.webp"},
    {"id": 3, "nombre": "Milanesa Fugazzeta", "precio": 24, "imagen": "milanesa_fugazzeta.webp"},
    {"id": 4, "nombre": "Milanesa Cheddar y Bacon", "precio": 26, "imagen": "milanesa_cheddar.webp"}
]
# --- FIN DE CAMBIOS DE PRODUCTOS ---

# Precios de los refrescos
refresco_precios = {
    '0': 0.00,  # Sin Refresco
    '1': 1.50,  # Coca-Cola
    '2': 1.75,  # Pepsi
    '3': 1.25,  # Sprite
    '4': 1.60,  # Fanta
    '5': 1.00,  # 7Up
    '6': 0.75   # Manaos
}

# --- NUEVO: Diccionario para las imágenes de los refrescos ---
refresco_imagenes = {
    '0': None, # Sin Refresco
    '1': "coca_cola.webp",
    '2': "pepsi.webp",
    '3': "sprite.webp",
    '4': "fanta.webp",
    '5': "7up.webp",
    '6': "manaos.webp"
}

def obtener_producto(producto_id):
    """Busca un producto por ID."""
    try:
        pid = int(producto_id)
        return next((p for p in productos if p["id"] == pid), None)
    except ValueError:
        return None

def calcular_totales(carrito):
    """Calcula el subtotal y total del carrito."""
    subtotal = 0
    for item in carrito:
        subtotal += item["precio_total"]
    
    # Simulación de impuestos y envío (simplemente un cargo fijo pequeño)
    impuestos = subtotal * 0.10
    envio = 5.00 if subtotal < 50 else 0.00
    total = subtotal + impuestos + envio
    
    return subtotal, impuestos, envio, total


# --- RUTA PRINCIPAL DE LA TIENDA ---
@app.route("/")
def index():
    """Muestra la lista de productos y el contador del carrito."""
    carrito = session.get("carrito", [])
    _, _, _, total = calcular_totales(carrito) # Se usa el total aquí para mostrar el botón de Carrito
    
    # Calcular la cantidad total de ítems en el carrito
    cart_count = sum(item.get('cantidad', 1) for item in carrito)
    
    return render_template("index.html", productos=productos, cart_count=cart_count, cart_total=total)

# --- RUTA DE CARRITO ---
@app.route("/carrito")
def carrito():
    """Muestra el contenido del carrito."""
    carrito = session.get("carrito", [])
    subtotal, impuestos, envio, total = calcular_totales(carrito)
    
    return render_template("carrito.html", 
                           carrito=carrito, 
                           subtotal=subtotal, 
                           impuestos=impuestos, 
                           envio=envio, 
                           total=total)

# --- NUEVA RUTA PARA AGREGAR PRODUCTOS (POST) ---
@app.route("/agregar", methods=["POST"])
def agregar_producto():
    """
    Agrega uno o varios ítems de un producto con refresco al carrito.
    Recibe los datos vía POST/JSON.
    """
    data = request.get_json()
    if not data or 'product_id' not in data or 'refresco_id' not in data or 'cantidad' not in data:
        return jsonify({'success': False, 'message': 'Datos inválidos.'}), 400

    producto_id = data.get('product_id')
    refresco_id = str(data.get('refresco_id'))
    try:
        cantidad = int(data.get('cantidad'))
    except ValueError:
        return jsonify({'success': False, 'message': 'Cantidad inválida.'}), 400

    if cantidad <= 0:
        return jsonify({'success': False, 'message': 'La cantidad debe ser mayor a cero.'}), 400

    producto = obtener_producto(producto_id)
    if not producto:
        return jsonify({'success': False, 'message': 'Producto no encontrado.'}), 404

    # Obtener el precio del refresco
    precio_refresco = refresco_precios.get(refresco_id, 0.00)
    
    # Calcular el precio unitario total
    precio_unitario_total = producto["precio"] + precio_refresco
    
    # Construir el nombre del refresco para el carrito
    nombre_refresco_map = {
        '0': "Sin Refresco", '1': "Coca-Cola", '2': "Pepsi", 
        '3': "Sprite", '4': "Fanta", '5': "7Up", '6': "Manaos"
    }
    nombre_refresco = nombre_refresco_map.get(refresco_id, "Refresco Desconocido")
    
    # --- CAMBIO: Obtener la imagen del refresco ---
    imagen_refresco = refresco_imagenes.get(refresco_id, None)


    # Obtener o inicializar el carrito
    carrito = session.get("carrito", [])

    # Crear el ítem del carrito
    for _ in range(cantidad):
        item = {
            "item_key": str(uuid.uuid4()), # ID única para eliminar/identificar el ítem
            "id": producto["id"],
            "nombre": producto["nombre"],
            "precio_base": producto["precio"], # Precio solo de la milanesa
            "refresco_id": refresco_id,
            "nombre_refresco": nombre_refresco,
            "imagen_refresco": imagen_refresco, # <-- CAMBIO: Se añade la imagen del refresco
            "precio_refresco": precio_refresco,
            "precio_total": precio_unitario_total,
            "imagen": producto["imagen"],
            # Nota: La cantidad es 1 aquí porque se agregan N ítems separados.
            # En la versión anterior con cantidades, se modificaría un solo ítem. 
            # Para simplificar la eliminación de un solo ítem, cada unidad se agrega separadamente.
            "cantidad": 1 
        }
        carrito.append(item)

    session["carrito"] = carrito
    session.modified = True

    # Calcular el nuevo conteo del carrito
    cart_count = sum(item.get('cantidad', 1) for item in carrito)

    return jsonify({'success': True, 'message': 'Producto(s) agregado(s) al carrito', 'cart_count': cart_count})


# --- RUTA PARA VACIAR CARRITO ---
@app.route("/vaciar")
def vaciar():
    """Vacía completamente el carrito de compras."""
    session.pop("carrito", None)
    session.modified = True
    return redirect(url_for("carrito"))

# --- RUTA DE API PARA PROCESAR PAGO ---
# --- MODIFICADO: /api/procesar_pago Y ACEPTA JSON ---
@app.route("/api/procesar_pago", methods=["POST"])
def procesar_pago():
    """
    Simula el procesamiento del pago (API).
    Ahora no requiere datos de tarjeta, solo simula el éxito si el carrito no está vacío.
    """
    if "carrito" in session and session["carrito"]:
        # El pago es exitoso, vaciamos el carrito
        session.pop("carrito", None)
        session.modified = True
        return jsonify({'success': True, 'message': 'Pago exitoso'})
    
    # Si el carrito ya estaba vacío (ej. doble click)
    return jsonify({'success': False, 'message': 'El carrito está vacío'}), 400


# --- RUTA PARA ELIMINAR ÍTEM DEL CARRITO ---
# Ahora acepta la item_key (string) en lugar del ID (int)
@app.route("/eliminar/<item_key>")
def eliminar(item_key):
    """Elimina un ítem específico (por item_key) del carrito."""
    carrito = session.get("carrito", [])
    
    # Filtrar el carrito para remover el ítem con la item_key dada
    nuevo_carrito = [item for item in carrito if item["item_key"] != item_key]
    
    if len(nuevo_carrito) < len(carrito):
        # Si la longitud cambió, significa que se eliminó algo.
        session["carrito"] = nuevo_carrito
        session.modified = True
    
    return redirect(url_for("carrito"))

if __name__ == '__main__':
    # La aplicación Flask se ejecutará en un puerto disponible
    # En un entorno real, se usaría un servidor WSGI como Gunicorn.
    port = int(os.environ.get("PORT", 5000))
    # Para el entorno de Canvas, es mejor no usar debug=True para evitar problemas de recarga.
    app.run(host='0.0.0.0', port=port)