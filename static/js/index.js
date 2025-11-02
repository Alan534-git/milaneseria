    // Datos de los refrescos para el script
    const refrescoData = {
        '1': 1.50, // Coca-Cola
        '2': 1.75, // Pepsi
        '3': 1.25, // Sprite
        '4': 1.60, // Fanta
        '5': 1.00  // 7Up
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

        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            const isDarkMode = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        });


        // ---------------------------------
        // 2. LÓGICA DE SELECCIÓN DE REFRESCOS
        // ---------------------------------

        const productoCards = document.querySelectorAll('.producto-card');

        productoCards.forEach(card => {
            const selector = card.querySelector('.refrescos-selector');
            const basePrice = parseFloat(selector.dataset.basePrice);
            const precioDisplay = card.querySelector('.milanesa-precio');
            const btnAgregar = card.querySelector('.btn-agregar');
            const refreshButtons = card.querySelectorAll('.btn-refresco');

            // Función para actualizar el precio y el data-attribute
            const updatePrice = (refrescoPrice) => {
                const newTotalPrice = basePrice + refrescoPrice;
                // Actualiza la visualización del precio
                precioDisplay.textContent = newTotalPrice.toFixed(2);
                // Actualiza el atributo que se usará para el envío al servidor (simulado)
                btnAgregar.dataset.refrescoPrice = refrescoPrice.toFixed(2);
                // Actualiza el texto del botón Agregar
                btnAgregar.textContent = `➕ Agregar al carrito ($${newTotalPrice.toFixed(2)})`;
            };

            // Inicializar el botón de agregar con el precio base
            updatePrice(0);


            refreshButtons.forEach(btn => {
                const price = parseFloat(btn.dataset.price);

                // Manejar la selección del refresco
                btn.addEventListener('click', () => {
                    let refrescoPrice = 0;
                    
                    // Si el botón ya está seleccionado, lo deseleccionamos
                    if (btn.classList.contains('selected')) {
                        btn.classList.remove('selected');
                        // El precio del refresco es 0, volvemos solo al precio base
                    } else {
                        // Deselecciona cualquier otro botón en el mismo grupo
                        refreshButtons.forEach(b => b.classList.remove('selected'));
                        
                        // Selecciona el botón actual
                        btn.classList.add('selected');
                        refrescoPrice = price;
                    }

                    // Actualiza el precio
                    updatePrice(refrescoPrice);
                });
            });


            // ---------------------------------
            // 3. LÓGICA DE AGREGAR AL CARRITO (AJAX)
            // ---------------------------------
            btnAgregar.addEventListener('click', function(event) {
                // Previene el comportamiento por defecto del enlace
                event.preventDefault();

                // Aquí obtenemos el precio del refresco seleccionado.
                // IMPORTANTE: Dado que la lógica del servidor (app.py) espera solo el ID,
                // este precio de refresco es solo para *fines visuales y de demo*.
                // En una app real, el precio del refresco y su ID DEBERÍAN
                // enviarse al servidor para ser incluidos como un ítem de línea.
                
                const productId = this.dataset.productId;
                const url = `/api/agregar/${productId}`;

                // Usa la API Fetch para enviar una solicitud POST al servidor
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('La respuesta de la red no fue correcta');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.total_cantidad !== undefined) {
                        // Actualiza el número en el botón del carrito
                        cartCountSpan.textContent = data.total_cantidad;
                    }
                })
                .catch(error => {
                    console.error('Hubo un problema con la operación de fetch:', error);
                });
            });
        });
    });