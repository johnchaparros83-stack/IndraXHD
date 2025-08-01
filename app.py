from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Función para buscar repositorios en GitHub
def search_github_repos(query):
    url = f"https://api.github.com/search/repositories?q={query}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("items", [])
    except requests.RequestException as e:
        return [{"error": str(e)}]

# Ruta principal para la interacción del asistente
@app.route("/assistant", methods=["POST"])
def assistant():
    data = request.get_json()
    user_input = data.get("message", "").lower()
    response = ""

    # Lógica del asistente
    if "aprender a programar" in user_input or "estudiar programación" in user_input:
        response = "¡Genial que quieras aprender a programar! Te recomiendo empezar con lenguajes como Python o JavaScript. En GitHub, puedes encontrar recursos como tutoriales y proyectos prácticos. ¿Te interesa un lenguaje en particular?"
        repos = search_github_repos("learn python tutorial")
        if repos and "error" not in repos[0]:
            response += "\nAquí tienes algunos repositorios en GitHub para aprender Python:\n"
            for repo in repos[:3]:
                response += f"- {repo['name']}: {repo['html_url']}\n"
    elif "python" in user_input:
        response = "Python es un excelente lenguaje para principiantes. En GitHub hay muchos recursos. ¿Quieres proyectos prácticos, tutoriales o cursos interactivos?"
        repos = search_github_repos("python tutorial")
        if repos and "error" not in repos[0]:
            response += "\nMira estos repositorios:\n"
            for repo in repos[:3]:
                response += f"- {repo['name']}: {repo['html_url']}\n"
    elif "github" in user_input:
        response = "GitHub es una plataforma increíble para aprender. Puedes explorar repositorios, clonar proyectos y colaborar. ¿Quieres consejos sobre cómo usar GitHub o buscar recursos específicos?"
    else:
        response = "No estoy seguro de lo que buscas. ¿Quieres aprender un lenguaje de programación, usar GitHub o algo más específico? ¡Cuéntame más!"

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)