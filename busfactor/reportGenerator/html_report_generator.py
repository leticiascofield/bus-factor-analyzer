import pandas as pd
import plotly.express as px
from pathlib import Path
from typing import List
from busfactor.models import RiskAnalysisResult


class HTMLReportGenerator:
    def __init__(self):
        pass

    def generate_html(self, results: List[RiskAnalysisResult], output_path: str = "report.html"):
        if not results:
            print("Nenhum resultado disponível para gerar HTML.")
            return

        data = [{
            "Repositório": r.repository,
            "Arquivo": r.file_path,
            "Autor Dominante (Commits)": r.dominant_author_commits,
            "Autor Dominante (Linhas)": r.dominant_author_lines,
            "Dominância (Commits)": round(r.commits_dominance * 100, 2),
            "Dominância (Linhas)": round(r.lines_dominance * 100, 2),
            "Total Commits": r.total_commits,
            "Total Linhas": r.total_lines_changed,
            "Autores": ", ".join(r.all_authors)
        } for r in results]

        df = pd.DataFrame(data)

        fig1_data = df["Autor Dominante (Commits)"].value_counts().reset_index()
        fig1_data.columns = ["Autor", "Arquivos em Risco"]

        fig1 = px.bar(
            fig1_data,
            x="Autor",
            y="Arquivos em Risco",
            title="Arquivos em risco por autor dominante (Commits)",
            color="Autor",
            text="Arquivos em Risco"
        )
        fig1.update_traces(textposition="outside")
        fig1.update_layout(width=1100, height=600, font=dict(size=13))

        dominance_avg = (
            df.groupby("Autor Dominante (Commits)")[["Dominância (Commits)", "Dominância (Linhas)"]]
            .mean()
            .reset_index()
            .rename(columns={"Autor Dominante (Commits)": "Autor"})
        )

        fig2 = px.bar(
            dominance_avg.melt(id_vars="Autor", var_name="Tipo", value_name="Média (%)"),
            x="Autor",
            y="Média (%)",
            color="Tipo",
            barmode="group",
            title="Média de Dominância por Autor"
        )
        fig2.update_layout(width=1100, height=600, font=dict(size=13))

        top_authors = fig1_data.head(5)
        fig3 = px.pie(
            top_authors,
            names="Autor",
            values="Arquivos em Risco",
            title="Top 5 Autores Dominantes (por número de arquivos)"
        )
        fig3.update_layout(width=1100, height=600, font=dict(size=13))

    
        fig4 = px.histogram(
            df[df["Total Commits"] > 1],
            x="Dominância (Commits)",
            nbins=20,  
            range_x=[0, 105],  
            title="Distribuição de Dominância (Commits) — arquivos com >1 commit",
            color_discrete_sequence=["#073769"]
        )
        fig4.update_layout(
            width=1100,  
            height=500,  
            font=dict(size=12),
            xaxis_title="Dominância (Commits)",
            yaxis_title="Quantidade de Arquivos"
        )



        html_content = f"""
        <html>
         <head>
            <meta charset="utf-8">
            <title>Relatório Bus Factor</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
            <style>
                body {{ font-size: 14px; }}
                h3 {{ margins-top: 40px; font-size: 20px; }}
                .small-table {{
                    font-size: 12px;
                    width: 95%;
                    margin: auto;
                }}
                .small-table th, .small-table td {{
                    padding: 6px 8px;
                    text-align: left;
                }}
                .container {{
                    max-width: 1200px;
                }}
            </style>
        </head>
        <body class="bg-light">
            <div class="container mt-4">
                <h1 class="mb-4 text-center">Relatório de Análise de Bus Factor</h1>
                <p>Foram encontrados <b>{len(df)}</b> arquivos de risco.</p>

                <h3>Arquivos em risco por autor</h3>
                <p>Este gráfico mostra quantos arquivos estão sob o domínio de cada autor,
                considerando o autor dominante baseado no número de commits.</p>
                {fig1.to_html(full_html=False, include_plotlyjs='cdn')}
                <p></p>

                <h3>Dispersão de dominância</h3>
                <p>Este gráfico mostra o quanto cada autor domina, em média, 
                os arquivos em que ele aparece como o autor dominante, 
                sob duas perspectivas diferentes:</p>
                <p>• <b>Dominância por Commits:</b> Percentual de commits feitos por esse autor em relação ao total de commits dos outros autores nos arquivos em que ele é dominante.</p>
                <p>• <b>Dominância por Linhas:</b> Percentual de linhas modificadas (adições/remoções) por esse autor em seus arquivos.</p>
                {fig2.to_html(full_html=False, include_plotlyjs=False)}
                <p></p>

                <h3>Distribuição de dominância (Commits)</h3>
                <p>Este histograma mostra como a dominância por commits está distribuída entre os arquivos 
                que possuem mais de um commit.</p>
                <p>Cada barra representa quantos arquivos têm um determinado nível de dominância — ou seja, 
                a porcentagem de commits feitos pelo autor principal.</p>
                <p>Valores próximos de 100% indicam arquivos praticamente controlados por um único autor, 
                enquanto valores intermediários (40–60%) sugerem colaboração maior entre desenvolvedores.</p>
                <p>Uma concentração alta em 100% pode indicar alto risco de bus factor, pois poucos autores 
                detêm conhecimento sobre muitos arquivos.</p>
                {fig4.to_html(full_html=False, include_plotlyjs=False)}
                <p></p>

                <h3>Top 5 autores dominantes</h3>
                <p>Este gráfico mostra os 5 autores que dominam o maior número de arquivos em risco.</p>
                {fig3.to_html(full_html=False, include_plotlyjs=False)}
                <p></p>

                <h3>Tabela de Arquivos de Risco</h3>
                <p>A tabela abaixo lista todos os arquivos identificados como de risco,
                juntamente com suas métricas associadas.</p>
                {df.to_html(classes="table table-striped table-bordered small-table", index=False)}
            </div>
        </body>
        </html>
        """

        Path(output_path).write_text(html_content, encoding="utf-8")
        print(f"Relatório HTML gerado com sucesso: {output_path}")
        print(f"Abra o arquivo no navegador: file://{Path(output_path).resolve()}")
