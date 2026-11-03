# Empório da Música — desafio Artefact

Protótipo em desenvolvimento de um agente de atendimento em Python.

## Estado desta versão

Primeira etapa: importação validada dos seis CSVs para SQLite em memória,
busca de catálogo, cálculo de preços e recuperação textual de políticas.
A CLI desta etapa demonstra ferramentas; **ainda não é um chatbot com LLM**.

## Executar

Python 3.11 ou superior. Na raiz do projeto:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -e .
emporio catalogo --categoria Violões --maximo 1000
emporio produto 90 --pagamento pix
emporio politica "posso devolver uma compra?"
python -m unittest discover -s tests -v
```

Não precisa de chave de API nesta etapa. Execute a CLI na raiz ou informe
`--data /caminho/data` antes do subcomando. Os arquivos são um snapshot fictício:
consulta ao SQLite não equivale a integração em tempo real com a loja.

## Decisões

- Python e biblioteca padrão no núcleo: lógica pequena, rastreável e testável.
- SQLite em memória: relações e consultas parametrizadas, sem servidor.
- Preços em centavos e Decimal: evitar erro de ponto flutuante.
- Modelo terá ferramentas específicas, sem SQL livre e sem acesso irrestrito a clientes.
- PDF preservado; índice textual acompanha página e hash da fonte.
- Busca textual inicial: baseline simples para um manual pequeno; avaliar recall
  antes de introduzir embeddings.
- A interface final prevista é Streamlit; o núcleo não depende dela.

## Próximas etapas

1. Integrar LLM com chamadas de ferramentas e limites de execução.
2. Implementar histórico, persona e consultas de pedidos vinculadas à sessão.
3. Adicionar interface, tratamento de falhas do provedor e avaliação conversacional.
4. Registrar 3–5 conversas reais e instruções finais de configuração.

Veja `docs/decisoes.md` para ambiguidades e limites desta etapa.

## Uso de IA

ChatGPT/Codex auxiliou na análise dos arquivos, proposta de arquitetura,
implementação inicial e execução dos testes. Esta descrição deve ser atualizada
durante o desenvolvimento para refletir o workflow efetivamente realizado.

## Histórico Git

O projeto inclui commits locais que registram etapas reais. Ainda não foi publicado
no GitHub. Preserve o diretório `.git` ao extrair o ZIP. Configure sua identidade
antes dos seus próprios commits; não é necessário reescrever os commits existentes.
Após a entrega, não alterar o repositório, conforme o enunciado.
