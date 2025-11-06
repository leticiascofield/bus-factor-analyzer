import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from typing import List
from busfactor.models import RiskAnalysisResult


class HTMLReportGenerator:
    def __init__(self):
        pass

    def generate_html(self, results: List[RiskAnalysisResult], output_path: str = "report.html"):
        if not results:
            print("⚠️ Nenhum resultado disponível para gerar HTML.")
            return

        # Converter resultados para DataFrame
        data = [{
            "Repositório": r.repository,
            "Arquivo": r.file_path,
            "Autor Dominante (Commits)": r.dominant_author_commits,
            "Autor Dominante (Linhas)": r.dominant_author_lines,
            "Dominância (Commits)": r.commits_dominance * 100,
            "Dominância (Linhas)": r.lines_dominance * 100,
            "Total Commits": r.total_commits,
            "Total Linhas": r.total_lines_changed,
            "Autores": ", ".join(r.all_authors)
        } for r in results]

        df = pd.DataFrame(data)

        # Gráfico 1: Arquivos em risco por autor dominante (commits)
        fig1 = px.bar(
            df,
            x="Autor Dominante (Commits)",
            title="Arquivos de risco por autor dominante (Commits)",
            color="Autor Dominante (Commits)"
        )

        # Gráfico 2: Dispersão commits vs linhas
        fig2 = px.scatter(
            df,
            x="Dominância (Commits)",
            y="Dominância (Linhas)",
            color="Autor Dominante (Commits)",
            title="Dominância por Commits x Linhas"
        )

        # Gráfico 3: Top 5 autores dominantes
        top_authors = df["Autor Dominante (Commits)"].value_counts().nlargest(5)
        fig3 = px.pie(
            names=top_authors.index,
            values=top_authors.values,
            title="Top 5 Autores Dominantes (por número de arquivos)"
        )

        # HTML — Tabelas e gráficos
        html_content = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>Relatório Bus Factor</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body class="bg-light">
            <div class="container mt-4">
                <h1 class="mb-4 text-center">Relatório de Análise de Bus Factor</h1>
                <p>Foram encontrados <b>{len(df)}</b> arquivos de risco.</p>

                <h3>📊 Arquivos de risco por autor</h3>
                {fig1.to_html(full_html=False, include_plotlyjs=False)}

                <h3>⚖️ Dispersão de dominância</h3>
                {fig2.to_html(full_html=False, include_plotlyjs=False)}

                <h3>🏆 Top 5 autores dominantes</h3>
                {fig3.to_html(full_html=False, include_plotlyjs=False)}

                <h3>📁 Tabela de Arquivos de Risco</h3>
                {df.to_html(classes="table table-striped table-bordered", index=False)}
            </div>
        </body>
        </html>
        """

        Path(output_path).write_text(html_content, encoding="utf-8")
        print(f"✅ Relatório HTML gerado com sucesso: {output_path}")
        print(f"📂 Abra o arquivo no navegador: file://{Path(output_path).resolve()}")
