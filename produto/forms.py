from django.forms.models import BaseInlineFormSet
from django import forms
from django import forms
from django.core.exceptions import ValidationError
from .models import Produto  # Importe seu modelo Produto


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'nome',
            'descricao_curta',
            'descricao_longa',
            'imagem',
            'slug',
            'preco_marketing',
            'preco_marketing_promocional',
            'tipo',
            'category',
        ]

    def clean_imagem(self):
        imagem = self.cleaned_data.get('imagem')

        # Valida se uma imagem foi fornecida
        if not imagem:
            raise ValidationError("Nenhuma imagem fornecida")
        
        # Valida o tipo de arquivo, se necessário
        if not imagem.name.lower().endswith(('png', 'jpg', 'jpeg')):
            raise ValidationError("Apenas arquivos PNG, JPG ou JPEG são permitidos.")
        
        return imagem

    def save(self, commit=True):
        # Salva o produto normalmente
        return super().save(commit=commit)





class VariacaoObrigatoria(BaseInlineFormSet):
    def _construct_form(self, i, **kwargs):
        form = super(VariacaoObrigatoria, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form
    



