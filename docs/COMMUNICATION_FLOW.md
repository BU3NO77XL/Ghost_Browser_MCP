# Fluxo de Comunicação - Ghost Browser MCP

## 📊 Visão Geral Simplificada

```
┌─────────────────────────────────────────────────────────────────┐
│                         AI Agent (Cliente MCP)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ MCP Protocol (stdio/http)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                         server.py                                │
│  • Cria FastMCP instance                                         │
│  • Define lifecycle (startup/shutdown)                           │
│  • Cria singletons (browser_manager, network_interceptor, etc.) │
│  • Registra tools dos módulos em tools/                         │
│  • Expõe funções no namespace para testes                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Dependency Injection (_deps)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      tools/ (11 módulos)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ browser_management.py    (10 tools)                      │   │
│  │ element_interaction.py   (11 tools)                      │   │
│  │ network_debugging.py     (5 tools)                       │   │
│  │ cookies_storage.py       (3 tools)                       │   │
│  │ tabs.py                  (5 tools)                       │   │
│  │ debugging.py             (7 tools)                       │   │
│  │ element_extraction.py    (9 tools)                       │   │
│  │ file_extraction.py       (9 tools)                       │   │
│  │ progressive_cloning.py   (10 tools)                      │   │
│  │ cdp_functions.py         (13 tools)                      │   │
│  │ dynamic_hooks.py         (10 tools)                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Usa dependências injetadas
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              Core Services (Business Logic)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ browser_manager.py       - Gerencia browsers             │   │
│  │ network_interceptor.py   - Intercepta rede               │   │
│  │ dom_handler.py           - Manipula DOM                  │   │
│  │ cdp_function_executor.py - Executa CDP                   │   │
│  │ element_cloner.py        - Clona elementos               │   │
│  │ cookie_manager.py        - Gerencia cookies              │   │
│  │ login_guard.py           - Controla acesso               │   │
│  │ manual_login_handler.py  - Login manual                  │   │
│  │ response_handler.py      - Gerencia respostas            │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Usa infraestrutura
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              Infrastructure (Storage, Logging, Utils)            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ persistent_storage.py    - Storage persistente           │   │
│  │ process_cleanup.py       - Cleanup de processos          │   │
│  │ platform_utils.py        - Utilitários de plataforma     │   │
│  │ debug_logger.py          - Logging centralizado          │   │
│  │ models.py                - Modelos Pydantic              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Exemplo de Fluxo Completo: Spawn Browser

```
1. AI Agent envia comando MCP:
   spawn_browser(headless=False, viewport_width=1920)
   
2. server.py recebe e roteia para:
   tools/browser_management.py → spawn_browser()
   
3. spawn_browser() usa dependências injetadas:
   ├─→ browser_manager.spawn_browser(options)
   │   ├─→ platform_utils.validate_browser_environment()
   │   ├─→ process_cleanup.track_process(pid)
   │   └─→ persistent_storage.store_instance(instance_id, data)
   │
   └─→ network_interceptor.setup_interception(tab, instance_id)
       └─→ dynamic_hook_system.apply_hooks(instance_id)
   
4. Retorna para AI Agent:
   {"instance_id": "abc123", "state": "ready", ...}
```

## 🔄 Exemplo de Fluxo Completo: Navigate + Login Detection

```
1. AI Agent envia comando MCP:
   navigate(instance_id="abc123", url="https://example.com")
   
2. server.py recebe e roteia para:
   tools/browser_management.py → navigate()
   
3. navigate() orquestra múltiplas dependências:
   ├─→ browser_manager.get_tab(instance_id)
   │   └─→ Retorna tab do browser
   │
   ├─→ cookie_manager.inject_cookies_from_file(tab, url)
   │   ├─→ Lê cookies.txt (Netscape format)
   │   ├─→ Filtra cookies por domínio
   │   └─→ Injeta via network_interceptor.set_cookie()
   │
   ├─→ tab.get(url)  # Navega
   │
   ├─→ manual_login_handler.detect_login_page(tab)
   │   ├─→ Verifica se é página de login
   │   └─→ Se SIM: registra pending login
   │
   └─→ Se login detectado:
       ├─→ login_watcher.start_watching(instance_id, tab)
       └─→ Retorna {"login_required": true, ...}
   
4. Se login_required=true:
   AI Agent PARA e pede ao usuário fazer login manual
   
5. Usuário faz login e confirma
   
6. AI Agent envia:
   confirm_manual_login(instance_id="abc123")
   
7. confirm_manual_login() verifica:
   ├─→ login_watcher.consume_detected(instance_id)
   │   └─→ Verifica se watcher detectou login
   │
   └─→ manual_login_handler.confirm_login(instance_id, tab)
       ├─→ Verifica se ainda está em página de login
       └─→ Se OK: remove pending login
   
8. Retorna para AI Agent:
   {"success": true, "current_url": "https://example.com/dashboard"}
