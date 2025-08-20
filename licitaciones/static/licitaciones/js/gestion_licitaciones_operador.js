// FUNCIONALIDAD DE PRUEBA: ACCIONES DINAMICAS
function initToggleAccionesDinamicas() {
    const checkboxes = document.querySelectorAll('tbody input[type="checkbox"][class="licitacion-check"]');
    const btnsAction = document.querySelectorAll('.btn-toggle-acciones');
    const toggleAcciones = document.querySelector('.toggle-acciones');
    const cerrarLicitacion = document.querySelector('.cerrar-licitacion-fila');
    const modalCerrarLicitacion = document.getElementById('modalCerrarLicitacion');

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
                // Mostrar modal
                if (modalCerrarLicitacion) {
                    cerrarLicitacion.addEventListener('click', () => {modalCerrarLicitacion.style.display = 'flex'});
                }
            }
        } else {
            toggleAcciones.style.transform = "translateX(115%)";
        }
    }

    checkboxes.forEach(cb => {
        cb.addEventListener('change', handleSingleSelection);
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, inicializando toggle...');
    setTimeout(() => {
        initToggleAccionesDinamicas();
    }, 100);
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

    

    // Enviar cierre de licitación vía AJAX
    if (formCerrarLicitacion) {
        formCerrarLicitacion.onsubmit = async function(e) {
            e.preventDefault();
            
            const licitacionId = document.getElementById('cerrarLicitacionId').value;
            const texto = document.getElementById('cerrarLicitacionTexto').value;
            const licitacionFallida = document.getElementById('licitacionFallidaCheckbox')?.checked;
            const tipoFallida = tipoFallidaSelect ? tipoFallidaSelect.value : false;
            
            if (!texto.trim()) {
                alert('Debe especificar el motivo del cierre de la licitación.');
                return;
            }

            // Validar que si está marcada como fallida, se haya seleccionado un tipo
            if (licitacionFallida && !tipoFallida) {
                alert('Debe seleccionar el tipo de falla para una licitación fallida.');
                return;
            }
            
            // Confirmación antes de cerrar
            const confirmMessage = `¿Está seguro que desea cerrar esta licitación?\n\nEsta acción cambiará el estado a "${licitacionFallida ? tipoFallida ? tipoFallida.toUpperCase() : 'FALLIDA' : 'CERRADA'}" y se registrará en la bitácora.`;
            if (!confirm(confirmMessage)) {
                return;
            }
            
            const formData = new FormData();
            formData.append('texto', texto);
            
            if (licitacionFallida) {
                formData.append('licitacion_fallida', 'on');
                if (tipoFallida) {
                    formData.append('tipo_fallida', tipoFallida);
                }
            }
            
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            
            try {
                const res = await fetch(`/api/licitacion/${licitacionId}/cerrar/`, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrftoken },
                    body: formData
                });
                  
                if (res.ok) {
                    alert('Licitación cerrada correctamente.');
                    modalCerrarLicitacion.style.display = 'none';
                    gestionarOverflowBody();
                    
                    // Actualizar el estado en la tabla
                    const fila = document.querySelector(`button.cerrar-licitacion-fila[data-id='${licitacionId}']`)?.closest('tr');
                    if (fila) {
                        const estadoCell = fila.querySelector('td .estado-badge');
                        if (estadoCell) {
                            estadoCell.textContent = 'CERRADA';
                            estadoCell.className = 'estado-badge estado-cerrada';
                        }
                    }
                    location.reload();
                } else {
                    const errorData = await res.json().catch(() => ({}));
                    const errorMessage = errorData.error || 'Error al cerrar la licitación.';
                    alert(errorMessage);
                }
            } catch (err) {
                console.error('Error al cerrar la licitación:', err);
                alert('Error de red al cerrar la licitación.');
            }
        };
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