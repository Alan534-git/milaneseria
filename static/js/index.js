// Datos de los refrescos para el script
const refrescoData = {
    '1': 1.50, // Coca-Cola
    '2': 1.75, // Pepsi
    '3': 1.25, // Sprite
    '4': 1.60, // Fanta
    '5': 1.00, // 7Up
    '6': 0.75  // Manaos (nuevo)
};

document.addEventListener('DOMContentLoaded', function() {
    const cartCountSpan = document.getElementById('cart-count');
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
    // 2. LÓGICA DE SELECCIÓN DE REFRESCO Y PRECIO
    // ---------------------------------
    document.querySelectorAll('.producto-card').forEach(card => {
        const basePriceElement = card.querySelector('.precio-base span');
        const btnAgregar = card.querySelector('.btn-agregar');
        const refreshButtons = card.querySelectorAll('.btn-refresco');

        if (!basePriceElement || !btnAgregar) return;

        const basePriceText = basePriceElement.textContent.replace('$', '');
        const basePrice = parseFloat(basePriceText.trim());

        // Manejador de clic para botones de refresco
        refreshButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                // Remover la clase 'selected' de todos los botones en esta tarjeta
                refreshButtons.forEach(b => b.classList.remove('selected'));
                // Añadir 'selected' al botón actual
                btn.classList.add('selected');

                const refrescoId = btn.dataset.refrescoId;
                const refrescoPrice = parseFloat(btn.dataset.price);
                
                // Actualizar el precio en el botón de agregar
                const newTotalPrice = basePrice + refrescoPrice;
                const priceSpan = btnAgregar.querySelector('.initial-price');
                if (priceSpan) {
                    priceSpan.textContent = newTotalPrice.toFixed(2);
                }

                // Almacenar el ID y precio del refresco seleccionado en el botón de agregar
                btnAgregar.dataset.refrescoId = refrescoId;
                btnAgregar.dataset.refrescoPrice = refrescoPrice;
            });
        });
    });
    
    // ---------------------------------
    // 3. LÓGICA DE AGREGAR AL CARRITO (Fetch)
    // ---------------------------------
    document.querySelectorAll('.btn-agregar').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault(); // Evita la navegación

            const productId = this.dataset.productId;
            const refrescoId = this.dataset.refrescoId || '0'; // '0' es el valor por defecto ('Sin Refresco')
            
            // *** CORRECCIÓN CRÍTICA DE LA RUTA: Usamos la ruta correcta /agregar/<id> ***
            // La URL en el HTML es /agregar/{{ p.id }}
            const url = this.getAttribute('href') + `?refresco_id=${refrescoId}`;
            
            fetch(url, {
                method: 'GET', // La ruta en Flask es GET, por eso mantenemos GET
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    // Si la respuesta HTTP no es 2xx, lanza un error
                    throw new Error('La respuesta de la red no fue correcta');
                }
                return response.json();
            })
            .then(data => {
                if (data.success && cartCountSpan) {
                    // Actualiza el contador del carrito
                    cartCountSpan.textContent = data.total_cantidad;
                    
                    // Opcional: Mostrar una retroalimentación visual al usuario
                    button.classList.add('added');
                    setTimeout(() => button.classList.remove('added'), 500);

                } else if (!data.success) {
                     // Si Flask retorna JSON con success: false
                     throw new Error(data.message || 'Error desconocido del servidor.');
                }
            })
            .catch(error => {
                console.error('Hubo un problema con la operación de fetch:', error);
                // Muestra un mensaje de error al usuario (opcional)
                alert('Error al agregar al carrito. Revisa la consola.'); // Usamos alert solo como fallback
            });
        });
    });

    // ---------------------------------
    // 4. LÓGICA DE INICIALIZACIÓN
    // ---------------------------------
    document.querySelectorAll('.producto-card').forEach(card => {
        const basePriceElement = card.querySelector('.precio-base span');
        const btnAgregar = card.querySelector('.btn-agregar');

        if (basePriceElement && btnAgregar) {
            const basePriceText = basePriceElement.textContent.replace('$', '');
            const basePrice = parseFloat(basePriceText.trim());
            
            // Inicializar el precio en el botón "Agregar al Carrito"
            const priceSpan = btnAgregar.querySelector('.initial-price');
            if (priceSpan) {
                priceSpan.textContent = basePrice.toFixed(2);
            }

            // Selecciona el botón "Sin Refresco" por defecto
            const sinRefrescoBtn = card.querySelector('.btn-refresco[data-refresco-id="0"]');
            if (sinRefrescoBtn) {
                sinRefrescoBtn.classList.add('selected');
                btnAgregar.dataset.refrescoId = '0'; // Asegura que el ID de refresco por defecto esté en el botón
            }
        }
    });
});
