from django import template

#FUNCION PARA MOSTRAR LOS NUMEROS EN FORMATO CHILENO#
def chilean_thousands(value):
    try:
        value = float(value)
        return f'{int(value):,}'.replace(",", ".")
    except (ValueError, TypeError):
        return value

register = template.Library()
register.filter('chilean_thousands', chilean_thousands)
