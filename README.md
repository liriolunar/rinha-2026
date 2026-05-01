# Rinha de Backend 2026

## Conceitos principais da busca vetorial

A detecção de fraude é feita por **busca vetorial** (similarity search), não por igualdade exata.

### Fluxo resumido

1. **Vetorização** — cada payload vira um vetor de 14 números entre `[0.0, 1.0]`, um por dimensão (amount, hora, distância, etc.)
2. **Normalização** — cada campo é dividido por uma constante de referência (ex: `amount / max_amount`) e depois **clampado** no intervalo `[0.0, 1.0]`
3. **Busca KNN** — calcula distância euclidiana entre o vetor da transação e todos os vetores do dataset de referência, seleciona os **K=5 mais próximos**
4. **Votação** — `fraud_score = nº de fraudes entre os 5 / 5`
5. **Decisão** — `approved = fraud_score < 0.6` (threshold fixo)

### Edge cases

| Caso | Tratamento |
|------|------------|
| Valor normalizado > 1.0 (ex: amount 12500 com max_amount 10000 → 1.25) | **Clamp** corta para `1.0` — o vetor nunca sai do intervalo normalizado |
| `last_transaction: null` (primeira transação do cliente) | Índices 5 e 6 recebem sentinela `-1` para indicar "ausência de dado" |
| Empate ou 0 vizinhos de fraude | `fraud_score = 0.0`, transação aprovada |
| Todos os K vizinhos são fraude | `fraud_score = 1.0`, transação negada |

### O que o sistema **não** faz

- Não "entende" fraude — apenas encontra transações passadas com "formato" parecido e deixa a maioria decidir
- Não tem modelo treinado — é **instance-based learning**: dataset memorizado + busca em tempo de consulta
- Não usa regras como "amount > X → nega" — a decisão depende unicamente da votação dos vizinhos

### Algoritmos de busca (performance)

| Estratégia | Complexidade | Descrição |
|------------|-------------|-----------|
| KNN exato (força bruta) | O(N) | Percorre todas as referências; simples mas pode ser lento |
| HNSW | O(log N) | Grafo em camadas; usado por pgvector, Qdrant |
| IVF | O(√N) | Particiona o espaço em células |
| LSH | sub-linear | Hash que colide para vetores parecidos |
