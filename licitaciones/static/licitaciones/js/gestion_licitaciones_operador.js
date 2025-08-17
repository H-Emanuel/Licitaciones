// FUNCIONALIDAD DE PRUEBA: ACCIONES DINAMICAS
const checkboxes = document.querySelectorAll('tbody input[type="checkbox"][class="licitacion-check"]');
const btnsAction = document.querySelectorAll('.btn-toggle-acciones');
const toggleAcciones = document.querySelector('.toggle-acciones');
const cerrarLicitacion = document.querySelector('.cerrar-licitacion-fila');
function handleSingleSelection(e) {
    if (e.target.checked) {
        checkboxes.forEach(cb => {
            if (cb !== e.target) {
                cb.checked = false;
            }
        });
        toggleAcciones.style.display="flex";
        setTimeout(() => {
            toggleAcciones.style.transform = "translateX(0)";
        }, 1);
        btnsAction.forEach(btnAction => {btnAction.dataset.id=e.target.value;});
        if (e.target.parentNode.parentNode !== null && e.target.parentNode.parentNode.classList.contains("lic-cerrada")){
            cerrarLicitacion.title="Licitación ya cerrada";
            cerrarLicitacion.display="none";
            cerrarLicitacion.disabled=true;
        } else {
            cerrarLicitacion.title="Cerrar licitación";
            cerrarLicitacion.querySelector('.icono-accion').innerHTML="🔒";
            cerrarLicitacion.disabled=false;
        }
    } else {
        toggleAcciones.style.transform = "translateX(115%)";
    }
}

checkboxes.forEach(cb => {
    cb.addEventListener('change', handleSingleSelection);
});





















