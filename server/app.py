from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from models import db, Exercise, Workout, WorkoutExercise

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)
ma = Marshmallow(app)

# --- SCHEMAS (Validation & Serialization) ---

class ExerciseSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Exercise
    
    id = ma.auto_field()
    # Schema Validation 1: Length check
    name = ma.auto_field(validate=validate.Length(min=3))
    category = ma.auto_field()
    equipment_needed = ma.auto_field()

class WorkoutSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Workout
    
    id = ma.auto_field()
    date = ma.auto_field()
    # Schema Validation 2: Range check
    duration_minutes = ma.auto_field(validate=validate.Range(min=1))
    notes = ma.auto_field()

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

# --- ROUTES ---

@app.route('/workouts', methods=['GET', 'POST'])
def workouts():
    if request.method == 'GET':
        w = Workout.query.all()
        return make_response(workouts_schema.jsonify(w), 200)
    
    if request.method == 'POST':
        data = request.get_json()
        try:
            new_workout = Workout(
                date=date.fromisoformat(data['date']),
                duration_minutes=data.get('duration_minutes'),
                notes=data.get('notes')
            )
            db.session.add(new_workout)
            db.session.commit()
            return make_response(workout_schema.jsonify(new_workout), 201)
        except Exception as e:
            return make_response({"errors": [str(e)]}, 400)

@app.route('/workouts/<int:id>', methods=['GET', 'DELETE'])
def workout_by_id(id):
    workout = Workout.query.get_or_404(id)
    if request.method == 'GET':
        return make_response(workout_schema.jsonify(workout), 200)
    
    if request.method == 'DELETE':
        db.session.delete(workout)
        db.session.commit()
        return make_response({}, 204)

@app.route('/exercises', methods=['GET', 'POST'])
def exercises():
    if request.method == 'GET':
        exs = Exercise.query.all()
        return make_response(exercises_schema.jsonify(exs), 200)
    
    if request.method == 'POST':
        data = request.get_json()
        try:
            new_ex = Exercise(
                name=data['name'],
                category=data['category'],
                equipment_needed=data.get('equipment_needed', False)
            )
            db.session.add(new_ex)
            db.session.commit()
            return make_response(exercise_schema.jsonify(new_ex), 201)
        except Exception as e:
            return make_response({"errors": [str(e)]}, 400)

@app.route('/workouts/<int:wid>/exercises/<int:eid>/workout_exercises', methods=['POST'])
def add_exercise_to_workout(wid, eid):
    data = request.get_json()
    new_we = WorkoutExercise(
        workout_id=wid,
        exercise_id=eid,
        reps=data.get('reps'),
        sets=data.get('sets'),
        duration_seconds=data.get('duration_seconds')
    )
    db.session.add(new_we)
    db.session.commit()
    return make_response({"message": "Exercise added to workout"}, 201)

if __name__ == '__main__':
    app.run(port=5555, debug=True)