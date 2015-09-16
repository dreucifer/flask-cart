import wtforms as forms
import wtforms.validators as validators


class AddToCartForm(forms.Form):

    product_id = forms.HiddenField('Product ID')
    quantity = forms.IntegerField('Quantity', [validators.NumberRange(min=1, max=999)])

    def __init__(self, *args, **kwargs):
        self.cart = kwargs.pop('cart')
        self.product = kwargs.pop('product')
        super(AddToCartForm, self).__init__(*args, **kwargs)

    def save(self):
        quantity = self.quantity.data or 1
        return self.cart.add(self.product, quantity=quantity,
                             check_quantity=False, replace=False)


class ReplaceCartLineForm(AddToCartForm):
    def __init__(self, *args, **kwargs):
        super(ReplaceCartLineForm, self).__init__(*args, **kwargs)
        self.cart_line = self.cart.get_line(self.product)

    def save(self):
        return self.cart.add(self.product, quantity=self.quantity,
                             replace=True)
