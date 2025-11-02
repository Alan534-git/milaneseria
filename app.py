from flask import Flask, render_template, redirect, url_for, session, jsonify, request
import os

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
refresco_nombres = {
    '0': 'Sin Refresco',
    '1': 'Coca-Cola',
    '2': 'Pepsi',
    '3': 'Sprite',
    '4': 'Fanta',
    '5': '7Up',
    '6': 'Manaos'
}

# Configuración de los datos del carrito
# El carrito se almacena en la sesión del usuario como una lista de diccionarios:
# [{"id": 1, "nombre": "Milanesa Napolitana", "precio": 25, "refresco_id": "1", "item_key": "..."}]

# --- RUTA PRINCIPAL ---
@app.route("/")
def index():
    """Muestra la lista de productos y el conteo del carrito."""
    total_cantidad = sum(item.get('cantidad', 1) for item in session.get('carrito', []))
    
    # Renderizar la plantilla principal con los productos y el conteo del carrito
    return render_template("index.html", productos=productos, total_cantidad=total_cantidad)

# --- RUTA DEL CARRITO ---
@app.route("/carrito")
def carrito():
    """Muestra el contenido del carrito."""
    carrito = session.get("carrito", [])
    total_precio = 0.0
    
    # Lógica para recalcular y enriquecer los datos del carrito para la plantilla
    # Esto asegura que todas las claves requeridas por la plantilla (carrito.html) existan.
    for item in carrito:
        milanesa_precio = item.get('precio', 0.0)
        refresco_id = item.get('refresco_id', '0')
        refresco_precio = refresco_precios.get(refresco_id, 0.0)

        # 1. Asegura que precio_total exista
        item['precio_total'] = milanesa_precio + refresco_precio
        
        # 2. Asegura que refresco_nombre exista
        item['refresco_nombre'] = refresco_nombres.get(refresco_id, 'Desconocido')
        
        # 3. Asegura que item_key exista (debería existir si se agregó correctamente)
        if 'item_key' not in item:
             # Si falta la clave, le asignamos una por seguridad (aunque debería venir del agregar)
            import uuid
            item['item_key'] = str(uuid.uuid4())

        total_precio += item['precio_total']

    # Renderizar la plantilla del carrito con el carrito y el total
    return render_template("carrito.html", carrito=carrito, total=total_precio)

# --- RUTA PARA AGREGAR AL CARRITO (AJAX/Fetch) ---
@app.route("/agregar/<int:producto_id>", methods=['GET', 'POST'])
def agregar(producto_id):
    """Agrega un producto con un refresco al carrito."""
    
    # Encuentra el producto base
    producto_base = next((p for p in productos if p['id'] == producto_id), None)

    if not producto_base:
        return jsonify({'success': False, 'message': 'Producto no encontrado'}), 404

    # Determina el ID del refresco. Por defecto, '0' (Sin Refresco)
    # En la práctica, esto debería venir del POST request, pero se asume un valor por defecto seguro.
    refresco_id = request.args.get('refresco_id', '0')
    
    # Obtener nombre y precio del refresco
    refresco_nombre = refresco_nombres.get(refresco_id, 'Sin Refresco')
    refresco_precio = refresco_precios.get(refresco_id, 0.0)

    # Crear la clave única para este ítem combinado (Milanesa + Refresco)
    import uuid
    item_key = str(uuid.uuid4())

    # Crear el nuevo ítem del carrito
    nuevo_item = {
        'id': producto_base['id'],
        'nombre': producto_base['nombre'],
        # *** IMPORTANTE: Usamos url_for para generar la ruta correcta para el carrito.html ***
        'imagen': url_for('static', filename=f'img/{producto_base["imagen"]}'),
        'precio': producto_base['precio'], # Precio base de la milanesa
        'refresco_id': refresco_id,
        'refresco_nombre': refresco_nombre,
        'precio_total': producto_base['precio'] + refresco_precio,
        'item_key': item_key
    }
    
    # Agregar a la sesión
    carrito = session.get('carrito', [])
    carrito.append(nuevo_item)
    session['carrito'] = carrito
    session.modified = True

    # Calcular la nueva cantidad total para actualizar el ícono del carrito
    total_cantidad = len(carrito)
    
    # La respuesta para llamadas asíncronas (desde index.js)
    return jsonify({'success': True, 'total_cantidad': total_cantidad})

# --- RUTA PARA VACIAR EL CARRITO ---
@app.route("/vaciar")
def vaciar():
    """Vacía completamente el carrito."""
    session.pop("carrito", None)
    session.modified = True
    return redirect(url_for("carrito"))

# --- RUTA PARA SIMULAR EL PAGO ---
@app.route("/api/procesar_pago", methods=['POST'])
def api_procesar_pago():
    """Simula el procesamiento de un pago y vacía el carrito."""
    
    # Simulamos un pago exitoso vaciando el carrito
    if "carrito" in session and session["carrito"]:
        # NOTA: La llamada a session.pop("carrito", None) elimina el carrito
        # El JavaScript en carrito.js lo vacía tras el éxito
        
        # Mantengo la lógica de vaciado aquí ya que es la API la que 'confirma' la transacción
        session.pop("carrito", None)
        session.modified = True
        return jsonify({'success': True, 'message': 'Pago exitoso'})
        
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
    # Usar un puerto diferente para evitar conflictos con XAMPP si está corriendo en 80/443
    # Y asegurar que la sesión funciona correctamente en el entorno de desarrollo
    app.run(debug=True, port=5000)
