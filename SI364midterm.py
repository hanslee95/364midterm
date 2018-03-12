###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, ValidationError, IntegerField # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, Length # Here, too
from flask_sqlalchemy import SQLAlchemy
import requests
import simplejson as json

## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True

## All app.config values
app.config['SECRET_KEY'] = 'hard to guess string from si364'
##Used createdb midterm to create db on postico which made the localhost work. Maybe work on name insertion that takes you
##to name of person with their favorite pokemons.
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/midterms364"
## Provided:
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)


######################################
######## HELPER FXNS (If any) ########
######################################




##################
##### MODELS #####
##################

class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))
    pokemon = db.relationship('Pokemon', backref=db.backref('Name', lazy = True))

    

class Pokemon(db.Model):
    __tablename__ = "pokemon"
    id = db.Column(db.Integer,primary_key=True)
    pokemon = db.Column(db.String())
    name_id = db.Column(db.Integer, db.ForeignKey('names.id'))

    
    

###################
###### FORMS ######
###################

class NameForm(FlaskForm):
    name = StringField("Please enter your name.",validators=[Required()])
    poke_name = StringField('Choose your favorite pokemon. (In all lowercase letters) E.g. pikachu, squirtle, onix ', validators = [Required()])
    submit = SubmitField("Submit")



#######################
###### VIEW FXNS ######
#######################
@app.route('/')
def base():
    return render_template('base.html')



@app.route('/input', methods = ['GET','POST'])
def input():
    form = NameForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
   
    name = form.name.data
    poke_name = form.poke_name.data
        

    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))

    return render_template('input.html',form=form)





@app.route('/pokeguess', methods = ['GET','POST'])
def poke_guess():
    form = NameForm(request.form)
    if form.validate_on_submit():
        name = form.name.data
        poke_name = form.poke_name.data
        trainer = Name(name=name)
        db.session.add(trainer)
        db.session.commit()
        pokemon = Pokemon(pokemon = poke_name, name_id = trainer.id)
        db.session.add(pokemon)
        db.session.commit()

    name = form.name.data
    poke_name = form.poke_name.data
    result = requests.get('http://pokeapi.co/api/v2/pokemon/{}'.format(poke_name)) 
    poke_dict = json.loads(result.text)
    height = poke_dict['height']
    return render_template('poke_guess.html', name = name, poke_name = poke_name, weight = poke_dict['weight'], height = height)



@app.route('/names')
def all_names():
    pokemon = Pokemon.query.all()
    trainer_and_pokemon = []
    for p in pokemon:
        
        trainer = Name.query.filter_by(id=p.name_id).first() # Change
        tup = (trainer.name, p.pokemon)
        trainer_and_pokemon.append(tup)
    return render_template('name_example.html',trainer_and_pokemon=trainer_and_pokemon)






#######################
###### ERROR HANDLER ######
#######################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404






## Code to run the application...

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!

if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual

