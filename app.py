from flask import Flask, render_template, redirect, url_for, session, jsonify, request
import os

# NOTA: La clave secreta debe ser una cadena de bytes aleatoria en producción
# Para Canvas, usamos un valor placeholder.
app = Flask(__name__)
app.secret_key = "clave-secreta"  # Necesario para manejar sesiones

# --- PRODUCTOS ACTUALIZADOS A MILANESAS ---
productos = [
    {"id": 1, "nombre": "Milanesa Napolitana", "precio": 25, "imagen": "https://placehold.co/600x400/D9534F/FFF?text=Milanesa+Napolitana"},
    {"id": 2, "nombre": "Milanesa a Caballo", "precio": 22, "imagen": "https://placehold.co/600x400/A67B5B/FFF?text=Milanesa+a+Caballo"},
    {"id": 3, "nombre": "Milanesa Fugazzeta", "precio": 24, "imagen": "https://placehold.co/600x400/FFC107/333?text=Milanesa+Fugazzeta"},
    {"id": 4, "nombre": "Milanesa Cheddar y Bacon", "precio": 26, "imagen": "https://placehold.co/600x400/E67E22/FFF?text=Milanesa+Cheddar"}
]
# --- FIN DE CAMBIOS EN PRODUCTOS ---

@app.route("/")
def index():
    """Renderiza la página principal de la tienda y pasa la cantidad total del carrito."""
    carrito = session.get("carrito", [])
    total_cantidad = sum(p["cantidad"] for p in carrito)
    return render_template("index.html", productos=productos, total_cantidad=total_cantidad)

# --- ENDPOINT ACTUALIZADO: ACEPTA POST Y DEVUELVE JSON ---
@app.route("/api/agregar/<int:id>", methods=['POST'])
def api_agregar(id):
    """
    Agrega un producto al carrito y devuelve la nueva cantidad total en formato JSON.
    Se utiliza para la comunicación AJAX con el botón "Agregar al carrito".
    """
    producto_a_agregar = next((p for p in productos if p["id"] == id), None)
    
    if not producto_a_agregar:
        return jsonify({'error': 'Producto no encontrado'}), 404

    carrito = session.get("carrito", [])
    item_existente = next((item for item in carrito if item["id"] == id), None)

    if item_existente:
        item_existente["cantidad"] += 1
    else:
        # Se agrega una copia del producto con cantidad inicial
        nuevo_item = producto_a_agregar.copy()
        nuevo_item["cantidad"] = 1
        carrito.append(nuevo_item)

    session["carrito"] = carrito
    session.modified = True
    
    total_cantidad = sum(p["cantidad"] for p in carrito)
    
    # Devuelve una respuesta JSON que el frontend espera
    return jsonify({'success': True, 'total_cantidad': total_cantidad})

# --- RUTA ORIGINAL DE AGREGAR (redirige si se accede directamente) ---
@app.route("/agregar/<int:id>")
def agregar(id):
    """Función de redirección para compatibilidad, aunque se usa /api/agregar."""
    # En un entorno real, esta ruta solo debería ser un redirect si se usa AJAX
    # En este caso, redirigimos al inicio si se accede directamente.
    return redirect(url_for("index"))
# ---------------------------------------------------------------------

@app.route("/eliminar/<int:id>")
def eliminar(id):
    """Elimina un producto completamente del carrito."""
    carrito = session.get("carrito", [])
    
    # Filtrar el carrito para remover el producto con el ID dado
    carrito = [p for p in carrito if p["id"] != id]
    
    session["carrito"] = carrito
    session.modified = True
    return redirect(url_for("carrito"))

@app.route("/cambiar_cantidad/<int:id>/<int:cantidad>")
def cambiar_cantidad(id, cantidad):
    """Cambia la cantidad de un producto en el carrito."""
    if cantidad < 0:
        cantidad = 0

    carrito = session.get("carrito", [])
    item_existente = next((item for item in carrito if item["id"] == id), None)

    if item_existente:
        item_existente["cantidad"] = cantidad
        if item_existente["cantidad"] <= 0:
            # Si la cantidad es cero o menos, eliminar el ítem
            return redirect(url_for("eliminar", id=id))
        session.modified = True
        
    return redirect(url_for("carrito"))

@app.route("/carrito")
def carrito():
    """Muestra el contenido del carrito de compras."""
    carrito = session.get("carrito", [])
    total = sum(p["precio"] * p["cantidad"] for p in carrito) if carrito else 0
    
    # Para el pago, usamos una simulación de total
    total_pago = total
    
    return render_template("carrito.html", carrito=carrito, total=total_pago)

@app.route("/vaciar")
def vaciar():
    """Vacía el carrito de compras."""
    session.pop("carrito", None)
    return redirect(url_for("carrito"))

# --- RUTA PARA SIMULAR EL PAGO ---
@app.route("/api/procesar_pago", methods=['POST'])
def api_procesar_pago():
    """Simula el procesamiento de un pago y vacía el carrito."""
    
    # Simulamos un pago exitoso vaciando el carrito
    if "carrito" in session and session["carrito"]:
        session.pop("carrito", None)
        session.modified = True
        return jsonify({'success': True, 'message': 'Pago exitoso. Carrito vaciado.'})
    else:
        # Retorna error si el carrito ya está vacío
        return jsonify({'success': False, 'message': 'El carrito ya está vacío.'}), 400

if __name__ == "__main__":
    app.run(debug=True)
