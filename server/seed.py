#!/usr/bin/env python3

from app import app
from models import db, Exercise, Workout, WorkoutExercise
from datetime import date

with app.app_context():
    print("Clearing database...")
    # Delete child records first to avoid Foreign Key constraint errors
    WorkoutExercise.query.delete()
    Exercise.query.delete()
    Workout.query.delete()

    print("Seeding exercises...")
    # Using categories defined in our model validation ('Strength', 'Cardio', etc.)
    e1 = Exercise(name="Pushups", category="Strength", equipment_needed=False)
    e2 = Exercise(name="Running", category="Cardio", equipment_needed=False)
    e3 = Exercise(name="Deadlift", category="Strength", equipment_needed=True)
    
    print("Seeding workouts...")
    # Note must be at least 5 characters (our model validation)
    w1 = Workout(date=date.today(), duration_minutes=45, notes="Morning strength session")
    w2 = Workout(date=date.today(), duration_minutes=30, notes="Evening cardio burn")

    db.session.add_all([e1, e2, e3, w1, w2])
    db.session.commit() # Commit parents first so they get IDs

    print("Linking exercises to workouts...")
    we1 = WorkoutExercise(workout_id=w1.id, exercise_id=e1.id, reps=20, sets=3)
    we2 = WorkoutExercise(workout_id=w1.id, exercise_id=e3.id, reps=5, sets=5)
    we3 = WorkoutExercise(workout_id=w2.id, exercise_id=e2.id, duration_seconds=1800)
    
    db.session.add_all([we1, we2, we3])
    db.session.commit()
    
    print("Database successfully seeded!")
