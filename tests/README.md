# Tests y Scripts de Validación

Esta carpeta contiene scripts de testing manual y utilidades para validar funcionalidades específicas del sistema.

## Scripts Disponibles

### `test_etapas_inhabilitadas.py`
**Propósito**: Prueba la funcionalidad de etapas inhabilitadas en licitaciones.

**Funcionalidad que prueba**:
- Lógica de inhabilitación de etapas según moneda y monto
- Regla de negocio: Licitaciones en UF con monto < 500 saltan la etapa "Aprobación del Concejo Municipal"
- Métodos del modelo: `debe_saltar_aprobacion_consejo()` y `get_etapas_todas_con_inhabilitacion()`

**Casos de prueba**:
- ✅ UF con monto < 500 (debe saltar etapa del consejo)
- ✅ UF con monto >= 500 (no debe saltar etapa)
- ✅ Otras monedas (no debe saltar etapa)

**Cómo ejecutar**:
```bash
cd tests/
python test_etapas_inhabilitadas.py
```

**Cuándo usar**:
- Después de cambios en el modelo `Licitacion`
- Al modificar lógica de etapas
- Para debuggear problemas con etapas inhabilitadas
- Durante desarrollo de nuevas funcionalidades de etapas

## Estructura de Tests

```
tests/
├── README.md                      # Este archivo
├── test_etapas_inhabilitadas.py   # Test de etapas inhabilitadas
└── [futuros scripts de test]
```

## Convenciones

- **Nomenclatura**: `test_[funcionalidad].py`
- **Limpieza**: Los scripts deben limpiar datos de prueba al finalizar
- **Logging**: Usar prints descriptivos con emojis para mejor legibilidad
- **Documentación**: Cada script debe tener docstring explicativo

## Notas Importantes

- ⚠️ **Estos scripts interactúan con la base de datos real**
- 🧹 **Siempre limpian los datos de prueba al finalizar**
- 🔧 **Son para testing manual, no automático**
- 📋 **Útiles para debugging y validación de funcionalidades**

## Agregar Nuevos Tests

Para agregar un nuevo script de test:

1. Crear archivo `test_[nombre_funcionalidad].py`
2. Incluir configuración Django al inicio
3. Implementar función de prueba con casos de test
4. Limpiar datos de prueba al finalizar
5. Documentar en este README

---

**Nota**: Para tests automáticos usar el framework de testing de Django (`python manage.py test`)
