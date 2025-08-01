from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from typing import Optional, Dict, List

app = FastAPI()

class UserInput(BaseModel):
    message: str
    formData: Optional[dict] = None

class ApplicationForm(BaseModel):
    form: Dict

# Función para buscar repositorios en GitHub
def search_github_repos(query: str) -> List[Dict]:
    url = f"https://api.github.com/search/repositories?q={query}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("items", [])
    except requests.RequestException:
        return []

# Generar recomendaciones según gustos
def generate_recommendations(likes: str, dislikes: str) -> tuple:
    likes = likes.lower()
    dislikes = dislikes.lower()
    recommendations = []
    study_plan = []
    quote_items = []

    if "matemáticas" in dislikes or "matematicas" in dislikes:
        recommendations = ["Derecho", "Filosofía", "Medicina", "Literatura", "Artes"]
        study_plan = [
            "Semana 1: Explora introducciones a las carreras recomendadas (e.g., Derecho).",
            "Semana 2: Realiza un curso introductorio online (e.g., 'Fundamentos de Filosofía').",
            "Semana 3: Busca proyectos en GitHub relacionados con humanidades."
        ]
        quote_items = [
            {"name": "Curso de Introducción al Derecho en Coursera", "cost": 30},
            {"name": "Libro: 'El contrato social' de Rousseau", "cost": 15}
        ]
    elif "matemáticas" in likes or "matematicas" in likes:
        recommendations = ["Ingeniería (Civil, Informática)", "Estadística", "Física", "Matemáticas Puras"]
        study_plan = [
            "Semana 1: Aprende conceptos básicos de álgebra o programación (Python).",
            "Semana 2: Realiza un curso de introducción a la ingeniería en edX.",
            "Semana 3: Clona un repositorio de GitHub para practicar matemáticas computacionales."
        ]
        quote_items = [
            {"name": "Curso de Python para Matemáticas en Udemy", "cost": 20},
            {"name": "Libro: 'Linear Algebra Done Right'", "cost": 40}
        ]
    else:
        # Para indecisos o gustos no específicos
        recommendations = ["Curso introductorio: 'Exploración de Carreras Universitarias'"]
        study_plan = [
            "Semana 1: Realiza un test vocacional online.",
            "Semana 2: Explora introducciones a diversas áreas (e.g., Coursera).",
            "Semana 3: Participa en foros de GitHub sobre orientación profesional."
        ]
        quote_items = [
            {"name": "Curso de Orientación Vocacional en Udemy", "cost": 25},
            {"name": "Suscripción a plataforma de cursos (1 mes)", "cost": 10}
        ]

    # Buscar recursos en GitHub
    query = recommendations[0].lower().replace(" ", "+") + "+tutorial"
    repos = search_github_repos(query)
    repo_text = "\nRecursos en GitHub:\n" if repos else "\nNo se encontraron recursos en GitHub.\n"
    for repo in repos[:3]:
        repo_text += f"- {repo['name']}: {repo['html_url']}\n"

    total_cost = sum(item["cost"] for item in quote_items)
    return recommendations, study_plan, quote_items, total_cost, repo_text

# Generar formulario de postulación
def generate_application_form(name: str, recommendation: str) -> Dict:
    return {
        "fields": [
            {"label": "Nombre completo", "value": name, "placeholder": "Tu nombre"},
            {"label": "Correo electrónico", "value": "", "placeholder": "tu@correo.com"},
            {"label": "Programa de interés", "value": recommendation, "placeholder": "e.g., Derecho"},
            {"label": "Motivación", "value": "", "placeholder": "Por qué quieres estudiar esto"}
        ]
    }

@app.post("/assistant")
async def assistant(user_input: UserInput):
    message = user_input.message.lower()
    form_data = user_input.formData or {}
    likes = form_data.get("likes", "")
    dislikes = form_data.get("dislikes", "")
    name = form_data.get("name", "Usuario")

    response = ""
    study_plan = None
    quote = None
    application_form = None

    if "gusta" in message or "interesa" in message or "estudiar" in message or likes or dislikes:
        recommendations, plan_tasks, quote_items, total_cost, repo_text = generate_recommendations(likes, dislikes)
        response = f"¡Entendido, {name}! Según tus gustos ({likes or 'no especificado'}) y lo que no te gusta ({dislikes or 'no especificado'}), te recomiendo: {', '.join(recommendations)}. {repo_text}"
        study_plan = {"tasks": plan_tasks}
        quote = {"items": quote_items, "total": total_cost}
        application_form = generate_application_form(name, recommendations[0])
    elif "no sé" in message or "indeciso" in message or "duda" in message:
        response = f"¡No te preocupes, {name}! Te recomiendo un curso introductorio para explorar opciones. Aquí tienes un plan y recursos:\n"
        recommendations, plan_tasks, quote_items, total_cost, repo_text = generate_recommendations("", "")
        response += repo_text
        study_plan = {"tasks": plan_tasks}
        quote = {"items": quote_items, "total": total_cost}
        application_form = generate_application_form(name, recommendations[0])
    elif "postulación" in message or "formulario" in message:
        response = f"Te ayudaré con la postulación, {name}. Completa el formulario que aparece en la pantalla."
        application_form = generate_application_form(name, form_data.get("goal", "Programa no especificado"))
    else:
        response = "Cuéntame más sobre lo que te gusta o no te gusta estudiar, o si estás indeciso. También puedo ayudarte con una postulación."

    return {"response": response, "studyPlan": study_plan, "quote": quote, "applicationForm": application_form}

@app.post("/form")
async def process_form(form_data: dict):
    name = form_data.get("name", "Usuario")
    likes = form_data.get("likes", "no especificado")
    recommendation = generate_recommendations(likes, form_data.get("dislikes", ""))[0][0]
    response = f"Datos recibidos, {name}. Según tus gustos ({likes}), te recomiendo {recommendation}. Completa el formulario de postulación."
    application_form = generate_application_form(name, recommendation)
    return {"response": response, "applicationForm": application_form}

@app.post("/submit_application")
async def submit_application(application: ApplicationForm):
    form = application.form
    name = next((field["value"] for field in form["fields"] if field["label"] == "Nombre completo"), "Usuario")
    program = next((field["value"] for field in form["fields"] if field["label"] == "Programa de interés"), "no especificado")
    response = f"¡Postulación enviada, {name}! Tu solicitud para {program} ha sido procesada. Te contactaremos pronto."
    return {"response": response}