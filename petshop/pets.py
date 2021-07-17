import datetime

from flask import Blueprint
from flask import render_template, request, redirect, url_for, jsonify
from flask import g

from . import db

bp = Blueprint("pets", "pets", url_prefix="")

def format_date(d):
    if d:
        d = datetime.datetime.strptime(d, '%Y-%m-%d')
        v = d.strftime("%a - %b %d, %Y")
        return v
    else:
        return None

@bp.route("/search/<field>/<value>")
def search(field, value):
    conn=db.get_db()
    cursor=conn.cursor()
    cursor.execute("select id from tag where name= ? ",value)
    tagids=cursor.fetchall()
    # for tagid in tagids:
        # cursor.execute(f"select p.id, p.name, p.bought, p.sold, p.species from pet p, tags_pets a where a.id={tagid}")
    # pets=cursor.fetchall()

    # return render_template('index.html', pets = pets)
    return tagids
@bp.route("/")
def dashboard():
    conn = db.get_db()
    cursor = conn.cursor()
    oby = request.args.get("order_by", "id") # TODO. This is currently not used.
    order = request.args.get("order", "asc")
    if oby == "id":
        if order == "asc":
            cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by p.id")
        else:
            cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by p.id desc")
    elif oby == "name":
        if order == "asc":
            cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by p.name")
        else:
            cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by p.name desc")
    elif oby == "bought":
        if order == "asc":
            cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by p.bought")
        else:
            cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by p.bought desc")
    elif oby == "sold":
        if order == "asc":
            cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by p.sold")
        else:
            cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by p.sold desc")
    elif oby == "species":
        if order == "asc":
            cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by p.species")
        else:
            cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by p.species desc")


    pets = cursor.fetchall()
    return render_template('index.html', pets = pets, order="desc" if order=="asc" else "asc")


@bp.route("/<pid>")
def pet_info(pid):
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("select p.name, p.bought, p.sold, p.description, s.name from pet p, animal s where p.species = s.id and p.id = ?", [pid])
    pet = cursor.fetchone()
    cursor.execute("select t.name from tags_pets tp, tag t where tp.pet = ? and tp.tag = t.id", [pid])
    tags = (x[0] for x in cursor.fetchall())
    name, bought, sold, description, species = pet
    data = dict(id = pid,
                name = name,
                bought = format_date(bought),
                sold = format_date(sold),
                description = description, #TODO Not being displayed
                species = species,
                tags = tags)
    return render_template("petdetail.html", **data)

@bp.route("/<pid>/edit", methods=["GET", "POST"])
def edit(pid):
    conn = db.get_db()
    cursor = conn.cursor()
    if request.method == "GET":
        cursor.execute("select p.name, p.bought, p.sold, p.description, s.name from pet p, animal s where p.species = s.id and p.id = ?", [pid])
        pet = cursor.fetchone()
        cursor.execute("select t.name from tags_pets tp, tag t where tp.pet = ? and tp.tag = t.id", [pid])
        tags = (x[0] for x in cursor.fetchall())
        name, bought, sold, description, species = pet
        data = dict(id = pid,
                    name = name,
                    bought = format_date(bought),
                    sold = format_date(sold),
                    description = description,
                    species = species,
                    tags = tags)
        return render_template("editpet.html", **data)
    elif request.method == "POST":
        description = request.form.get('description')
        sold = request.form.get("sold")
        # TODO Handle sold
        data1=dict(des=description,id=pid)
        cursor.execute("""UPDATE pet SET description= ? WHERE id =?""",[description,pid])
        conn.commit()
        if sold==1:
            sold=format_date(date.today())
            cursor.execute("""UPDATE pet SET sold= ? WHERE id = ?""",[sold,pid])
            conn.commit()
        return redirect(url_for("pets.pet_info", pid=pid), 302)
