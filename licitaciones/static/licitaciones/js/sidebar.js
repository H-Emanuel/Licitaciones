/**
 * Módulo para la funcionalidad del sidebar, incluyendo el reloj y las notificaciones
 */

(function() {
    'use strict';

    // Funcionalidad del reloj
    function initializeClock() {
        function updateClock() {
            const now = new Date();
            const timeOptions = { 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit',
                hour12: false 
            };
            const dateOptions = { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            };
            
            const time = now.toLocaleTimeString('es-CL', timeOptions);
            const date = now.toLocaleDateString('es-CL', dateOptions);
            
            const clockTimeElement = document.getElementById('clock-time');
            const clockDateElement = document.getElementById('clock-date');
            
            if (clockTimeElement) clockTimeElement.textContent = time;
            if (clockDateElement) clockDateElement.textContent = date.charAt(0).toUpperCase() + date.slice(1);
        }
        
        setInterval(updateClock, 1000);
        updateClock();
    }

    // Variables del sistema de notificaciones
    let notificacionesToggle, modalNotificaciones, notificacionesBadge;
    let notificacionesLista, notificacionesVacia, notificacionesAcciones;
    let btnMarcarTodasLeidas, cerrarModalNotificaciones;
    let notificacionesIntervalId;

    // Mostrar estado cuando no hay notificaciones o hay error
    function mostrarEstadoSinNotificaciones() {
        if (notificacionesBadge) notificacionesBadge.style.display = 'none';
        if (notificacionesLista) notificacionesLista.innerHTML = '';
        if (notificacionesVacia) notificacionesVacia.style.display = 'block';
        if (notificacionesAcciones) notificacionesAcciones.style.display = 'none';
    }

    // Cargar notificaciones del servidor
    function cargarNotificaciones() {
        if (!notificacionesBadge || !notificacionesLista || !notificacionesVacia || !notificacionesAcciones) {
            console.warn('Elementos de notificaciones no encontrados');
            return;
        }
        
        fetch('/api/notificaciones/')
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                }
                return response.json();
            })
            .then(function(data) {
                if (data && data.ok) {
                    actualizarNotificaciones(data.notificaciones || [], data.total_no_leidas || 0);
                } else {
                    console.warn('Respuesta de notificaciones inválida:', data);
                    mostrarEstadoSinNotificaciones();
                }
            })
            .catch(function(error) {
                console.warn('Error al cargar notificaciones (probablemente la API no está implementada):', error.message);
                mostrarEstadoSinNotificaciones();
            });
    }

    // Actualizar interfaz de notificaciones
    function actualizarNotificaciones(notificaciones, totalNoLeidas) {
        try {
            // Verificar que los elementos existan
            if (!notificacionesBadge || !notificacionesLista || !notificacionesVacia || !notificacionesAcciones) {
                console.warn('Elementos de notificaciones no disponibles');
                return;
            }
            
            if (totalNoLeidas > 0) {
                notificacionesBadge.textContent = totalNoLeidas > 99 ? '99+' : totalNoLeidas;
                notificacionesBadge.style.display = 'block';
            } else {
                notificacionesBadge.style.display = 'none';
            }

            notificacionesLista.innerHTML = '';
            
            if (!notificaciones || notificaciones.length === 0) {
                notificacionesVacia.style.display = 'block';
                notificacionesAcciones.style.display = 'none';
            } else {
                notificacionesVacia.style.display = 'none';
                notificacionesAcciones.style.display = 'flex';
                
                notificaciones.forEach(function(notif) {
                    const item = document.createElement('div');
                    item.className = 'notificacion-item';
                    

                    const titulo = (notif.titulo || 'Sin título').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                    const mensaje = (notif.mensaje || 'Sin mensaje').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                    const fechaRelativa = (notif.fecha_relativa || 'Fecha desconocida').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                    const tipo = (notif.tipo || 'info').replace(/[^a-zA-Z]/g, '');
                    
                    item.innerHTML = 
                        '<div class="notificacion-header">' +
                            '<div class="notificacion-tipo ' + tipo + '"></div>' +
                            '<div class="notificacion-content">' +
                                '<div class="notificacion-titulo">' + titulo + '</div>' +
                                '<div class="notificacion-mensaje">' + mensaje + '</div>' +
                                '<div class="notificacion-tiempo">' + fechaRelativa + '</div>' +
                            '</div>' +
                        '</div>';
                    

                    item.addEventListener('click', function() {
                        if (notif.id) {
                            marcarNotificacionLeida(notif.id);
                        }
                        if (notif.licitacion_id) {
                            window.location.href = '/bitacora/' + notif.licitacion_id + '/';
                        }
                    });
                    
                    notificacionesLista.appendChild(item);
                });
            }
        } catch (error) {
            console.error('Error al actualizar notificaciones:', error);
            mostrarEstadoSinNotificaciones();
        }
    }

    // Marcar notificación como leída
    function marcarNotificacionLeida(notificacionId) {
        if (!notificacionId) return;
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!csrfToken) {
            console.warn('Token CSRF no encontrado');
            return;
        }
        
        fetch('/api/notificaciones/' + notificacionId + '/marcar_leida/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken.value,
                'Content-Type': 'application/json'
            }
        })
        .then(function(response) {
            if (!response.ok) {
                throw new Error('HTTP ' + response.status + ': ' + response.statusText);
            }
            return response.json();
        })
        .then(function(data) {
            if (data && data.ok) {
                cargarNotificaciones(); 
            } else {
                console.warn('Error al marcar notificación como leída:', data);
            }
        })
        .catch(function(error) {
            console.warn('Error al marcar notificación como leída:', error.message);
        });
    }

    // Marcar todas las notificaciones como leídas
    function marcarTodasLeidas() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!csrfToken) {
            console.warn('Token CSRF no encontrado');
            return;
        }
        
        fetch('/api/notificaciones/marcar_todas_leidas/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken.value,
                'Content-Type': 'application/json'
            }
        })
        .then(function(response) {
            if (!response.ok) {
                throw new Error('HTTP ' + response.status + ': ' + response.statusText);
            }
            return response.json();
        })
        .then(function(data) {
            if (data && data.ok) {
                cargarNotificaciones();
            } else {
                console.warn('Error al marcar todas las notificaciones como leídas:', data);
            }
        })
        .catch(function(error) {
            console.warn('Error al marcar todas las notificaciones como leídas:', error.message);
        });
    }

    // Inicializar sistema de notificaciones
    function initializeNotifications(esAdmin) {
        if (!esAdmin) return;

        // Obtener elementos del DOM
        notificacionesToggle = document.getElementById('notificacionesToggle');
        modalNotificaciones = document.getElementById('modalNotificaciones');
        notificacionesBadge = document.getElementById('notificacionesBadge');
        notificacionesLista = document.getElementById('notificacionesLista');
        notificacionesVacia = document.getElementById('notificacionesVacia');
        notificacionesAcciones = document.getElementById('notificacionesAcciones');
        btnMarcarTodasLeidas = document.getElementById('btnMarcarTodasLeidas');
        cerrarModalNotificaciones = document.getElementById('cerrarModalNotificaciones');

        // Verificar que todos los elementos estén disponibles
        if (!notificacionesToggle || !modalNotificaciones || !notificacionesBadge || 
            !notificacionesLista || !notificacionesVacia || !notificacionesAcciones) {
            console.warn('Sistema de notificaciones no inicializado: elementos faltantes');
            return;
        }

        // Toggle del modal
        notificacionesToggle.addEventListener('click', function() {
            modalNotificaciones.classList.add('show');
            modalNotificaciones.style.display = 'flex';
            
            // Cargar notificaciones cuando se abre el modal
            cargarNotificaciones();
        });

        // Cerrar modal
        if (cerrarModalNotificaciones) {
            cerrarModalNotificaciones.addEventListener('click', function() {
                modalNotificaciones.classList.remove('show');
                modalNotificaciones.style.display = 'none';
            });
        }

        // Cerrar modal al hacer clic fuera del contenido
        modalNotificaciones.addEventListener('click', function(e) {
            if (e.target === modalNotificaciones) {
                modalNotificaciones.classList.remove('show');
                modalNotificaciones.style.display = 'none';
            }
        });

        // Event listener para marcar todas como leídas
        if (btnMarcarTodasLeidas) {
            btnMarcarTodasLeidas.addEventListener('click', marcarTodasLeidas);
        }

        // Cargar notificaciones iniciales (solo para el badge)
        cargarNotificaciones();
        
        // Actualizar cada 30 segundos, pero solo si la página está visible
        notificacionesIntervalId = setInterval(function() {
            if (!document.hidden) {
                cargarNotificaciones();
            }
        }, 30000);
        
        // Pausar actualizaciones cuando la página no está visible y reanudar cuando esté visible
        document.addEventListener('visibilitychange', function() {
            if (!document.hidden) {
                cargarNotificaciones();
            }
        });
        
        // Limpiar intervalo cuando se cierra la página
        window.addEventListener('beforeunload', function() {
            if (notificacionesIntervalId) {
                clearInterval(notificacionesIntervalId);
            }
        });
    }

    // Inicialización cuando el DOM esté listo
    function initializeSidebar() {
        // Inicializar reloj
        initializeClock();

        if (typeof window.esAdmin !== 'undefined') {
            initializeNotifications(window.esAdmin);
        }
    }

    // Esperar a que el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeSidebar);
    } else {
        initializeSidebar();
    }

})();

