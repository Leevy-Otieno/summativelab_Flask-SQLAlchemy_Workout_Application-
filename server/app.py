from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate, ValidationError
from models import db, Exercise, Workout, WorkoutExercise

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)

# --- SCHEMAS ---

class WorkoutExerciseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WorkoutExercise
        load_instance = True
        include_fk = True  # Includes workout_id and exercise_id
    
    # Schema Validations (Requirement: >1)
    reps = ma.auto_field(validate=validate.Range(min=1))
    sets = ma.auto_field(validate=validate.Range(min=1))

class ExerciseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Exercise
        load_instance = True
    
    # Schema Validation
    name = ma.auto_field(validate=validate.Length(min=2))
    # Nested relationship for GET /exercises/<id>
    workout_exercises = fields.Nested(WorkoutExerciseSchema, many=True, dump_only=True)

class WorkoutSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Workout
        load_instance = True
    
    # Schema Validation
    duration_minutes = ma.auto_field(validate=validate.Range(min=1))
    # Nested relationship for GET /workouts/<id> (Stretch Goal)
    workout_exercises = fields.Nested(WorkoutExerciseSchema, many=True, dump_only=True)

# Initialize schemas
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()

# --- ROUTES ---

# WORKOUT ROUTES
@app.route('/workouts', methods=['GET', 'POST'])
def workouts():
    if request.method == 'GET':
        return make_response(workouts_schema.jsonify(Workout.query.all()), 200)
    
    if request.method == 'POST':
        try:
            # load_instance=True automatically creates the Workout object
            new_workout = workout_schema.load(request.get_json(), session=db.session)
            db.session.add(new_workout)
            db.session.commit()
            return make_response(workout_schema.jsonify(new_workout), 201)
        except ValidationError as e:
            return make_response({"errors": e.messages}, 400)

@app.route('/workouts/<int:id>', methods=['GET', 'DELETE'])
def workout_by_id(id):
    workout = Workout.query.get_or_404(id)
    if request.method == 'GET':
        return make_response(workout_schema.jsonify(workout), 200)
    
    if request.method == 'DELETE':
        db.session.delete(workout)
        db.session.commit()
        return make_response({}, 204)

# EXERCISE ROUTES
@app.route('/exercises', methods=['GET', 'POST'])
def exercises():
    if request.method == 'GET':
        return make_response(exercises_schema.jsonify(Exercise.query.all()), 200)
    
    if request.method == 'POST':
        try:
            new_ex = exercise_schema.load(request.get_json(), session=db.session)
            db.session.add(new_ex)
            db.session.commit()
            return make_response(exercise_schema.jsonify(new_ex), 201)
        except ValidationError as e:
            return make_response({"errors": e.messages}, 400)

@app.route('/exercises/<int:id>', methods=['GET', 'DELETE'])
def exercise_by_id(id):
    exercise = Exercise.query.get_or_404(id)
    if request.method == 'GET':
        return make_response(exercise_schema.jsonify(exercise), 200)
    
    if request.method == 'DELETE':
        db.session.delete(exercise)
        db.session.commit()
        return make_response({}, 204)

# JOIN TABLE ROUTE
@app.route('/workouts/<int:wid>/exercises/<int:eid>/workout_exercises', methods=['POST'])
def add_exercise_to_workout(wid, eid):
    # Verify parents exist first
    Workout.query.get_or_404(wid)
    Exercise.query.get_or_404(eid)
    
    try:
        data = request.get_json()
        # Manually inject the IDs from the URL into the data for the schema to load
        data['workout_id'] = wid
        data['exercise_id'] = eid
        
        new_we = workout_exercise_schema.load(data, session=db.session)
        db.session.add(new_we)
        db.session.commit()
        return make_response(workout_exercise_schema.jsonify(new_we), 201)
    except ValidationError as e:
        return make_response({"errors": e.messages}, 400)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
