# Correção do Sistema de Mapeamento de Caminhos - Docker

## 🎯 Resposta Direta

### Você precisa pedir para a IA detectar o caminho?

# ❌ NÃO!

O sistema **detecta automaticamente** onde você está trabalhando.

---

## 🔄 Como Funciona (Automático)

```
┌─────────────────────────────────────────────────────────┐
│ 1. Você abre a IA em uma pasta                         │
│    Exemplo: C:\Users\Seu\Desktop\meu_projeto           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 2. MCP Client informa automaticamente o caminho        │
│    (via Context.list_roots())                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Ghost Browser detecta e armazena como client_root   │
│    (função get_client_root_paths)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Você pede: "Materialize em ./output"                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 5. Sistema resolve automaticamente:                     │
│    ./output → C:\Users\Seu\Desktop\meu_projeto\output   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 6. Mapeia para o container:                             │
│    → /host_root/Desktop/meu_projeto/output              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 7. Cria os arquivos no lugar certo! ✅                  │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 O Que Foi Corrigido

### Problema Anterior
- Sistema não detectava corretamente drive letters do Windows
- Caminhos fora do `GHOST_HOST_ROOT` não eram mapeados
- Faltavam logs de debug para diagnóstico

### Correções Implementadas

1. **`src/core/output_paths.py`**
   - ✅ Melhor detecção de drive letters (C:, D:, etc.)
   - ✅ Validação se caminho está dentro do host root
   - ✅ Logs de debug detalhados para cada etapa

2. **Documentação**
   - ✅ `RESPOSTA_SIMPLES.md` - Resposta direta
   - ✅ `GUIA_RAPIDO_PT.md` - Guia prático
   - ✅ `docs/DOCKER_PATH_MAPPING_PT.md` - Documentação técnica
   - ✅ `test_path_mapping.py` - Script de teste

---

## 🚀 Como Usar (3 Passos)

### 1️⃣ Inicie o Docker (uma vez)

```powershell
docker compose -f docker-compose.image.yml up -d
```

### 2️⃣ Configure o MCP (uma vez)

```json
{
  "mcpServers": {
    "ghost_browser_mcp": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### 3️⃣ Use normalmente

```
"Materialize os assets em ./output"
```

**Pronto!** O sistema detecta tudo automaticamente.

---

## 💡 Exemplos Práticos

### Exemplo 1: Caminho Relativo (Recomendado)

**Você está em:** `C:\Users\Maria\Desktop\site_clone`

**Você pede:**
```
"Materialize os assets em ./assets"
```

**Sistema faz:**
- Detecta: `C:\Users\Maria\Desktop\site_clone` (automático)
- Resolve: `./assets` → `C:\Users\Maria\Desktop\site_clone\assets`
- Cria: Arquivos em `C:\Users\Maria\Desktop\site_clone\assets`

### Exemplo 2: Caminho Absoluto

**Você pede:**
```
"Salve em C:/Users/Maria/Desktop/backup/assets"
```

**Sistema faz:**
- Valida: Está dentro de `C:\Users\Maria` (GHOST_HOST_ROOT)
- Mapeia: → `/host_root/Desktop/backup/assets`
- Cria: Arquivos em `C:\Users\Maria\Desktop\backup\assets`

### Exemplo 3: Drive Diferente (Precisa Configurar)

**Se você quer usar D: ou E:**

```powershell
# Configure antes de iniciar
$env:GHOST_HOST_ROOT = "D:\MeusProjetos"
docker compose -f docker-compose.image.yml up -d
```

**Depois pode usar:**
```
"Materialize em D:/MeusProjetos/site/assets"
```

---

## 🔍 Testando

### Teste Rápido

```powershell
# Dentro do container
docker exec -it ghost-browser-mcp-ghost-browser-mcp-1 python test_path_mapping.py "C:/Users/Seu/Desktop/teste"
```

### Ver Logs de Debug

```powershell
docker logs ghost-browser-mcp-ghost-browser-mcp-1 --tail 50
```

Procure por:
```
DEBUG [core.output_paths] Resolving output_path: ...
DEBUG [core.output_paths]   -> mapped to host_root: ...
```

---

## ⚙️ Configurações Avançadas

### Apenas se Necessário

#### Usar Drive Diferente

```powershell
$env:GHOST_HOST_ROOT = "D:\Projetos"
docker compose -f docker-compose.image.yml up -d
```

#### Ativar Logs de Debug

Edite `docker-compose.yml`:
```yaml
environment:
  LOG_LEVEL: "DEBUG"
  PYTHONUNBUFFERED: "1"
```

---

## 📚 Arquivos de Referência

| Arquivo | Propósito |
|---------|-----------|
| `RESPOSTA_SIMPLES.md` | Resposta direta: precisa pedir para IA? |
| `GUIA_RAPIDO_PT.md` | Guia prático de uso |
| `docs/DOCKER_PATH_MAPPING_PT.md` | Documentação técnica completa |
| `test_path_mapping.py` | Script de teste e diagnóstico |
| `src/core/output_paths.py` | Código com as correções |

---

## ✅ Checklist de Verificação

- [ ] Docker está rodando: `docker ps`
- [ ] MCP configurado no client
- [ ] Testou com caminho relativo: `./output`
- [ ] Arquivos aparecem na pasta correta
- [ ] (Opcional) Testou com `test_path_mapping.py`

---

## 🆘 Problemas Comuns

### Arquivos não aparecem

**Solução:**
```powershell
# Veja os logs
docker logs ghost-browser-mcp-ghost-browser-mcp-1 --tail 50

# Teste o mapeamento
docker exec -it ghost-browser-mcp-ghost-browser-mcp-1 python test_path_mapping.py "C:/Users/Seu/Desktop/teste"
```

### Permission denied

**Solução:**
```powershell
icacls "C:\Users\Seu\Desktop\pasta" /grant Everyone:F
```

### Drive diferente não funciona

**Solução:**
```powershell
$env:GHOST_HOST_ROOT = "D:\Projetos"
docker compose -f docker-compose.image.yml restart
```

---

## 🎉 Resumo Final

### Você Precisa Fazer:
1. ✅ Iniciar Docker (uma vez)
2. ✅ Configurar MCP (uma vez)
3. ✅ Pedir para IA: "Materialize em ./output"

### Sistema Faz Automaticamente:
- ✅ Detecta onde você está
- ✅ Resolve caminhos relativos
- ✅ Mapeia para o container
- ✅ Cria arquivos no lugar certo

### Você NÃO Precisa:
- ❌ Pedir para IA detectar o caminho
- ❌ Configurar variáveis (exceto drive diferente)
- ❌ Fazer nada especial

**Simplesmente funciona!** 🚀
