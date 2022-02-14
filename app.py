from flask import Flask,abort, jsonify,request
import os
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from sqlalchemy import *
from dotenv import load_dotenv
load_dotenv()

motdepasse=quote_plus(os.getenv('pswrd'))
dialect=quote_plus(os.getenv('dialect'))
user=quote_plus(os.getenv('user'))
host=quote_plus(os.getenv('host'))
database=quote_plus(os.getenv('database'))
port=quote_plus(os.getenv('port'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://ndckkzeqdicovm:fd4c01724735b95d2fe0bfc4d64468386d331793a78e395682c6ed2e02d981f2@ec2-54-157-160-218.compute-1.amazonaws.com:5432/d6i75jaq0h3m9h"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Categorie(db.Model):
    __tablename__ = "Categories"
    id = db.Column(db.Integer, primary_key=True)
    libelle_categorie = db.Column(db.String(50), nullable=false)
    les_livres = db.relationship('Livre',backref='Categorie',lazy=True)

    def __init__(self, libelle_categorie):
        self.libelle_categorie = libelle_categorie

    def insert(self):
        db.session.add(self)
        db.session.commit()
  
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
        'id': self.id,
        'libelle': self.libelle_categorie
        }

class Livre(db.Model):
    __tablename__ = "Livres"
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(50), nullable=False)
    titre = db.Column(db.String(50), nullable=False)
    date_publication = db.Column(db.Date, nullable=False)
    auteur = db.Column(db.String(50), nullable=False)
    editeur = db.Column(db.String(50), nullable=False)
    categorie_id = db.Column(db.Integer, db.ForeignKey('Categories.id'), nullable=False)

    def __init__(self, isbn, titre, date_publication, auteur, editeur, categorie_id):
        self.isbn = isbn
        self.titre = titre
        self.date_publication = date_publication
        self.auteur = auteur
        self.editeur = editeur
        self.categorie_id = categorie_id
        
    def insert(self):
        db.session.add(self)
        db.session.commit()
  
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        cat  = Categorie.query.get(self.categorie_id)
        return {
        'id': self.id,
        'isbn': self.isbn,
        'titre': self.titre,
        'date de publication': self.date_publication,
        'auteur': self.auteur,
        'editeur': self.editeur,
        'categorie': cat.format()
        }

db.create_all()

    
#  Récupérer tous les livres

@app.route('/livres')
def get_all_livres():
    livres = Livre.query.all()
    livres = [livre.format() for livre in livres]
    return jsonify(
        {
        'success':True,
        'livres':livres,
        'nombre':len(Livre.query.all())}
    )
    

#  Récupérer les livres d'une catégorie

@app.route('/livres/categories/<int:cat_id>')
def get_all_livres_of_catgeorie(cat_id):
    livres = Livre.query.filter(Livre.categorie_id == cat_id)
    if livres is not None:
        cat = Categorie.query.get(cat_id)
        livres = [livre.format() for livre in livres]
        return jsonify(
            {
            'success':True,
            'livres':livres,
            'nombre':Livre.query.filter(Livre.categorie_id == cat_id).count()
            }
        )
    

#  Récupérer un livre
   
@app.route('/livres/<int:livre_id>')
def one_livre(livre_id):
    livre = Livre.query.get(livre_id)
 
    if livre is None:
        abort(404)
    else:
        return jsonify({
            'success':True,
            'id':livre_id,
            'livre':livre.format()
        })
    
# Ajouter un livre      
        
@app.route('/livres',methods=['POST'])
def add_livre():
    body = request.get_json()
    new_isbn = body.get('isbn',None)
    new_auteur = body.get('auteur',None)
    new_editeur = body.get('editeur',None)
    new_date_publication = body.get('date_publication',None)
    new_titre = body.get('titre',None)
    new_categorie_id =body.get('categorie_id',None)
    livre = Livre (isbn=new_isbn,auteur=new_auteur,date_publication=new_date_publication,categorie_id=new_categorie_id,editeur=new_editeur,titre=new_titre)
    livre.insert()
    livres=Livre.query.all()
    livre_format=[livre.format() for livre in livres]
    return jsonify({
          'success':True,
          'created':livre.id,
          'livres':livre_format,
          'total_livre':len(Livre.query.all())
        })
    