```

## 🔄 Exemplo de Fluxo Completo: Click Element

```
1. AI Agent envia comando MCP:
   click_element(instance_id="abc123", selector="button.login")
   
2. server.py recebe e roteia para:
   tools/element_interaction.py → click_element()
   
3. click_element() verifica guard e executa:
   ├─→ login_guard.check_pending_login_guard(instance_id)
   │   └─→ Se pending login: retorna erro bloqueando execução
   │
   ├─→ browser_manager.get_tab(instance_id)
   │   └─→ Retorna tab do browser
   │
   └─→ dom_handler.click_element(tab, selector)
       ├─→ tab.select(selector)  # Encontra elemento via CDP
       ├─→ element.scroll_into_view()  # Garante visibilidade
       ├─→ element.click()  # Clica via CDP
       └─→ debug_logger.log_info("Clicked element")
   
4. Retorna para AI Agent:
   true
```

## 🔄 Exemplo de Fluxo Completo: Extract Element Styles

```
1. AI Agent envia comando MCP:
   extract_element_styles(instance_id="abc123", selector=".hero")
   
2. server.py recebe e roteia para:
   tools/element_extraction.py → extract_element_styles()
   
3. extract_element_styles() usa element_cloner:
   ├─→ browser_manager.get_tab(instance_id)
   │
   └─→ element_cloner.extract_element_styles(tab, selector)
       ├─→ Carrega JavaScript de src/js/extract_styles.js
       ├─→ tab.evaluate(js_code)  # Executa no browser
       ├─→ Extrai computed styles via getComputedStyle()
       ├─→ Extrai CSS rules via getMatchedCSSRules()
       ├─→ Extrai pseudo-elements (::before, ::after)
       └─→ Retorna objeto com todos os estilos
   
4. Se resposta muito grande:
   response_handler.handle_response(result)
   ├─→ Estima tokens (len(json) / 4)
   ├─→ Se > 20000 tokens: salva em arquivo
   └─→ Retorna {"file_path": "...", "estimated_tokens": ...}
   
5. Retorna para AI Agent:
   {
     "computed_styles": {...},
     "css_rules": [...],
     "pseudo_elements": {...}
   }
```

## 📦 Injeção de Dependências

O `server.py` cria um container `_deps` com todas as dependências:

```python
# server.py
_deps = {
    "browser_manager": browser_manager,           # Singleton
    "network_interceptor": network_interceptor,   # Singleton
    "dom_handler": dom_handler,                   # Singleton
    "cdp_function_executor": cdp_function_executor, # Singleton
    "element_cloner": element_cloner,             # Singleton
    "comprehensive_element_cloner": comprehensive_element_cloner, # Singleton
    "file_based_element_cloner": file_based_element_cloner, # Singleton
    "progressive_element_cloner": progressive_element_cloner, # Singleton
    "response_handler": response_handler,         # Singleton
    "persistent_storage": persistent_storage,     # Singleton
    "manual_login_handler": manual_login_handler, # Singleton
    "dynamic_hook_ai": dynamic_hook_ai,           # Singleton
    "debug_logger": debug_logger,                 # Singleton
}
```

Cada módulo de tools recebe `_deps` e extrai o que precisa:

```python
# tools/browser_management.py
def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]
    network_interceptor = deps["network_interceptor"]
    manual_login_handler = deps["manual_login_handler"]
    persistent_storage = deps["persistent_storage"]
    
    @section_tool("browser-management")
    async def spawn_browser(...):
        # Usa as dependências injetadas
        instance = await browser_manager.spawn_browser(...)
        await network_interceptor.setup_interception(...)
        return {...}
```

## ✅ Vantagens desta Arquitetura

1. **Separação de Responsabilidades**
   - Tools MCP (interface) separadas da lógica de negócio
   - Core services não conhecem MCP
   - Infraestrutura isolada

2. **Testabilidade**
   - Fácil mockar dependências
   - Testes podem importar funções do `server.py`
   - Core services testáveis independentemente

3. **Manutenibilidade**
   - Cada módulo de tools tem ~100-300 linhas
   - Fácil encontrar e modificar funcionalidades
   - Mudanças em core services não afetam tools

4. **Reutilização**
   - Managers/handlers usados por múltiplas tools
   - Lógica de negócio centralizada
   - Sem duplicação de código

5. **Escalabilidade**
   - Fácil adicionar novas tools
   - Fácil adicionar novos core services
   - Dependency injection facilita extensão

## 🚫 O que NÃO Fazer

❌ **Tools importando de outras tools**
```python
# ❌ ERRADO
from tools.browser_management import spawn_browser
```

❌ **Core services importando de tools**
```python
# ❌ ERRADO
from tools.element_interaction import click_element
```

❌ **Tools acessando singletons diretamente**
```python
# ❌ ERRADO
from browser_manager import browser_manager
browser_manager.spawn_browser(...)
```

✅ **Sempre usar dependency injection**
```python
# ✅ CORRETO
def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]
    # Usa browser_manager injetado
```
