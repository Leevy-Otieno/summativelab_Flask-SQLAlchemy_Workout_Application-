from app import app
from models import db, Exercise, Workout, WorkoutExercise
from datetime import date

with app.app_context():
    print("Clearing database...")
    Exercise.query.delete()
    Workout.query.delete()
    WorkoutExercise.query.delete()

    print("Seeding exercises...")
    e1 = Exercise(name="Pushups", category="Calisthenics", equipment_needed=False)
    e2 = Exercise(name="Deadlift", category="Powerlifting", equipment_needed=True)
    
    print("Seeding workouts...")
    w1 = Workout(date=date.today(), duration_minutes=45, notes="Morning session")

    db.session.add_all([e1, e2, w1])
    db.session.commit()

    print("Linking exercise to workout...")
    we1 = WorkoutExercise(workout_id=w1.id, exercise_id=e1.id, reps=20, sets=3)
    db.session.add(we1)
    db.session.commit()
    print("Done!")