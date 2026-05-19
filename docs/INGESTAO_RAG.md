# Ingestão de moléculas via RAG (JSON)

Documentação para a equipe que alimenta a base LMW .

## Visão geral


| JSON em lote | `POST /api/molecules/import/` | Pipeline RAG (este documento) |

O processamento químico (RDKit: InChI, propriedades, SVG) é feito **no servidor**. Não envie esses campos no JSON.

## Autenticação

Todas as requisições de escrita exigem header:

```http
Authorization: Token <sua_chave>
```


## Endpoint de importação

```http
POST /api/molecules/import/
Content-Type: application/json
Authorization: Token <token>
```

### Corpo da requisição

```json
{
  "molecules": [
    {
      "nome_molecula": "Etanol",
      "smiles": "CCO",
      "referencia": "10.1234/exemplo.doi",
      "nome_planta": "Saccharum officinarum",
      "database": "RAG",
      "origem": "Brasil",
      "geolocalizacao": "Nordeste",
      "activity": "Atividade reportada no estudo X"
    }
  ]
}
```

### Campos por molécula

| Campo | Obrigatório | Observação |
|-------|-------------|------------|
| `nome_molecula` | Sim | |
| `smiles` | Sim | 
| `referencia` | Sim |
| `nome_planta` | Sim | |
| `database` | Sim |
| `origem` | Não | 
| `geolocalizacao` | Não | 
| `activity` | Não |

Chaves extras no objeto são ignoradas.

**Importante:** envie todas as chaves obrigatórias em cada item. Se omitir uma chave (ex.: `referencia` ausente), o lote inteiro é rejeitado.

### Limites

- Máximo **500** moléculas por requisição.
- Lista `molecules` não pode estar vazia.

## Respostas

### Sucesso (201)

```json
{
  "status": "sucesso",
  "created": 10,
  "updated": 3,
  "message": "10 cadastrada(s), 3 atualizada(s)"
}
```

- **created:** registros novos (por `smiles` inédito).
- **updated:** registros existentes atualizados (mesmo `smiles` após trim).

Duplicatas no mesmo lote: a **última** entrada para o mesmo `smiles` prevalece.

### Falha de validação (400)

Validação **tudo ou nada**: se um item falhar, **nenhum** registro do lote é gravado.

```json
{
  "status": "falha",
  "errors": [
    {
      "indice": 2,
      "erros": {
        "referencia": ["Este campo é obrigatório."]
      }
    }
  ]
}
```

`indice` é 0-based na lista `molecules`.

### Outros erros

| HTTP | Situação |
|------|----------|
| 401 | Token ausente ou inválido |
| 400 | Body inválido, lista vazia ou acima do limite |
| 500 | Erro interno no processamento químico |

### SMILES inválido para o RDKit

O lote pode ser aceito (201), mas o registro fica com `status_processamento: "erro"` e mensagem em `erro_processamento`. Consulte o detalhe em `GET /api/molecules/{id}/` (usuário vê erros na listagem).


Não envie esses campos no JSON. Eles são preenchidos automaticamente com o **usuário do Token**:

- Criação: `created_by` e `updated_by` = usuário do token.
- Atualização (upsert por `smiles` existente): apenas `updated_by` muda; `created_by` permanece.

Para identificar registros da RAG: use `database: "RAG"` e/ou filtre por `created_by_username` do usuário de serviço (ex.: `rag-ingest`) na API de detalhe.

## Exemplos curl

### Importar um lote

```bash
curl -X POST http://localhost:8000/api/molecules/import/ \
  -H "Authorization: Token SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "molecules": [
      {
        "nome_molecula": "Etanol",
        "smiles": "CCO",
        "referencia": "10.1234/exemplo",
        "nome_planta": "Planta X",
        "database": "AMAZONIADB"
      }
    ]
  }'
```