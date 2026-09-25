# ADC Figueiras V2 Preview

Versão de teste da app do ADC Figueiras.

## Incluído nesta build
- Gestão de plantel, treinos, presenças e pesagens.
- Jogos, convocatórias, 5 inicial, marcadores, assistências e cartões.
- Estatísticas individuais por número de equipamento.
- Multas e regras de multas, incluindo multa automática por atraso ao treino.
- Épocas e arquivo.
- Notificações preparadas para Dia de Jogo, convocatória, resultado final e plano pré-jogo.
- Sincronização externa de classificação e calendário/resultados do ADC Figueiras.

## Sincronização do Zerozero
A app não tenta abrir o Zerozero diretamente no telemóvel. O fluxo é:

1. `.github/workflows/sync-zerozero.yml` corre automaticamente uma vez por hora.
2. `scripts/sync_zerozero.py` lê a fonte definida em `data/sync-config.json`.
3. Se a fonte responder e o parser reconhecer os dados, é atualizado `data/competition.json`.
4. O GitHub Pages volta a publicar o ficheiro.
5. A app recarrega esse ficheiro automaticamente e atualiza classificação e jogos.

Se o site bloquear a recolha automática ou alterar o HTML, o workflow não substitui os últimos dados válidos. Nesse caso é necessário ajustar o parser.

### Forçar uma sincronização
No GitHub:
`Actions` → `Sync Zerozero` → `Run workflow`.

O botão **Recarregar dados** da app apenas volta a ler o último `competition.json` já publicado; não dispara o workflow do GitHub.

### Fonte atual
- Competição: `https://www.zerozero.pt/edicao/af-porto-i-divisao-futsal-serie-2-2026-2027/223354`
- Jogos do ADC Figueiras: `https://www.zerozero.pt/equipa/adc-figueiras/229832/jogos`

Para mudar a fonte realmente usada pela automação, altera `data/sync-config.json` no repositório. A gestão de fontes dentro da app fica preparada para a futura versão com backend.

## Publicar no GitHub Pages
Na raiz do repositório devem existir, pelo menos:
- `index.html`
- `app.js`
- `styles.css`
- `manifest.webmanifest`
- `sw.js`
- `assets/`
- `data/`
- `scripts/`
- `.github/workflows/sync-zerozero.yml`

Mantém o GitHub Pages apontado para `main` / `/(root)`.

## Atualizações
Antes de grandes alterações, usa **Definições → Exportar JSON**. Os dados locais continuam separados do código da aplicação.
