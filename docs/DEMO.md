# 🎬 DEMO.md — Roteiros de Apresentação

> Este documento é o mais importante para o dia a dia de uso deste MVP.
> Leia-o antes de qualquer call.

---

## Credenciais demo

| Campo | Valor |
|-------|-------|
| Admin user | `admin` |
| Admin senha | `demo1234` |
| URL admin | `http://localhost:5173/admin` |
| URL landing | `http://localhost:5173` |
| API docs | `http://localhost:8000/docs` |

---

## Roteiro A — Link público / demo offline (~5 min)

> Usado para: link no portfólio, vídeo Loom, cliente explorando sozinho.
> Configuração: `DEMO_MODE=true` (padrão)

1. **Abra a landing** em mobile (DevTools > responsive 375px).
   - Destaque o design premium e a vitrine de produtos.
2. **Adicione 2 produtos** ao carrinho (ex.: Brigadeiro Gourmet + Bolo de Pote).
3. **Abra o carrinho** (drawer lateral) — mostre subtotal em tempo real.
4. **Finalize o pedido** → preencha dados falsos → escolha "Entrega".
5. **Agendamento**: mostre um slot **lotado** (desabilitado) vs disponível.
6. **Pagamento Pix**: QR Code aparece + botão "🎭 Simular pagamento aprovado".
   - Clique o botão → tela de confirmação com número do pedido.
7. **Abra `/admin`** em outra aba → login `admin / demo1234`.
   - Veja o pedido na lista → mude status para "preparing".
   - Vá em **Caixa de Saída** → mostre a notificação gerada.
8. **Abra o link de rastreio** (`/pedido/{token}`) → timeline atualizada.

**Frase de saída:** "Isso tudo roda offline. Quando você quiser Pix de verdade, é só trocar uma variável de ambiente."

---

## Roteiro B — Call de fechamento / demo ao vivo (~3 min)

> Usado para: videoconferência com o cliente.
> Configuração: `DEMO_MODE=false` + chaves da AbacatePay e Resend configuradas.

### Checklist pré-call

- [ ] `DEMO_MODE=false` no `.env`
- [ ] `ABACATEPAY_API_KEY` com chave dev válida
- [ ] `ABACATEPAY_WEBHOOK_SECRET` configurado
- [ ] `RESEND_API_KEY` configurado
- [ ] Seed inclui produto barato (ex.: Palha Italiana R$ 45,00 — ou ajuste um produto para R$ 1,00 no admin)
- [ ] Testar 1 pagamento sozinho antes da call (cobrar e estornar via painel AbacatePay)
- [ ] Webhook URL pública registrada (usar `cloudflared tunnel` ou ngrok)
- [ ] Email do cliente em mãos (para enviar confirmação ao vivo)

### Roteiro

1. Mesmo fluxo: adicionar produto barato → checkout → dados.
   - No campo e-mail, **use o e-mail do cliente**.
2. Tela de pagamento: QR Code **real** aparece.
   - Peça ao cliente: "Aponte seu celular e paga esse R$ X,XX pra mim."
3. **Aguarde** — a tela faz polling a cada 3 segundos.
   - Quando o webhook chegar, o status muda **ao vivo** na frente dele.
4. Mostre: "O e-mail de confirmação acabou de chegar no seu inbox."
5. Abra o painel admin e mostre o pedido com status "paid".

**Frase de fechamento:** "Isso que você acabou de pagar passou pelo mesmo fluxo que os pedidos dos seus clientes vão passar."

---

## Truques úteis

### Cartão em modo demo

- **Último dígito PAR** (0, 2, 4, 6, 8) → aprovado
- **Último dígito ÍMPAR** (1, 3, 5, 7, 9) → recusado
- Ex.: `4111 1111 1111 1110` = aprovado (termina em 0)

### Perguntas frequentes do cliente

| Pergunta | Resposta rápida |
|----------|-----------------|
| "Funciona com outro gateway?" | "Sim, a arquitetura usa interfaces plugáveis. Integrar Stripe ou MercadoPago é criar um arquivo e registrar." |
| "Manda WhatsApp de verdade?" | "Não neste MVP, mas a interface já existe — é só implementar o provider com a Meta Cloud API. Posso incluir no escopo." |
| "Quanto tempo pra colocar no ar?" | "Se for só trocar textos e produtos: 2 dias. Customização mais profunda: 1 semana." |
| "Quanto custa por venda?" | "AbacatePay cobra R$ 0,80 fixo por Pix recebido. Sem mensalidade." |
| "Posso usar meu domínio?" | "Sim, é só apontar o DNS. Mostro o passo a passo no docs/DEPLOY.md." |

---

## Estornar pagamentos de teste

Acesse o painel da AbacatePay → Transações → selecione → Estornar.
O estorno é instantâneo via Pix.
