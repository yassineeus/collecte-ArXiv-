 import json
import os
from datetime import datetime
from jinja2 import Template

class TableGenerator:
    def __init__(self):
        self.data_file = "data/papers_database.json"
        self.output_file = "docs/index.html"
        
    def load_papers(self):
        """Charge les articles de la base de données"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def format_date(self, date_str):
        """Formate la date pour l'affichage"""
        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date.strftime('%Y-%m-%d')
        except:
            return date_str
    
    def truncate_text(self, text, max_length=200):
        """Tronque le texte si trop long"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def generate_html(self):
        """Génère le fichier HTML avec le tableau"""
        papers = self.load_papers()
        
        html_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Articles - Géométrie Symplectique & Poisson</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.datatables.net/1.11.5/css/dataTables.bootstrap5.min.css" rel="stylesheet">
    <style>
        .abstract-cell { max-width: 300px; }
        .author-cell { max-width: 200px; }
        .badge-keyword { font-size: 0.8em; }
        h1 { margin-bottom: 30px; color: #2c3e50; }
        .last-update { color: #6c757d; font-style: italic; }
    </style>
</head>
<body>
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="text-center">📐 Articles Récents - Géométrie Symplectique & Poisson</h1>
                <p class="text-center last-update">
                    Dernière mise à jour: {{ update_time }} | 
                    Total: {{ total_papers }} articles
                </p>
                
                <div class="table-responsive">
                    <table id="papersTable" class="table table-striped table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>Date</th>
                                <th>Titre</th>
                                <th>Auteurs</th>
                                <th>Résumé</th>
                                <th>Catégories</th>
                                <th>Mot-clé</th>
                                <th>Liens</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for paper in papers %}
                            <tr>
                                <td>{{ format_date(paper.published) }}</td>
                                <td>
                                    <strong>{{ paper.title }}</strong>
                                    <br><small class="text-muted">ID: {{ paper.arxiv_id }}</small>
                                </td>
                                <td class="author-cell">
                                    {% for author in paper.authors[:3] %}
                                        {{ author }}{% if not loop.last %}, {% endif %}
                                    {% endfor %}
                                    {% if paper.authors|length > 3 %}
                                        <br><small class="text-muted">+{{ paper.authors|length - 3 }} autres</small>
                                    {% endif %}
                                </td>
                                <td class="abstract-cell">
                                    <small>{{ truncate_text(paper.abstract) }}</small>
                                </td>
                                <td>
                                    {% for cat in paper.categories %}
                                        <span class="badge bg-secondary me-1">{{ cat }}</span>
                                    {% endfor %}
                                </td>
                                <td>
                                    <span class="badge bg-primary badge-keyword">{{ paper.keyword_found }}</span>
                                </td>
                                <td>
                                    <a href="{{ paper.url }}" target="_blank" class="btn btn-sm btn-outline-primary me-1">ArXiv</a>
                                    <a href="{{ paper.pdf_url }}" target="_blank" class="btn btn-sm btn-outline-danger">PDF</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                
                <div class="mt-4 text-center">
                    <p class="text-muted">
                        <small>
                            Collecte automatique via ArXiv API - 
                            <a href="https://github.com/votre-username/symplectic-poisson-papers">Code source</a>
                        </small>
                    </p>
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.11.5/js/dataTables.bootstrap5.min.js"></script>
    
    <script>
        $(document).ready(function() {
            $('#papersTable').DataTable({
                "order": [[ 0, "desc" ]], // Trier par date décroissante
                "pageLength": 25,
                "language": {
                    "url": "//cdn.datatables.net/plug-ins/1.11.5/i18n/fr-FR.json"
                },
                "columnDefs": [
                    { "width": "10%", "targets": 0 }, // Date
                    { "width": "25%", "targets": 1 }, // Titre
                    { "width": "15%", "targets": 2 }, // Auteurs
                    { "width": "30%", "targets": 3 }, // Résumé
                    { "width": "10%", "targets": 4 }, // Catégories
                    { "width": "10%", "targets": 5 }  // Liens
                ]
            });
        });
    </script>
</body>
</html>
        """
        
        template = Template(html_template)
        
        html_content = template.render(
            papers=papers,
            total_papers=len(papers),
            update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            format_date=self.format_date,
            truncate_text=self.truncate_text
        )
        
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Tableau HTML généré: {self.output_file}")

if __name__ == "__main__":
    generator = TableGenerator()
    generator.generate_html()
