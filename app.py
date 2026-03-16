from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import glob

app = Flask(__name__)

DEGREES_DIR = os.path.join(os.path.dirname(__file__), 'data', 'degrees')

def get_available_degrees():
    degrees = []
    if os.path.exists(DEGREES_DIR):
        for filepath in glob.glob(os.path.join(DEGREES_DIR, "*.json")):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    degrees.append({
                        "id": data.get("id", os.path.basename(filepath).replace(".json", "")),
                        "name": data.get("name", "Unbenannter Studiengang")
                    })
            except:
                pass
    return sorted(degrees, key=lambda x: x["name"])

def load_degree_data(degree_id):
    filepath = os.path.join(DEGREES_DIR, f"{degree_id}.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

@app.route("/")
def index():
    degrees = get_available_degrees()
    # Default to Informatik if available, else first one
    default_id = "informatik_bsc"
    if any(d['id'] == default_id for d in degrees):
        return redirect(url_for('degree_view', degree_id=default_id))
    elif degrees:
        return redirect(url_for('degree_view', degree_id=degrees[0]['id']))
    else:
        return "Keine Studiengänge gefunden."

@app.route("/<degree_id>")
def degree_view(degree_id):
    degree_data = load_degree_data(degree_id)
    if not degree_data:
        # Fallback or error
        degrees = get_available_degrees()
        if degrees:
            return redirect(url_for('degree_view', degree_id=degrees[0]['id']))
        return "Studiengang nicht gefunden.", 404
        
    available_degrees = get_available_degrees()
    
    return render_template("index.html", 
                         default_courses=degree_data.get("default_courses", []),
                         macro_sections=degree_data.get("macro_sections", []),
                         current_degree=degree_data,
                         available_degrees=available_degrees)

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