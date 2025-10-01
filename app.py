from flask import Flask, render_template, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = "clave-secreta"  # Necesario para manejar sesiones

# Productos de ejemplo con rutas de imágenes
productos = [
    {"id": 1, "nombre": "Laptop Pro", "precio": 1200, "imagen": "https://placehold.co/600x400/EEE/31343C?text=Laptop+Pro"},
    {"id": 2, "nombre": "Auriculares Inalámbricos", "precio": 50, "imagen": "https://placehold.co/600x400/EEE/31343C?text=Auriculares"},
    {"id": 3, "nombre": "Mouse Gamer RGB", "precio": 30, "imagen": "https://placehold.co/600x400/EEE/31343C?text=Mouse+Gamer"},
    {"id": 4, "nombre": "Teclado Mecánico", "precio": 80, "imagen": "https://placehold.co/600x400/EEE/31343C?text=Teclado"}
]

@app.route("/")
def index():
    """Renderiza la página principal de la tienda y pasa la cantidad total del carrito."""
    carrito = session.get('carrito', [])
    total_cantidad = sum(item.get('cantidad', 0) for item in carrito)
    return render_template("index.html", productos=productos, total_cantidad=total_cantidad)

@app.route("/agregar/<int:id>")
def agregar(id):
    """Agrega o incrementa la cantidad de un producto en el carrito (fallback sin JS)."""
    if "carrito" not in session:
        session["carrito"] = []
    
    producto = next((p for p in productos if p["id"] == id), None)
    if producto:
        item_existente = next((item for item in session["carrito"] if item["id"] == id), None)
        if item_existente:
            item_existente["cantidad"] += 1
        else:
            nuevo_item = producto.copy()
            nuevo_item["cantidad"] = 1
            session["carrito"].append(nuevo_item)
        session.modified = True

    return redirect(url_for("index"))

@app.route("/api/agregar/<int:id>", methods=['POST'])
def api_agregar(id):
    """Endpoint de API para agregar un producto y devolver la nueva cantidad total."""
    if "carrito" not in session:
        session["carrito"] = []
    
    producto = next((p for p in productos if p["id"] == id), None)
    if producto:
        item_existente = next((item for item in session["carrito"] if item["id"] == id), None)
        if item_existente:
            item_existente["cantidad"] += 1
        else:
            nuevo_item = producto.copy()
            nuevo_item["cantidad"] = 1
            session["carrito"].append(nuevo_item)
        session.modified = True
    
    total_cantidad = sum(item.get('cantidad', 0) for item in session.get("carrito", []))
    return jsonify({'total_cantidad': total_cantidad})


@app.route("/eliminar/<int:id>")
def eliminar(id):
    """Elimina un producto del carrito de compras."""
    if "carrito" in session:
        session["carrito"] = [item for item in session["carrito"] if item["id"] != id]
        session.modified = True
    return redirect(url_for("carrito"))

@app.route("/cambiar_cantidad/<int:id>/<int:cantidad>")
def cambiar_cantidad(id, cantidad):
    """Cambia la cantidad de un producto en el carrito."""
    if "carrito" in session:
        item_existente = next((item for item in session["carrito"] if item["id"] == id), None)
        if item_existente:
            item_existente["cantidad"] = cantidad
            if item_existente["cantidad"] <= 0:
                return redirect(url_for("eliminar", id=id))
            session.modified = True
    return redirect(url_for("carrito"))

@app.route("/carrito")
def carrito():
    """Muestra el contenido del carrito de compras."""
    carrito = session.get("carrito", [])
    total = sum(p["precio"] * p["cantidad"] for p in carrito) if carrito else 0
    return render_template("carrito.html", carrito=carrito, total=total)

@app.route("/vaciar")
def vaciar():
    """Vacía el carrito de compras."""
    session.pop("carrito", None)
    return redirect(url_for("carrito"))

if __name__ == "__main__":
    app.run(debug=True)
