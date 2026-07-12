# API Reference — Doce Encanto

Base URL: `http://localhost:8000` (dev) ou `https://{seu-dominio}` (prod)

---

## Produtos

### GET /api/products

Lista produtos ativos.

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Brigadeiro Gourmet (cx 12)",
    "slug": "brigadeiro-gourmet-cx-12",
    "description": "Caixa com 12 brigadeiros...",
    "price_cents": 3800,
    "image_url": "/img/brigadeiro.svg",
    "is_active": true
  }
]
```

---

## Agendamento

### GET /api/scheduling/availability?date=2026-07-15&fulfillment=pickup

**Response 200:**
```json
{
  "date": "2026-07-15",
  "fulfillment": "pickup",
  "slots": [
    { "id": 42, "date": "2026-07-15", "start_time": "09:00", "end_time": "11:00", "capacity": 5, "remaining": 3, "available": true },
    { "id": 43, "date": "2026-07-15", "start_time": "11:00", "end_time": "13:00", "capacity": 5, "remaining": 0, "available": false }
  ]
}
```

---

## Pedidos

### POST /api/orders

**Body:**
```json
{
  "items": [{"product_id": 1, "quantity": 2}],
  "customer": {"name": "Maria", "email": "m@ex.com", "phone": "11987654321", "cpf": ""},
  "fulfillment_type": "delivery",
  "address": {"cep": "04101000", "street": "Rua X", "number": "10", "complement": "", "neighborhood": "Vila Mariana", "city": "São Paulo", "state": "SP"},
  "scheduled_date": "2026-07-15",
  "slot_id": 42,
  "payment_method": "pix"
}
```

**Response 201:** OrderOut (ver schema)

### GET /api/orders/:id

**Response 200:** OrderOut

---

## Pagamento

### POST /api/orders/:id/pay

Gera cobrança Pix (provider-agnóstico).

**Response 200:**
```json
{
  "qr_code_base64": "data:image/png;base64,...",
  "copy_paste_code": "00020101021226...",
  "expires_at": "2026-07-12T10:15:00Z",
  "demo_mode": true
}
```

### GET /api/orders/:id/payment-status

**Response 200:**
```json
{"status": "pending", "order_status": "pending_payment", "provider": "fake"}
```

### POST /api/orders/:id/simulate-payment

(Somente `DEMO_MODE=true`) Simula aprovação.

**Response 200:**
```json
{"status": "paid", "order_number": "DE-2026-0001"}
```

---

## Webhooks

### POST /api/webhooks/abacatepay

Recebe notificação da AbacatePay. Header: `X-Webhook-Signature`.

**Response 200:** `{"status": "processed"}` | `{"status": "duplicate"}`

---

## Tracking

### GET /api/tracking/:public_token

**Response 200:** OrderOut (público)

---

## Admin (requer JWT via `Authorization: Bearer <token>`)

### POST /api/admin/login

**Body:** `{"username": "admin", "password": "demo1234"}`

**Response 200:**
```json
{"access_token": "eyJ...", "token_type": "bearer", "expires_in_minutes": 720}
```

### GET /api/admin/dashboard
### GET /api/admin/orders
### PATCH /api/admin/orders/:id/status
### GET /api/admin/products
### POST /api/admin/products
### PATCH /api/admin/products/:id
### GET /api/admin/notifications

Ver detalhes em [`ARCHITECTURE.md`](./ARCHITECTURE.md).
