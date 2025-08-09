# forms.py
from django import forms
from .models import Licitacion, Financiamiento

class LicitacionForm(forms.ModelForm):
    financiamiento = forms.ModelMultipleChoiceField(
        queryset=Financiamiento.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'size': 5}),
        label="Financiamiento"
    )
    documentos = forms.FileField(
        label="Adjuntar documentos",
        required=False,
        widget=forms.ClearableFileInput(attrs={'multiple': True})
    )

    class Meta:
        model = Licitacion
        fields = [
            'numero_pedido',
            'id_mercado_publico',
            'numero_cuenta',
            'operador_user',
            'operador_2',
            'iniciativa',
            'direccion',
            'institucion',
            'moneda',
            'categoria',
            'financiamiento',
            'monto_presupuestado',
            'tipo_presupuesto',
            'en_plan_anual',
            'etapa_fk',
            'departamento',
            'llamado_cotizacion',
            'pedido_devuelto',
            'tipo_licitacion',
            'licitacion_fallida_linkeada'
        ]
        widgets = {
            'tipo_licitacion': forms.HiddenInput(),
            'licitacion_fallida_linkeada': forms.HiddenInput(),
        }