document.addEventListener('DOMContentLoaded', function() {
    // Buscador - solo si existe (en operador no hay buscador)
    const buscador = document.querySelector('.buscador');
    if (buscador) {
        buscador.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                const q = this.value.trim();
                window.location.href = `?q=${encodeURIComponent(q)}`;
            }
        });
    }

    // Filtrar anuales y fallidas
    const btnFiltrarAnuales = document.getElementById('btnFiltrarAnuales');
    if (btnFiltrarAnuales) {
        btnFiltrarAnuales.addEventListener('click', function() {
            const url = new URL(window.location.href);
            const actual = url.searchParams.get('solo_anuales');
            if (actual === '1') {
                url.searchParams.delete('solo_anuales');
            } else {
                url.searchParams.set('solo_anuales', '1');
                url.searchParams.delete('page');
            }
            window.location.href = url.toString();
        });
    }

    const btnFiltrarFallidas = document.getElementById('btnFiltrarFallidas');
    if (btnFiltrarFallidas) {
        btnFiltrarFallidas.addEventListener('click', function() {
            const url = new URL(window.location.href);
            const actual = url.searchParams.get('solo_fallidas');
            if (actual === '1') {
                url.searchParams.delete('solo_fallidas');
            } else {
                url.searchParams.set('solo_fallidas', '1');
                url.searchParams.delete('page');
            }
            window.location.href = url.toString();
        });
    }
    document.getElementById('btnFiltrarPedido')?.addEventListener('click', function() {
        const numeroPedido = document.getElementById('numeroPedido');
        const url = new URL(window.location.href);
        const actual = url.searchParams.get('q');
        url.searchParams.set('q', numeroPedido.value.trim());
        url.searchParams.delete('page');
        console.log('Filtro aplicado para número de pedido:', numeroPedido.value.trim());
        window.location.href = url.toString();
    });
    // Botón Mostrar Todas - para limpiar filtros
    const btnMostrarTodas = document.getElementById('btnMostrarTodas');
    if (btnMostrarTodas) {
        btnMostrarTodas.addEventListener('click', function() {
            const url = new URL(window.location.href);
            url.searchParams.delete('solo_anuales');
            url.searchParams.delete('solo_fallidas');
            url.searchParams.delete('q');
            url.searchParams.delete('page');
            window.location.href = url.toString();
        });
    }

    // --- MODAL ÚLTIMA OBSERVACIÓN ---
    const modalUltimaObs = document.getElementById('modalUltimaObs');
    const cerrarModalUltimaObs = document.getElementById('cerrarModalUltimaObs');
    
    // Configurar botones de última observación
    document.querySelectorAll('.ultima-obs-fila').forEach(btn => {
        btn.addEventListener('click', async function() {
            const licitacionId = this.getAttribute('data-id');
            
            try {
                const res = await fetch(`/api/licitacion/${licitacionId}/ultima_observacion/`);
                if (res.ok) {
                    const data = await res.json();
                    
                    // Mostrar observación del operador
                    const contenidoOperador = document.getElementById('contenidoUltimaObsOperador');
                    const fechaOperador = document.getElementById('fechaUltimaObsOperador');
                    
                    if (contenidoOperador && data.ok && data.operador) {
                        contenidoOperador.textContent = data.operador.texto || 'No hay observación';
                        fechaOperador.textContent = data.operador.fecha || '';
                    } else if (contenidoOperador) {
                        contenidoOperador.textContent = 'No hay observación del operador';
                        fechaOperador.textContent = '';
                    }
                    
                    // Mostrar observación del administrador
                    const contenidoAdmin = document.getElementById('contenidoUltimaObsAdmin');
                    const fechaAdmin = document.getElementById('fechaUltimaObsAdmin');
                    
                    if (contenidoAdmin && data.ok && data.admin) {
                        contenidoAdmin.textContent = data.admin.texto || 'No hay observación';
                        fechaAdmin.textContent = data.admin.fecha || '';
                    } else if (contenidoAdmin) {
                        contenidoAdmin.textContent = 'No hay observación del administrador';
                        fechaAdmin.textContent = '';
                    }
                    
                    // Mostrar modal
                    if (modalUltimaObs) {
                        modalUltimaObs.style.display = 'flex';
                    }
                } else {
                    alert('Error al cargar la observación');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al cargar la observación');
            }
        });
    });

    // Cerrar modal de última observación
    if (cerrarModalUltimaObs) {
        cerrarModalUltimaObs.addEventListener('click', function() {
            if (modalUltimaObs) {
                modalUltimaObs.style.display = 'none';
            }
        });
    }

    // Cerrar modal al hacer clic fuera
    if (modalUltimaObs) {
        modalUltimaObs.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    }

    // --- MODAL CERRAR LICITACIÓN ---
    const modalCerrarLicitacion = document.getElementById('modalCerrarLicitacion');
    const cerrarModalCerrarLicitacion = document.getElementById('cerrarModalCerrarLicitacion');
    const btnCancelarCerrarLicitacion = document.getElementById('btnCancelarCerrarLicitacion');
    const formCerrarLicitacion = document.getElementById('formCerrarLicitacion');
    const licitacionFallidaCheckbox = document.getElementById('licitacionFallidaCheckbox');
    const tipoFallidaContainer = document.getElementById('tipoFallidaContainer');

    // Configurar botones de cerrar licitación
    document.querySelectorAll('.cerrar-licitacion-fila').forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.disabled) return;
            
            const licitacionId = this.getAttribute('data-id');
            document.getElementById('cerrarLicitacionId').value = licitacionId;
            
            // Resetear formulario
            document.getElementById('cerrarLicitacionTexto').value = '';
            if (licitacionFallidaCheckbox) {
                licitacionFallidaCheckbox.checked = false;
            }
            if (tipoFallidaContainer) {
                tipoFallidaContainer.style.display = 'none';
            }
            
            // Mostrar modal
            if (modalCerrarLicitacion) {
                modalCerrarLicitacion.style.display = 'flex';
            }
        });
    });

    // Toggle tipo de falla
    if (licitacionFallidaCheckbox && tipoFallidaContainer) {
        licitacionFallidaCheckbox.addEventListener('change', function() {
            tipoFallidaContainer.style.display = this.checked ? 'block' : 'none';
        });
    }

    // Cerrar modal de cerrar licitación
    if (cerrarModalCerrarLicitacion) {
        cerrarModalCerrarLicitacion.addEventListener('click', function() {
            if (modalCerrarLicitacion) {
                modalCerrarLicitacion.style.display = 'none';
            }
        });
    }

    if (btnCancelarCerrarLicitacion) {
        btnCancelarCerrarLicitacion.addEventListener('click', function() {
            if (modalCerrarLicitacion) {
                modalCerrarLicitacion.style.display = 'none';
            }
        });
    }

    // Cerrar modal al hacer clic fuera
    if (modalCerrarLicitacion) {
        modalCerrarLicitacion.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    }

    // Enviar formulario de cerrar licitación
    if (formCerrarLicitacion) {
        formCerrarLicitacion.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const licitacionId = document.getElementById('cerrarLicitacionId').value;
            const texto = document.getElementById('cerrarLicitacionTexto').value.trim();
            const licitacionFallida = licitacionFallidaCheckbox ? licitacionFallidaCheckbox.checked : false;
            const tipoFallida = document.getElementById('tipoFallidaSelect').value;
            
            if (!texto) {
                alert('Debe ingresar un motivo para cerrar la licitación');
                return;
            }
            
            if (licitacionFallida && !tipoFallida) {
                alert('Debe seleccionar un tipo de falla');
                return;
            }
            
            try {
                const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
                const res = await fetch('/api/cerrar_licitacion/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        licitacion_id: licitacionId,
                        texto: texto,
                        licitacion_fallida: licitacionFallida,
                        tipo_fallida: tipoFallida
                    })
                });
                
                if (res.ok) {
                    const data = await res.json();
                    if (data.success) {
                        // Actualizar la fila en la tabla
                        const fila = document.querySelector(`button.cerrar-licitacion-fila[data-id='${licitacionId}']`)?.closest('tr');
                        if (fila) {
                            // Actualizar estado en la columna 4 (Status)
                            const estadoCell = fila.querySelector('td:nth-child(4) .estado-badge');
                            if (estadoCell) {
                                estadoCell.textContent = 'CERRADA';
                                estadoCell.className = 'estado-badge estado-cerrada';
                            }
                            
                            // Deshabilitar botón de cerrar
                            const btnCerrarLicitacion = fila.querySelector('button.cerrar-licitacion-fila');
                            if (btnCerrarLicitacion) {
                                btnCerrarLicitacion.disabled = true;
                                btnCerrarLicitacion.title = 'Licitación ya cerrada';
                                btnCerrarLicitacion.style.background = '#6c757d';
                                btnCerrarLicitacion.style.color = '#dee2e6';
                            }
                        }
                        
                        alert('Licitación cerrada exitosamente');
                        modalCerrarLicitacion.style.display = 'none';
                    } else {
                        alert(data.message || 'Error al cerrar la licitación');
                    }
                } else {
                    const data = await res.json();
                    alert(data.message || 'Error al cerrar la licitación');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al cerrar la licitación');
            }
        });
    }
    
    // === SINCRONIZACIÓN DE HOVER ENTRE TABLA Y COLUMNA STICKY ===
    
    // Sincronizar hover entre filas de tabla y filas de acciones
    const tablaFilas = document.querySelectorAll('.tabla-proyectos tbody tr');
    const accionesFilas = document.querySelectorAll('.acciones-row');
    
    // Agregar eventos de hover a las filas de la tabla
    tablaFilas.forEach((fila, index) => {
        fila.addEventListener('mouseenter', function() {
            if (accionesFilas[index]) {
                accionesFilas[index].style.background = '#f8f9fa';
            }
        });
        
        fila.addEventListener('mouseleave', function() {
            if (accionesFilas[index]) {
                accionesFilas[index].style.background = '#fff';
            }
        });
    });
    
    // Agregar eventos de hover a las filas de acciones
    accionesFilas.forEach((fila, index) => {
        fila.addEventListener('mouseenter', function() {
            if (tablaFilas[index]) {
                tablaFilas[index].style.background = '#f8f9fa';
            }
        });
        
        fila.addEventListener('mouseleave', function() {
            if (tablaFilas[index]) {
                tablaFilas[index].style.background = '';
            }
        });
    });
    
    // === FIN SINCRONIZACIÓN HOVER ===
    
    // toggle de acciones
    console.log('DOM cargado - Inicializando toggle de acciones');
    
    const btnToggle = document.getElementById('btnToggleAcciones');
    const accionesSticky = document.getElementById('accionesSticky');
    
    if (!btnToggle || !accionesSticky) {
        console.error('No se encontraron los elementos del toggle');
        return;
    }
    
    console.log('Elementos encontrados - Configurando evento click');
    let isVisible = false;
    let isAnimating = false; // Prevenir clics durante animación
    // Función para toggle
    function toggleAcciones(e) {
        // Prevenir clics múltiples durante animación
        if (isAnimating) {
            console.log('Animación en progreso, ignorando clic');
            return;
        }
        
        console.log('Toggle clicked! Estado actual:', isVisible);
        
        isVisible = !isVisible;
        
        // Obtener la referencia actual del botón después del replaceWith
        const currentBtnToggle = document.getElementById('btnToggleAcciones');
        
        if (isVisible) {
            isAnimating = true;
            console.log('Mostrando columna de acciones...');
            // Mostrar columna de acciones
            accionesSticky.style.display = 'flex';
            setTimeout(() => {
                accionesSticky.classList.add('show');
                accionesSticky.classList.remove('hide');
            }, 10);
            
            currentBtnToggle.classList.add('active');
            currentBtnToggle.title = 'Ocultar Acciones';
            currentBtnToggle.querySelector('.toggle-icon').textContent = '✕';
            
            // Permitir nuevos clics después de la animación
            setTimeout(() => {
                isAnimating = false;
            }, 450);
        } else {
            isAnimating = true;
            console.log('Ocultando columna de acciones...');
            // Ocultar columna de acciones
            accionesSticky.classList.add('hide');
            accionesSticky.classList.remove('show');
            
            setTimeout(() => {
                accionesSticky.style.display = 'none';
                isAnimating = false; // Permitir nuevos clics
            }, 400);
            
            currentBtnToggle.classList.remove('active');
            currentBtnToggle.title = 'Mostrar Acciones';
            currentBtnToggle.querySelector('.toggle-icon').textContent = '⚙️';
        }
    }
        
    // Limpiar eventos anteriores
    btnToggle.replaceWith(btnToggle.cloneNode(true));
    const newBtnToggle = document.getElementById('btnToggleAcciones');
    newBtnToggle.addEventListener('click', toggleAcciones);
    
    console.log('Event listener configurado correctamente');
    // Agregar evento al nuevo botón
    newBtnToggle.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Click en botón toggle detectado');
        toggleAcciones();
    });
    
    console.log('Toggle de acciones inicializado correctamente');
});
window.etapasLicitacion = JSON.parse(document.getElementById('etapas-licitacion-data').textContent);
window.tiposLicitacion = JSON.parse(document.getElementById('tipos-licitacion-data').textContent);
// Relación tipo-etapa (ordenada)
function buildTiposLicitacionEtapaRaw(raw) {
    const out = {};
    raw.forEach(rel => {
        if (!out[rel.tipo_licitacion_id]) out[rel.tipo_licitacion_id] = [];
        out[rel.tipo_licitacion_id].push({id: rel.etapa_id, orden: rel.orden});
    });
    Object.keys(out).forEach(tipoId => {
        out[tipoId] = out[tipoId].sort((a,b) => a.orden-b.orden).map(e => e.id);
    });
    return out;
}
window.tiposLicitacionEtapaRaw = buildTiposLicitacionEtapaRaw(JSON.parse(document.getElementById('tipos-licitacion-etapa-raw-data').textContent));