window.addEventListener('DOMContentLoaded', function() {
    // Detectar si venimos del historial de licitaciones fallidas o del modal de documentos
    const urlParams = new URLSearchParams(window.location.search);
    const fromHistorial = urlParams.get('from_historial');
    const fromDocuments = urlParams.get('from_documents');
    const licitacionId = urlParams.get('licitacion_id');
    
    // Configurar los botones de volver según de dónde vengamos
    if (fromHistorial === '1') {
        // Guardar esta información en sessionStorage
        sessionStorage.setItem('from_historial', '1');
        
        // Modificar todos los botones de "Volver" para que regresen a la página con los modales abiertos
        document.querySelectorAll('.volver-btn').forEach(btn => {
            // Preservar la URL base según el tipo de usuario
            let originalUrl = btn.getAttribute('href');
            
            // Solo añadir el parámetro si es una URL interna
            if (originalUrl && (originalUrl.startsWith('/') || originalUrl.indexOf('://') === -1)) {
                // Verificar si ya tiene parámetros
                if (originalUrl.indexOf('?') !== -1) {
                    btn.setAttribute('href', originalUrl + '&open_modals=1');
                } else {
                    btn.setAttribute('href', originalUrl + '?open_modals=1');
                }            }
        });
    } else if (fromDocuments === '1' && licitacionId) {
        // Cuando venimos del modal de documentos, necesitamos volver a él
        document.querySelectorAll('.volver-btn').forEach(btn => {
            // Modificar el comportamiento del botón volver para abrir el modal de documentos
            btn.setAttribute('href', '/');
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Guardar en sessionStorage que venimos del modal de documentos y qué licitación debemos abrir
                sessionStorage.setItem('from_documents', '1');
                sessionStorage.setItem('open_documents_for_licitacion', licitacionId);
                
                // Redirigir a la página principal
                window.location.href = '/';
            });
        });
    }
    
    var textarea = document.querySelector('textarea[name="texto"]');
    if (textarea) textarea.focus();

    // Botón para subir archivo
    const btnSubirArchivo = document.getElementById('btnSubirArchivo');
    const inputArchivo = document.getElementById('inputArchivo');
    const archivoNombre = document.getElementById('archivoNombre');
    if (btnSubirArchivo && inputArchivo) {
        btnSubirArchivo.addEventListener('click', function() {
            inputArchivo.click();
        });
        inputArchivo.addEventListener('change', function() {
            archivoNombre.textContent = inputArchivo.files.length ? inputArchivo.files[0].name : '';
        });
    }

    // flechas de navegación
    const etapas = window.etapasLicitacion || [];
    const inputEtapa = document.getElementById('inputEtapa');
    const etapaActual = document.getElementById('etapaActual');
    const btnAvanzar = document.getElementById('avanzarEtapa');
    const btnRetroceder = document.getElementById('retrocederEtapa');
    if (inputEtapa && etapaActual && etapas.length) {
        btnAvanzar.addEventListener('click', function() {
            let idx = etapas.findIndex(e => Number(e.id) === Number(inputEtapa.value));
            if (idx < etapas.length - 1) {
                inputEtapa.value = etapas[idx + 1].id;
                etapaActual.textContent = etapas[idx + 1].nombre;
            }
        });
        btnRetroceder.addEventListener('click', function() {
            let idx = etapas.findIndex(e => Number(e.id) === Number(inputEtapa.value));
            if (idx > 0) {
                inputEtapa.value = etapas[idx - 1].id;
                etapaActual.textContent = etapas[idx - 1].nombre;
            }
        });

        etapaActual.onmouseenter = null;
        etapaActual.onmouseleave = null;
        etapaActual.removeAttribute('title');
        const oldTooltip = etapaActual.querySelector('.etapa-tooltip');
        if (oldTooltip) oldTooltip.remove();
    }

    // --- Observaciones Bitácora ---
    function showModalObservacion(bitacoraId, texto) {
        const modalContainer = document.querySelector('.modal-container');
        modalContainer.classList.add('active');
        document.getElementById('observacionBitacoraId').value = bitacoraId;
        document.getElementById('modalObservacionTexto').value = texto || '';
    }
    function closeModalObservacion() {
        const modalContainer = document.querySelector('.modal-container');
        modalContainer.style.display = 'none';
       
        modalContainer.classList.remove('active');
        
        // Limpiar archivos del modal
        modalSelectedFiles = [];
        if (modalArchivos) modalArchivos.value = '';
        if (modalPreviewArchivos) modalPreviewArchivos.innerHTML = '';
        
        // Limpiar texto del modal
        const modalTexto = document.getElementById('modalObservacionTexto');
        if (modalTexto) modalTexto.value = '';
    }    // Delegación de eventos para botones de observación (por si la tabla se recarga dinámicamente)
    document.body.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-agregar-observacion-bitacora')) {
            showModalObservacion(e.target.dataset.id, '');
        } else if (e.target.classList.contains('editar-observacion-mini')) {
            const bitacoraId = e.target.dataset.id;
            fetch(`/api/bitacora/${bitacoraId}/observacion/`)
                .then(res => res.json())
                .then(data => {
                    if (data.ok) {
                        showModalObservacion(bitacoraId, data.texto);
                    } else {
                        alert('No se pudo cargar la observación');
                    }
                });
        } else if (e.target.classList.contains('eliminar-observacion-mini')) {
            if (confirm('¿Eliminar esta observación?')) {
                fetch(`/api/bitacora/${e.target.dataset.id}/observacion/`, { 
                    method: 'DELETE', 
                    headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value } 
                })
                .then(res => res.json())
                .then(data => { 
                    if (data.ok) location.reload(); 
                    else alert('Error al eliminar'); 
                });
            }
        } else if (e.target.classList.contains('btn-eliminar-entrada')) {
            if (confirm('¿Seguro que deseas eliminar esta entrada de bitácora?')) {
                fetch(`/bitacora/eliminar/${e.target.dataset.id}/`, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.ok) location.reload();
                    else alert('Error al eliminar entrada');
                });
            }
        }
    });
    document.getElementById('cerrarModalObservacion').onclick = closeModalObservacion;
    document.getElementById('btnCancelarObservacion').onclick = closeModalObservacion;
    const formObservacionBitacora = document.getElementById('formObservacionBitacora');
    if (formObservacionBitacora){
        formObservacionBitacora.onsubmit = function(e) {
            e.preventDefault();
            const bitacoraId = document.getElementById('observacionBitacoraId').value;
            const texto = document.getElementById('observacionTexto').value;
            fetch(`/api/bitacora/${bitacoraId}/observacion/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value },
                body: JSON.stringify({ texto })
            })
            .then(res => res.json())
            .then(data => {
                if (data.ok) { closeModalObservacion(); location.reload(); }
                else alert('Error al guardar observación');
            });
        };
    }

    // Manejo del formulario del modal (separado)
    const formModalObservacion = document.getElementById('formModalObservacion');
    if (formModalObservacion) {
        formModalObservacion.onsubmit = function(e) {
            e.preventDefault();
            const bitacoraId = document.getElementById('observacionBitacoraId').value;
            const texto = document.getElementById('modalObservacionTexto').value;
            
            // Crear FormData para enviar archivos también
            const formData = new FormData();
            formData.append('texto', texto);
            
            // Agregar archivos del modal si los hay
            if (modalSelectedFiles && modalSelectedFiles.length > 0) {
                modalSelectedFiles.forEach(file => {
                    formData.append('archivos', file);
                });
            }
            fetch(`/api/bitacora/${bitacoraId}/observacion/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.ok) { 
                    closeModalObservacion(); 
                    location.reload(); 
                } else {
                    alert('Error: ' + (data.error || 'No se pudo guardar la observación'));
                }
            });
        };
    }

    // --- Mini modal de opciones para observación (admin) ---
    document.body.addEventListener('click', function(e) {
        // Mostrar mini modal al hacer click en la tuerca
        if (e.target.classList.contains('btn-tuerca-observacion')) {
            e.preventDefault();
            e.stopPropagation();
            // Cerrar otros mini modales abiertos
            document.querySelectorAll('.mini-modal-opciones').forEach(m => m.style.display = 'none');
            // Mostrar el mini modal de esta fila
            const bitacoraId = e.target.dataset.id;
            const miniModal = document.getElementById('miniModalObs' + bitacoraId);
            if (miniModal) {
                // Posicionar el mini modal cerca del botón, considerando el scroll
                const rect = e.target.getBoundingClientRect();
                miniModal.style.display = 'block';
                miniModal.style.position = 'fixed';
                miniModal.style.top = (rect.bottom + 6) + 'px';
                miniModal.style.left = (rect.left) + 'px';
                miniModal.style.zIndex = 4000;
            }
        }
        // Opción editar
        if (e.target.classList.contains('editar-observacion-mini')) {
            e.preventDefault();
            e.stopPropagation();
            const bitacoraId = e.target.dataset.id;
            fetch(`/api/bitacora/${bitacoraId}/observacion/`)
                .then(res => res.json())
                .then(data => {
                    if (data.ok) {
                        document.querySelectorAll('.mini-modal-opciones').forEach(m => m.style.display = 'none');
                        showModalObservacion(bitacoraId, data.texto);
                    } else {
                        alert('No se pudo cargar la observación');
                    }
                });
        }
        // Opción eliminar
        if (e.target.classList.contains('eliminar-observacion-mini')) {
            e.preventDefault();
            e.stopPropagation();
            if (confirm('¿Eliminar esta observación?')) {
                fetch(`/api/bitacora/${e.target.dataset.id}/observacion/`, { method: 'DELETE', headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value } })
                    .then(res => res.json())
                    .then(data => { if (data.ok) location.reload(); else alert('Error al eliminar'); });
            }
            document.querySelectorAll('.mini-modal-opciones').forEach(m => m.style.display = 'none');
        }
    });
    // Cerrar mini modal al hacer click fuera
    document.addEventListener('click', function(e) {
        if (!e.target.classList.contains('btn-tuerca-observacion') && !e.target.classList.contains('mini-modal-opciones') && !e.target.classList.contains('btn-opcion-mini') && !e.target.closest('.mini-modal-opciones')) {
            document.querySelectorAll('.mini-modal-opciones').forEach(m => m.style.display = 'none');
        }
    });
    
    // --- PANEL INTEGRADO OBSERVACIÓN OPERADOR ---
    const panelObservacion = document.getElementById('panelObservacionOperador');
    const togglePanelBtn = document.getElementById('togglePanelObservacion');
    const contenidoPanel = document.getElementById('contenidoPanelObservacion');
    
    // Toggle del panel - Inicialmente cerrado
    if (togglePanelBtn && contenidoPanel) {
        // Asegurar que inicia cerrado
        contenidoPanel.classList.remove('expanded');
        togglePanelBtn.classList.remove('expanded');
        
        togglePanelBtn.addEventListener('click', function() {
            const isExpanded = contenidoPanel.classList.contains('expanded');
            
            if (isExpanded) {
                // Cerrar panel
                contenidoPanel.classList.remove('expanded');
                togglePanelBtn.classList.remove('expanded');
            } else {
                // Abrir panel
                contenidoPanel.classList.add('expanded');
                togglePanelBtn.classList.add('expanded');
            }
        });
        
        // También permitir toggle haciendo clic en el header
        const panelHeader = document.querySelector('.panel-header');
        if (panelHeader) {
            panelHeader.addEventListener('click', function(e) {
                if (e.target !== togglePanelBtn && !e.target.classList.contains('toggle-icono')) {
                    togglePanelBtn.click();
                }
            });
        }
    }
    
    // --- CHECKBOX MARCAR FALLIDA Y TIPO DE FALLA ---
    const marcarFallidaCheckbox = document.getElementById('marcarFallidaCheckbox');
    const tipoFallidaContainer = document.getElementById('tipoFallidaContainer');
    const tipoFallidaSelect = document.getElementById('tipoFallidaSelect');
    
    if (marcarFallidaCheckbox && tipoFallidaContainer) {
        marcarFallidaCheckbox.addEventListener('change', function() {
            if (this.checked) {
                tipoFallidaContainer.classList.remove('hidden');
            } else {
                tipoFallidaContainer.classList.add('hidden');
                if (tipoFallidaSelect) {
                    tipoFallidaSelect.value = '';
                }
            }
        });
    }
    
    // Funcionalidad de avanzar etapa
    const btnAvanzarEtapa = document.getElementById('btnAvanzarEtapa');
    const nombreEtapaActual = document.getElementById('nombreEtapaActual');
    const accionEtapa = document.getElementById('accionEtapa');
    const btnRetrocederEtapa = document.getElementById('btnRetrocederEtapa');
    
    // Variable para guardar la etapa original (antes de hacer cambios)
    let etapaOriginal = null;
    
    // Guardar la etapa original al cargar la página
    if (nombreEtapaActual) {
        etapaOriginal = {
            id: nombreEtapaActual.dataset.etapaId,
            nombre: nombreEtapaActual.textContent.trim()
        };
    }
    
    function toggleFechasImportantes() {
        const fechasImportantes = document.getElementById('fechasImportantesContainer');
        const idMercadoPublicoInput = document.getElementById('fechasImportantes');
        
        if (!fechasImportantes || !nombreEtapaActual) return;
        
        const etapaActualTexto = nombreEtapaActual.textContent.trim().toLowerCase();
        
        // Mostrar campo si la etapa es "Publicacion en portal"
        if (etapaActualTexto === 'publicacion en portal' || etapaActualTexto === 'publicación en portal') {
            fechasImportantes.classList.remove('hidden');
        } else {
            fechasImportantes.classList.add('hidden');
        }
    }

    // Función para mostrar/ocultar campo ID Mercado Público
    function toggleIdMercadoPublico() {
        const idMercadoPublicoContainer = document.getElementById('idMercadoPublicoContainer');
        const idMercadoPublicoInput = document.getElementById('idMercadoPublicoInput');
        
        if (!idMercadoPublicoContainer || !nombreEtapaActual) return;
        
        const etapaActualTexto = nombreEtapaActual.textContent.trim().toLowerCase();
        
        // Mostrar campo si la etapa es "Publicacion en portal"
        if (etapaActualTexto === 'publicacion en portal' || etapaActualTexto === 'publicación en portal') {
            idMercadoPublicoContainer.classList.remove('hidden');
            if (idMercadoPublicoInput) {
                idMercadoPublicoInput.focus();
            }
        } else {
            idMercadoPublicoContainer.classList.add('hidden');
        }
    }
    
    // Función para mostrar/ocultar campos de Recepción de Ofertas
    function toggleRecepcionOfertas() {
        const recepcionOfertasContainer = document.getElementById('recepcionOfertasContainer');
        const numeroOfertasInput = document.getElementById('numeroOfertasInput');
        
        if (!recepcionOfertasContainer || !nombreEtapaActual) return;
        
        const etapaActualTexto = nombreEtapaActual.textContent.trim().toLowerCase();
        
        // Mostrar campos si la etapa es "Recepción de Ofertas"
        if (etapaActualTexto === 'recepcion de ofertas' || 
            etapaActualTexto === 'recepción de ofertas' ||
            etapaActualTexto === 'recepcion ofertas' ||
            etapaActualTexto === 'recepción ofertas') {
            recepcionOfertasContainer.classList.remove('hidden');
            if (numeroOfertasInput) {
                numeroOfertasInput.focus();
            }
        } else {
            recepcionOfertasContainer.classList.add('hidden');
        }
    }

    function toggleEtapaButton() {
        const etapaActualId = parseInt(nombreEtapaActual.dataset.etapaId);
        const currentIndex = etapas.findIndex(e => parseInt(e.id) === etapaActualId);
        console.log(etapaActualId, etapaOriginal.id);
        if (currentIndex == etapas.length - 1) {
            btnAvanzarEtapa.classList.add('hidden');
        }
        else if (etapaActualId == parseInt(etapaOriginal.id)) {
            btnRetrocederEtapa.classList.add('hidden');
        }
        else {
            btnRetrocederEtapa.classList.remove('hidden');
            btnAvanzarEtapa.classList.remove('hidden');
        }
    }
    
    // Verificar al cargar la página
    toggleFechasImportantes();
    toggleIdMercadoPublico();
    toggleRecepcionOfertas();
    toggleEtapaButton();

    if (btnAvanzarEtapa && nombreEtapaActual && etapas.length) {
        btnAvanzarEtapa.addEventListener('click', function() {
            const etapaActualId = parseInt(nombreEtapaActual.dataset.etapaId);
            const currentIndex = etapas.findIndex(e => parseInt(e.id) === etapaActualId);
            if (currentIndex < 0) {
                alert('No se encontró la etapa actual en el catálogo.');
                return;
            }

            if (currentIndex >= etapas.length - 1) {
                alert('Ya se encuentra en la última etapa.');
                return;
            }
            
            // Avanzar a la siguiente etapa
            const nextEtapa = etapas[currentIndex + 1];
            nombreEtapaActual.textContent = nextEtapa.nombre;
            nombreEtapaActual.dataset.etapaId = nextEtapa.id;
            
            // Dar feedback visual
            nombreEtapaActual.style.transition = 'all 0.3s';
            nombreEtapaActual.style.background = '#dcfce7';
            nombreEtapaActual.style.borderColor = '#22c55e';
            nombreEtapaActual.style.color = '#16a34a';
            
            btnAvanzarEtapa.style.transform = 'scale(1.05)';
            setTimeout(() => {
                btnAvanzarEtapa.style.transform = '';
                nombreEtapaActual.style.background = '#f0f9ff';
                nombreEtapaActual.style.borderColor = '#bae6fd';
                nombreEtapaActual.style.color = '#0275d8';
            }, 1000);
            
            // Establecer la acción para el envío del formulario
            if (accionEtapa) {
                accionEtapa.value = 'advance';
            }
            
            // Llamar a las funciones para mostrar/ocultar campos específicos por etapa
            toggleFechasImportantes();
            toggleIdMercadoPublico();
            toggleRecepcionOfertas();
            toggleEtapaButton();
        });
    }
    
    // Función para verificar si puede retroceder
    async function verificarPuedeRetroceder(licitacionId) {
        try {
            const response = await fetch(`/api/licitacion/${licitacionId}/puede_retroceder/`);
            if (response.ok) {
                const data = await response.json();
                return data.puede_retroceder;
            }
            return false;
        } catch (error) {
            console.error('Error al verificar si puede retroceder:', error);
            return false;
        }
    }
    
    // Mostrar/ocultar botón de retroceder según si puede retroceder
    async function actualizarVisibilidadRetroceder() {
        if (!btnRetrocederEtapa) return;
        
        const licitacionId = window.location.pathname.match(/\/bitacora\/(\d+)\//)?.[1];
        if (!licitacionId) return;
        // IMPLEMENTACION DESCONTINUADA
        //const puedeRetroceder = await verificarPuedeRetroceder(licitacionId);
        const puedeRetroceder = false;
        if (puedeRetroceder) {
            btnRetrocederEtapa.classList.remove('hidden');
            btnRetrocederEtapa.style.display = 'inline-flex';
        } else {
            btnRetrocederEtapa.classList.add('hidden');
        }
    }
    
    // Configurar el botón de retroceder etapa
    if (btnRetrocederEtapa && nombreEtapaActual && etapas.length) {
        btnRetrocederEtapa.addEventListener('click', function() {
            const etapaActualId = parseInt(nombreEtapaActual.dataset.etapaId);
            const currentIndex = etapas.findIndex(e => parseInt(e.id) === etapaActualId);
            if (currentIndex < 0) {
                alert('No se encontró la etapa actual en el catálogo.');
                return;
            }
            
            // Retroceder a la etapa anterior
            const prevEtapa = etapas[currentIndex - 1];
            nombreEtapaActual.textContent = prevEtapa.nombre;
            nombreEtapaActual.dataset.etapaId = prevEtapa.id;
            
            // Dar feedback visual (color rojo/naranja para retroceso)
            nombreEtapaActual.style.transition = 'all 0.3s';
            nombreEtapaActual.style.background = '#fef3c7';
            nombreEtapaActual.style.borderColor = '#f59e0b';
            nombreEtapaActual.style.color = '#d97706';
            
            btnRetrocederEtapa.style.transform = 'scale(1.05)';
            setTimeout(() => {
                btnRetrocederEtapa.style.transform = '';
                nombreEtapaActual.style.background = '#f0f9ff';
                nombreEtapaActual.style.borderColor = '#bae6fd';
                nombreEtapaActual.style.color = '#0275d8';
            }, 1000);
            
            // Establecer la acción para el envío del formulario
            if (accionEtapa) {
                accionEtapa.value = 'retreat';
            }
            
            // Llamar a las funciones para mostrar/ocultar campos específicos por etapa
            toggleFechasImportantes();
            toggleIdMercadoPublico();
            toggleRecepcionOfertas();
            toggleEtapaButton();
        });
    }
    
    // Verificar al cargar la página si puede retroceder
    actualizarVisibilidadRetroceder();

    // Manejo mejorado de archivos en el dropzone de bitácora
    const dropzoneBitacora = document.getElementById('dropzoneBitacora');
    const inputArchivos = document.getElementById('observacionArchivos');
    const previewContainer = document.getElementById('previewArchivosBitacora');
    let selectedFiles = [];

    // Variables para el modal
    const modalDropzone = document.getElementById('modalDropzone');
    const modalArchivos = document.getElementById('modalArchivos');
    const modalPreviewArchivos = document.getElementById('modalPreviewArchivos');
    let modalSelectedFiles = [];

    // Función para actualizar el input con los archivos seleccionados
    function updateFileInputBitacora() {
        if (!inputArchivos) return;
        const dt = new DataTransfer();
        selectedFiles.forEach(file => dt.items.add(file));
        inputArchivos.files = dt.files;
    }

    // Función para mostrar la preview de archivos mejorada
    function showFilePreviewBitacora() {
        if (!previewContainer) return;
        
        previewContainer.innerHTML = '';
        
        if (selectedFiles.length === 0) {
            return;
        }

        selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'archivo-preview-item';
            fileItem.innerHTML = `
                <div class="archivo-preview-content">
                    <span class="archivo-preview-icon">📄</span>
                    <span class="archivo-preview-name">${file.name}</span>
                    <span class="archivo-preview-size">(${(file.size / 1024).toFixed(1)} KB)</span>
                    <button type="button" class="archivo-preview-remove" data-index="${index}" title="Eliminar archivo">
                        <span class="remove-icon">✕</span>
                    </button>
                </div>
            `;
            previewContainer.appendChild(fileItem);
        });

        // Agregar estilos si no existen
        if (!document.getElementById('archivo-preview-styles-bitacora')) {
            const style = document.createElement('style');
            style.id = 'archivo-preview-styles-bitacora';
            style.textContent = `
                .preview-archivos {
                    margin-top: 10px;
                }
                .archivo-preview-item {
                    margin-bottom: 4px;
                }
                .archivo-preview-content {
                    display: flex;
                    align-items: center;
                    padding: 8px 12px;
                    background: #f1f3f4;
                    border: 1px solid #d0d7de;
                    border-radius: 6px;
                    gap: 8px;
                    min-height: 36px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }
                .archivo-preview-icon {
                    font-size: 16px;
                    flex-shrink: 0;
                }
                .archivo-preview-name {
                    flex: 1;
                    font-weight: 400;
                    color: #1f2328;
                    font-size: 14px;
                    line-height: 1.2;
                    text-overflow: ellipsis;
                    overflow: hidden;
                    white-space: nowrap;
                }
                .archivo-preview-size {
                    font-size: 12px;
                    color: #656d76;
                    flex-shrink: 0;
                    margin-left: 8px;
                }
                .archivo-preview-remove {
                    background: #cf222e;
                    border: none;
                    border-radius: 6px;
                    color: white;
                    width: 20px;
                    height: 20px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: background-color 0.2s;
                    flex-shrink: 0;
                    margin-left: 8px;
                }
                .archivo-preview-remove:hover {
                    background: #a40e26;
                }
                .remove-icon {
                    font-size: 11px;
                    font-weight: bold;
                    line-height: 1;
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Event listener para eliminar archivos
    if (previewContainer) {
        previewContainer.addEventListener('click', function(e) {
            if (e.target.closest('.archivo-preview-remove')) {
                const index = parseInt(e.target.closest('.archivo-preview-remove').dataset.index);
                selectedFiles.splice(index, 1);
                updateFileInputBitacora();
                showFilePreviewBitacora();
            }
        });
    }
    
    if (dropzoneBitacora && inputArchivos) {
        dropzoneBitacora.addEventListener('click', function() {
            inputArchivos.click();
        });
        
        dropzoneBitacora.addEventListener('dragover', function(e) {
            e.preventDefault();
            dropzoneBitacora.style.backgroundColor = '#e3f2fd';
            dropzoneBitacora.style.borderColor = '#2196f3';
        });
        
        dropzoneBitacora.addEventListener('dragleave', function(e) {
            e.preventDefault();
            dropzoneBitacora.style.backgroundColor = '';
            dropzoneBitacora.style.borderColor = '';
        });
        
        dropzoneBitacora.addEventListener('drop', function(e) {
            e.preventDefault();
            dropzoneBitacora.style.backgroundColor = '';
            dropzoneBitacora.style.borderColor = '';
            
            const files = Array.from(e.dataTransfer.files);
            // Agregar archivos a la lista existente
            selectedFiles.push(...files);
            updateFileInputBitacora();
            showFilePreviewBitacora();
        });
        
        inputArchivos.addEventListener('change', function() {
            const files = Array.from(this.files);
            // Agregar archivos a la lista existente (no reemplazar)
            selectedFiles.push(...files);
            updateFileInputBitacora();
            showFilePreviewBitacora();
        });
    }
    
    // Botón limpiar
    const btnLimpiar = document.getElementById('btnLimpiarObservacion');
    if (btnLimpiar) {
        btnLimpiar.addEventListener('click', function() {
            if (confirm('¿Estás seguro de que quieres limpiar todos los campos?')) {
                // Limpiar campos básicos
                const textoInput = document.getElementById('observacionTexto');
                if (textoInput) textoInput.value = '';
                
                const archivosInput = document.getElementById('observacionArchivos');
                if (archivosInput) archivosInput.value = '';
                
                const fallidaCheckbox = document.getElementById('marcarFallidaCheckbox');
                if (fallidaCheckbox) fallidaCheckbox.checked = false;
                
                // Limpiar ID Mercado Público
                const idMercadoPublicoInput = document.getElementById('idMercadoPublicoInput');
                if (idMercadoPublicoInput) {
                    idMercadoPublicoInput.value = '';
                }
                
                // Limpiar campos de Recepción de Ofertas
                const numeroOfertasInput = document.getElementById('numeroOfertasInput');
                if (numeroOfertasInput) {
                    numeroOfertasInput.value = '';
                    numeroOfertasInput.style.borderColor = '';
                    numeroOfertasInput.style.backgroundColor = '';
                }
                
                const empresaNombreInput = document.getElementById('empresaNombreInput');
                if (empresaNombreInput) {
                    empresaNombreInput.value = '';
                }
                
                const empresaRutInput = document.getElementById('empresaRutInput');
                if (empresaRutInput) {
                    empresaRutInput.value = '';
                    empresaRutInput.style.borderColor = '';
                    empresaRutInput.style.backgroundColor = '';
                }
                
                if (accionEtapa) accionEtapa.value = 'none';
                if (previewContainer) previewContainer.innerHTML = '';
                
                // Limpiar array de archivos seleccionados
                selectedFiles = [];
                updateFileInputBitacora();
                
                // Feedback visual del botón
                const textoOriginal = btnLimpiar.innerHTML;
                btnLimpiar.innerHTML = '<span class="btn-icono">✅</span>Limpiado';
                btnLimpiar.style.background = '#22c55e';
                btnLimpiar.style.color = 'white';
                
                setTimeout(() => {
                    btnLimpiar.innerHTML = textoOriginal;
                    btnLimpiar.style.background = '';
                    btnLimpiar.style.color = '';
                }, 1500);
                
                // Restaurar etapa original si se había cambiado
                if (nombreEtapaActual && etapaOriginal) {
                    // Restaurar el nombre y ID de la etapa original
                    nombreEtapaActual.textContent = etapaOriginal.nombre;
                    nombreEtapaActual.dataset.etapaId = etapaOriginal.id;
                    
                    // Restaurar estilos normales
                    nombreEtapaActual.style.background = '#f0f9ff';
                    nombreEtapaActual.style.borderColor = '#bae6fd';
                    nombreEtapaActual.style.color = '#0275d8';
                    nombreEtapaActual.style.transition = '';
                }
            }
        });
    }
    
    // Envío del formulario integrado
    if (formObservacionBitacora) {
        formObservacionBitacora.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const licitacionId = this.querySelector('input[name="licitacion_id"]').value;        const texto = document.getElementById('observacionTexto').value;
        
        // Solo obtener archivos si el campo existe (panel de operadores)
        const archivosInput = document.getElementById('observacionArchivos');
        const archivos = archivosInput ? archivosInput.files : [];
        
        // Solo obtener elementos de marcado como fallida si existen (panel de operadores)
        const marcarFallidaCheckbox = document.getElementById('marcarFallidaCheckbox');
        const tipoFallidaSelect = document.getElementById('tipoFallidaSelect');
        const marcarFallida = marcarFallidaCheckbox ? marcarFallidaCheckbox.checked : false;
        const tipoFallida = tipoFallidaSelect ? tipoFallidaSelect.value : '';
        
        const accionEtapaValue = accionEtapa ? accionEtapa.value : 'none';
        
        // Solo obtener ID Mercado Público si el campo existe (panel de operadores)
        const idMercadoPublicoInput = document.getElementById('idMercadoPublicoInput');
        const idMercadoPublico = idMercadoPublicoInput ? idMercadoPublicoInput.value.trim() : '';
        
        if (!texto.trim()) {
            alert('La observación no puede estar vacía.');
            return;
        }
        
        // Validar que si se marca como fallida, se seleccione un tipo
        if (marcarFallida && !tipoFallida) {
            alert('Debe seleccionar un tipo de falla.');
            return;
        }
        
        const formData = new FormData();
        formData.append('texto', texto);
        
        // Agregar ID Mercado Público si está presente
        if (idMercadoPublico) {
            formData.append('id_mercado_publico', idMercadoPublico);
        }
        
        for (let i = 0; i < archivos.length; i++) {
            formData.append('archivos', archivos[i]);
        }
        
        if (marcarFallida) {
            formData.append('marcar_fallida', 'on');
            if (tipoFallida) {
                formData.append('tipo_fallida', tipoFallida);
            }
        }
        
        if (accionEtapaValue === 'advance') {
            formData.append('avanzar_etapa', 'on');
        }
                  // En lugar de enviar vía fetch, usar el formulario estándar
        const form = document.getElementById('formObservacionBitacora');
        
        // Agregar los campos necesarios si no están presentes
        if (accionEtapaValue !== 'none') {
            let accionEtapaInput = document.getElementById('accionEtapa');
            if (!accionEtapaInput) {
                accionEtapaInput = document.createElement('input');
                accionEtapaInput.type = 'hidden';
                accionEtapaInput.name = 'accion_etapa';
                accionEtapaInput.id = 'accionEtapa';
                form.appendChild(accionEtapaInput);
            }
            accionEtapaInput.value = accionEtapaValue;
        }
        
        // Agregar etapa actual si se está avanzando
        if (accionEtapaValue === 'advance' && nombreEtapaActual) {
            let etapaInput = document.createElement('input');
            etapaInput.type = 'hidden';
            etapaInput.name = 'etapa';
            etapaInput.value = nombreEtapaActual.dataset.etapaId;
            form.appendChild(etapaInput);
        }
        
        // Enviar el formulario de manera estándar
        form.submit();
        });
    }
    
    // --- MANEJO DE ARCHIVOS DEL MODAL ---

    // Función para actualizar el input del modal con los archivos seleccionados
    function updateModalFileInput() {
        if (!modalArchivos) return;
        const dt = new DataTransfer();
        modalSelectedFiles.forEach(file => dt.items.add(file));
        modalArchivos.files = dt.files;
    }

    // Función para obtener el icono apropiado según el tipo de archivo
    function getFileIcon(fileName) {
        const extension = fileName.split('.').pop().toLowerCase();
        const iconMap = {
            // Documentos
            'pdf': '📄',
            'doc': '📝',
            'docx': '📝',
            'txt': '📝',
            'rtf': '📝',
            'odt': '📝',
            // Hojas de cálculo
            'xls': '📊',
            'xlsx': '📊',
            'csv': '📊',
            'ods': '📊',
            // Presentaciones
            'ppt': '📑',
            'pptx': '📑',
            'odp': '📑',
            // Imágenes
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'png': '🖼️',
            'gif': '🖼️',
            'bmp': '🖼️',
            'svg': '🖼️',
            'webp': '🖼️',
            // Archivos comprimidos
            'zip': '🗜️',
            'rar': '🗜️',
            '7z': '🗜️',
            'tar': '🗜️',
            'gz': '🗜️',
            // Otros
            'xml': '📋',
            'json': '📋',
            'html': '🌐',
            'css': '🎨',
            'js': '⚙️'
        };
        
        return iconMap[extension] || '📄';
    }

    // Función para formatear el tamaño del archivo
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Función para mostrar la vista previa de archivos del modal
    function showModalFilePreview() {
        if (!modalPreviewArchivos) return;
        
        modalPreviewArchivos.innerHTML = '';
        
        if (modalSelectedFiles.length === 0) {
            // Remover contador si no hay archivos
            const existingCounter = modalDropzone?.querySelector('.modal-files-counter');
            if (existingCounter) existingCounter.remove();
            return;
        }

        // Agregar/actualizar contador de archivos
        updateFileCounter();

        modalSelectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'modal-file-item';
            
            const fileIcon = getFileIcon(file.name);
            const fileSize = formatFileSize(file.size);
            
            fileItem.innerHTML = `
                <div class="modal-file-icon">${fileIcon}</div>
                <div class="modal-file-info">
                    <div class="modal-file-name">${file.name}</div>
                    <div class="modal-file-size">${fileSize}</div>
                </div>
                <button type="button" class="modal-file-remove" data-index="${index}" title="Eliminar archivo">
                    ✕
                </button>
            `;
            modalPreviewArchivos.appendChild(fileItem);
        });
    }

    // Función para actualizar el contador de archivos
    function updateFileCounter() {
        if (!modalDropzone) return;
        
        let counter = modalDropzone.querySelector('.modal-files-counter');
        
        if (modalSelectedFiles.length > 0) {
            if (!counter) {
                counter = document.createElement('div');
                counter.className = 'modal-files-counter';
                modalDropzone.style.position = 'relative';
                modalDropzone.appendChild(counter);
            }
            counter.textContent = modalSelectedFiles.length;
        } else if (counter) {
            counter.remove();
        }
    }

    // Función para mostrar feedback visual temporal
    function showDropzoneFeedback(type = 'success') {
        if (!modalDropzone) return;
        
        modalDropzone.classList.add(type);
        
        setTimeout(() => {
            modalDropzone.classList.remove(type);
        }, 1000);
    }

    // Event listener para eliminar archivos del modal
    if (modalPreviewArchivos) {
        modalPreviewArchivos.addEventListener('click', function(e) {
            if (e.target.closest('.modal-file-remove')) {
                const index = parseInt(e.target.closest('.modal-file-remove').dataset.index);
                modalSelectedFiles.splice(index, 1);
                updateModalFileInput();
                showModalFilePreview();
            }
        });
    }

    // Event listeners para el dropzone del modal
    if (modalDropzone && modalArchivos) {
        modalDropzone.addEventListener('click', function() {
            modalArchivos.click();
        });

        modalDropzone.addEventListener('dragover', function(e) {
            e.preventDefault();
            modalDropzone.classList.add('dragover');
        });

        modalDropzone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            modalDropzone.classList.remove('dragover');
        });

        modalDropzone.addEventListener('drop', function(e) {
            e.preventDefault();
            modalDropzone.classList.remove('dragover');
            
            const files = Array.from(e.dataTransfer.files);
            if (files.length > 0) {
                // Mostrar feedback de procesamiento
                modalDropzone.classList.add('processing');
                
                setTimeout(() => {
                    // Validar archivos
                    const { validFiles, errors } = validateFiles(files);
                    
                    // Mostrar errores si los hay
                    if (errors.length > 0) {
                        showFileErrors(errors);
                    }
                    
                    // Agregar archivos válidos a la lista existente
                    if (validFiles.length > 0) {
                        modalSelectedFiles.push(...validFiles);
                        updateModalFileInput();
                        showModalFilePreview();
                        showDropzoneFeedback('success');
                    }
                    
                    modalDropzone.classList.remove('processing');
                }, 300);
            }
        });

        modalArchivos.addEventListener('change', function() {
            const files = Array.from(this.files);
            if (files.length > 0) {
                // Mostrar feedback de procesamiento
                modalDropzone.classList.add('processing');
                
                setTimeout(() => {
                    // Validar archivos
                    const { validFiles, errors } = validateFiles(files);
                    
                    // Mostrar errores si los hay
                    if (errors.length > 0) {
                        showFileErrors(errors);
                    }
                    
                    // Agregar archivos válidos a la lista existente (no reemplazar)
                    if (validFiles.length > 0) {
                        modalSelectedFiles.push(...validFiles);
                        updateModalFileInput();
                        showModalFilePreview();
                        showDropzoneFeedback('success');
                    }
                    
                    modalDropzone.classList.remove('processing');
                }, 300);
            }
        });
    }
    
    // Configuración para validación de archivos
    const ARCHIVO_CONFIG = {
        maxSize: 10 * 1024 * 1024, // 10MB máximo por archivo
        allowedTypes: [
            // Documentos
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'application/rtf',
            // Hojas de cálculo
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/csv',
            // Presentaciones
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            // Imágenes
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/bmp',
            'image/svg+xml',
            'image/webp',
            // Archivos comprimidos
            'application/zip',
            'application/x-rar-compressed',
            'application/x-7z-compressed',
            // Otros
            'application/xml',
            'application/json',
            'text/html',
            'text/css',
            'application/javascript'
        ]
    };

    // Función para validar archivos
    function validateFiles(files) {
        const errors = [];
        const validFiles = [];

        files.forEach(file => {
            // Validar tamaño
            if (file.size > ARCHIVO_CONFIG.maxSize) {
                errors.push(`${file.name}: El archivo es demasiado grande (máximo ${formatFileSize(ARCHIVO_CONFIG.maxSize)})`);
                return;
            }

            // Validar tipo (opcional - permitir todos los tipos pero mostrar advertencia)
            if (!ARCHIVO_CONFIG.allowedTypes.includes(file.type) && file.type !== '') {
                // Solo mostrar advertencia, no bloquear
                console.warn(`Tipo de archivo no común: ${file.name} (${file.type})`);
            }

            validFiles.push(file);
        });

        return { validFiles, errors };
    }

    // Función para mostrar mensajes de error
    function showFileErrors(errors) {
        if (errors.length === 0) return;

        const errorContainer = document.createElement('div');
        errorContainer.className = 'modal-file-errors';
        errorContainer.innerHTML = `
            <div class="error-header">
                <span class="error-icon">⚠️</span>
                <span class="error-title">Algunos archivos no se pudieron agregar:</span>
            </div>
            <ul class="error-list">
                ${errors.map(error => `<li>${error}</li>`).join('')}
            </ul>
        `;

        // Insertar antes de la vista previa
        if (modalPreviewArchivos && modalPreviewArchivos.parentNode) {
            modalPreviewArchivos.parentNode.insertBefore(errorContainer, modalPreviewArchivos);
            
            // Remover después de 5 segundos
            setTimeout(() => {
                errorContainer.remove();
            }, 5000);
        }
    }
    
    // Función para formatear RUT chileno
    function formatearRUT(rut) {
        // Eliminar puntos, guiones y espacios
        let rutLimpio = rut.replace(/[\.\-\s]/g, '');
        
        // Si no tiene contenido, retornar vacío
        if (!rutLimpio) return '';
        
        // Separar el dígito verificador
        let cuerpo = rutLimpio.slice(0, -1);
        let dv = rutLimpio.slice(-1).toUpperCase();
        
        // Formatear el cuerpo con puntos
        cuerpo = cuerpo.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        
        return `${cuerpo}-${dv}`;
    }
    
    // Función para validar RUT chileno
    function validarRUT(rut) {
        if (!rut) return true; // Permitir vacío
        
        // Limpiar el RUT
        let rutLimpio = rut.replace(/[\.\-\s]/g, '');
        
        // Verificar que tenga al menos 2 caracteres (1 dígito + DV)
        if (rutLimpio.length < 2) return false;
        
        // Separar cuerpo y dígito verificador
        let cuerpo = rutLimpio.slice(0, -1);
        let dv = rutLimpio.slice(-1).toUpperCase();
        
        // Verificar que el cuerpo sean solo números
        if (!/^\d+$/.test(cuerpo)) return false;
        
        // Calcular dígito verificador
        let suma = 0;
        let multiplicador = 2;
        
        for (let i = cuerpo.length - 1; i >= 0; i--) {
            suma += parseInt(cuerpo[i]) * multiplicador;
            multiplicador = multiplicador === 7 ? 2 : multiplicador + 1;
        }
        
        let dvCalculado = 11 - (suma % 11);
        if (dvCalculado === 11) dvCalculado = '0';
        if (dvCalculado === 10) dvCalculado = 'K';
        else dvCalculado = dvCalculado.toString();
        
        return dv === dvCalculado;
    }
    
    // Agregar event listeners para el formateo y validación del RUT
    const empresaRutInput = document.getElementById('empresaRutInput');
    if (empresaRutInput) {
        empresaRutInput.addEventListener('input', function() {
            let rutFormateado = formatearRUT(this.value);
            this.value = rutFormateado;
            
            // Validar RUT y mostrar feedback visual
            if (rutFormateado && !validarRUT(rutFormateado)) {
                this.style.borderColor = '#e74c3c';
                this.style.backgroundColor = '#fdf2f2';
            } else {
                this.style.borderColor = '';
                this.style.backgroundColor = '';
            }
        });
        
        empresaRutInput.addEventListener('blur', function() {
            if (this.value && !validarRUT(this.value)) {
                alert('El RUT ingresado no es válido. Por favor verifique.');
                this.focus();
            }
        });
    }
    
    // Agregar event listener para validar número de ofertas
    const numeroOfertasInput = document.getElementById('numeroOfertasInput');
    if (numeroOfertasInput) {
        numeroOfertasInput.addEventListener('input', function() {
            // Validar que sea un número positivo
            let valor = parseInt(this.value);
            if (isNaN(valor) || valor < 0) {
                this.style.borderColor = '#e74c3c';
                this.style.backgroundColor = '#fdf2f2';
            } else {
                this.style.borderColor = '';
                this.style.backgroundColor = '';
            }
        });
    }
});
