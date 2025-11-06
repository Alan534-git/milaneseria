from flask import Flask, render_template, redirect, url_for, session, jsonify, request
import os
import uuid # Necesario para generar item_key únicas

# NOTA: La clave secreta debe ser una cadena de bytes aleatoria en producción
# Para Canvas, usamos un valor placeholder.
app = Flask(__name__)
app.secret_key = "clave-secreta"  # Necesario para manejar sesiones

# --- PRODUCTOS ACTUALIZADOS A MILANESAS ---
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

# CAMBIO: Función para calcular el conteo del carrito (basado en milanesas)
def get_cart_count(carrito):
    """Calcula la cantidad total de milanesas en el carrito."""
    return sum(item.get('cantidad_milanesa', 0) for item in carrito)


# --- RUTA PRINCIPAL DE LA TIENDA ---
@app.route("/")
def index():
    """Muestra la lista de productos y el contador del carrito."""
    carrito = session.get("carrito", [])
    _, _, _, total = calcular_totales(carrito) # Se usa el total aquí para mostrar el botón de Carrito
    
    # CAMBIO: Usar la nueva función de conteo
    cart_count = get_cart_count(carrito)
    
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

# --- CAMBIO: RUTA PARA AGREGAR PRODUCTOS (POST) ---
@app.route("/agregar", methods=["POST"])
def agregar_producto():
    """
    Agrega UN ítem (con múltiples cantidades) al carrito.
    Recibe los datos vía POST/JSON.
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Datos inválidos.'}), 400

    producto_id = data.get('product_id')
    refresco_id = str(data.get('refresco_id'))
    try:
        # Leer las nuevas cantidades
        cantidad_milanesa = int(data.get('cantidad_milanesa'))
        cantidad_refresco = int(data.get('cantidad_refresco'))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Cantidad inválida.'}), 400

    if cantidad_milanesa <= 0:
        return jsonify({'success': False, 'message': 'La cantidad de milanesas debe ser mayor a cero.'}), 400
    if cantidad_refresco < 0:
        return jsonify({'success': False, 'message': 'La cantidad de refrescos no puede ser negativa.'}), 400
    
    # Si el refresco es "0" (Sin Refresco), la cantidad de refresco debe ser 0
    if refresco_id == '0':
        cantidad_refresco = 0
    # Si la cantidad de refresco es 0, el refresco es "0" (Sin Refresco)
    elif cantidad_refresco == 0:
        refresco_id = '0'

    producto = obtener_producto(producto_id)
    if not producto:
        return jsonify({'success': False, 'message': 'Producto no encontrado.'}), 404

    # Obtener el precio del refresco
    precio_refresco = refresco_precios.get(refresco_id, 0.00)
    
    # Calcular el precio total del ítem
    precio_total = (producto["precio"] * cantidad_milanesa) + (precio_refresco * cantidad_refresco)
    
    # Construir el nombre del refresco para el carrito
    nombre_refresco_map = {
        '0': "Sin Refresco", '1': "Coca-Cola", '2': "Pepsi", 
        '3': "Sprite", '4': "Fanta", '5': "7Up", '6': "Manaos"
    }
    nombre_refresco = nombre_refresco_map.get(refresco_id, "N/A")
    
    # Obtener la imagen del refresco
    imagen_refresco = refresco_imagenes.get(refresco_id, None)

    # Obtener o inicializar el carrito
    carrito = session.get("carrito", [])

    # Crear el ítem del carrito (UNO solo)
    item_key = str(uuid.uuid4()) # ID única para este pedido
    item = {
        "item_key": item_key,
        "id": producto["id"],
        "nombre": producto["nombre"],
        "precio_base": producto["precio"], 
        "refresco_id": refresco_id,
        "nombre_refresco": nombre_refresco,
        "imagen_refresco": imagen_refresco,
        "precio_refresco": precio_refresco,
        "cantidad_milanesa": cantidad_milanesa, # CAMBIO
        "cantidad_refresco": cantidad_refresco, # CAMBIO
        "precio_total": precio_total, # CAMBIO
        "imagen": producto["imagen"],
    }
    carrito.append(item)

    session["carrito"] = carrito
    session.modified = True

    # Calcular el nuevo conteo del carrito
    cart_count = get_cart_count(carrito)

    # CAMBIO: Devolver el item_key para la función de cancelar
    return jsonify({'success': True, 
                    'message': 'Producto(s) agregado(s) al carrito', 
                    'cart_count': cart_count,
                    'item_key': item_key})


# --- RUTA PARA VACIAR CARRITO ---
@app.route("/vaciar")
def vaciar():
    """Vacía completamente el carrito de compras."""
    session.pop("carrito", None)
    session.modified = True
    return redirect(url_for("carrito"))

# --- RUTA DE API PARA PROCESAR PAGO ---
@app.route("/api/procesar_pago", methods=["POST"])
def procesar_pago():
    """
    Simula el procesamiento del pago (API).
    """
    if "carrito" in session and session["carrito"]:
        session.pop("carrito", None)
        session.modified = True
        return jsonify({'success': True, 'message': 'Pago exitoso'})
    
    return jsonify({'success': False, 'message': 'El carrito está vacío'}), 400


# --- RUTA PARA ELIMINAR ÍTEM DEL CARRITO (Usada por carrito.html) ---
@app.route("/eliminar/<item_key>")
def eliminar(item_key):
    """Elimina un ítem específico (por item_key) del carrito."""
    carrito = session.get("carrito", [])
    
    nuevo_carrito = [item for item in carrito if item["item_key"] != item_key]
    
    if len(nuevo_carrito) < len(carrito):
        session["carrito"] = nuevo_carrito
        session.modified = True
    
    return redirect(url_for("carrito"))

# --- NUEVA RUTA API PARA ELIMINAR (Usada por index.js para "Cancelar") ---
@app.route("/api/eliminar", methods=["POST"])
def api_eliminar():
    """
    Elimina un ítem específico (por item_key) del carrito y devuelve JSON.
    """
    data = request.get_json()
    item_key = data.get('item_key')
    
    if not item_key:
        return jsonify({'success': False, 'message': 'Falta item_key'}), 400

    carrito = session.get("carrito", [])
    nuevo_carrito = [item for item in carrito if item["item_key"] != item_key]
    
    if len(nuevo_carrito) < len(carrito):
        session["carrito"] = nuevo_carrito
        session.modified = True
        cart_count = get_cart_count(nuevo_carrito)
        return jsonify({'success': True, 'message': 'Ítem eliminado', 'cart_count': cart_count})
    else:
        # El ítem no se encontró (quizás ya se canceló)
        cart_count = get_cart_count(carrito)
        return jsonify({'success': False, 'message': 'Ítem no encontrado'}, 404)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)