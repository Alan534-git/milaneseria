    document.addEventListener('DOMContentLoaded', function() {
        // ---------------------------------
        // 1. LÓGICA DE MODO CLARO/OSCURO
        // ---------------------------------
        const themeToggle = document.getElementById('theme-toggle');
        
        const storedTheme = localStorage.getItem('theme');
        if (storedTheme) {
            document.body.classList.toggle('dark-mode', storedTheme === 'dark');
        } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('dark-mode');
        }

        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            const isDarkMode = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        });


        // ---------------------------------
        // 2. LÓGICA DEL MODAL DE PAGO
        // ---------------------------------
        const modal = document.getElementById('modal-pago');
        const btnPagar = document.getElementById('btn-iniciar-pago');
        const btnCerrar = modal.querySelector('.btn-cerrar-modal');
        const paymentForm = document.getElementById('payment-form');
        const formPago = document.getElementById('form-pago');
        const btnSubmitPago = document.getElementById('btn-submit-pago');
        const successMessage = document.getElementById('success-message');
        const errorMessage = document.getElementById('error-message');

        if (btnPagar) {
             btnPagar.addEventListener('click', () => {
                modal.style.display = 'flex';
                // Resetear el estado del modal
                paymentForm.style.display = 'block';
                successMessage.style.display = 'none';
                errorMessage.style.display = 'none';
            });
        }
        
        btnCerrar.addEventListener('click', () => {
            modal.style.display = 'none';
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });

        // Manejo del envío del formulario de pago
        formPago.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Deshabilita el botón y cambia el texto
            btnSubmitPago.disabled = true;
            btnSubmitPago.textContent = 'Procesando...';
            errorMessage.style.display = 'none'; // Oculta errores previos

            // Simulación de la llamada a la API
            fetch('/api/procesar_pago', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Respuesta del servidor no fue OK');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Muestra mensaje de éxito
                    paymentForm.style.display = 'none'; // Oculta el formulario
                    successMessage.style.display = 'block'; // Muestra el éxito

                    // Redirige al inicio después de 2.5 segundos
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 2500);
                } else {
                    // Si la API devuelve success: false
                    throw new Error(data.message || 'Error desconocido');
                }
            })
            .catch(error => {
                // Muestra mensaje de error en caso de fallo del fetch o de la API
                console.error('Error en el pago:', error);
                errorMessage.style.display = 'block';
                btnSubmitPago.disabled = false; // Reactiva el botón
                // Restaura el texto del botón al total original
                const totalText = document.querySelector('.carrito-total span').textContent;
                btnSubmitPago.textContent = `Pagar ${totalText}`;
            });
        });
    });