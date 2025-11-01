# Bus Factor Analyzer

Ferramenta de linha de comando para detectar arquivos com risco de monopólio de conhecimento (bus factor baixo) em repositórios Git, a partir da mineração de metadados de commits e autores.

<br>

## Membros do Grupo
- Ana Luisa Messias Ferreira Mendes
- Davi Porto Araujo
- Laura Oliveira Ribeiro
- Leticia Scofield Lenzoni

<br>

## Explicação do sistema


O bus-factor-analyzer identifica arquivos de um repositório em que há concentração excessiva de autoria, isto é, quando um único desenvolvedor domina grande parte das modificações recentes.  
Esse tipo de concentração é um risco de manutenção e evolução, pois o conhecimento crítico fica centralizado em poucas pessoas.

A ferramenta faz isso analisando:
- Commits e linhas modificadas por autor em uma janela temporal configurável.  
- Distribuição da autoria por arquivo, destacando os casos em que um autor domina ≥ limiar definido (ex: 50%)

O resultado é uma lista de arquivos “de risco”, com informações sobre o autor dominante e métricas de dominância.

<br>


**Funcionamento:**

1. **Coleta (Git):** dentro de uma janela temporal configurável (padrão: 90 dias), extrai:
   - Autores de cada arquivo modificado;
   - Quantidade de commits e linhas alteradas por autor.
2. **Cálculo de dominância:** identifica o autor dominante em cada arquivo e calcula sua proporção de contribuição por:
   - Quantidade de commits;
   - Volume de linhas modificadas.
3. **Critério de risco:** um arquivo é marcado como de risco quando o autor dominante ultrapassa o limiar definido (padrão: 50%) em qualquer das métricas.
4. **Relatórios:** gera uma tabela contendo:
   - Caminho do arquivo;
   - Autor dominante;
   - Percentuais de dominância (commits e linhas);
   - Número total de commits e linhas alteradas no período.
  
<br>

## Parâmetros do sistema

| Parâmetro | Descrição | Padrão |
|------------|------------|--------|
| `REPO...` | Um ou mais repositórios (URL, nome GitHub ou caminho local) | - |
| `--days` | Janela temporal de análise (em dias) | `90` |
| `--dominance-threshold` | Limiar de dominância para marcar risco (0–1) | `0.5` |
| `--include` | Caminhos a incluir (glob) | `**/*` |
| `--exclude` | Caminhos a excluir (glob) | `tests/**`, `docs/**`, `.github/**` |
| `--format` | Formato de saída (`table`, `json`, `csv`) | `table` |

<br>

## Explicação das possíveis tecnologias utilizadas

* **Seleção de repositórios:**

  * **SEART GitHub Search Tool (GHS)** — usada apenas para selecionar projetos de teste com filtros (estrelas, commits, colaboradores).
* **Coleta de metadados:**

  * **PyDriller** — varrer o histórico Git local para extrair commits, arquivos modificados e linhas adicionadas/removidas.
  * **GitPython** — suporte a operações Git locais.
* **CLI e relatórios:**

  * **Typer** — criação da interface de linha de comando e documentação de parâmetros.
  * **Rich** — formatação de tabelas no terminal.
  * **pandas** — agregações e exportação em **JSON/CSV**.
