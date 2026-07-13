#!/bin/bash
# Ativa DEMO_MODE=false na VPS com chaves reais da AbacatePay
# Uso: bash ativar_pix_real.sh <API_KEY> <WEBHOOK_SECRET>
#
# Pré-requisito: conta criada em app.abacatepay.com
# Webhook URL pra registrar no painel: http://93.127.211.7:8010/api/webhooks/abacatepay
# Eventos: transparent.completed, transparent.refunded

API_KEY=$1
WEBHOOK_SECRET=$2

if [ -z "$API_KEY" ] || [ -z "$WEBHOOK_SECRET" ]; then
  echo "Uso: bash ativar_pix_real.sh <API_KEY> <WEBHOOK_SECRET>"
  exit 1
fi

ssh root@93.127.211.7 "
cat > /opt/doce-encanto/.env << EOF
DEMO_MODE=false
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/doce_encanto
ADMIN_USERNAME=admin
ADMIN_PASSWORD=demo1234
JWT_SECRET=secret-key-123
ABACATEPAY_API_KEY=$API_KEY
ABACATEPAY_WEBHOOK_SECRET=$WEBHOOK_SECRET
PUBLIC_BASE_URL=http://93.127.211.7:8010
MIN_LEAD_TIME_HOURS=24
SLOT_CAPACITY=5
DAYS_AHEAD=14
EOF

cd /opt/doce-encanto && docker compose up -d
echo 'Aguardando API...'
sleep 5
curl -s http://localhost:8010/health
"
