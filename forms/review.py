from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class ReviewForm(FlaskForm):
    contenido = TextAreaField('Tu opinión', validators=[
        DataRequired(),
        Length(min=10, max=2000, message='La reseña debe tener entre 10 y 2000 caracteres.')
    ])
    calificacion = SelectField('Calificación', validators=[DataRequired()], 
                              choices=[
                                  (0.5, '0.5 - Pésimo'),
                                  (1.0, '1.0 - Muy malo'),
                                  (1.5, '1.5 - Malo'),
                                  (2.0, '2.0 - Regular bajo'),
                                  (2.5, '2.5 - Regular'),
                                  (3.0, '3.0 - Regular alto'),
                                  (3.5, '3.5 - Bueno'),
                                  (4.0, '4.0 - Muy bueno'),
                                  (4.5, '4.5 - Excelente'),
                                  (5.0, '5.0 - Perfecto')
                              ], coerce=float)
    ciudad_declarada = SelectField('Ciudad', validators=[DataRequired()])
    submit = SubmitField('Enviar Reseña')
    
    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        # The choices will be populated in the route