# groundedrag

**Uma trava que impede seu RAG de responder sem evidência.**

[Read in English](README.md)

> Este é um espelho em português do README principal. A documentação técnica
> detalhada (arquitetura, ADRs) é mantida em inglês para alcançar o maior
> público possível — este arquivo é atualizado por conveniência, mas pode
> ficar levemente atrás do README em inglês.

> Status: desenvolvimento inicial (Fase 3 — empacotamento). Ainda não
> publicado no PyPI — falta apenas configurar o "trusted publisher" no
> lado do PyPI (veja [`docs/RELEASING.md`](docs/RELEASING.md), em inglês).

[Site de documentação](https://jeffersonwagner.github.io/groundedrag/) ·
[Benchmark](docs/benchmark.md) · [Changelog](CHANGELOG.md)

## O problema

A maioria dos pipelines de RAG (geração aumentada por recuperação) sempre
chama o LLM, mesmo quando a recuperação não encontra nada relevante. O modelo
preenche a lacuna com informação inventada — com confiança. Em domínios onde
uma resposta errada tem custo real (compliance, suporte interno, documentação
técnica, procedimentos de segurança), isso não é um bug de UX, é um passivo.

## O que o groundedrag faz

`groundedrag` é uma biblioteca Python pequena e opinativa que adiciona duas
coisas em cima de qualquer stack de recuperação que você já tenha:

1. **Gate documental.** Antes de o LLM ser chamado, o `groundedrag` verifica se
   existe cobertura real para o tópico da pergunta, usando um mapa
   `tópico → documentos` auditável que uma pessoa não-programadora consegue
   ler e editar. Sem cobertura, o LLM nunca é chamado, e quem fez a pergunta
   recebe uma resposta explícita de "não documentado, cadastre isto" em vez
   de um chute.
2. **Citações verificadas.** Toda afirmação factual do LLM precisa citar
   `[n]`. Um verificador roda **depois** da geração e confere se cada
   citação aponta para um trecho realmente recuperado, sinalizando ou
   removendo qualquer afirmação não rastreável. Pedir ao modelo para citar
   fontes no prompt é uma instrução, não uma garantia — a verificação em
   código é o que transforma isso em garantia.

O `groundedrag` não substitui sua stack de recuperação, seu banco vetorial ou seu
provedor de LLM. Ele fica na frente da chamada ao LLM e depois da geração,
como uma camada fina e agnóstica de provedor.

## Por que não usar LangChain / LlamaIndex / Guardrails AI?

Esses são frameworks grandes e genéricos. O `groundedrag` é deliberadamente
estreito: faz duas coisas — o gate e a verificação de citação — e foi
pensado para encaixar em uma stack que você já tem, inclusive uma construída
sobre LangChain ou LlamaIndex, sem exigir que você adote um framework novo.

## Status

**Fase 2 (CLI e exemplos) concluída.** A biblioteca e o CLI funcionam de
ponta a ponta. Veja [`docs/architecture.md`](docs/architecture.md) para o
desenho completo e [`docs/adr/`](docs/adr) para o raciocínio por trás de
cada decisão.

### Experimente em dois minutos — sem chave de API

```bash
uv sync --extra dev --extra chroma
uv run python examples/helpdesk_bot/demo.py
```

Isso mostra as duas garantias centrais do `groundedrag` com documentos de
exemplo já no repositório: uma pergunta documentada recupera trechos reais,
e uma pergunta sem documentação é recusada **antes** de qualquer chamada ao
LLM. Veja [`examples/`](examples) para os dois exemplos rodáveis.

### CLI

```bash
groundedrag init meu-projeto && cd meu-projeto
# coloque alguns arquivos .txt/.md/.pdf em documents/, depois:
groundedrag ingest documents --topic politica-rh
groundedrag ask "quantos dias de trabalho remoto são permitidos?" --topic politica-rh
```

Por padrão, `ingest`/`ask` usam o `HashingEmbedder` (sem dependências, sem
chave de API, mas com qualidade de recuperação menor — veja `docs/adr/0003`)
e um Chroma local persistido em `.groundedrag/chroma`. Use `--embedder openai`
(com `OPENAI_API_KEY` configurada) para qualidade real de recuperação, e
`--provider anthropic|openai|ollama` para escolher o LLM que gera a
resposta final.

## Desenvolvimento

Requer Python 3.11+ e [uv](https://docs.astral.sh/uv/).

```bash
# sentence-transformers fica de fora de propósito — puxa um download de
# GBs do PyTorch. Adicione --extra sentence-transformers se precisar dele.
uv sync --extra dev --extra anthropic --extra openai --extra ollama --extra chroma --extra pdf
uv run pytest
uv run ruff check .
```

## Licença

[Apache 2.0](LICENSE).
