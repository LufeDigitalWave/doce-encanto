# Doce Encanto 🧁

> Página de vendas + checkout + agendamento para uma doceria fictícia.
> MVP de portfólio usado em propostas no 99Freelas e Workana.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](./LICENSE)

---

## O que é

A **Doce Encanto** é uma doceria fictícia criada para demonstrar, do zero ao vivo, como uma loja de doces online pode vender com checkout integrado (Pix), agendamento de retirada/entrega e notificações automáticas — tudo num único produto.

O backend (Python + FastAPI) conversa com um **gateway de pagamento real** (AbacatePay) através de uma interface plugável que pode ser trocada por um provider simulado sem alterar uma linha de código de produto. O frontend (React + TypeScript) é uma landing page de alta conversão mobile-first, com carrinho persistente, checkout em etapas e painel admin para gerenciar pedidos.

Este é um **MVP de portfólio**: dados fictícios, marca fictícia, projetado para impressionar clientes em chamadas de fechamento.

---

## Demonstração

> 🔗 **Demo ao vivo**: [em breve]
> 📁 Screenshots/GIFs em [`docs/assets/`](docs/assets/)

_(espaço reservado para vídeo curto mostrando o fluxo de compra)_

---

## ✨ Funcionalidades

- 🛍️ **Vitrine** com 8+ produtos fictícios (brigadeiro gourmet, bolo de pote, torta, kit festa…)
- 🛒 **Carrinho persistente** com drawer lateral e subtotal em tempo real
- 📅 **Agendamento** de retirada ou entrega com calendário de 14 dias e slots de 2h (capacidade controlada)
- 💳 **Checkout em 4 etapas** (dados → agendamento → pagamento → confirmação) sem redirecionamento externo
- 📱 **Pix via QR Code** (real ou simulado) + polling de status em tempo real
- 🔔 **Caixa de saída** com todas as notificações geradas — você mostra ao cliente o que ele receberia
- 🛠️ **Painel admin** com pedidos, agenda, produtos (CRUD) e Caixa de Saída
- 📦 **Rastreamento público** do pedido via link com token
- 🌓 **Design premium** mobile-first (paleta rosa/creme/marrom-chocolate)

---

## 🚀 Como rodar (1 comando)

```bash
git clone https://github.com/LufeDigitalWave/doce-encanto.git
cd doce-encanto
cp .env.example .env
docker compose up --build
```

Acesse:

| Serviço | URL |
|---|---|
| Landing | http://localhost:5173 |
| API (Swagger) | http://localhost:8000/docs |
| Admin | http://localhost:5173/admin (login: `admin` / `demo1234`) |

Migrações e seed rodam automaticamente no startup do container da API.

---

## 🎭 Modos de operação

A variável `DEMO_MODE` controla qual provider é usado. A troca é **só uma variável de ambiente** — o código não muda.

| | `DEMO_MODE=true` (padrão) | `DEMO_MODE=false` |
|---|---|---|
| **Pagamento** | QR fake + botão "Simular pagamento aprovado" | Pix real via AbacatePay (QR Code real, webhook real) |
| **E-mail** | ConsoleEmailProvider (log) | Resend (e-mail real entregue) |
| **WhatsApp** | FakeWhatsAppProvider (só log) | FakeWhatsAppProvider (mesmo — Meta Cloud API documentado como extensão) |
| **Credenciais** | Nenhuma | `ABACATEPAY_API_KEY`, `ABACATEPAY_WEBHOOK_SECRET`, `RESEND_API_KEY`, `EMAIL_FROM` |
| **Quando usar** | Link público do portfólio, demo offline, Roteiro A do DEMO.md | Call de fechamento, demo ao vivo, Roteiro B do DEMO.md |

> Se `DEMO_MODE=false` e as credenciais obrigatórias estiverem vazias, a aplicação **falha no startup** com mensagem clara — nunca cai silenciosamente no fake.

A extensão para WhatsApp real (Meta Cloud API) é suportada pela arquitetura: basta implementar mais um `NotificationProvider`.

---

## 🏗️ Stack e arquitetura

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic
- **Frontend**: React 18, TypeScript, Vite, TailwindCSS, TanStack Query, Axios, Zod
- **Banco**: PostgreSQL 16
- **Pagamento**: AbacatePay (Pix) — contrato via [SDK Python oficial](https://github.com/AbacatePay/abacatepay-python-sdk)
- **E-mail**: Resend (somente quando `DEMO_MODE=false`)
- **Infra local**: Docker Compose
- **Infra prod**: VPS Hostinger com Easypanel (passo a passo em [`docs/DEPLOY.md`](docs/DEPLOY.md))

Detalhes arquiteturais, diagrama Mermaid e mapa de rotas da API: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## 📚 Documentação

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — decisões de arquitetura, diagrama, mapa de rotas
- [`docs/DEMO.md`](docs/DEMO.md) ⭐ — **roteiros de apresentação** (leia antes de qualquer call)
- [`docs/API.md`](docs/API.md) — referência de endpoints
- [`docs/DEPLOY.md`](docs/DEPLOY.md) — deploy em VPS Hostinger/Easypanel
- [`PROPOSTA_SNIPPET.md`](PROPOSTA_SNIPPET.md) — parágrafos prontos pra colar em proposta no 99Freelas/Workana

---

## 🧪 Testes

```bash
docker compose exec api pytest -v
```

Cobre: cálculo de total, frete grátis ≥ R$150, capacidade de slot (incluindo concorrência), lead time de 24h, pagamento fake aprovado/recusado, webhook AbacatePay com assinatura válida/inválida (mock HTTP), idempotência de webhook.

---

## 📄 Licença

MIT — use à vontade em propostas, adapte, demonstre.

---

## English Summary

**Doce Encanto** is a portfolio MVP showcasing a complete fictional Brazilian confectionery's online store: a high-conversion landing page, persistent cart, 4-step checkout (Pix), pickup/delivery scheduling with capacity-controlled time slots, and a notification outbox that renders every message that would be sent in production.

Built with Python 3.12 + FastAPI on the backend and React 18 + TypeScript on the frontend, all wired through Docker Compose. The `DEMO_MODE` env var swaps the payment/notification providers in one place (no business code changes): when `true`, everything is simulated and runs fully offline; when `false`, real Pix via AbacatePay and real email via Resend. The same interface (`PaymentProvider`, `NotificationProvider` ABCs) supports both modes — adding Stripe, MercadoPago, or Meta WhatsApp is just one more implementation.

Features: 8+ product catalog, scheduling calendar with 14-day horizon, slot capacity enforced at the database level (`SELECT ... FOR UPDATE`), idempotent webhook handler (`payment_events.external_event_id` UNIQUE), admin dashboard with outbox preview, and a public order tracking page via signed token. Deployable to any VPS via Easypanel — full guide in [`docs/DEPLOY.md`](docs/DEPLOY.md).
