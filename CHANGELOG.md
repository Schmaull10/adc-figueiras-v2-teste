# ADC Figueiras V2 Preview — Changelog

## Build com sincronização da competição
- Fonte Zerozero configurada para AF Porto I Divisão Futsal Série 2 2026/27.
- Classificação automática através de `data/competition.json`.
- Importação/atualização dos jogos do ADC Figueiras sem apagar convocatória, 5 inicial, timeline ou estatísticas internas.
- GitHub Action agendada de hora a hora para atualizar a fonte.
- Botão de recarregar os dados publicados e indicação da última sincronização.
- Últimos dados válidos são preservados se a recolha externa falhar.

## Ajustes anteriores
- Emblema metálico final preservado como logotipo da app.
- Match Center sem modo live: convocatória, 5 inicial, marcadores, assistências e cartões.
- Estatísticas mostram número de equipamento em vez das iniciais.
- Multa automática por atraso ao treino.
- Área **Regras de multas** para gerir motivos, valores e automatismos.
