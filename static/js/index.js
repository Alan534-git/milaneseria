// Datos de los refrescos para el script
const refrescoData = {
    '1': 1.50, // Coca-Cola
    '2': 1.75, // Pepsi
    '3': 1.25, // Sprite
    '4': 1.60, // Fanta
    '5': 1.00, // 7Up
    '6': 0.75  // Manaos (nuevo)
};

/**
 * CAMBIO: Función para calcular el precio total.
 * Ahora usa la cantidad de milanesas y la cantidad de refrescos por separado.
 */
function updateTotalPrice(card) {
    const basePrice = parseFloat(card.querySelector('.precio-base span').dataset.basePrice);
    const selectedRefrescoBtn = card.querySelector('.btn-refresco.selected');
    const refrescoPrice = parseFloat(selectedRefrescoBtn.dataset.price);
    
    // Leer las dos cantidades
    const cantMilanesa = parseInt(card.querySelector('.input-cantidad-milanesa').value);
    const cantRefresco = parseInt(card.querySelector('.input-cantidad-refresco').value);

    // Validar que las cantidades sean números válidos
    const validCantMilanesa = (isNaN(cantMilanesa) || cantMilanesa < 1) ? 1 : cantMilanesa;
    const validCantRefresco = (isNaN(cantRefresco) || cantRefresco < 0) ? 0 : cantRefresco;

    // Si el refresco seleccionado es "Sin Refresco", forzar la cantidad de refresco a 0
    const finalCantRefresco = selectedRefrescoBtn.dataset.refrescoId === '0' ? 0 : validCantRefresco;
    
    // Si la cantidad de refresco es 0, el precio del refresco es 0
    const finalRefrescoPrice = finalCantRefresco === 0 ? 0.00 : refrescoPrice;

    // Calcular el precio total
    const totalPrice = (basePrice * validCantMilanesa) + (finalRefrescoPrice * finalCantRefresco);

    // Actualiza el botón (solo si es 'btn-agregar', si es 'btn-cancelar' no toca el texto)
    const btnAccion = card.querySelector('.btn-accion-card');
    
    if (btnAccion.classList.contains('btn-agregar')) {
        const priceSpan = btnAccion.querySelector('.total-price');
        
        // Almacena los IDs y las cantidades en los dataset del botón para el envío
        btnAccion.dataset.refrescoId = selectedRefrescoBtn.dataset.refrescoId;
        btnAccion.dataset.cantidadMilanesa = validCantMilanesa;
        btnAccion.dataset.cantidadRefresco = finalCantRefresco;

        // Actualiza el precio en el texto del botón
        priceSpan.textContent = totalPrice.toFixed(2);
    }
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

// Función para mostrar un feedback temporal en el botón
function setButtonFeedback(button, text, isError = false) {
    const originalHTML = button.innerHTML;
    const originalClasses = button.className;
    
    button.disabled = true;
    button.innerHTML = text;
    if (isError) {
        button.classList.add('btn-cancelar'); // Reusamos el estilo gris/rojo
    }

    setTimeout(() => {
        button.disabled = false;
        button.innerHTML = originalHTML;
        button.className = originalClasses;
        
        // Si falló, debemos recalcular el precio para restaurar el botón
        if (isError) {
            const card = button.closest('.producto-card');
            if (card) {
                updateTotalPrice(card);
            }
        }
    }, 1000);
}

// CAMBIO: Nueva función para manejar el clic en "Agregar"
async function handleAgregar(button) {
    const card = button.closest('.producto-card');
    const productId = button.dataset.productId;
    const refrescoId = button.dataset.refrescoId;
    const cantidadMilanesa = button.dataset.cantidadMilanesa;
    const cantidadRefresco = button.dataset.cantidadRefresco;

    button.disabled = true;
    button.innerHTML = 'Agregando...';

    // Crear el objeto de datos a enviar
    const postData = {
        product_id: productId,
        refresco_id: refrescoId,
        cantidad_milanesa: cantidadMilanesa,
        cantidad_refresco: cantidadRefresco
    };

    try {
        const response = await fetch('/agregar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(postData),
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.message || 'Error al agregar.');
        }

        const data = await response.json();
        
        // Éxito:
        updateCartCount(data.cart_count);

        // Transformar en botón de "Cancelar"
        button.innerHTML = '✅ Agregado (Cancelar)';
        button.classList.remove('btn-agregar');
        button.classList.add('btn-cancelar');
        button.dataset.itemKey = data.item_key; // Guardamos el ID del item creado
        button.disabled = false;

    } catch (error) {
        console.error('Hubo un problema con la operación de fetch:', error);
        // Mostrar error y restaurar
        button.disabled = false;
        button.innerHTML = '❌ Error';
        setTimeout(() => {
             if (card) {
                // Restaura el botón al estado original
                button.innerHTML = `➕ Agregar al carrito ($<span class="total-price">0.00</span>)`;
                updateTotalPrice(card);
             }
        }, 1000);
    }
}

