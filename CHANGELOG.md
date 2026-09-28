# V2.10.0 — Ícones de navegação

- Novo conjunto de ícones desportivos no menu lateral.
- "Dashboard" apresentado como "Início".
- Ícones consistentes para Resultados, Classificação, Estatísticas, Plantel, Treinos, Pesagens, Match Center, Multas, Regras de multas, Épocas, Equipas/gestão e Definições.
- Mantida toda a lógica e estrutura de dados da V2.9.

# V2.9

## Resultados e Taça AF Porto
- Adicionada a competição **Taça AF Porto**.
- Na Taça são apresentados apenas os jogos do ADC Figueiras.
- Novo filtro em Resultados: **Todos os jogos / Campeonato / Taça AF Porto**.
- Campeonato mantém a coluna **Jornada**; Taça usa **Ronda**.
- Quando são mostradas as duas competições, aparecem em blocos separados na mesma página para preservar o cabeçalho correto.
- Botão **+ Jogo da Taça** na página Resultados.
- Os jogos da Taça não contam para a classificação.

## Match Center
- Ao selecionar cartão amarelo ou vermelho, o campo **Assistência** é ocultado automaticamente.
- A assistência é limpa ao guardar um cartão, evitando dados residuais.
- Acontecimentos manuais da cronologia podem agora ser eliminados diretamente.
- O intervalo automático dos jogos de campeonato continua protegido e não pode ser eliminado.

## Outros
- Em Jogos, encontros da Taça passam a mostrar **Ronda** em vez de Jornada.
- Mantida a mesma chave de armazenamento V2 para preservar os dados existentes.
