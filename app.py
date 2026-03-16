from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Standard courses for Grundstudium as fallback based on RPTU study plan
DEFAULT_COURSES = [
    # ---- PFLICHTBEREICH (120 LP) ----
    
    # Software-Entwicklung (44 LP)
    {"name": "Konzepte der Programmierung", "ects": 10, "type": "Software-Entwicklung", "grade": "", "status": "ausstehend", "graded": True},
    {"name": "Modellierung von Software-Systemen", "ects": 4, "type": "Software-Entwicklung", "grade": "", "status": "ausstehend", "graded": True},
    {"name": "Verteilte und nebenläufige Systeme", "ects": 4, "type": "Software-Entwicklung", "grade": "", "status": "ausstehend", "graded": True},
    {"name": "Algorithmen und Datenstrukturen", "ects": 8, "type": "Software-Entwicklung", "grade": "", "status": "ausstehend", "graded": True},
    {"name": "Projektmanagement", "ects": 6, "type": "Software-Entwicklung", "grade": "", "status": "ausstehend", "graded": False},
    {"name": "Software-Entwicklungsprojekt", "ects": 8, "type": "Software-Entwicklung", "grade": "", "status": "ausstehend", "graded": True},
    {"name": "Programmierpraktikum", "ects": 4, "type": "Software-Entwicklung", "grade": "", "status": "ausstehend", "graded": False},
    
    # Informatiksysteme (36 LP)
    {"name": "Digitaltechnik und Rechnerarchitektur", "ects": 8, "type": "Informatiksysteme", "grade": "", "status": "ausstehend", "graded": True},
    {"name": "Rechnerorganisation und Systemsoftware", "ects": 8, "type": "Informatiksysteme", "grade": "", "status": "ausstehend", "graded": True},
    {"name": "Informationssysteme", "ects": 8, "type": "Informatiksysteme", "grade": "", "status": "ausstehend", "graded": True},
    {"name": "Kommunikationssysteme", "ects": 4, "type": "Informatiksysteme", "grade": "", "status": "ausstehend", "graded": True},
    {"name": "Scientific Computing", "ects": 4, "type": "Informatiksysteme", "grade": "", "status": "ausstehend", "graded": True},
    {"name": "Künstliche Intelligenz", "ects": 4, "type": "Informatiksysteme", "grade": "", "status": "ausstehend", "graded": True},

    # Theoretische Grundlagen (33 LP)
    {"name": "Mathematik für Informatiker: Algebraische Strukturen", "ects": 8, "type": "Theoretische Grundlagen", "grade": "", "status": "ausstehend", "graded": True},
    {"name": "Mathematik für Informatiker: Kombinatorik, Stochastik und Statistik", "ects": 8, "type": "Theoretische Grundlagen", "grade": "", "status": "ausstehend", "graded": True},
    {"name": "Mathematik für Informatiker: Analysis", "ects": 5, "type": "Theoretische Grundlagen", "grade": "", "status": "ausstehend", "graded": True},
    {"name": "Formale Sprachen und Berechenbarkeit", "ects": 6, "type": "Theoretische Grundlagen", "grade": "", "status": "ausstehend", "graded": True},
    {"name": "Logik und Semantik von Programmiersprachen", "ects": 6, "type": "Theoretische Grundlagen", "grade": "", "status": "ausstehend", "graded": True},

    # Überfachliche Qualifikation (7 LP)
    {"name": "Informatik und Gesellschaft", "ects": 3, "type": "Überfachliche Qualifikation", "grade": "", "status": "ausstehend", "graded": False},
    {"name": "Bachelor-Seminar", "ects": 4, "type": "Überfachliche Qualifikation", "grade": "", "status": "ausstehend", "graded": True},
    
    # ---- WAHBEREICH / REST ----
    {"name": "Vertiefungsvorlesung", "ects": 8, "type": "Vertiefung: Algorithmik und Deduktion", "grade": "", "status": "ausstehend", "graded": True},
    {"name": "Vertiefungsprojekt", "ects": 8, "type": "Vertiefung: Algorithmik und Deduktion", "grade": "", "status": "ausstehend", "graded": False},
    
    {"name": "Wahlbereich (Ergänzung)", "ects": 10, "type": "Ergänzung", "grade": "", "status": "ausstehend", "graded": True},
    {"name": "Bachelorarbeit", "ects": 12, "type": "Abschlussarbeit", "grade": "", "status": "ausstehend", "graded": True}
]

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/store")
def store():
    return render_template("store.html")

@app.route("/app/notenrechner")
def notenrechner():
    return render_template("notenrechner.html", default_courses=DEFAULT_COURSES)

@app.route("/app/pomodoro")
def pomodoro():
    return render_template("pomodoro.html")

@app.route("/app/linkhub")
def linkhub():
    return render_template("linkhub.html")

@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.json
    courses = data.get("courses", [])
    
    total_ects_graded = 0
    total_grade_points = 0.0
    total_ects_passed = 0
    
    results_by_type = {}
    
    for course in courses:
        ctype = course.get("type", "Sonstiges")
        status = course.get("status", "ausstehend")
        ects = float(course.get("ects", 0) or 0)
        grade_str = course.get("grade", "")
        # Standardmäßig ist alles benotet, es sei denn es ist explizit als False markiert
        is_graded = course.get("graded", True)
        
        if ctype not in results_by_type:
            results_by_type[ctype] = {"ects_graded": 0, "grade_points": 0, "ects_passed": 0}
        
        if status == "bestanden":
            total_ects_passed += ects
            results_by_type[ctype]["ects_passed"] += ects
            
            if grade_str and is_graded:
                try:
                    grade = float(grade_str)
                    total_ects_graded += ects
                    total_grade_points += (grade * ects)
                    
                    results_by_type[ctype]["ects_graded"] += ects
                    results_by_type[ctype]["grade_points"] += (grade * ects)
                except ValueError:
                    pass
                    
    # Overall GPA
    overall_gpa = round(total_grade_points / total_ects_graded, 2) if total_ects_graded > 0 else 0.0
    
    # GPA by type
    gpas = {}
    for ctype, vals in results_by_type.items():
        if vals["ects_graded"] > 0:
            gpas[ctype] = round(vals["grade_points"] / vals["ects_graded"], 2)
        else:
            gpas[ctype] = 0.0
            
    return jsonify({
        "overall_gpa": overall_gpa,
        "total_ects_passed": total_ects_passed,
        "total_ects_graded": total_ects_graded,
        "gpas_by_type": gpas,
        "details": results_by_type
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5500)