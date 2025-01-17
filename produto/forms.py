from django.forms.models import BaseInlineFormSet
from django import forms
from django import forms
from django.core.exceptions import ValidationError
from .models import Produto  # Importe seu modelo Produto


# class ProdutoForm(forms.ModelForm):
#     class Meta:
#         model = Produto
#         fields = [
#             'nome',
#             'descricao_curta',
#             'descricao_longa',
#             'imagem',
#             'slug',
#             'preco_marketing',
#             'preco_marketing_promocional',
#             'tipo',
#             'category',
#         ]

#     def clean_imagem(self):
#         imagem = self.cleaned_data.get('imagem')

#         # Valida se uma imagem foi fornecida
#         if not imagem:
#             raise ValidationError("Nenhuma imagem fornecida")
        
#         # Valida o tipo de arquivo, se necessário
#         if not imagem.name.lower().endswith(('png', 'jpg', 'jpeg')):
#             raise ValidationError("Apenas arquivos PNG, JPG ou JPEG são permitidos.")
        
#         return imagem

#     def save(self, commit=True):
#         # Salva o produto normalmente
#         return super().save(commit=commit)


from django import forms
from django.utils.text import slugify
from .models import Produto, Category

class ProdutoForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        label="Categoria",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Produto
        fields = [
            'nome',
            'descricao_curta',
            'descricao_longa',
            'imagem',
            'slug',  # Adicionado o campo slug
            'preco_marketing',
            'preco_marketing_promocional',
            'tipo',
            'category',
            'visivel'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao_curta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'descricao_longa': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'slug': forms.HiddenInput(),  # Campo oculto pois será gerado automaticamente
            'preco_marketing': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'preco_marketing_promocional': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'visivel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'nome': 'Nome do Produto',  # Personalizado aqui
            'descricao_curta': 'Descrição do Produto',
        }

    def clean_imagem(self):
        imagem = self.cleaned_data.get('imagem')
        if imagem:
            if not imagem.name.lower().endswith(('png', 'jpg', 'jpeg')):
                raise forms.ValidationError("Apenas arquivos PNG, JPG ou JPEG são permitidos.")
        return imagem

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome')
        
        # Gera o slug apenas se o nome existir e o slug não foi fornecido
        if nome and not cleaned_data.get('slug'):
            cleaned_data['slug'] = slugify(nome)
        
        return cleaned_data

    def save(self, commit=True):
        produto = super().save(commit=False)
        
        # Garante que o slug seja gerado/atualizado
        if not produto.slug:
            produto.slug = slugify(produto.nome)
        
        if commit:
            produto.save()
        
        return produto


class VariacaoObrigatoria(BaseInlineFormSet):
    def _construct_form(self, i, **kwargs):
        form = super(VariacaoObrigatoria, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form
    



