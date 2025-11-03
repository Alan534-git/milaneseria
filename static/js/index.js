// Datos de los refrescos para el script
const refrescoData = {
    '1': 1.50, // Coca-Cola
    '2': 1.75, // Pepsi
    '3': 1.25, // Sprite
    '4': 1.60, // Fanta
    '5': 1.00, // 7Up
    '6': 0.75  // Manaos (nuevo)
};

// Función para calcular el precio total basado en el precio base, refresco y cantidad
function updateTotalPrice(card) {
    const basePrice = parseFloat(card.querySelector('.precio-base span').dataset.basePrice);
    const selectedRefrescoBtn = card.querySelector('.btn-refresco.selected');
    const refrescoPrice = parseFloat(selectedRefrescoBtn.dataset.price);
    const cantidad = parseInt(card.querySelector('.input-cantidad').value);

    const unitPrice = basePrice + refrescoPrice;
    const totalPrice = unitPrice * cantidad;

    // Actualiza el texto del botón "Agregar"
    const btnAgregar = card.querySelector('.btn-agregar');
    const priceSpan = btnAgregar.querySelector('.total-price');
    const cantidadSpan = btnAgregar.querySelector('.cantidad-display');
    
    // Almacena los IDs y la cantidad en los dataset del botón para el envío
    btnAgregar.dataset.refrescoId = selectedRefrescoBtn.dataset.refrescoId;
    btnAgregar.dataset.cantidad = cantidad;

    priceSpan.textContent = totalPrice.toFixed(2);
    cantidadSpan.textContent = cantidad;
}

// Función para actualizar el contador del carrito en el header
function updateCartCount(newCount) {
    const cartCountSpan = document.getElementById('cart-count');
    if (cartCountSpan) {
        cartCountSpan.textContent = newCount;
        // Muestra u oculta el badge
        cartCountSpan.style.display = newCount > 0 ? 'inline-block' : 'none';
    }
}


document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');

    // ---------------------------------
    // 1. LÓGICA DE MODO CLARO/OSCURO
    // ---------------------------------
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme) {
        document.body.classList.toggle('dark-mode', storedTheme === 'dark');
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        // Establecer modo oscuro por defecto si el sistema lo prefiere
        document.body.classList.add('dark-mode');
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            const isDarkMode = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        });
    }

    // ---------------------------------
    // 2. LÓGICA DE SELECCIÓN DE REFRESCO
    // ---------------------------------
    document.querySelectorAll('.refresco-botones').forEach(container => {
        container.addEventListener('click', (event) => {
            const btn = event.target.closest('.btn-refresco');
            if (btn) {
                // Quitar 'selected' de todos los hermanos
                container.querySelectorAll('.btn-refresco').forEach(b => b.classList.remove('selected'));
                // Agregar 'selected' al botón clickeado
                btn.classList.add('selected');

                // Recalcular el precio total
                const card = btn.closest('.producto-card');
                if (card) {
                    updateTotalPrice(card);
                }
            }
        });
    });

    // ---------------------------------
    // 3. LÓGICA DE CAMBIO DE CANTIDAD
    // ---------------------------------
    document.querySelectorAll('.input-cantidad').forEach(input => {
        input.addEventListener('change', (event) => {
            let value = parseInt(input.value);
            
            // Validar que la cantidad sea al menos 1
            if (isNaN(value) || value < 1) {
                value = 1;
                input.value = 1;
            }
            // Limitar a un máximo razonable (ej. 99)
            if (value > 99) {
                value = 99;
                input.value = 99;
            }

            // Recalcular el precio total
            const card = input.closest('.producto-card');
            if (card) {
                updateTotalPrice(card);
            }
        });
    });

    // ---------------------------------
    // 4. LÓGICA DE AGREGAR AL CARRITO (POST/JSON)
    // ---------------------------------
    document.querySelectorAll('.btn-agregar').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            const productId = button.dataset.productId;
            const refrescoId = button.dataset.refrescoId;
            const cantidad = button.dataset.cantidad; // Obtenida de updateTotalPrice

            // Deshabilitar botón para prevenir doble click
            button.disabled = true;
            button.textContent = 'Agregando...';

            // Crear el objeto de datos a enviar
            const postData = {
                product_id: productId,
                refresco_id: refrescoId,
                cantidad: cantidad 
            };
            
            // Usar fetch para enviar datos como JSON (POST)
            fetch('/agregar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(postData),
            })
            .then(response => {
                // Si la respuesta no es 200 OK, lanzar un error para ir al catch
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.message || 'Error al agregar al carrito.'); });
                }
                return response.json();
            })
            .then(data => {
                // Éxito:
                console.log('Respuesta del servidor:', data);
                
                // 1. Actualiza el contador del carrito
                if (data.cart_count !== undefined) {
                    updateCartCount(data.cart_count);
                }

                // 2. Opcional: Mostrar una confirmación visual rápida (ej. animación)
                button.textContent = '✅ Agregado';
                setTimeout(() => {
                    const card = button.closest('.producto-card');
                    if (card) {
                        updateTotalPrice(card); // Restaura el texto y precio
                    }
                    button.disabled = false;
                    button.textContent = `➕ Agregar ${cantidad} al carrito ($${button.querySelector('.total-price').textContent})`;
                }, 800);

            })
            .catch(error => {
                // Fallo:
                console.error('Hubo un problema con la operación de fetch:', error);
                // Restaurar el botón
                button.disabled = false;
                button.textContent = '❌ Error';
                setTimeout(() => {
                     const card = button.closest('.producto-card');
                    if (card) {
                        updateTotalPrice(card);
                    }
                }, 800);
            });
        });
    });

    // ---------------------------------
    // 5. LÓGICA DE INICIALIZACIÓN
    // ---------------------------------
    document.querySelectorAll('.producto-card').forEach(card => {
        const btnAgregar = card.querySelector('.btn-agregar');
        const inputCantidad = card.querySelector('.input-cantidad');

        if (btnAgregar && inputCantidad) {
            // Selecciona el botón "Sin Refresco" por defecto
            const sinRefrescoBtn = card.querySelector('.btn-refresco[data-refresco-id="0"]');
            if (sinRefrescoBtn) {
                sinRefrescoBtn.classList.add('selected');
                btnAgregar.dataset.refrescoId = '0'; // Asegura que el ID de refresco por defecto esté en el botón
            }
            
            // Inicializar el precio y cantidad en el botón "Agregar al Carrito"
            updateTotalPrice(card);
        }
    });
});
