from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class SearchForm(FlaskForm):
    query = StringField('Buscar', validators=[DataRequired()])
    category = SelectField('Categoría', coerce=int, validators=[Optional()])
    submit = SubmitField('Buscar')
    
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        # The choices will be populated in the route
        self.category.choices = [(0, 'Todas las categorías')]