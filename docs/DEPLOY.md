# Deploy — Doce Encanto

## VPS Hostinger com Easypanel

### 1. Pré-requisitos

- VPS com Docker e Docker Compose instalados
- Easypanel configurado (ou Swarm puro)
- Domínio apontando para o IP da VPS (ex.: `doceencanto.seucliente.com.br`)

### 2. Clonar e configurar

```bash
ssh root@SEU_IP
cd /opt
git clone https://github.com/LufeDigitalWave/doce-encanto.git
cd doce-encanto
cp .env.example .env
nano .env  # Ajustar variáveis
```

### 3. Variáveis de ambiente para produção

```bash
DEMO_MODE=false
DATABASE_URL=postgresql+asyncpg://postgres:SUA_SENHA_FORTE@db:5432/doce_encanto
ADMIN_USERNAME=admin
ADMIN_PASSWORD=SUA_SENHA_ADMIN
JWT_SECRET=GERE_COM_openssl_rand_hex_32
ABACATEPAY_API_KEY=sua_chave_prod
ABACATEPAY_WEBHOOK_SECRET=seu_secret_webhook
PUBLIC_BASE_URL=https://doceencanto.seucliente.com.br
RESEND_API_KEY=re_xxxxxxxxxxxx
EMAIL_FROM=pedidos@seucliente.com.br
```

### 4. Subir

```bash
docker compose up -d --build
```

Migrações e seed rodam automaticamente no startup.

### 5. SSL via Easypanel

- No painel Easypanel, crie um "Custom App" apontando para as portas 8000 (api) e 80 (web).
- Ou configure um Nginx reverso com Certbot:

```nginx
server {
    listen 443 ssl;
    server_name doceencanto.seucliente.com.br;

    ssl_certificate /etc/letsencrypt/live/doceencanto.seucliente.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/doceencanto.seucliente.com.br/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5173;
    }
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 6. Webhook AbacatePay

1. Acesse [app.abacatepay.com](https://app.abacatepay.com) → Webhooks → Criar.
2. **URL**: `https://doceencanto.seucliente.com.br/api/webhooks/abacatepay`
3. **Secret**: o mesmo valor de `ABACATEPAY_WEBHOOK_SECRET` no `.env`.
4. **Eventos**: `transparent.completed`, `transparent.refunded`.
5. Salvar.

### 7. Testar localmente antes do deploy (webhook)

Use Cloudflare Tunnel (gratuito):

```bash
# Terminal 1 — api rodando na porta 8000
docker compose up api

# Terminal 2 — expor publicamente
cloudflared tunnel --url http://localhost:8000
```

Copie a URL gerada (ex.: `https://abc123.trycloudflare.com`) e registre
como webhook temporário na AbacatePay. Faça um pagamento de R$ 1,00 e
confirme que o pedido muda de status.

---

## Checklist pós-deploy

- [ ] Seed executou (produtos + slots + admin)
- [ ] Login admin funciona
- [ ] Criar pedido → pagar Pix → status muda
- [ ] E-mail de confirmação chega via Resend
- [ ] Atualizar link no README e no PROPOSTA_SNIPPET.md
- [ ] Verificar crontab para slot regeneration (ou rodar seed diariamente)

---

## Regenerar slots diariamente

Adicione ao cron da VPS:

```bash
0 3 * * * cd /opt/doce-encanto && docker compose exec -T api python -m app.seeds.run
```

Isso garante que os próximos 14 dias sempre tenham slots disponíveis.
