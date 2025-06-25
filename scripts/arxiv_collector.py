import arxiv
import json
import os
from datetime import datetime, timedelta
import time

class ArxivCollector:
    def __init__(self):
        self.client = arxiv.Client()
        self.data_file = "data/papers_database.json"
        self.keywords = [
            "symplectic geometry",
            "Poisson geometry", 
            "Poisson manifold",
            "Hamiltonian mechanics",
            "moment map",
            "Lie-Poisson",
            "symplectic reduction",
            "Poisson bracket",
            "symplectic manifold",
            "Poisson-Lie group",
            "symplectic form",
            "Poisson cohomology"
        ]
        
    def load_existing_papers(self):
        """Charge la base de données existante"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_papers(self, papers):
        """Sauvegarde la base de données"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
    
    def search_papers(self, days_back=7):
        """Recherche les nouveaux articles"""
        papers = self.load_existing_papers()
        existing_ids = {paper['arxiv_id'] for paper in papers}
        
        # Date limite pour la recherche
        date_limit = datetime.now() - timedelta(days=days_back)
        
        new_papers = []
        
        for keyword in self.keywords:
            print(f"Recherche pour: {keyword}")
            
            # Construction de la requête
            query = f'cat:math.SG OR cat:math.DG OR cat:math-ph.MP AND ({keyword})'
            
            try:
                search = arxiv.Search(
                    query=query,
                    max_results=50,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending
                )
                
                for paper in self.client.results(search):
                    # Vérifier si l'article est récent
                    if paper.published < date_limit:
                        continue
                        
                    # Éviter les doublons
                    arxiv_id = paper.entry_id.split('/')[-1]
                    if arxiv_id in existing_ids:
                        continue
                    
                    paper_data = {
                        'arxiv_id': arxiv_id,
                        'title': paper.title,
                        'authors': [str(author) for author in paper.authors],
                        'abstract': paper.summary,
                        'published': paper.published.isoformat(),
                        'updated': paper.updated.isoformat(),
                        'categories': paper.categories,
                        'url': paper.entry_id,
                        'pdf_url': paper.pdf_url,
                        'keyword_found': keyword,
                        'collected_date': datetime.now().isoformat()
                    }
                    
                    new_papers.append(paper_data)
                    existing_ids.add(arxiv_id)
                    print(f"  Nouvel article: {paper.title[:50]}...")
                
                # Pause pour éviter de surcharger l'API
                time.sleep(1)
                
            except Exception as e:
                print(f"Erreur lors de la recherche '{keyword}': {e}")
        
        # Ajouter les nouveaux articles
        papers.extend(new_papers)
        
        # Trier par date de publication (plus récent en premier)
        papers.sort(key=lambda x: x['published'], reverse=True)
        
        self.save_papers(papers)
        print(f"Total: {len(new_papers)} nouveaux articles collectés")
        
        return new_papers

if __name__ == "__main__":
    collector = ArxivCollector()
    collector.search_papers(days_back=30)  # Recherche sur 30 jours