function initToggleSidebar() {
    const btnToggle = document.getElementById('btnToggleSidebar');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (btnToggle && sidebar && mainContent) {
        console.log('Inicializando toggle de sidebar...');
        console.log('btnToggle:', btnToggle);
        console.log('sidebar:', sidebar);
        let isVisible = true;
        let isAnimating = false; // Prevenir clics durante animación
        
        function toggleSidebar(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Prevenir clics múltiples durante animación
            if (isAnimating) {
                console.log('Animación en progreso, ignorando clic');
                return;
            }
            
            console.log('Toggle clicked! Estado actual:', isVisible);
            
            isVisible = !isVisible;
            const currentBtnToggle = document.getElementById('btnToggleSidebar');

            if (isVisible) {
                isAnimating = true;
                setTimeout(() => {
                    sidebar.classList.add('show');
                    sidebar.classList.remove('hide');
                }, 10);
                
                currentBtnToggle.classList.add('active');
                
                currentBtnToggle.title = 'Ocultar sidebar';
                currentBtnToggle.querySelector('.toggle-sidebar-icon').textContent = '✕';
                mainContent.classList.add('m-sidebar'); // Ajustar margen del contenido principal
                // Permitir nuevos clics después de la animación
                setTimeout(() => {
                    isAnimating = false;
                }, 450);
            } else {
                isAnimating = true;
                // Ocultar sidebar
                sidebar.classList.add('hide');
                sidebar.classList.remove('show');
                mainContent.classList.remove('m-sidebar');
                setTimeout(() => {
                    isAnimating = false; // Permitir nuevos clics
                }, 400);
                
                currentBtnToggle.classList.remove('active');
                currentBtnToggle.title = 'Mostrar sidebar';
                currentBtnToggle.querySelector('.toggle-sidebar-icon').textContent = '☰';
            }
        }
        
        // Limpiar eventos anteriores
        btnToggle.replaceWith(btnToggle.cloneNode(true));
        const newBtnToggle = document.getElementById('btnToggleSidebar');
        newBtnToggle.addEventListener('click', toggleSidebar);
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, inicializando toggle...');
    setTimeout(() => {
        initToggleSidebar();
    }, 100);
});

// También inicializar cuando la página esté completamente cargada
window.addEventListener('load', function() {
    console.log('Window loaded, re-inicializando toggle...');
    setTimeout(() => {
        initToggleSidebar();
    }, 200);
});

// Animaciones para las notificaciones
const notificationStyles = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;

// Agregar estilos de animación al head
if (!document.getElementById('notification-styles')) {
    const styleElement = document.createElement('style');
    styleElement.id = 'notification-styles';
    styleElement.textContent = notificationStyles;
    document.head.appendChild(styleElement);
}