// CAMBIO: Nueva función para manejar el clic en "Cancelar"
async function handleCancelar(button) {
    const card = button.closest('.producto-card');
    const itemKey = button.dataset.itemKey;

    if (!itemKey) return;

    button.disabled = true;
    button.innerHTML = 'Cancelando...';

    try {
        // Usamos la nueva API para eliminar
        const response = await fetch('/api/eliminar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_key: itemKey }),
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.message || 'Error al cancelar.');
        }

        const data = await response.json();

        // Éxito:
        updateCartCount(data.cart_count);

        // Restaurar el botón a "Agregar"
        button.innerHTML = `➕ Agregar al carrito ($<span class="total-price">0.00</span>)`; // Texto base
        button.classList.remove('btn-cancelar');
        button.classList.add('btn-agregar');
        delete button.dataset.itemKey; // Limpiamos el ID
        button.disabled = false;
        
        // Recalculamos el precio para el botón
        if (card) {
            updateTotalPrice(card);
        }

    } catch (error) {
        console.error('Hubo un problema con la operación de fetch:', error);
        // Mostrar error y restaurar
        button.disabled = false;
        button.innerHTML = '❌ Error'; // Mantenemos el estado de "Cancelar" si falla
        setTimeout(() => {
            button.innerHTML = '✅ Agregado (Cancelar)';
            button.disabled = false;
        }, 1000);
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
                container.querySelectorAll('.btn-refresco').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                
                const card = btn.closest('.producto-card');
                if (card) {
                    const inputRefresco = card.querySelector('.input-cantidad-refresco');
                    // Si eligen "Sin Refresco", pone la cantidad de refresco a 0
                    if (btn.dataset.refrescoId === '0') {
                        inputRefresco.value = 0;
                    } else if (inputRefresco.value === '0') {
                        // Si eligen un refresco y la cantidad era 0, la pone a 1
                        inputRefresco.value = 1;
                    }
                    updateTotalPrice(card);
                }
            }
        });
    });

    // ---------------------------------
    // 3. LÓGICA DE CAMBIO DE CANTIDAD
    // ---------------------------------
    // CAMBIO: Ahora escucha a los dos inputs
    document.querySelectorAll('.input-cantidad').forEach(input => {
        input.addEventListener('change', (event) => {
            const card = input.closest('.producto-card');
            
            // Si cambian la cantidad de refresco a 0, selecciona "Sin Refresco"
            if (input.classList.contains('input-cantidad-refresco') && input.value === '0') {
                card.querySelectorAll('.btn-refresco').forEach(b => b.classList.remove('selected'));
                card.querySelector('.btn-refresco[data-refresco-id="0"]').classList.add('selected');
            }
            // Si cambian la cantidad de refresco a > 0 y estaba "Sin Refresco"
            else if (input.classList.contains('input-cantidad-refresco') && input.value > '0') {
                const selectedBtn = card.querySelector('.btn-refresco.selected');
                if (selectedBtn && selectedBtn.dataset.refrescoId === '0') {
                    // Selecciona el primer refresco real (ej. Coca-Cola)
                    selectedBtn.classList.remove('selected');
                    card.querySelector('.btn-refresco[data-refresco-id="1"]').classList.add('selected');
                }
            }
            
            if (card) {
                updateTotalPrice(card);
            }
        });
    });

    // ---------------------------------
    // 4. LÓGICA DE AGREGAR/CANCELAR CARRITO (DELEGACIÓN)
    // ---------------------------------
    const productosContainer = document.querySelector('.productos-container');
    if (productosContainer) {
        productosContainer.addEventListener('click', (event) => {
            const btnAgregar = event.target.closest('.btn-agregar');
            if (btnAgregar) {
                event.preventDefault();
                handleAgregar(btnAgregar);
                return;
            }

            const btnCancel = event.target.closest('.btn-cancelar');
            if (btnCancel) {
                event.preventDefault();
                handleCancelar(btnCancel);
                return;
            }
        });
    }


    // ---------------------------------
    // 5. LÓGICA DE INICIALIZACIÓN
    // ---------------------------------
    document.querySelectorAll('.producto-card').forEach(card => {
        // Selecciona el botón "Sin Refresco" por defecto
        const sinRefrescoBtn = card.querySelector('.btn-refresco[data-refresco-id="0"]');
        if (sinRefrescoBtn) {
            sinRefrescoBtn.classList.add('selected');
        }
        
        // Ponemos la cantidad de refresco a 0 por defecto si "Sin Refresco" está seleccionado
        const inputRefresco = card.querySelector('.input-cantidad-refresco');
        if (sinRefrescoBtn.classList.contains('selected')) {
            inputRefresco.value = 0;
        }

        // Inicializar el precio y cantidad en el botón "Agregar al Carrito"
        updateTotalPrice(card);
    });
});