#  Mettre à jour un livre

@app.route('/livres/<int:livre_id>',methods=['PATCH'])
def update_livre(livre_id):
    body=request.get_json()
    try:
      livre = Livre.query.filter(Livre.id==livre_id).one_or_none()
      if livre is None:
            abort(404)
      if 'isbn' in body:
            livre.isbn = body.get('isbn')
      if 'titre' in body:
            livre.titre = body.get('titre')
      if 'auteur' in body:
            livre.auteur = body.get('auteur')
      if 'date_publication' in body:
            livre.date_publication = body.get('date_publication')
      if 'editeur' in body:
            livre.editeur = body.get('editeur')
      if 'categorie_id' in body:
            livre.categorie_id = body.get('categorie_id')
      livre.update()
      return jsonify({
        'success':True,
        'id':livre.id,
        'livre_modifie':livre.format()
      })
    except:
      abort(400)

    

#  Supprimer un livre

@app.route('/livres/<int:livre_id>',methods=['DELETE'])
def supprimer_livre(livre_id):
    try:
        livre = Livre.query.get(livre_id)
        if livre is None:
            abort(404)
        else:
            livre.delete()
            return jsonify({
                "success":True,
                "id_supprimee":livre_id,
                "total_livre":len(Livre.query.all())
            })
    except:
        abort(400)
        

    

#   Lister les catégories

@app.route('/categories')
def get_all_categorie():
    categories = Categorie.query.all()
    categories =[cat.format() for cat in categories]
    return jsonify(
        {
        'success':True,
        'categories':categories,
        'nombre':len(Categorie.query.all())}
    )
    
    

#  Récupérer une catégorie
    
@app.route('/categories/<int:id>')
def one_categorie(id):
    cat = Categorie.query.get(id)
    if cat is None:
        abort(404)
    else:
        return jsonify({
            'success':True,
            'id':id,
            'categorie':cat.format()
        })
    

# Ajouter une categorie      
        
@app.route('/categories',methods=['POST'])
def add_categorie():
    body=request.get_json()
    if 'libelle_categorie' in body:
        new_categorie_libelle = body.get('libelle_categorie',None)
        cat = Categorie(libelle_categorie=new_categorie_libelle)
        cat.insert()
        categories = Categorie.query.all()
        categories_format = [cat.format() for cat in categories]
        return jsonify({
            'success':True,
            'cree':cat.id,
            'categorie':categories_format,
            'total_categorie':len(Categorie.query.all())
            })
    
#   Mettre à jour une categorie

@app.route('/categories/<int:id>',methods=['PATCH'])
def update_categorie(id):
    body=request.get_json()
    try:
      cat = Categorie.query.filter(Categorie.id==id).one_or_none()
      if cat is None:
            abort(404)
      if 'libelle_categorie' in body:
            cat.libelle_categorie=body.get('libelle_categorie')
            cat.update()
            return jsonify({
                'success':True,
                'id':cat.id,
                'categorie_modifie':cat.format()
            })
      return jsonify({
        "erreur" : "Modifier le champ saisi"
        })
    except:
      abort(400)
    
#  Supprimer une categorie

@app.route('/categories/<int:id>',methods=['DELETE'])
def supprimer_categorie(id):
    try:
        cat = Categorie.query.get(id)
        if cat is None:
            abort(404)
        else:
            cat.delete()
            return jsonify({
                "success":True,
                "id_supprimee":id,
                "total_categorie":len(Categorie.query.all())
            })
    except:
        abort(400)
