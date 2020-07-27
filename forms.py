from wtforms import form,IntegerField,StringField,TextAreaField,BooleanField,validators
class AddProducts(form):
    name=StringField('Name',[validators.data_required()])
    price = IntegerField('price', [validators.data_required()])
    discription=StringField('Discription',[validators.data_required()])
    colors=TextAreaField('colors',validators.data_required())



